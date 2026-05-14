export const emptyCandidateForm = {
  name: '',
  email: '',
  role_applied: '',
  skills: [],
  internal_notes: '',
}

export default function CandidateCreateForm({ form, options, onChange, onSubmit }) {
  function toggleSkill(skill) {
    const skills = form.skills.includes(skill)
      ? form.skills.filter((item) => item !== skill)
      : [...form.skills, skill]
    onChange({ ...form, skills })
  }

  return (
    <form className="space-y-3" onSubmit={onSubmit}>
      {[
        ['name', 'Name'],
        ['email', 'Email'],
      ].map(([field, label]) => (
        <input
          key={field}
          className="w-full border border-slate-300 px-3 py-2 text-sm"
          placeholder={label}
          value={form[field]}
          onChange={(event) => onChange({ ...form, [field]: event.target.value })}
          required
        />
      ))}

      <select
        className="w-full border border-slate-300 px-3 py-2 text-sm"
        value={form.role_applied}
        onChange={(event) => onChange({ ...form, role_applied: event.target.value })}
        required
      >
        <option value="">Select role</option>
        {options.roles.map((role) => (
          <option key={role} value={role}>
            {role}
          </option>
        ))}
      </select>

      <div>
        <p className="mb-2 text-sm font-medium">Skills</p>
        <div className="grid max-h-44 grid-cols-2 gap-2 overflow-auto border border-slate-200 p-3">
          {options.skills.map((skill) => (
            <label key={skill} className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={form.skills.includes(skill)}
                onChange={() => toggleSkill(skill)}
              />
              {skill}
            </label>
          ))}
        </div>
      </div>

      <textarea
        className="min-h-24 w-full border border-slate-300 px-3 py-2 text-sm"
        placeholder="Internal notes"
        value={form.internal_notes}
        onChange={(event) => onChange({ ...form, internal_notes: event.target.value })}
      />
      <button className="w-full bg-slate-950 px-3 py-2 text-sm font-medium text-white">
        Create candidate
      </button>
    </form>
  )
}
