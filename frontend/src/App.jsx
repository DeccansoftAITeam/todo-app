import { useCallback, useEffect, useState } from 'react'
import { createTodo, deleteTodo, listOverdue, listTodos, updateTodo } from './api.js'
import { downloadTodosCsv } from './csv.js'
import Filters from './components/Filters.jsx'
import TodoForm from './components/TodoForm.jsx'
import TodoList from './components/TodoList.jsx'
import './App.css'

export default function App() {
  const [view, setView] = useState('all') // 'all' | 'overdue'
  const [query, setQuery] = useState('')
  const [showArchived, setShowArchived] = useState(false)
  const [todos, setTodos] = useState([])
  const [error, setError] = useState('')
  const [theme, setTheme] = useState(() => {
    const t = document.documentElement.dataset.theme
    if (t) return t
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  })
  const [reloadKey, setReloadKey] = useState(0)

  function toggleTheme() {
    const next = theme === 'dark' ? 'light' : 'dark'
    setTheme(next)
    document.documentElement.dataset.theme = next
    try {
      localStorage.setItem('theme', next)
    } catch {
      /* storage unavailable */
    }
  }

  const reload = useCallback(() => setReloadKey((k) => k + 1), [])

  useEffect(() => {
    let ignore = false // drop stale responses when filters change quickly
    const request =
      view === 'overdue'
        ? listOverdue({ q: query })
        : listTodos({ q: query, includeArchived: showArchived })
    request
      .then((data) => {
        if (ignore) return
        setTodos(data)
        setError('')
      })
      .catch((err) => {
        if (!ignore) setError(err.message)
      })
    return () => {
      ignore = true
    }
  }, [view, query, showArchived, reloadKey])

  async function handleCreate(todo) {
    await createTodo(todo)
    reload()
  }

  async function mutate(id, changes) {
    try {
      await updateTodo(id, changes)
      reload()
    } catch (err) {
      setError(err.message)
    }
  }

  async function handleDelete(todo) {
    if (!window.confirm(`Permanently delete "${todo.title}"?`)) return
    try {
      await deleteTodo(todo.id)
      reload()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <main className="app">
      <div className="app-header">
        <h1>To-Do</h1>
        <button
          type="button"
          className="theme-toggle"
          onClick={toggleTheme}
          aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
          title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {theme === 'dark' ? (
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" /></svg>
          ) : (
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" /></svg>
          )}
        </button>
      </div>
      <TodoForm onCreate={handleCreate} />
      <Filters
        view={view}
        onViewChange={setView}
        query={query}
        onQueryChange={setQuery}
        showArchived={showArchived}
        onShowArchivedChange={setShowArchived}
        onExport={() => downloadTodosCsv(todos)}
        exportDisabled={!todos.some((t) => !t.archived)}
      />
      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}
      <TodoList
        todos={todos}
        view={view}
        searching={query.trim() !== ''}
        onToggleComplete={(t) => mutate(t.id, { completed: !t.completed })}
        onToggleArchive={(t) => mutate(t.id, { archived: !t.archived })}
        onDelete={handleDelete}
      />
    </main>
  )
}
