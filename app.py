import requests
import asyncio
import random
import time
import json
from typing import Dict
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Encar Backup Proxy", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Только один рабочий прокси IPRoyal Korea
IPROYAL_PROXY_CONFIGS = [
    {
        "name": "Korea Residential",
        "proxy": "geo.iproyal.com:12321",
        "auth": "oGKgjVaIooWADkOR:O8J73QYtjYWgQj4m_country-kr",
        "location": "South Korea",
    },
]

def get_proxy_config(proxy_info):
    proxy_url = f"http://{proxy_info['auth']}@{proxy_info['proxy']}"
    return {"http": proxy_url, "https": proxy_url}

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
]

BASE_HEADERS = {
    "accept": "*/*",
    "accept-language": "en,ru;q=0.9",
    "origin": "https://cars.prokorea.trading",
    "referer": "https://cars.prokorea.trading/",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
}

class EncarBackupProxy:
    def __init__(self):
        self.current_proxy_index = 0
        self.request_count = 0
        self.session_request_count = 0
        self.last_request_time = 0
        self._create_fresh_session()

    def _create_fresh_session(self):
        if hasattr(self, "session"):
            self.session.close()
        self.session = requests.Session()
        self.session.timeout = (10, 30)
        self.session.max_redirects = 3
        self._rotate_proxy()
        self.session_request_count = 0
        logger.info("New session created")

    def _rotate_proxy(self):
        proxy_info = IPROYAL_PROXY_CONFIGS[self.current_proxy_index % len(IPROYAL_PROXY_CONFIGS)]
        proxy_config = get_proxy_config(proxy_info)
        self.session.proxies = proxy_config
        self.current_proxy_index += 1
        logger.info(f"Using proxy: {proxy_info['name']} ({proxy_info['location']})")

    def _get_headers(self):
        ua = random.choice(USER_AGENTS)
        headers = BASE_HEADERS.copy()
        headers["user-agent"] = ua
        headers["sec-ch-ua"] = '"Google Chrome";v="137", "Chromium";v="137", "Not.A/Brand";v="24"'
        return headers

    def _rate_limit(self):
        now = time.time()
        if now - self.last_request_time < 0.5:
            time.sleep(0.5 - (now - self.last_request_time))
        self.last_request_time = time.time()

        if self.request_count % 20 == 0 and self.request_count > 0:
            self._rotate_proxy()
        if self.session_request_count >= 50:
            self._create_fresh_session()

        self.request_count += 1
        self.session_request_count += 1

    async def request(self, url: str, retries=5):
        for attempt in range(retries):
            try:
                self._rate_limit()
                headers = self._get_headers()
                loop = asyncio.get_event_loop()
                response =  loop.run_in_executor(
                    None, lambda: self.session.get(url, headers=headers)
                )
               if response.status_code == 200:
    return {"success": True, "text": response.text, "status": 200}
elif response.status_code == 407:
    self._rotate_proxy()
elif response.status_code == 403:
    self._create_fresh_session()
    await asyncio.sleep(1)
elif response.status_code in [429, 503]:
    self._rotate_proxy()
    await asyncio.sleep(2 ** attempt)
else:
    return {
        "success": False,
        "status": response.status_code,
        "text": response.text
    }

    


proxy = EncarBackupProxy()

@app.get("/api/catalog")
async def proxy_catalog(q: str = Query(...), sr: str = Query(...)):
    url = f"https://api.encar.com/search/car/list?count=true&q={q}&sr={sr}"
    result = await proxy.request(url)

    if result.get("success"):
        try:
            parsed_json = json.loads(result["text"])
            return JSONResponse(content=parsed_json, media_type="application/json")
        except Exception as e:
            logger.error(f"Failed to parse JSON: {e}")
            return JSONResponse(content={"error": "Failed to parse JSON"}, status_code=500)
    else:
        return JSONResponse(content=result, status_code=result.get("status", 500), media_type="application/json")

@app.get("/health")
async def health():
    current_index = (proxy.current_proxy_index - 1) % len(IPROYAL_PROXY_CONFIGS)
    current_proxy = IPROYAL_PROXY_CONFIGS[current_index]
    return {
        "status": "ok",
        "proxy": current_proxy["name"],
        "location": current_proxy["location"],
        "requests": proxy.request_count,
        "session_requests": proxy.session_request_count,
    }

@app.get("/")
async def root():
    return {
        "service": "Backup Encar Proxy",
        "version": "1.0",
        "endpoints": ["/api/catalog", "/health"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
