
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib.request
import urllib.parse

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path

        if path == "/api/health":
            return self.reply({"ok": True, "message": "Server is running"})

        if path == "/api/klines":
            query = urllib.parse.parse_qs(
                urllib.parse.urlparse(self.path).query
            )
            symbol = query.get("symbol", ["BTCUSDT"])[0].upper()
            interval = query.get("interval", ["5m"])[0]

            if not symbol.endswith("USDT") or interval not in ("5m", "15m"):
                return self.reply({"error": "Invalid symbol or interval"}, 400)

            url = (
                "https://fapi.binance.com/fapi/v1/klines?"
                + urllib.parse.urlencode({
                    "symbol": symbol,
                    "interval": interval,
                    "limit": 100
                })
            )

            try:
                req = urllib.request.Request(
                    url, headers={"User-Agent": "CryptoSignalBot/1.0"}
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    candles = json.loads(response.read().decode("utf-8"))
                return self.reply({"ok": True, "symbol": symbol,
                                   "interval": interval, "candles": candles})
            except Exception as exc:
                return self.reply({
                    "ok": False,
                    "error": "Market data unavailable",
                    "detail": str(exc)
                }, 502)

        return self.reply({"error": "Not found"}, 404)

    def reply(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
