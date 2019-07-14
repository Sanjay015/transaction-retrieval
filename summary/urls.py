from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('load_data/', views.transaction_data, name='load-data'),

    url(r'^transactionSummary/(?P<transaction_id>[0-9]+)/$',
        views.transaction_summary, name='transaction-summary'),

        url(r'^transactionSummaryByProducts/(?P<last_n_days>[0-9]+)/$',
        views.transaction_summary_by_product, name='transaction-summary-by-product'),

    url(r'^transactionSummaryByManufacturingCity/(?P<last_n_days>[0-9]+)/$',
        views.transaction_summary_by_manufacturing_city, name='transaction-summary-by-city'),
]

# Load reference data on server startup
views.load_reference_data()
# Load transaction data on server startup
views.transaction_data(None)
