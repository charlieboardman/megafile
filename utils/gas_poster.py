# utils/gas_poster.py
import requests
import json
import hmac
import hashlib
import time
import os # For potentially getting secrets/URL from environment

def post_data_to_gas(transaction_data, receipt_base64, gas_url, hmac_secret):
    """
    Sends transaction data (JSON) including base64 PDF to the GAS web app endpoint.

    Args:
        transaction_data (dict): Dictionary containing transaction details.
                                 'authHash' and 'receipt_base64' will be added/updated.
                                 'receipt_id' will be removed if present.
        receipt_base64 (str): Base64 encoded string of the PDF receipt.
        gas_url (str): The URL of the deployed Google Apps Script web app.
        hmac_secret (str): The shared secret key for HMAC authentication.

    Returns:
        dict: A dictionary containing the status ('success' or 'error')
              and the response data/message from GAS.
    """
    # --- Input Validation ---
    if not hmac_secret:
         print("Client Error: HMAC secret was not provided.")
         return {'status': 'error', 'message': 'Client Configuration Error: HMAC secret missing.'}
    if not gas_url:
         print("Client Error: GAS URL was not provided.")
         return {'status': 'error', 'message': 'Client Configuration Error: GAS URL missing.'}
    if receipt_base64 is None:
         # Decide if sending without a receipt is allowed. Assuming yes for now.
         # GAS script might need logic to handle transactions without receipts if this occurs.
         print("Warning: No receipt Base64 data provided.")
         # You might want to return an error here if a receipt is always required:
         # return {'status': 'error', 'message': 'Client Error: Receipt data is missing.'}


    try:
        # --- 1. Generate Authentication Hash ---
        time_step = 30 # Must match GAS config (TIME_STEP)
        counter = int(time.time() // time_step)
        message = str(counter).encode('utf-8')
        # Calculate HMAC-SHA256 using the secret key and the counter string
        h = hmac.new(key=hmac_secret.encode('utf-8'), msg=message, digestmod=hashlib.sha256)
        auth_hash = h.hexdigest()
        print(f"Generated authHash: {auth_hash} for counter: {counter}")

        # --- 2. Prepare JSON Payload ---
        # Make a copy to avoid modifying the original dict if it's reused elsewhere
        payload_data = transaction_data.copy()
        # Add the authentication hash required by the GAS script
        payload_data['authHash'] = auth_hash

        # Add the base64 string representation of the pdf into the payload
        # Ensure it's added even if None, GAS needs to handle potentially missing field if needed
        payload_data['base64File'] = receipt_base64 # Match key expected by GAS

        # IMPORTANT: Ensure 'receipt_id' is NOT sent from the client.
        # GAS is responsible for generating the final unique receipt_id. Remove it.
        if 'receipt_id' in payload_data:
            print("Note: Removing client-generated 'receipt_id' before sending to GAS.")
            del payload_data['receipt_id']

        # Convert the final dictionary to a JSON string
        json_payload_string = json.dumps(payload_data)


        # --- 3. Prepare Data for POST Request ---
        # GAS doPost expects parameters like form data. We send the JSON string
        # as the value associated with the key 'jsonData'.
        post_form_data = {'jsonData': json_payload_string}

        # Set headers to indicate form data submission (optional but good practice)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        # --- 4. Send HTTP POST Request ---
        print(f"Sending POST request to GAS endpoint: {gas_url}")
        # Use the 'data' parameter for form-encoded data, not 'files'.
        response = requests.post(gas_url, data=post_form_data, headers=headers, timeout=90) # 90 seconds timeout

        # --- 5. Process the Response from GAS ---
        response.raise_for_status() # Check for HTTP errors (4xx or 5xx)

        gas_response = response.json() # Parse JSON response from GAS

        # Check the 'status' field *within the JSON returned by GAS*
        if gas_response.get('status') == 'success':
            print("Success: GAS script processed the request successfully.")
            return {'status': 'success', 'data': gas_response}
        else:
            error_msg_from_gas = gas_response.get('message', 'Unknown error reported by GAS.')
            print(f"Error: GAS script reported an error: {error_msg_from_gas}")
            return {'status': 'error', 'message': error_msg_from_gas, 'data': gas_response}

    # --- Error Handling for the Request/Communication ---
    except requests.exceptions.Timeout:
        print("Error: The request to the GAS endpoint timed out.")
        return {'status': 'error', 'message': 'Request Timeout: No response from GAS within the time limit.'}
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to send request to GAS: {e}")
        error_message = f"HTTP Request Failed: {e}"
        if e.response is not None:
            error_message += f" | Status Code: {e.response.status_code}"
            try:
                error_message += f" | Response Body: {e.response.text}"
            except Exception:
                error_message += " | Response Body: (Could not read response body)"
        return {'status': 'error', 'message': error_message}
    except json.JSONDecodeError:
         print("Error: Could not decode the JSON response received from GAS. Check GAS Execution Logs.")
         raw_response = response.text if 'response' in locals() and hasattr(response, 'text') else "(No response text available)"
         return {'status': 'error', 'message': 'Invalid JSON response received from GAS.', 'raw_response': raw_response}
    except Exception as e:
        print(f"An unexpected Python error occurred: {e}")
        return {'status': 'error', 'message': f'Unexpected Python error: {e}'}