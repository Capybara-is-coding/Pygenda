import unittest 
import pygenda
import tkinter as tk
from tkinter import messagebox
from unittest.mock import patch

class TestApp(unittest.TestCase):
    def setUp(self):
        '''Set up an app before each test.'''
        global tasks
        self.root = tk.Tk()
        pygenda.tasks.clear()
        pygenda.task_entry = tk.Entry(self.root)  
        pygenda.tasks_frame = tk.Frame(self.root) 

    def tearDown(self):
        '''Destroy the root window after each test.'''
        self.root.destroy()

    def test_adding(self):
        '''Test if tasks are added to the task list and if they are unchecked by default.'''
        task_text = 'test'
        pygenda.task_entry.insert(0, task_text)
        pygenda.add_task()
        self.assertEqual(pygenda.tasks[0][0], task_text, 'Task is not added to the list.')
        self.assertFalse(pygenda.tasks[0][1].get(), 'Task is marked completed by default.')

    def test_adding_empty(self):
        '''Test that empty tasks are not added to the task list.'''
        initial_tasks = len(pygenda.tasks)
        task_text = ''
        pygenda.task_entry.insert(0, task_text)
        pygenda.add_task()
        self.assertEqual(len(pygenda.tasks), initial_tasks, 'An empty task was added to the list.')
        
    def test_warning(self): 
        '''Test that the warning is shown when trying to add an empty task.'''
        task_text = ''
        pygenda.task_entry.insert(0, task_text)
        with patch.object(messagebox, 'showwarning') as mock_warning:  
            pygenda.add_task()
            mock_warning.assert_called_once_with('Warning', 'Task cannot be empty!')

    def test_removing(self):
        '''Test if the task is removed from the task list.'''
        task_text = 'test'
        pygenda.task_entry.insert(0, task_text)
        pygenda.add_task()
        task_check = pygenda.tasks[0][2]
        remove_btn = pygenda.tasks[0][3]
        pygenda.remove_task(task_text, task_check, remove_btn)
        self.assertEqual(len(pygenda.tasks), 0, 'Task was not removed from the task list.')

    def test_completion(self):
        '''Test marking a task as complete.'''
        task_text = 'test'
        pygenda.task_entry.insert(0, task_text)
        pygenda.add_task()
        task_var = pygenda.tasks[0][1]
        task_check = pygenda.tasks[0][2]
        task_check.invoke()
        self.assertTrue(task_var.get(), 'Task was not marked as completed.')

    def test_remove_completed(self):
        '''Test removing of all tasks that were marked completed.'''
        task_done = 'done'
        task_todo = 'not done'
        task_todo2 = 'not done'
        pygenda.task_entry.insert(0, task_done)
        pygenda.add_task()    
        pygenda.tasks[0][1].set(True)
        pygenda.task_entry.insert(0, task_todo)
        pygenda.add_task()
        pygenda.task_entry.insert(0, task_todo2)
        pygenda.add_task()
        pygenda.remove_completed_tasks()
        self.assertEqual(len(pygenda.tasks), 2, 'Number of task in the list is not correct.')
        self.assertEqual(pygenda.tasks[0][0], task_todo)
        self.assertEqual(pygenda.tasks[1][0], task_todo2)
