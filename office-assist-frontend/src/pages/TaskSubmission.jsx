import { useEffect, useState } from 'react';
import { FileText, Upload as UploadIcon, CheckCircle, XCircle, ListChecks } from 'lucide-react';
import { getEmployeeProgress, submitTask } from '../services/api';
import './TaskSubmission.css';

function TaskSubmission({ user }) {
  const [taskText, setTaskText] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [progress, setProgress] = useState(null);

  useEffect(() => {
    const loadProgress = async () => {
      try {
        const employeeId = user.email || user.conversationId;
        const progressData = await getEmployeeProgress(employeeId);
        setProgress(progressData);
      } catch (error) {
        console.error('Progress fetch error:', error);
      }
    };
    loadProgress();
  }, [user]);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if ((!taskText.trim() && !file) || loading) return;

    setLoading(true);
    setResult(null);

    try {
      const employeeId = user.email || user.conversationId;
      const response = await submitTask(taskText, file, {
        id: employeeId,
        name: user.name,
      });
      const progressData = await getEmployeeProgress(employeeId);
      setProgress(progressData);
      setResult({ success: true, data: response });
      setTaskText('');
      setFile(null);
      if (e.target.file) {
        e.target.file.value = '';
      }
    } catch (error) {
      setResult({
        success: false,
        error: error.response?.data?.error || 'Failed to submit task. Please ensure the backend is running.',
      });
      console.error('Task submission error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return '#10b981';
    if (score >= 60) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div className="task-page">
      <div className="container">
        <div className="task-container">
          <div className="task-header">
            <h1>📝 Task Submission</h1>
            <p>Submit your training tasks and get AI-powered feedback</p>
          </div>

          <div className="task-content">
            <div className="submission-form card">
              <div className="section-title-row">
                <div>
                  <span className="eyebrow">Work queue</span>
                  <h3>Submit Your Task</h3>
                </div>
                <div className="task-counter-badge">
                  <ListChecks size={16} />
                  <span>{progress?.standard_tasks_completed || 0} tasks done</span>
                </div>
              </div>

              {progress && (
                <div className="task-progress-strip">
                  <div className="task-progress-item">
                    <strong>{progress.total_tasks_completed || 0}</strong>
                    <span>Total completed</span>
                  </div>
                  <div className="task-progress-item">
                    <strong>{progress.standard_tasks_completed || 0}</strong>
                    <span>Standard tasks</span>
                  </div>
                  <div className="task-progress-item">
                    <strong>{progress.scenario_tasks_completed || 0}</strong>
                    <span>Scenario tasks</span>
                  </div>
                </div>
              )}

              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label htmlFor="taskText">Task Description or Answer</label>
                  <textarea
                    id="taskText"
                    className="input textarea"
                    placeholder="Describe your task or paste your answer here..."
                    value={taskText}
                    onChange={(e) => setTaskText(e.target.value)}
                    rows="8"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="file">Or Upload a File (Optional)</label>
                  <div className="file-input-wrapper">
                    <input
                      type="file"
                      id="file"
                      className="file-input"
                      onChange={handleFileChange}
                      accept=".txt,.doc,.docx,.pdf"
                    />
                    <label htmlFor="file" className="file-label">
                      <UploadIcon size={20} />
                      {file ? file.name : 'Choose a file'}
                    </label>
                  </div>
                  <p className="help-text">Accepted formats: .txt, .doc, .docx, .pdf</p>
                </div>

                <button
                  type="submit"
                  className="btn btn-primary btn-block"
                  disabled={loading || (!taskText.trim() && !file)}
                >
                  {loading ? (
                    <>
                      <div className="spinner"></div>
                      Grading...
                    </>
                  ) : (
                    <>
                      <FileText size={20} />
                      Submit Task
                    </>
                  )}
                </button>
              </form>
            </div>

            {result && (
              <div className={`result-card card fade-in ${result.success ? 'success' : 'error'}`}>
                {result.success ? (
                  <>
                    <div className="result-header">
                      <CheckCircle size={48} color="#10b981" />
                      <h3>Task Graded Successfully!</h3>
                    </div>
                    <div className="score-section">
                      <div className="score-circle" style={{ borderColor: getScoreColor(result.data.score) }}>
                        <span className="score-value" style={{ color: getScoreColor(result.data.score) }}>
                          {result.data.score}
                        </span>
                        <span className="score-label">/ 100</span>
                      </div>
                    </div>
                    <div className="feedback-section">
                      <h4>Feedback:</h4>
                      <p>{result.data.feedback}</p>
                    </div>
                    <div className="metadata">
                      <p><strong>Task ID:</strong> {result.data.task_id}</p>
                      <p><strong>Submitted:</strong> {new Date(result.data.timestamp).toLocaleString()}</p>
                      {progress && <p><strong>Tasks Done:</strong> {progress.standard_tasks_completed}</p>}
                    </div>
                  </>
                ) : (
                  <>
                    <div className="result-header">
                      <XCircle size={48} color="#ef4444" />
                      <h3>Submission Failed</h3>
                    </div>
                    <p className="error-message">{result.error}</p>
                  </>
                )}
              </div>
            )}
          </div>

          <div className="info-section card">
            <h3>ℹ️ How it works</h3>
            <ul className="info-list">
              <li>Submit your completed training task as text or file</li>
              <li>Our AI will grade your submission against job readiness rubrics</li>
              <li>Receive detailed feedback and a score out of 100</li>
              <li>All submissions are saved to your profile for tracking progress</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TaskSubmission;
