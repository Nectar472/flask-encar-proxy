from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/parse')
def parse():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Origin": "https://www.encar.com",
        "Referer": "https://www.encar.com/",
        "Accept": "application/json",
    }

    # Можно вставить куки, если потребуется
    cookies = {}

    try:
        res = requests.get(url, headers=headers, cookies=cookies, timeout=10)
        res.raise_for_status()
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
