# models/priority_manager.py

from collections import deque

class PriorityManager:
    def __init__(self, tasks):
        """
        Initialize the PriorityManager with a dictionary of tasks.
        
        :param tasks: Dictionary where keys are task identifiers (e.g., 'E1', 'D1') and 
                      values are dictionaries with task properties including 'priority' and 'dependencies'.
        
        Time Complexity: O(1) - Constant time initialization of the object.
        Space Complexity: O(n) - Storing 'n' tasks in the self.tasks dictionary.
        """
        self.tasks = tasks  # Store the dictionary of tasks and their properties in self.tasks for quick access

    def boost_priorities(self):
        """
        Boost priorities of tasks based on dependencies. If a higher-priority task depends on a
        lower-priority task, the lower-priority task gets its priority boosted to match the higher-priority task.

        Time Complexity: O(n + D) - Each task is iterated once (O(n)), and dependencies are recursively boosted.
                        D is the sum of dependencies, representing the worst-case recursion.
        Space Complexity: O(h) - Due to the recursive stack, where 'h' is the maximum depth of the dependency chain.
        """
        def recursive_boost(task_id, min_priority):
            # Boost the priority of the current task to at least `min_priority` to align with dependent task's priority
            if self.tasks[task_id]['priority'] < min_priority:
                self.tasks[task_id]['priority'] = min_priority
            
            # Recursively boost priority for each dependency of the current task to maintain consistency across dependencies
            for dep_id in self.tasks[task_id].get('dependencies', []):
                recursive_boost(dep_id, min_priority)  

        # Iterate through each task to check and boost priorities based on dependencies to ensure correct task order
        for task_id, properties in self.tasks.items():
            priority = properties['priority']  # Get the task's initial priority for comparison in recursive boosting
            # For each dependency, boost its priority based on the current task's priority to satisfy dependency requirements
            for dep_id in properties.get('dependencies', []):
                recursive_boost(dep_id, priority)  
        

    def quicksort_by_priority(self, tasks):
        """
        Sort tasks by priority using QuickSort.
        
        :param tasks: List of task identifiers sorted by priority.
        :return: List of sorted task identifiers.

        Time Complexity: O(n log n) average, O(n^2) worst case - QuickSort has an average n log n complexity,
                        but degrades to n^2 if pivot selection is poor.
        Space Complexity: O(log n) average, O(n) worst case - Space complexity due to recursive stack depth.
        """
        if len(tasks) <= 1:
            return tasks  # Base case: return the list if it's empty or has only one element (sorted)

        pivot = tasks[0]  # Choose the first task as the pivot for QuickSort partitioning
        pivot_priority = self.tasks[pivot]['priority']  # Get the pivot task's priority to compare with other tasks

        # Partition tasks into `left` and `right` based on pivot priority to structure for QuickSort
        left = [task for task in tasks[1:] if self.tasks[task]['priority'] > pivot_priority]
        right = [task for task in tasks[1:] if self.tasks[task]['priority'] <= pivot_priority]

        # Recursively sort the left and right partitions, and concatenate them with the pivot to complete QuickSort
        return self.quicksort_by_priority(left) + [pivot] + self.quicksort_by_priority(right)

    def custom_dependency_sort(self, tasks):
        """
        Sort tasks by resolving dependencies.
        
        :param tasks: List of task identifiers sorted by priority.
        :return: List of task identifiers sorted by dependency order.

        Time Complexity: O(n * D) - Each task is checked multiple times to resolve dependencies, leading to 
                        O(n * D) in the worst case for dense dependencies.
        Space Complexity: O(n) - Space for the sorted_tasks list and remaining_tasks set.
        """
    
        return sorted(tasks, key=lambda task: (-self.tasks[task]['priority'], len(self.tasks[task]['dependencies'])))

    def sort_tasks(self):
        """
        Boost priorities based on dependencies, then sort tasks first by priority and then by dependency.
        
        :return: List of task identifiers sorted by priority and dependencies.

        Time Complexity: O(n * D + n log n) - Calls boost_priorities (O(n + D)), quicksort_by_priority (O(n log n)),
                        and custom_dependency_sort (O(n * D)). In the worst case, complexity is O(n * D + n log n).
        Space Complexity: O(n) - Storing intermediate lists and results from each step.
        """

        # Step 1: Boost priorities based on dependencies 
        self.boost_priorities()
        
        # Step 2: Sort by priority
        task_ids = list(self.tasks.keys())
        priority_sorted = self.quicksort_by_priority(task_ids)
        
        # Step 3: Sort by dependencies within each priority level
        dependency_sorted = self.custom_dependency_sort(priority_sorted)

        # Convert the dependency-sorted list into a queue
        task_queue = deque(dependency_sorted[::-1]) # The Queue Logic note refers to this line
        
        return task_queue
        

#testing Priority Manager:
tasksSet1 = {
    'E1': {'priority': 9, 'dependencies': []},
    'E2': {'priority': 3, 'dependencies': ['E1']},
    'D1': {'priority': 2, 'dependencies': ['E1', 'E2']},
    'D2': {'priority': 8, 'dependencies': ['E2']},
}
# Expected Output: [D1,D2,E2,E1]

tasksSet2 = {
    'E1': {'priority': 10, 'dependencies': []},
    'E2': {'priority': 9, 'dependencies': []},
    'D1': {'priority': 8, 'dependencies': []},
    'D2': {'priority': 1, 'dependencies': []},
}
# Expected Output: [D2,D1,E2,E1]

tasksSet3 = {
    'E1': {'priority': 1, 'dependencies': []},
    'E2': {'priority': 2, 'dependencies': []},
    'D1': {'priority': 3, 'dependencies': ['E1']},
    'D2': {'priority': 4, 'dependencies': []},
}
# Expected Output: [E2,D1,E1,D2]

tasksSet4 = {
    'E1': {'priority': 4, 'dependencies': []},
    'E2': {'priority': 2, 'dependencies': ['D3']},
    'D1': {'priority': 8, 'dependencies': ['E1']},
    'D2': {'priority': 9, 'dependencies': ['E2']},
    'D3': {'priority': 3, 'dependencies': ['E1', 'D1','E1']},
}
# Expected Output: [D3,D2,D1,E2,E1] - order of the 3 in the middle do not matter 

# pm = PriorityManager(tasksSet1)
# pm.boost_priorities()
# for task_id, properties in pm.tasks.items():
#     print(f"Task {task_id} : Priority {properties['priority']}")
# Results: boost_priorities() function works as expected

# task_ids = list(pm.tasks.keys())
# l1 = pm.quicksort_by_priority(task_ids)
#print(l1)
# Results: quicksort_by_priority() function works as expected


# Notes:
# At a glance, it looks functional; however, further testing is necessary to be certain. 
# Queue Logic might not be properly setup/implemented

# Code Does NOT:
# Current implemention does NOT allow for Task data to come from another component which is expected. (10/30/2024), (11/2/2024)
