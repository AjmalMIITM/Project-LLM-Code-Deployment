from flask import Flask, request, jsonify
from github import Github
import os
import requests
import time
from generate_html import generate_task_html, generate_task_readme

app = Flask(__name__)

# Your secret key (verify incoming requests)
SECRET = os.environ.get('SECRET_KEY')

# Your GitHub token and repo details
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
REPO_NAME = "AjmalMIITM/Project-LLM-Code-Deployment"

# Set your unique usercode for evaluation response
USERCODE = os.environ.get('USERCODE', 'ajmalmiitm')

@app.route('/api-endpoint', methods=['POST'])
def api_endpoint():
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "No JSON body"}), 400

    # Verify secret
    if data.get("secret") != SECRET:
        return jsonify({"error": "Unauthorized"}), 403

    # Validate required fields
    required_fields = ["email", "task", "round", "nonce", "brief", "evaluation_url"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field {field}"}), 400

    # Immediately return usercode per specification
    resp = jsonify({"usercode": USERCODE})
    resp.status_code = 200

    # Generate rich files using generate_html.py
    output_dir = "./deploy_dir"
    os.makedirs(output_dir, exist_ok=True)
    generate_task_html(data, output_dir)
    generate_task_readme(data, output_dir)
    
    # Prepare files for push from generated files
    files = {}
    for filename in ["index.html", "README.md", "LICENSE"]:
        # LICENSE remains minimal, you can replace with your actual LICENSE file contents
        if filename == "LICENSE":
            files[filename] = """MIT License

Copyright (c) 2025 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell...
"""
        else:
            with open(os.path.join(output_dir, filename), "r") as f:
                files[filename] = f.read()

    # Push files to GitHub
    push_to_github(GITHUB_TOKEN, REPO_NAME, files, f"Build for task {data['task']} round {data['round']}")

    # Get latest commit SHA for notification
    g = Github(GITHUB_TOKEN)
    commit_sha = g.get_repo(REPO_NAME).get_commits()[0].sha

    pages_url = f"https://{REPO_NAME.split('/')[0].lower()}.github.io/{REPO_NAME.split('/')[1]}/"

    # Notify evaluation API asynchronously (optional enhancement)
    notify_payload = {
        "email": data["email"],
        "task": data["task"],
        "round": data["round"],
        "nonce": data["nonce"],
        "repo_url": f"https://github.com/{REPO_NAME}",
        "commit_sha": commit_sha,
        "pages_url": pages_url
    }
    notify_evaluation(data["evaluation_url"], notify_payload)

    return resp

def push_to_github(token, repo_name, files_dict, commit_message):
    g = Github(token)
    repo = g.get_repo(repo_name)
    for path, content in files_dict.items():
        try:
            file = repo.get_contents(path)
            repo.update_file(file.path, commit_message, content, file.sha)
            print(f"Updated {path}")
        except Exception:
            repo.create_file(path, commit_message, content)
            print(f"Created {path}")

def notify_evaluation(evaluation_url, payload, retries=5):
    headers = {"Content-Type": "application/json"}
    delay = 1
    for attempt in range(retries):
        try:
            r = requests.post(evaluation_url, json=payload, headers=headers)
            if r.status_code == 200:
                print("Notification successful")
                return True
            else:
                print(f"Received HTTP {r.status_code}: {r.text}")
        except Exception as e:
            print(f"Error during notification: {e}")
        print(f"Retrying in {delay} seconds...")
        time.sleep(delay)
        delay *= 2
    print("Failed to notify evaluation API after retries")
    return False

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
