import React, { useState, useEffect } from 'react';
import { API_BASE } from './config';
import { Sparkles, History, BarChart2, Compass, LayoutGrid, Clock, ChevronRight, Search, FileDown } from 'lucide-react';
import QueryInput from './components/QueryInput';
import AgentTraceSidebar from './components/AgentTraceSidebar';
import ReportView from './components/ReportView';
import ContradictionPanel from './components/ContradictionPanel';
import SourceDashboard from './components/SourceDashboard';
import EvalDashboard from './components/EvalDashboard';

export default function App() {
  const [activeTab, setActiveTab] = useState('console'); // 'console' | 'history' | 'eval'
  const [isLoading, setIsLoading] = useState(false);
  const [traceLogs, setTraceLogs] = useState([]);
  
  // Current session outputs
  const [currentQuery, setCurrentQuery] = useState('');
  const [currentSessionId, setCurrentSessionId] = useState('');
  const [currentReport, setCurrentReport] = useState('');
  const [currentVerifiedData, setCurrentVerifiedData] = useState([]);
  const [currentSources, setCurrentSources] = useState([]);
  const [currentDiscardedCount, setCurrentDiscardedCount] = useState(0);

  // History sessions list
  const [history, setHistory] = useState([]);

  const fetchHistory = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/history`);
      if (response.ok) {
        const data = await response.json();
        setHistory(data);
      }
    } catch (e) {
      console.error("Failed to fetch history:", e);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleResearchSubmit = async (query, depth) => {
    setIsLoading(true);
    setTraceLogs([]);
    setCurrentReport('');
    setCurrentVerifiedData([]);
    setCurrentSources([]);
    setCurrentDiscardedCount(0);
    setCurrentSessionId('');
    setCurrentQuery(query);
    setActiveTab('console');

    try {
      // Use the combined POST+SSE endpoint (works on both local dev and Vercel serverless)
      const response = await fetch(`${API_BASE}/api/research/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status} — failed to start research stream`);
      }

      // Read SSE events from the fetch response body stream
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      const processStream = async () => {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const parts = buffer.split('\n\n');
          buffer = parts.pop(); // Keep the incomplete last chunk

          for (const part of parts) {
            const line = part.trim();
            if (!line.startsWith('data:')) continue;
            const jsonStr = line.slice(5).trim();
            if (!jsonStr) continue;

            let msg;
            try { msg = JSON.parse(jsonStr); } catch { continue; }
            if (msg.heartbeat) continue;

            // Extract session_id from first message
            if (msg.session_id && !currentSessionId) {
              setCurrentSessionId(msg.session_id);
            }

            setTraceLogs((prev) => [...prev, msg]);

            if (msg.agent === 'DeepLens System') {
              if (msg.status === 'completed') {
                setCurrentSessionId(msg.session_id || '');
                setCurrentReport(msg.details.report);
                setCurrentVerifiedData(msg.details.verified_data);
                setCurrentSources(msg.details.sources);
                setCurrentDiscardedCount(msg.details.discarded_count);
                setIsLoading(false);
                import('canvas-confetti').then((confetti) => {
                  confetti.default({
                    particleCount: 150,
                    spread: 80,
                    origin: { y: 0.6 },
                    colors: ['#00D8F6', '#9F7AEA', '#5A67D8', '#ED64A6']
                  });
                });
                fetchHistory();
                return;
              } else if (msg.status === 'failed') {
                setIsLoading(false);
                alert(`Research pipeline encountered an error: ${msg.details}`);
                return;
              }
            }
          }
        }
        setIsLoading(false);
      };

      processStream().catch((e) => {
        console.error('Stream error:', e);
        setIsLoading(false);
      });

    } catch (e) {
      console.error(e);
      setIsLoading(false);
      alert('Failed to connect to the research backend. Check that the server is running.');
    }
  };

  const loadPastSession = async (sessionId) => {
    setIsLoading(true);
    setActiveTab('console');
    setTraceLogs([]);
    setCurrentReport('');
    setCurrentVerifiedData([]);
    setCurrentSources([]);
    
    try {
      const response = await fetch(`${API_BASE}/api/sessions/${sessionId}`);
      if (response.ok) {
        const data = await response.json();
        setCurrentQuery(data.query);
        setCurrentSessionId(data.id);
        setCurrentReport(data.report);
        setCurrentVerifiedData(data.verified_data);
        setCurrentSources(data.sources);
        setCurrentDiscardedCount(data.discarded_count);
        
        // Force mock complete logs for historical view
        setTraceLogs([
          { agent: "Planner", status: "completed", timestamp: data.timestamp - 40 },
          { agent: "Searcher", status: "completed", timestamp: data.timestamp - 30 },
          { agent: "Source Evaluator", status: "completed", timestamp: data.timestamp - 25 },
          { agent: "Extractor", status: "completed", timestamp: data.timestamp - 15 },
          { agent: "Verifier", status: "completed", timestamp: data.timestamp - 10 },
          { agent: "Writer", status: "completed", timestamp: data.timestamp - 5 },
          { agent: "Critic", status: "completed", timestamp: data.timestamp - 1 },
          { agent: "DeepLens System", status: "completed", timestamp: data.timestamp }
        ]);
      }
    } catch (e) {
      console.error("Failed to load session details:", e);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen text-slate-100 flex flex-col font-sans">
      
      {/* Top Navigation Bar */}
      <header className="glass-panel sticky top-0 z-50 px-6 py-4 flex items-center justify-between border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-primary-600 to-accent-cyan flex items-center justify-center shadow-lg shadow-primary-500/20">
            <Sparkles className="w-5.5 h-5.5 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
              DeepLens
            </h1>
            <span className="text-[10px] text-accent-cyan font-mono leading-none block">
              Autonomous Agentic Research v1.0
            </span>
          </div>
        </div>

        {/* Tab Menus */}
        <nav className="flex gap-1.5 bg-dark-bg/60 p-1 rounded-xl border border-white/5">
          <button
            onClick={() => setActiveTab('console')}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'console'
                ? 'bg-primary-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Compass className="w-4 h-4" />
            <span>Research Console</span>
          </button>
          
          <button
            onClick={() => setActiveTab('history')}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'history'
                ? 'bg-primary-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <History className="w-4 h-4" />
            <span>Past Research</span>
          </button>
          
          <button
            onClick={() => setActiveTab('eval')}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'eval'
                ? 'bg-primary-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <BarChart2 className="w-4 h-4" />
            <span>Eval Dashboard</span>
          </button>
        </nav>
      </header>

      {/* Main Body Containers */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 md:px-8 py-8">
        
        {activeTab === 'console' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            {/* Left Column (Input & Reports) */}
            <div className="lg:col-span-2 space-y-8">
              <QueryInput onSubmit={handleResearchSubmit} isLoading={isLoading} />
              
              {/* Show loading placeholder or finalized report */}
              {isLoading && !currentReport && (
                <div className="glass-panel rounded-2xl p-12 text-center border border-white/5 flex flex-col items-center justify-center min-h-[400px]">
                  <div className="relative w-16 h-16 mb-6">
                    <div className="absolute inset-0 rounded-full border-4 border-slate-800"></div>
                    <div className="absolute inset-0 rounded-full border-4 border-t-accent-cyan animate-spin"></div>
                  </div>
                  <h3 className="text-lg font-semibold text-slate-200 mb-2">DeepLens is Researching</h3>
                  <p className="text-xs text-slate-400 max-w-xs leading-relaxed">
                    Planner, Searcher, and Verifier agents are analyzing sources, extracting facts, and drafting your report. Watch the live trace sidebar!
                  </p>
                </div>
              )}

              {currentReport && (
                <>
                  <ContradictionPanel verifiedData={currentVerifiedData} />
                  <ReportView 
                    report={currentReport} 
                    verifiedData={currentVerifiedData} 
                    sessionId={currentSessionId}
                    query={currentQuery}
                  />
                  <SourceDashboard 
                    sources={currentSources} 
                    discardedCount={currentDiscardedCount} 
                  />
                </>
              )}
            </div>

            {/* Right Column (Agent Logs Sidebar) */}
            <div className="lg:col-span-1">
              <AgentTraceSidebar traceLogs={traceLogs} />
            </div>

          </div>
        )}

        {/* Saved History Tab */}
        {activeTab === 'history' && (
          <div className="glass-panel rounded-2xl p-6 md:p-8 border border-white/5 shadow-2xl text-left">
            <div className="flex items-center gap-2 mb-6 pb-4 border-b border-white/5">
              <Clock className="w-6 h-6 text-accent-cyan" />
              <div>
                <h3 className="font-semibold text-lg text-slate-100">Saved Research History</h3>
                <p className="text-xs text-slate-400">Recall, read, or export reports generated by previous runs.</p>
              </div>
            </div>

            {history.length === 0 ? (
              <div className="py-16 text-center text-slate-500 text-sm">
                No past sessions found. Start a new research run on the console!
              </div>
            ) : (
              <div className="grid gap-4">
                {history.map((session) => (
                  <div 
                    key={session.id}
                    className="bg-dark-card border border-white/5 hover:border-slate-700 rounded-xl p-4.5 flex items-center justify-between transition-all hover:translate-x-1 duration-200 group cursor-pointer"
                    onClick={() => loadPastSession(session.id)}
                  >
                    <div className="min-w-0 flex-1">
                      <h4 className="text-sm font-semibold text-slate-200 group-hover:text-accent-cyan transition-colors truncate">
                        {session.query}
                      </h4>
                      <div className="flex items-center gap-4 text-[10px] text-slate-500 mt-2 font-mono">
                        <span>Session: {session.id.slice(0, 8)}...</span>
                        <span>•</span>
                        <span>Date: {new Date(session.timestamp * 1000).toLocaleString()}</span>
                        <span>•</span>
                        <span>Discarded URLs: {session.discarded_count}</span>
                      </div>
                    </div>
                    
                    <ChevronRight className="w-5 h-5 text-slate-650 group-hover:text-slate-350 transition-colors" />
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Benchmark Dashboard Tab */}
        {activeTab === 'eval' && (
          <EvalDashboard />
        )}

      </main>

      {/* Footer */}
      <footer className="py-6 mt-12 border-t border-white/5 text-center text-xs text-slate-500">
        <p>© 2026 DeepLens — Agentic Research Assistant. Engineered for PS-02.</p>
      </footer>
    </div>
  );
}
