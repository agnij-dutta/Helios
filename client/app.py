import os
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.uix.camera import Camera
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
import pyzbar.pyzbar as pyzbar
from PIL import Image
import base64
import cv2
import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(r"C:/Users/Agnij/Coding_projects/Helios/encryption/AES.py") ) ) )
import encryption.AES as aes
import socket
from blockchain import TBlockchain

#  Initializing Blockchain
tchain = TBlockchain()
port = 0


class QRScannerScreen(Screen):
    def __init__(self, **kwargs):
        super(QRScannerScreen, self).__init__(**kwargs)
        self.camera = Camera(resolution=(640, 480), play=True)
        self.scan_btn = Button(text="Scan Code", size_hint=(None, None), size=(150, 50))
        self.scan_btn.bind(on_press=self.scan_qr)
        self.layout = BoxLayout(orientation="vertical")
        self.layout.add_widget(self.camera)
        self.layout.add_widget(self.scan_btn)
        self.add_widget(self.layout)

    def scan_qr(self, instance):
        Clock.schedule_once(self.capture_image, 0.5)

    def capture_image(self, dt):
        print("Capturing image...")
        filename = "capture.png"
        self.camera.export_to_png(filename)
        print("Image captured.")
        img = Image.open(filename)
        barcodes = pyzbar.decode(img)
        if barcodes:
            qr_data = barcodes[0].data.decode("utf-8")
            
            msg = base64.b64decode(qr_data)
            msg = aes.decrypt(msg, key='esmmb5r8u6zveps5')
            global port
            port = msg
            print("QR Code Data:", qr_data)
            app = App.get_running_app()
            app.port = msg
            app.root.current = "Login"
        else:
            print("No QR code detected.")


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical")
        self.qr_label = Label(text="QR Code Data:", font_size=20)
        self.id_input = TextInput(hint_text="Enter User ID")
        self.password_input = TextInput(hint_text="Enter Password", password=True)
        self.submit_btn = Button(text="Submit")
        self.submit_btn.bind(on_press=self.authenticate)
        self.layout.add_widget(self.id_input)
        self.layout.add_widget(self.qr_label)
        self.layout.add_widget(self.password_input)
        self.layout.add_widget(self.submit_btn)
        self.add_widget(self.layout)

    def authenticate(self, instance):
            id_number = self.id_input.text
            password = self.password_input.text
            app = App.get_running_app()
            port = app.port
            if self.qr_scanned and port:
                token = tchain.transaction(id_number, password)
                response = self.send_message(self.port, f"authenticate, {id_number}, {password}, {token.timestamp}, {token.hash}")
                if response == "Success":
                    tchain.acknowledge(token, password)
                else:
                    self.ids.qr_label.text = "Authentication Failed"
            else:
                self.qr_label.text = "Please scan a QR code first"

    def send_message(self, port, message):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('127.0.0.1', port))
            client_socket.send(message.encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            client_socket.close()
            return response
        except Exception as e:
            self.qr_label.text = f"Error: {e}"


class MyApp(App):
    qr_data = ""

    def build(self):
        sm = ScreenManager()
        sm.add_widget(QRScannerScreen(name="QRScanner"))
        sm.add_widget(LoginScreen(name="Login"))
        return sm


if __name__ == "__main__":
    MyApp().run()

