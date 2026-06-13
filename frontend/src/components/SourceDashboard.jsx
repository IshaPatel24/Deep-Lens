import React from 'react';
import { Award, Compass, EyeOff, ShieldCheck, Star } from 'lucide-react';

export default function SourceDashboard({ sources, discardedCount }) {
  const totalCount = (sources?.length || 0) + (discardedCount || 0);
  const acceptedCount = sources?.length || 0;
  const acceptanceRate = totalCount > 0 ? Math.round((acceptedCount / totalCount) * 100) : 100;

  return (
    <div className="glass-panel rounded-2xl p-6 border border-white/5 shadow-2xl mb-8">
      <div className="flex items-center gap-2.5 mb-6 pb-4 border-b border-white/5">
        <Award className="w-5 h-5 text-accent-cyan" />
        <h3 className="font-semibold text-lg text-slate-100">Source Quality & Transparency Dashboard</h3>
      </div>

      {/* Grid of stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-dark-card/50 border border-white/5 rounded-xl p-4 text-center">
          <span className="text-xs text-slate-500 block mb-1">Total Sources Analyzed</span>
          <span className="text-2xl font-bold text-slate-200 font-mono">{totalCount}</span>
        </div>
        <div className="bg-accent-emerald/5 border border-accent-emerald/15 rounded-xl p-4 text-center">
          <span className="text-xs text-slate-500 block mb-1">Accepted Sources</span>
          <span className="text-2xl font-bold text-accent-emerald font-mono">{acceptedCount}</span>
        </div>
        <div className="bg-accent-crimson/5 border border-accent-crimson/15 rounded-xl p-4 text-center">
          <span className="text-xs text-slate-500 block mb-1">Discarded (Score &lt; 4)</span>
          <span className="text-2xl font-bold text-accent-crimson font-mono">{discardedCount || 0}</span>
        </div>
        <div className="bg-primary-500/5 border border-primary-500/15 rounded-xl p-4 text-center">
          <span className="text-xs text-slate-500 block mb-1">Acceptance Rate</span>
          <span className="text-2xl font-bold text-accent-cyan font-mono">{acceptanceRate}%</span>
        </div>
      </div>

      {/* Main split display: Accepted vs Discarded details */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 text-left">
        {/* Accepted Sources List */}
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-accent-emerald mb-3 flex items-center gap-1.5">
            <ShieldCheck className="w-4.5 h-4.5" />
            <span>Trusted Sources List ({acceptedCount})</span>
          </h4>
          
          <div className="space-y-3 max-h-[300px] overflow-y-auto pr-1">
            {sources && sources.length > 0 ? (
              sources.map((src, index) => (
                <div 
                  key={index}
                  className="bg-dark-card/30 border border-white/5 rounded-xl p-3.5 flex items-start gap-3"
                >
                  <div className="bg-accent-emerald/10 border border-accent-emerald/25 text-accent-emerald rounded-lg px-2 py-1 font-mono text-xs font-bold flex flex-col items-center justify-center flex-shrink-0 w-12 h-12">
                    <span className="text-base leading-none">{src.score}</span>
                    <span className="text-[8px] uppercase tracking-wide">Score</span>
                  </div>
                  
                  <div className="min-w-0 flex-1">
                    <a 
                      href={src.url} 
                      target="_blank" 
                      rel="noreferrer" 
                      className="text-xs font-semibold text-slate-300 hover:text-accent-cyan hover:underline truncate block mb-1"
                    >
                      {src.url}
                    </a>
                    <p className="text-[11px] text-slate-450 leading-relaxed">
                      {src.reason}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-500 italic py-4">No sources stored.</p>
            )}
          </div>
        </div>

        {/* Discarded Heuristics explanation */}
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-accent-amber mb-3 flex items-center gap-1.5">
            <EyeOff className="w-4.5 h-4.5" />
            <span>Source Filtering Policy & Discarded Stats</span>
          </h4>
          
          <div className="bg-dark-card/30 border border-white/5 rounded-xl p-4 h-[300px] flex flex-col justify-between">
            <div className="space-y-3.5 text-xs text-slate-350 leading-relaxed">
              <p>
                To preserve report rigor and eliminate hallucinations, DeepLens filters out online references with scores lower than <strong>4 out of 10</strong>.
              </p>
              <ul className="list-disc pl-4 space-y-1.5">
                <li>
                  <strong className="text-slate-200">Authority Penalty:</strong> Personal forums, Reddit, and user blogs are assigned low scores (&lt; 3) and automatically rejected.
                </li>
                <li>
                  <strong className="text-slate-200">Recency Tuning:</strong> Time-sensitive topics deduct points from old pages (older than 2-3 years) to keep facts relevant.
                </li>
                <li>
                  <strong className="text-slate-200">Bias Filter:</strong> Highly promotional product pages or heavily opinionated outlets are discarded or scored lower.
                </li>
              </ul>
            </div>

            <div className="bg-slate-900/40 p-3 rounded-lg border border-white/5 text-[11px] text-slate-450">
              {discardedCount > 0 ? (
                <span>
                  💡 During this run, <strong>{discardedCount}</strong> references were discarded due to low authority or excessive bias.
                </span>
              ) : (
                <span>
                  💡 During this run, all analyzed URLs met the minimum score of 4/10 and were utilized.
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
