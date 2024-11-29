# scheduling_strategy.py

from collections import deque
from priority_manager import PriorityManager  # Ensure this import points to your PriorityManager file
from datetime import datetime, timedelta
import math

class SchedulingStrategy:
    """
    Handles task scheduling using optimization strategies.

    Combines Greedy, Dynamic Programming, and Backtracking approaches
    to optimize task scheduling based on priorities, deadlines, and constraints.
    """

    def __init__(self, break_interval=90, break_duration=15):
        """
        Initializes the SchedulingStrategy object.

        Args:
            break_interval (int): Interval in minutes for mandatory breaks.
            break_duration (int): Duration of each mandatory break in minutes.
        """
        self.schedule = []  # Stores finalized task schedules.
        self.BREAK_INTERVAL = break_interval  # Interval for scheduling breaks.
        self.BREAK_DURATION = break_duration  # Duration of each break.
        self.WORKING_HOURS_START = 9 * 60   # 9 AM in minutes
        self.WORKING_HOURS_END = 17 * 60    # 5 PM in minutes

    @staticmethod
    def get_minute_of_week(timestamp):
        """
        Converts a timestamp string into the minute of the week it represents.

        Args:
            timestamp (str): Input timestamp string in the format:
                             "Sat Nov 09 2024 20:00:00 GMT-0500 (Eastern Standard Time)"

        Returns:
            int: Minute of the week (0-10079) corresponding to the input timestamp.
        """
        time_str = timestamp.replace("Start Time: ", "").split(" GMT")[0]
        dt = datetime.strptime(time_str, "%a %b %d %Y %H:%M:%S")
        day_of_week = dt.weekday()  # Monday = 0, Sunday = 6
        total_minutes = day_of_week * 24 * 60 + dt.hour * 60 + dt.minute
        return total_minutes

    @staticmethod
    def create_task(name, priority, dependencies, start_time=None, end_time=None, deadline=None, ETTC=None):
        """
        Creates a task dictionary.

        Args:
            name (str): Name of the task.
            priority (int): Task priority.
            dependencies (list): List of dependent task names.
            start_time (int): Start time in minutes from the start of the week.
            end_time (int): End time in minutes from the start of the week.
            deadline (int): Deadline in minutes from the start of the week.
            ETTC (int): Estimated time to complete in minutes.

        Returns:
            dict: Task dictionary.
        """
        return {
            'name': name,
            'priority': priority,
            'dependencies': dependencies,
            'start_time': start_time,
            'end_time': end_time,
            'duration': (end_time - start_time) if start_time and end_time else None,
            'deadline': deadline,
            'estimated_time_to_complete': ETTC
        }

    def generate_weekly_slots(self):
        slots = []
        self.minute_to_slot_index = {}  # Map from minute_of_week to index in slots
        index = 0  # Index in slots
        week_minutes = 7 * 24 * 60  # Total minutes in a week

        for minute in range(week_minutes):
            # Determine the day of the week and minute of the day
            day = minute // (24 * 60)
            minute_of_day = minute % (24 * 60)

            # Check if the current minute falls within working hours
            is_working_hour = self.WORKING_HOURS_START <= minute_of_day < self.WORKING_HOURS_END

            if is_working_hour:
                # Determine if the current minute falls within a break period
                work_time_since_start = (minute_of_day - self.WORKING_HOURS_START)
                is_break = (work_time_since_start % (self.BREAK_INTERVAL + self.BREAK_DURATION)) >= self.BREAK_INTERVAL

                slots.append({
                    "start_time": minute,
                    "end_time": minute + 1,
                    "is_occupied": False,  # By default, slots are unoccupied
                    "is_break": is_break,  # Mark slot as break if it's a break time
                    "task": None,
                })
                self.minute_to_slot_index[minute] = index
                index += 1
        return slots

    @staticmethod
    def convert_weekly_minute_to_hour(minutes):
        """
        Converts a minute-based value into the hour of the day in HH:MM format (formatted string).

        Args:
            minutes (int): Total number of minutes (can exceed 1440 for testing purposes).

        Returns:
            str: Time in HH:MM format for the corresponding minute of the day, ignoring the day.
        """
        # Reduce minutes to a single day's range (0 to 1439)
        minutes_in_a_day = 1440
        minutes = minutes % minutes_in_a_day

        # Calculate hours and minutes
        hours = minutes // 60
        mins = minutes % 60

        # Format as HH:MM0
        return f"{hours:02}:{mins:02}"
        
    @staticmethod
    def print_schedule(weekly_slots):
        """
        Prints the tasks scheduled in each slot range for the week.

        Args:
            weekly_slots (list): List of time slots for the week.

        Returns:
            None: Prints the schedule.
        """
        task_schedule = {}
        
        # Aggregate slots for each task
        for index, slot in enumerate(weekly_slots):
            if slot['is_occupied'] and slot['task'] is not None:  # Ensure 'task' is not None
                task_name = slot['task']['name']
                if task_name not in task_schedule:
                    task_schedule[task_name] = []
                task_schedule[task_name].append(index)
        
        # Print task schedule with slot ranges
        print("\nWeekly Schedule:")
        for task_name, slots in task_schedule.items():
            start_slot = slots[0]
            end_slot = slots[-1]
            print(f"Task {task_name} -> Time {SchedulingStrategy.convert_weekly_minute_to_hour(start_slot)}-{SchedulingStrategy.convert_weekly_minute_to_hour(end_slot)}")

    def get_task_duration(self, task):
        duration = task.get("duration")
        if duration is None:
            duration = task.get("estimated_time_to_complete")
        if duration is None:
            print(f"Task {task['name']} skipped (no duration or estimated time to complete).")
            return None
        return int(math.ceil(duration))

    def optimize_schedule(self, tasks, time_slots):
        """
        Main function to optimize the schedule.
        Combines Greedy, Dynamic Programming, and Backtracking approaches.

        Steps:
        1. Use PriorityManager to sort tasks by priority and resolve dependencies.
        2. Schedule fixed tasks.
        3. Greedy: Quickly fill time slots with highest-priority tasks.
        4. DP: Refine schedule to minimize lateness.
        5. Backtracking: Handle edge cases with complex dependencies.

        Args:
            tasks (list): List of Task objects to be scheduled.
            time_slots (list): List of available time slots.

        Returns:
            None: Updates `self.schedule`.
        """
        print("Starting optimization...")
        print(f"Initial number of tasks: {len(tasks)}")
        print(f"Initial time slots: {len(time_slots)}")

        # Step 1: Use PriorityManager to sort tasks
        print("Sorting tasks using PriorityManager...")
        task_dict = {task['name']: task for task in tasks}
        pm = PriorityManager(task_dict)
        sorted_task_queue = pm.sort_tasks()
        print("Tasks sorted by PriorityManager:", list(sorted_task_queue))

        # Separate tasks into fixed and flexible
        fixed_tasks = []
        flexible_tasks = deque()
        for task_name in sorted_task_queue:
            task = task_dict[task_name]
            if task.get('start_time') is not None and task.get('end_time') is not None:
                fixed_tasks.append(task)
            else:
                flexible_tasks.append(task_name)

        # Initialize completed tasks set
        completed_tasks = set()

        # Step 2: Schedule fixed tasks
        print("Scheduling fixed tasks...")
        self.schedule_fixed_tasks(fixed_tasks, time_slots, completed_tasks)
        print("Fixed tasks scheduled.")

        # Step 3: Perform greedy scheduling
        print("Running Greedy Scheduling...")
        self.greedy_schedule(flexible_tasks, task_dict, time_slots, completed_tasks)
        print("After greedy scheduling, schedule contains:")
        for task in self.schedule:
            print(f"  {task['name']} -> Start: {task.get('start_time')}, End: {task.get('end_time')}")

        # Final output
        print("Final Optimized Schedule:")
        for task in self.schedule:
            print(f"  Task {task['name']} -> Start Time: {task.get('start_time')}, End Time: {task.get('end_time')}")


    def schedule_fixed_tasks(self, fixed_tasks, time_slots, completed_tasks):
        for task in fixed_tasks:
            # Map task's start_time and end_time to indices in time_slots
            if task['start_time'] in self.minute_to_slot_index and task['end_time'] - 1 in self.minute_to_slot_index:
                start_index = self.minute_to_slot_index[task['start_time']]
                end_index = self.minute_to_slot_index[task['end_time'] - 1]
                task_duration = end_index - start_index + 1

                # Check if the slots are available
                if self.can_fit_fixed(task, time_slots, start_index, task_duration):
                    self.assign_task_to_slot_fixed(task, time_slots, start_index, task_duration)
                    # Add the task name to completed_tasks
                    completed_tasks.add(task['name'])
                else:
                    print(f"Task {task['name']} cannot be scheduled at its fixed time due to conflicts.")
            else:
                missing_times = []
                if task['start_time'] not in self.minute_to_slot_index:
                    missing_times.append('start_time')
                if task['end_time'] - 1 not in self.minute_to_slot_index:
                    missing_times.append('end_time')
                print(f"Task {task['name']} cannot be scheduled because its {', '.join(missing_times)} is outside working hours.")

    def can_fit_fixed(self, task, time_slots, start_index, task_duration):
        for i in range(start_index, start_index + task_duration):
            if i >= len(time_slots) or time_slots[i]["task"] is not None:
                return False
        return True

    def assign_task_to_slot_fixed(self, task, time_slots, start_index, task_duration):
        for i in range(start_index, start_index + task_duration):
            time_slots[i]["is_occupied"] = True
            time_slots[i]["task"] = task

        # Update task metadata and add to schedule
        self.schedule.append(task)
        print(f"Task {task['name']} assigned to fixed slots {start_index}-{start_index + task_duration - 1}.")

    def greedy_schedule(self, sorted_task_queue, task_dict, time_slots, completed_tasks):
        while sorted_task_queue:
            task_name = sorted_task_queue.pop()
            task = task_dict[task_name]
            
            # Check if dependencies are met
            dependencies = task.get("dependencies", [])
            if not all(dep in completed_tasks for dep in dependencies):
                sorted_task_queue.appendleft(task_name)
                continue

            task_duration = self.get_task_duration(task)
            if task_duration is None:
                continue

            # Determine earliest and latest start indices
            if dependencies:
                dep_end_times = [task_dict[dep]['end_time'] for dep in dependencies if task_dict[dep]['end_time'] is not None]
                if dep_end_times:
                    earliest_start_minute = max(dep_end_times)
                    earliest_start = self.minute_to_slot_index.get(earliest_start_minute, 0)
                else:
                    earliest_start = 0
            else:
                # Set earliest_start to the first available slot after fixed tasks
                earliest_start = 0
                while earliest_start < len(time_slots) and time_slots[earliest_start]["is_occupied"]:
                    earliest_start += 1

            latest_start = len(time_slots) - task_duration

            if task.get('deadline') is not None:
                # Find the latest working minute before the deadline
                deadline_minutes = [minute for minute in self.minute_to_slot_index.keys() if minute < task['deadline']]
                if deadline_minutes:
                    latest_deadline_minute = max(deadline_minutes)
                    deadline_slot_index = self.minute_to_slot_index[latest_deadline_minute]
                    latest_start = min(latest_start, deadline_slot_index - task_duration + 1)
                else:
                    # No working slots before deadline
                    print(f"Task {task['name']} could not be scheduled because its deadline is outside working hours.")
                    continue

            task['earliest_start_time'] = earliest_start
            task['latest_start_time'] = latest_start

            # Try to fit the task into available slots
            assigned = False
            for start_index in range(earliest_start, latest_start + 1):
                if self.can_fit(task, time_slots, start_index):
                    self.assign_task_to_slot(task, time_slots, start_index)
                    completed_tasks.add(task_name)
                    assigned = True
                    break
            if not assigned:
                print(f"Task {task['name']} could not be scheduled due to lack of available slots.")

    def can_fit(self, task, time_slots, start_index):
        task_duration = self.get_task_duration(task)
        if task_duration is None:
            return False

        earliest_start = task.get('earliest_start_time', 0)
        latest_start = task.get('latest_start_time', len(time_slots) - 1)
        if start_index < earliest_start or start_index > latest_start:
            return False

        # Check if the task will finish before its deadline
        if task.get('deadline') is not None:
            deadline_slot = self.minute_to_slot_index.get(task['deadline'] - 1, latest_start)
            latest_start = min(latest_start, deadline_slot)

        # Check if there are enough available slots during working hours
        slots_needed = task_duration
        i = start_index
        while slots_needed > 0 and i <= latest_start:
            slot = time_slots[i]
            if slot["is_occupied"]:
                i += 1
                continue
            slots_needed -= 1
            i += 1

        return slots_needed == 0

    def assign_task_to_slot(self, task, time_slots, start_index):
        task_duration = self.get_task_duration(task)
        if task_duration is None:
            return

        if not self.can_fit(task, time_slots, start_index):
            return

        # Assign task to the required slots
        slots_assigned = 0
        i = start_index
        start_time = None
        while slots_assigned < task_duration and i < len(time_slots):
            slot = time_slots[i]
            if slot["is_occupied"]:
                i += 1
                continue
            slot["is_occupied"] = True
            slot["task"] = task
            if start_time is None:
                start_time = slot["start_time"]
            end_time = slot["end_time"]
            slots_assigned += 1
            i += 1

        # Update task metadata and add to schedule
        task["start_time"] = start_time
        task["end_time"] = end_time
        self.schedule.append(task)
        print(f"Task {task['name']} assigned starting at minute {start_time}.")
if __name__ == "__main__":
    scheduler = SchedulingStrategy()

    # Create tasks using the methods in SchedulingStrategy
    tasks = [
        # Event tasks
        scheduler.create_task(
            name="E1",
            priority=4,
            dependencies=[],
            start_time=SchedulingStrategy.get_minute_of_week("Mon Nov 11 2024 09:00:00 GMT-0500 (Eastern Standard Time)"),
            end_time=SchedulingStrategy.get_minute_of_week("Mon Nov 11 2024 11:00:00 GMT-0500 (Eastern Standard Time)"),
            deadline=None,
            ETTC=None
        ),
        scheduler.create_task(
            name="E2",
            priority=5,
            dependencies=["E1"],
            start_time=SchedulingStrategy.get_minute_of_week("Tue Nov 12 2024 14:00:00 GMT-0500 (Eastern Standard Time)"),
            end_time=SchedulingStrategy.get_minute_of_week("Tue Nov 12 2024 16:00:00 GMT-0500 (Eastern Standard Time)"),
            deadline=None,
            ETTC=None
        ),
        scheduler.create_task(
            name="E3",
            priority=3,
            dependencies=[],
            start_time=SchedulingStrategy.get_minute_of_week("Wed Nov 13 2024 10:00:00 GMT-0500 (Eastern Standard Time)"),
            end_time=SchedulingStrategy.get_minute_of_week("Wed Nov 13 2024 12:00:00 GMT-0500 (Eastern Standard Time)"),
            deadline=None,
            ETTC=None
        ),
        # Deadline tasks
        scheduler.create_task(
            name="D1",
            priority=8,
            dependencies=["E3"],
            start_time=None,
            end_time=None,
            deadline=SchedulingStrategy.get_minute_of_week("Thu Nov 14 2024 18:00:00 GMT-0500 (Eastern Standard Time)"),
            ETTC=180  # 3 hours
        ),
        scheduler.create_task(
            name="D2",
            priority=7,
            dependencies=["D1"],
            start_time=None,
            end_time=None,
            deadline=SchedulingStrategy.get_minute_of_week("Fri Nov 15 2024 17:00:00 GMT-0500 (Eastern Standard Time)"),
            ETTC=240  # 4 hours
        ),
        scheduler.create_task(
            name="D3",
            priority=9,
            dependencies=[],
            start_time=None,
            end_time=None,
            deadline=SchedulingStrategy.get_minute_of_week("Sun Nov 17 2024 16:00:00 GMT-0500 (Eastern Standard Time)"),
            ETTC=120  # 2 hours
        ),
    ]

    # Generate weekly slots
    weekly_slots = scheduler.generate_weekly_slots()

    # Optimize schedule
    scheduler.optimize_schedule(tasks, weekly_slots)

    # Print results
    print("\nFinal Schedule:")
    for task in scheduler.schedule:
        print(f"Task {task['name']} -> Start Time: {task.get('start_time', 'N/A')}, End Time: {task.get('end_time', 'N/A')}, Priority: {task['priority']}, Deadline: {task.get('deadline', 'N/A')}, ETTC: {task.get('estimated_time_to_complete', 'N/A')}")