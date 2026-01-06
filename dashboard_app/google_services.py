import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric, Dimension
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Configuration
KEY_FILE_PATH = 'dashboard_app/credentials.json'  # Put your downloaded JSON key here
GA_PROPERTY_ID = 'YOUR_GA4_PROPERTY_ID' # e.g., '123456789'
GSC_SITE_URL = 'sc-domain:yourdomain.com' # or 'https://yourdomain.com/'

def get_ga4_data():
    """
    Fetches active users and total users from Google Analytics 4.
    """
    if not os.path.exists(KEY_FILE_PATH):
        return {"error": "Missing credentials.json file"}

    try:
        credentials = service_account.Credentials.from_service_account_file(KEY_FILE_PATH)
        client = BetaAnalyticsDataClient(credentials=credentials)

        request = RunReportRequest(
            property=f"properties/{GA_PROPERTY_ID}",
            date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
            metrics=[Metric(name="activeUsers"), Metric(name="totalUsers")],
        )

        response = client.run_report(request=request)

        data = {}
        if response.rows:
            data['active_users'] = response.rows[0].metric_values[0].value
            data['total_users'] = response.rows[0].metric_values[1].value
        
        return data
    except Exception as e:
        return {"error": str(e)}

def get_gsc_data():
    """
    Fetches Clicks and Impressions from Google Search Console.
    """
    if not os.path.exists(KEY_FILE_PATH):
        return {"error": "Missing credentials.json file"}

    try:
        credentials = service_account.Credentials.from_service_account_file(KEY_FILE_PATH)
        service = build('searchconsole', 'v1', credentials=credentials)

        # Request data for the last 30 days
        request = {
            'startDate': '2023-12-01', # You should calculate this dynamically in production
            'endDate': '2024-01-01',   # You should calculate this dynamically in production
            'dimensions': ['date'],
            'rowLimit': 10
        }

        response = service.searchanalytics().query(siteUrl=GSC_SITE_URL, body=request).execute()
        
        # Process response to sum up clicks/impressions
        total_clicks = 0
        total_impressions = 0
        
        if 'rows' in response:
            for row in response['rows']:
                total_clicks += row['clicks']
                total_impressions += row['impressions']
                
        return {
            "clicks": total_clicks,
            "impressions": total_impressions
        }
    except Exception as e:
        return {"error": str(e)}
