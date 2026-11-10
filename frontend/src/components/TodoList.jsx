import TodoItem from './TodoItem.jsx'

export default function TodoList({
  todos,
  view,
  searching,
  onToggleComplete,
  onToggleArchive,
}) {
  if (todos.length === 0) {
    let message = 'No to-dos yet. Add one above.'
    if (searching) message = 'No to-dos match your search.'
    else if (view === 'overdue') message = 'Nothing is overdue.'
    return <p className="empty">{message}</p>
  }
  return (
    <ul className="todo-list">
      {todos.map((todo) => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onToggleComplete={onToggleComplete}
          onToggleArchive={onToggleArchive}
        />
      ))}
    </ul>
  )
}
