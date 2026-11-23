todo-title = Todo
todo-new = Add a task
todo-all = All
todo-active = To do
todo-done = Done
todo-left = { $count ->
    [0] Nothing left to do
    [one] One task to do
   *[other] { $count } tasks to do
}
todo-empty = No tasks yet
todo-empty-hint = Type one above and press Enter.
todo-nothing-active = Nothing to do
todo-nothing-active-hint = Every task is done.
todo-nothing-done = Nothing done yet
todo-nothing-done-hint = Tap a task once it is done.
todo-clear = Clear done
todo-deleted = Task deleted
todo-cleared = { $count ->
    [one] One task deleted
   *[other] { $count } tasks deleted
}
todo-undo = Undo
todo-not-kept = The storage is full: the tasks were not kept.
todo-mark-done = Mark done
todo-mark-undone = Mark not done
todo-delete = Delete
