from flask import Flask, send_file, abort, request, jsonify
import os

app = Flask(__name__)

# Path to the folder containing the data
DATA_FOLDER = "/home/alana/ALANA/AI/EMCROTUR/DataComex_output_with_metadata"

# API Token for authentication
API_TOKEN = "your_secret_token"


# Serve CSV files through an API endpoint with token authentication
@app.route("/data/<filename>", methods=["GET"])
def serve_file(filename):
    # Check API token
    token = request.headers.get("Authorization")
    if token != f"Bearer {API_TOKEN}":
        return jsonify({"error": "Unauthorized access"}), 403

    # Build the file path
    file_path = os.path.join(DATA_FOLDER, filename)

    # Verify if the requested file exists
    if os.path.isfile(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        abort(404, description=f"File {filename} not found")


# List available files (Optional: helpful for debugging)
@app.route("/files", methods=["GET"])
def list_files():
    try:
        files = os.listdir(DATA_FOLDER)
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
