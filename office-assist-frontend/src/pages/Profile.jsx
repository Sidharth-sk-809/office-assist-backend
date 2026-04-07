import { useState, useEffect } from 'react';
import { User, Save, AlertCircle } from 'lucide-react';
import './Profile.css';

function Profile({ user, onUpdateProfile }) {
  const [formData, setFormData] = useState({
    name: user.name || '',
    email: user.email || '',
    role: user.role || 'new-joiner',
    position: user.position || 'basic',
  });
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onUpdateProfile(formData);
    setMessageType('success');
    setMessage('Profile updated successfully! 🎉');
    setTimeout(() => setMessage(''), 3000);
  };

  return (
    <div className="profile-page">
      <div className="container">
        <div className="profile-header">
          <div className="profile-icon">
            <User size={48} />
          </div>
          <div>
            <h1>Your Profile</h1>
            <p className="subtitle">Manage your personal information and work experience level</p>
          </div>
        </div>

        <div className="profile-content">
          <form onSubmit={handleSubmit} className="profile-form card">
            <h2>Personal Information</h2>

            <div className="form-group">
              <label htmlFor="name">Full Name</label>
              <input
                type="text"
                id="name"
                name="name"
                className="input"
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

            <h2 style={{ marginTop: '2rem' }}>Work Experience Level</h2>
            <p className="experience-hint">Select your current skill level based on your work experience</p>

            <div className="experience-levels">
              {[
                {
                  value: 'basic',
                  label: 'Beginner',
                  description: 'Just starting out with less than 1 year of experience',
                  icon: '🌱'
                },
                {
                  value: 'intermediate',
                  label: 'Intermediate',
                  description: '1-3 years of experience with solid foundational skills',
                  icon: '📈'
                },
                {
                  value: 'expert',
                  label: 'Expert',
                  description: '3+ years of experience with advanced expertise',
                  icon: '⭐'
                }
              ].map(level => (
                <label key={level.value} className={`experience-card ${formData.position === level.value ? 'selected' : ''}`}>
                  <input
                    type="radio"
                    name="position"
                    value={level.value}
                    checked={formData.position === level.value}
                    onChange={handleChange}
                    className="radio-input"
                  />
                  <div className="experience-content">
                    <div className="icon">{level.icon}</div>
                    <div className="text">
                      <strong>{level.label}</strong>
                      <p>{level.description}</p>
                    </div>
                  </div>
                </label>
              ))}
            </div>

            <button type="submit" className="btn btn-primary btn-submit">
              <Save size={18} />
              Save Changes
            </button>

            {message && (
              <div className={`message ${messageType}`}>
                <AlertCircle size={18} />
                {message}
              </div>
            )}
          </form>

          <div className="profile-info card">
            <h2>Current Profile</h2>
            <div className="info-item">
              <strong>Name:</strong> {user.name}
            </div>
            <div className="info-item">
              <strong>Email:</strong> {user.email}
            </div>
            <div className="info-item">
              <strong>Role:</strong> <span style={{ textTransform: 'capitalize' }}>{user.role}</span>
            </div>
            <div className="info-item">
              <strong>Work Experience Level:</strong> 
              <span style={{ 
                textTransform: 'capitalize', 
                fontWeight: '600', 
                color: '#6366f1',
                marginLeft: '0.5rem'
              }}>
                {user.position === 'basic' ? 'Beginner' : user.position === 'intermediate' ? 'Intermediate' : 'Expert'}
              </span>
            </div>
            <div className="info-item">
              <strong>Session ID:</strong> {user.conversationId}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Profile;
