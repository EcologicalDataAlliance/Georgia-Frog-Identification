import React, {useState, useRef} from 'react'
import { post } from '../api/api'

export default function Classifier(){
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [audioUrl, setAudioUrl] = useState(null)
  const [isRecording, setIsRecording] = useState(false)
  const [recordingMode, setRecordingMode] = useState('upload') // 'upload' or 'record'
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])

  const handleFile = (e) => {
    const selectedFile = e.target.files[0]
    setFile(selectedFile)
    setResult(null)
    setError(null)
    
    // Create audio URL for playback
    if (selectedFile) {
      if (audioUrl) URL.revokeObjectURL(audioUrl)
      setAudioUrl(URL.createObjectURL(selectedFile))
    }
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      
      // Try to use MP3 if supported, fall back to webm
      let mimeType = 'audio/webm'
      if (MediaRecorder.isTypeSupported('audio/mp4')) {
        mimeType = 'audio/mp4'
      } else if (MediaRecorder.isTypeSupported('audio/mpeg')) {
        mimeType = 'audio/mpeg'
      } else if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
        mimeType = 'audio/webm;codecs=opus'
      }
      
      const mediaRecorder = new MediaRecorder(stream, { mimeType })
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType })
        const extension = mimeType.includes('mp4') ? '.m4a' : (mimeType.includes('mpeg') ? '.mp3' : '.webm')
        const file = new File([audioBlob], `recording${extension}`, { type: mimeType })
        setFile(file)
        
        // Create audio URL for playback
        if (audioUrl) URL.revokeObjectURL(audioUrl)
        setAudioUrl(URL.createObjectURL(audioBlob))
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start()
      setIsRecording(true)
      setError(null)
      setResult(null)
    } catch (err) {
      console.error('Error accessing microphone:', err)
      setError('Could not access microphone. Please check permissions.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
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
      <p>Upload or record an audio file containing frog calls. The classifier will identify the top 3 most likely species with confidence scores.</p>

      <div className="card form-card">
        <div className="recording-mode-toggle">
          <button 
            className={`mode-btn ${recordingMode === 'upload' ? 'active' : ''}`}
            onClick={() => setRecordingMode('upload')}
            disabled={isRecording}
          >
            📁 Upload File
          </button>
          <button 
            className={`mode-btn ${recordingMode === 'record' ? 'active' : ''}`}
            onClick={() => setRecordingMode('record')}
            disabled={isRecording}
          >
            🎤 Record Audio
          </button>
        </div>

        {recordingMode === 'upload' ? (
          <label className="file-input">
            <input type="file" accept="audio/*" onChange={handleFile} />
            {file && <span className="file-name">Selected: {file.name}</span>}
          </label>
        ) : (
          <div className="recording-controls">
            {!isRecording ? (
              <button onClick={startRecording} className="record-btn">
                🎤 Start Recording
              </button>
            ) : (
              <button onClick={stopRecording} className="stop-btn">
                ⏹️ Stop Recording
              </button>
            )}
            {isRecording && <span className="recording-indicator">● Recording...</span>}
            {file && !isRecording && <span className="file-name">Recording ready: {file.name}</span>}
          </div>
        )}

        {audioUrl && (
          <div className="audio-playback">
            <h4>Preview Audio:</h4>
            <audio controls src={audioUrl} style={{width:'100%'}}>
              Your browser does not support the audio element.
            </audio>
          </div>
        )}

        <div className="classifier-disclaimer">
          <strong>💡 For Best Results:</strong>
          <ul>
            <li>Record for 15-30 seconds to capture clear frog calls</li>
            <li>Get as close as safely possible to the sound source</li>
            <li>Minimize background noise (wind, traffic, talking)</li>
            <li>Record during peak calling times (evening/night)</li>
            <li>Supported formats: WAV, MP3, FLAC, OGG, M4A, WebM</li>
          </ul>
        </div>

        <div className="form-actions">
          <button onClick={runClassification} disabled={loading || !file}>
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
