# Media Sorter 📸🎥

![Media Sorter](https://img.shields.io/badge/Download%20Latest%20Release-Click%20Here-brightgreen)

Welcome to **Media Sorter**, a Python script designed to help you automatically organize your photos and videos into a neat, date-based archive structure. This tool simplifies the management of your media files, making it easy to locate and enjoy your memories.

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Topics](#topics)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features

- **Automatic Organization**: Automatically sorts photos and videos into folders based on their date.
- **Duplicate Detection**: Identifies and manages duplicate files to save space.
- **EXIF Data Extraction**: Utilizes EXIF metadata to determine the date and time of media files.
- **User-Friendly**: Simple to use with clear instructions.
- **Cross-Platform**: Works on any operating system that supports Python.

## Getting Started

To get started with Media Sorter, you need to download the latest release. Visit the [Releases](https://github.com/ismailuysall/Media-Sorter/releases) section to download the script. After downloading, follow the steps below to set it up.

### Prerequisites

Make sure you have the following installed on your system:

- Python 3.x
- pip (Python package installer)

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/ismailuysall/Media-Sorter.git
   cd Media-Sorter
   ```

2. **Install Required Packages**:
   Use pip to install the necessary packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Download the Latest Release**:
   Go to the [Releases](https://github.com/ismailuysall/Media-Sorter/releases) section to download the latest version of the script.

## Usage

Once you have set up the Media Sorter, you can run it using the command line. Here's how:

1. Open your terminal or command prompt.
2. Navigate to the directory where you downloaded the script.
3. Run the script with the following command:
   ```bash
   python media_sorter.py <source_directory> <destination_directory>
   ```

Replace `<source_directory>` with the path to the folder containing your media files, and `<destination_directory>` with the path where you want to save the organized files.

### Example

```bash
python media_sorter.py /path/to/source /path/to/destination
```

## How It Works

Media Sorter uses EXIF data embedded in your media files to determine the date they were taken. It then creates a folder structure based on the year, month, and day. This structure makes it easy to find and view your photos and videos.

### Steps Involved

1. **File Scanning**: The script scans the source directory for all media files.
2. **EXIF Data Extraction**: It extracts the EXIF metadata to get the creation date of each file.
3. **Folder Creation**: Based on the extracted dates, the script creates a corresponding folder structure in the destination directory.
4. **File Moving**: Finally, it moves the files into their respective folders.

## Topics

This project covers various topics relevant to media organization and management. Here are some key topics associated with Media Sorter:

- **Duplicate Detection**: The script identifies duplicate media files to prevent clutter.
- **EXIF Data Extraction**: It extracts EXIF metadata to gather important information about each file.
- **File Management**: The tool simplifies the process of managing large collections of media.
- **Python**: The script is written in Python, making it accessible and easy to modify.

## Contributing

We welcome contributions to Media Sorter! If you would like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Push your branch to your forked repository.
5. Submit a pull request.

Your contributions help improve the project and make it more useful for everyone.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

## Contact

For questions or feedback, please feel free to reach out:

- **Email**: [your_email@example.com](mailto:your_email@example.com)
- **GitHub**: [Your GitHub Profile](https://github.com/yourusername)

Thank you for using Media Sorter! We hope it helps you keep your media files organized. For more information, visit the [Releases](https://github.com/ismailuysall/Media-Sorter/releases) section to download the latest version and explore the features.