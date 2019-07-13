import datetime
from django.http import JsonResponse
import logging
import os
import pandas as pd

from utils import config
from utils.utils import transaction_files, move_transaction_file, get_root

logger = logging.getLogger("app")

DATA = {}


def load_reference_data():
    """Load and cache reference data"""
    reference_file = os.path.join(get_root(), config.REFERENCE_DATA_FILE)
    updated_at = datetime.datetime.fromtimestamp(os.path.getmtime(reference_file))

    # Update reference file modified time and clear the cache if file got updated
    if DATA.get("reference_updated_at", updated_at) > updated_at:
        DATA.pop("reference_data")
        DATA.pop("reference_updated_at")

    if "reference_data" not in DATA:
        DATA["reference_data"] = pd.read_csv(reference_file)
        DATA["reference_updated_at"] = datetime.datetime.fromtimestamp(os.path.getmtime(reference_file))


def transaction_data(request):
    """Load transaction data"""
    # Get transaction files to load
    trans_files = transaction_files(load_processed=True if "transaction_data" not in DATA else False)
    for trans_file in trans_files:
        if os.path.getsize(trans_file) > 0:
            data = pd.read_csv(trans_file, parse_dates=[config.TRANS_DATE_COL])
            DATA["transaction_data"] = data if "transaction_data" not in DATA else DATA["transaction_data"].append(data)
            logger.debug("Data loaded from file: {}".format(trans_file))
        else:
            logger.warning("File: {} is an empty file".format(trans_file))
        move_transaction_file(trans_file)
        logger.debug("Moved file from : {} to processed location".format(trans_file))
    return JsonResponse({"status": "Data loaded successfully"})
