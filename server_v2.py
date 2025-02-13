from flask import Flask
from api.routes import register_routes

app = Flask(__name__)

BASE_DATA_FOLDER = "/home/alana/ALANA/AI/EMCROTUR/EMCROTUR/"
API_TOKEN = "your_secret_token"

# Simplified route for serving files
@app.route("/data/<folder>/<filename>", methods=["GET"])
def serve_file(folder, filename):
    token = request.headers.get("Authorization")
    if token != f"Bearer {API_TOKEN}":
        return jsonify({"error": "Unauthorized access"}), 403

    file_path = os.path.join(BASE_DATA_FOLDER, folder, filename)
    if os.path.isfile(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        abort(404, description=f"File {filename} not found in folder {folder}")

# Simplified route for listing files
@app.route("/data/<folder>/files", methods=["GET"])
def list_folder_files(folder):
    try:
        token = request.headers.get("Authorization")
        if token != f"Bearer {API_TOKEN}":
            return jsonify({"error": "Unauthorized access"}), 403

        folder_path = os.path.join(BASE_DATA_FOLDER, folder)
        if not os.path.isdir(folder_path):
            return jsonify({"error": f"Folder {folder} not found"}), 404
        
        files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)