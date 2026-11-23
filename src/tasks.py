"""The tasks: each its number, its words and whether it is done, in the
order they were added; which a filter shows, how many are left, and the
form the storage keeps them in."""

from __future__ import annotations

import json
from dataclasses import dataclass

#: The filters, as the chips name them: every task, those to do, those done.
FILTERS = ("all", "active", "done")
#: The longest a task's words may be: a line, not a document.
LONGEST = 200


@dataclass
class Task:
    number: int
    words: str
    done: bool = False


class Tasks:
    """The tasks, in the order they were added, and the number the next one
    takes."""

    def __init__(self, tasks: list[Task] | None = None, next_number: int = 1) -> None:
        self.tasks = tasks or []
        self.next_number = max([next_number, *(task.number + 1 for task in self.tasks)])

    def add(self, words: str) -> Task | None:
        """A task of `words`, at the end; none for words that are only space."""
        words = " ".join(words.split())[:LONGEST]
        if not words:
            return None
        task = Task(self.next_number, words)
        self.next_number += 1
        self.tasks.append(task)
        return task

    def find(self, number: int) -> Task | None:
        return next((task for task in self.tasks if task.number == number), None)

    def toggle(self, number: int) -> None:
        """The task `number` done, or to do again."""
        task = self.find(number)
        if task:
            task.done = not task.done

    def remove(self, number: int) -> tuple[int, Task] | None:
        """The task `number` taken away: where it was, and it, to put back."""
        for place, task in enumerate(self.tasks):
            if task.number == number:
                return place, self.tasks.pop(place)
        return None

    def put_back(self, place: int, task: Task) -> None:
        """A task taken away put back where it was."""
        self.tasks.insert(min(place, len(self.tasks)), task)

    def clear_done(self) -> list[tuple[int, Task]]:
        """The tasks done taken away, each with where it was."""
        gone = [(place, task) for place, task in enumerate(self.tasks) if task.done]
        self.tasks = [task for task in self.tasks if not task.done]
        return gone

    def shown(self, which: str) -> list[Task]:
        """The tasks the filter `which` shows."""
        if which == "active":
            return [task for task in self.tasks if not task.done]
        if which == "done":
            return [task for task in self.tasks if task.done]
        return list(self.tasks)

    def left(self) -> int:
        """How many are still to do."""
        return sum(not task.done for task in self.tasks)

    def done(self) -> int:
        return len(self.tasks) - self.left()

    def encode(self) -> str:
        """The tasks as the storage keeps them: JSON."""
        listed = [{"n": task.number, "w": task.words, "d": task.done} for task in self.tasks]
        return json.dumps({"next": self.next_number, "tasks": listed}, ensure_ascii=False)

    @classmethod
    def decode(cls, text: str | None) -> Tasks:
        """The tasks the storage kept as `text`; none when it kept nothing,
        or what it kept cannot be read."""
        try:
            kept = json.loads(text or "{}")
            tasks = [Task(int(t["n"]), str(t["w"]), bool(t["d"])) for t in kept.get("tasks", [])]
            return cls(tasks, int(kept.get("next", 1)))
        except (ValueError, TypeError, KeyError, AttributeError):
            return cls()
