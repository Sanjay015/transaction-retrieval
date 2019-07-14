"""Module to generate random transaction data"""
import argparse
import datetime
import logging.config
import pickle
import time
import random

import config
import pandas as pd
from pathlib import Path

from utils.utils import get_root
from log.logger import setup_logger

logger = logging.getLogger("random_data_generator")


class GenerateRandomData(object):

    def __init__(self, frequency=60):
        self.frequency = frequency
        self.cities = ["C1", "C2", "C3", "C5", "C5"]
        self.products = ["P1", "P2", "P3", "P4", "P5"]
        self.product_ids = [10, 30, 20, 50, 40]
        self.root_folder = Path(get_root())
        self.ref_location = self.root_folder / Path(config.REFERENCE_DATA_FILE)
        self.trans_location = self.root_folder / Path(config.DATA_FILE_LOCATION)
        self.max_trans_id_location = self.root_folder / Path(config.DATA_FILE_LOCATION) / "max_trans_id.pickle"

        # Create data directory if not available
        self.ref_location.parent.mkdir(parents=True, exist_ok=True)
        self.trans_location.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def dump_max_trans_id(location, data):
        """Dump python object to a pickle file."""
        with open(str(location), 'wb') as handle:
            pickle.dump(data, handle)

    @staticmethod
    def read_max_trans_id(location):
        """Read data from pickle object."""
        with open(str(location), 'rb') as handle:
            data = pickle.load(handle)
        return data

    def generate_random_reference_data(self):
        """Create static reference file, if not available"""
        if not self.ref_location.exists():
            data = pd.DataFrame(
                data={
                    "productId": self.product_ids,
                    "productName": self.products,
                    "productManufacturingCity": self.cities
                }
            )
            error_message = "Reference data column mismatch found in config, while generating random data"
            assert sorted(list(data.columns)) == sorted(config.REF_COLS),  error_message
            logging.debug("Created reference file at: {}".format(self.ref_location))
            data.to_csv(self.ref_location, index=False)

    def generate_random_transaction_data(self):
        """Function to generate random transaction data"""
        random_data = {
            "transactionId": [],
            "productId": [],
            "transactionAmount": [],
            "transactionDatetime": []
        }

        if not self.max_trans_id_location.exists():
            self.dump_max_trans_id(self.max_trans_id_location, 1)

        max_trans_id = self.read_max_trans_id(self.max_trans_id_location)

        # Create random number of rows between 0-5
        number_of_rows = random.randint(0, 5)

        for row_num in range(number_of_rows):
            # Generate random datetime
            random_date_time = datetime.datetime.now() - datetime.timedelta(
                hours=random.randint(0, 3),
                minutes=random.randint(0, 50),
                seconds=random.randint(0, 50)
            )

            # Pick random product id's index
            pid_index = random.randint(0, len(self.product_ids) - 1)
            random_data["productId"].append(self.product_ids[pid_index])
            random_data["transactionId"].append(max_trans_id + row_num)
            random_data["transactionAmount"].append(random.randint(10, 2000))
            random_data["transactionDatetime"].append(random_date_time.strftime("%Y-%m-%d %H:%M:%S"))

            max_trans_id += row_num

        self.dump_max_trans_id(self.max_trans_id_location, max_trans_id)

        # Random data file name
        file_name = "transactions_{}.csv".format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
        store_data_location = self.trans_location / file_name

        # Store random transaction data file
        pd.DataFrame(data=random_data).to_csv(store_data_location, index=False)

        logger.debug("Generated random data at : {}, with {} rows.".format(store_data_location, number_of_rows))

    def start(self):
        self.generate_random_reference_data()
        while True:
            time.sleep(self.frequency)
            self.generate_random_transaction_data()


if __name__ == '__main__':
    # Logger setup
    logging.config.dictConfig(setup_logger())

    # Command Line Argument parser
    parser = argparse.ArgumentParser(description='Command Line Argument parser')
    parser.add_argument('-f', '--frequency', default=60, type=int,
                        help='Frequency interval in seconds to generate random data')
    args = parser.parse_args()

    logging.info("Random transaction data generator is running")
    random_data_generator = GenerateRandomData(frequency=args.frequency)
    random_data_generator.start()
