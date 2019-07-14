import os
import shutil

import config


def get_root() -> str:
    """Returns root location of project"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def filter_files(base_location: str, file_list: list) -> list:
    """Filter files bases on extension
        Args:
            base_location: Processing/processed file's dir name
            file_list: List of files available under base directory
        Returns:
            List of all files with the defined extension in config
    """
    return [os.path.join(base_location, file_name) for file_name in file_list
            if file_name.lower().endswith(config.DATA_FILE_EXTENSION)]


def transaction_files(load_processed=False) -> list:
    """Data file folder location"""
    processed_files = []
    new_file_location = os.path.join(get_root(), config.DATA_FILE_LOCATION)

    processed_location = os.path.join(new_file_location, config.PROCESSED_FOLDER_NAME)
    # Processed files to load
    if load_processed and os.path.exists(processed_location):
        processed_files = filter_files(processed_location, os.listdir(processed_location))

    # Transaction files to load
    new_files = filter_files(new_file_location, os.listdir(new_file_location))

    return processed_files + new_files


def move_transaction_file(source) -> None:
    """Once data is loaded move data file to `processed` directory
    Args:
        source: source file location of data file
    """
    processed_folder = os.path.join(get_root(), config.DATA_FILE_LOCATION, config.PROCESSED_FOLDER_NAME)
    if not os.path.exists(processed_folder):
        os.makedirs(processed_folder, exist_ok=True)

    file_name = os.path.basename(source)
    target = os.path.join(processed_folder, file_name)
    shutil.move(source, target)
