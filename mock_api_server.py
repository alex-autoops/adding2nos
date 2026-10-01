import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class API(BaseHTTPRequestHandler):
    resource = None

    def log_message(self, *args):
        pass

    def reply(self, code, data=None):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        if data is not None:
            self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        if self.path != "/items/1":
            return self.reply(404, {"error": "not found"})

        if API.resource is not None:
            self.reply(200, API.resource)
        else:
            self.reply(404, {"error": "not found"})

    def change(self, method):
        expected = "/items" if method == "POST" else "/items/1"

        if self.path != expected:
            return self.reply(404, {"error": "not found"})

        if method == "POST" and API.resource is not None:
            return self.reply(409, {"error": "already exists"})

        if method != "POST" and API.resource is None:
            return self.reply(404, {"error": "not found"})

        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))
        except (ValueError, TypeError):
            return self.reply(400, {"error": "invalid JSON"})

        if not isinstance(data, dict):
            return self.reply(400, {"error": "object required"})

        if method == "PATCH":
            API.resource.update(data)
        else:
            API.resource = data

        self.reply(201 if method == "POST" else 200, API.resource)

    def do_POST(self):
        self.change("POST")

    def do_PUT(self):
        self.change("PUT")

    def do_PATCH(self):
        self.change("PATCH")

    def do_DELETE(self):
        if self.path != "/items/1" or API.resource is None:
            return self.reply(404, {"error": "not found"})

        API.resource = None
        self.reply(204)


print("Mock API running at http://127.0.0.1:8765")
print("Stop with Ctrl+C")

try:
    HTTPServer(("127.0.0.1", 8765), API).serve_forever()
except KeyboardInterrupt:
    print("\nMock API stopped.")
