from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import json
import os

N8N_URL = os.getenv("N8N_URL", "http://127.0.0.1:5678/webhook/rag-chat")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8080"))
MAX_BODY_BYTES = 1_000_000


class Handler(SimpleHTTPRequestHandler):
    def _send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/healthz":
            self._send_json(200, {"ok": True})
            return
        super().do_GET()

    def do_POST(self):
        if self.path != "/api/rag-chat":
            self._send_json(404, {"error": "Not found"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_BODY_BYTES:
                self._send_json(413, {"error": "Invalid request size"})
                return

            body = self.rfile.read(length)

            # Validate that the browser actually sent JSON before forwarding.
            json.loads(body.decode("utf-8"))

            request = Request(
                N8N_URL,
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            with urlopen(request, timeout=120) as response:
                response_body = response.read()
                self.send_response(response.status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(response_body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(response_body)

        except json.JSONDecodeError:
            self._send_json(400, {"error": "Expected JSON request body"})
        except HTTPError as error:
            response_body = error.read()
            self.send_response(error.code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(response_body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(response_body)
        except Exception as error:
            self._send_json(502, {"error": str(error)})


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Planner: http://localhost:{PORT}")
    print(f"RAG proxy: http://localhost:{PORT}/api/rag-chat")
    print(f"n8n upstream: {N8N_URL}")
    server.serve_forever()
