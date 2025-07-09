const filters = [
  { label: 'All', value: 'all' },
  { label: 'People', value: 'people' },
  { label: 'Nature', value: 'nature' },
  { label: 'Food', value: 'food' },
  { label: 'Sport', value: 'sport' },
  { label: 'Other', value: 'other' },
]

export default function CommunitySortBar({ selected, onSelect }: { selected: string, onSelect: (v: string) => void }) {
  return (
    <div className="flex gap-2 items-center py-3 px-2">
      <button className="rounded bg-indigo-500 text-white px-4 py-1 font-semibold shadow mr-2">Find</button>
      {filters.map(f => (
        <button
          key={f.value}
          onClick={() => onSelect(f.value)}
          className={`px-3 py-1 rounded-full font-medium transition
            ${selected === f.value ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-indigo-50'}`}
        >
          {f.label}
        </button>
      ))}
    </div>
  )
}
