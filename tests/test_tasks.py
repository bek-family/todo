"""The tasks' own rules, on this computer's Python: python3 tests/test_tasks.py"""

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from tasks import Tasks  # noqa: E402


class TasksTest(unittest.TestCase):
    def test_a_task_is_added_at_the_end_its_spaces_tidied(self):
        tasks = Tasks()
        tasks.add("Buy milk")
        added = tasks.add("  Call   mom ")
        self.assertEqual(added.words, "Call mom")
        self.assertEqual([task.words for task in tasks.tasks], ["Buy milk", "Call mom"])
        self.assertIsNone(tasks.add("   "), "space alone is no task")

    def test_filters_show_what_is_to_do_or_done(self):
        tasks = Tasks()
        milk, mom = tasks.add("Buy milk"), tasks.add("Call mom")
        tasks.toggle(milk.number)
        self.assertEqual(tasks.shown("active"), [mom])
        self.assertEqual(tasks.shown("done"), [milk])
        self.assertEqual(len(tasks.shown("all")), 2)
        self.assertEqual((tasks.left(), tasks.done()), (1, 1))

    def test_a_task_taken_away_goes_back_where_it_was(self):
        tasks = Tasks()
        for words in ("a", "b", "c"):
            tasks.add(words)
        place, task = tasks.remove(2)
        self.assertEqual((place, task.words), (1, "b"))
        tasks.put_back(place, task)
        self.assertEqual([task.words for task in tasks.tasks], ["a", "b", "c"])

    def test_clear_done_takes_the_done_ones_away(self):
        tasks = Tasks()
        for words in ("a", "b", "c"):
            tasks.add(words)
        tasks.toggle(1)
        tasks.toggle(3)
        gone = tasks.clear_done()
        self.assertEqual([place for place, _ in gone], [0, 2])
        self.assertEqual([task.words for task in tasks.tasks], ["b"])

    def test_the_tasks_are_kept_and_read_back(self):
        tasks = Tasks()
        tasks.add("Нон олиш")
        tasks.toggle(tasks.add("Call mom").number)
        again = Tasks.decode(tasks.encode())
        self.assertEqual(again.tasks, tasks.tasks)
        self.assertEqual(again.add("next").number, 3, "numbers go on")

    def test_what_cannot_be_read_is_no_tasks(self):
        for kept in (None, "", "not json", '{"tasks": [{"n": "x"}]}', "[1]"):
            self.assertEqual(Tasks.decode(kept).tasks, [], kept)


if __name__ == "__main__":
    unittest.main()
