export default function CandidateFilters({
  filters,
  options,
  onChange,
  onApply,
  onClear,
}) {
  return (
    <section className="border border-slate-200 bg-white p-4">
      <div className="grid gap-3 md:grid-cols-4">
        <select
          className="border border-slate-300 px-3 py-2 text-sm"
          value={filters.status}
          onChange={(event) => onChange({ ...filters, status: event.target.value })}
        >
          <option value="">All statuses</option>
          <option value="new">New</option>
          <option value="reviewed">Reviewed</option>
          <option value="hired">Hired</option>
          <option value="rejected">Rejected</option>
          <option value="archived">Archived</option>
        </select>
        <select
          className="border border-slate-300 px-3 py-2 text-sm"
          value={filters.role_applied}
          onChange={(event) =>
            onChange({ ...filters, role_applied: event.target.value })
          }
        >
          <option value="">All roles</option>
          {options.roles.map((role) => (
            <option key={role} value={role}>
              {role}
            </option>
          ))}
        </select>
        <select
          className="border border-slate-300 px-3 py-2 text-sm"
          value={filters.skill}
          onChange={(event) => onChange({ ...filters, skill: event.target.value })}
        >
          <option value="">All skills</option>
          {options.skills.map((skill) => (
            <option key={skill} value={skill}>
              {skill}
            </option>
          ))}
        </select>
        <FilterInput
          placeholder="Keyword"
          value={filters.keyword}
          onChange={(keyword) => onChange({ ...filters, keyword })}
        />
      </div>
      <div className="mt-3 flex flex-wrap gap-2">
        <button
          className="bg-teal-700 px-4 py-2 text-sm font-medium text-white"
          onClick={onApply}
        >
          Apply filters
        </button>
        <button
          className="border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700"
          onClick={onClear}
        >
          Clear filters
        </button>
      </div>
    </section>
  )
}

function FilterInput({ placeholder, value, onChange }) {
  return (
    <input
      className="border border-slate-300 px-3 py-2 text-sm"
      placeholder={placeholder}
      value={value}
      onChange={(event) => onChange(event.target.value)}
    />
  )
}
