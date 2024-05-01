# Import required libraries
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
import random
import threading

cred = credentials.Certificate(r"C:\Users\Anutosh\Coding_projects\Startup_ideas\Helios\helios-c9483-firebase-adminsdk-judse-e1d436f342.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://helios-c9483-default-rtdb.asia-southeast1.firebasedatabase.app'
})
db_ref = db.reference()

hashseed = os.getenv('PYTHONHASHSEED')

thread = None

if not hashseed:
    os.environ['PYTHONHASHSEED'] = '0'
    os.execv(sys.executable, [sys.executable] + sys.argv)

#defining the parent class
class Coin:

    def __init__(self, index, timestamp, previous_hash):
        self.index = index
        self.timestamp = str(timestamp)
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        data = str(self.index) + str(self.timestamp) + str(self.previous_hash) + str(self.nonce)
        data = data.strip()
        return hashlib.sha256((data).encode('utf-8')).hexdigest()
    
    def mine_block(self, difficulty):
     target = '0' * difficulty
     while True:
        self.nonce += 1
        guess = self.calculate_hash()
        self.hash = guess
        if guess[:difficulty] == target:
            return self.nonce
    
    def validate_block(self, difficulty):
        target = '0' * difficulty
        return self.hash[:difficulty] == target



#Child class 1: Handles transanctions 
class TCoin(Coin):

    def __init__(self, index, timestamp, previous_hash, name, data = dict()) -> None:
        self.index = index
        self.timestamp = timestamp
        self.name = name
        self.previous_hash = previous_hash
        self.data = data
        super().__init__(index, timestamp, previous_hash)

    def to_dict(self):
        return {
            'name': self.name,
            'index': self.index,
            'timestamp': self.timestamp,
            'data': self.data,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'hash': self.hash
        }



#Child class 2: Handles users as blocks
class UserBlock:

    def __init__(self, name, id, index, rank, timestamp, previous_hash, tokens = list(), data = dict()): 
        self.name = name
        self.index = index
        self.id = id
        self.rank = rank
        self.nonce = 0
        self.tokens = str(tokens)
        self.data = data
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.ref_id = None

        self.calculate_hash()

    def to_dict(self):
        return {
            'name': self.name,
            'data': self.data,
            'id': self.id,
            'rank': self.rank,
            'index': self.index,
            'tokens': self.tokens,
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'hash': self.hash
        }
    
    def calculate_hash(self):
        data = str(self.index) + str(self.timestamp) + str(self.previous_hash) + str(self.id) + str(self.nonce)
        data = data.strip()
        return hashlib.sha256((data).encode('utf-8')).hexdigest()
        
    def mine_hash(self, difficulty):
     target = '0' * difficulty
     while True:
        self.nonce += 1
        guess = self.calculate_hash()
        self.hash = guess
        if guess[:difficulty] == target:
            return self.nonce

    def validate_block(self, difficulty):
        target = '0' * difficulty
        return self.hash[:difficulty] == target



# Define the Users Blockchain class
class Wallet:

    def __init__(self, difficulty=2):
        self.difficulty = difficulty
        self.user_ids = []
        self.user_chain = self.load_chain()
        # self.user_chain = []
        if len(self.user_chain) == 0:
            print("creating genesis block")
            self.create_genesis()
        else:
            pass

        if not self.validate_chain():
            pass

        if len(self.user_chain) > 216:
            difficulty += 1

        self.current_block = None


        # if not thread.is_alive():
        #     print("created 10 wallets")

    def gen_id(self):
        char = "qwertyuiopasdfghjklzxcvbnm"
        nos = "1234567890"
        char = char.upper()
        id = random.choice(char) + random.choice(char) + random.choice(char) + "-" + random.choice(nos) + random.choice(nos) + random.choice(nos)
        return id

    def load_chain(self):
        user_chain = []
        user_ids = []
        db_ref = db.reference('user_blocks')
        blocks = db_ref.get()
        if blocks:
           for user_id in blocks:
                block_data = blocks[user_id]
                block = UserBlock(
                    id=block_data['id'],
                    rank=block_data['rank'],
                    index=block_data['index'],
                    tokens=block_data['tokens'],
                    timestamp=block_data['timestamp'],
                    data = "", 
                    previous_hash=block_data['previous_hash'],
                    name=block_data['name']
                )

                # block = eval(block_data)

                block.data = block_data['data']
                block.hash = block_data['hash']
                block.nonce = block_data['nonce']
                user_chain.append(block)
                block.ref_id = user_id

           print("chain loaded")
        else:
            print("load failed")
            return user_chain
        user_chain = sorted(user_chain, key=lambda b: b.index)
        self.user_ids = user_ids
        return user_chain
    
    def create_genesis(self):
        timestamp = date.datetime.now()
        index = 0
        id = "AAA-000"
        block = UserBlock(id=id, index=index, rank="administrator", timestamp=str(timestamp), previous_hash="0", tokens=[], name="Admin", data="")
        block.mine_hash(self.difficulty)
        self.user_chain.append(block)
        db_ref.child('user_blocks').push(block.to_dict())

    
    def create_wallet(self):
        if len(self.user_chain) > 0:
            previous_block = self.user_chain[-1]
            index = previous_block.index + 1
            timestamp = date.datetime.now()
            id = self.gen_id()
            
            self.validate_chain()   
            block = UserBlock(id=id, index=index, rank="", timestamp=str(timestamp), previous_hash=previous_block.hash,tokens=[], name="", data="")
        
        else:
            timestamp = date.datetime.now()
            id = self.gen_id()

            self.validate_chain()
            block = UserBlock(id=id, index=0, rank="", timestamp=str(timestamp), previous_hash="0", tokens=[], name="", data="")
        
        block.mine_hash(self.difficulty)
        # self.user_chain.append(block)
        # if self.validate_chain():
        #     db_ref.child("user_blocks").push(block.to_dict())
            
        # else:
        #     print("Cannot add block")
        return block

    def add_user(self, name, rank, data, key):
        self.load_chain()
        self.validate_chain()
        for user in self.user_chain:
            if len(user.name) == 0:
                user.name = name
                user.rank = rank
                encrypted_dict = AES.encrypt(json.dumps(data), key)
                encrypted_dict = base64.b64encode(encrypted_dict).decode()
                user.data = encrypted_dict
                if self.validate_chain():
                    self.current_block = user
                    self.update_chain(key=key)
                    return user.id
                else:
                    print("Failed to add user wallet")
                return
        # self.create_wallet()

                

        # previous_block = self.user_chain[-1]
        # index = previous_block.index + 1
        # timestamp = date.datetime.now()
        
        # self.validate_chain()   
        # block = UserBlock(id=id, index=index, rank=rank, timestamp=str(timestamp), previous_hash=previous_block.hash,tokens=[], name=name, data=data)
        # block.mine_hash(self.difficulty)
        # encrypted_dict = AES.encrypt(json.dumps(block.data), key)
        # encrypted_dict = base64.b64encode(encrypted_dict).decode()
        # block.data = encrypted_dict
        # self.user_chain.append(block)
        # if self.validate_chain():
        #     block_dict = {
        #     'name': block.name,
        #     'index': block.index,
        #     'tokens': block.tokens,
        #     'timestamp': block.timestamp,
        #     'data': block.data,
        #     'previous_hash': block.previous_hash,
        #     'nonce': block.nonce,
        #     'hash': block.hash
        # }
        #     db_ref.child("user_blocks").push(block_dict)
            
        # else:
        #     print("Cannot add block")
        
    def get_latest_block(self):
        return self.user_chain[-1]

    def get_blockchain(self):
        chain_data = []
        for block in self.user_chain:
            chain_data.append(block.__dict__)
        return chain_data
    
    def validate_chain(self):
        self.load_chain()
        previous_hash = None
        for block in self.user_chain:
            if not block.validate_block(self.difficulty):
                print("block problem")
                return False
            # check if the previous_hash of the current block is the hash of the previous block
            if previous_hash is not None and block.previous_hash != previous_hash:
                print("previous hash problem")
                return False
            previous_hash = block.hash
        return True

    def update_chain(self, key):
       
       db_ref = db.reference('user_blocks')
       if self.current_block != None:
        user_id = self.current_block.ref_id  

        # Encrypting the current data
        encrypted_dict = AES.encrypt(json.dumps(self.current_block.data), key)
        encrypted_dict = base64.b64encode(encrypted_dict).decode()

        self.current_block.data = encrypted_dict
        self.user_chain[self.current_block.index] = self.current_block

        if self.validate_chain():
            block_dict = self.current_block.to_dict()
            db_ref.child(user_id).set(block_dict)
            print('done')
        else:
            print('not done')



#Define the Token(check-in transaction) Blockchain class
class TBlockchain:

    def __init__(self, difficulty=2):
        self.users = Wallet()
        self.difficulty = difficulty
        self.Tchain = self.load_Tchain()
        if not self.validate_Tchain():
            pass
        if len(self.Tchain) > 216:
            difficulty += 1

        self.current_user = None

    def load_Tchain(self):
        Uchain = self.users.user_chain
        Tchain = []
        for user in Uchain:
            if len(eval(user.tokens)) != 0:
                print('yes')
                for token in eval(user.tokens):
                    Tchain.append(token)
                # Tchain = sorted(Tchain, key=lambda b:b.index)
                self.Tchain = Tchain
                return Tchain
            else:
                self.Tchain = Tchain
                return Tchain

    def validate_Tchain(self):
        previous_hash = None
        if len(self.Tchain) != 0:
            for token in self.Tchain:
                if not token.validate_block(self.difficulty):
                    print("token problem")
                    return False
                # check if the previous_hash of the current block is the hash of the previous block
                if previous_hash is not None and token.previous_hash != previous_hash:
                    print("previous token hash problem")
                    return False
                previous_hash = token.hash
            return True

    def transaction(self, id, key):
        previous_coin = self.users.user_chain[-1]
        index = previous_coin.index + 1
        timestamp = date.datetime.now()
        for user in self.users.user_chain:
            if user.id == id:
                self.current_user = user
                name = user.name
                data = user.data
                break

        #decrypting the block data
        coin_data = base64.b64decode(data)
        coin_data = eval(AES.decrypt(coin_data, key))
        self.validate_Tchain()
        token = TCoin(index, timestamp, previous_coin.hash, name=name, data=data)
        token.mine_block(self.difficulty)
        encrypted_dict = AES.encrypt(json.dumps(token.data), key)
        encrypted_dict = base64.b64encode(encrypted_dict).decode()
        token.data = encrypted_dict
        self.Tchain.append(token)
        if self.validate_Tchain():
            coin_dict = token.to_dict()

        return coin_dict

    def acknowledge(self, token, key):
        list(self.current_user.tokens).append(token)
        self.current_user.tokens - str(self.current_user.tokens)
        self.users.user_chain.pop(self.current_user.index)
        self.users.user_chain.insert(self.current_user.index, self.current_user)
        self.users.update_chain(key)



if __name__ == "__main__":
    wallet = Wallet()
    wallet.add_user("Agnij", "emp", {"phone":"8583848726"}, "duttalakssoo0dr2")
    # tchain = TBlockchain()
    # tchain.transaction("NWM-525", "duttalakssoo0dr2")
