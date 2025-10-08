from flask import Flask, request, jsonify
from github import Github
import os
import requests
import time

app = Flask(__name__)

# Your secret key (verify incoming requests)
SECRET = "a9fd43c6-a7fa-400e-9208-39f984876201"

# Your GitHub token and repo details
GITHUB_TOKEN = "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"
REPO_NAME = "AjmalMIITM/Project-LLM-Code-Deployment"

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

    email = data["email"]
    task = data["task"]
    round_num = data["round"]
    nonce = data["nonce"]
    brief = data["brief"]
    evaluation_url = data["evaluation_url"]

    # Generate minimal app content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head><title>Task App</title></head>
    <body>
      <h1>Task Brief</h1>
      <p>{brief}</p>
    </body>
    </html>
    """

    # Files to push to GitHub
    files = {
        "index.html": html_content,
        "README.md": f"# {task}\n\nThis app does: {brief}",
        # Simple MIT License placeholder text
        "LICENSE": """MIT License

Copyright (c) 2025 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell...
"""
    }

    # Push files to GitHub
    push_to_github(GITHUB_TOKEN, REPO_NAME, files, f"Build for task {task} round {round_num}")

    # Get latest commit SHA
    g = Github(GITHUB_TOKEN)
    commit_sha = g.get_repo(REPO_NAME).get_commits()[0].sha

    pages_url = f"https://{REPO_NAME.split('/')[0].lower()}.github.io/{REPO_NAME.split('/')[1]}/"

    # Notify evaluation API
    notify_payload = {
        "email": email,
        "task": task,
        "round": round_num,
        "nonce": nonce,
        "repo_url": f"https://github.com/{REPO_NAME}",
        "commit_sha": commit_sha,
        "pages_url": pages_url
    }

    notify_evaluation(evaluation_url, notify_payload)

    return jsonify({"status": "OK"}), 200

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
    app.run(port=8080)
