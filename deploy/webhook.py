"""Tiny webhook server that auto-deploys on push to main."""

import hashlib
import hmac
import os
import subprocess

from flask import Flask, abort, request

app = Flask(__name__)
SECRET = os.environ["WEBHOOK_SECRET"]


def verify_signature(payload, signature):
    expected = (
        "sha256=" + hmac.new(SECRET.encode(), payload, hashlib.sha256).hexdigest()
    )
    return hmac.compare_digest(expected, signature)


@app.route("/deploy", methods=["POST"])
def deploy():
    signature = request.headers.get("X-Hub-Signature-256", "")
    if not verify_signature(request.data, signature):
        abort(403)

    if request.headers.get("X-GitHub-Event") != "push":
        return "ignored", 200

    if request.json.get("ref") != "refs/heads/main":
        return "not main", 200

    subprocess.Popen(
        ["bash", "-c", "sudo -u memi bash -c 'cd /opt/memi-kr && git pull && uv sync' && systemctl restart memi-kr"],
    )
    return "deploying", 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=9013)
