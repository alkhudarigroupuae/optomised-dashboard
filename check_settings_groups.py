from import_cakes import wcapi
import json
import sys

def list_settings_groups():
    print("Listing Settings Groups...", flush=True)
    try:
        response = wcapi.get("settings")
        print(f"Status Code: {response.status_code}", flush=True)
        if response.status_code == 200:
            groups = response.json()
            print(f"Found {len(groups)} groups.", flush=True)
            for g in groups:
                print(f"- ID: {g.get('id')}, Label: {g.get('label')}", flush=True)
        else:
            print(f"Failed: {response.status_code}", flush=True)
            print(response.text, flush=True)
    except Exception as e:
        print(f"Error: {e}", flush=True)

if __name__ == "__main__":
    list_settings_groups()
