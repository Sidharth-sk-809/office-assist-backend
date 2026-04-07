import { useState } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle, Loader } from 'lucide-react';
import { uploadMaterial } from '../services/api';
import './MaterialsUpload.css';

function MaterialsUpload({ user }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
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

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type === 'application/pdf') {
      setFile(droppedFile);
      setError(null);
      setResult(null);
    } else {
      setError('Please upload a PDF file');
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (selectedFile.type === 'application/pdf') {
        setFile(selectedFile);
        setError(null);
        setResult(null);
      } else {
        setError('Please select a PDF file');
      }
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setUploading(true);
    setError(null);
    setResult(null);

    try {
      const response = await uploadMaterial(file);
      setResult(response);
      setFile(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload material. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setResult(null);
    setError(null);
  };

  return (
    <div className="materials-upload-page">
      <div className="container">
        <div className="page-header">
          <div className="header-icon" style={{ backgroundColor: '#8b5cf620', color: '#8b5cf6' }}>
            <Upload size={32} />
          </div>
          <div>
            <h1>Upload Training Materials</h1>
            <p className="subtitle">Upload policy documents and training materials for the knowledge base</p>
          </div>
        </div>

        <div className="upload-container card">
          {!result ? (
            <>
              <div 
                className={`upload-zone ${dragActive ? 'drag-active' : ''} ${file ? 'has-file' : ''}`}
                onDragEnter={handleDrag}
                onDragOver={handleDrag}
                onDragLeave={handleDrag}
                onDrop={handleDrop}
              >
                {file ? (
                  <div className="file-preview">
                    <FileText size={48} className="file-icon" />
                    <div className="file-details">
                      <h3>{file.name}</h3>
                      <p className="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                    </div>
                    <button onClick={handleReset} className="btn-secondary btn-sm">
                      Change File
                    </button>
                  </div>
                ) : (
                  <div className="upload-prompt">
                    <Upload size={48} className="upload-icon" />
                    <h3>Drop your PDF here</h3>
                    <p>or click to browse</p>
                    <input
                      type="file"
                      accept=".pdf"
                      onChange={handleFileChange}
                      className="file-input"
                      id="file-upload"
                    />
                    <label htmlFor="file-upload" className="btn-primary">
                      Select PDF File
                    </label>
                  </div>
                )}
              </div>

              {file && (
                <div className="upload-actions">
                  <button 
                    onClick={handleUpload} 
                    disabled={uploading}
                    className="btn-primary btn-large"
                  >
                    {uploading ? (
                      <>
                        <Loader size={20} className="spinner" />
                        Uploading...
                      </>
                    ) : (
                      <>
                        <Upload size={20} />
                        Upload Material
                      </>
                    )}
                  </button>
                </div>
              )}

              {error && (
                <div className="alert alert-error">
                  <AlertCircle size={20} />
                  <div>
                    <strong>Upload Failed</strong>
                    <p>{error}</p>
                  </div>
                </div>
              )}

              <div className="info-section">
                <h3>📚 About Material Upload</h3>
                <div className="info-grid">
                  <div className="info-item">
                    <strong>Supported Format:</strong>
                    <p>PDF documents only</p>
                  </div>
                  <div className="info-item">
                    <strong>File Size:</strong>
                    <p>Maximum 10 MB per file</p>
                  </div>
                  <div className="info-item">
                    <strong>Processing Time:</strong>
                    <p>10-30 minutes for indexing</p>
                  </div>
                  <div className="info-item">
                    <strong>Usage:</strong>
                    <p>Materials are added to the AI knowledge base for policy chat</p>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="success-container">
              <div className="success-icon">
                <CheckCircle size={64} />
              </div>
              <h2>Material Uploaded Successfully!</h2>
              <div className="result-details">
                <div className="result-item">
                  <strong>File:</strong>
                  <p>{result.filename}</p>
                </div>
                {result.gcs_uri && (
                  <div className="result-item">
                    <strong>Storage Location:</strong>
                    <p className="mono-text">{result.gcs_uri}</p>
                  </div>
                )}
                <div className="result-item">
                  <strong>Status:</strong>
                  <p className="status-badge success">{result.status}</p>
                </div>
                {result.message && (
                  <div className="result-item">
                    <strong>Note:</strong>
                    <p>{result.message}</p>
                  </div>
                )}
              </div>
              
              <div className="alert alert-info">
                <strong>ℹ️ Next Steps</strong>
                <p>Your material has been uploaded and will be indexed within 10-30 minutes. Once indexed, it will be available for queries in the Policy Chat.</p>
              </div>

              <button onClick={handleReset} className="btn-primary btn-large">
                Upload Another Material
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default MaterialsUpload;
