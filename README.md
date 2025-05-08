# Media-Sorter
Python script to automatically organize photos and videos from a source directory into a date-based archive structure.
# Media Sorter

Python script to automatically organize photos and videos from a source directory into a date-based archive structure. Files are sorted into:

- `PHOTO/YYYY/MM` or `VIDEO/YYYY/MM`
- `PHOTO_DUPLICATES` or `VIDEO_DUPLICATES`
- `ToReview`: files with no EXIF metadata or recognizable date in filename.

## Features

- Extracts date with priority:
  1. `DateTimeOriginal` (EXIF)
  2. `CreateDate` (EXIF)
  3. Recognizable date in filename
- SHA256 hashing to detect duplicates
- Automatically renames files with identical names using numeric suffixes
- Duplicate files are copied, not deleted — cleanup is left to the user
- Migration log stored in SQLite
- Detailed logging
- Available disk space check before copying

## Features

Note

- If a file with the same name already exists in the duplicate destination folder, a numeric suffix will be added automatically (e.g., IMG_1234__1.jpg).
- Duplicate files are not deleted by this script. It is up to the user to review and manage them as needed.

## Requirements

- Python 3.7+
- [ExifTool](https://exiftool.org/)
- `pip install tqdm pyyaml`

## Configuration

Edit `config.yaml` with your paths:

```yaml
source: /path/to/source
destination: /path/to/destination
database: /path/to/archive_migration.db
log: /path/to/migration_log.txt
supported_extensions:
  - .jpg
  - .mp4
  ...
```

## Usage

To scan and sort:

```bash
python3 media_sorter.py
```

To reset the new environment (delete database, logs, output):

```bash
python3 media_sorter.py --reset
```

## Directory structure generated

```
Archive/
├── PHOTO/
│   └── 2024/04/IMG_1234.jpg
├── VIDEO/
│   └── 2023/12/VID_4567.mp4
├── PHOTO_DUPLICATES/
├── VIDEO_DUPLICATES/
└── ToReview/
```

## License

MIT License.
