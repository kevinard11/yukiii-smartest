from flask import Flask, jsonify, request
import json, logging
import smartest_main as smartest
from bson import json_util
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Example endpoint
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Hello from localhost!"})

@app.route('/smartest', methods=['GET'])
def get_10_latest_smartest():
    doc = smartest.find_10_latest_smartest()

    return jsonify(json.loads(json_util.dumps(doc))), 200

@app.route('/smartest', methods=['POST'])
def run_smartest():
    data = request.get_data().decode('utf-8')
    data = json.loads(data)

    repo_url = data.get("repo_url")
    # is_print = data.get("is_print")
    # app.logger.info(repo_url)

    res = smartest.run_smartest(repo_url, True)
    if res == '401':
        return jsonify({"message": "File smartest.yaml not found"}), 404

    # return jsonify(res)
    return jsonify(res), 200, {'Content-Type': 'application/json'}

@app.route('/smartest/<id>', methods=['GET'])
def get_result_by_id(id):
    doc = smartest.find_smartest(id)

    if doc:
        return json.loads(json_util.dumps(doc)), 200
    else:
        return jsonify({"message": "Document not found"}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Runs on localhost:5000 by default