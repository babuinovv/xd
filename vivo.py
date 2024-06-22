import socket
import threading
import http.server
import socketserver

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.proxy_request()

    def do_POST(self):
        self.proxy_request()

    def proxy_request(self):
        try:
            # Parse the URL
            url = self.path
            host, port, path = self.parse_url(url)

            # Connect to the target server
            with socket.create_connection((host, port)) as remote_socket:
                # Send the request to the target server
                remote_socket.sendall(f"{self.command} {path} {self.request_version}\r\n".encode())
                self.headers['Host'] = host
                for header, value in self.headers.items():
                    remote_socket.sendall(f"{header}: {value}\r\n".encode())
                remote_socket.sendall(b"\r\n")

                # Receive the response from the target server and forward it to the client
                while True:
                    data = remote_socket.recv(4096)
                    if not data:
                        break
                    self.wfile.write(data)
        except Exception as e:
            self.send_error(500, f"Error: {e}")

    def parse_url(self, url):
        # Basic URL parsing
        if url.startswith("http://"):
            url = url[7:]
        host_port, path = url.split('/', 1)
        path = '/' + path
        if ':' in host_port:
            host, port = host_port.split(':')
            port = int(port)
        else:
            host, port = host_port, 80
        return host, port, path

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    pass

def main():
    port = int(input("Введите порт прокси: "))
    server_address = ('', port)
    httpd = ThreadedHTTPServer(server_address, ProxyHandler)
    print(f"HTTP Proxy Server running on port {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    main()
