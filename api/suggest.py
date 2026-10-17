import os
import json
from http.server import BaseHTTPRequestHandler
import google.generativeai as genai

SYSTEM = """You are a friendly personal stylist. Using ONLY the wardrobe items
provided (refer to them by their id), suggest up to 3 outfits for the given
occasion and weather. Each outfit should be a sensible combination (for example a
top + bottom + shoes, or a dress + shoes) and may include outerwear or an
accessory when it makes sense. Return JSON of the form:
{"outfits": [{"title": "...", "item_ids": ["id1", "id2"], "why": "one short sentence"}]}
If the wardrobe cannot make a sensible outfit, return {"outfits": []}."""


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            items = body.get("items", [])
            occasion = body.get("occasion", "everyday")
            weather = body.get("weather", "mild")

            if len(items) < 2:
                return self._send(200, {"outfits": []})

            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                return self._send(500, {"error": "Server is missing GEMINI_API_KEY."})

           
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-3.8-flash", system_instruction=SYSTEM)
prompt = (
    f"Occasion: {occasion}\nWeather: {weather}\n"
    f"Wardrobe items:\n{json.dumps(items)}"
)
response = model.generate_content(
    prompt, generation_config={"response_mime_type": "application/json"}
)
self._send(200, json.loads(response.text))

            )
            response = model.generate_content(
                prompt, generation_config={"response_mime_type": "application/json"}
            )
            self._send(200, json.loads(response.text))
        except Exception as e:
            self._send(500, {"error": str(e)})

    def _send(self, status, payload):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))
