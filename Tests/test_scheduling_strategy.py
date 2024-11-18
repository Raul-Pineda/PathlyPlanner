# test_scheduling_strategy.py

import unittest
from Optimizers.priority_manager import PriorityManager
from Optimizers.scheduling_strategy import SchedulingStrategy

class TestSchedulingStrategy(unittest.TestCase):

    def test_optimize_schedule(self):
        """
        Test the optimize_schedule method of SchedulingStrategy with a predefined task set and time slots.
        """
        # Define tasks
        tasks = {
            'E1': {'priority': 4, 'dependencies': []},
            'E2': {'priority': 2, 'dependencies': ['D3']},
            'D1': {'priority': 8, 'dependencies': ['E1']},
            'D2': {'priority': 9, 'dependencies': ['E2']},
            'D3': {'priority': 3, 'dependencies': ['E1', 'D1']},
        }

        # Define time slots
        time_slots = [
            {'start_time': 0, 'end_time': 5, 'is_occupied': False, 'task': None},
            {'start_time': 6, 'end_time': 10, 'is_occupied': False, 'task': None},
            {'start_time': 11, 'end_time': 15, 'is_occupied': False, 'task': None},
        ]

        # Initialize PriorityManager and get sorted tasks
        pm = PriorityManager(tasks)
        sorted_tasks = pm.sort_tasks()

        # Initialize SchedulingStrategy and optimize schedule
        ss = SchedulingStrategy()
        final_schedule = ss.optimize_schedule(tasks, time_slots)

        # Validate the final schedule
        self.assertEqual(len(final_schedule), 3)
        self.assertTrue(all(task['start_time'] is not None for task in final_schedule))
        self.assertTrue(final_schedule[0]['priority'] >= final_schedule[1]['priority'])

if __name__ == "__main__":
    unittest.main()