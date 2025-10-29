import React from 'react'
import { Routes, Route, Link } from 'react-router-dom'
import Home from './components/Home'
import SpeciesDictionary from './components/SpeciesDictionary'
import Classifier from './components/Classifier'

export default function App() {
  return (
    <div className="app-root">
      <header className="site-header">
        <div className="container">
          <Link to="/" className="brand">Hikes of Georgia</Link>
          <nav className="main-nav">
            <Link to="/species">Species Dictionary</Link>
            <Link to="/classifier">Classifier</Link>
          </nav>
        </div>
      </header>

      <main className="container">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/species" element={<SpeciesDictionary />} />
          <Route path="/classifier" element={<Classifier />} />
        </Routes>
      </main>

      <footer className="site-footer">
        <div className="container">© {(new Date()).getFullYear()} Hikes of Georgia</div>
      </footer>
    </div>
  )
}