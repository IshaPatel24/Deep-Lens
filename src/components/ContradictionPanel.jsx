import React from 'react';
import { AlertTriangle, GitFork, ArrowRight, ExternalLink } from 'lucide-react';

export default function ContradictionPanel({ verifiedData }) {
  // Extract only topics with status 'contradiction'
  const contradictions = verifiedData?.filter(g => g.status === 'contradiction') || [];

  if (contradictions.length === 0) {
    return null;
  }

  return (
    <div className="glass-panel rounded-2xl p-6 border border-accent-crimson/20 shadow-2xl relative overflow-hidden mb-8">
      {/* Background soft crimson glow */}
      <div className="absolute -top-10 -left-10 w-32 h-32 bg-accent-crimson/5 rounded-full blur-2xl pointer-events-none"></div>

      <div className="flex items-center gap-3 mb-6">
        <div className="p-2.5 bg-accent-crimson/20 text-accent-crimson rounded-lg border border-accent-crimson/15">
          <AlertTriangle className="w-6 h-6 animate-pulse-slow" />
        </div>
        <div className="text-left">
          <h3 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
            <span>Contradiction Spotlight Panel</span>
            <span className="text-xs bg-accent-crimson/20 text-accent-crimson font-mono font-bold px-2 py-0.5 rounded border border-accent-crimson/30">
              {contradictions.length} Conflict{contradictions.length > 1 ? 's' : ''} Detected
            </span>
          </h3>
          <p className="text-xs text-slate-400">
            Our Verifier Agent flagged points where evaluated sources disagree. Review these side-by-side.
          </p>
        </div>
      </div>

      <div className="space-y-6">
        {contradictions.map((conflict, index) => (
          <div 
            key={index} 
            className="bg-dark-card/60 border border-white/5 rounded-xl p-4 md:p-5 text-left"
          >
            <div className="flex items-center gap-2 mb-4 pb-2 border-b border-white/5">
              <GitFork className="w-4 h-4 text-accent-cyan" />
              <span className="text-sm font-semibold text-slate-200">{conflict.topic}</span>
            </div>

            {/* Split claims list */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {conflict.claims.map((c, cIdx) => (
                <div 
                  key={cIdx} 
                  className="bg-dark-bg/60 border border-slate-800/80 rounded-lg p-3.5 flex flex-col justify-between"
                >
                  <div>
                    <span className="text-[10px] font-semibold text-slate-500 uppercase block mb-1">
                      Perspective #{cIdx + 1}
                    </span>
                    <p className="text-xs text-slate-350 italic leading-relaxed">
                      "{c.claim}"
                    </p>
                    {c.support_note && (
                      <div className="mt-2 text-[10px] text-slate-500">
                        <span className="font-semibold">Context:</span> "{c.support_note}"
                      </div>
                    )}
                  </div>
                  
                  <div className="mt-3 pt-2 border-t border-white/5 flex justify-between items-center text-[10px]">
                    <span className="text-accent-crimson font-semibold">Source Link:</span>
                    <a 
                      href={c.source_url} 
                      target="_blank" 
                      rel="noreferrer" 
                      className="text-slate-400 hover:text-accent-cyan hover:underline flex items-center gap-0.5 truncate max-w-[180px]"
                    >
                      {c.source_url} <ExternalLink className="w-2.5 h-2.5" />
                    </a>
                  </div>
                </div>
              ))}
            </div>
            
            {/* Resolution hint */}
            <div className="mt-4 bg-accent-amber/5 rounded-lg p-3 border border-accent-amber/10 flex gap-2 text-xs text-slate-450">
              <ArrowRight className="w-4 h-4 text-accent-amber flex-shrink-0 mt-0.5" />
              <span>
                <strong>DeepLens Note:</strong> Both perspectives have been neutrally integrated into the final report references. We recommend verifying these values against primary engineering datasheets when they become available.
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
