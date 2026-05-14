const tones = {
  status: {
    new: 'bg-sky-50 text-sky-700 ring-sky-200',
    reviewed: 'bg-amber-50 text-amber-700 ring-amber-200',
    hired: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
    rejected: 'bg-rose-50 text-rose-700 ring-rose-200',
    archived: 'bg-slate-100 text-slate-600 ring-slate-200',
  },
  role: 'bg-indigo-50 text-indigo-700 ring-indigo-200',
  skill: 'bg-teal-50 text-teal-700 ring-teal-200',
}

export default function Badge({ type = 'skill', value }) {
  const color =
    type === 'status'
      ? tones.status[value] || tones.status.new
      : tones[type] || tones.skill

  return (
    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ring-1 ${color}`}>
      {String(value).replace('_', ' ')}
    </span>
  )
}
