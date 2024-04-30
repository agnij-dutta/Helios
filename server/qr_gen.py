import qrcode
import random
from kivy.uix.image import Image
from kivy.uix.screenmanager import SlideTransition, Screen, ScreenManager
from kivy.graphics.texture import Texture
from kivy.app import App
from kivy.uix.widget import Widget
import encryption.AES as aes


class Server(App):
    def build(self):
        pass

    def generate(self):
        data = "Auther12340302"
        data = aes.encrypt(data, key='esmmb5r8u6zveps5')
        qr = qrcode.make(data)
        qr.save("qr_code.png")


