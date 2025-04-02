from flask import Flask, jsonify, request
import json, logging
import smartest

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Example endpoint
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Hello from localhost!"})

@app.route('/smartest', methods=['POST'])
def run_smartest():
    data = request.get_data().decode('utf-8')
    data = json.loads(data)

    repo_url = data.get("repo_url")
    is_print = data.get("is_print")

    res = smartest.run_smartest(repo_url, is_print=False)

    # return jsonify(res)
    return jsonify(res.to_response()), 200, {'Content-Type': 'application/json'}


if __name__ == '__main__':
    app.run(debug=True)  # Runs on localhost:5000 by default