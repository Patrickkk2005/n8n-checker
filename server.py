import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler

from rules import analyze_workflow
import ai_analysis

# Serve files from the project directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class Handler(SimpleHTTPRequestHandler):

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        try:
            data = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, ValueError):
            self._json({'error': 'Invalid JSON in request body.'}, 400)
            return

        if self.path == '/api/scan':
            if 'workflow' not in data:
                self._json({'error': 'Missing workflow in request body.'}, 400)
                return
            try:
                findings = analyze_workflow(data['workflow'])
                self._json({'findings': findings})
            except Exception as e:
                self._json({'error': str(e)}, 500)

        elif self.path == '/api/deep-scan':
            if 'workflow' not in data:
                self._json({'error': 'Missing workflow in request body.'}, 400)
                return
            try:
                findings = ai_analysis.deep_analyze(
                    data['workflow'],
                    data.get('staticFindings', []),
                )
                self._json({'findings': findings})
            except RuntimeError as e:
                self._json({'error': str(e)}, 400)
            except Exception as e:
                self._json({'error': str(e)}, 500)

        else:
            self._json({'error': 'Not found.'}, 404)

    def _json(self, payload, status=200):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self._cors()
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass  # silence request logs


if __name__ == '__main__':
    port = 8765
    print(f'Running at http://localhost:{port} — press Ctrl+C to stop')
    HTTPServer(('127.0.0.1', port), Handler).serve_forever()
