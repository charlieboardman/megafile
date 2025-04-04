# Example: utils/gas_poster.py
import requests
import json
import hmac
import hashlib
import time
import os # For potentially getting secrets/URL from environment

def post_data_to_gas(transaction_data, pdf_data, gas_url, hmac_secret):
    """
    Sends transaction data (JSON) and a PDF (bytes) to the GAS web app endpoint.

    Args:
        transaction_data (dict): Dictionary containing transaction details.
                                 'authHash' will be added. 'receipt_id' should be omitted
                                 as GAS will generate and assign it based on its logic.
        pdf_data (bytes): Bytes object containing the PDF content. Can be None if no PDF.
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
    # Allow pdf_data to be None, but check later before adding to files dict if needed
    # Let GAS handle the case where pdfFile parameter is missing if pdf_data is None


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

        # IMPORTANT: Ensure 'receipt_id' is NOT sent from the client.
        # GAS is responsible for generating the final unique receipt_id based on
        # its internal logic and sheet data. Remove it if it exists.
        if 'receipt_id' in payload_data:
            print("Note: Removing client-generated 'receipt_id' before sending to GAS.")
            del payload_data['receipt_id']

        # Convert the dictionary to a JSON string
        json_payload = json.dumps(payload_data)

        # --- 3. Prepare Files for Multipart POST ---
        # The 'files' dictionary tells the requests library how to structure
        # the multipart/form-data request.
        files = {
            # 'jsonData' is sent as form data (filename=None) with specified content type
            'jsonData': (None, json_payload, 'application/json'),
        }

        # Only add the PDF file part if pdf_data actually contains data
        if pdf_data:
             # 'pdfFile' is sent as a file upload.
             # The filename 'receipt.pdf' here is arbitrary for the request structure;
             # GAS ignores this filename and generates its own based on the schema.
            files['pdfFile'] = ('receipt.pdf', pdf_data, 'application/pdf')
            print("Preparing to send JSON data and PDF file...")
        else:
             print("Preparing to send JSON data (no PDF file included)...")


        # --- 4. Send HTTP POST Request ---
        print(f"Sending POST request to GAS endpoint: {gas_url}")
        # Use a timeout (in seconds) to prevent the script from hanging indefinitely
        response = requests.post(gas_url, files=files, timeout=90) # 90 seconds timeout

        # --- 5. Process the Response from GAS ---
        # Check if the HTTP request itself was successful (e.g., 200 OK)
        # This will raise an HTTPError exception for 4xx or 5xx responses.
        response.raise_for_status()

        # If the request was successful, try to parse the JSON response body from GAS
        gas_response = response.json()

        # Check the 'status' field *within the JSON returned by GAS*
        if gas_response.get('status') == 'success':
            print("Success: GAS script processed the request successfully.")
            # Return the full success response from GAS
            return {'status': 'success', 'data': gas_response}
        else:
            # GAS reported an error in its own processing
            error_msg_from_gas = gas_response.get('message', 'Unknown error reported by GAS.')
            print(f"Error: GAS script reported an error: {error_msg_from_gas}")
            return {'status': 'error', 'message': error_msg_from_gas, 'data': gas_response}

    # --- Error Handling for the Request/Communication ---
    except requests.exceptions.Timeout:
        print("Error: The request to the GAS endpoint timed out.")
        return {'status': 'error', 'message': 'Request Timeout: No response from GAS within the time limit.'}
    except requests.exceptions.RequestException as e:
        # Handle other potential request errors (network issues, DNS errors, HTTP errors)
        print(f"Error: Failed to send request to GAS: {e}")
        error_message = f"HTTP Request Failed: {e}"
        # Include response details if available (especially for HTTP errors raised by raise_for_status)
        if e.response is not None:
            error_message += f" | Status Code: {e.response.status_code}"
            try:
                # Attempt to include the response body (might be HTML error from GAS/Google)
                error_message += f" | Response Body: {e.response.text}"
            except Exception:
                error_message += " | Response Body: (Could not read response body)"
        return {'status': 'error', 'message': error_message}
    except json.JSONDecodeError:
        # Handle cases where GAS returned a successful HTTP status (e.g., 200)
        # but the response body wasn't valid JSON (e.g., HTML output, script error message).
         print("Error: Could not decode the JSON response received from GAS. Check GAS Execution Logs.")
         raw_response = response.text if 'response' in locals() and hasattr(response, 'text') else "(No response text available)"
         return {'status': 'error', 'message': 'Invalid JSON response received from GAS.', 'raw_response': raw_response}
    except Exception as e:
        # Catch any other unexpected Python errors during the process
        print(f"An unexpected Python error occurred: {e}")
        return {'status': 'error', 'message': f'Unexpected Python error: {e}'}