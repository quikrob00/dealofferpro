from flask import send_file
import os

@app.route('/')
def home():
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static', 'index.html'))
    return send_file(path)
