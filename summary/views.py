import datetime
import logging
import os
import config
import pandas as pd

from django.http import JsonResponse
from utils.utils import transaction_files, move_transaction_file, get_root

logger = logging.getLogger("app")

DATA = {}


def calculate_last_n_days(last_n_days: int) -> datetime:
    """Calculate date interval
        Args:
            last_n_days: Go back to number of days from current date
        Returns:
            starting date(which is n days back from current date)
    """
    today = datetime.datetime.now().replace(minute=0, hour=0, second=0, microsecond=0)
    from_date = today - datetime.timedelta(days=last_n_days)
    return from_date


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
    # Load reference mapping
    load_reference_data()

    # Get transaction files to load
    trans_files = transaction_files(load_processed=True if "transaction_data" not in DATA else False)
    for trans_file in trans_files:
        if os.path.getsize(trans_file) > 0:
            data = pd.read_csv(trans_file, parse_dates=[config.TRANS_DATE_COL])
            # Adding product mapping to transaction data
            data = pd.merge(data, DATA["reference_data"], on=["productId"], how="left")

            DATA["transaction_data"] = data if "transaction_data" not in DATA else DATA["transaction_data"].append(data)
            logger.debug("Data loaded from file: {}".format(trans_file))
        else:
            logger.warning("File: {} is an empty file".format(trans_file))
        move_transaction_file(trans_file)
        logger.debug("Moved file from : {} to processed location".format(trans_file))

    # If data files are not available, lets create empty data frame
    if "transaction_data" not in DATA:
        DATA["transaction_data"] = pd.DataFrame(columns=config.TOTAL_COLS)

    return JsonResponse({"status": "Data loaded successfully"})


def transaction_summary(request, transaction_id):
    """Generate full detail of transaction"""
    data = DATA["transaction_data"][DATA["transaction_data"]["transactionId"] == int(transaction_id)]
    if not len(data):
        return JsonResponse({"summary": "No records found"})

    data = data[["transactionId", "productName", "transactionAmount", "transactionDatetime"]]
    data["transactionDatetime"] = data["transactionDatetime"].apply(lambda x: x.strftime("%Y-%m-%d %H:%M:%S"))
    return JsonResponse({"summary": data.to_dict(orient="records")})


def transaction_summary_by_product(request, last_n_days):
    """Get transaction summary by products in last n days from current day"""
    from_date = calculate_last_n_days(int(last_n_days))
    data = DATA["transaction_data"][DATA["transaction_data"][config.TRANS_DATE_COL] >= from_date]
    if not len(data):
        return JsonResponse({"summary": "No records found"})

    data = data[["productName", "transactionAmount"]]
    data = data.rename(columns={"transactionAmount": "totalAmount"})
    data = data.groupby(["productName"], as_index=False).agg({"totalAmount": sum})
    return JsonResponse({"summary": data.to_dict(orient="records")})


def transaction_summary_by_manufacturing_city(request, last_n_days):
    """Get transaction summary by manufacturing city in last n days from current day"""
    from_date = calculate_last_n_days(int(last_n_days))
    data = DATA["transaction_data"][DATA["transaction_data"][config.TRANS_DATE_COL] >= from_date]
    if not len(data):
        return JsonResponse({"summary": "No records found"})

    data = data[["productManufacturingCity", "transactionAmount"]]
    data = data.rename(columns={"productManufacturingCity": "cityName", "transactionAmount": "totalAmount"})
    data = data.groupby(["cityName"], as_index=False).agg({"totalAmount": sum})
    return JsonResponse({"summary": data.to_dict(orient="records")})
