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
      // posts to `${VITE_API_BASE}/classify` which proxies to FastAPI
      const res = await post('/classify', form, { isFormData: true })
      setResult(res)
    }catch(err){
      console.error(err)
      setError(err?.message || 'Failed to classify audio. Make sure the backend services are running.')
    }finally{
      setLoading(false)
    }
  }

  // Format species name for display (e.g., "american_bullfrog" -> "American Bullfrog")
  const formatSpeciesName = (slug) => {
    return slug
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  return (
    <section>
      <h2>Frog Call Classifier</h2>
      <p>Upload an audio file (WAV, MP3, FLAC, OGG, M4A) containing frog calls. The classifier will identify the top 3 most likely species with confidence scores.</p>

      <div className="card form-card">
        <label className="file-input">
          <input type="file" accept="audio/*" onChange={handleFile} />
          {file && <span className="file-name">Selected: {file.name}</span>}
        </label>

        <div className="form-actions">
          <button onClick={runClassification} disabled={loading}>
            {loading ? 'Analyzing...' : 'Classify Recording'}
          </button>
        </div>

        {error && <div className="error">{error}</div>}

        {result && result.top_3 && (
          <div className="results-container">
            <h3>Top 3 Predictions</h3>
            <div className="prediction-cards">
              {result.top_3.map((pred, index) => (
                <div key={index} className="prediction-card" data-rank={index + 1}>
                  <div className="rank-badge">#{index + 1}</div>
                  <div className="prediction-image-container">
                    <img 
                      src={pred.image_url} 
                      alt={formatSpeciesName(pred.species)}
                      className="prediction-image"
                      onError={(e) => {
                        e.target.style.display = 'none'
                        e.target.nextElementSibling.style.display = 'flex'
                      }}
                    />
                    <div className="image-placeholder" style={{display: 'none'}}>
                      🐸
                    </div>
                  </div>
                  <div className="prediction-info">
                    <h4 className="species-name">{formatSpeciesName(pred.species)}</h4>
                    <div className="confidence-bar-container">
                      <div 
                        className="confidence-bar" 
                        style={{width: `${pred.confidence * 100}%`}}
                      ></div>
                    </div>
                    <p className="confidence-text">
                      {(pred.confidence * 100).toFixed(1)}% confidence
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  )
}
