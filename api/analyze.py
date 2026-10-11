import os
import json
import base64
from http.server import BaseHTTPRequestHandler
import google.generativeai as genai

PROMPT = """Analyze this clothing item photo and return JSON with exactly these keys:
- name: short descriptive name, e.g. "Navy denim jacket"
- category: one of "top", "bottom", "outerwear", "dress", "shoes", "accessory"
- color: the main color as a simple word
- style: one of "casual", "formal", "sporty", "streetwear", "ethnic", "party"
- season: one of "summer", "winter", "monsoon", "all-season"
- occasions: array of 1 to 3 from "everyday", "work", "party", "formal", "workout", "travel"
Return only the JSON object."""


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            image_b64 = body.get("image", "")
            mime = body.get("mime", "image/jpeg")

            if not image_b64:
                return self._send(400, {"error": "No image provided."})

            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                return self._send(500, {"error": "Server is missing GEMINI_API_KEY."})

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(
                [PROMPT, {"mime_type": mime, "data": base64.b64decode(image_b64)}],
                generation_config={"response_mime_type": "application/json"},
            )
            tags = json.loads(response.text)
            self._send(200, tags)
        except Exception as e:
            self._send(500, {"error": str(e)})

    def _send(self, status, payload):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))
