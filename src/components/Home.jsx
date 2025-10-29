import React from 'react'

export default function Home(){
  return (
    <section className="home-hero">
      <div className="hero-grid">
        <div>
          <h1>Frog Call Classifier Dashboard</h1>
          <p className="lede">Explore recordings, look up species, and run the classifier. This scaffold is ready to connect to a backend API.</p>
          <ul className="features">
            <li>Searchable species dictionary</li>
            <li>Classifier interface (upload audio / send to backend)</li>
            <li>Modern responsive UI</li>
          </ul>
        </div>
        <div className="hero-panel">
          <div className="card">
            <strong>Ready</strong>
            <p>Connect backend by setting <code>VITE_API_BASE</code>.</p>
          </div>
        </div>
      </div>
    </section>
  )
}