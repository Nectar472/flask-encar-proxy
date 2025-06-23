import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

PROXY = {
    "http": "http://tkYhzB2WFMzk6v7R:yH0EdPksqTLURsF2@geo.iproyal.com:12321",
    "https": "http://tkYhzB2WFMzk6v7R:yH0EdPksqTLURsF2@geo.iproyal.com:12321"
}

@app.route('/')
def index():
    return jsonify({"message": "Encar Proxy API Active"})

@app.route('/api/nav')
def proxy_request():
    target_url = "https://api.encar.com/search/car/list/general"
    params = request.args.to_dict()
    headers = {
        "Referer": "https://www.encar.com/",
        "Origin": "https://www.encar.com",
        "User-Agent": request.headers.get("User-Agent", "Mozilla/5.0"),
    }

    try:
        response = requests.get(target_url, params=params, headers=headers, proxies=PROXY)
        print("📡 Status Code:", response.status_code)
        print("📄 Response Preview:", response.text[:500])  # Показывает первые 500 символов
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)})
