"""Todo, a Bek OS app written in Python: tasks added from a field, ticked
off, filtered (all, to do, done) and deleted (a cross, a swipe, or Clear
done), Undo putting back what went, for four seconds; kept in the app's
storage. componentize-py makes it a component of the phone's world, CPython
in it; the phone gives it its page (`dom`), its words (`words`) and its
storage (`host-api`)."""

from __future__ import annotations

import wit_world
from wit_world.imports import dom, host_api, resources

import store
from page import Page
from tasks import Task
from words import t, translate

#: How long the snackbar offers Undo, in milliseconds.
NOTICE_MS = 4000


class Todo:
    """The app's state between updates: its tasks, the filter chosen, and
    what Undo would put back, until when."""

    def __init__(self) -> None:
        self.root = dom.root()
        dom.add_stylesheet(resources.get("ui/style.css") or "")
        dom.set_markup(self.root, resources.get("ui/main.html") or "")
        translate(self.root)
        self.locale = host_api.locale()
        self.page = Page(self.root)
        self.tasks = store.load()
        self.which = "all"
        self.gone: list[tuple[int, Task]] = []
        self.notice_until = 0
        self.page.show(self.tasks, self.which)

    def update(self) -> None:
        """What the person did, done; the snackbar gone once its time is up;
        the words put in again when the phone's language changed."""
        events = dom.events()
        for event in events:
            self.answer(event)
        if self.notice_until and host_api.now_millis() >= self.notice_until:
            self.forget()
        language_changed = host_api.locale() != self.locale
        if language_changed:
            self.locale = host_api.locale()
            translate(self.root)
        if events or language_changed:
            self.page.show(self.tasks, self.which)

    def answer(self, event: dom.Event) -> None:
        page, at = self.page, event.current
        if event.kind == "submit" and at == page.field:
            if self.tasks.add(event.value):
                dom.set_attribute(page.field, "value", "")
                self.keep()
        elif event.kind == "swipe" and at in page.rows.toggles:
            self.delete(page.rows.toggles[at])
        elif event.kind != "click":
            return
        elif at in page.rows.removes:
            self.delete(page.rows.removes[at])
        elif at in page.rows.toggles:
            self.tasks.toggle(page.rows.toggles[at])
            self.keep()
        elif at == page.clear:
            self.offer_back(self.tasks.clear_done())
        elif at == page.undo:
            self.put_back()
        else:
            self.which = next((name for name, chip in page.filters.items() if chip == at),
                              self.which)

    def delete(self, number: int) -> None:
        gone = self.tasks.remove(number)
        if gone:
            self.offer_back([gone])

    def offer_back(self, gone: list[tuple[int, Task]]) -> None:
        """`gone` taken away, the snackbar saying so and offering Undo."""
        if not gone:
            return
        self.keep()
        self.gone = gone
        words = t("todo-deleted") if len(gone) == 1 else t("todo-cleared", count=len(gone))
        self.page.say(words)
        self.notice_until = host_api.now_millis() + NOTICE_MS
        host_api.request_frame(NOTICE_MS)

    def put_back(self) -> None:
        for place, task in sorted(self.gone, key=lambda gone: gone[0]):
            self.tasks.put_back(place, task)
        self.keep()
        self.forget()

    def forget(self) -> None:
        """The snackbar gone, and what it offered back."""
        self.gone, self.notice_until = [], 0
        self.page.say(None)

    def keep(self) -> None:
        if not store.save(self.tasks):
            self.page.say(t("todo-not-kept"))


APP: Todo | None = None


class WitWorld(wit_world.WitWorld):
    """The world's exports, which componentize-py finds by this name."""

    def init(self) -> None:
        global APP
        APP = Todo()

    def update(self) -> None:
        if APP is not None:
            APP.update()
