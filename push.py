from github import Github

# Your GitHub personal access token
GITHUB_TOKEN = "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"

# Your repository full name
REPO_NAME = "AjmalMIITM/Project-LLM-Code-Deployment"

# Initialize Github object
g = Github(GITHUB_TOKEN)

# Get repository
repo = g.get_repo(REPO_NAME)

def create_or_update_file(file_path, commit_msg):
    try:
        file = repo.get_contents(file_path)
        with open(file_path, "r") as f:
            content = f.read()
        repo.update_file(file.path, commit_msg, content, file.sha)
        print(f"Updated {file_path}")
    except:
        with open(file_path, "r") as f:
            content = f.read()
        repo.create_file(file_path, commit_msg, content)
        print(f"Created {file_path}")

# Push files
for file in ["index.html", "README.md", "LICENSE"]:
    create_or_update_file(file, f"Add or update {file}")
