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

    Attributes:
        schedule (list): Stores finalized task schedules.
        BREAK_INTERVAL (int): Interval (in minutes) between mandatory breaks.
        BREAK_DURATION (int): Duration (in minutes) of each mandatory break.
        WORKING_HOURS_START (int): Start of the working hours in minutes from midnight (default: 8 AM).
        WORKING_HOURS_END (int): End of the working hours in minutes from midnight (default: 9 PM).
    """

    def __init__(self, break_interval=90, break_duration=15):
        """
        Initializes the SchedulingStrategy class with break intervals and durations.

        Args:
            break_interval (int): Interval (in minutes) between breaks.
            break_duration (int): Duration (in minutes) of each break.

        Time Complexity:
            O(1) - Constant time initialization of variables.

        Space Complexity:
            O(1) - No additional memory usage besides class attributes.
        """

        self.schedule = []  # Stores finalized task schedules.
        self.BREAK_INTERVAL = break_interval  # Interval for scheduling breaks.
        self.BREAK_DURATION = break_duration  # Duration of each break.
        self.WORKING_HOURS_START = 8 * 60   # 8 AM in minutes
        self.WORKING_HOURS_END = 21 * 60    # 9 PM in minutes

    @staticmethod
    def get_minute_of_week(timestamp):
        """
        Converts a timestamp into the minute of the week.

        Args:
            timestamp (str): A timestamp string in the format "Day Mon DD YYYY HH:MM:SS".

        Returns:
            int: The minute of the week the timestamp corresponds to.

        Time Complexity:
            O(1) - Parsing the timestamp and performing calculations.

        Space Complexity:
            O(1) - Only intermediate variables used.
        """

        time_str = timestamp.replace("Start Time: ", "").split(" GMT")[0]
        dt = datetime.strptime(time_str, "%a %b %d %Y %H:%M:%S")
        day_of_week = dt.weekday()  # Monday = 0, Sunday = 6
        total_minutes = day_of_week * 24 * 60 + dt.hour * 60 + dt.minute
        return total_minutes

    @staticmethod
    def create_task(name, priority, dependencies, start_time=None, end_time=None, deadline=None, ETTC=None):
        """
        Creates a dictionary representing a task with the given attributes.

        Args:
            name (str): Name of the task.
            priority (int): Task priority level.
            dependencies (list): List of task dependencies (other task names).
            start_time (int, optional): Start time in minutes from the start of the week.
            end_time (int, optional): End time in minutes from the start of the week.
            deadline (int, optional): Deadline in minutes from the start of the week.
            ETTC (int, optional): Estimated time to complete the task, in minutes.

        Returns:
            dict: A dictionary representing the task.

        Time Complexity:
            O(1) - Dictionary creation.

        Space Complexity:
            O(1) - Minimal memory usage for the dictionary.
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
        """
        Generates all available time slots for a week, marking working hours and breaks.

        Returns:
            list: A list of dictionaries representing time slots.

        Time Complexity:
            O(N) - Where N is the number of minutes in a week (10,080).
            Iterates through every minute of the week.

        Space Complexity:
            O(N) - Stores a list of slots for the week.

        Note:
            - Working hours are determined by WORKING_HOURS_START and WORKING_HOURS_END.
            - Break intervals and durations are marked within working hours.
        """
        slots = []
        self.minute_to_slot_index = {}  # Map from minute_of_week to index in slots
        index = 0  # Index in slots
        week_minutes = 7 * 24 * 60  # Total minutes in a week

        for minute in range(week_minutes):
            day = minute // (24 * 60)
            minute_of_day = minute % (24 * 60)

            is_working_hour = self.WORKING_HOURS_START <= minute_of_day < self.WORKING_HOURS_END

            if is_working_hour:
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
        Converts a minute of the week into a readable day and time.

        Args:
            minutes (int): Minute of the week.

        Returns:
            str: A string representation of the day and time in "Day HH:MM AM/PM" format.

        Time Complexity:
            O(1) - Arithmetic and string formatting operations.

        Space Complexity:
            O(1) - Minimal memory for intermediate variables.
        """
        minutes_in_week = 7 * 1440  # 10080 minutes
        minutes = minutes % minutes_in_week

        day_index = minutes // 1440  # 0 to 6
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        day_name = day_names[day_index]

        minutes_in_day = minutes % 1440
        hours_24 = minutes_in_day // 60
        mins = minutes_in_day % 60

        if hours_24 == 0:
            hours_12 = 12
            period = 'AM'
        elif 1 <= hours_24 < 12:
            hours_12 = hours_24
            period = 'AM'
        elif hours_24 == 12:
            hours_12 = 12
            period = 'PM'
        else:
            hours_12 = hours_24 - 12
            period = 'PM'

        time_str = f"{hours_12}:{mins:02d} {period}"

        return f"{day_name} {time_str}"

    @staticmethod
    def print_schedule(weekly_slots):
        """
        Prints a summary of the schedule with task start and end times.

        Args:
            weekly_slots (list): List of time slots representing the weekly schedule.

        Time Complexity:
            O(N) - Iterates through all time slots to identify tasks.

        Space Complexity:
            O(M) - Where M is the number of unique tasks scheduled.

        Notes:
            - Outputs a readable schedule to the console.
        """
        task_schedule = {}

        for index, slot in enumerate(weekly_slots):
            if slot['is_occupied'] and slot['task'] is not None:
                task_name = slot['task']['name']
                if task_name not in task_schedule:
                    task_schedule[task_name] = []
                task_schedule[task_name].append(index)

        print("\nWeekly Schedule:")
        for task_name, slots in task_schedule.items():
            start_slot = slots[0]
            end_slot = slots[-1]
            print(f"Task {task_name} -> Time {SchedulingStrategy.convert_weekly_minute_to_hour(weekly_slots[start_slot]['start_time'])}-{SchedulingStrategy.convert_weekly_minute_to_hour(weekly_slots[end_slot]['end_time'])}")

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
        Optimizes the schedule by sorting tasks, scheduling fixed tasks,
        and applying a greedy algorithm for flexible tasks.

        Steps:
            1. Sorts tasks by priority and dependencies.
            2. Schedules fixed tasks with predefined start and end times.
            3. Greedy scheduling for tasks without predefined times.

        Args:
            tasks (list): List of task dictionaries to be scheduled.
            time_slots (list): List of time slot dictionaries for scheduling.

        Time Complexity:
            O(M + M log M + G) - Sorting tasks takes O(M log M),
            fixed task scheduling takes O(F), and greedy scheduling takes O(G),
            where M is the number of tasks, F is the number of fixed tasks,
            and G is the cost of greedy scheduling.

        Space Complexity:
            O(M + T) - Task dictionary storage (O(M)) and time slot index mapping (O(T)).
        """
        print("Starting optimization...")
        print(f"Initial number of tasks: {len(tasks)}")
        print(f"Initial time slots: {len(time_slots)}")

        # Step 1: Sort tasks and store task_dict
        print("Sorting tasks...")
        self.task_dict = {task['name']: task for task in tasks}
        task_dict = self.task_dict
        pm = PriorityManager(task_dict)
        sorted_task_queue = pm.sort_tasks()
        print("Tasks sorted by priority and dependencies:", list(sorted_task_queue))

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
        self.greedy_schedule(flexible_tasks, time_slots, completed_tasks)
        print("After greedy scheduling, schedule contains:")
        self.schedule.sort(key=lambda task: task['start_time'])
        
        # self.print_schedule(weekly_slots)
        # for task in self.schedule:
        #     print(f"  {task['name']} -> Start: {task.get('start_time')}, End: {task.get('end_time')}")

        # # # Step 4: Perform DP scheduling to minimize lateness
        # print("Running DP scheduling...")
        # self.DP_schedule(list(flexible_tasks), time_slots, completed_tasks)

        # Step 5: perform backtracking to handle edgecases
        # print("Running Backtracking Scheduling for edge cases...")
        # remaining_tasks = [task for task in tasks if task['name'] not in completed_tasks]
        # if remaining_tasks:
        #     self.backtracking_schedule(remaining_tasks, time_slots, completed_tasks)
        # else:
        #     print("No remaining tasks for backtracking.")

        #     self.backtracking_schedule()

    

    def schedule_fixed_tasks(self, fixed_tasks, time_slots, completed_tasks):
        """
        Schedules tasks with fixed start and end times into the given time slots.

        Resolves conflicts and includes mandatory breaks after each task.

        Args:
            fixed_tasks (list): List of fixed tasks with predefined start and end times.
            time_slots (list): List of time slot dictionaries for scheduling.
            completed_tasks (set): Set of already scheduled task names.

        Time Complexity:
            O(F * D) - Iterates over F fixed tasks and checks up to D time slots for each.

        Space Complexity:
            O(F + D) - Tracks completed tasks and temporary conflicting tasks.
        """
        for task in fixed_tasks:
            start_index = self.minute_to_slot_index.get(task['start_time'])
            end_index = self.minute_to_slot_index.get(task['end_time'] - 1)

            if start_index is None or end_index is None:
                print(f"Task {task['name']} cannot be scheduled because it is outside working hours.")
                continue

            # Include break after the task
            total_duration = (end_index - start_index + 1) + self.BREAK_DURATION
            adjusted_end_index = end_index + self.BREAK_DURATION

            if adjusted_end_index >= len(time_slots):
                adjusted_end_index = len(time_slots) - 1
                total_duration = adjusted_end_index - start_index + 1

            # Check for conflicts
            can_schedule = True
            conflicting_tasks = set()
            for i in range(start_index, adjusted_end_index + 1):
                if time_slots[i]["is_occupied"]:
                    if time_slots[i]["task"] is not None:
                        conflicting_tasks.add(time_slots[i]["task"]["name"])
                    else:
                        can_schedule = False
                        break

            if can_schedule:
                if conflicting_tasks:
                    # Resolve conflicts
                    self.resolve_conflicts(conflicting_tasks, time_slots, completed_tasks)

                # Assign the task
                for i in range(start_index, end_index + 1):
                    time_slots[i]["is_occupied"] = True
                    time_slots[i]["task"] = task
                # Assign break after the task
                for i in range(end_index + 1, adjusted_end_index + 1):
                    time_slots[i]["is_occupied"] = True
                    time_slots[i]["task"] = None
                # Update task metadata and add to schedule
                self.schedule.append(task)
                completed_tasks.add(task['name'])
                print(f"Task {task['name']} assigned to fixed slots {start_index}-{end_index} with break after.")
            else:
                print(f"Task {task['name']} could not be scheduled due to conflicts.")
                # Attempt to reschedule
                task['rescheduled'] = True
                self.greedy_schedule_task(task, time_slots, completed_tasks)

    def free_task_slots(self, task, time_slots):
        """
        Frees the time slots occupied by a task, including any associated breaks.

        Args:
            task (dict): Task dictionary whose slots need to be freed.
            time_slots (list): List of time slot dictionaries.

        Time Complexity:
            O(D) - Frees D time slots occupied by the task.

        Space Complexity:
            O(1) - No additional memory allocation.
        """
        
        # Free up the slots occupied by the task
        start_index = self.minute_to_slot_index.get(task['start_time'])
        end_index = self.minute_to_slot_index.get(task['end_time'] - 1)
        for i in range(start_index, end_index + 1):
            time_slots[i]["is_occupied"] = False
            time_slots[i]["task"] = None

        # Also free up the break time after the task
        break_end_index = end_index + self.BREAK_DURATION
        for i in range(end_index + 1, min(break_end_index + 1, len(time_slots))):
            time_slots[i]["is_occupied"] = False
            time_slots[i]["task"] = None

    def resolve_conflicts(self, conflicting_tasks, time_slots, completed_tasks):
        """
        Resolves conflicts by freeing slots of conflicting tasks and attempting to reschedule them.

        Args:
            conflicting_tasks (set): Set of conflicting task names.
            time_slots (list): List of time slot dictionaries.
            completed_tasks (set): Set of already scheduled task names.

        Time Complexity:
            O(C * (R + D)) - Where C is the number of conflicting tasks,
            R is the cost of rescheduling a task, and D is the number of slots per task.

        Space Complexity:
            O(C + D) - Temporary storage for conflicting tasks.
        """
        for conflict_task_name in conflicting_tasks:
            conflict_task = next((t for t in self.schedule if t['name'] == conflict_task_name), None)
            if conflict_task:
                # Remove the conflicting task from the schedule
                self.schedule.remove(conflict_task)
                completed_tasks.discard(conflict_task_name)
                # Free up the slots occupied by the conflicting task
                self.free_task_slots(conflict_task, time_slots)
                print(f"Rescheduling Task {conflict_task_name} due to conflict.")

                # Mark the task as needing rescheduling
                conflict_task['rescheduled'] = True

                # Attempt to reschedule the conflicting task
                self.greedy_schedule_task(conflict_task, time_slots, completed_tasks)

    def greedy_schedule_task(self, task, time_slots, completed_tasks):
        """
        Attempts to schedule a task greedily, respecting dependencies and deadlines.

        Args:
            task (dict): Task dictionary to be scheduled.
            time_slots (list): List of time slot dictionaries.
            completed_tasks (set): Set of already scheduled task names.

        Time Complexity:
            O(D * C) - Checks up to D slots and resolves conflicts recursively for C tasks.

        Space Complexity:
            O(D + C) - Temporary storage for dependencies and conflicts.
        """
        task_name = task['name']
        task_duration = self.get_task_duration(task)
        if task_duration is None:
            return

        dependencies = task.get("dependencies", [])
        dep_end_times = [self.task_dict[dep]['end_time'] for dep in dependencies if self.task_dict[dep]['end_time'] is not None]
        if dep_end_times:
            earliest_start_minute = max(dep_end_times)
            earliest_start = self.minute_to_slot_index.get(earliest_start_minute, 0)
        else:
            earliest_start = 0

        latest_start = len(time_slots) - task_duration - self.BREAK_DURATION

        if task.get('deadline') is not None:
            deadline_minutes = [minute for minute in self.minute_to_slot_index.keys() if minute < task['deadline']]
            if deadline_minutes:
                latest_deadline_minute = max(deadline_minutes)
                deadline_slot_index = self.minute_to_slot_index[latest_deadline_minute]
                latest_start = min(latest_start, deadline_slot_index - task_duration - self.BREAK_DURATION + 1)
            else:
                print(f"Task {task['name']} could not be rescheduled because its deadline is outside working hours.")
                return

        # Try to fit the task into available slots
        assigned = False
        for start_index in range(earliest_start, latest_start + 1):
            can_fit, new_conflicts = self.can_fit_with_conflict_resolution(task, time_slots, start_index, completed_tasks)
            if can_fit:
                self.assign_task_to_slot(task, time_slots, start_index)
                completed_tasks.add(task_name)
                assigned = True
                break
            elif new_conflicts:
                # Try to resolve conflicts recursively
                self.resolve_conflicts(new_conflicts, time_slots, completed_tasks)
                # Try to fit the task again
                can_fit_after_resolve, _ = self.can_fit_with_conflict_resolution(task, time_slots, start_index, completed_tasks)
                if can_fit_after_resolve:
                    self.assign_task_to_slot(task, time_slots, start_index)
                    completed_tasks.add(task_name)
                    assigned = True
                    break

        if not assigned:
            print(f"Task {task['name']} could not be rescheduled due to lack of available slots.")

    def greedy_schedule(self, sorted_task_queue, time_slots, completed_tasks):
        """
        Schedules flexible tasks using a greedy approach, resolving conflicts as needed.

        Args:
            sorted_task_queue (deque): Queue of tasks sorted by priority.
            time_slots (list): List of time slot dictionaries.
            completed_tasks (set): Set of already scheduled task names.

        Time Complexity:
            O(M * D * C) - Where M is the number of flexible tasks,
            D is the number of slots per task, and C is the cost of resolving conflicts.

        Space Complexity:
            O(M + T) - Task queue and completed tasks storage.
        """

        while sorted_task_queue:
            task_name = sorted_task_queue.pop()
            task = self.task_dict[task_name]

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
                dep_end_times = [self.task_dict[dep]['end_time'] for dep in dependencies if self.task_dict[dep]['end_time'] is not None]
                if dep_end_times:
                    earliest_start_minute = max(dep_end_times)
                    earliest_start = self.minute_to_slot_index.get(earliest_start_minute, 0)
                else:
                    earliest_start = 0
            else:
                earliest_start = 0

            latest_start = len(time_slots) - task_duration - self.BREAK_DURATION

            if task.get('deadline') is not None:
                deadline_minutes = [minute for minute in self.minute_to_slot_index.keys() if minute < task['deadline']]
                if deadline_minutes:
                    latest_deadline_minute = max(deadline_minutes)
                    deadline_slot_index = self.minute_to_slot_index[latest_deadline_minute]
                    latest_start = min(latest_start, deadline_slot_index - task_duration - self.BREAK_DURATION + 1)
                else:
                    print(f"Task {task['name']} could not be scheduled because its deadline is outside working hours.")
                    continue

            assigned = False
            for start_index in range(earliest_start, latest_start + 1):
                can_fit, conflicting_tasks = self.can_fit_with_conflict_resolution(task, time_slots, start_index, completed_tasks)
                if can_fit:
                    self.assign_task_to_slot(task, time_slots, start_index)
                    completed_tasks.add(task_name)
                    assigned = True
                    break
                elif conflicting_tasks:
                    # Try to resolve conflicts
                    self.resolve_conflicts(conflicting_tasks, time_slots, completed_tasks)
                    # Try to fit the task again
                    can_fit_after_resolve, _ = self.can_fit_with_conflict_resolution(task, time_slots, start_index, completed_tasks)
                    if can_fit_after_resolve:
                        self.assign_task_to_slot(task, time_slots, start_index)
                        completed_tasks.add(task_name)
                        assigned = True
                        break

            if not assigned:
                print(f"Task {task['name']} could not be scheduled due to lack of available slots.")

    def can_fit_with_conflict_resolution(self, task, time_slots, start_index, completed_tasks):
        """
        Determines if a task can fit in the given time slots, accounting for conflicts.

        Args:
            task (dict): Task dictionary to check.
            time_slots (list): List of time slot dictionaries.
            start_index (int): Starting index of the time slot.
            completed_tasks (set): Set of already scheduled task names.

        Returns:
            tuple: (bool, set) - Whether the task can fit and any conflicting tasks.

        Time Complexity:
            O(D) - Checks D time slots for the task's duration.

        Space Complexity:
            O(C) - Stores conflicting tasks temporarily.
        """
        task_duration = self.get_task_duration(task)
        if task_duration is None:
            return False, None

        total_duration = task_duration + self.BREAK_DURATION  # Task duration plus break
        end_index = start_index + total_duration - 1

        # Check if the task ends before its deadline
        if task.get('deadline') is not None:
            deadline_index = self.minute_to_slot_index.get(task['deadline'] - 1, len(time_slots) - 1)
            if end_index > deadline_index:
                return False, None

        if end_index >= len(time_slots):
            return False, None  # Not enough slots until the end

        conflicting_tasks = set()
        for i in range(start_index, end_index + 1):
            if time_slots[i]["is_occupied"]:
                if time_slots[i]["task"] is not None:
                    conflicting_tasks.add(time_slots[i]["task"]["name"])
                else:
                    # Slot is occupied by a break or other non-task event
                    return False, None

        return True, conflicting_tasks

    def assign_task_to_slot(self, task, time_slots, start_index):
        """
        Assigns a task to the specified time slots, including breaks after the task.

        Args:
            task (dict): Task dictionary to assign.
            time_slots (list): List of time slot dictionaries.
            start_index (int): Starting index for the task's schedule.

        Time Complexity:
            O(D) - Assigns D slots for the task and associated breaks.

        Space Complexity:
            O(1) - No additional memory allocation.
        """
        task_duration = self.get_task_duration(task)
        if task_duration is None:
            return

        for i in range(start_index, start_index + task_duration):
            time_slots[i]["is_occupied"] = True
            time_slots[i]["task"] = task

        # Assign break after the task
        for i in range(start_index + task_duration, start_index + task_duration + self.BREAK_DURATION):
            if i < len(time_slots):
                time_slots[i]["is_occupied"] = True  # Mark as break
                time_slots[i]["task"] = None

        start_time = time_slots[start_index]["start_time"]
        end_time = time_slots[start_index + task_duration - 1]["end_time"]
        task["start_time"] = start_time
        task["end_time"] = end_time
        self.schedule.append(task)
        print(f"Task {task['name']} assigned starting at minute {start_time}.")

        if task.get('rescheduled'):
            print(f"Task {task['name']} was rescheduled due to conflicts.")

    def DP_schedule(self, tasks, time_slots, completed_tasks):
        """
        Uses dynamic programming to minimize task lateness.

        Args:
            tasks (list): List of task dictionaries to schedule.
            time_slots (list): List of time slot dictionaries.
            completed_tasks (set): Set of already scheduled task names.

        Time Complexity:
            O(M * T) - Where M is the number of tasks with deadlines
            and T is the number of time slots.

        Space Complexity:
            O(M * T) - DP table and task schedule reconstruction.
        """
        print("Starting DP scheduling to minimize lateness...")
        
        # Filter tasks that have a deadline
        tasks_with_deadlines = [task for task in tasks if task.get('deadline') is not None]
        
        # Sort tasks by deadline (earliest deadline first)
        tasks_with_deadlines.sort(key=lambda task: task['deadline'])
        
        # Initialize DP table
        n = len(tasks_with_deadlines)
        dp = [[float('inf')] * (len(time_slots) + 1) for _ in range(n + 1)]
        dp[0][0] = 0  # Base case: no tasks, no lateness
        
        # Store task placement to reconstruct the schedule
        task_schedule = [[None] * (len(time_slots) + 1) for _ in range(n + 1)]
        
        for i in range(1, n + 1):
            task = tasks_with_deadlines[i - 1]
            task_duration = self.get_task_duration(task)
            if task_duration is None:
                continue

            for t in range(len(time_slots) + 1):
                # Option 1: Don't include the current task
                dp[i][t] = dp[i - 1][t]
                task_schedule[i][t] = task_schedule[i - 1][t]

                # Option 2: Include the current task if it fits
                if t >= task_duration:
                    completion_time = t
                    lateness = completion_time - task['deadline']
                    
                    if dp[i - 1][t - task_duration] + lateness < dp[i][t]:
                        dp[i][t] = dp[i - 1][t - task_duration] + lateness
                        task_schedule[i][t] = (task, t - task_duration)
        
        # Backtrack to assign tasks based on the DP table
        t = len(time_slots)
        for i in range(n, 0, -1):
            if task_schedule[i][t] is not None:
                task, start_time = task_schedule[i][t]
                self.assign_task_to_slot(task, time_slots, start_time)
                completed_tasks.add(task['name'])
                t -= self.get_task_duration(task)

    def backtracking_schedule(self, tasks, time_slots, completed_tasks):
        """
        Optimized backtracking scheduler to handle edge cases.

        Args:
            tasks (list): List of unscheduled task dictionaries.
            time_slots (list): List of time slot dictionaries.
            completed_tasks (set): Set of already scheduled task names.

        Time Complexity:
            O(C * D) - Where C is the number of conflicting tasks, and D is the number of time slots per task.

        Space Complexity:
            O(C + D) - Temporary storage for conflicts and recursion stack.
        """

        def is_feasible(task, start_index):
            """
            Checks if the task can be scheduled starting at the given index.

            Args:
                task (dict): Task to check.
                start_index (int): Index to start scheduling.

            Returns:
                bool: True if the task can be scheduled, False otherwise.
            """
            task_duration = self.get_task_duration(task)
            if task_duration is None:
                return False

            total_duration = task_duration + self.BREAK_DURATION
            end_index = start_index + total_duration - 1

            if task.get('deadline') is not None:
                deadline_index = self.minute_to_slot_index.get(task['deadline'] - 1, len(time_slots) - 1)
                if end_index > deadline_index:
                    return False

            if end_index >= len(time_slots):
                return False

            for i in range(start_index, end_index + 1):
                if time_slots[i]["is_occupied"]:
                    return False

            return True

        def try_schedule_task(task):
            """
            Attempts to schedule a single task into available time slots.

            Args:
                task (dict): Task to schedule.

            Returns:
                bool: True if the task was successfully scheduled, False otherwise.
            """
            task_duration = self.get_task_duration(task)
            if task_duration is None:
                return False

            earliest_start = 0
            dependencies = task.get("dependencies", [])
            dep_end_times = [self.task_dict[dep]['end_time'] for dep in dependencies if self.task_dict[dep]['end_time'] is not None]
            if dep_end_times:
                earliest_start_minute = max(dep_end_times)
                earliest_start = self.minute_to_slot_index.get(earliest_start_minute, 0)

            latest_start = len(time_slots) - task_duration - self.BREAK_DURATION
            if task.get('deadline') is not None:
                deadline_minutes = [minute for minute in self.minute_to_slot_index.keys() if minute < task['deadline']]
                if deadline_minutes:
                    latest_deadline_minute = max(deadline_minutes)
                    deadline_slot_index = self.minute_to_slot_index[latest_deadline_minute]
                    latest_start = min(latest_start, deadline_slot_index - task_duration - self.BREAK_DURATION + 1)

            for start_index in range(earliest_start, latest_start + 1):
                if is_feasible(task, start_index):
                    self.assign_task_to_slot(task, time_slots, start_index)
                    completed_tasks.add(task['name'])
                    return True

            return False

        def backtrack(index):
            """
            Recursive backtracking function to schedule tasks.

            Args:
                index (int): Index of the current task to attempt scheduling.

            Returns:
                bool: True if all tasks were successfully scheduled, False otherwise.
            """
            if index == len(tasks):
                return True  # All tasks have been scheduled

            task = tasks[index]
            if task['name'] in completed_tasks:
                return backtrack(index + 1)

            if try_schedule_task(task):
                if backtrack(index + 1):
                    return True

                # Undo the assignment (backtrack)
                self.free_task_slots(task, time_slots)
                completed_tasks.remove(task['name'])

            return False

        # Sort tasks by priority, deadline, and duration to maximize efficiency
        tasks.sort(key=lambda t: (t['priority'], t.get('deadline', float('inf')), self.get_task_duration(t)), reverse=True)

        # Start the backtracking process
        print("Starting optimized backtracking...")
        if not backtrack(0):
            print("Backtracking could not resolve conflicts.")
        else:
            print("Backtracking successfully resolved conflicts.")

if __name__ == "__main__":
    scheduler = SchedulingStrategy()

    # Create tasks
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
        scheduler.create_task(
            name="E4",
            priority=5,
            dependencies=[],
            start_time=SchedulingStrategy.get_minute_of_week("Tue Nov 12 2024 12:00:00 GMT-0500 (Eastern Standard Time)"),
            end_time=SchedulingStrategy.get_minute_of_week("Tue Nov 12 2024 14:00:00 GMT-0500 (Eastern Standard Time)"),
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

    tasks2 = [
        SchedulingStrategy.create_task(name="Task A", priority=10, dependencies=[], deadline=300, ETTC=120),
        SchedulingStrategy.create_task(name="Task B", priority=8, dependencies=[], deadline=480, ETTC=90),
        SchedulingStrategy.create_task(name="Task C", priority=7, dependencies=[], deadline=960, ETTC=180),
        SchedulingStrategy.create_task(name="Task D", priority=6, dependencies=["Task A"], deadline=1080, ETTC=60),
        SchedulingStrategy.create_task(name="Task E", priority=5, dependencies=["Task B"], deadline=1440, ETTC=120),
        SchedulingStrategy.create_task(name="Task F", priority=4, dependencies=[], deadline=600, ETTC=30),
]
    
    
    # Generate weekly slots
    weekly_slots = scheduler.generate_weekly_slots()

    # Optimize schedule
    scheduler.optimize_schedule(tasks, weekly_slots)


    # Print the weekly schedule
    SchedulingStrategy.print_schedule(weekly_slots)