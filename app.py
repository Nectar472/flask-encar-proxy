from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return "Flask proxy is working!"

@app.route("/proxy", methods=["GET"])
def proxy():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        resp = requests.get(url, headers=headers)
        return (resp.text, resp.status_code, resp.headers.items())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()

