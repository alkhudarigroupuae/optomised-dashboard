from import_cakes import wcapi
import json
import sys

TARGET_EMAIL = "contact@avtrav.net"

def update_email_settings():
    print(f"Updating Email Recipients to: {TARGET_EMAIL}", flush=True)
    
    # Group IDs
    groups = ['email_new_order', 'email_cancelled_order', 'email_failed_order']
    
    for group_id in groups:
        print(f"\nProcessing {group_id}...", flush=True)
        
        try:
            # 1. Get Group Settings
            response = wcapi.get(f"settings/{group_id}")
            if response.status_code != 200:
                print(f"  Failed to get group: {response.status_code}", flush=True)
                continue
                
            settings = response.json()
            
            # 2. Find Recipient Setting ID
            recipient_setting = None
            for s in settings:
                if 'recipient' in s.get('id', ''):
                    recipient_setting = s
                    break
            
            if recipient_setting:
                s_id = recipient_setting.get('id')
                current_val = recipient_setting.get('value')
                print(f"  Found Recipient Setting: {s_id}", flush=True)
                print(f"  Current Value: '{current_val}'", flush=True)
                
                if current_val != TARGET_EMAIL:
                    print(f"  Updating to '{TARGET_EMAIL}'...", flush=True)
                    # Try PUT to settings/{group_id}/{s_id}
                    endpoint = f"settings/{group_id}/{s_id}"
                    
                    # Note: value must be wrapped in object usually? Or just data?
                    # API v3: PUT /settings/{group_id}/{id} with body { "value": "..." }
                    up_resp = wcapi.put(endpoint, {"value": TARGET_EMAIL})
                    
                    if up_resp.status_code == 200:
                        print("  Success! Updated.", flush=True)
                        # Verify
                        print(f"  New Value: {up_resp.json().get('value')}", flush=True)
                    else:
                        print(f"  Failed Update: {up_resp.status_code}", flush=True)
                        print(up_resp.text, flush=True)
                else:
                    print("  Already set correctly.", flush=True)
            else:
                print("  No 'recipient' setting found in this group.", flush=True)
                
        except Exception as e:
            print(f"  Error: {e}", flush=True)

if __name__ == "__main__":
    update_email_settings()
