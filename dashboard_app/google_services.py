import os
import json
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric, Dimension
from google.oauth2 import service_account
from googleapiclient.discovery import build

from datetime import datetime, timedelta

# Configuration
KEY_FILE_PATH = 'dashboard_app/credentials.json'  # Put your downloaded JSON key here
GA_PROPERTY_ID = os.environ.get('GA_PROPERTY_ID', 'YOUR_GA4_PROPERTY_ID')
GSC_SITE_URL = os.environ.get('GSC_SITE_URL', 'sc-domain:yourdomain.com')

def get_credentials():
    """
    Helper to get Google Credentials from Env Var (JSON string) or File.
    """
    # 1. Try Env Var with JSON content
    json_creds = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    if json_creds:
        try:
            info = json.loads(json_creds)
            return service_account.Credentials.from_service_account_info(info)
        except Exception as e:
            print(f"Error parsing GOOGLE_APPLICATION_CREDENTIALS_JSON: {e}")

    # 2. Try Local File
    if os.path.exists(KEY_FILE_PATH):
        return service_account.Credentials.from_service_account_file(KEY_FILE_PATH)

    return None

def get_ga4_data():
    """
    Fetches active users and total users from Google Analytics 4.
    """
    credentials = get_credentials()
    if not credentials:
        # Return demo/placeholder data if not configured
        return {"active_users": "0", "total_users": "0", "status": "demo"}

    try:
        client = BetaAnalyticsDataClient(credentials=credentials)

        request = RunReportRequest(
            property=f"properties/{GA_PROPERTY_ID}",
            date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
            metrics=[Metric(name="activeUsers"), Metric(name="totalUsers")],
        )

        response = client.run_report(request=request)

        data = {"status": "live"}
        if response.rows:
            data['active_users'] = response.rows[0].metric_values[0].value
            data['total_users'] = response.rows[0].metric_values[1].value
        else:
            data['active_users'] = "0"
            data['total_users'] = "0"
        
        return data
    except Exception as e:
        print(f"GA4 Error: {e}")
        return {"active_users": "Err", "total_users": "Err", "error": str(e)}

def get_gsc_data():
    """
    Fetches Clicks and Impressions from Google Search Console.
    """
    credentials = get_credentials()
    if not credentials:
        # Return demo/placeholder data if not configured
        return {"clicks": 0, "impressions": 0, "status": "demo"}

    try:
        service = build('searchconsole', 'v1', credentials=credentials)

        # Dynamic dates: Last 30 days
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        request = {
            'startDate': start_date,
            'endDate': end_date,
            'dimensions': ['date'],
            'rowLimit': 100
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
            "impressions": total_impressions,
            "status": "live"
        }
    except Exception as e:
        print(f"GSC Error: {e}")
        return {"clicks": 0, "impressions": 0, "error": str(e)}
