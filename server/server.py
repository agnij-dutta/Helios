import socket
import threading
import qrcode
import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath("C:/Users/Agnij/Coding_projects/Helios/encryption/AES.py") ) ) )
import encryption.AES as aes
import base64
import requests
from random_open_port import random_port
from blockchain import TBlockchain, TCoin


# Initialising socketIO
# socketio = SocketIO(app)

# Initialising the blockchain class
tchain = TBlockchain()


class ServerApp:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = random_port()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server running on {self.host}:{self.port}")
        self.generate_qr()
        

    def start(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"Connected to {client_address}")
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self, client_socket):
        try:
            while True:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                elif data == 'generate_qr':
                    self.generate_qr()
                    client_socket.send("QR code generated successfully".encode('utf-8'))
                elif data.startswith('authenticate'):
                    id, password, time, token_hash = data.split(',')[1:]
                    acknowledgment = self.authenticate(id, password, time, token_hash)
                    client_socket.send(acknowledgment)
                    self.records = [id, password, time, token_hash]
        finally:
            client_socket.close()
            

    def generate_qr(self):
        data = str(self.port)
        data = aes.encrypt(data=data, key='esmmb5r8u6zveps5')
        data = base64.b64encode(data).decode()
        qr = qrcode.make(data)
        qr.save(r"static/qr_code.png")
        self.start()


    def authenticate(self, id, password, time, token_hash):
        previous_coin = tchain.user_chain[-1]
        index = previous_coin.index + 1
        timestamp = time
        for user in self.users.user_chain:
            if user.id == id:
                break

        coin_data = base64.b64decode(user.data)
        coin_data = eval(aes.decrypt(coin_data, password))
        tchain.validate_chain()   
        token = TCoin(index, timestamp, previous_coin.hash,tokens=[], name=user.name, data=coin_data)
        token.mine_block(tchain.difficulty)
        if token.hash == token_hash:
            return True
        else:
            return False


if __name__ == '__main__':
    server = ServerApp()
