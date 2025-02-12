import os
from flask import abort


def secure_path(base_path, user_path):
    """
    Join the base path and user-provided path and then check that
    the resulting absolute path is within the base directory.
    """
    # Construct the absolute file path
    file_path = os.path.join(base_path, user_path)
    abs_file_path = os.path.realpath(file_path)
    abs_base_path = os.path.realpath(base_path)

    # Check if the file is actually within the base directory
    if not abs_file_path.startswith(abs_base_path):
        abort(403, description="Forbidden: Invalid file path.")
    return abs_file_path
