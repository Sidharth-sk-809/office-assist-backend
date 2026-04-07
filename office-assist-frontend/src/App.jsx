import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Chat from './pages/Chat';
import TaskSubmission from './pages/TaskSubmission';
import Scenarios from './pages/Scenarios';
import ResumeUpload from './pages/ResumeUpload';
import MaterialsUpload from './pages/MaterialsUpload';
import Profile from './pages/Profile';
import Header, { Topbar } from './components/Header';
import './App.css';

function App() {
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load session from localStorage
    const savedSession = localStorage.getItem('userSession');
    if (savedSession) {
      try {
        setSession(JSON.parse(savedSession));
      } catch (e) {
        localStorage.removeItem('userSession');
      }
    }
    setLoading(false);
  }, []);

  const handleLogin = (userData) => {
    const sessionData = {
      ...userData,
      loginTime: new Date().toISOString(),
      conversationId: `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    };
    setSession(sessionData);
    localStorage.setItem('userSession', JSON.stringify(sessionData));
  };

  const handleLogout = () => {
    setSession(null);
    localStorage.removeItem('userSession');
  };

  const handleUpdateProfile = (updatedData) => {
    const updatedSession = {
      ...session,
      ...updatedData
    };
    setSession(updatedSession);
    localStorage.setItem('userSession', JSON.stringify(updatedSession));
  };

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <Router>
      <div className={`app ${session ? 'app-shell' : 'app-auth'}`}>
        {session && <Header user={session} onLogout={handleLogout} />}
        <main className={session ? 'app-main' : 'app-auth-main'}>
          {session ? (
            <div className="main-shell">
              <Topbar user={session} />
              <div className="page-shell">
                <Routes>
                  <Route 
                    path="/login" 
                    element={session ? <Navigate to="/dashboard" /> : <Login onLogin={handleLogin} />} 
                  />
                  <Route 
                    path="/dashboard" 
                    element={session ? <Dashboard user={session} /> : <Navigate to="/login" />} 
                  />
                  <Route 
                    path="/chat" 
                    element={session ? <Chat user={session} /> : <Navigate to="/login" />} 
                  />
                  <Route 
                    path="/tasks" 
                    element={session ? <TaskSubmission user={session} /> : <Navigate to="/login" />} 
                  />
                  <Route
                    path="/scenarios"
                    element={session ? <Scenarios user={session} /> : <Navigate to="/login" />}
                  />
                  <Route 
                    path="/resume" 
                    element={session ? <ResumeUpload user={session} /> : <Navigate to="/login" />} 
                  />
                  <Route 
                    path="/materials" 
                    element={session ? <MaterialsUpload user={session} /> : <Navigate to="/login" />} 
                  />
                  <Route
                    path="/profile"
                    element={session ? <Profile user={session} onUpdateProfile={handleUpdateProfile} /> : <Navigate to="/login" />}
                  />
                  <Route path="/" element={<Navigate to={session ? "/dashboard" : "/login"} />} />
                </Routes>
              </div>
            </div>
          ) : (
            <Routes>
              <Route 
                path="/login" 
                element={session ? <Navigate to="/dashboard" /> : <Login onLogin={handleLogin} />} 
              />
              <Route 
                path="/dashboard" 
                element={session ? <Dashboard user={session} /> : <Navigate to="/login" />} 
              />
              <Route 
                path="/chat" 
                element={session ? <Chat user={session} /> : <Navigate to="/login" />} 
              />
              <Route 
                path="/tasks" 
                element={session ? <TaskSubmission user={session} /> : <Navigate to="/login" />} 
              />
              <Route
                path="/scenarios"
                element={session ? <Scenarios user={session} /> : <Navigate to="/login" />}
              />
              <Route 
                path="/resume" 
                element={session ? <ResumeUpload user={session} /> : <Navigate to="/login" />} 
              />
              <Route 
                path="/materials" 
                element={session ? <MaterialsUpload user={session} /> : <Navigate to="/login" />} 
              />
              <Route
                path="/profile"
                element={session ? <Profile user={session} onUpdateProfile={handleUpdateProfile} /> : <Navigate to="/login" />}
              />
              <Route path="/" element={<Navigate to={session ? "/dashboard" : "/login"} />} />
            </Routes>
          )}
        </main>
      </div>
    </Router>
  );
}

export default App;
