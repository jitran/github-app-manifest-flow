from flask import Flask, request, redirect, session, url_for, render_template_string
import glob
import json
import os
import requests
import shutil

app = Flask(__name__)
SERVER_URL = os.environ.get("SERVER_URL", "http://127.0.0.1:5000")

# Step 0: Landing page with "Register GitHub App" button
@app.route("/")
def index():
    json_files = sorted(glob.glob("requests/*.json"))
    content = ""
    for file_path in json_files:
        with open(file_path, "r") as f:
            try:
                data = json.load(f)
                manifest = {
                    "name": data["name"],
                    "url": f"{SERVER_URL}",
                    "hook_attributes": {"url": f"{SERVER_URL}/webhook"},
                    "redirect_url": f"{SERVER_URL}/after-auth",
                    "public": False,
                    "default_permissions": data["permissions"]
                }
                org = data["org"]
                issue = data["issue"]
                content += render_template_string("""
                    <h2>Register {{ name }}</h2>
                    <ul>
                        <li>Organisation: {{ org }}</li>
                        <li>Permissions: {{ manifest.default_permissions | tojson }}</li>
                        <li>Issue: <a href="{{ issue }}">{{ issue }}</a></li>
                    </ul>
                    <form action="https://github.com/organizations/{{ org }}/settings/apps/new" method="POST">
                        <input type="hidden" name="manifest" value='{{ manifest|tojson }}'>
                        <button type="submit">Register GitHub App</button>
                    </form>
                    """, manifest=manifest, name=manifest["name"], org=org, issue=issue)
            except Exception:
                continue
    return content


# Step 1: GitHub will redirect to this URL after manifest registration with a code
@app.route("/after-auth")
def after_auth():
    code = request.args.get("code")
    if not code:
        return "Missing code parameter", 400

    # Step 2: Exchange the code for app credentials
    github_api_url = "https://api.github.com/app-manifests/{}/conversions".format(code)
    resp = requests.post(github_api_url, headers={"Accept": "application/vnd.github+json"})
    if resp.status_code != 201:
        return "GitHub manifest conversion failed: {}".format(resp.text), 400
    app_data = resp.json()

    # Move the request file to a completed directory
    os.makedirs("completed", exist_ok=True)
    shutil.move(f"requests/{app_data['slug']}.json", "completed/")

    # TODO: Store app_data securely by invoking a secure storage mechanism.
    # For learning purposes, we will render the output directly.
    return render_template_string("""
        <h2>GitHub App Registered!</h2>
        <p>App Name: {{ app_name }}</p>
        <p>App ID: {{ app_id }}</p>
        <p>Client ID: {{ client_id }}</p>
        <p>Client secret: {{ client_secret }}</p>
        <p>Webhook secret: {{ webhook_secret }}</p>
        <p>Private key (save it!):<br>
        <textarea rows=10 cols=80 readonly>{{ pem }}</textarea></p>
        """, app_name=app_data["slug"], app_id=app_data["id"], client_id=app_data["client_id"],
        client_secret=app_data["client_secret"], webhook_secret=app_data["webhook_secret"],
        pem=app_data["pem"])


if __name__ == "__main__":
    app.run(debug=True)
