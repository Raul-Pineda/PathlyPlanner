# API/__init__.py

from flask import Flask
from API.routes import task_view  # Import the view for TaskAPI

def create_app():
    app = Flask(__name__)
    
    # Register task routes
    app.add_url_rule('/tasks', view_func=task_view, methods=['GET', 'POST'])
    app.add_url_rule('/tasks/<string:task_id>', view_func=task_view, methods=['GET', 'DELETE'])
    
    return app