from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import mimetypes
import pathlib
import datetime
from time import sleep
import socket
import threading
import atexit
from data_handling import run_server
from multiprocessing import Process

class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('front-init/index.html')
        elif pr_url.path == '/contact':
            self.send_html_file('front-init/message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('front-init/error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())

    def do_POST(self):
        recive_time=datetime.datetime.now()

        print(recive_time)
        data = self.rfile.read(int(self.headers['Content-Length']))
        print(data+b'&recive_time='+bytes(str(recive_time),'utf-8'))
        data_parse = urllib.parse.unquote_plus(data.decode())
        print(data_parse)
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        print(data_dict)

        data_sending=threading.Thread(target=simple_client,args=("localhost",5000,data+bytes(f"&recive_time={str(recive_time)}",'utf-8')))
        data_sending.start()

        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()


def simple_client(host, port, data):
    with socket.socket() as s:
        while True:
            try:
                s.connect((host, port))
                s.sendall(data)
                returned_data = s.recv(1024)
                print(f'From server: {returned_data}')
                break
            except ConnectionRefusedError:
                print('Failed to connect to server')
                sleep(0.5)

def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    p=Process(target=run_server)
    p.start()
    atexit.register(p.terminate)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()



if __name__ == '__main__':
    run()
