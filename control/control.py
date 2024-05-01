from flask import Flask, request, render_template, redirect, abort, session
import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath("C:/Users/Anutosh/Coding_projects/Startup_ideas/Helios/encryption/AES.py") ) ) )
import encryption.AES as aes
sys.path.append( path.dirname( path.dirname( path.abspath("C:/Users/Anutosh/Coding_projects/Startup_ideas/Helios/server/server.py") ) ) )
from server.server import ServerApp
import base64
from blockchain import Wallet
import threading


server = None
Uchain = Wallet()
thread = None

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "qazwsxedcrfvtgbyhnujmikolpqazwsxedcrfvtgbyhnujmikolpqazwsxedcrfvtgbyhnujmikolphjkksxvbjcxerfghjnbi"

def start_server():
    global server
    server = ServerApp()

@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()
    global code_thread
    code_thread = threading.Thread(target=start_server)
    code_thread.start()
    

@app.route('/scan_code')
def display():
    return render_template('report copy.html', redirect_url="/auth")

@app.route('/auth')
def auth():
    Uchain.load_chain()

    for user in Uchain.user_chain():
        if user.id == server.records[0]:
            break

    for ouser in session['chain']:
        if ouser.id == user.id:
            old_list = user.tokens

    if len(old_list) == len(user.tokens) - 1:
        session['login'] = True
        return render_template('license.html', redirect_url='/')

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'login' in session:
        return render_template('leaderboard.html')
    else:
        redirect('/login')

@app.route('/input_data', methods=['GET', 'POST'])
def input_data():
    values = request.form.getlist('value[]')
    session['values'] = values
    return render_template('index.html')

def push_data():
    name, key, rank = session['values']
    session['id'] = Uchain.add_user(name=name, data=session['data'], rank=rank, key=key)

@app.route('/add_records', methods=['GET', 'POST'])
def add():
    keys = request.form.getlist('key[]')  # Get all key inputs
    values = request.form.getlist('value[]')  # Get all value inputs
    data_dict = dict(zip(keys, values))  # Combine keys and values into a dictionary
    session['data'] = data_dict
    push_data()
    return render_template('load.html', redirect_url='/display')

@app.route('/display')
def display():
    # name, key, rank = session['values']
    # data = session['data']
    # output = {'name':name, 'rank':rank}
    # output.update(data)
    for user in Uchain.user_chain():
        if user.id == session['id']:
            break

    output = user.to_dict()
    return render_template('report.html', output=output, redirect_url='/')

@app.route('/show_data')
def show_data():

    id = request.form.get('id')
    Uchain.load_chain()

    for user in Uchain.user_chain():
        if user.id == id:
            break

    output = user.to_dict()
    return render_template('report.html', output=output)

if __name__ == "__main__":
    app.run(host = "0.0.0.0", debug=True)