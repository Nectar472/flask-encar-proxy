# app.py
from flask import Flask, request, jsonify
from playwright.async_api import async_playwright
import asyncio

app = Flask(__name__)

async def fetch_encar_data(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Настоящий переход на страницу Encar
        await page.goto(url)

        # Ожидание получения всех запросов (напр., JSON с машинками)
        response = await page.wait_for_response(lambda r: "car/list" in r.url and r.status == 200)
        data = await response.json()

        await browser.close()
        return data

@app.route("/parse", methods=["GET"])
def parse():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    data = asyncio.run(fetch_encar_data(url))
    return jsonify(data)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
