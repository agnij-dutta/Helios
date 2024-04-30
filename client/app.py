from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.camera import Camera
from kivy.clock import Clock
import pyzbar.pyzbar as pbar
import base64
import cv2
import encryption.AES as aes
import socket
from blockchain import TBlockchain

tchain = TBlockchain()

class ClientApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        self.label = Label(text="Welcome to Helios")
        self.layout.add_widget(self.label)
        self.scan_button = Button(text="Scan QR Code", on_press=self.scan_qr_code)
        self.layout.add_widget(self.scan_button)
        self.id_input = TextInput(hint_text="Enter ID number")
        self.layout.add_widget(self.id_input)
        self.password_input = TextInput(hint_text="Enter password", password=True)
        self.layout.add_widget(self.password_input)
        self.submit_button = Button(text="Submit", on_press=self.authenticate)
        self.layout.add_widget(self.submit_button)
        self.camera = Camera(play=True)
        self.camera.resolution = (640, 480)
        self.layout.add_widget(self.camera)
        return self.layout

    def scan_qr_code(self, instance):
        if not self.qr_scanned:
            decoded_objects = pbar.decode(self.camera.texture.pixels)

            if decoded_objects:
                for obj in decoded_objects:
                    if obj.type == 'QRCODE':
                        self.qr_scanned = True

        msg = base64.b64decode(obj.data)
        msg = aes.decrypt(msg)
        self.port = msg    

    def authenticate(self, instance):
        id_number = self.id_input.text
        password = self.password_input.text
        token = tchain.transaction(id_number, password)
        response = self.send_message(self.port, f"authenticate, {id_number}, {password}, {token["timestamp"]}, {token["hash"]}")
        if response == True:
            tchain.acknowledge(token, password)

    def send_message(self, port, message):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('127.0.0.1', port))
            client_socket.send(message.encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            self.label.text = response
            client_socket.close()
            return response
        except Exception as e:
            self.label.text = f"Error: {e}"
    

if __name__ == '__main__':
    ClientApp().run()
