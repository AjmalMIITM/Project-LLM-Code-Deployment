from flask import Flask, request, jsonify
from github import Github
import os
import requests
import time
import shutil
import logging
from generate_html import generate_task_html, generate_task_readme

# Set up logging (creates logs.txt on server only, not in GitHub)
logging.basicConfig(
    filename='logs.txt',
    filemode='a',
    format='%(asctime)s %(levelname)s %(message)s',
    level=logging.INFO
)

app = Flask(__name__)

SECRET = os.environ.get('SECRET_KEY')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
REPO_NAME = "AjmalMIITM/Project-LLM-Code-Deployment"
USERCODE = os.environ.get('USERCODE', 'ajmalmiitm')

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

        # 1. Generate HTML and README in ./deploy_dir
        output_dir = "./deploy_dir"
        os.makedirs(output_dir, exist_ok=True)
        logging.info(f"Generating HTML and README for task: {data['task']}")
        generate_task_html(data, output_dir)
        generate_task_readme(data, output_dir)

        # 2. Move generated files to project root (overwrite)
        for filename in ["index.html", "README.md"]:
            shutil.copyfile(os.path.join(output_dir, filename), filename)
        # Always generate LICENSE in the root
        with open("LICENSE", "w") as f:
            f.write("""MIT License

Copyright (c) 2025 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell...
""")

        # 3. Read files from root for push
        files = {}
        for filename in ["index.html", "README.md", "LICENSE"]:
            with open(filename, "r") as f:
                files[filename] = f.read()

        # 4. Push to GitHub
        logging.info(f"Pushing files to GitHub: {list(files.keys())}")
        push_to_github(GITHUB_TOKEN, REPO_NAME, files, f"Build for task {data['task']} round {data['round']}")

        # 5. Notify evaluation API
        g = Github(GITHUB_TOKEN)
        commit_sha = g.get_repo(REPO_NAME).get_commits()[0].sha
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
        
        logging.info(f"Successfully processed request for task: {data['task']}")
        return resp
        
    except Exception as e:
        logging.error(f"Unexpected error in api_endpoint: {str(e)}")
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
