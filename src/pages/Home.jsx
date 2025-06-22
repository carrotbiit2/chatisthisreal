import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '../config';
import './Pages.css';
import './DarkMode.css';

function Home({ isDarkMode, onToggleDarkMode }) {
  const [selectedImage, setSelectedImage] = useState(null);
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [uploadType, setUploadType] = useState('image');
  const [activeTab, setActiveTab] = useState('image');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [percentage, setPercentage] = useState(0);
  const [isDragOver, setIsDragOver] = useState(false);

  // Auto-scroll to bottom when analysis result is displayed
  useEffect(() => {
    if (analysisResult) {
      window.scrollTo({
        top: document.documentElement.scrollHeight,
        behavior: 'smooth'
      });
    }
  }, [analysisResult]);

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedImage(file);
      setSelectedVideo(null);
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      setUploadType('image');
    }
  };

  const handleVideoUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedVideo(file);
      setSelectedImage(null);
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      setUploadType('video');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (selectedImage || selectedVideo) {
      const file = selectedImage || selectedVideo;
      
      setIsLoading(true); // Start loading
      
      try {
        console.log('Starting upload...');
        console.log('File:', file);
        console.log('API URL:', `${API_BASE_URL}/upload`);
        
        // Create FormData to send file
        const formData = new FormData();
        formData.append('file', file);
        
        // Send file to Python backend using config URL
        const response = await fetch(`${API_BASE_URL}/upload`, {
          method: 'POST',
          body: formData,
        });
        
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        
        const result = await response.json();
        console.log('Response body:', result);
        
        if (response.ok) {
          console.log('File uploaded successfully:', result);
          setAnalysisResult(result.analysis_result);
          setPercentage(result.percentage);
        } else {
          console.error('Upload failed:', result.error);
          alert(`Upload failed: ${result.error}`);
        }
      } catch (error) {
        console.error('Error uploading file:', error);
        console.error('Error details:', error.message);
        alert('Error uploading file. Please try again.');
      } finally {
        setIsLoading(false); // Stop loading regardless of success/failure
      }
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) {
      if (file.type.startsWith('image/')) {
        setSelectedImage(file);
        setSelectedVideo(null);
        setUploadType('image');
        setActiveTab('image');
      } else if (file.type.startsWith('video/')) {
        setSelectedVideo(file);
        setSelectedImage(null);
        setUploadType('video');
        setActiveTab('video');
      }
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    }
  };

  const resetUpload = () => {
    setSelectedImage(null);
    setSelectedVideo(null);
    setPreviewUrl(null);
    setUploadType(activeTab);
    setAnalysisResult(null);
    setPercentage(0);
    setIsLoading(false);
    setIsDragOver(false);
  };

  return (
    <div className={`page ${isDarkMode ? 'dark-mode' : ''}`}>
      {!previewUrl ? (
        <>
          <h1>Upload Your Image/Video</h1>
          
          <div className="upload-tabs">
            <button 
              className={`tab-btn ${activeTab === 'image' ? 'active' : ''}`}
              onClick={() => setActiveTab('image')}
            >
              Upload Image
            </button>
            <button 
              className={`tab-btn ${activeTab === 'video' ? 'active' : ''}`}
              onClick={() => setActiveTab('video')}
            >
              Upload Video
            </button>
          </div>
          
          <div className="upload-container">
            <div 
              className={`upload-area ${isDragOver ? 'dragover' : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <div className="upload-content">
                <h3>Drag & Drop your {activeTab} here</h3>
                <p>or</p>
                <label htmlFor={`${activeTab}-upload`} className="upload-btn">
                  Choose {activeTab === 'image' ? 'Image' : 'Video'}
                  <input
                    id={`${activeTab}-upload`}
                    type="file"
                    accept={activeTab === 'image' ? 'image/*' : 'video/*'}
                    onChange={activeTab === 'image' ? handleImageUpload : handleVideoUpload}
                    style={{ display: 'none' }}
                  />
                </label>
              </div>
            </div>
          </div>
        </>
      ) : (
        <div className="preview-page">
          <div className="preview-header">
            <h1>Your {uploadType === 'image' ? 'Image' : 'Video'}</h1>
            <div className="preview-buttons">
              <button 
                onClick={handleSubmit} 
                className="submit-btn"
                disabled={isLoading}
              >
                {isLoading ? 'Uploading...' : 'Upload to Server'}
              </button>
              <button 
                onClick={resetUpload} 
                className="change-btn"
                disabled={isLoading}
              >
                Upload New File
              </button>
            </div>
          </div>
          
          <div className="large-preview">
            {uploadType === 'image' ? (
              <img src={previewUrl} alt="Preview" className="large-image" />
            ) : (
              <video src={previewUrl} controls className="large-video" />
            )}
            {analysisResult && (
              <div className="analysis-result">
                <h3>Media Analysis</h3>
                <div className="gradient-bar-container">
                  <div className="gradient-bar">
                    <div 
                      className="percentage-marker" 
                      style={{ left: `${percentage}%` }}
                    ></div>
                  </div>
                  <div className="gradient-labels">
                    <span className="label-ai">AI (0%)</span>
                    <span className="label-human">Human (100%)</span>
                  </div>
                  <div className="percentage-display">
                    <span className="percentage-value">{percentage}</span>
                  </div>
                </div>
              </div>
            )}
            {isLoading && (
              <div className="loading-overlay">
                <div className="loading-spinner"></div>
                <p>Processing Image... This could take a while.</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default Home;