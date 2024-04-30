import hashlib
import datetime as date
import os
import sys
import firebase_admin
from firebase_admin import db
from firebase_admin import credentials
# Importing my own encrption file and necessary libraries
import encryption.AES as AES
import base64
import json

index = 0
timestamp = "2023-03-19 21:24:18.183179"
key = "heathcliff"
previous_hash = "0"
nonce = 0
difficulty = 5


def calculate_hash():
    data = str(index) + str(timestamp) + str(key) + str(previous_hash) + str(nonce)
    data = data.strip()
    hash = hashlib.sha256((data).encode('utf-8')).hexdigest()
    return hash
    

def mine():
    global nonce
    target = '0' * difficulty
    while True:
        nonce = nonce + 1
        guess = calculate_hash()
        if guess[:difficulty] == target:
            return guess, nonce

print(mine())