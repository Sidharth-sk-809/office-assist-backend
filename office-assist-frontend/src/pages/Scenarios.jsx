import { useEffect, useState } from 'react';
import { AlertCircle, ArrowRight, BrainCircuit, CheckCircle2, ShieldAlert } from 'lucide-react';
import { getEmployeeProgress, getScenarioDetail, getScenarios, submitScenarioSolution } from '../services/api';
import './Scenarios.css';

function Scenarios({ user }) {
  const employeeId = user.email || user.conversationId;
  const [scenarios, setScenarios] = useState([]);
  const [selectedScenario, setSelectedScenario] = useState(null);
  const [solutionText, setSolutionText] = useState('');
  const [comparison, setComparison] = useState(null);
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setLoading(true);
        const [scenarioData, progressData] = await Promise.all([
          getScenarios({ limit: 20 }),
          getEmployeeProgress(employeeId),
        ]);
        setScenarios(scenarioData.scenarios || []);
        setProgress(progressData);

        if (scenarioData.scenarios?.length) {
          const detail = await getScenarioDetail(scenarioData.scenarios[0].scenario_id);
          setSelectedScenario(detail);
        }
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to load scenarios.');
      } finally {
        setLoading(false);
      }
    };

    loadInitialData();
  }, [employeeId]);

  const handleSelectScenario = async (scenarioId) => {
    try {
      setComparison(null);
      setSolutionText('');
      const detail = await getScenarioDetail(scenarioId);
      setSelectedScenario(detail);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load scenario details.');
    }
  };

  const handleSubmitSolution = async (e) => {
    e.preventDefault();
    if (!selectedScenario || !solutionText.trim() || submitting) return;

    try {
      setSubmitting(true);
      setError('');
      const result = await submitScenarioSolution(selectedScenario.scenario_id, {
        employee_id: employeeId,
        employee_name: user.name,
        solution_text: solutionText.trim(),
      });
      setComparison(result);
      const progressData = await getEmployeeProgress(employeeId);
      setProgress(progressData);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to submit scenario solution.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="scenarios-page">
      <div className="container">
        <div className="scenarios-header">
          <div>
            <span className="eyebrow">Real company pressure cases</span>
            <h1>Scenario Tasks</h1>
            <p>New joiners can solve technical and high-pressure project situations, then compare their approach with how the company actually handled them.</p>
          </div>
          <div className="scenario-summary-card card">
            <strong>{progress?.scenario_tasks_completed || 0}</strong>
            <span>Scenario tasks done</span>
            <small>{progress?.total_tasks_completed || 0} total completed tasks</small>
          </div>
        </div>

        {error && (
          <div className="alert alert-error">
            <AlertCircle size={18} />
            <div>{error}</div>
          </div>
        )}

        <div className="scenarios-layout">
          <aside className="scenario-library card">
            <div className="section-title-row">
              <div>
                <span className="eyebrow">Library</span>
                <h3>Available scenarios</h3>
              </div>
              <ShieldAlert size={18} />
            </div>

            <div className="scenario-list">
              {loading ? (
                <p className="empty-state">Loading scenario library...</p>
              ) : scenarios.length === 0 ? (
                <p className="empty-state">No scenarios uploaded yet.</p>
              ) : (
                scenarios.map((scenario) => (
                  <button
                    key={scenario.scenario_id}
                    type="button"
                    className={`scenario-list-item ${selectedScenario?.scenario_id === scenario.scenario_id ? 'active' : ''}`}
                    onClick={() => handleSelectScenario(scenario.scenario_id)}
                  >
                    <div>
                      <strong>{scenario.title}</strong>
                      <span>{scenario.category} • {scenario.difficulty_level}</span>
                    </div>
                    <div className="scenario-list-meta">
                      <small>{scenario.submission_count || 0} done</small>
                      <ArrowRight size={15} />
                    </div>
                  </button>
                ))
              )}
            </div>
          </aside>

          <section className="scenario-workspace">
            {selectedScenario ? (
              <>
                <div className="scenario-detail card">
                  <div className="section-title-row">
                    <div>
                      <span className="eyebrow">Scenario brief</span>
                      <h3>{selectedScenario.title}</h3>
                    </div>
                    <div className="scenario-badges">
                      <span>{selectedScenario.category}</span>
                      <span>{selectedScenario.difficulty_level}</span>
                    </div>
                  </div>

                  <div className="scenario-detail-grid">
                    <div className="scenario-panel">
                      <h4>Description</h4>
                      <p>{selectedScenario.description}</p>
                    </div>
                    <div className="scenario-panel">
                      <h4>Technical Context</h4>
                      <p>{selectedScenario.technical_context}</p>
                    </div>
                    <div className="scenario-panel">
                      <h4>Challenges Faced</h4>
                      <p>{selectedScenario.challenges_faced}</p>
                    </div>
                  </div>
                </div>

                <div className="scenario-submit card">
                  <div className="section-title-row">
                    <div>
                      <span className="eyebrow">Your response</span>
                      <h3>Propose your solution</h3>
                    </div>
                    <BrainCircuit size={18} />
                  </div>

                  <form onSubmit={handleSubmitSolution} className="scenario-form">
                    <textarea
                      className="input textarea"
                      rows="10"
                      placeholder="Explain how you would handle this situation, including technical decisions, risk handling, communication, and trade-offs."
                      value={solutionText}
                      onChange={(e) => setSolutionText(e.target.value)}
                    />
                    <button type="submit" className="btn btn-primary" disabled={submitting || !solutionText.trim()}>
                      {submitting ? 'Comparing Solution...' : 'Submit Scenario Task'}
                    </button>
                  </form>
                </div>

                {comparison && (
                  <div className="scenario-feedback card fade-in">
                    <div className="section-title-row">
                      <div>
                        <span className="eyebrow">Comparison result</span>
                        <h3>Company vs your approach</h3>
                      </div>
                      <div className="comparison-score">
                        <CheckCircle2 size={18} />
                        <strong>{comparison.score}/100</strong>
                      </div>
                    </div>

                    <div className="scenario-detail-grid">
                      <div className="scenario-panel">
                        <h4>Approach Alignment</h4>
                        <p>{comparison.approach_alignment}</p>
                      </div>
                      <div className="scenario-panel">
                        <h4>Feedback</h4>
                        <p>{comparison.feedback}</p>
                      </div>
                      <div className="scenario-panel">
                        <h4>Strengths</h4>
                        <ul className="scenario-points">
                          {(comparison.strengths || []).map((item, index) => (
                            <li key={`${item}-${index}`}>{item}</li>
                          ))}
                        </ul>
                      </div>
                      <div className="scenario-panel">
                        <h4>Gaps</h4>
                        <ul className="scenario-points">
                          {(comparison.gaps || []).map((item, index) => (
                            <li key={`${item}-${index}`}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="card empty-workspace">
                <p>Select a scenario to begin.</p>
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}

export default Scenarios;
