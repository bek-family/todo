"""The page: its parts, found once in its markup (`ui/main.html`), and the
tasks shown on it, a row each, made again as they change. A row's check and
words tick it off; its cross, or a swipe either way, deletes it."""

from __future__ import annotations

from dataclasses import dataclass, field

from wit_world.imports import dom

from tasks import FILTERS, Task, Tasks
from words import t

#: Each filter's words when it shows nothing: what it is, and what to do.
EMPTY = {
    "all": ("todo-empty", "todo-empty-hint"),
    "active": ("todo-nothing-active", "todo-nothing-active-hint"),
    "done": ("todo-nothing-done", "todo-nothing-done-hint"),
}


def one(scope: int, selector: str) -> int:
    """The element `selector` names under `scope`."""
    found = dom.query_all(scope, selector)
    if not found:
        raise LookupError(f"ui/main.html has no {selector}")
    return found[0]


def element(tag: str, classes: tuple[str, ...] = (), words: str | None = None) -> int:
    """A new element of `tag`, of `classes`, saying `words`."""
    made = dom.create_element(tag)
    for name in classes:
        dom.toggle_class(made, name, True)
    if words is not None:
        dom.set_text(made, words)
    return made


@dataclass
class Rows:
    """The rows shown, by what each part of them does to which task."""

    toggles: dict[int, int] = field(default_factory=dict)
    removes: dict[int, int] = field(default_factory=dict)


class Page:
    """The page's parts, and the rows it shows now."""

    def __init__(self, root: int) -> None:
        self.field = one(root, "#new")
        self.filters = {dom.get_attribute(chip, "data-filter"): chip
                        for chip in dom.query_all(root, "x-chip")}
        self.count = one(root, "#count")
        self.list = one(root, "#list")
        self.empty = one(root, "#empty")
        self.empty_title = one(root, "#empty-title")
        self.empty_hint = one(root, "#empty-hint")
        self.clear = one(root, "#clear")
        self.notice = one(root, "#notice")
        self.notice_words = one(root, "#notice-words")
        self.undo = one(root, "#undo")
        self.rows = Rows()
        dom.listen(self.field, "submit")
        for control in [*self.filters.values(), self.clear, self.undo]:
            dom.listen(control, "click")

    def show(self, tasks: Tasks, which: str) -> None:
        """`tasks` as the filter `which` shows them, and what is said of them."""
        for row in dom.children(self.list):
            dom.release(row)
        self.rows = Rows()
        shown = tasks.shown(which)
        for task in shown:
            dom.append_child(self.list, self.row(task))
        for name in FILTERS:
            dom.toggle_class(self.filters[name], "selected", name == which)
        dom.set_text(self.count, t("todo-left", count=tasks.left()))
        self.hide(self.count, not tasks.tasks)
        self.hide(self.list, not shown)
        self.hide(self.empty, bool(shown))
        title, hint = EMPTY[which]
        dom.set_text(self.empty_title, t(title))
        dom.set_text(self.empty_hint, t(hint))
        self.hide(self.clear, tasks.done() == 0)

    def row(self, task: Task) -> int:
        """A task's row: its check, its words, and its cross."""
        row = element("x-row", ("task", "done") if task.done else ("task",))
        check = element("x-icon", ("check",), "check_circle" if task.done else
                        "radio_button_unchecked")
        mark = "todo-mark-undone" if task.done else "todo-mark-done"
        dom.set_attribute(check, "aria-label", t(mark))
        text = element("x-text")
        dom.append_child(text, element("b", (), task.words))
        remove = element("x-icon", ("remove",), "close")
        dom.set_attribute(remove, "aria-label", t("todo-delete"))
        for part in (check, text, remove):
            dom.append_child(row, part)
        for kind in ("click", "swipe"):
            dom.listen(row, kind)
        dom.listen(remove, "click")
        self.rows.toggles[row] = task.number
        self.rows.removes[remove] = task.number
        return row

    def say(self, words: str | None) -> None:
        """The snackbar saying `words`, with Undo; or gone, for none."""
        self.hide(self.notice, words is None)
        if words is not None:
            dom.set_text(self.notice_words, words)

    @staticmethod
    def hide(item: int, hidden: bool) -> None:
        if hidden:
            dom.set_attribute(item, "hidden", "")
        else:
            dom.remove_attribute(item, "hidden")
