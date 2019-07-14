"""Config modules for static values"""
# Relative location under root folder
DATA_FILE_LOCATION = "data"

# Data file extension
DATA_FILE_EXTENSION = ".csv"

# Create folder to move processed file(within data file location folder)
PROCESSED_FOLDER_NAME = "processed"

# Reference data file location
REFERENCE_DATA_FILE = "data/reference/reference.csv"

# Transaction data datetime column
TRANS_DATE_COL = "transactionDatetime"

# Total expected columns in transaction data after merging with reference file
TOTAL_COLS = ["transactionId", "productId", "transactionAmount", "transactionDatetime",
              "productName", "productManufacturingCity"]

# Expected columns in transaction data
TRANS_COLS = ["transactionId", "productId", "transactionAmount", "transactionDatetime"]

# Expected columns in reference data
REF_COLS = ["productId", "productName", "productManufacturingCity"]

# Data load URL pattern
DATA_LOAD_URL_PATTERN = "transaction/load_data/"
