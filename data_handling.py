import socket
import urllib.parse
import json
import os.path
from threading import Event
JSON_PATH=os.path.join(__file__.rsplit('\\',1)[0],'front-init/storage/data.json')
def echo_server(host, port):
    print("server listening")
    with socket.socket() as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(1)
        conn, addr = s.accept()
        print(f"Connected by {addr}")
        with conn:
            while True:
                data = conn.recv(1024)
                print(f'From client: {data}')
                if not data:
                    break
                else:
                    recived_data=data
                conn.send(b"Data_recived")
    data_parse = urllib.parse.unquote_plus(recived_data.decode())
    data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
    print(data_dict)
    recive_time=data_dict.pop("recive_time")
    formated_data = {recive_time:data_dict}
    with open(JSON_PATH,"r") as fh: 
        file_data=json.load(fh)
    file_data.update(formated_data)
    with open(JSON_PATH,"w") as fh:
        json.dump(file_data,fh)

def run_server(close:Event=Event()):
    while not close.is_set():
        echo_server("localhost",5000)

if __name__=="__main__":
    while True:
        echo_server("localhost",5000)
