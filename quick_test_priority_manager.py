from Optimizers.priority_manager import PriorityManager

# Sample test data
tasks = [
    {"id": 1, "priority": 10, "dependencies": []},
    {"id": 2, "priority": 5, "dependencies": [1]},
    {"id": 3, "priority": 8, "dependencies": [1, 2]}
]

# Initialize PriorityManager with test data
priority_manager = PriorityManager(tasks)

# Run your sorting function or other main function
sorted_tasks = priority_manager.sort_tasks()

# Print results for verification
print("Sorted Tasks:", sorted_tasks)