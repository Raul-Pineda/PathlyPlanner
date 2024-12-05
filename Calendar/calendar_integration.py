from ics import Calendar, Event
from datetime import datetime, timedelta
import uuid
import sys, os
# print("Python executable:", sys.executable)
# print("sys.path:", sys.path)
print("Current working directory:", os.getcwd())

class calendarIntegration:
    def __init__(self, tasks, week_start=None):
        """
        Initialize the scheduling_integration class with a list of tasks.

        Each task is a dictionary with the following keys:
            - 'name': Name of the task (string).
            - 'priority': Task priority (int).
            - 'dependencies': List of dependent task names (list of strings).
            - 'start_time': Start time in minutes from the start of the week (int).
            - 'end_time': End time in minutes from the start of the week (int).
            - 'duration': Duration in minutes (int).
            - 'deadline': Deadline in minutes from the start of the week (int).
            - 'estimated_time_to_complete': Estimated time to complete in minutes (int).
            - 'earliest_start_time': Earliest possible start time in minutes from the start of the week (int, optional).
            - 'latest_start_time': Latest possible start time in minutes from the start of the week (int, optional).
        """
        self.tasks = tasks
        if week_start is None:
            # Set week_start to the most recent Monday at 00:00
            today = datetime.today()
            week_start = today - timedelta(days=today.weekday(),
                                           hours=today.hour,
                                           minutes=today.minute,
                                           seconds=today.second,
                                           microseconds=today.microsecond)
        self.week_start = week_start


    def calculate_start_time(date_time):
        """
        Calculate start_time in minutes from the start of the week.

        Args:
            date_time (datetime): The datetime object.

        Returns:
            int: The start_time in minutes from the week's start.
        """
        # Calculate the number of minutes from the start of the week
        day_of_week = date_time.weekday()  # Monday = 0, Sunday = 6
        hour = date_time.hour
        minute = date_time.minute
        start_time = (day_of_week * 1440) + (hour * 60) + minute
        return start_time
    

    def export_to_ics(self, filename):
        """
        Export the tasks to an .ics file.

        Parameters:
            - filename: The name of the file to save the calendar to (string).
        """
        cal = Calendar()
        for task in self.tasks:
            event = Event()
            event.name = task.get('name', 'No Title')

            # Convert 'start_time' and 'end_time' from minutes to datetime
            start_time = task.get('start_time')
            end_time = task.get('end_time')

            if start_time is not None:
                event.begin = self.week_start + timedelta(minutes=start_time)
            else:
                # Skip tasks without a start_time
                continue

            if end_time is not None:
                event.end = self.week_start + timedelta(minutes=end_time)
            elif task.get('duration') is not None:
                # Calculate end_time using duration
                event.end = event.begin + timedelta(minutes=task['duration'])
            elif task.get('estimated_time_to_complete') is not None:
                # Use estimated time to complete
                event.end = event.begin + timedelta(minutes=task['estimated_time_to_complete'])
            else:
                # Default duration of 1 hour
                event.end = event.begin + timedelta(hours=1)

            # Set priority
            priority = task.get('priority')
            if priority is not None:
                event.priority = priority

            # Build description
            description = []

            dependencies = task.get('dependencies', [])
            if dependencies:
                description.append('Dependencies: ' + ', '.join(dependencies))

            deadline = task.get('deadline')
            if deadline is not None:
                deadline_dt = self.week_start + timedelta(minutes=deadline)
                description.append(f'Deadline: {deadline_dt.strftime("%Y-%m-%d %H:%M")}')

            estimated_time = task.get('estimated_time_to_complete')
            if estimated_time is not None:
                description.append(f'Estimated Time to Complete: {estimated_time} minutes')

            earliest_start_time = task.get('earliest_start_time')
            if earliest_start_time is not None:
                earliest_dt = self.week_start + timedelta(minutes=earliest_start_time)
                description.append(f'Earliest Start Time: {earliest_dt.strftime("%Y-%m-%d %H:%M")}')

            latest_start_time = task.get('latest_start_time')
            if latest_start_time is not None:
                latest_dt = self.week_start + timedelta(minutes=latest_start_time)
                description.append(f'Latest Start Time: {latest_dt.strftime("%Y-%m-%d %H:%M")}')

            event.description = '\n'.join(description)

            # Generate a unique identifier
            event.uid = str(uuid.uuid4())
            cal.events.add(event)

        with open(filename, 'w') as f:
            f.writelines(cal)

# Your provided list of task dictionaries
tasks = [{'name': 'E1', 'priority': 5, 'dependencies': [],
 'start_time': 540, 'end_time': 660, 'duration': 120, 'deadline': None, 'estimated_time_to_complete': None}, 
 {'name': 'E2', 'priority': 5, 'dependencies': ['E1'], 'start_time': 660, 'end_time': 780, 'duration': 120, 'deadline': None, 'estimated_time_to_complete': None, 'rescheduled': True}, 
 {'name': 'E3', 'priority': 8, 'dependencies': [], 'start_time': 3480, 'end_time': 3600, 'duration': 120, 'deadline': None, 'estimated_time_to_complete': None}, 
 {'name': 'E4', 'priority': 5, 'dependencies': [], 'start_time': 2160, 'end_time': 2280, 'duration': 120, 'deadline': None, 'estimated_time_to_complete': None}, 
 {'name': 'D1', 'priority': 8, 'dependencies': ['E3'], 'start_time': 3615, 'end_time': 3795, 'duration': None, 'deadline': 5400, 'estimated_time_to_complete': 180}, 
 {'name': 'D2', 'priority': 7, 'dependencies': ['D1'], 'start_time': 3810, 'end_time': 4050, 'duration': None, 'deadline': 6780, 'estimated_time_to_complete': 240}, 
 {'name': 'D3', 'priority': 9, 'dependencies': [], 'start_time': 480, 'end_time': 600, 'duration': None, 'deadline': 9600, 'estimated_time_to_complete': 120}]

# Create an instance of scheduling_integration
scheduler = calendarIntegration(tasks)

# Export tasks to an .ics file
scheduler.export_to_ics('my_schedule.ics')