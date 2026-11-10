export default function Filters({
  view,
  onViewChange,
  query,
  onQueryChange,
  showArchived,
  onShowArchivedChange,
}) {
  return (
    <div className="filters">
      <div className="tabs" role="group" aria-label="View">
        <button
          type="button"
          className={view === 'all' ? 'active' : ''}
          aria-pressed={view === 'all'}
          onClick={() => onViewChange('all')}
        >
          All
        </button>
        <button
          type="button"
          className={view === 'overdue' ? 'active' : ''}
          aria-pressed={view === 'overdue'}
          onClick={() => onViewChange('overdue')}
        >
          Overdue
        </button>
      </div>
      <input
        type="search"
        value={query}
        onChange={(e) => onQueryChange(e.target.value)}
        placeholder="Search titles"
        aria-label="Search by title"
      />
      <label className="archived-toggle">
        <input
          type="checkbox"
          checked={showArchived}
          disabled={view === 'overdue'}
          onChange={(e) => onShowArchivedChange(e.target.checked)}
        />
        Show archived
      </label>
    </div>
  )
}
