const BASE = import.meta.env.VITE_API_BASE || ''

async function request(path, options = {}){
  const url = `${BASE}${path}`
  const opts = { ...options }

  const resp = await fetch(url, opts)
  if(!resp.ok){
    const text = await resp.text().catch(()=>null)
    const err = new Error(`HTTP ${resp.status}: ${resp.statusText}`)
    err.status = resp.status
    err.body = text
    throw err
  }

  const ct = resp.headers.get('content-type') || ''
  if(ct.includes('application/json')) return resp.json()
  return resp.text()
}

export async function get(path){
  return request(path, { method: 'GET' })
}

// options: { isFormData: boolean, headers: {} }
export async function post(path, body, options = {}){
  const { isFormData, headers } = options
  const opts = {
    method: 'POST',
    headers: isFormData ? { ...headers } : { 'Content-Type': 'application/json', ...headers },
    body: isFormData ? body : JSON.stringify(body)
  }
  return request(path, opts)
}

// Get media URLs for a single species
export async function getSpeciesMedia(slug){
  return get(`/api/species/${slug}/media`)
}

// Get media URLs for multiple species (batch request)
export async function getSpeciesMediaBatch(slugs){
  return post('/api/species/media/batch', { slugs })
}

export default { get, post, getSpeciesMedia, getSpeciesMediaBatch }
