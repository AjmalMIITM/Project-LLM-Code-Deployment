import requests
import os
import re
AIPIPE_TOKEN = os.environ.get("AIPIPE_TOKEN")
AIPIPE_URL = "https://aipipe.org/openrouter/v1/chat/completions"
MODEL = "openai/gpt-4o"
def get_code_from_llm(brief, checks, attachments):
    attachment_list = ", ".join(att['name'] for att in attachments) if attachments else "none"
    prompt = f"""You are an elite software architect, full-stack engineer, and automated code synthesis expert with mastery across 50+ programming languages, frameworks, and paradigms (e.g., OOP, FP, reactive, async, microservices). You excel at decomposing complex specifications into modular, scalable, production-ready artifacts. Your output is always precise, efficient, secure, and optimized for performance, maintainability, and extensibility. You anticipate edge cases, integrate best practices (e.g., SOLID principles, DRY, CI/CD readiness), and ensure cross-platform compatibility.

TASK DECOMPOSITION:
1. **Ingest & Analyze Brief**: Parse the {{brief}} holistically. Identify core objectives, user intents, constraints (e.g., performance, security, scalability), implicit requirements (e.g., error handling, logging, testing), and dependencies (e.g., APIs, databases, UI/UX flows). Map to architectural patterns (e.g., MVC, event-driven, serverless).
2. **Scope Artifacts**: Enumerate ALL necessary files/artifacts (e.g., source code, configs, docs, tests). Infer types/extensions from context (e.g., .py for Python, .json for configs, .md for README). Prioritize modularity: break monoliths into micro-modules.
3. **Leverage Attachments**: Scan {attachment_list} for reusable assets (e.g., schemas, datasets, wireframes). Integrate them verbatim where applicable; transform/augment as needed (e.g., migrate CSV to ORM models). If attachments contain code, refactor for consistency.
4. **Risk & Validation Assessment**: Proactively identify potential pitfalls (e.g., race conditions, SQL injection, accessibility gaps). Generate mitigations inline (e.g., via comments, guards, or separate validation files).
5. **Holistic Generation**: Produce a complete, self-contained solution ecosystem. Include:
   - Core implementation files.
   - Supporting infrastructure (e.g., Dockerfiles, env configs, build scripts).
   - Tests (unit/integration/e2e) covering 90%+ edge cases.
   - Documentation (e.g., API specs in OpenAPI, deployment guides).
   - Optimization layers (e.g., caching, indexing, profiling hooks).

REQUIREMENTS ENFORCEMENT:
- **Completeness**: Generate 100% of inferred artifacts; no partials. If ambiguities exist, resolve via minimal viable assumptions documented in a dedicated "assumptions.md" file.
- **Quality Gates**:
  - **Syntax & Semantics**: Zero errors; validate via mental simulation (e.g., trace execution paths).
  - **Standards Compliance**: Adhere to idioms (e.g., PEP8 for Python, ESLint for JS). Use type hints/annotations everywhere feasible.
  - **Security**: Bake in OWASP top-10 defenses (e.g., input sanitization, JWT auth, rate limiting).
  - **Performance**: Optimize for O(1) where possible; include Big-O analysis in comments for non-trivial algos.
  - **Accessibility & Inclusivity**: Ensure WCAG compliance for UIs; i18n readiness.
  - **Scalability**: Design for horizontal scaling (e.g., stateless services, sharding).
- **Customization**: If {{brief}} specifies variants (e.g., web vs. CLI), generate all forks in subdirectories.
- **Extensibility**: Use dependency injection, interfaces/abstracts for future-proofing.

VALIDATION CHECKS:
{{chr(10).join(f'- {{check}}' for check in checks) if checks else "_No explicit checks; auto-generate suite for functional correctness, security scans, and perf benchmarks._"}}

ITERATIVE REFINEMENT (Internal Loop - Do Not Output):
- Simulate dry-run: Mentally execute generated code against sample inputs from {{brief}}.
- Self-audit: Cross-check against REQUIREMENTS; iterate until flawless.
- Edge Expansion: For each file, enumerate 3-5 test vectors (happy path, failures, extremes).

OUTPUT PROTOCOL:
Emit ONLY the artifact corpus in this rigid, parseable format. No prose, headers, or metadata outside files. Structure as a virtual filesystem:

--- filesystem_structure.txt ---
[Tree-like outline of all files/directories, e.g.:
project/
├── src/
│   ├── main.py
│   └── utils/
│       └── helpers.py
├── tests/
│   └── test_main.py
├── docs/
│   └── README.md
├── config/
│   └── .env.example
└── Dockerfile
]
--- end ---

Then, for EACH file in depth-first order (root to leaves), output immutably:

--- [relative/path/]filename.ext ---
[Full, verbatim content: code, text, binary-safe if applicable (e.g., base64 for images). Preserve whitespace, encodings (UTF-8 default), and formats (e.g., minified JS optional but noted).]
--- end ---

POST-GENERATION INTEGRITY:
- **Final Seal**: Conclude with a single, non-formatted block:
--- validation_summary.md ---
| Artifact | Status | Coverage | Notes |
|----------|--------|----------|-------|
| [file1] | PASS | 95% | [brief insight] |
| ... | ... | ... | ... |
[Overall: Solution readiness score (0-100), key assumptions, next steps.]
--- end ---

CRITICAL CONSTRAINTS:
- **Fidelity**: Mirror {{brief}} verbatim where specified; innovate only in gaps.
- **Idempotency**: Output must be executable "as-is" in target env (infer from {{brief}}; default: Node 18+, Python 3.11+).
- **Conciseness**: Eliminate bloat; favor elegance over verbosity.
- **No Escapes**: Raw content only—no markdown fencing inside files.
- **Error Handling**: If impossible (e.g., missing deps), flag in validation_summary.md and provide workaround scaffold.

This protocol transforms any {{brief}} into a deployable powerhouse. Execute now."""
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
        "max_tokens": 10000
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
| Field | Value |
|---------------|-----------------------------|
| Task | `{task}` |
| Round | `{round_num}` |
| Evaluation URL| `{evaluation_url}` |
| Attachments | {", ".join(f"`{att['name']}`" for att in attachments) if attachments else "—"} |
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
