import argparse
import hashlib
import logging
import os
from datetime import datetime
from pathlib import Path

from PIL import Image

logging.basicConfig(
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class ValidateFile:
    correct_date_name: str
    correct_file_path: Path
    md5checksum: str
    filepath: Path
    duplicate_paths: []

    def __init__(self, filepath=None, md5checksum=None):
        self.duplicate_paths = []
        self.filepath = Path(filepath)
        self.md5checksum = md5checksum
        self.correct_date_name = get_image_date_taken(filepath)
        if self.correct_date_name is None:
            self.correct_date_name = f'none_{self.md5checksum[0:5]}'
        self.correct_file_path = self.filepath.with_name(f"{self.correct_date_name}{self.filepath.suffix}")

    def __eq__(self, other):
        duplicate = self.md5checksum == other.md5checksum
        if duplicate:
            self.duplicate_paths.append(other.filepath)
        return duplicate

    def rename(self):
        self.filepath.rename(self.correct_file_path)


def calculate_md5(filename):
    if not Path(filename).is_dir():
        hasher = hashlib.md5()
        with open(filename, 'rb') as file:
            for chunk in iter(lambda: file.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()


def get_image_date_taken(filepath):
    try:
        image = Image.open(filepath)
        exif_data = image._getexif()
        if exif_data:
            date_taken = exif_data.get(36867) or exif_data.get(306)
            if date_taken:
                return str(date_taken).replace(':', '-', 2).replace(':', '.')
    except (AttributeError, OSError) as e:
        logger.error(f"Error processing file {filepath}: {e}")


def find_duplicates(directory_path):
    file_list = create_file_list(directory_path)
    duplicates = [file for file in file_list if file_list.count(file) > 1]

    removed = []
    for file in duplicates:
        if file.filepath in removed:
            continue

        for duplicate in file.duplicate_paths:
            os.remove(duplicate)
            removed.append(duplicate)
            logger.info(f'Removed duplicate: {duplicate}')

        if file.correct_file_path != file.filepath:
            file.rename()
            logger.info(f'Renamed: {file.filepath} to {file.correct_file_path}')


def find_image_files_in_directory(directory_path):
    image_file_extensions = ['.jpg', '.png', '.gif', '.bmp', '.tif', '.webp', '.svg', '.jpeg', '.tiff', '.heic']
    image_files = []

    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if any(file.lower().endswith(ext) for ext in image_file_extensions):
                image_files.append(os.path.join(root, file))

    return image_files


def create_file_list(directory: str):
    start_time = datetime.now()
    file_list = []
    image_files = find_image_files_in_directory(directory)

    for index, file in enumerate(image_files, start=1):
        try:
            md5_checksum = calculate_md5(file)
            file_obj = ValidateFile(file, md5_checksum)
            file_list.append(file_obj)
            if index % 50 == 0:
                log_progress(index, len(image_files), start_time)
        except OSError as e:
            logger.error(f"Exception thrown for {file}: {e}")

    return file_list


def log_progress(index: int, total_files: int, start_time: datetime):
    run_time = datetime.now() - start_time
    logger.info(f"Runtime: {run_time.seconds} Seconds -- Progress: {index}/{total_files}")


def main():
    description="""
    This small script is meant to scan folders for images, 
    find any duplicates, remove those duplicates, and rename the
    files to the datetime they were taken.
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--path", help="comma separated list of paths to scan",required=True)
    args = parser.parse_args()

    path_list = args.path.split(',')

    for path in path_list:
        if Path(path).exists():
            logger.info(f"Starting scan for duplicates - root folder {path}")
            for entry in Path(path).rglob('*'):
                if entry.is_dir():
                    find_duplicates(entry)
            logger.info(f"Scan completed for {path}")
            logger.info("Full scan ending")
        else:
            logger.error(f"{path} is not a valid path")


if __name__ == '__main__':
    main()
