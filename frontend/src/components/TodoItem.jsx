export default function TodoItem({ todo, onToggleComplete, onToggleArchive }) {
  const classes = ['todo-item']
  if (todo.completed) classes.push('completed')
  if (todo.archived) classes.push('archived')

  return (
    <li className={classes.join(' ')}>
      <label className="check">
        <input
          type="checkbox"
          checked={todo.completed}
          onChange={() => onToggleComplete(todo)}
          aria-label={`${todo.completed ? 'Mark incomplete' : 'Mark complete'}: ${todo.title}`}
        />
      </label>
      <div className="body">
        <span className="title">{todo.title}</span>
        <span className="meta">
          <span className="status">{todo.completed ? 'Completed' : 'Open'}</span>
          {todo.due_date && <span>Due {todo.due_date}</span>}
          <span className="tag">{todo.category}</span>
          <span className={`tag priority-${todo.priority}`}>{todo.priority}</span>
          {todo.archived && <span className="tag archived-tag">Archived</span>}
        </span>
      </div>
      <button type="button" onClick={() => onToggleArchive(todo)}>
        {todo.archived ? 'Restore' : 'Archive'}
      </button>
    </li>
  )
}
