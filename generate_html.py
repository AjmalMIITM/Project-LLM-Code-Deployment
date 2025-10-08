# Save this file as generate_html.py

import os

def generate_minimal_app(brief_text, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head><title>Task App</title></head>
    <body>
      <h1>Task Brief</h1>
      <p>{brief_text}</p>
    </body>
    </html>
    """
    with open(os.path.join(output_dir, "index.html"), "w") as f:
        f.write(html_content)

# Replace the text below with your actual app description
generate_minimal_app(
    "Create a captcha solver that handles ?url=https://.../image.png. Default to attached sample.",
    "."
)
