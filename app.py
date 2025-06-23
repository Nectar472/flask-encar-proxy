from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/api/nav')
def proxy_encar():
    base_url = "https://api.encar.com/search/car/list/general"
    # Собираем параметры GET-запроса и пробрасываем к Encar
    params = request.args.to_dict()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Referer": "https://www.encar.com/",
        "Origin": "https://www.encar.com",
        "Accept": "application/json",
        "Accept-Language": "ko-KR,ko;q=0.9",
        # Можно добавить больше заголовков, если потребуется
    }

    try:
        response = requests.get(base_url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
