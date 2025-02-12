import os
import streamlit as st
from flask import send_file, abort, request, jsonify

from api.utils import secure_path

DATA_FOLDER = st.secrets["api"]["DATA_FOLDER"]
API_TOKEN = st.secrets["api"]["API_TOKEN"]


def register_routes(app):
    # Serve CSV files through an API endpoint with token authentication.
    # Using <path:filename> allows filenames with subdirectories.
    @app.route("/data/<path:filename>", methods=["GET"])
    def serve_file(filename):
        # Check API token
        token = request.headers.get("Authorization")
        if token != f"Bearer {API_TOKEN}":
            return jsonify({"error": "Unauthorized access"}), 403

        # Build and secure the file path
        file_path = secure_path(DATA_FOLDER, filename)

        # Verify if the requested file exists
        if os.path.isfile(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            abort(404, description=f"File '{filename}' not found.")

    # List available CSV files (including those in subfolders)
    @app.route("/files", methods=["GET"])
    def list_files():
        csv_files = []
        # Walk through DATA_FOLDER recursively
        for root, dirs, files in os.walk(DATA_FOLDER):
            for file in files:
                if file.lower().endswith(".csv"):
                    # Get the relative file path from DATA_FOLDER for clarity
                    rel_dir = os.path.relpath(root, DATA_FOLDER)
                    rel_file = os.path.join(rel_dir, file) if rel_dir != "." else file
                    csv_files.append(rel_file)
        return jsonify({"files": csv_files})
