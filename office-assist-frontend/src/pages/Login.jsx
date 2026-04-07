import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bot, FileText, ShieldCheck, UserPlus } from 'lucide-react';
import './Login.css';

function Login({ onLogin }) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    role: 'new-joiner',
    position: 'basic',
  });
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.name && formData.email) {
      onLogin(formData);
      navigate('/dashboard');
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-card card">
          <div className="login-header">
            <div>
              <div className="login-icon">
                <UserPlus size={48} />
              </div>
              <h1>Elegant workspace. Same trusted workflow.</h1>
              <p>Your AI-powered HR training companion for policy guidance, task review, and resume insight.</p>
            </div>

            <div className="login-highlights">
              <div className="login-highlight">
                <ShieldCheck size={20} />
                <div>
                  <strong>Policy support</strong>
                  <span>Ask HR and training questions instantly</span>
                </div>
              </div>
              <div className="login-highlight">
                <FileText size={20} />
                <div>
                  <strong>Automated grading</strong>
                  <span>Submit tasks and receive structured feedback</span>
                </div>
              </div>
              <div className="login-highlight">
                <Bot size={20} />
                <div>
                  <strong>Resume intelligence</strong>
                  <span>Upload a PDF and get role-level analysis</span>
                </div>
              </div>
            </div>
          </div>

          <div className="login-form-panel">
            <form onSubmit={handleSubmit} className="login-form">
              <div className="form-group">
                <label htmlFor="name">Full Name</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  className="input"
                  placeholder="Enter your full name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="email">Email Address</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  className="input"
                  placeholder="Enter your email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="role">Role</label>
                <select
                  id="role"
                  name="role"
                  className="input"
                  value={formData.role}
                  onChange={handleChange}
                >
                  <option value="new-joiner">New Joiner</option>
                  <option value="intern">Intern</option>
                  <option value="trainee">Trainee</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="position">Skill Level / Position</label>
                <select
                  id="position"
                  name="position"
                  className="input"
                  value={formData.position}
                  onChange={handleChange}
                >
                  <option value="basic">Basic</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="expert">Expert</option>
                </select>
              </div>

              <button type="submit" className="btn btn-primary btn-block">
                Start Your Journey
              </button>
            </form>

            <div className="login-footer">
              <p className="info-text">
                Get instant answers to company policies, submit tasks for grading, and assess your resume with AI.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;
