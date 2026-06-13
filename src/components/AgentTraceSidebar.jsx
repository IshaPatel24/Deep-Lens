import React from 'react';
import { Play, CheckCircle2, AlertCircle, RefreshCw, Layers } from 'lucide-react';

const AGENTS_CONFIG = [
  { id: 'Planner', label: 'Planner Agent', desc: 'Breaks query into non-overlapping research angles' },
  { id: 'Searcher', label: 'Search Agent', desc: 'Generates queries & performs search fetches' },
  { id: 'Source Evaluator', label: 'Source Evaluator', desc: 'Appraises source trust, recency, and bias' },
  { id: 'Extractor', label: 'Reader/Extractor', desc: 'Fetches page texts and extracts raw claims' },
  { id: 'Verifier', label: 'Verifier Agent', desc: 'Cross-checks facts and maps contradictions' },
  { id: 'Writer', label: 'Writer Agent', desc: 'Synthesizes report sections and citations' },
  { id: 'Critic', label: 'Critic Agent', desc: 'Factual sanity check & loop feedback' },
  { id: 'DeepLens System', label: 'Research Completed', desc: 'Finalizing formatting and outputs' }
];

export default function AgentTraceSidebar({ traceLogs }) {
  // Find current active log state per agent
  const getAgentStatus = (agentId) => {
    const logs = traceLogs.filter(log => log.agent === agentId);
    if (logs.length === 0) return { state: 'idle', details: null, time: null };
    
    // Sort by timestamp desc to find last status
    const sorted = [...logs].sort((a, b) => b.timestamp - a.timestamp);
    const last = sorted[0];
    
    return {
      state: last.status, // running, completed, revision_required, failed
      details: last.details,
      time: new Date(last.timestamp * 1000).toLocaleTimeString()
    };
  };

  const isPipelineStarted = traceLogs.length > 0;

  return (
    <div className="glass-panel rounded-2xl p-6 border border-white/5 shadow-2xl h-full flex flex-col">
      <div className="flex items-center gap-2 mb-6 pb-4 border-b border-white/5">
        <Layers className="w-5 h-5 text-accent-cyan" />
        <h3 className="font-semibold text-lg text-slate-100">Live Agent Activity Trace</h3>
      </div>

      {!isPipelineStarted ? (
        <div className="flex-1 flex flex-col items-center justify-center text-center p-8">
          <div className="w-12 h-12 rounded-full border border-dashed border-slate-700 flex items-center justify-center text-slate-500 mb-4 animate-pulse-slow">
            <Play className="w-5 h-5" />
          </div>
          <p className="text-sm text-slate-500 max-w-[200px]">
            Launch a research run to view the agentic workflow logs in real-time.
          </p>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto space-y-6 pr-2">
          {AGENTS_CONFIG.map((agent, index) => {
            const { state, details, time } = getAgentStatus(agent.id);
            
            // Visual styles based on agent state
            let icon = <div className="w-2.5 h-2.5 rounded-full bg-slate-700" />;
            let borderStyle = 'border-slate-800 bg-dark-card';
            let titleStyle = 'text-slate-500';
            
            if (state === 'running') {
              icon = <RefreshCw className="w-4 h-4 text-accent-cyan animate-spin" />;
              borderStyle = 'border-accent-cyan/40 bg-accent-cyan/5 shadow-lg shadow-accent-cyan/5';
              titleStyle = 'text-accent-cyan font-semibold';
            } else if (state === 'completed') {
              icon = <CheckCircle2 className="w-4.5 h-4.5 text-accent-emerald" />;
              borderStyle = 'border-accent-emerald/30 bg-accent-emerald/5';
              titleStyle = 'text-slate-200';
            } else if (state === 'failed') {
              icon = <AlertCircle className="w-4.5 h-4.5 text-accent-crimson" />;
              borderStyle = 'border-accent-crimson/30 bg-accent-crimson/5';
              titleStyle = 'text-accent-crimson';
            } else if (state === 'revision_required') {
              icon = <RefreshCw className="w-4 h-4 text-accent-amber animate-spin" />;
              borderStyle = 'border-accent-amber/30 bg-accent-amber/5';
              titleStyle = 'text-accent-amber font-semibold';
            }

            return (
              <div 
                key={agent.id} 
                className={`relative flex gap-4 p-3 rounded-xl border transition-all duration-300 ${borderStyle}`}
              >
                {/* Vertical connecting line */}
                {index < AGENTS_CONFIG.length - 1 && (
                  <div className="absolute left-[23px] top-[40px] bottom-[-24px] w-0.5 bg-slate-800" />
                )}
                
                {/* Status Indicator */}
                <div className="flex items-start justify-center pt-0.5 z-10 w-5">
                  {icon}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0 text-left">
                  <div className="flex justify-between items-center gap-2 mb-1">
                    <span className={`text-sm ${titleStyle}`}>{agent.label}</span>
                    {time && <span className="text-[10px] font-mono text-slate-500">{time}</span>}
                  </div>
                  <p className="text-xs text-slate-400 mb-2">{agent.desc}</p>
                  
                  {/* Detailed runtime messages */}
                  {state !== 'idle' && details && (
                    <div className="mt-2 bg-dark-bg/60 rounded-lg p-2.5 border border-white/5 font-mono text-[11px] text-slate-300 overflow-x-auto max-h-40 scrollbar-none">
                      {typeof details === 'string' && (
                        <span>{details}</span>
                      )}
                      
                      {Array.isArray(details) && agent.id === 'Planner' && (
                        <ol className="list-decimal pl-4 space-y-1">
                          {details.map((q, idx) => (
                            <li key={idx}>{q}</li>
                          ))}
                        </ol>
                      )}

                      {typeof details === 'object' && agent.id === 'Source Evaluator' && (
                        <div>
                          <p className="font-bold text-accent-emerald mb-1">
                            Evaluated: {details.considered} | Passed: {details.accepted}
                          </p>
                          <ul className="space-y-1 text-slate-400">
                            {details.sources?.slice(0, 3).map((s, idx) => (
                              <li key={idx} className="truncate">
                                [{s.score}/10] {s.url}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {typeof details === 'object' && agent.id === 'Extractor' && (
                        <p>Extracted {details.total_claims} factual claims from source texts.</p>
                      )}

                      {typeof details === 'object' && agent.id === 'Verifier' && (
                        <div className="space-y-1">
                          <p className="font-bold text-accent-cyan">Verification Summary:</p>
                          <p>✅ {details.verified} Multi-source Verified</p>
                          <p>⚠️ {details.single_source} Single-source Claims</p>
                          <p>🚨 {details.contradictions} Contradictions Detected</p>
                        </div>
                      )}

                      {typeof details === 'object' && agent.id === 'Writer' && (
                        <p>Structured report drafted successfully (Loop {details.loop}).</p>
                      )}

                      {typeof details === 'object' && agent.id === 'Critic' && (
                        <div className="text-accent-amber">
                          <p className="font-semibold">Critic Revision Flags:</p>
                          <p>{details.feedback}</p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
