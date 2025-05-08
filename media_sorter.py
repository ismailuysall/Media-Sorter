#!/usr/bin/env python3

import os
import shutil
import hashlib
import subprocess
import sqlite3
import re
from datetime import datetime
from pathlib import Path
import logging
import yaml
from time import time
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

# Load configuration from YAML file
with open("config.yaml") as f:
    config = yaml.safe_load(f)

SOURCE_DIR = Path(config["source"])
DEST_DIR = Path(config["destination"])
DATABASE_PATH = Path(config["database"])
LOG_PATH = Path(config["log"])
SUPPORTED_EXTENSIONS = config["supported_extensions"]

# Ensure necessary directories exist
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def compute_hash(file_path):
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for block in iter(lambda: f.read(4096), b""):
            hasher.update(block)
    return str(file_path), hasher.hexdigest()

def extract_date(file_path):
    # Try EXIF metadata
    try:
        result = subprocess.run(
            ["exiftool", "-DateTimeOriginal", "-d", "%Y%m%d", str(file_path)],
            capture_output=True, text=True, check=True
        )
        match = re.search(r": (\d{8})", result.stdout)
        if match:
            date_str = match.group(1)
            return date_str[:4], date_str[4:6], date_str
    except Exception as e:
        logging.warning(f"Exiftool failed for {file_path}: {e}")

    # Try parsing date from filename
    name = file_path.name
    match = re.search(r"(\d{4})[-_]?(\d{2})[-_]?(\d{2})", name)
    if match:
        year, month, day = match.groups()
        return year, month, f"{year}{month}{day}"

    # No valid date found
    return None

def create_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY,
            original_path TEXT,
            hash TEXT,
            year TEXT,
            month TEXT,
            media_type TEXT,
            status TEXT,
            destination_path TEXT,
            final_name TEXT
        )
    """)
    conn.commit()
    return conn

def safe_copy(src_path, dest_dir, base_name):
    dest_file = dest_dir / base_name
    counter = 1
    while dest_file.exists():
        stem, suffix = dest_file.stem, dest_file.suffix
        dest_file = dest_dir / f"{stem}__{counter}{suffix}"
        counter += 1
    shutil.copy2(src_path, dest_file)
    return dest_file

PHOTOGRAPHIC_PREFIXES = config.get("photographic_prefixes", [])

def is_photographic_name(name):
    return any(name.startswith(prefix) for prefix in PHOTOGRAPHIC_PREFIXES)

def available_space(path):
    stats = os.statvfs(str(path))
    return stats.f_bavail * stats.f_frsize

# Main processing function

def process_file(file_path, file_hash, migrated_hashes, conn, stats, hash_counter):
    cursor = conn.cursor()
    date_extracted = extract_date(file_path)
    if date_extracted is None:
        year = month = yyyymmdd = None
    else:
        year, month, yyyymmdd = date_extracted

    media_type = "PHOTO" if file_path.suffix.lower() in [".jpg", ".jpeg", ".png"] else "VIDEO"
    file_name = file_path.name

    # Ensure review directory exists
    review_dir = DEST_DIR / "ToReview"
    review_dir.mkdir(parents=True, exist_ok=True)

    # If no date, move to review
    if year is None or month is None:
        new_path = safe_copy(file_path, review_dir, file_name)
        logging.info(f"Moved to review: {new_path} - Hash: {file_hash}")
        status = "to_review"
        stats["to_review"] += 1
    else:
        # Define destination and duplicate dirs
        dest_dir = DEST_DIR / media_type / year / month
        dup_dir = DEST_DIR / f"{media_type}_DUPLICATES" / year / month
        dest_dir.mkdir(parents=True, exist_ok=True)
        dup_dir.mkdir(parents=True, exist_ok=True)

        is_photo = is_photographic_name(file_name)
        first_occurrence = file_hash not in migrated_hashes
        if first_occurrence:
            hash_counter[file_hash] = []
        hash_counter[file_hash].append((file_path, is_photo))

        if first_occurrence:
            chosen = sorted(hash_counter[file_hash], key=lambda x: not x[1])[0][0]
            if file_path == chosen:
                status = "migrated"
                target_dir = dest_dir
                stats["migrated"] += 1
                migrated_hashes.add(file_hash)
            else:
                status = "duplicate"
                target_dir = dup_dir
                stats["duplicates"] += 1
        else:
            status = "duplicate"
            target_dir = dup_dir
            stats["duplicates"] += 1

        new_path = safe_copy(file_path, target_dir, file_name)
        logging.info(f"File {status}: {new_path} - Hash: {file_hash}")

    # Insert record
    cursor.execute(
        """
        INSERT INTO files (original_path, hash, year, month, media_type, status, destination_path, final_name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (str(file_path), file_hash, year, month, media_type, status, str(new_path.parent), new_path.name)
    )
    conn.commit()

# Scan source directory

def scan_directory():
    start = time()
    conn = create_db()

    all_files = []
    ignored = []
    for root, _, files in os.walk(SOURCE_DIR):
        for name in files:
            path = Path(root) / name
            if path.suffix.lower() in SUPPORTED_EXTENSIONS:
                all_files.append(path)
            else:
                ignored.append(path)

    if not all_files:
        print("No files found in source directory.")
        logging.info("No files found in source directory.")
        return

    if ignored:
        logging.info(f"Ignored unsupported files: {len(ignored)}")
        for p in ignored:
            logging.info(f"Ignored: {p} (extension: {p.suffix})")

    # Check space
    required = sum(p.stat().st_size for p in all_files)
    free = available_space(DEST_DIR)
    if free < required:
        logging.error(f"Insufficient space: needed {required}, available {free}")
        print(f"Insufficient space: needed {required} bytes, available {free} bytes")
        return

    stats = {"migrated": 0, "duplicates": 0, "to_review": 0}
    hash_counter = {}

    # Compute hashes
    with ThreadPoolExecutor() as executor:
        hash_results = list(executor.map(compute_hash, all_files))
    hash_map = dict(hash_results)

    # Load already migrated hashes
    cursor = conn.cursor()
    cursor.execute("SELECT hash FROM files WHERE status = 'migrated'")
    migrated_hashes = set(row[0] for row in cursor.fetchall())

    # Process files
    total = len(all_files)
    for idx, file_path in enumerate(all_files, 1):
        pct = (idx / total) * 100
        msg = f"{pct:.1f}% completed - Migrated: {stats['migrated']}, Duplicates: {stats['duplicates']}, ToReview: {stats['to_review']}"
        print(msg, end='\r')
        logging.info(msg)
        try:
            process_file(
                file_path,
                hash_map[str(file_path)],
                migrated_hashes,
                conn,
                stats,
                hash_counter
            )
        except Exception as e:
            logging.error(f"Error processing {file_path}: {e}")

    conn.close()
    duration = time() - start
    logging.info(f"Total execution time: {duration:.2f} seconds")

    # Summary
    summary = (
        "\nSummary:\n"
        f"  Migrated files: {stats['migrated']}\n"
        f"  Duplicate files: {stats['duplicates']}\n"
        f"  Files to review: {stats['to_review']}\n"
        f"  Unsupported files: {len(ignored)}\n"
    )
    print(summary)
    logging.info(summary)

    # Check for duplicate migrated hashes
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT hash, COUNT(*) AS count
        FROM files
        WHERE status = 'migrated'
        GROUP BY hash
        HAVING count > 1
    """
    )
    duplicates = cursor.fetchall()
    if duplicates:
        logging.warning("Warning: duplicate migrated hashes found:")
        for hash_val, count in duplicates:
            logging.warning(f"Hash: {hash_val} - Occurrences: {count}")
    else:
        logging.info("Validation OK: no duplicate migrated hashes.")
    conn.close()

# Reset environment

def reset_environment():
    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()
        print(f"Removed database: {DATABASE_PATH}")
    if LOG_PATH.exists():
        LOG_PATH.unlink()
        print(f"Removed log file: {LOG_PATH}")
    for folder in ["PHOTO", "VIDEO", "PHOTO_DUPLICATES", "VIDEO_DUPLICATES", "ToReview"]:
        p = DEST_DIR / folder
        if p.exists():
            shutil.rmtree(p)
            print(f"Removed directory: {p}")

# Entry point

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        reset_environment()
    else:
        scan_directory()
