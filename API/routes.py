# API/routes.py

from flask import jsonify, request, make_response
from flask.views import MethodView

# Placeholder dictionary for storing tasks; consider using a database in the future
tasks = {}

class TaskAPI(MethodView):
    def get(self, task_id=None):
        if task_id:
            task = tasks.get(task_id)
            return jsonify(task) if task else ("Task not found", 404)
        return jsonify(tasks)

    def post(self):
        new_task = request.json
        task_id = new_task.get("title")  # Using title as the ID for simplicity
        if task_id in tasks:
            return make_response("Task with this title already exists.", 400)
        tasks[task_id] = new_task
        return jsonify(new_task), 201

    def delete(self, task_id):
        if task_id in tasks:
            deleted_task = tasks.pop(task_id)
            return jsonify(deleted_task)
        return "Task not found", 404

# Create a view for TaskAPI
task_view = TaskAPI.as_view('tasks_api')