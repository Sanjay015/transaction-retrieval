import tempfile
import config
from pathlib import Path
from unittest import TestCase, mock

from utils import utils


class TestUtils(TestCase):
    def setUp(self) -> None:
        self.processed_fake_file = ["data/processed/processed_fake.csv", "data/processed/processed_fake.txt",
                                    "data/processed/processed_fake.json", "data/processed/processed_fake1.csv"]
        self.non_processed_fake_files = ["data/non_processed_fake.csv", "data/non_processed_fake.txt",
                                         "data/non_processed_fake.json", "data/non_processed_fake1.csv"]

        self.fake_files = ["file1.csv", "file1.txt", "file1.json", "file2.CSV", "file2.txt", "file2.json"]
        self.fake_base_location = "fake/location"

    def create_fake_files(self, temp_dir):
        """Function to create temp files"""
        for fake_file in self.processed_fake_file + self.non_processed_fake_files:
            temp_fake_file = Path(temp_dir) / Path(fake_file)
            temp_fake_file.mkdir(parents=True, exist_ok=True)
            temp_fake_file.touch(exist_ok=True)

    def test_filter_files(self):
        # Test case to test `utils.utils.filter_files` function

        # Should return only csv files from the list
        expected = [Path("fake/location/file1.csv"), Path("fake/location/file2.CSV")]
        actual = utils.filter_files(self.fake_base_location, self.fake_files)
        self.assertListEqual(expected, [Path(p) for p in actual])

        # Should return empty list as input does not contains any .csv file
        expected = []
        actual = utils.filter_files(self.fake_base_location, ["data.txt", "data.json", "data.html"])
        self.assertListEqual(expected, actual)

    def test_transaction_files_including_proceed_folder(self):
        # Test case to test `utils.utils.transaction_files` function, including processed folder
        with tempfile.TemporaryDirectory() as temp_dir:
            self.create_fake_files(temp_dir)
            expected = [Path(temp_dir) / f for f in self.processed_fake_file + self.non_processed_fake_files
                        if f.lower().endswith(".csv")]

            with mock.patch("utils.utils.get_root", return_value=temp_dir):
                # Test load files including processed
                actual = utils.transaction_files(load_processed=True)
                self.assertListEqual(expected, [Path(p) for p in actual])

    def test_transaction_files_only_new_data(self):
        # Test case to test `utils.utils.transaction_files` function, only with new data
        with tempfile.TemporaryDirectory() as temp_dir:
            self.create_fake_files(temp_dir)
            expected = [Path(temp_dir) / f for f in self.non_processed_fake_files if f.lower().endswith(".csv")]

            with mock.patch("utils.utils.get_root", return_value=temp_dir):
                # Load only new files
                actual = utils.transaction_files(load_processed=False)
                self.assertListEqual(expected, [Path(p) for p in actual])

    def test_move_transaction_file(self):
        # Test case to test `utils.utils.move_transaction_file`
        with tempfile.TemporaryDirectory() as temp_dir:
            self.create_fake_files(temp_dir)
            source_files = [Path(temp_dir) / f for f in self.non_processed_fake_files if f.lower().endswith(".csv")]

            for fake_file in source_files:
                with mock.patch("utils.utils.get_root", return_value=temp_dir):
                    utils.move_transaction_file(str(fake_file))
                # File should not be available in non processed folder
                self.assertFalse(fake_file.exists())
                processed_path = Path(temp_dir) / config.DATA_FILE_LOCATION / config.PROCESSED_FOLDER_NAME
                processed_path = processed_path / Path("{}{}".format(fake_file.stem, fake_file.suffix))
                # File should be available in processed folder
                self.assertTrue(processed_path.exists())
