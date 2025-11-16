from flask import Flask, request, jsonify
from github import Github
import os
import sys
import requests
import time
import shutil
import logging
from generate_html import generate_task_files

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler("logs.txt"),
        logging.StreamHandler(sys.stdout)
    ]
)

app = Flask(__name__)

SECRET = os.environ.get('SECRET_KEY')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
REPO_NAME = "AjmalMIITM/Project-LLM-Code-Deployment"
USERCODE = os.environ.get('USERCODE', 'ajmalmiitm')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/api-endpoint', methods=['POST'])
def api_endpoint():
    try:
        data = request.get_json(force=True)
        logging.info(f"Received POST request: {data}")
        
        if not data:
            logging.error("No JSON body received")
            return jsonify({"error": "No JSON body"}), 400

        # Verify secret
        if data.get("secret") != SECRET:
            logging.error("Unauthorized access attempt")
            return jsonify({"error": "Unauthorized"}), 403

        required_fields = ["email", "task", "round", "nonce", "brief", "evaluation_url"]
        for field in required_fields:
            if field not in data:
                logging.error(f"Missing field: {field}")
                return jsonify({"error": f"Missing field {field}"}), 400

        resp = jsonify({"usercode": USERCODE})
        resp.status_code = 200

        output_dir = "./deploy_dir"
        os.makedirs(output_dir, exist_ok=True)

        logging.info(f"Generating task files for: {data['task']}")
        generate_task_files(data, output_dir)

        # Validate ONLY index.html (most critical file from LLM)
        index_path = os.path.join(output_dir, "index.html")
        if not os.path.isfile(index_path) or os.path.getsize(index_path) == 0:
            logging.error("Generated file index.html missing or empty")
            return jsonify({"error": "File index.html missing or empty"}), 500
        
        # Copy index.html to project root
        shutil.copyfile(index_path, "index.html")
        
        # Write MIT License
        with open("LICENSE", "w") as f:
            f.write("""MIT License

Copyright (c) 2025 AjmalMIITM

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""")

        # Read files for GitHub push (only index.html and LICENSE)
        files = {}
        with open("index.html", "r", encoding="utf-8") as f:
            files["index.html"] = f.read()
        with open("LICENSE", "r", encoding="utf-8") as f:
            files["LICENSE"] = f.read()

        logging.info(f"Pushing files to GitHub: {list(files.keys())}")
        push_to_github(GITHUB_TOKEN, REPO_NAME, files, f"Build for task {data['task']} round {data['round']}")

        # Notify evaluation API with retries
        from github import GithubException
        try:
            g = Github(GITHUB_TOKEN)
            repo = g.get_repo(REPO_NAME)
            commit_sha = repo.get_commits()[0].sha
            pages_url = f"https://{REPO_NAME.split('/')[0].lower()}.github.io/{REPO_NAME.split('/')[1]}/"

            notify_payload = {
                "email": data["email"],
                "task": data["task"],
                "round": data["round"],
                "nonce": data["nonce"],
                "repo_url": f"https://github.com/{REPO_NAME}",
                "commit_sha": commit_sha,
                "pages_url": pages_url
            }
            logging.info(f"Sending notification to: {data['evaluation_url']}")
            notify_evaluation(data["evaluation_url"], notify_payload)
        except GithubException as ge:
            logging.error(f"GitHub Exception: {ge}")

        logging.info(f"Successfully processed request for task: {data['task']}")
        return resp
        
    except Exception as e:
        logging.error(f"Unexpected error in api_endpoint: {str(e)}")
        print(f"Exception in /api-endpoint: {str(e)}", flush=True)
        return jsonify({"error": "Server error"}), 500


def push_to_github(token, repo_name, files_dict, commit_message):
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        for path, content in files_dict.items():
            try:
                file = repo.get_contents(path)
                repo.update_file(file.path, commit_message, content, file.sha)
                logging.info(f"Updated {path}")
                print(f"Updated {path}")
            except Exception:
                repo.create_file(path, commit_message, content)
                logging.info(f"Created {path}")
                print(f"Created {path}")
    except Exception as e:
        logging.error(f"Error in push_to_github: {str(e)}")

def notify_evaluation(evaluation_url, payload, retries=5):
    headers = {"Content-Type": "application/json"}
    delay = 1
    for attempt in range(retries):
        try:
            r = requests.post(evaluation_url, json=payload, headers=headers)
            if r.status_code == 200:
                logging.info("Notification successful")
                print("Notification successful")
                return True
            else:
                logging.warning(f"Received HTTP {r.status_code}: {r.text}")
                print(f"Received HTTP {r.status_code}: {r.text}")
        except Exception as e:
            logging.error(f"Error during notification: {e}")
            print(f"Error during notification: {e}")
        logging.info(f"Retrying notification in {delay} seconds...")
        print(f"Retrying in {delay} seconds...")
        time.sleep(delay)
        delay *= 2
    logging.error("Failed to notify evaluation API after retries")
    print("Failed to notify evaluation API after retries")
    return False


if __name__ == '__main__':
    logging.info("Starting Flask application")
    app.run(host='0.0.0.0', port=8080)
