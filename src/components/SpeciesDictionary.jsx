import React, {useState} from 'react'

export default function SpeciesDictionary(){
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])

  // Placeholder: in the future we'll fetch from the backend
  const mockSpecies = [
    {id: 'Litoria caerulea', common: 'Green tree frog'},
    {id: 'Rana temporaria', common: 'Common frog'},
    {id: 'Hyla arborea', common: 'European tree frog'}
  ]

  const doSearch = (e)=>{
    e.preventDefault()
    const q = query.toLowerCase().trim()
    setResults(mockSpecies.filter(s => s.id.toLowerCase().includes(q) || s.common.toLowerCase().includes(q)))
  }

  return (
    <section>
      <h2>Species Dictionary</h2>
      <p>Search for species by scientific or common name. This is a client-side placeholder; we'll wire a backend endpoint later.</p>

      <form className="search-form" onSubmit={doSearch}>
        <input placeholder="Search species..." value={query} onChange={e => setQuery(e.target.value)} />
        <button type="submit">Search</button>
      </form>

      <div className="cards">
        {results.length === 0 && <div className="muted">No results — try "frog" or "Litoria" (sample data)</div>}
        {results.map(r => (
          <div className="card" key={r.id}>
            <h3>{r.id}</h3>
            <p className="muted">{r.common}</p>
          </div>
        ))}
      </div>
    </section>
  )
}
