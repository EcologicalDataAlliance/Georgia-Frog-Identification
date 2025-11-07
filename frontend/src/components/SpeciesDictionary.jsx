import React, {useState, useEffect} from 'react'
import { getSpeciesMediaBatch } from '../api/api'

export default function SpeciesDictionary(){
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(true)
  const [mediaUrls, setMediaUrls] = useState({})

  // Placeholder species list (14 entries). Each item includes placeholder image and audio paths
  const mockSpecies = [
    { id: 'Anaxyrus americanus', common: 'American Toad', slug: 'american_toad' },
    { id: 'Hyla avivoca', common: 'Bird-Voiced Tree Frog', slug: 'bird_voiced_tree_frog' },
    { id: 'Lithobates catesbeianus', common: 'American bullfrog', slug: 'american_bullfrog' },
    { id: 'Hyla chrysoscelis', common: "Cope’s gray treefrog", slug: 'copes_gray_treefrog' },
    { id: 'Gastrophryne carolinensis', common: 'Eastern narrow-mouthed toad', slug: 'eastern_narrow_mouthed_toad' },
    { id: 'Scaphiopus holbrookii', common: 'Eastern Spadefoot Toad', slug: 'eastern_spadefoot_toad' },
    { id: 'Anaxyrus fowleri', common: "Fowler’s Toad", slug: 'fowlers_toad' },
    { id: 'Lithobates clamitans', common: 'Green Frog', slug: 'green_frog' },
    { id: 'Hyla cinerea', common: 'Green Tree Frog', slug: 'green_tree_frog' },
    { id: 'Acris crepitans', common: 'Northern cricket frog', slug: 'northern_cricket_frog' },
    { id: 'Lithobates palustris', common: 'Pickerel frog', slug: 'pickerel_frog' },
    { id: 'Lithobates sphenocephalus', common: 'Southern Leopard frog', slug: 'southern_leopard_frog' },
    { id: 'Pseudacris crucifer', common: 'Spring peeper', slug: 'spring_peeper' },
    { id: 'Pseudacris feriarum', common: 'Upland chorus frog', slug: 'upland_chorus_frog' }
  ]

  // Fetch media URLs from Supabase on component mount
  useEffect(() => {
    const fetchMediaUrls = async () => {
      try {
        setLoading(true)
        const slugs = mockSpecies.map(s => s.slug)
        const urls = await getSpeciesMediaBatch(slugs)
        setMediaUrls(urls)
      } catch (error) {
        console.error('Error fetching media URLs:', error)
        // Continue with fallback paths if backend fails
      } finally {
        setLoading(false)
      }
    }
    
    fetchMediaUrls()
  }, [])

  // Add derived image/audio paths with Supabase URLs or fallbacks
  const species = mockSpecies.map(s => ({
    ...s,
    image: mediaUrls[s.slug]?.image || `/assets/images/${s.slug}.jpg`,
    audio: mediaUrls[s.slug]?.audio || `/assets/audio/${s.slug}.mp3`
  }))

  const doSearch = (e)=>{
    e.preventDefault()
    const q = query.toLowerCase().trim()
    if(!q) return setResults(species)
    setResults(species.filter(s => s.id.toLowerCase().includes(q) || s.common.toLowerCase().includes(q) || s.slug.includes(q)))
  }

  return (
    <section>
      <h2>Species Dictionary</h2>
      <p>Search for species by scientific, common name, or slug name. {loading && 'Loading media from Supabase...'}</p>

      <form className="search-form" onSubmit={doSearch}>
        <input placeholder="Search species..." value={query} onChange={e => setQuery(e.target.value)} />
        <button type="submit">Search</button>
      </form>

      <div className="cards">
        {results.length === 0 && <div className="muted">No results — try "frog" or "Lithobates" (sample data)</div>}
        {results.map(r => (
          <div className="card" key={r.id}>
            <div style={{display:'flex',gap:12,alignItems:'center'}}>
              <img src={r.image} alt={`${r.common} thumbnail`} style={{width:96,height:64,objectFit:'cover',borderRadius:8,flex:'0 0 auto',background:'#efefef'}} onError={(e)=>{e.target.style.display='none'}} />
              <div style={{flex:1}}>
                <h3 style={{margin:0}}>{r.common}</h3>
                <div className="muted" style={{fontSize:'0.9rem'}}>{r.id}</div>
              </div>
            </div>

            <div style={{marginTop:12}}>
              <audio controls src={r.audio} style={{width:'100%'}}>
                Your browser does not support the audio element.
              </audio>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
