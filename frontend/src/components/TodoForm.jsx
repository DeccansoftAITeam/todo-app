import { useState } from 'react'

const CATEGORIES = ['work', 'personal', 'shopping', 'other']

export default function TodoForm({ onCreate }) {
  const [title, setTitle] = useState('')
  const [dueDate, setDueDate] = useState('')
  const [category, setCategory] = useState('other')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    const trimmed = title.trim()
    if (!trimmed) {
      setError('Title is required.')
      return
    }
    if (trimmed.length > 200) {
      setError('Title must be 200 characters or fewer.')
      return
    }
    setError('')
    setBusy(true)
    try {
      await onCreate({
        title: trimmed,
        due_date: dueDate || null,
        category,
      })
      setTitle('')
      setDueDate('')
      setCategory('other')
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <form className="todo-form" onSubmit={handleSubmit} noValidate>
      <div className="field grow">
        <label htmlFor="title">Title</label>
        <input
          id="title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="What needs doing?"
          aria-invalid={error ? 'true' : undefined}
          aria-describedby={error ? 'form-error' : undefined}
        />
      </div>
      <div className="field">
        <label htmlFor="due">Due date</label>
        <input id="due" type="date" value={dueDate} onChange={(e) => setDueDate(e.target.value)} />
      </div>
      <div className="field">
        <label htmlFor="category">Category</label>
        <select id="category" value={category} onChange={(e) => setCategory(e.target.value)}>
          {CATEGORIES.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </div>
      <button type="submit" className="primary" disabled={busy}>
        Add
      </button>
      {error && (
        <p id="form-error" className="error" role="alert">
          {error}
        </p>
      )}
    </form>
  )
}
