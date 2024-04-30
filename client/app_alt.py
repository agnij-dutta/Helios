
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, OptionProperty, ObjectProperty
from kivy.graphics import Color, BorderImage
from kivy.clock import Clock
from kivy.vector import Vector
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.utils import platform
from kivy.factory import Factory
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.lang import Builder
from random import choice, random
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.camera import Camera
from kivy.uix.label import Label
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
import cv2
import pyzbar.pyzbar as pbar


import pyaes
import base64



# Load the kv file for customizing the UI
# Builder.load_file('app.kv')
class MainScreen(Screen):
    pass

# class ScannerScreen(Screen):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.camera = Camera(play=True)
#         self.camera.resolution = (640, 480)
#         self.add_widget(self.camera)
#         self.qr_scanned = False
#         Clock.schedule_interval(self.check_qr_code, 1)

    # def check_qr_code(self, dt):
        # if not self.qr_scanned:
        #     decoded_objects = pbar.decode(self.camera.texture.pixels)

        #     if decoded_objects:
        #         for obj in decoded_objects:
        #             if obj.type == 'QRCODE':
        #                 self.qr_scanned = True
    #                     self.handle_authentication(obj.data.decode('utf-8'))
    #                     break
    
    # def handle_authentication(self, data):
    #     # Decrypt QR code data
    #     decrypted_data = self.decrypt_data(data)

    # def decrypt_data(self, encrypted_data):
    #     # Decrypt the encrypted data using AES
    #     key = b'16_byte_key_for_AES'  # Replace with your AES key
    #     iv = b'16_byte_initialization_vector'
    #     aes = pyaes.AESModeOfOperationCBC(key, iv=iv)
    #     decrypted_data = aes.decrypt(base64.b64decode(encrypted_data)).decode('utf-8')
    #     return decrypted_data
                    

class QRAuthApp(App):
    def build(self):
        # sm = ScreenManager()
        # sm.add_widget(MainScreen(name='main'))
        # sm.add_widget(ScannerScreen(name='scanner'))
        self.layout = BoxLayout(orientation='vertical')
        self.label = Label(text="Scan the QR code")
        self.layout.add_widget(self.label)
        self.button = Button(text="Scan QR Code")
        self.button.bind(on_press=self.scan_qr_code)
        self.layout.add_widget(self.button)
        self.id_input = TextInput(hint_text="Enter ID number")
        self.layout.add_widget(self.id_input)
        self.password_input = TextInput(hint_text="Enter password", password=True)
        self.layout.add_widget(self.password_input)
        self.submit_button = Button(text="Submit", on_press=self.authenticate)
        self.layout.add_widget(self.submit_button)
        return self.layout
    
    def check_qr_code(self, instance):
        if not self.qr_scanned:
            decoded_objects = pbar.decode(self.camera.texture.pixels)

            if decoded_objects:
                for obj in decoded_objects:
                    if obj.type == 'QRCODE':
                        self.qr_scanned = True
                        break
    
    def authenticate(self, data):
        # Decrypt QR code data
        decrypted_data = self.decrypt_data(data)

    def decrypt_data(self, encrypted_data):
        # Decrypt the encrypted data using AES
        key = b'16_byte_key_for_AES'  # Replace with your AES key
        iv = b'16_byte_initialization_vector'
        aes = pyaes.AESModeOfOperationCBC(key, iv=iv)
        decrypted_data = aes.decrypt(base64.b64decode(encrypted_data)).decode('utf-8')
        return decrypted_data


if __name__ == '__main__':
    QRAuthApp().run()