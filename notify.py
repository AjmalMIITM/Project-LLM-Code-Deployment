import requests
import time

def notify_evaluation_api(evaluation_url, payload, max_retries=5):
    headers = {"Content-Type": "application/json"}
    delay = 1  # retry delay in seconds
    for attempt in range(max_retries):
        try:
            response = requests.post(evaluation_url, json=payload, headers=headers)
            if response.status_code == 200:
                print("Notification successful")
                return True
            else:
                print(f"Received HTTP {response.status_code}: {response.text}")
        except Exception as e:
            print(f"Error during notification: {e}")

        print(f"Retrying in {delay} seconds...")
        time.sleep(delay)
        delay *= 2  # exponential backoff

    print("Failed to notify evaluation API after retries")
    return False


# ====== FILL IN YOUR DATA HERE ======

evaluation_url = "https://example.com/notify"  # Replace this with your actual evaluation URL from the request

payload = {
    "email": "student@example.com",  # Your email
    "task": "captcha-solver-abc",    # Task ID from request
    "round": 1,                      # The round (1 for first submit)
    "nonce": "xyz123",               # Nonce value from request
    "repo_url": "https://github.com/AjmalMIITM/Project-LLM-Code-Deployment",
    "commit_sha": "YOUR_COMMIT_SHA_HERE",  # Latest commit SHA from GitHub (see next step)
    "pages_url": "https://ajmalmiitm.github.io/Project-LLM-Code-Deployment/"
}

# Uncomment the next line after editing the above variables
# notify_evaluation_api(evaluation_url, payload)
