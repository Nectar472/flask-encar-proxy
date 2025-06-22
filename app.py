from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/proxy")
def proxy():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        return (response.content, response.status_code, response.headers.items())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
