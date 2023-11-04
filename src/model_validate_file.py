from pathlib import Path
from src.helper import get_image_date_taken


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
