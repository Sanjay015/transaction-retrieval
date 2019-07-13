from django.urls import path
from .views import transaction_data, load_reference_data

urlpatterns = [
    path('load_data/', transaction_data, name='load-data'),
]
# Load reference data on server startup
load_reference_data()
# Load transaction data on server startup
transaction_data(None)
