# tests/test_priority_manager.py

from Models.task import Task  # Assuming Task is a base class for your tasks
from datetime import timedelta

# Define dummy tasks with various priority levels and dependencies
class DummyTask(Task):
    def __init__(self, name, priority, dependencies=None):
        super().__init__(name, timedelta(hours=1), priority=priority)
        self.dependencies = dependencies if dependencies else []

# Example tasks
task1 = DummyTask("Task 1", priority=8, dependencies=[])
task2 = DummyTask("Task 2", priority=9, dependencies=[task1])
task3 = DummyTask("Task 3", priority=10, dependencies=[])
task4 = DummyTask("Task 4", priority=7, dependencies=[task1, task2])

# Initialize PriorityManager and test functionality
def test_priority_manager():
    priority_manager = PriorityManager()
    priority_manager.add_task(task1)
    priority_manager.add_task(task2)
    priority_manager.add_task(task3)
    priority_manager.add_task(task4)

    priority_manager.sort_by_priority_and_dependencies()
    sorted_queue = priority_manager.export_queue()

    for task in sorted_queue:
        print(f"{task.name} - Priority: {task.priority}, Dependencies: {len(task.dependencies)}")

# Run the test
if __name__ == "__main__":
    test_priority_manager()