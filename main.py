from flask import Flask, jsonify, request
import subprocess
import datetime
from waitress import serve

app = Flask(__name__)

BASE_GIT_DIR = "/mnt/dev-data/Projects"

def run_git_commands(subfolder):
    git_dir = f"{BASE_GIT_DIR}/{subfolder}"
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    commit_message = f"work of {date_str}"

    responses = {}

    commands = {
        "add": ["git", "add", "."],
        "commit": ["git", "commit", "-m", commit_message],
        "pull": ["git", "pull", "origin","main"],
        "push": ["git", "push", "origin"]
    }

    for cmd_name, cmd in commands.items():
        try:
            result = subprocess.run(cmd, cwd=git_dir, capture_output=True, text=True)
            responses[cmd_name] = {
                "status": "success" if result.returncode == 0 else "failed",
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip()
            }
        except Exception as e:
            responses[cmd_name] = {"status": "error", "error": str(e)}

    return responses

@app.route("/commit", methods=["POST"])
def commit_changes():
    try:
        data = request.get_json()
        subfolder = data.get("subfolder")
        if not subfolder:
            return jsonify({"status": "error", "message": "Missing subfolder parameter."}), 400

        result = run_git_commands(subfolder)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=5000)
