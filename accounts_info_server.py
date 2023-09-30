import http.server
import socketserver

port = 8080

class TextFileHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):

        if self.path == '/favicon.ico': return

        with open("plain_accounts.txt", 'r') as f:
            content = f.read()

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()

        self.wfile.write(content.encode('utf-8'))

def start_server():
    with socketserver.TCPServer(("", port), TextFileHandler) as httpd:
        print(f"Serving on port {port}...")
        httpd.serve_forever()