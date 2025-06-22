import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './TopBar.css';
import DarkModeToggle from './DarkModeToggle';
import logo from '../assets/logo.png';

function TopBar({ isDarkMode, onToggleDarkMode }) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  return (
    <nav className={`topbar ${isDarkMode ? 'dark-mode' : ''}`}>
      <div className="topbar-container">
        <div className="topbar-brand">
          <div className="brand-content">
            <img src={logo} alt="Logo" className="topbar-logo" />
            <div className="brand-text">
              <h2>Chat Is This Real?</h2>
              <h5>By Connect</h5>
            </div>
          </div>
        </div>
        
        <div className={`topbar-menu ${isMenuOpen ? 'active' : ''}`}>
          <Link to="/" className="topbar-link">Home</Link>
          <Link to="/about" className="topbar-link">About</Link>
          <Link to="/contact" className="topbar-link">Report a Problem</Link>
          <div className="mode-toggle-container">
            <span className="mode-label">Theme</span>
            <DarkModeToggle isDarkMode={isDarkMode} onToggle={onToggleDarkMode} />
          </div>
        </div>
        
        <div className="topbar-toggle" onClick={toggleMenu}>
          <span className="hamburger"></span>
          <span className="hamburger"></span>
          <span className="hamburger"></span>
        </div>
      </div>
    </nav>
  );
}

export default TopBar; 