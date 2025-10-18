import requests
import os

AIPIPE_TOKEN = os.environ.get("AIPIPE_TOKEN")
AIPIPE_URL = "https://aipipe.org/openrouter/v1/chat/completions"
MODEL = "openai/gpt-4o-mini"  # or any strong model you have quota for

def get_code_from_llm(brief, checks, attachments):
    prompt = f"""
You are an expert software engineer and code generator.

TASK:
{brief}

REQUIREMENTS:
- Analyze the brief and determine the correct programming language, framework, and file type needed.
- If the task is a web app, generate a complete HTML/JS/CSS file.
- If the task is a script, generate a complete Python, Bash, or other script as needed.
- If the task is an API, generate a complete Flask/FastAPI app.
- If the task is a config, generate a valid Dockerfile, YAML, or JSON as required.
- If the task is a document, generate Markdown or HTML as needed.
- If there are attachments, reference them in the code as required.
- Pass all checks listed below.

CHECKS:
{chr(10).join(f'- {check}' for check in checks)}

OUTPUT:
- Output only the complete code for the required file(s), with no explanation or extra text.
- Use the correct file extension and structure for the task.
"""
    headers = {
        "Authorization": f"Bearer {AIPIPE_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful AI code generator."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 1400
    }

    try:
        resp = requests.post(AIPIPE_URL, headers=headers, json=payload, timeout=60)
        result = resp.json()
        if "choices" in result and len(result["choices"]) > 0:
            return result['choices'][0]['message']['content']
        elif "error" in result:
            err = result["error"]
            msg = err["message"] if isinstance(err, dict) and "message" in err else str(err)
            return f"<h2 style='color:red;'>LLM API ERROR: {msg}</h2>"
        else:
            return f"<h2 style='color:red;'>Unexpected LLM API response:<br>{result}</h2>"
    except Exception as e:
        return f"<h2 style='color:red;'>Server exception: {e}</h2>"

def generate_task_html(task_json, output_dir="."):
    code = get_code_from_llm(
        task_json.get("brief"),
        task_json.get("checks"),
        task_json.get("attachments", [])
    )
    # Try to guess file type from code (simple heuristic)
    if code.strip().startswith("<!DOCTYPE html>") or "<html" in code:
        filename = "index.html"
    elif code.strip().startswith("FROM "):
        filename = "Dockerfile"
    elif code.strip().startswith("import") or code.strip().startswith("def") or "python" in task_json.get("brief", "").lower():
        filename = "app.py"
    elif code.strip().startswith("{") or code.strip().startswith("["):
        filename = "config.json"
    elif code.strip().startswith("#") or code.strip().startswith("---"):
        filename = "README.md"
    else:
        filename = "index.html"  # fallback

    with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
        f.write(code)

def generate_task_readme(task_json, output_dir="."):
    task = task_json.get('task', 'Task')
    round_num = task_json.get('round', '')
    brief = task_json.get('brief', '')
    evaluation_url = task_json.get('evaluation_url', '')
    attachments = task_json.get('attachments', [])
    checks = task_json.get('checks', [])

    readme_content = f"""# LLM Code Deployment

[![Deploy Status](https://img.shields.io/badge/deploy-on--render-brightgreen)](https://project-llm-code-deployment.onrender.com/api-endpoint)

## 🚀 Project Overview

This repo is an **auto-generated app or script** for a specific LLM-assisted TDS Project 1 task.

- **Current Task:** `{task}`
- **Round:** `{round_num}`
- **App Brief:**  
  > {brief}

---

## 📋 Features (This Task)

- LLM-generated, ready-to-use code for the current task brief
- Deploys to [GitHub Pages](https://ajmalmiitm.github.io/Project-LLM-Code-Deployment/) or as appropriate
- Receives its brief/updates by secure API POST

---

## ⚡ Task Metadata

| Field         | Value                        |
|---------------|-----------------------------|
| Task          | `{task}`                    |
| Round         | `{round_num}`               |
| Evaluation URL| `{evaluation_url}`          |
| Attachments   | {", ".join(f"`{att['name']}`" for att in attachments) if attachments else "—"} |

### ✅ Auto-Evaluation Checks

{chr(10).join(f'- [ ] {chk}' for chk in checks) if checks else "_No checks provided_"}

---

## 📜 API Info

- API endpoint for future POSTs:  
  [`https://project-llm-code-deployment.onrender.com/api-endpoint`](https://project-llm-code-deployment.onrender.com/api-endpoint)

- This deployment is managed fully by automated LLM code generation.

---

## 📝 License

MIT License [(LICENSE)](LICENSE)

---

_Made with ❤️ for IITM TDS Project 1 — auto-generated by LLM Code Deployment system._
"""
    with open(os.path.join(output_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)
