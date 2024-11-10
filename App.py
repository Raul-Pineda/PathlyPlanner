from flask import Flask, jsonify, request
from flask.views import MethodView
from flask_cors import CORS  # Import CORS
import logging

# Sample data for testing purposes
tasks = {
    "task1": {
        "title": "Sample Task 1",
        "details": "Details for task 1",
        "priority": 3,
        "dependency": "",
        "startTime": None,
        "endTime": None,
        "location": "Home",
        "movable": False,
        "deadline": None,
        "estimatedTime": "1 hour",
        "type": "event"
    },
    "task2": {
        "title": "Sample Task 2",
        "details": "Details for task 2",
        "priority": 5,
        "dependency": "task1",
        "startTime": None,
        "endTime": None,
        "location": "Office",
        "movable": True,
        "deadline": None,
        "estimatedTime": "2 hours",
        "type": "deadline"
    }
}
task_history = {}  # Initialize an empty task history

logging.basicConfig(level=logging.DEBUG)

def create_app():
    """
    Creates and configures the Flask application with API routes.
    """
    app = Flask(__name__)
    CORS(app, origins="http://localhost:3000", supports_credentials=True)

    # Define Task API class with GET and POST handlers
    class TaskAPI(MethodView):
        def get(self):
            """
            GET endpoint to retrieve current tasks.
            """
            processed_tasks = process_tasks(tasks)
            return jsonify({"tasks": processed_tasks}), 200

        def post(self):
            """
            POST endpoint to save new tasks and move current tasks to history.
            """
            new_tasks = request.json
            global task_history, tasks
            task_history = tasks.copy()  # Backup current tasks to history
            tasks = new_tasks  # Replace current tasks with the new data
            return jsonify({"message": "Tasks updated successfully", "new_tasks": new_tasks}), 201

    def process_tasks(tasks):
        """
        Processes and optimizes tasks (currently a placeholder).
        """
        return tasks

    # Register the endpoint for Task API
    task_view = TaskAPI.as_view('tasks_api')
    app.add_url_rule('/tasks', view_func=task_view, methods=['GET', 'POST'])

    return app

# Only run the server if this file is executed directly
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)