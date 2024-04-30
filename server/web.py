from flask import Flask, request, render_template, abort, session
from flask_socketio import SocketIO
import requests
from server import ServerApp
import threading
from blockchain import TBlockchain

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnmmqwertyuiopasdfghjklzxcvbnm"

Tchain = TBlockchain()
session['chain'] = Tchain.users.user_chain
server = None

code_thread = None

# @app.before_request
# def check_tor():
#     """
#     Check if the request is coming from a Tor exit node
#     """
#     exit_nodes = set()
#     response = requests.get('https://check.torproject.org/exit-addresses')
#     for line in response.iter_lines():
#         if line.startswith(b'ExitAddress '):
#             exit_nodes.add(line.split()[1].decode())
#     if request.remote_addr in exit_nodes:
#         abort(403)

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('credits.html')


def start_server():
    global server
    server = ServerApp()


@app.route('/load', methods=['GET', 'POST'])
def load():
    global code_thread
    code_thread = threading.Thread(target=start_server)
    code_thread.start()
    return render_template('load.html', redirect_url = '/scan_code')


@app.route('/scan_code')
def display():
    return render_template('report.html', redirect_url="/auth")


@app.route('/auth')
def auth():
    Tchain.users.load_chain()
    Tchain.load_Tchain()
    for user in Tchain.users.user_chain():
        if user.id == server.records[0]:
            break

    for ouser in session['chain']:
        if ouser.id == user.id:
            old_list = user.tokens

    if len(old_list) == len(user.tokens) - 1:
        return render_template('license.html')

    
if __name__ == "__main__":
    app.run(host = "0.0.0.0", debug=True)