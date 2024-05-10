import os
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.camera import Camera
from kivy.clock import Clock
from kivy.graphics.texture import Texture

from pyzbar import pyzbar
import base64
import cv2
import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(r"C:/Users/Agnij/Coding_projects/Helios/encryption/AES.py") ) ) )
import encryption.AES as aes
import socket
from blockchain import TBlockchain

# kivy.require('1.9.0')

#  Initializing Blockchain
tchain = TBlockchain()

class ClientApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        self.label = Label(text="Welcome to Helios")
        self.layout.add_widget(self.label)

        self.camera = cv2.VideoCapture(0)
        self.camera.set(3,1280)        # set resolution of camera
        self.camera.set(4,720)
        self.img=Image()        # Image widget to display frames

        # self.layout.add_widget(self.camera)
        self.layout.add_widget(self.img)

        self.scan_button = Button(text="Scan QR Code", on_press=self.scan_qr_code)
        self.layout.add_widget(self.scan_button)

        self.id_input = TextInput(hint_text="Enter ID number")
        self.layout.add_widget(self.id_input)
        self.password_input = TextInput(hint_text="Enter password", password=True)
        self.layout.add_widget(self.password_input)
        self.submit_button = Button(text="Submit", on_press=self.authenticate)
        self.layout.add_widget(self.submit_button)
        self.qr_scanned = False
        self.port = None
        # Clock.schedule_interval(self.update, 1.0/30)  # Schedule camera update
        return self.layout

    def scan_qr_code(self, instance):
        self.camera.release()

        ret, frame = self.camera.read() # retrieve frame from OpenCV camera

        if ret:
            buf1 = cv2.flip(frame, 0)
            buf = buf1.tostring()
            image_texture = Texture.create(size=(frame.shape[1],frame.shape[0]),colorfmt='bgr')
            image_texture.blit_buffer(buf,colorfmt='bgr',bufferfmt='ubyte')
            self.img.texture = image_texture  # display image from the texture
             
            barcodes = pyzbar.decode(frame)     # detect barcode from image
        

            for barcode in barcodes:
                (x, y, w, h) = barcode.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                barcodeData = barcode.data.decode("utf-8")
                barcodeType = barcode.type

                msg = base64.b64decode(barcodeData)
                msg = aes.decrypt(msg, key='esmmb5r8u6zveps5')
                self.port = msg


    def authenticate(self, instance):
        id_number = self.id_input.text
        password = self.password_input.text
        if self.qr_scanned and self.port:
            token = tchain.transaction(id_number, password)
            response = self.send_message(self.port, f"authenticate, {id_number}, {password}, {token.timestamp}, {token.hash}")
            if response == "Success":
                tchain.acknowledge(token, password)
            else:
                self.label.text = "Authentication Failed"
        else:
            self.label.text = "Please scan a QR code first"

    def send_message(self, port, message):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('127.0.0.1', port))
            client_socket.send(message.encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            client_socket.close()
            return response
        except Exception as e:
            self.label.text = f"Error: {e}"

    # def update(self, dt):
    #     frame = self.camera.texture
    #     if frame:
    #         frame_data = frame.pixels
    #         decoded_objects = pyzbar.decode(frame_data)
            
    #         if decoded_objects:
    #             for obj in decoded_objects:
    #                 if obj.type == 'QRCODE':
    #                     self.qr_scanned = True

    #                     msg = base64.b64decode(obj.data)
    #                     msg = aes.decrypt(msg)
    #                     self.port = msg
    #                     self.label.text = "QR Code scanned successfully"

if __name__ == '__main__':
    ClientApp().run()
