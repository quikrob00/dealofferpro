from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Deal Offer Pro is live and running!"

if __name__ == '__main__':
    app.run(debug=True)
