# 🚀 LLM Code Deployment 
[![Deploy Status](https://img.shields.io/badge/Deploy-Live%20on%20Render-success?style=for-the-badge&logo=render)](https://project-llm-code-deployment.onrender.com/api-endpoint)
[![Made with Python](https://img.shields.io/badge/Made%20with-Python%203.9+-blue?style=for-the-badge&logo=python)](#)

---

### 🧠 Project Overview

This project is an **automated app builder and deployer** for LLM-assisted tasks within the IITM TDS program.  
It dynamically creates and deploys single-page web apps (like captcha solvers) to **GitHub Pages**, fully orchestrated through a POST API.

- 🌐 **API URL:** [`https://project-llm-code-deployment.onrender.com/api-endpoint`](https://project-llm-code-deployment.onrender.com/api-endpoint)  
- 💾 **Demo Repo:** [`AjmalMIITM/Project-LLM-Code-Deployment`](https://github.com/AjmalMIITM/Project-LLM-Code-Deployment)

---

## 📋 Features

- Receives POST requests with app briefs
- Authenticates using a secret key
- Generates minimal HTML apps with LLM assistance
- Publishes web apps to GitHub Pages with MIT license
- Notifies evaluation endpoint with deployment metadata
- Ready for dynamic revision rounds and automated evaluation

---

## 🛠️ Stack

- **Flask** – REST API backend
- **Python** – Automation and integration scripts
- **GitHub API & Pages** – Static deployment
- **Render.com** – Cloud API hosting

---

## ⚡ Quick Start

### Requirements

- Python 3.9 or higher
- `requirements.txt` dependencies

### Setup

1. **Clone the repo:**
   ```bash
   git clone https://github.com/AjmalMIITM/Project-LLM-Code-Deployment.git
   cd Project-LLM-Code-Deployment
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment secrets** (locally with `.env` or on Render):
   ```
   GITHUB_TOKEN=<your_github_token>
   SECRET_KEY=<your_api_secret>
   ```

4. **Run locally:**
   ```bash
   python app.py
   ```
   - The API is available at `http://127.0.0.1:8080/api-endpoint`

5. **Deploy:**
   - Deploy your API using Render, Heroku, Replit, etc.

---

## 🧪 API Usage

**Endpoint:**  
`POST /api-endpoint`

**Sample request:**
```json
{
  "secret": "<your_api_secret>",
  "email": "<your_email>",
  "task": "captcha-solver-xyz",
  "round": 1,
  "nonce": "random-nonce",
  "brief": "Sample app brief",
  "evaluation_url": "https://example.com/notify"
}
```

- Returns: `{ "status": "OK" }` on successful receipt.

---

## 📂 Repository Structure

| File                 | Purpose                              |
|----------------------|--------------------------------------|
| app.py               | Main Flask API                       |
| generate_html.py     | HTML app generator                   |
| push.py/notify.py    | GitHub/Evaluation API integrations   |
| Procfile             | For cloud deployment (Render/Heroku) |
| requirements.txt     | Dependencies                         |
| LICENSE              | MIT License                          |
| index.html           | Deployed sample app                  |
| README.md            | You are here!                        |

---

## 📝 License

This project is licensed under the [MIT License](LICENSE).

---

## 🤝 Contact

For questions, open an [Issue](https://github.com/AjmalMIITM/Project-LLM-Code-Deployment/issues) or reach out via [AjmalMIITM GitHub](https://github.com/AjmalMIITM).

---

**Made with ❤️ for IITM TDS Project 1**
