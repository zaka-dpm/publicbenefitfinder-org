"""Preview the Apache clean routes locally: python3 scripts/preview.py."""
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
ROUTES = json.loads((ROOT / "data/routes.json").read_text())
REDIRECTS = json.loads((ROOT / "data/redirects.json").read_text()) if (ROOT / "data/redirects.json").exists() else {}


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def redirect_route(self):
        path = urlsplit(self.path).path
        route = REDIRECTS.get(path) or next((url for url, file in ROUTES.items() if path == "/" + file), None)
        if route is None and path != "/" and path + "/" in ROUTES:
            route = path + "/"
        if route is not None:
            query = urlsplit(self.path).query
            self.send_response(301)
            self.send_header("Location", route + ("?" + query if query else ""))
            self.end_headers()
            return True
        return False

    def do_GET(self):
        if not self.redirect_route():
            super().do_GET()

    def do_HEAD(self):
        if not self.redirect_route():
            super().do_HEAD()

    def translate_path(self, path):
        route = urlsplit(path).path
        if route in ROUTES:
            return str(ROOT / ROUTES[route])
        return super().translate_path(path)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8093), partial(Handler, directory=str(ROOT)))
    print("Local preview: http://127.0.0.1:8093/", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
