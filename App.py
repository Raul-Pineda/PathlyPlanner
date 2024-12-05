from flask import Flask, jsonify, request
from flask.views import MethodView
from flask_cors import CORS
import logging
import re
from datetime import datetime, timedelta

# Import the provided classes
from Calendar.calendar_integration import calendarIntegration
from Optimizers.priority_manager import PriorityManager
from Optimizers.scheduling_strategy import SchedulingStrategy

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

# Sample data for testing purposes
tasks = {
    "task1": {
        "title": "Sample Task 1",
        "details": "Details for task 1",
        "priority": 3,
        "dependencies": [],
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
        "dependencies": ["task1"],
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
        Processes and optimizes tasks using the scheduling strategies.
        """
        # Transform tasks to the expected format
        transformed_tasks = transform_tasks(tasks)

        # Create an instance of PriorityManager and adjust priorities
        priority_manager = PriorityManager(transformed_tasks)
        sorted_task_queue = priority_manager.sort_tasks()

        # Create an instance of SchedulingStrategy
        scheduling_strategy = SchedulingStrategy()
        weekly_slots = scheduling_strategy.generate_weekly_slots()

        # Convert deque to list of tasks
        task_dict = {task['name']: task for task in transformed_tasks}
        sorted_tasks = [task_dict[task_name] for task_name in sorted_task_queue]

        # Optimize the schedule
        scheduling_strategy.optimize_schedule(sorted_tasks, weekly_slots)

        # Get the scheduled tasks
        scheduled_tasks = scheduling_strategy.schedule

        # Transform scheduled tasks back to the original format
        processed_tasks = transform_scheduled_tasks_back(scheduled_tasks)
        return processed_tasks

    def transform_tasks(tasks):
        """
        Transforms tasks from the format in which they are stored in the app
        to the format expected by the scheduling_integration class.
        """
        transformed_tasks = []
        for task_id, task_data in tasks.items():
            transformed_task = {
                'name': task_id,  # Use task_id as the name
                'priority': task_data.get('priority', 0),
                'dependencies': task_data.get('dependencies', []),
                'start_time': parse_time(task_data.get('startTime')),
                'end_time': parse_time(task_data.get('endTime')),
                'duration': parse_duration(task_data.get('estimatedTime')),
                'deadline': parse_time(task_data.get('deadline')),
                'estimated_time_to_complete': parse_duration(task_data.get('estimatedTime')),
                'earliest_start_time': None,  # Could be added if needed
                'latest_start_time': None,    # Could be added if needed
            }
            transformed_tasks.append(transformed_task)
        return transformed_tasks

    def parse_duration(duration_str):
        """
        Parses a duration string like '1 hour', '2 hours 30 minutes', '90 minutes' and returns the duration in minutes.
        """
        if not duration_str:
            return 0
        duration_str = duration_str.lower()
        pattern = r'(?:(\d+)\s*hour[s]?)?\s*(?:(\d+)\s*minute[s]?)?'
        match = re.match(pattern, duration_str)
        if not match:
            return 0
        hours = int(match.group(1)) if match.group(1) else 0
        minutes = int(match.group(2)) if match.group(2) else 0
        total_minutes = hours * 60 + minutes
        return total_minutes

    def parse_time(time_str):
        """
        Parses a time string and returns the time in minutes from the start of the week.
        """
        if not time_str:
            return None
        # Expected format: 'Mon Nov 11 2024 09:00:00 GMT-0500 (Eastern Standard Time)'
        try:
            dt = datetime.strptime(time_str.split(' GMT')[0], "%a %b %d %Y %H:%M:%S")
            day_of_week = dt.weekday()  # Monday = 0
            total_minutes = day_of_week * 1440 + dt.hour * 60 + dt.minute
            return total_minutes
        except Exception as e:
            logging.error(f"Error parsing time '{time_str}': {e}")
            return None

    def transform_scheduled_tasks_back(scheduled_tasks):
        """
        Transforms scheduled tasks back to the format expected by the app.
        """
        processed_tasks = {}
        for task in scheduled_tasks:
            task_id = task['name']  # Using task['name'] as the task ID
            processed_task = {
                "title": task.get('name', ''),
                "details": '',  # Details not present in scheduled task
                "priority": task.get('priority', 0),
                "dependencies": task.get('dependencies', []),
                "startTime": convert_minute_to_datetime_str(task.get('start_time')),
                "endTime": convert_minute_to_datetime_str(task.get('end_time')),
                "location": '',  # Location not available
                "movable": True,  # Assume movable
                "deadline": convert_minute_to_datetime_str(task.get('deadline')),
                "estimatedTime": f"{task.get('duration') or task.get('estimated_time_to_complete')} minutes",
                "type": 'event'  # Assuming type 'event'
            }
            processed_tasks[task_id] = processed_task
        return processed_tasks

    def convert_minute_to_datetime_str(minutes):
        """
        Converts minutes from the start of the week to a datetime string.
        """
        if minutes is None:
            return None
        week_start = datetime.now() - timedelta(days=datetime.now().weekday())
        dt = week_start + timedelta(minutes=minutes)
        return dt.strftime("%a %b %d %Y %H:%M:%S")

    # Register the endpoint for Task API
    task_view = TaskAPI.as_view('tasks_api')
    app.add_url_rule('/tasks', view_func=task_view, methods=['GET', 'POST'])

    return app

# Only run the server if this file is executed directly
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
    
    scheduler = SchedulingStrategy()
    
    
    # Generate weekly slots
    weekly_slots = scheduler.generate_weekly_slots()

    # Optimize schedule
    scheduler.optimize_schedule(tasks, weekly_slots)


    # Print the weekly schedule
    SchedulingStrategy.print_schedule(weekly_slots)
    
    exporter = calendarIntegration(scheduler.task)



    #export calendar
    exporter.export_to_ics(exporter)



