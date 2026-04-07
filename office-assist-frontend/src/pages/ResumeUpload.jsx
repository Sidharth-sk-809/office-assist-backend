import { useState } from 'react';
import { Upload as UploadIcon, FileCheck, AlertCircle, Award } from 'lucide-react';
import { classifyResume } from '../services/api';
import './ResumeUpload.css';

function ResumeUpload({ user }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.type === 'application/pdf') {
        setFile(droppedFile);
      } else {
        alert('Please upload a PDF file');
      }
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || loading) return;

    setLoading(true);
    setResult(null);

    try {
      const response = await classifyResume(file);
      setResult({ success: true, data: response });
    } catch (error) {
      setResult({
        success: false,
        error: error.response?.data?.error || 'Failed to classify resume. Please ensure the backend is running.',
      });
      console.error('Resume classification error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getLevelColor = (level) => {
    const colors = {
      Junior: '#3b82f6',
      Mid: '#10b981',
      Senior: '#f59e0b',
    };
    return colors[level] || '#6b7280';
  };

  const getLevelIcon = (level) => {
    const levels = {
      Junior: '🌱',
      Mid: '🚀',
      Senior: '👑',
    };
    return levels[level] || '📄';
  };

  return (
    <div className="resume-page">
      <div className="container">
        <div className="resume-container">
          <div className="resume-header">
            <h1>📄 Resume Analysis</h1>
            <p>Upload your resume to get AI-powered experience level assessment</p>
          </div>

          <div className="resume-content">
            <div className="upload-section card">
              <h3>Upload Your Resume</h3>
              
              <form onSubmit={handleSubmit}>
                <div
                  className={`drop-zone ${dragActive ? 'active' : ''} ${file ? 'has-file' : ''}`}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                >
                  <input
                    type="file"
                    id="resume-file"
                    className="file-input"
                    accept=".pdf"
                    onChange={handleFileChange}
                  />
                  <label htmlFor="resume-file" className="drop-zone-label">
                    {file ? (
                      <>
                        <FileCheck size={48} color="#10b981" />
                        <p className="file-name">{file.name}</p>
                        <p className="file-size">{(file.size / 1024).toFixed(2)} KB</p>
                      </>
                    ) : (
                      <>
                        <UploadIcon size={48} color="#6b7280" />
                        <p>Drag & drop your resume here</p>
                        <p className="or-text">or</p>
                        <span className="browse-btn">Browse Files</span>
                      </>
                    )}
                  </label>
                </div>
                <p className="help-text">Only PDF files are accepted</p>

                {file && (
                  <button
                    type="submit"
                    className="btn btn-primary btn-block"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <div className="spinner"></div>
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <Award size={20} />
                        Analyze Resume
                      </>
                    )}
                  </button>
                )}
              </form>
            </div>

            {result && (
              <div className={`result-card card fade-in ${result.success ? 'success' : 'error'}`}>
                {result.success ? (
                  <>
                    <div className="result-header">
                      <div
                        className="level-badge"
                        style={{ backgroundColor: `${getLevelColor(result.data.level)}20`, color: getLevelColor(result.data.level) }}
                      >
                        <span className="level-icon">{getLevelIcon(result.data.level)}</span>
                        <span className="level-text">{result.data.level} Level</span>
                      </div>
                    </div>

                    {result.data.confidence && (
                      <div className="confidence-section">
                        <h4>Confidence Score</h4>
                        <div className="confidence-bar">
                          <div
                            className="confidence-fill"
                            style={{
                              width: `${result.data.confidence * 100}%`,
                              backgroundColor: getLevelColor(result.data.level),
                            }}
                          />
                        </div>
                        <p className="confidence-text">{(result.data.confidence * 100).toFixed(1)}%</p>
                      </div>
                    )}

                    {result.data.reasoning && (
                      <div className="reasoning-section">
                        <h4>Analysis</h4>
                        <p>{result.data.reasoning}</p>
                      </div>
                    )}

                    <button
                      className="btn btn-secondary btn-block"
                      onClick={() => {
                        setFile(null);
                        setResult(null);
                      }}
                    >
                      Upload Another Resume
                    </button>
                  </>
                ) : (
                  <>
                    <div className="result-header">
                      <AlertCircle size={48} color="#ef4444" />
                      <h3>Analysis Failed</h3>
                    </div>
                    <p className="error-message">{result.error}</p>
                  </>
                )}
              </div>
            )}
          </div>

          <div className="info-section card">
            <h3>ℹ️ How Resume Analysis Works</h3>
            <ul className="info-list">
              <li>Upload your resume in PDF format</li>
              <li>Our AI analyzes your experience, skills, and achievements</li>
              <li>Get classified as Junior, Mid-level, or Senior professional</li>
              <li>Receive detailed reasoning for the classification</li>
              <li>Use this insight to understand how employers might view your experience</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ResumeUpload;
