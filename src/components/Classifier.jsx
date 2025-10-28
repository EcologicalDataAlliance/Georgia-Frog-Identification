import React, {useState} from 'react'
import { post } from '../api/api'

export default function Classifier(){
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleFile = (e) => {
    setFile(e.target.files[0])
    setResult(null)
    setError(null)
  }

  const runClassification = async () => {
    if(!file) return setError('Please select an audio file')
    setLoading(true)
    setError(null)
    setResult(null)
    try{
      const form = new FormData()
      form.append('file', file)
      // posts to `${VITE_API_BASE}/classify` if VITE_API_BASE set
      const res = await post('/classify', form, { isFormData: true })
      setResult(res)
    }catch(err){
      console.error(err)
      setError(err?.message || 'Failed to contact backend — this is a scaffold; set VITE_API_BASE to enable API calls')
    }finally{
      setLoading(false)
    }
  }

  return (
    <section>
      <h2>Classifier Interface</h2>
      <p>Upload an audio file (wav/mp3) to run classification. This will POST to <code>/classify</code> on your configured API base.</p>

      <div className="card form-card">
        <label className="file-input">
          <input type="file" accept="audio/*" onChange={handleFile} />
        </label>

        <div className="form-actions">
          <button onClick={runClassification} disabled={loading}>{loading ? 'Running...' : 'Run Classifier'}</button>
        </div>

        {error && <div className="error">{error}</div>}

        {result && (
          <div className="result">
            <h3>Result</h3>
            <pre>{JSON.stringify(result, null, 2)}</pre>
          </div>
        )}
      </div>
    </section>
  )
}
