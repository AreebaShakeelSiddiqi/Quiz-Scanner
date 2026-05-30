import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

const API = process.env.REACT_APP_API_URL || 'http://localhost:5001';

function ReportsPage() {
  const [reports, setReports] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const fetchReports = () => {
    setLoading(true);
    axios.get(`${API}/api/reports`)
      .then(r => { setReports(r.data); setLoading(false); })
      .catch(() => setLoading(false));
  };
  React.useEffect(() => { fetchReports(); }, []);
  const clearReports = async () => {
    if (!window.confirm('Clear all reports?')) return;
    await axios.delete(`${API}/api/reports/clear`);
    setReports([]);
  };
  const avgScore = reports.length ? (reports.reduce((a,r) => a + r.percentage, 0) / reports.length).toFixed(1) : null;
  const highest  = reports.length ? Math.max(...reports.map(r => r.percentage)) : null;
  const lowest   = reports.length ? Math.min(...reports.map(r => r.percentage)) : null;
  return (
    <div>
      <div className="page-title">Reports</div>
      <div className="page-sub">Full grading history — {reports.length} scans total</div>
      {reports.length > 0 && (
        <div className="stats-row" style={{marginTop:'20px'}}>
          <div className="stat-card"><div className="stat-label">Total scans</div><div className="stat-val">{reports.length}</div></div>
          <div className="stat-card"><div className="stat-label">Average score</div><div className="stat-val gold">{avgScore}%</div></div>
          <div className="stat-card"><div className="stat-label">Highest</div><div className="stat-val green">{highest}%</div></div>
          <div className="stat-card"><div className="stat-label">Lowest</div><div className="stat-val red">{lowest}%</div></div>
        </div>
      )}
      {loading && <p style={{color:'#555',marginTop:'20px'}}>Loading...</p>}
      {!loading && reports.length === 0 && (
        <div className="card" style={{marginTop:'20px'}}>
          <h3>No reports yet</h3>
          <p style={{color:'#555',fontSize:'14px',marginTop:'8px'}}>Grade some quizzes in the Scanner tab — reports appear here automatically.</p>
        </div>
      )}
      {!loading && reports.length > 0 && (
        <>
          <div style={{display:'flex',gap:'12px',margin:'20px 0',flexWrap:'wrap'}}>
            <button onClick={fetchReports} style={{padding:'8px 18px',background:'#1e1e22',border:'1px solid #2a2a2e',borderRadius:'8px',color:'#e8e6e0',cursor:'pointer',fontSize:'13px'}}>
              Refresh
            </button>
            <a href={`${API}/api/reports/excel`} style={{padding:'8px 18px',background:'#1a3528',border:'1px solid #2a5040',borderRadius:'8px',color:'#6dbf8a',cursor:'pointer',fontSize:'13px',textDecoration:'none',display:'inline-block'}} download>
              Download Excel
            </a>
            <button onClick={clearReports} style={{padding:'8px 18px',background:'#2a1515',border:'1px solid #5a2020',borderRadius:'8px',color:'#e07070',cursor:'pointer',fontSize:'13px'}}>
              Clear All
            </button>
          </div>
          <div className="batch-table-wrap">
            <table className="batch-table">
              <thead>
                <tr><th>Time</th><th>Name</th><th>Reg No</th><th>Set</th><th>Score</th><th>%</th><th>Grade</th><th>✓</th><th>✗</th><th>—</th></tr>
              </thead>
              <tbody>
                {[...reports].reverse().map((r,i) => (
                  <tr key={i}>
                    <td style={{fontSize:'11px',color:'#444'}}>{new Date(r.timestamp).toLocaleString()}</td>
                    <td style={{color:'#e8e6e0'}}>{r.student?.name||'—'}</td>
                    <td style={{fontFamily:'monospace',fontSize:'12px',color:'#c9a96e'}}>{r.student?.reg_no||'—'}</td>
                    <td>{r.set||'—'}</td>
                    <td style={{color:'#e8e6e0',fontWeight:'500'}}>{r.score}/{r.total}</td>
                    <td>{r.percentage}%</td>
                    <td><span className="grade-pill">{r.grade||'—'}</span></td>
                    <td style={{color:'#6dbf8a'}}>{r.correct}</td>
                    <td style={{color:'#e07070'}}>{r.incorrect}</td>
                    <td style={{color:'#555'}}>{r.unattempted}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}

function App() {
  const [mode, setMode] = useState('single');
  const [page, setPage] = useState('scanner');
  const [files, setFiles] = useState([]);
  const [result, setResult] = useState(null);
  const [batchResults, setBatchResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [quizName, setQuizName] = useState('Quiz 1');
  const [excelFile, setExcelFile] = useState('');
  const [dragging, setDragging] = useState(false);
  const [totalScanned, setTotalScanned] = useState(0);
  const [avgScore, setAvgScore] = useState(null);

  const handleDrop = (e) => {
    e.preventDefault(); setDragging(false);
    const dropped = Array.from(e.dataTransfer.files).filter(f => f && (f.type.startsWith('image/') || f.type === 'application/pdf' || f.name.endsWith('.pdf')));
    if (!dropped.length) return;
    setFiles(mode === 'single' ? [dropped[0]] : dropped);
    setResult(null); setBatchResults(null); setError('');
  };
  const handleFileInput = (e) => {
    const selected = Array.from(e.target.files).filter(f => f && (f.type.startsWith('image/') || f.type === 'application/pdf' || f.name.endsWith('.pdf')));
    if (!selected.length) return;
    setFiles(mode === 'single' ? [selected[0]] : selected);
    setResult(null); setBatchResults(null); setError('');
  };
  const processImage = async () => {
    if (!files.length) return setError('Please upload an image first.');
    setLoading(true); setError('');
    try {
      const fd = new FormData();
      fd.append('image', files[0]);
      const res = await axios.post(`${API}/api/process`, fd);
      setResult(res.data);
      setTotalScanned(t => t + 1);
      if (res.data.grade_report) setAvgScore(res.data.grade_report.percentage);
    } catch (e) { setError(e.response?.data?.error || 'Processing failed.'); }
    setLoading(false);
  };
  const processBatch = async () => {
    if (!files.length) return setError('Please upload images first.');
    setLoading(true); setError('');
    try {
      const fd = new FormData();
      files.forEach(f => fd.append('images', f));
      fd.append('quiz_name', quizName);
      const res = await axios.post(`${API}/api/batch`, fd);
      setBatchResults(res.data.results);
      setExcelFile(res.data.excel_file);
      setTotalScanned(t => t + res.data.count);
      const avg = res.data.results.reduce((a,r) => a + r.Percentage, 0) / res.data.results.length;
      setAvgScore(Math.round(avg));
    } catch (e) { setError(e.response?.data?.error || 'Batch failed.'); }
    setLoading(false);
  };
  const bubbleClass = (status) =>
    status === 'correct' ? 'correct' : status === 'incorrect' ? 'incorrect' : status === 'invalid' ? 'invalid' : 'unattempted';

  return (
    <div className="app">
      <div className="sidebar">
        <div className="logo">Quiz<span>Scan</span></div>
        <div className={`nav-item ${page==='scanner'?'active':''}`} onClick={() => setPage('scanner')}>Scanner</div>
        <div className={`nav-item ${page==='reports'?'active':''}`} onClick={() => setPage('reports')}>Reports</div>
        <div className={`nav-item ${page==='students'?'active':''}`} onClick={() => setPage('students')}>Students</div>
        <div className="nav-label">Settings</div>
        <div className={`nav-item ${page==='prefs'?'active':''}`} onClick={() => setPage('prefs')}>Preferences</div>
        <div className={`nav-item ${page==='keys'?'active':''}`} onClick={() => setPage('keys')}>Answer Keys</div>
      </div>
      <div className="main">

        {page === 'reports' && <ReportsPage />}

        {page === 'students' && (
          <div>
            <div className="page-title">Students</div>
            <div className="page-sub">Student records and performance overview</div>
            <div className="card" style={{marginTop:'20px'}}>
              <h3>No students yet</h3>
              <p style={{color:'#555',fontSize:'14px',marginTop:'8px'}}>Student records will appear here after grading.</p>
            </div>
          </div>
        )}

        {page === 'prefs' && (
          <div>
            <div className="page-title">Preferences</div>
            <div className="page-sub">Configure grading settings</div>
            <div className="card" style={{marginTop:'20px'}}>
              <h3>Negative marking</h3>
              <p style={{color:'#555',fontSize:'14px',marginTop:'8px'}}>Currently disabled. Each correct answer = 1 mark.</p>
            </div>
          </div>
        )}

        {page === 'keys' && (
          <div>
            <div className="page-title">Answer Keys</div>
            <div className="page-sub">Manage QR-encoded answer keys</div>
            <div className="card" style={{marginTop:'20px'}}>
              <h3>Keys are embedded in QR codes</h3>
              <p style={{color:'#555',fontSize:'14px',marginTop:'8px'}}>Each quiz sheet carries its own answer key via QR code. No manual entry needed.</p>
            </div>
          </div>
        )}

        {page === 'scanner' && (
          <div>
            <div className="page-title">Quiz Scanner</div>
            <div className="page-sub">Upload a quiz sheet to decode, read, and grade automatically</div>
            <div className="stats-row">
              <div className="stat-card"><div className="stat-label">Scanned today</div><div className="stat-val">{totalScanned||'0'}</div></div>
              <div className="stat-card"><div className="stat-label">Last score</div><div className="stat-val gold">{avgScore?avgScore+'%':'—'}</div></div>
              <div className="stat-card"><div className="stat-label">Status</div><div className="stat-val green">{loading?'Processing':result||batchResults?'Done':'Ready'}</div></div>
              <div className="stat-card"><div className="stat-label">Mode</div><div className="stat-val">{mode==='single'?'Single':'Batch'}</div></div>
            </div>
            <div className="mode-tabs">
              <div className={`tab ${mode==='single'?'active':''}`} onClick={() => { setMode('single'); setFiles([]); setResult(null); }}>Single Quiz</div>
              <div className={`tab ${mode==='batch'?'active':''}`} onClick={() => { setMode('batch'); setFiles([]); setBatchResults(null); }}>Batch Processing</div>
            </div>
            {mode === 'batch' && (
              <div className="quiz-name-input">
                <label>Quiz name:</label>
                <input value={quizName} onChange={e => setQuizName(e.target.value)} placeholder="e.g. Quiz 1" />
              </div>
            )}
            <div
              className={`dropzone-container ${dragging?'dragging':''}`}
              onDragOver={e => { e.preventDefault(); setDragging(true); }}
              onDragLeave={() => setDragging(false)}
              onDrop={handleDrop}
              onClick={() => document.getElementById('fi').click()}
            >
              <input id="fi" type="file" accept="image/*,.pdf,application/pdf" multiple={mode==='batch'} style={{display:'none'}} onChange={handleFileInput} />
              <div className="dz-icon">📄</div>
              <p>Drop your quiz sheet{mode==='batch'?'s':''} here</p>
              <small>Supports JPG, PNG, PDF — QR code must be visible</small>
              <div className="upload-cta">Choose File{mode==='batch'?'s':''}</div>
            </div>
            {files.filter(f=>f).length > 0 && (
              <div className="file-list">
                {files.filter(f=>f).map((f,i) => <span key={i} className="file-tag">📄 {f.name}</span>)}
              </div>
            )}
            <button className="process-btn" onClick={mode==='single'?processImage:processBatch} disabled={loading||!files.filter(f=>f).length}>
              {loading?'Processing...':mode==='single'?'Scan & Grade':'Process Batch'}
            </button>
            {error && <div className="error-box">{error}</div>}
            {result && mode === 'single' && (
              <div className="results">
                <h2>Results</h2>
                <div className="grade-grid">
                  {result.student_info && (
                    <div className="card">
                      <h3>Student</h3>
                      <div className="student-name">{result.student_info.name}</div>
                      <div className="student-reg">{result.student_info.reg_no}</div>
                      {result.answer_key && (
                        <div style={{marginTop:'16px',paddingTop:'14px',borderTop:'1px solid #222'}}>
                          <div style={{fontSize:'12px',color:'#444',marginBottom:'8px'}}>SET {result.answer_key.set} · {result.answer_key.subject}</div>
                          <div className="answer-chips">
                            {Object.entries(result.answer_key.part1||{}).map(([q,a]) => <span key={q} className="answer-chip">{q}:{a}</span>)}
                          </div>
                          <div className="answer-chips" style={{marginTop:'6px'}}>
                            {Object.entries(result.answer_key.part2||{}).map(([q,a]) => <span key={q} className="answer-chip">{q}:{a}</span>)}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                  {result.grade_report && (
                    <div className="card">
                      <h3>Grade</h3>
                      <div className="score-display">
                        <div className="big-grade">{result.grade_report.grade}</div>
                        <div>
                          <div className="score">{result.grade_report.total_marks} / {result.grade_report.total_questions}</div>
                          <div className="percentage">{result.grade_report.percentage}%</div>
                        </div>
                      </div>
                      <div className="stats-mini">
                        <span className="stat-mini correct">✓ {result.grade_report.correct} correct</span>
                        <span className="stat-mini incorrect">✗ {result.grade_report.incorrect} wrong</span>
                        <span className="stat-mini unattempted">— {result.grade_report.unattempted} skipped</span>
                      </div>
                    </div>
                  )}
                  {result.grade_report && ['part1','part2'].map(part => (
                    <div key={part} className="card full-width">
                      <h3>{part==='part1'?'Part I':'Part II'} breakdown</h3>
                      <div className="bubble-grid">
                        {Object.entries(result.grade_report[part]||{}).map(([q,info]) => (
                          <div key={q} className="bubble-cell">
                            <div className="bubble-q">{q}</div>
                            <div className={`bubble ${bubbleClass(info.status)}`}>{info.student||'—'}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                  {result.errors && Object.keys(result.errors).length > 0 && (
                    <div className="card full-width warning">
                      <h3>Processing notes</h3>
                      {Object.entries(result.errors).map(([k,v]) =>
                        <p key={k} style={{fontSize:'13px',color:'#888',marginTop:'6px'}}><strong style={{color:'#c9a96e'}}>{k}:</strong> {v}</p>)}
                    </div>
                  )}
                </div>
              </div>
            )}
            {batchResults && mode === 'batch' && (
              <div className="results">
                <h2>Batch results — {batchResults.length} sheets</h2>
                {excelFile && <a href={`${API}/api/download/${excelFile}`} className="download-btn" download>Download Excel Report</a>}
                <div className="batch-table-wrap">
                  <table className="batch-table">
                    <thead>
                      <tr><th>Name</th><th>Reg No</th><th>Set</th><th>Correct</th><th>Wrong</th><th>Score</th><th>%</th><th>Grade</th></tr>
                    </thead>
                    <tbody>
                      {batchResults.map((r,i) => (
                        <tr key={i}>
                          <td style={{color:'#e8e6e0'}}>{r.Name||'—'}</td>
                          <td style={{fontFamily:'monospace',fontSize:'12px',color:'#c9a96e'}}>{r['Reg No']||'—'}</td>
                          <td>{r.Set||'—'}</td>
                          <td style={{color:'#6dbf8a'}}>{r.Correct}</td>
                          <td style={{color:'#e07070'}}>{r.Incorrect}</td>
                          <td style={{color:'#e8e6e0',fontWeight:'500'}}>{r['Total Marks']}</td>
                          <td>{r.Percentage}%</td>
                          <td><span className="grade-pill">{r.Grade}</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;