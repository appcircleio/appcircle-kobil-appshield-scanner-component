#!/usr/bin/env python3
import time
import os
from urllib.parse import urljoin
import sys, site
import subprocess
import importlib

# Params
BASE_URL = "https://api.appshield.kobil.com"

def print_colored(message, level="info"):
    """
    Prints a colored message to the console using ANSI escape codes.
    Supported levels: success (green), warn (yellow), info (blue), error (red)
    """
    colors = {
        "success": "\033[32m",  # Green
        "warn": "\033[33m",     # Yellow
        "info": "\033[34m",     # Blue
        "error": "\033[31m"     # Red
    }
    reset = "\033[0m"

    color = colors.get(level.lower(), "\033[0m")
    print(f"{color}{message}{reset}")

def set_env_var_in_file(key, value):
    try:
        
        env_path = os.getenv("AC_ENV_FILE_PATH")
        if not env_path or not os.path.exists(env_path):
            raise FileNotFoundError(f"AC_ENV_FILE_PATH is not set or file not found: {env_path}")

        line = key + "=" + value + "\n"
        print_colored(f"Key: {key}, Value: {value}, Path: {env_path}")

        # Write back
        with open(env_path, "a+") as f:
            f.write(line)

        print_colored(f"✅ Updated {key} in {env_path}", level="success")
    except Exception as e:
        print_colored(f"@@[error] [SET_ENV_VAR_IN_FILE] ❌ Failed to update {key} in {env_path}: {e}", level="error")
        return None


# Upload & Poll helpers
def upload_and_start_test(file_path, user_email, api_key):
    try:
        upload_url = urljoin(BASE_URL, "/upload_and_test_app_parallel")
        headers = {"secret-key": api_key}
        data = {
            "user_email": user_email
        }

        if not os.path.exists(file_path):
            raise Exception(f"Error: File not found at {file_path}")

        files = None
        
        f = open(file_path, "rb")
        files = {"file": (os.path.basename(file_path), f)}
        
        print_colored(f"[UPLOAD_AND_START_TEST] Uploading {file_path} to {upload_url}...")
        response = requests.post(upload_url, headers=headers, data=data, files=files, timeout=300, verify=False)
        response.raise_for_status()
        
        print_colored(f"[UPLOAD_AND_START_TEST] Successfully uploaded {file_path} to {upload_url}", level="success")

        response_data = response.json()
        session_id = response_data.get("session_id")
        if not session_id:
            raise Exception(f"Error: Failed to start test. Response: {response_data}")
        
        estimated_wait_minutes = 0
        if "queued" in response_data.get("message", "").lower():
            estimated_wait_minutes = response_data.get("estimated_wait_minutes", 0)
            print_colored(f"[UPLOAD_AND_START_TEST] Test queued. Estimated wait time: {estimated_wait_minutes} minutes")
    
        else:
            print_colored(f"[UPLOAD_AND_START_TEST] Successfully started test session: {session_id}", level="success")
        return session_id, estimated_wait_minutes

    except requests.exceptions.Timeout:
        raise Exception("UPLOAD_TIMEOUT: Upload request timed out")

    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else "unknown"
        try:
            err_json = e.response.json()
            message = err_json.get("message", "").lower()
            if "already protected" in message:
                print_colored("App already protected by KOBIL.")
                return True
        except Exception:
            # Fallback if JSON parse fails
            pass

        return None

    except requests.exceptions.RequestException as e:
        print_colored(f"@@[error] [UPLOAD_AND_START_TEST] Request exception during upload: {str(e)}", level="error")
        return None

    except Exception as e:
        print_colored(f"@@[error] [UPLOAD_AND_START_TEST] Unexpected error during upload: {str(e)}", level="error")
        return None
    finally:
        if f:
            f.close()

def poll_session_status(session_id, estimated_wait_minutes, api_key, poll_interval=10):
    
    status_url = urljoin(BASE_URL, f"/get-session-status?session_id={session_id}")
    headers = {"secret-key": api_key}
    status_arr = ["queued", "active", "completed", "not exist"]

    max_wait_seconds = estimated_wait_minutes*60 if estimated_wait_minutes > 0 else 60000
    wait_time_seconds = 0

    while True:
        try:
            if wait_time_seconds > max_wait_seconds:
                raise Exception(f"Max wait time ({max_wait_seconds} seconds) exceeded for session {session_id}")

            response = requests.get(status_url, headers=headers, timeout=60, verify=False)
            response.raise_for_status()
            
            status_data = response.json()
            status = status_data.get("status")

            if status not in status_arr:
                raise Exception(f"Unexpected status: {status}")
            
            if status == "not exist":
                raise Exception(f"Session {session_id} does not exist")
            
            if status == "completed":
                print_colored(f"[POLL_SESSION_STATUS] Session {session_id} completed", level="success")
                return True

            print_colored(f"[POLL_SESSION_STATUS] Session {session_id} status: {status}, waiting...")
            time.sleep(poll_interval)
            wait_time_seconds += poll_interval
        
        except requests.exceptions.RequestException as e:
            print_colored(f"[POLL_SESSION_STATUS] An error occurred while polling for status: {str(e)}", level='warn')
            print_colored(f"[POLL_SESSION_STATUS] Retrying in {poll_interval} seconds...")
            time.sleep(poll_interval)
            wait_time_seconds += poll_interval
        except Exception as e:
            print_colored(f"@@[error] [POLL_SESSION_STATUS] Unexpected error during poll: {str(e)}", level="error")
            return None

# Fetch results directly from DB
def get_session_results(session_id, api_key):
    status_url = urljoin(BASE_URL, f"/get-session-results?session_id={session_id}")
    headers = {"secret-key": api_key}
    try:
        print_colored(f"Fetching test results for session {session_id}...")
        response = requests.get(status_url, headers=headers, timeout=60, verify=False)
        response.raise_for_status()
        
        status_data = response.json()
        # print_colored(status_data)
        status = status_data.get("status")

        if status != "completed":
            raise Exception(f"Session {session_id} is not completed. Status: {status}")
        
        is_app_secure = status_data.get("is_app_secure")
        if is_app_secure is None:
            raise Exception(f"Failed to fetch is_app_secured for session {session_id}")
        
        return is_app_secure

    except requests.exceptions.RequestException as e:
        print_colored(f"@@[error] [GET_SESSION_RESULTS] An error occurred while polling for status: {str(e)}", level='error')
        return None
    except Exception as e:
        print_colored(f"@@[error] [GET_SESSION_RESULTS] Unexpected error during fetching session results: {str(e)}", level="error")
        return None

    

# Per-test runner
def run_scanner(file_path=None, user_email=None, api_key=None):
    is_app_secure = None
    try:
        # Check parameters first
        if not file_path:
            raise Exception("FILE_PATH_REQUIRED: File path is required")
        
        if not api_key:
            raise Exception("api_key_REQUIRED: Secret key is required")
        
        if not user_email:
            user_email = "efe.erdil@kobil.com"
            print_colored(f"[RUN_SCANNER] User e-mail not provided, using default: {user_email}", level="warn")
        
        if not os.path.exists(file_path):
            raise Exception(f"FILE_NOT_FOUND: File {file_path} not found")
        
        session_id, estimated_wait_minutes = upload_and_start_test(
            file_path=file_path,
            user_email=user_email,
            api_key=api_key
        )

        # App protected case
        if session_id is True:
            print_colored("App already protected by KOBIL.")
            is_app_secure = True
            return True
        
        # Upload failed due to some exception
        if not session_id:
            raise Exception("UPLOAD_FAILED")

        res = poll_session_status(session_id, estimated_wait_minutes, api_key=api_key)
        if not res:
            raise Exception("GET_SESSION_STATUS_FAILED")
        
        is_app_secure = get_session_results(session_id, api_key=api_key)

        if is_app_secure is None:
            raise Exception("GET_SESSION_RESULTS_FAILED")
        
        print_colored("Test OK, app is secured" if is_app_secure else "Test OK, app is NOT secured", level="success")

        if is_app_secure is False:
            raise Exception("APP IS NOT SECURE!")
        
        print_colored(f"Test OK, APP IS SECURE, Setting AC_APPSHIELD_IS_APP_SECURE to true...", level="success")
        return is_app_secure
    except Exception as e:
        print_colored(f"@@[error] [RUN_SCANNER] Error: {str(e)}", level="error")
        sys.exit(1)
        return None
    finally:
        print_colored(f"Setting AC_APPSHIELD_IS_APP_SECURE to {is_app_secure}")
        set_env_var_in_file("AC_APPSHIELD_IS_APP_SECURE", "null" if is_app_secure is None else str(is_app_secure).lower())
       

if __name__ == "__main__":
    try:
        print_colored("Installing dependencies...")

        subprocess.run([
            sys.executable, "-m", "pip", "install",
            "requests", "urllib3", "--break-system-packages", "--user"
        ], check=True)

        # reload import system (optional but safer)
        importlib.invalidate_caches()

        sys.path.append(site.getusersitepackages())

        # now import
        import requests, urllib3

        print("✅ Requests and urllib3 imported successfully!", requests.__version__, urllib3.__version__)
        
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        DEFAULT_FILE_PATH = os.getenv("AC_APPSHIELD_APP_FILE_PATH")
        DEFAULT_EMAIL = os.getenv("AC_APPSHIELD_USER_MAIL")
        API_KEY = os.getenv("AC_APPSHIELD_API_KEY")

        # print(DEFAULT_EMAIL, DEFAULT_FILE_PATH)
        print_colored(run_scanner(file_path=DEFAULT_FILE_PATH, user_email=DEFAULT_EMAIL, api_key=API_KEY))

    except Exception as e:
        print_colored(f"@@[error] [MAIN] Error: {str(e)}", level="error")
        sys.exit(1)