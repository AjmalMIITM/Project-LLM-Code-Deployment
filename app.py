from flask import Flask, request, jsonify

app = Flask(__name__)

# Replace this with your generated secret
SECRET = "a9fd43c6-a7fa-400e-9208-39f984876201"

@app.route('/api-endpoint', methods=['POST'])
def handle_request():
    data = request.get_json(force=True)
    
    if not data:
        return jsonify({"error": "No JSON body found"}), 400

    # Verify secret
    if data.get("secret") != SECRET:
        return jsonify({"error": "Unauthorized"}), 403

    # Parse expected fields
    try:
        email = data["email"]
        task = data["task"]
        round_num = data["round"]
        nonce = data["nonce"]
        brief = data["brief"]
        evaluation_url = data["evaluation_url"]
    except KeyError as e:
        return jsonify({"error": f"Missing field {e}"}), 400

    # Log for confirmation
    print(f"Received task {task}, round {round_num} for {email}")
    print(f"Brief: {brief}")

    # Placeholder: You will build your app here based on brief

    return jsonify({"status": "OK"}), 200

if __name__ == '__main__':
    app.run(port=8080)
