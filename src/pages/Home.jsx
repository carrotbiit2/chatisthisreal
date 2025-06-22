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
    const uploadStartTime = Date.now();
    
    if (selectedImage || selectedVideo) {
      const file = selectedImage || selectedVideo;
      
      setIsLoading(true); // Start loading
      
      try {
        console.log('=== FRONTEND UPLOAD START ===');
        console.log('Upload start time:', new Date().toISOString());
        console.log('File:', file);
        console.log('File name:', file.name);
        console.log('File size:', file.size, 'bytes');
        console.log('File type:', file.type);
        console.log('File last modified:', new Date(file.lastModified).toISOString());
        console.log('API URL:', `${API_BASE_URL}/upload`);
        console.log('Environment:', import.meta.env.PROD ? 'production' : 'development');
        console.log('Current timestamp:', Date.now());
        
        // Create FormData to send file
        const formData = new FormData();
        formData.append('file', file);
        
        // Log FormData contents
        console.log('FormData entries:');
        for (let [key, value] of formData.entries()) {
          console.log(`${key}:`, value);
        }
        
        console.log('Creating fetch request...');
        const requestStartTime = Date.now();
        
        // Create a timeout promise
        const timeoutPromise = new Promise((_, reject) => {
          setTimeout(() => reject(new Error('Request timeout after 60 seconds')), 60000);
        });
        
        // Send file to Python backend using config URL
        const fetchPromise = fetch(`${API_BASE_URL}/upload`, {
          method: 'POST',
          body: formData,
          mode: 'cors',
          credentials: 'omit'
        });
        
        console.log('Fetch request created, waiting for response...');
        
        // Race between fetch and timeout
        const response = await Promise.race([fetchPromise, timeoutPromise]);
        
        const requestEndTime = Date.now();
        const requestDuration = requestEndTime - requestStartTime;
        
        console.log('=== RESPONSE RECEIVED ===');
        console.log('Response received at:', new Date().toISOString());
        console.log('Request duration:', requestDuration, 'ms');
        console.log('Response status:', response.status);
        console.log('Response status text:', response.statusText);
        console.log('Response headers:', Object.fromEntries(response.headers.entries()));
        
        if (!response.ok) {
          console.error('Response not OK. Status:', response.status);
          const errorText = await response.text();
          console.error('Error response body:', errorText);
          throw new Error(`HTTP ${response.status}: ${errorText}`);
        }
        
        console.log('Parsing response JSON...');
        const result = await response.json();
        console.log('=== RESPONSE BODY ===');
        console.log('Response body:', result);
        console.log('Response body type:', typeof result);
        console.log('Response body keys:', Object.keys(result));
        
        if (response.ok) {
          console.log('=== UPLOAD SUCCESS ===');
          console.log('File uploaded successfully:', result);
          console.log('Analysis result:', result.analysis_result);
          console.log('Percentage:', result.percentage);
          console.log('Model used:', result.model_used);
          console.log('Request duration from backend:', result.request_duration, 'seconds');
          
          setAnalysisResult(result.analysis_result);
          setPercentage(result.percentage);
        } else {
          console.error('Upload failed:', result.error);
          alert(`Upload failed: ${result.error}`);
        }
      } catch (error) {
        const uploadEndTime = Date.now();
        const totalUploadDuration = uploadEndTime - uploadStartTime;
        
        console.error('=== UPLOAD ERROR ===');
        console.error('Error occurred at:', new Date().toISOString());
        console.error('Total upload duration:', totalUploadDuration, 'ms');
        console.error('Error type:', error.constructor.name);
        console.error('Error name:', error.name);
        console.error('Error message:', error.message);
        console.error('Error stack:', error.stack);
        
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
          alert('Network error: Cannot connect to server. Please check your internet connection.');
        } else if (error.message.includes('CORS')) {
          alert('CORS error: Server is not allowing requests from this domain.');
        } else if (error.message.includes('timeout')) {
          alert(`Timeout error: ${error.message}. The server took too long to respond.`);
        } else {
          alert(`Error uploading file: ${error.message}`);
        }
      } finally {
        const uploadEndTime = Date.now();
        const totalUploadDuration = uploadEndTime - uploadStartTime;
        
        console.log('=== UPLOAD COMPLETE ===');
        console.log('Upload completed at:', new Date().toISOString());
        console.log('Total upload duration:', totalUploadDuration, 'ms');
        console.log('Loading state set to false');
        
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