
import { useState } from 'react'
import './App.css'

function App() {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)


  // Authentication State
  const [authMode, setAuthMode] = useState('login')
  const [authName, setAuthName] = useState('')
  const [authEmail, setAuthEmail] = useState('')
  const [authPassword, setAuthPassword] = useState('')

  const [token, setToken] = useState(
    () => sessionStorage.getItem('smartresume_token') || ''
  )

  const [authLoading, setAuthLoading] = useState(false)
  const [authError, setAuthError] = useState('')
  const [authMessage, setAuthMessage] = useState('')


  // Job Matching State
const [jobDescription, setJobDescription] = useState('')
const [matchingLoading, setMatchingLoading] = useState(false)
const [matchingError, setMatchingError] = useState('')
const [matchResult, setMatchResult] = useState(null)


  // Login and Registration Handler
  const handleAuthSubmit = async (e) => {
    e.preventDefault()

    setAuthLoading(true)
    setAuthError('')
    setAuthMessage('')

    try {
      const isRegister = authMode === 'register'

      const endpoint = isRegister
        ? 'register'
        : 'login'

      const payload = isRegister
        ? {
            name: authName,
            email: authEmail,
            password: authPassword
          }
        : {
            email: authEmail,
            password: authPassword
          }

      const response = await fetch(
        `http://127.0.0.1:8000/${endpoint}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'Authentication failed.'
        )
      }

      if (isRegister) {
        setAuthMessage(
          'Registration successful! Please log in.'
        )
        setAuthMode('login')
        setAuthPassword('')
      } else {
        sessionStorage.setItem(
          'smartresume_token',
          data.access_token
        )

        setToken(data.access_token)
        setAuthPassword('')
        setAuthMessage('Login successful!')
      }

    } catch (err) {
      setAuthError(
        err.message === 'Failed to fetch'
          ? 'Cannot connect to the backend.'
          : err.message
      )
    } finally {
      setAuthLoading(false)
    }
  }

  // Logout Handler
  const handleLogout = () => {
    sessionStorage.removeItem('smartresume_token')
    setToken('')
    setFile(null)
    setResult(null)
    setMatchResult(null)
    setJobDescription('')
    setAuthPassword('')
    setAuthMessage('You have logged out successfully.')
  }


  const handleFileChange = (selectedFile) => {
    setError('')
    setResult(null)

    if (!selectedFile) return

    const validExtension = /\.(pdf|docx)$/i.test(selectedFile.name)

    if (!validExtension) {
      setFile(null)
      setError('Please select a PDF or DOCX resume.')
      return
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
      setFile(null)
      setError('File size must be below 10 MB.')
      return
    }

    setFile(selectedFile)
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a resume first.')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('http://127.0.0.1:8000/upload-resume', {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Resume upload failed.')
      }

      setResult(data)
    } catch (err) {
      setError(
        err.message === 'Failed to fetch'
          ? 'Cannot connect to the backend. Make sure FastAPI is running.'
          : err.message
      )
    } finally {
      setLoading(false)
    }
  }

  const candidate = result?.candidate_information

  const handleJobMatch = async () => {
  if (!result?.extracted_text) {
    setMatchingError('Please upload your resume first.')
    return
  }

  if (!jobDescription.trim()) {
    setMatchingError('Please enter a job description.')
    return
  }

  setMatchingLoading(true)
  setMatchingError('')
  setMatchResult(null)

  try {
    const response = await fetch('http://127.0.0.1:8000/match-job', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        resume_text: result.extracted_text,
        resume_skills: candidate?.skills || [],
        job_description: jobDescription,
      }),
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Job matching failed.')
    }

    setMatchResult(data)
  } catch (err) {
    setMatchingError(
      err.message === 'Failed to fetch'
        ? 'Cannot connect to the backend. Make sure FastAPI is running.'
        : err.message
    )
  } finally {
    setMatchingLoading(false)
  }
}

  const resumeScore = candidate?.score ?? 0
const maximumScore = candidate?.maximum_score ?? 100

const scorePercentage = Math.min(
  100,
  Math.max(0, (resumeScore / maximumScore) * 100)
)

  // Show Login / Register screen when user is logged out
  if (!token) {
    return (
      <div className="auth-page">
        <div className="auth-card">

          <div className="auth-brand">
            <span className="brand-icon">S</span>
            <h2>SmartResume</h2>
          </div>

          <h1>
            {authMode === 'login'
              ? 'Welcome back'
              : 'Create your account'}
          </h1>

          <p className="auth-description">
            {authMode === 'login'
              ? 'Login to access your resume dashboard.'
              : 'Register to start using SmartResume.'}
          </p>

          <form onSubmit={handleAuthSubmit}>

            {authMode === 'register' && (
              <div className="auth-field">
                <label>Full Name</label>
                <input
                  type="text"
                  placeholder="Enter your name"
                  value={authName}
                  onChange={(e) => setAuthName(e.target.value)}
                  minLength={2}
                  maxLength={100}
                  required
                />
              </div>
            )}

            <div className="auth-field">
              <label>Email Address</label>
              <input
                type="email"
                placeholder="Enter your email"
                value={authEmail}
                onChange={(e) => setAuthEmail(e.target.value)}
                required
              />
            </div>

            <div className="auth-field">
              <label>Password</label>
              <input
                type="password"
                placeholder="Enter your password"
                value={authPassword}
                onChange={(e) => setAuthPassword(e.target.value)}
                minLength={8}
                maxLength={128}
                required
              />
            </div>

            {authError && (
              <div className="error-message">
                {authError}
              </div>
            )}

            {authMessage && (
              <div className="auth-success">
                {authMessage}
              </div>
            )}

            <button
              type="submit"
              className="analyze-button"
              disabled={authLoading}
            >
              {authLoading
                ? 'Please wait...'
                : authMode === 'login'
                  ? 'Login to SmartResume'
                  : 'Create Account'}
            </button>

          </form>

          <div className="auth-switch">
            {authMode === 'login'
              ? "Don't have an account?"
              : 'Already have an account?'}

            <button
              type="button"
              onClick={() => {
                setAuthMode(
                  authMode === 'login' ? 'register' : 'login'
                )
                setAuthError('')
                setAuthMessage('')
              }}
            >
              {authMode === 'login'
                ? 'Register'
                : 'Login'}
            </button>
          </div>

        </div>
      </div>
    )
  }


  return (
    <div className="app">
      <nav className="navbar">
        <a className="brand" href="/">
          <span className="brand-icon">S</span>
          <span>SmartResume</span>
        </a>

        <div className="nav-right">
          <span className="nav-status">
            <span className="status-dot"></span>
            AI Resume Analyzer
          </span>
        </div>
      </nav>

      <main className="main-container">
        <section className="hero-section">
          <div className="eyebrow">
            <span>✦</span> SMART RESUME ANALYSIS
          </div>

          <h1>
            Make your resume
            <br />
            <span>work smarter.</span>
          </h1>

          <p className="hero-description">
            Upload your resume and let SmartResume extract your
            information, identify your skills, and organize your
            professional profile.
          </p>
        </section>

        <section className="upload-card">
          <div className="section-heading">
            <div>
              <h2>Upload your resume</h2>
              <p>Start by selecting your resume file.</p>
            </div>
            <span className="step-label">STEP 01</span>
          </div>

          <label className="upload-zone" htmlFor="resume-file">
            <input
              id="resume-file"
              type="file"
              accept=".pdf,.docx"
              onChange={(e) => handleFileChange(e.target.files[0])}
            />

            <div className="upload-icon">
              <svg
                width="30"
                height="30"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.7"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M12 16V4" />
                <path d="m7 9 5-5 5 5" />
                <path d="M20 16.5v2A1.5 1.5 0 0 1 18.5 20h-13A1.5 1.5 0 0 1 4 18.5v-2" />
              </svg>
            </div>

            <h3>Choose a resume to upload</h3>
            <p>Click here to browse files from your computer</p>

            <span className="browse-button">Browse files</span>

            <div className="file-support">
              <span>PDF</span>
              <span>DOCX</span>
              <span>Maximum 10 MB</span>
            </div>
          </label>

          {file && (
            <div className="selected-file">
              <div className="file-icon">
                {file.name.toLowerCase().endsWith('.pdf') ? 'PDF' : 'DOC'}
              </div>

              <div className="file-details">
                <strong>{file.name}</strong>
                <span>{(file.size / (1024 * 1024)).toFixed(2)} MB</span>
              </div>

              <button
                className="remove-file"
                onClick={() => {
                  setFile(null)
                  setResult(null)
                  setError('')
                }}
                aria-label="Remove selected file"
              >
                ×
              </button>
            </div>
          )}

          {error && <div className="error-message">{error}</div>}

          <button
            className="analyze-button"
            onClick={handleUpload}
            disabled={!file || loading}
          >
            {loading ? 'Analyzing resume...' : 'Analyze my resume'}
            {!loading && <span>→</span>}
          </button>

          <p className="privacy-note">
            Your resume is processed by the SmartResume backend.
          </p>
        </section>


{result && candidate && (
  <section className="results-section">
    <div className="results-heading">
      <div>
        <span className="eyebrow">ANALYSIS COMPLETE</span>
        <h2>Your resume profile</h2>
      </div>
      <span className="success-badge">
        ✓ Successfully analyzed
      </span>
    </div>

    {/* Resume Score */}
    <div className="score-card">
      <div className="score-header">
        <div>
          <span className="result-label">RESUME COMPLETENESS</span>
          <h3>Your Resume Score</h3>
          <p>Based on the sections detected in your resume.</p>
        </div>

        <div className="score-number">
          <strong>{resumeScore}</strong>
          <span>/{maximumScore}</span>
        </div>
      </div>

      <div className="score-progress">
        <div
          className="score-progress-fill"
          style={{ width: `${scorePercentage}%` }}
        />
      </div>

      <div className="score-feedback">
        <h4>Improvement suggestions</h4>

        {candidate.feedback?.length ? (
          <ul>
            {candidate.feedback.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        ) : (
          <p>No improvement suggestions available.</p>
        )}
      </div>
    </div>

    {/* Candidate Profile */}
    <div className="profile-card">

{/* Job Description Matching */}
<div className="job-match-card">
  <div className="section-heading">
    <div>
      <h2>Job Description Matching</h2>
      <p>Compare your resume with your target job.</p>
    </div>
    <span className="step-label">STEP 02</span>
  </div>

  <textarea
    className="job-description-input"
    placeholder="Paste the complete job description here..."
    value={jobDescription}
    onChange={(e) => {
      setJobDescription(e.target.value)
      setMatchResult(null)
      setMatchingError('')
    }}
    rows={8}
  />

  {matchingError && (
    <div className="error-message">{matchingError}</div>
  )}

  <button
    className="analyze-button"
    onClick={handleJobMatch}
    disabled={matchingLoading || !jobDescription.trim()}
  >
    {matchingLoading
      ? 'Matching your resume...'
      : 'Analyze Job Match →'}
  </button>

  {matchResult && (
    <div className="job-match-results">
      <div className="match-score-display">
        <span className="result-label">OVERALL JOB MATCH</span>
        <h2>{matchResult.match_score}%</h2>
      </div>

      <div className="match-metrics">
        <div>
          <span className="result-label">SEMANTIC SIMILARITY</span>
          <h3>{matchResult.semantic_score}%</h3>
        </div>

        <div>
          <span className="result-label">SKILL MATCH</span>
          <h3>{matchResult.skill_score}%</h3>
        </div>
      </div>

      <div className="skill-comparison">
        <div>
          <h3>Matched Skills</h3>
          <div className="skill-list">
            {matchResult.matched_skills.length ? (
              matchResult.matched_skills.map((skill, index) => (
                <span className="matched-skill" key={index}>
                  {skill}
                </span>
              ))
            ) : (
              <p>No matching skills found.</p>
            )}
          </div>
        </div>

        <div>
          <h3>Missing Skills</h3>
          <div className="skill-list">
            {matchResult.missing_skills.length ? (
              matchResult.missing_skills.map((skill, index) => (
                <span className="missing-skill" key={index}>
                  {skill}
                </span>
              ))
            ) : (
              <p>No missing skills detected.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )}
</div>

      <div className="profile-avatar">
        {(candidate.name || 'U').charAt(0).toUpperCase()}
      </div>

      <div className="profile-info">
        <h3>{candidate.name || 'Name not detected'}</h3>
        <p>{candidate.email || 'Email not detected'}</p>
        <p>{candidate.phone || 'Phone not detected'}</p>
      </div>
    </div>

    {/* Resume Information */}
    <div className="result-grid">
      <div className="result-card">
        <span className="result-label">TECHNICAL SKILLS</span>
        <h3>{candidate.skills?.length || 0}</h3>

        <div className="skill-list">
          {candidate.skills?.length ? (
            candidate.skills.map((skill, index) => (
              <span className="skill-tag" key={`${skill}-${index}`}>
                {skill}
              </span>
            ))
          ) : (
            <p>No skills detected.</p>
          )}
        </div>

      </div>
      <div className="result-card">
  <span className="result-label">PROJECTS</span>
  <h3>{candidate.projects?.length || 0} projects</h3>

  {candidate.projects?.length ? (
    <ul className="result-list">
      {candidate.projects.map((project, index) => (
        <li key={index}>{project}</li>
      ))}
    </ul>
  ) : (
    <p>No projects detected.</p>
  )}
</div>

      <div className="result-card">
        <span className="result-label">EDUCATION</span>
        <h3>{candidate.education?.length || 0} entries</h3>

        {candidate.education?.length ? (
          <ul className="result-list">
            {candidate.education.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        ) : (
          <p>No education details detected.</p>
        )}
      </div>

      <div className="result-card">
        <span className="result-label">EXPERIENCE</span>
        <h3>
          {candidate.experience_years != null
            ? `${candidate.experience_years} years`
            : 'Not detected'}
        </h3>

        {candidate.experience?.length ? (
          <ul className="result-list">
            {candidate.experience.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        ) : (
          <p>No experience details detected.</p>
        )}
      </div>
    </div>
  </section>
)}


        <footer className="footer">
          <span>SmartResume © 2026</span>
          <span>Built with React and FastAPI</span>
        </footer>
      </main>
    </div>
  )
}

export default App
