# models/event.py

from datetime import datetime, timedelta
from Models.task import Task

class Event(Task):
    def __init__(self, name, duration, priority=0, is_immovable=False, dependencies=None, deadline=None):
        super().__init__(name, duration, priority, is_immovable, dependencies, deadline)

    def schedule(self, start_time=None):
        if not self.is_ready_to_schedule():
            raise ValueError(f"Event '{self.name}' cannot be scheduled until dependencies are met.")
        if start_time:
            self.set_scheduled_time(start_time)
        else:
            self.set_scheduled_time(datetime.now())
        
        print(f"Event '{self.name}' scheduled from {self.start_time} to {self.end_time}")

    def __repr__(self):
        return (f"Event(name={self.name}, duration={self.duration}, priority={self.priority}, "
                f"is_immovable={self.is_immovable}, start_time={self.start_time}, end_time={self.end_time})")

