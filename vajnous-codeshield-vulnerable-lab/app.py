"""
INTENTIONALLY VULNERABLE CODE.
For Vajnous CodeShield AI testing only.
Do not deploy to production or expose to the Internet.
"""

import hashlib
import logging
import pickle
import random
import sqlite3
import subprocess
from pathlib import Path

import requests
import yaml
from flask import Flask, jsonify, redirect, request, render_template_string
from flask_cors import CORS
from markupsafe import Markup

app = Flask(__name__)

# VULNERABILITY: hard-coded application/session secret.
app.secret_key = "super-secret-admin-key-123"

# VULNERABILITY: insecure cookie configuration.
app.config["SESSION_COOKIE_SECURE"] = False
app.config["SESSION_COOKIE_HTTPONLY"] = False
app.config["SESSION_COOKIE_SAMESITE"] = None

# VULNERABILITY: wildcard CORS.
CORS(app, resources={r"/*": {"origins": "*"}})

# VULNERABILITY: hard-coded database credential.
DATABASE_PASSWORD = "admin-password-123"

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("codeshield-vulnerable-lab")

LAB_ROOT = Path("/tmp/codeshield-lab")
LAB_ROOT.mkdir(parents=True, exist_ok=True)
DB = LAB_ROOT / "lab.db"


def init_db():
    conn = sqlite3.connect(DB)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users "
        "(id INTEGER PRIMARY KEY, username TEXT, email TEXT, role TEXT)"
    )
    conn.execute(
        "INSERT OR IGNORE INTO users(id, username, email, role) "
        "VALUES (1, 'alice', 'alice@example.invalid', 'admin')"
    )
    conn.execute(
        "INSERT OR IGNORE INTO users(id, username, email, role) "
        "VALUES (2, 'bob', 'bob@example.invalid', 'user')"
    )
    conn.commit()
    conn.close()


init_db()


@app.get("/")
def index():
    return jsonify({
        "name": "Vajnous CodeShield Vulnerable Lab",
        "warning": "INTENTIONALLY VULNERABLE - LAB USE ONLY"
    })


@app.get("/user")
def get_user():
    username = request.args.get("username", "")

    # VULNERABILITY: SQL injection from string concatenation.
    query = "SELECT id, username, email, role FROM users WHERE username = '" + username + "'"

    conn = sqlite3.connect(DB)
    row = conn.execute(query).fetchone()
    conn.close()
    return jsonify({"result": row})


@app.get("/ping")
def ping():
    host = request.args.get("host", "localhost")

    # VULNERABILITY: OS command injection via shell=True.
    # Lab-only command. Never use this pattern in production.
    output = subprocess.check_output(
        "echo PING_TARGET=" + host,
        shell=True,
        text=True
    )
    return jsonify({"output": output})


@app.get("/fetch")
def fetch_url():
    target = request.args.get("url", "https://example.com")

    # VULNERABILITY: SSRF - untrusted URL fetched by server with no allowlist.
    response = requests.get(target, timeout=5)
    return jsonify({
        "status_code": response.status_code,
        "preview": response.text[:200]
    })


@app.get("/read")
def read_file():
    name = request.args.get("file", "demo.txt")

    # VULNERABILITY: path traversal.
    path = LAB_ROOT / name
    try:
        return path.read_text(errors="ignore")[:1000]
    except FileNotFoundError:
        return "not found", 404


@app.post("/deserialize")
def deserialize():
    data = request.get_data()

    # VULNERABILITY: insecure deserialization.
    obj = pickle.loads(data)
    return jsonify({"type": str(type(obj)), "value": str(obj)[:200]})


@app.post("/calculate")
def calculate():
    expression = request.json.get("expression", "1+1")

    # VULNERABILITY: arbitrary code execution through eval().
    value = eval(expression)
    return jsonify({"result": str(value)})


@app.post("/yaml")
def parse_yaml():
    raw = request.get_data(as_text=True)

    # VULNERABILITY: unsafe YAML loader.
    parsed = yaml.load(raw, Loader=yaml.Loader)
    return jsonify({"parsed": str(parsed)[:500]})


@app.get("/hello")
def hello():
    name = request.args.get("name", "world")

    # VULNERABILITY: reflected XSS - explicitly marks untrusted data safe.
    html = "<h1>Hello " + str(Markup(name)) + "</h1>"
    return render_template_string(html)


@app.post("/login")
def login():
    body = request.get_json(force=True)
    username = body.get("username", "")
    password = body.get("password", "")

    # VULNERABILITY: sensitive credentials written to logs.
    logger.info("Login attempt username=%s password=%s", username, password)

    # VULNERABILITY: weak password hash.
    digest = hashlib.md5(password.encode()).hexdigest()

    # VULNERABILITY: hard-coded password comparison.
    if username == "admin" and password == "admin123":
        return jsonify({"ok": True, "md5": digest, "role": "admin"})
    return jsonify({"ok": False, "md5": digest}), 401


@app.get("/reset-token")
def reset_token():
    user = request.args.get("user", "demo")

    # VULNERABILITY: predictable PRNG used for a security token.
    token = str(random.randint(100000, 999999))
    logger.warning("Generated reset token for %s: %s", user, token)
    return jsonify({"user": user, "reset_token": token})


@app.get("/users/<int:user_id>")
def user_by_id(user_id):
    # VULNERABILITY: IDOR / missing authorization check.
    conn = sqlite3.connect(DB)
    row = conn.execute(
        "SELECT id, username, email, role FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()
    conn.close()
    return jsonify({"user": row})


@app.get("/redirect")
def unsafe_redirect():
    target = request.args.get("next", "/")

    # VULNERABILITY: open redirect.
    return redirect(target)


@app.get("/config")
def config_dump():
    # VULNERABILITY: secret/configuration disclosure.
    return jsonify({
        "database_password": DATABASE_PASSWORD,
        "flask_secret_key": app.secret_key,
        "debug": app.debug
    })


if __name__ == "__main__":
    # VULNERABILITY: debug mode enabled.
    # Safety: bind only to localhost for the test lab.
    app.run(host="127.0.0.1", port=5000, debug=True)
