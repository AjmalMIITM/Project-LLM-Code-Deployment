import requests
import os

AIPIPE_TOKEN = os.environ.get("AIPIPE_TOKEN") 
AIPIPE_URL = "https://aipipe.org/openrouter/v1/chat/completions"
MODEL = "qwen/qwen3-coder:free"  # change to other "free" models if needed

def get_code_from_llm(brief, checks, attachments):
    prompt = f"""You are an expert web developer. Generate the complete HTML+JS code for the following task so that it works by itself and satisfies all checks.

Brief:
{brief}

Checks:
{checks}

Attachments (descriptions only, do not depend on file contents unless sample given):
{attachments}

Important:
- Output only the code (no explanation, just code for index.html).
- If any required HTML elements or IDs are mentioned in checks, be sure to correctly implement them.
- Your code should look minimal but must work for the description and checks above.
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

    resp = requests.post(AIPIPE_URL, headers=headers, json=payload, timeout=60)
    result = resp.json()
    # There may be model variations, but this pattern returns the code as text.
    return result['choices'][0]['message']['content']

# In your generate_task_html:
def generate_task_html(task_json, output_dir="."):
    code = get_code_from_llm(
        task_json.get("brief"), 
        task_json.get("checks"), 
        task_json.get("attachments", [])
    )
    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(code)
