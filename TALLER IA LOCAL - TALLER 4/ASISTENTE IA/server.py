#!/usr/bin/env python3
import json
import urllib.request
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "asistenteia-vm"

class Handler(SimpleHTTPRequestHandler):
    def _send_json(self, status, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.end_headers()

    def do_POST(self):
        if self.path != "/api/chat":
            self._send_json(404, {"error": "Ruta no encontrada"})
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            payload = json.loads(raw.decode("utf-8"))

            messages = payload.get("messages", [])
            if not messages:
                self._send_json(400, {"error": "No se recibieron mensajes"})
                return

            ollama_payload = {
                "model": MODEL,
                "messages": messages,
                "stream": False
            }

            req = urllib.request.Request(
                OLLAMA_URL,
                data=json.dumps(ollama_payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=180) as response:
                result = json.loads(response.read().decode("utf-8"))

            answer = result.get("message", {}).get("content", "")
            self._send_json(200, {
                "message": {"role": "assistant", "content": answer},
                "model": result.get("model", MODEL),
                "done": result.get("done", True),
                "total_duration": result.get("total_duration"),
                "load_duration": result.get("load_duration"),
                "prompt_eval_count": result.get("prompt_eval_count"),
                "eval_count": result.get("eval_count"),
            })

        except urllib.error.URLError as e:
            self._send_json(502, {
                "error": "No se pudo contactar con Ollama",
                "detail": str(e)
            })
        except Exception as e:
            self._send_json(500, {
                "error": "Error interno",
                "detail": str(e)
            })

if __name__ == "__main__":
    print("AsistenteIA-VM disponible en http://127.0.0.1:8000")
    print("Modelo Ollama:", MODEL)
    ThreadingHTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
