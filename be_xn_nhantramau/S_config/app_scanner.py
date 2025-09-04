import os


def find_local_apps(base_dir):
    """
    Scans the given base directory for potential Django applications.
    It identifies directories that contain an __init__.py and/or apps.py,
    and are not part of the main project configuration or common non-app directories.

    Args:
        base_dir (str): The absolute path to your Django project's root directory
                        (where manage.py resides).

    Returns:
        list: A list of strings, where each string is the name of a detected local app.
    """
    local_apps = []
    # Directories to explicitly ignore (e.g., virtual environments, static/media roots, build artifacts)
    # Add any other directories that are at the same level as your apps but are not apps.
    ignore_dirs = [
        'venv', '.venv', 'env', 'node_modules', 'static', 'media',
        'staticfiles', 'build', '__pycache__', 'dist',
        # Your main project directory name (e.g., 'myproject' if your settings.py is in myproject/settings.py)
        # You might need to adjust this based on your actual project structure.
        # This attempts to get the parent directory of utils/app_scanner.py's parent.
        os.path.basename(os.path.dirname(os.path.dirname(__file__))),
        # If settings.py is in 'myproject/myproject/settings.py', this will be 'myproject'.
        # If settings.py is in 'myproject/settings.py', this needs adjustment.
        # A safer way might be to pass the main project name.
    ]

    # Get the name of the main project directory (e.g., 'myproject')
    # This assumes settings.py is in myproject/myproject/settings.py
    # If settings.py is directly in myproject/settings.py, adjust this.
    main_project_name = os.path.basename(
        os.path.dirname(os.path.abspath(__file__)))

    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        # Check if it's a directory and not in the ignore list
        if os.path.isdir(item_path) and item not in ignore_dirs and not item.startswith('.'):
            # A directory is considered a potential Django app if it contains:
            # 1. An __init__.py file (making it a Python package)
            # 2. Or, an apps.py file (Django's preferred way for app configuration)
            # 3. And is not the main project directory itself.
            is_python_package = os.path.exists(
                os.path.join(item_path, '__init__.py'))
            has_app_config = os.path.exists(os.path.join(item_path, 'apps.py'))

            # Ensure it's not the main project directory itself (e.g., 'myproject' where settings.py lives)
            if item == main_project_name:
                continue  # Skip the main project directory

            if is_python_package or has_app_config:
                local_apps.append(item)
    return local_apps
