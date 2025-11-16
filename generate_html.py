import requests
import os
import re

AIPIPE_TOKEN = os.environ.get("AIPIPE_TOKEN")
AIPIPE_URL = "https://aipipe.org/openrouter/v1/chat/completions"
MODEL = "anthropic/claude-3.5-sonnet"
def get_code_from_llm(brief, checks, attachments):
    attachment_list = ", ".join(att['name'] for att in attachments) if attachments else "none"
    prompt = f"""
You are an expert software engineer and code generator.

TASK:
{brief}

REQUIREMENTS:
- Carefully analyze the brief and determine all required files (names and file types).
- Generate ALL required files exactly as specified in the task.
- Use the provided attachments as needed (filenames: {attachment_list}).
- Pass all checks listed below and generate files with correct structure and content.

CHECKS:
{chr(10).join(f'- {check}' for check in checks) if checks else "_No checks provided_"}

OUTPUT FORMAT:
For each file, output the full contents in this exact format, with no explanation or extra text:

--- filename.ext ---
[file content]

--- end ---

Important:
- Preserve file formats exactly (JSON, YAML, Markdown, CSV, SVG, Python, HTML).
- Ensure JSON files are valid and well-formatted.
- Ensure code files compile and run without syntax errors.
- Use placeholders only if data is missing, but still produce the file.
- Do not deviate from the output format or filenames.
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
        "max_tokens": 2000
    }
    try:
        resp = requests.post(AIPIPE_URL, headers=headers, json=payload, timeout=90)
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

def parse_llm_output(output):
    """
    Parse output to extract files using:
    --- filename.ext ---
    [file contents]
    --- end ---
    """
    pattern = r"--- ([^\n]+?) ---\n([\s\S]+?)(?=(?:--- [^\n]+? ---)|$)"
    files = {}
    for match in re.finditer(pattern, output):
        filename = match.group(1).strip()
        content = match.group(2).strip()
        files[filename] = content
    return files

def generate_task_files(task_json, output_dir="."):
    llm_output = get_code_from_llm(
        task_json.get("brief"),
        task_json.get("checks", []),
        task_json.get("attachments", [])
    )
    if llm_output.startswith("<h2"):
        print("LLM API Error:", llm_output)
        return
    files_map = parse_llm_output(llm_output)
    # Save all files
    for filename, content in files_map.items():
        file_path = os.path.join(output_dir, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    # Save attachments as is
    for att in task_json.get("attachments", []):
        att_path = os.path.join(output_dir, att['name'])
        try:
            att_resp = requests.get(att['url'], timeout=30)
            att_resp.raise_for_status()
            with open(att_path, 'wb') as fp:
                fp.write(att_resp.content)
        except Exception as e:
            print(f"Failed to download attachment {att['name']}: {e}")

def generate_task_readme(task_json, output_dir="."):
    task = task_json.get('task', 'Task')
    round_num = task_json.get('round', '')
    brief = task_json.get('brief', '')
    evaluation_url = task_json.get('evaluation_url', '')
    attachments = task_json.get('attachments', [])
    checks = task_json.get('checks', [])
    readme_content = f"""# LLM Code Deployment

[![Deploy Status](https://img.shields.io/badge/deploy-on--render-brightgreen)](https://project-llm-code-deployment.onrender.com/api-endpoint)

## Project Overview

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

