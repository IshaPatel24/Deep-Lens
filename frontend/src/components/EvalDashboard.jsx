import React, { useState, useEffect } from 'react';
import { Award, ShieldAlert, Sparkles, RefreshCw, BarChart2, CheckCircle } from 'lucide-react';
import { API_BASE } from '../config';

export default function EvalDashboard() {
  const [evals, setEvals] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchEvals = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/eval`);
      if (response.ok) {
        const data = await response.json();
        setEvals(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvals();
  }, []);

  const handleRunEval = async () => {
    setIsRunning(true);
    try {
      const response = await fetch(`${API_BASE}/api/eval/run`, { method: 'POST' });
      if (response.ok) {
        // Poll for completion or explain to user
        alert("Evaluation benchmark triggered. It will run in the background. Please wait 10-15 seconds and refresh.");
        setTimeout(fetchEvals, 15000);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsRunning(false);
    }
  };

  const latestEval = evals[0];

  return (
    <div className="glass-panel rounded-2xl p-6 md:p-8 border border-white/5 shadow-2xl text-left">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 pb-4 border-b border-white/5">
        <div className="flex items-center gap-2.5">
          <BarChart2 className="w-6 h-6 text-accent-pink animate-pulse-slow" />
          <div>
            <h3 className="font-semibold text-lg text-slate-100">Agent Performance & Evaluation Suite</h3>
            <p className="text-xs text-slate-400">Precision and fact-citation audit dashboard based on benchmark questions.</p>
          </div>
        </div>
        
        <button
          onClick={handleRunEval}
          disabled={isRunning || loading}
          className="flex items-center gap-2 text-xs font-semibold bg-gradient-to-r from-accent-pink to-accent-purple hover:from-pink-500 hover:to-purple-500 text-white px-4 py-2.5 rounded-xl border border-transparent shadow transition-all disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isRunning ? 'animate-spin' : ''}`} />
          <span>{isRunning ? 'Running Eval Suite...' : 'Trigger Benchmark Run'}</span>
        </button>
      </div>

      {loading ? (
        <div className="py-12 text-center text-slate-500 text-sm">
          Loading evaluation metrics...
        </div>
      ) : !latestEval ? (
        <div className="py-12 text-center text-slate-500 text-sm flex flex-col items-center justify-center gap-3">
          <Sparkles className="w-8 h-8 text-slate-650" />
          <p>No evaluations found in database.</p>
          <p className="text-xs text-slate-500">Run a benchmark to evaluate graph precision, citation alignment, and factual recall.</p>
        </div>
      ) : (
        <div className="space-y-8">
          {/* Latest Metric Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Citation Accuracy */}
            <div className="bg-dark-card border border-white/5 rounded-2xl p-6 flex items-center justify-between relative overflow-hidden">
              <div className="absolute top-0 right-0 w-24 h-24 bg-accent-emerald/5 rounded-full blur-2xl pointer-events-none"></div>
              <div>
                <span className="text-xs text-slate-500 block mb-1">Avg Citation Accuracy</span>
                <span className="text-3xl font-extrabold text-accent-emerald font-mono">
                  {latestEval.score_citation}%
                </span>
                <span className="text-[10px] text-slate-450 block mt-2">
                  Verifies cited facts align with source URLs
                </span>
              </div>
              <div className="p-3 bg-accent-emerald/15 text-accent-emerald rounded-2xl">
                <CheckCircle className="w-7 h-7" />
              </div>
            </div>

            {/* Claim Coverage */}
            <div className="bg-dark-card border border-white/5 rounded-2xl p-6 flex items-center justify-between relative overflow-hidden">
              <div className="absolute top-0 right-0 w-24 h-24 bg-accent-cyan/5 rounded-full blur-2xl pointer-events-none"></div>
              <div>
                <span className="text-xs text-slate-500 block mb-1">Avg Claim Recall</span>
                <span className="text-3xl font-extrabold text-accent-cyan font-mono">
                  {latestEval.score_coverage}%
                </span>
                <span className="text-[10px] text-slate-450 block mt-2">
                  Measures coverage against ground truth facts
                </span>
              </div>
              <div className="p-3 bg-accent-cyan/15 text-accent-cyan rounded-2xl">
                <Sparkles className="w-7 h-7" />
              </div>
            </div>

            {/* Total Latency */}
            <div className="bg-dark-card border border-white/5 rounded-2xl p-6 flex items-center justify-between relative overflow-hidden">
              <div className="absolute top-0 right-0 w-24 h-24 bg-accent-pink/5 rounded-full blur-2xl pointer-events-none"></div>
              <div>
                <span className="text-xs text-slate-500 block mb-1">Suite Processing Latency</span>
                <span className="text-3xl font-extrabold text-accent-pink font-mono">
                  {latestEval.latency_seconds}s
                </span>
                <span className="text-[10px] text-slate-450 block mt-2">
                  Total time to query and verifiy 3 test questions
                </span>
              </div>
              <div className="p-3 bg-accent-pink/15 text-accent-pink rounded-2xl">
                <Award className="w-7 h-7" />
              </div>
            </div>
          </div>

          {/* Test Questions List */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">
              Detailed Benchmark Breakdown (Last Run: {new Date(latestEval.timestamp * 1000).toLocaleString()})
            </h4>
            
            <div className="border border-white/5 rounded-xl overflow-hidden bg-dark-card/30">
              <table className="w-full text-sm text-left border-collapse">
                <thead className="bg-slate-900/60 text-slate-400 text-xs uppercase font-mono">
                  <tr>
                    <th className="px-5 py-4 border-b border-slate-800">Test Question</th>
                    <th className="px-5 py-4 border-b border-slate-800 text-center">Citation Score</th>
                    <th className="px-5 py-4 border-b border-slate-800 text-center">Recall Score</th>
                    <th className="px-5 py-4 border-b border-slate-800 text-right">Time</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800 text-xs">
                  {latestEval.details?.map((res, index) => (
                    <tr key={index} className="hover:bg-white/5 transition-all">
                      <td className="px-5 py-3.5 text-slate-200 font-medium">
                        {res.question}
                      </td>
                      <td className="px-5 py-3.5 text-center font-mono font-semibold text-accent-emerald">
                        {res.citation_accuracy}%
                      </td>
                      <td className="px-5 py-3.5 text-center font-mono font-semibold text-accent-cyan">
                        {res.claim_coverage}%
                      </td>
                      <td className="px-5 py-3.5 text-right font-mono text-slate-400">
                        {res.latency_seconds}s
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
