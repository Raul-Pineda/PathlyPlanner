# Models/user.py

from Models.task import Task
from Models.event import Event
from Models.recurring_task import RecurringTask
from Models.scheduled_task import ScheduledTask
from calendar import Calendar  # Adjust the import to reflect Calendar's location later

class User:
    def __init__(self, username, preferences=None):
        """
        Initialize a User with a username and optional preferences.
        
        :param username: Unique identifier for the user.
        :param preferences: Dictionary of user-specific preferences (e.g., time zone).
        """
        self.username = username
        self.tasks = []  # List to store Task objects (Event, RecurringTask)
        self.preferences = preferences if preferences else {}
        self.calendar = Calendar()  # Initialize a Calendar instance for scheduling

    def add_task(self, task):
        """Add a new task to the user's task list."""
        if isinstance(task, Task):
            self.tasks.append(task)
            print(f"Task '{task.name}' added for user {self.username}.")
        else:
            raise TypeError("Only instances of Task or its subclasses can be added.")

    def remove_task(self, task):
        """Remove a specified task from the user's task list."""
        if task in self.tasks:
            self.tasks.remove(task)
            print(f"Task '{task.name}' removed for user {self.username}.")
        else:
            print("Task not found in user's task list.")

    def get_tasks(self):
        """Retrieve all tasks associated with the user."""
        return self.tasks

    def update_preferences(self, preferences):
        """Update user-specific preferences."""
        self.preferences.update(preferences)
        print(f"Preferences updated for user {self.username}.")

    def schedule_tasks(self):
        """Schedule all tasks in the user's task list according to preferences."""
        self.calendar.schedule_all(self.tasks, self.preferences)
        print(f"All tasks scheduled for user {self.username}.")