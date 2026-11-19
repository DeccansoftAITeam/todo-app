// CSV export built from todos already loaded in the UI (no backend call).

const COLUMNS = ['id', 'title', 'due_date', 'category', 'completed', 'archived', 'created_at']
const BOM = '﻿' // lets Excel detect UTF-8 for non-ASCII titles

// Prefix cells that a spreadsheet would treat as a formula (CSV injection).
function guardFormula(value) {
  return /^[=+\-@\t\r]/.test(value) ? `'${value}` : value
}

function escapeCell(value) {
  const s = String(value)
  return /[",\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s
}

function cellValue(todo, column) {
  const value = todo[column]
  if (column === 'due_date') return value || '-'
  if (column === 'completed' || column === 'archived') return value ? 'true' : 'false'
  if (column === 'title') return guardFormula(value ?? '')
  return value ?? ''
}

// Only active (non-archived) todos are exported.
export function todosToCsv(todos) {
  const rows = todos
    .filter((t) => !t.archived)
    .map((t) => COLUMNS.map((c) => escapeCell(cellValue(t, c))).join(','))
  return [COLUMNS.join(','), ...rows].join('\r\n') + '\r\n'
}

export function downloadTodosCsv(todos) {
  const blob = new Blob([BOM, todosToCsv(todos)], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `todos-${new Date().toISOString().slice(0, 10)}.csv`
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}
