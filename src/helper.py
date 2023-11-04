import hashlib
import logging
import os
from datetime import datetime
from pathlib import Path
from src.model_validate_file import ValidateFile
from PIL import Image

logging.basicConfig(
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


def log_progress(index: int, total_files: int, start_time: datetime):
    run_time = datetime.now() - start_time
    logger.info(f"Runtime: {run_time.seconds} Seconds -- Progress: {index}/{total_files}")


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
