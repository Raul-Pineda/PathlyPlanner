# scheduling_strategy.py

from collections import deque
from priority_manager import PriorityManager  # Ensure this import points to your PriorityManager file

class SchedulingStrategy:
    """
    Handles task scheduling using optimization strategies.

    Combines Greedy, Dynamic Programming, and Backtracking approaches
    to optimize task scheduling based on priorities, deadlines, and constraints.
    """

    def __init__(self):
        """
        Initializes the SchedulingStrategy object.
        """
        # Stores the final schedule after optimization
        self.schedule = []

    def optimize_schedule(self, tasks, time_slots):
        """
        Main function to optimize the schedule.
        Combines Greedy, Dynamic Programming, and Backtracking approaches.

        Steps:
        1. Use PriorityManager to sort tasks by priority and resolve dependencies.
        2. Greedy: Quickly fill time slots with highest-priority tasks.
        3. DP: Refine schedule to minimize lateness.
        4. Backtracking: Handle edge cases with complex dependencies.

        Args:
            tasks (list): List of Task objects to be scheduled.
            time_slots (list): List of available time slots.

        Returns:
            None: Updates `self.schedule`.
        """
        # Step 1: Use PriorityManager to sort tasks
        print("Sorting tasks using PriorityManager...")
        task_dict = {task['name']: task for task in tasks}  # Convert list of tasks to a dictionary
        pm = PriorityManager(task_dict)
        sorted_task_queue = pm.sort_tasks()  # Returns a deque of task names in sorted order
        print("Tasks sorted by PriorityManager:", list(sorted_task_queue))

        # Step 2: Perform greedy scheduling using sorted tasks
        print("Running Greedy Scheduling...")
        self.greedy_schedule(sorted_task_queue, task_dict, time_slots)

        # Step 3 (Optional): Refine schedule using Dynamic Programming
        print("Running Dynamic Programming to Minimize Lateness...")
        refined_schedule = self.dp_minimize_lateness(tasks)
        print("Dynamic Programming Complete. Refined Schedule:")
        for task in refined_schedule:
            print(f"  Task {task['name']} -> Start Time: {task['start_time']}")
        
        # Replace current schedule with refined schedule
        self.schedule = refined_schedule

        # Step 4 (Optional): Use Backtracking to handle complex dependencies
        print("Running Backtracking to Handle Edge Cases...")
        if not self.backtracking_schedule(tasks, [], time_slots):
            print("Warning: Backtracking could not resolve all conflicts.")

        # Final schedule
        print("Final Optimized Schedule:")
        for task in self.schedule:
            print(f"  Task {task['name']} -> Start Time: {task['start_time']}")

    def greedy_schedule(self, sorted_task_queue, task_dict, time_slots):
        """
        Greedy algorithm enhanced with dependency resolution.

        Args:
            sorted_task_queue (deque): Deque of sorted task names from PriorityManager.
            task_dict (dict): Dictionary of Task objects.
            time_slots (list): List of available time slots.

        Returns:
            None: Updates `self.schedule`.

        Time Complexity:
            Best: O(T + T * S)
            Average: O(T + T * S)
            Worst: O(T + T * S)

        Space Complexity:
            Best, Average, Worst: O(1)
        """

        while sorted_task_queue:
            task_name = sorted_task_queue.pop()  # Get task name from deque
            task = task_dict[task_name]  # Retrieve task object from dictionary
            print(f"Processing task: {task['name']} with priority {task['priority']}")

            for slot in time_slots:
                print(f"  Checking time slot {slot['start_time']}-{slot['end_time']}")
                if self.can_fit(task, slot):
                    self.assign_task_to_slot(task, slot)
                    break  # Task assigned, move to next

    def can_fit(self, task, slot):
        """
        Check if the task can fit into the given time slot.

        Args:
            task (Task): The task to check.
            slot (TimeSlot): The time slot to evaluate.

        Returns:
            bool: True if the task fits in the slot, False otherwise.

        Time Complexity:
            Best, Average, Worst: O(1)

        Space Complexity:
            Best, Average, Worst: O(1)
        """
        return slot.start_time + task.duration <= slot.end_time and not slot.is_occupied

    def assign_task_to_slot(self, task, slot):
        """
        Assign a task to the given slot and update scheduling data.

        Args:
            task (Task): The task to assign.
            slot (TimeSlot): The slot to which the task is assigned.

        Returns:
            None: Updates `self.schedule`.

        Time Complexity:
            Best, Average, Worst: O(1)

        Space Complexity:
            Best, Average, Worst: O(1)
        """
        slot.is_occupied = True
        slot.task = task
        task.start_time = slot.start_time
        self.schedule.append(task)

    def dp_minimize_lateness(self, tasks):
        """
        Dynamic Programming to minimize task lateness with reduced space complexity.

        Args:
            tasks (list): List of Task objects to schedule.

        Returns:
            list: Optimized schedule.

        Time Complexity:
            Best, Average, Worst: O(T^2)

        Space Complexity:
            Best, Average, Worst: O(T)
        """
        tasks.sort(key=lambda task: task.deadline)  # O(T log T)
        n = len(tasks)
        
        # Use a 1D rolling array for DP
        dp = [0] * (n + 1)

        for i in range(1, n + 1):
            for j in range(n, 0, -1):  # Iterate backward to prevent overwriting
                if tasks[i - 1].duration <= j:
                    dp[j] = max(dp[j], dp[j - tasks[i - 1].duration] + tasks[i - 1].priority)
        
        # Reconstruct the schedule
        schedule = []
        remaining_time = n
        for i in range(n, 0, -1):
            if dp[remaining_time] != dp[remaining_time - tasks[i - 1].duration]:
                schedule.append(tasks[i - 1])
                remaining_time -= tasks[i - 1].duration

        self.schedule = schedule
        return schedule

    def backtracking_schedule(self, tasks, current_schedule, time_slots, memo=None):
        """
        Improved backtracking with pruning and memoization.

        Args:
            tasks (list): List of Task objects to schedule.
            current_schedule (list): Current partial schedule.
            time_slots (list): List of available time slots.
            memo (dict): Memoization cache to store previously computed states.

        Returns:
            bool: True if a valid schedule is found, False otherwise.

        Time Complexity:
            Best: O(T * S)
            Average: O(S^D), where D is the depth of the search tree (<= T).
            Worst: O(S^T)

        Space Complexity:
            Best: O(1)
            Average: O(D), for the recursion stack and memoization.
            Worst: O(S^T), due to memoization storage.
        """
        if not tasks:
            return True  # All tasks are successfully scheduled

        # Memoization: Avoid recomputing for the same state
        state = tuple((task.name, task.start_time) for task in tasks)
        if memo is None:
            memo = {}
        if state in memo:
            return memo[state]

        for task in tasks:
            for slot in time_slots:
                if self.can_fit(task, slot):
                    # Temporarily assign task to slot
                    self.assign_task_to_slot(task, slot)
                    remaining_tasks = [t for t in tasks if t != task]

                    # Recurse to schedule remaining tasks
                    if self.backtracking_schedule(remaining_tasks, current_schedule, time_slots, memo):
                        memo[state] = True
                        return True

                    # Backtrack: Unassign task from slot
                    self.unassign_task_from_slot(task, slot)

        # No valid schedule found for this state
        memo[state] = False
        return False

    def unassign_task_from_slot(self, task, slot):
        """
        Remove a task from a slot during backtracking.

        Args:
            task (Task): The task to unassign.
            slot (TimeSlot): The slot to free.

        Returns:
            None: Updates task and slot properties.

        Time Complexity:
            Best, Average, Worst: O(1)

        Space Complexity:
            Best, Average, Worst: O(1)
        """
        slot.is_occupied = False
        slot.task = None
        task.start_time = None
    

if __name__ == "__main__":
    # Sample tasks with priorities and dependencies
    tasks = [
        {'name': 'E1', 'priority': 4, 'dependencies': [], 'duration': 3, 'start_time': None},
        {'name': 'E2', 'priority': 2, 'dependencies': ['D3'], 'duration': 2, 'start_time': None},
        {'name': 'D1', 'priority': 8, 'dependencies': ['E1'], 'duration': 3, 'start_time': None},
        {'name': 'D2', 'priority': 9, 'dependencies': ['E2'], 'duration': 4, 'start_time': None},
        {'name': 'D3', 'priority': 3, 'dependencies': ['E1', 'D1'], 'duration': 2, 'start_time': None},
    ]

    # Sample time slots
    time_slots = [
        {'start_time': 0, 'end_time': 5, 'is_occupied': False, 'task': None},
        {'start_time': 6, 'end_time': 10, 'is_occupied': False, 'task': None},
        {'start_time': 11, 'end_time': 15, 'is_occupied': False, 'task': None},
        {'start_time': 16, 'end_time': 20, 'is_occupied': False, 'task': None},
    ]

    # Initialize SchedulingStrategy and run optimize_schedule
    scheduler = SchedulingStrategy()
    scheduler.optimize_schedule(tasks, time_slots)

    # Print results 
    print("\nFinal Schedule:")
    for task in scheduler.schedule:
        print(f"Task {task['name']} -> Start Time: {task['start_time']}, Priority: {task['priority']}")