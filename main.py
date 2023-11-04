import argparse
import logging
from pathlib import Path
from src.helper import find_duplicates

logging.basicConfig(
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    description = """
    This small script is meant to scan folders for images, 
    find any duplicates, remove those duplicates, and rename the
    files to the datetime they were taken.
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--path", help="comma separated list of paths to scan", required=True)
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
