// Fetch wrapper for /api/todos.

async function request(path, options) {
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    let message = `Request failed (${res.status})`
    try {
      const body = await res.json()
      if (typeof body.detail === 'string') message = body.detail
      else if (res.status === 422) message = 'Please check your input and try again.'
    } catch {
      // non-JSON error body; keep the generic message
    }
    throw new Error(message)
  }
  return res.json()
}

function withQuery(path, params) {
  const search = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value !== '' && value !== false && value != null) search.set(key, value)
  }
  const qs = search.toString()
  return qs ? `${path}?${qs}` : path
}

export function listTodos({ q = '', includeArchived = false } = {}) {
  return request(withQuery('/api/todos', { q, include_archived: includeArchived }))
}

export function listOverdue({ q = '' } = {}) {
  return request(withQuery('/api/todos/overdue', { q }))
}

export function createTodo(todo) {
  return request('/api/todos', { method: 'POST', body: JSON.stringify(todo) })
}

export function updateTodo(id, changes) {
  return request(`/api/todos/${id}`, { method: 'PATCH', body: JSON.stringify(changes) })
}
