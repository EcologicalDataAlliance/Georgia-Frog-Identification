import React from 'react'
import { Link } from 'react-router-dom'

export default function Home(){
  return (
    <section className="home-hero">
      <div className="hero-grid">
        <div>
          <h1>🐸 Georgia Frog Identification</h1>
          <p className="lede">Identify Georgia's native frog species using ML-powered audio classification. Upload or record frog calls to get instant species identification with confidence scores.</p>
          
          <div className="feature-cards">
            <div className="feature-card">
              <div className="feature-icon">🎵</div>
              <h3>ML Classifier</h3>
              <p>Upload or record frog calls to identify species with our trained Random Forest model</p>
              <Link to="/classifier" className="feature-link">Try Classifier →</Link>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">📚</div>
              <h3>Species Dictionary</h3>
              <p>Browse and listen to calls from 14 native Georgia frog and toad species</p>
              <Link to="/species" className="feature-link">View Species →</Link>
            </div>
          </div>

          <div className="stats-bar">
            <div className="stat">
              <strong>14</strong>
              <span>Species Classified</span>
            </div>
            <div className="stat">
              <strong>Top 3</strong>
              <span>Predictions</span>
            </div>
            <div className="stat">
              <strong>Audio</strong>
              <span>Upload & Record</span>
            </div>
          </div>
        </div>
        
        <div className="hero-panel">
          <div className="card hero-info-card">
            <h3>🎯 How It Works</h3>
            <ol className="steps-list">
              <li>Record or upload a frog call audio file</li>
              <li>Our ML model analyzes the audio features</li>
              <li>Get top 3 species predictions with confidence scores</li>
              <li>View images and learn about each species</li>
            </ol>
          </div>
          
          <div className="card hero-info-card">
            <h3>💡 Best Practices</h3>
            <ul className="tips-list">
              <li>Record for 15-30 seconds</li>
              <li>Get close to the source</li>
              <li>Minimize background noise</li>
              <li>Avoid wind and traffic sounds</li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  )
}