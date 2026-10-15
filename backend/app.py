import json
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", 8080))

# Latency of a single read against the config store.
CONFIG_FETCH_SECONDS = float(os.environ.get("CONFIG_FETCH_SECONDS", 2))

# In a real deployment these values come from a remote configuration
# service. Here they are inlined, but the per-key fetch latency is kept
# so the service behaves like the real thing.
_CONFIG_STORE = {
    "service": "f5-backend",
    "version": "1.0.0",
    "environment": "dev",
    "status": "operational",
}


def load_config():
    """Read the service configuration, one key at a time."""
    config = {}
    for key, value in _CONFIG_STORE.items():
        time.sleep(CONFIG_FETCH_SECONDS)
        print(f"[Backend] loaded config key: {key}", flush=True)
        config[key] = value
    return config


CONFIG = {}


class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self._respond(200, {"status": "healthy"})
        elif self.path == "/api/info":
            self._respond(200, CONFIG)
        else:
            self._respond(404, {"error": "not_found"})

    def _respond(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        print(f"[Backend] {self.address_string()} - {format % args}", flush=True)


if __name__ == "__main__":
    CONFIG = load_config()

    server = HTTPServer(("0.0.0.0", PORT), SimpleHandler)
    print(f"Backend listening on port {PORT}...", flush=True)
    server.serve_forever()
