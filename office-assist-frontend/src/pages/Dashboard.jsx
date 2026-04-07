import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  CheckCircle,
  Clock,
  FileText,
  ListChecks,
  MessageSquare,
  ShieldAlert,
  Sparkles,
  Upload,
} from 'lucide-react';
import { checkHealth, getEmployeeProgress, getScenarios } from '../services/api';
import './Dashboard.css';

function Dashboard({ user }) {
  const [apiStatus, setApiStatus] = useState('checking');
  const [progress, setProgress] = useState(null);
  const [scenarioCount, setScenarioCount] = useState(0);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        const employeeId = user.email || user.conversationId;
        const [, progressResult, scenarioResult] = await Promise.all([
          checkHealth(),
          getEmployeeProgress(employeeId).catch(() => null),
          getScenarios({ limit: 50 }).catch(() => ({ total_count: 0 })),
        ]);
        if (healthResult) {
          setApiStatus('healthy');
        }
        setProgress(progressResult);
        setScenarioCount(scenarioResult?.total_count || scenarioResult?.scenarios?.length || 0);
      } catch (error) {
        setApiStatus('error');
      }
    };
    loadDashboardData();
  }, [user]);

  const features = [
    {
      icon: MessageSquare,
      title: 'Policy Chat',
      description: 'Ask questions about company policies and get instant AI-powered answers',
      link: '/chat',
      color: '#6366f1',
      metric: '24/7',
      note: 'Instant policy guidance',
    },
    {
      icon: FileText,
      title: 'Task Submission',
      description: 'Submit your training tasks and receive automated grading with feedback',
      link: '/tasks',
      color: '#10b981',
      metric: `${progress?.standard_tasks_completed || 0}`,
      note: 'Completed task count',
    },
    {
      icon: ShieldAlert,
      title: 'Scenario Tasks',
      description: 'Solve real pressure-filled company situations and compare your idea with the actual internal solution',
      link: '/scenarios',
      color: '#f97316',
      metric: `${progress?.scenario_tasks_completed || 0}`,
      note: `${scenarioCount} scenarios available`,
    },
    {
      icon: Upload,
      title: 'Resume Analysis',
      description: 'Upload your resume for AI-powered classification and insights',
      link: '/resume',
      color: '#f59e0b',
      metric: 'PDF',
      note: 'Role-ready assessment',
    },
    {
      icon: Upload,
      title: 'Upload Materials',
      description: 'Upload training materials and policy documents to the knowledge base',
      link: '/materials',
      color: '#8b5cf6',
      metric: 'KB',
      note: 'Knowledge base updates',
    },
  ];

  const overviewStats = [
    { value: `${progress?.total_tasks_completed || 0}`, label: 'Tasks done', accent: '#f3efe6' },
    { value: `${scenarioCount}`, label: 'Scenarios live', accent: '#8d78ff' },
    { value: apiStatus === 'healthy' ? 'Live' : apiStatus === 'checking' ? 'Sync' : 'Sync', label: 'API status', accent: '#1d1d1d' },
    { value: `${progress?.average_score || 0}`, label: 'Avg score', accent: '#f59e0b' },
  ];

  return (
    <div className="dashboard-page">
      <div className="container">
        <div className="dashboard-layout">
          <section className="dashboard-main-column">
            <div className="dashboard-hero card">
              <div className="dashboard-header">
                <div>
                  <span className="eyebrow">Weekly overview</span>
                  <h1>Hello, {user.name}!</h1>
                  <p className="subtitle">A refined workspace for training, policy support, submissions, and resume review.</p>
                </div>
              </div>

              <div className="overview-grid">
                {overviewStats.map((stat) => (
                  <div key={stat.label} className="overview-card">
                    <div className="overview-accent" style={{ background: stat.accent }}></div>
                    <strong>{stat.value}</strong>
                    <span>{stat.label}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="features-grid">
              {features.map((feature) => {
                const Icon = feature.icon;
                return (
                  <Link key={feature.link} to={feature.link} className="feature-card card">
                    <div className="feature-card-top">
                      <div className="feature-icon" style={{ backgroundColor: `${feature.color}20`, color: feature.color }}>
                        <Icon size={28} />
                      </div>
                      <div className="feature-metric">{feature.metric}</div>
                    </div>
                    <h3>{feature.title}</h3>
                    <p>{feature.description}</p>
                    <div className="feature-card-footer">
                      <span className="feature-note">{feature.note}</span>
                      <span className="feature-link">Open <ArrowRight size={16} /></span>
                    </div>
                  </Link>
                );
              })}
            </div>

            <div className="session-info card">
              <div className="section-title-row">
                <div>
                  <span className="eyebrow">Session details</span>
                  <h3>Your workspace context</h3>
                </div>
                <Sparkles size={18} />
              </div>
              <div className="session-details">
                <div className="session-item">
                  <strong>Email</strong>
                  <span>{user.email}</span>
                </div>
                <div className="session-item">
                  <strong>Role</strong>
                  <span>{user.role}</span>
                </div>
                <div className="session-item">
                  <strong>Skill Level</strong>
                  <span className="session-highlight">{user.position}</span>
                </div>
                <div className="session-item">
                  <strong>Session ID</strong>
                  <span className="session-mono">{user.conversationId}</span>
                </div>
                <div className="session-item">
                  <strong>Started</strong>
                  <span>{new Date(user.loginTime).toLocaleString()}</span>
                </div>
                <div className="session-item">
                  <strong>Tasks Completed</strong>
                  <span>{progress?.total_tasks_completed || 0}</span>
                </div>
              </div>
            </div>
          </section>

          <aside className="dashboard-side-column">
            <div className="insight-card card">
              <span className="eyebrow">Focus</span>
              <h3>Learning by real company scenarios</h3>
              <p>New joiners can now work through technical and pressure-heavy project situations, compare with the company’s solution, and build completion history inside the same workspace.</p>
              <div className="insight-ring">
                <div className="ring-core">
                  <strong>{progress?.progress_percentage ? `${Math.round(progress.progress_percentage)}%` : '60%'}</strong>
                  <span>Learning progress</span>
                </div>
              </div>
            </div>

            <div className="mini-card card">
              <span className="eyebrow">Recommendations</span>
              <h3>Suggested next action</h3>
              <p>{apiStatus === 'healthy' ? 'Open a scenario task, draft your response, and then use Policy Chat if you need supporting company context from materials or prior scenarios.' : 'Reconnect the backend first so grading, chat, uploads, and scenario comparisons can respond normally.'}</p>
            </div>

            <div className="mini-card card">
              <span className="eyebrow">Completion snapshot</span>
              <h3>Task breakdown</h3>
              <div className="progress-mini-list">
                <div className="progress-mini-item">
                  <ListChecks size={16} />
                  <span>Standard tasks: {progress?.standard_tasks_completed || 0}</span>
                </div>
                <div className="progress-mini-item">
                  <ShieldAlert size={16} />
                  <span>Scenario tasks: {progress?.scenario_tasks_completed || 0}</span>
                </div>
              </div>
            </div>

          
          </aside>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
