# simple callback receiver for webhook testin
from flask import Flask, request
app = Flask(__name__)

@app.route('/callback', methods=['POST'])
def callback():
    data = request.json
    print(f"Received webhook callback with data: {data}")
    return '', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)