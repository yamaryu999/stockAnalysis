"""Simple mock news API server for integration tests.

Endpoints:
- GET /news?symbol=XXXX.T&days_back=7 -> JSON list of news articles

Usage:
  python tests/mocks/news_mock_server.py [port]
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


def build_articles(symbol: str, days_back: int) -> list[dict]:
    now = datetime.utcnow()
    base = int(now.timestamp())
    articles = []
    titles = [
        f"{symbol} 決算発表、増収増益",
        f"{symbol} 新製品を発表、市場の期待高まる",
        f"{symbol} 提携発表、事業シナジーに期待",
    ]
    for i, title in enumerate(titles):
        ts = base - i * 3600
        articles.append(
            {
                "title": title,
                "summary": f"{symbol} に関する好材料ニュースの要約 #{i+1}",
                "published": ts,
                "source": "Mock News",
                "url": f"http://localhost/mock/{symbol}/{i+1}",
                "provider": "MockProvider",
            }
        )
    return articles


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        try:
            parsed = urlparse(self.path)
            if parsed.path == "/news":
                qs = parse_qs(parsed.query)
                symbol = (qs.get("symbol") or ["TEST.T"])[0]
                try:
                    days_back = int((qs.get("days_back") or ["7"])[0])
                except Exception:
                    days_back = 7
                data = build_articles(symbol, days_back)
                payload = json.dumps(data).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return

            if parsed.path == "/sector":
                qs = parse_qs(parsed.query)
                sector = (qs.get("sector") or ["technology"])[0]
                resp = {
                    "sector": sector,
                    "sentiment": {"score": 0.35, "sentiment": "positive", "confidence": 0.8},
                    "keywords": {"keywords": ["ai", "software", "cloud"], "frequency": {"ai": 10, "software": 8, "cloud": 7}},
                    "news_count": 12,
                    "confidence": 0.8,
                }
                payload = json.dumps(resp).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return

            if parsed.path == "/indicators":
                resp = {
                    "nikkei_sentiment": {"score": 0.1, "sentiment": "neutral", "confidence": 0.5},
                    "fx_sentiment": {"score": -0.2, "sentiment": "negative", "confidence": 0.6},
                    "interest_sentiment": {"score": 0.3, "sentiment": "positive", "confidence": 0.7},
                }
                payload = json.dumps(resp).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return

            self.send_response(404)
            self.end_headers()
        except Exception:
            self.send_response(500)
            self.end_headers()


def main() -> None:
    port = 9100
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except Exception:
            pass
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Mock News server listening on :{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
