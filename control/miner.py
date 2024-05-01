from blockchain import Wallet
import time
from firebase_admin import credentials, db
import firebase_admin

cred = credentials.Certificate(r"C:\Users\Anutosh\Coding_projects\Startup_ideas\Helios\helios-c9483-firebase-adminsdk-judse-e1d436f342.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://helios-c9483-default-rtdb.asia-southeast1.firebasedatabase.app'
})
db_ref = db.reference()

wallet = Wallet()
pool = []
while True:
    for i in range(10):
        block = wallet.create_wallet()
        pool.append(block)
    time.sleep(600)
    for block in pool:
        wallet.user_chain.append(block)
        if wallet.validate_chain():
            db_ref.child("user_blocks").push(block.to_dict())
            
        else:
            print("Cannot add block")
        