# Models/time_constraint.py

from datetime import timedelta

class TimeConstraint:
    def __init__(self, buffer_time=timedelta(minutes=15), location=None):
        """
        Initialize TimeConstraint with optional buffer time and location constraints.

        :param buffer_time: Minimum buffer time between tasks (as a timedelta object).
        :param location: Optional location constraint information.
        """
        self.buffer_time = buffer_time
        self.location = location
        self.dependencies = {}  # Dictionary to track dependencies, e.g., {task1: [task2, task3]}

    def set_buffer_time(self, buffer_time):
        """Set the buffer time required between tasks."""
        self.buffer_time = buffer_time

    def add_dependency(self, task, dependency_task):
        """Add a dependency so that a task cannot start until dependency_task is completed."""
        if task in self.dependencies:
            self.dependencies[task].append(dependency_task)
        else:
            self.dependencies[task] = [dependency_task]

    def validate_constraints(self, task1, task2):
        """Check if task1 and task2 meet all constraints (e.g., buffer time, location, dependencies)."""
        if not self.validate_buffer(task1, task2):
            return False
        if not self.validate_dependency(task1):
            return False
        # Add more validation logic as needed
        return True

    def validate_buffer(self, task1, task2):
        """Validate if buffer time between two tasks is sufficient."""
        return abs((task2.start_time - task1.end_time)) >= self.buffer_time

    def detect_conflict(self, task1, task2):
        """Detect if task1 and task2 have overlapping time slots."""
        return task1.start_time < task2.end_time and task2.start_time < task1.end_time

    def validate_dependency(self, task):
        """Ensure that dependencies for a task are met before it is scheduled."""
        if task in self.dependencies:
            for dep in self.dependencies[task]:
                if not dep.is_completed:
                    return False
        return True