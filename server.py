import os
if not os.path.isfile("config.json"):
    print("config.json not found, please create one")
    exit()

import json
with open("config.json", "r") as f:
    IMAGE_ROOT_PATH = json.load(f)["image-path"]

with open("searchsite.html", "r") as f:
    website = "".join(f.readlines())

from search import create_image_string

# simple http server
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import re

image_regex = re.compile('/\d+/')

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes(website, "utf-8"))
        elif self.path.startswith("/search"):
            self.send_response(200)
            self.end_headers()
            query = parse_qs(urlparse(self.path).query)["query"][0]
            self.wfile.write(bytes(f'<div id="imagecontainer" onkeydown="inputEventHandler()">{create_image_string(query, True)}</div>', "utf-8"))
        elif image_regex.match(self.path):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(open(IMAGE_ROOT_PATH + self.path, "rb").read())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes("404 Not Found", "utf-8"))

httpd = HTTPServer(("0.0.0.0", 8000), SimpleHTTPRequestHandler)
print("Serving on http://localhost:8000")
httpd.serve_forever()
