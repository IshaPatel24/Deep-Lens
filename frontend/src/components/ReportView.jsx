import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Download, FileText, FileCode, CheckCircle, HelpCircle, AlertTriangle, ShieldCheck, ExternalLink } from 'lucide-react';

export default function ReportView({ report, verifiedData, sessionId, query }) {
  const [activeTab, setActiveTab] = useState('report'); // 'report' or 'claims'

  const handleExport = (format) => {
    window.open(`http://localhost:8000/api/export/${sessionId}/${format}`, '_blank');
  };

  // Group claims by confidence
  const highConfClaims = verifiedData?.filter(g => g.confidence === 'high' || g.status === 'verified') || [];
  const medConfClaims = verifiedData?.filter(g => g.confidence === 'medium' || g.status === 'single-source') || [];
  const lowConfClaims = verifiedData?.filter(g => g.confidence === 'low' || g.status === 'contradiction') || [];

  return (
    <div className="glass-panel rounded-2xl border border-white/5 shadow-2xl overflow-hidden mb-8">
      {/* Header and Toolbar */}
      <div className="bg-dark-card/90 px-6 py-4 border-b border-white/5 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <span className="text-[10px] font-mono uppercase tracking-wider text-accent-cyan bg-accent-cyan/10 px-2 py-0.5 rounded border border-accent-cyan/25">
            Research Result
          </span>
          <h3 className="font-semibold text-lg text-slate-100 mt-1 truncate max-w-md">
            {query}
          </h3>
        </div>
        
        {/* Export Buttons */}
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => handleExport('pdf')}
            className="flex items-center gap-1.5 text-xs bg-dark-bg hover:bg-dark-hover text-slate-300 px-3.5 py-2 rounded-lg border border-slate-700 hover:border-slate-500 transition-all shadow"
          >
            <Download className="w-3.5 h-3.5 text-accent-pink" />
            <span>PDF</span>
          </button>
          <button
            onClick={() => handleExport('docx')}
            className="flex items-center gap-1.5 text-xs bg-dark-bg hover:bg-dark-hover text-slate-300 px-3.5 py-2 rounded-lg border border-slate-700 hover:border-slate-500 transition-all shadow"
          >
            <FileText className="w-3.5 h-3.5 text-primary-500" />
            <span>Word (DOCX)</span>
          </button>
          <button
            onClick={() => handleExport('markdown')}
            className="flex items-center gap-1.5 text-xs bg-dark-bg hover:bg-dark-hover text-slate-300 px-3.5 py-2 rounded-lg border border-slate-700 hover:border-slate-500 transition-all shadow"
          >
            <FileCode className="w-3.5 h-3.5 text-accent-cyan" />
            <span>MD</span>
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-dark-card/40 border-b border-white/5 flex">
        <button
          onClick={() => setActiveTab('report')}
          className={`px-6 py-3.5 text-sm font-medium border-b-2 transition-all ${
            activeTab === 'report' 
              ? 'border-primary-500 text-slate-100 bg-white/5' 
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Research Report
        </button>
        <button
          onClick={() => setActiveTab('claims')}
          className={`px-6 py-3.5 text-sm font-medium border-b-2 transition-all flex items-center gap-2 ${
            activeTab === 'claims' 
              ? 'border-primary-500 text-slate-100 bg-white/5' 
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <span>Confidence Map</span>
          <span className="text-[10px] font-mono px-2 py-0.5 bg-slate-800 text-slate-300 rounded-full">
            {verifiedData?.length || 0} Claims
          </span>
        </button>
      </div>

      {/* Content Area */}
      <div className="p-6 md:p-8 min-h-[500px]">
        {activeTab === 'report' ? (
          <article className="prose prose-invert max-w-none text-left space-y-6">
            <ReactMarkdown 
              components={{
                h1: ({node, ...props}) => <h1 className="text-2xl font-bold border-b border-slate-800 pb-3 text-slate-100" {...props} />,
                h2: ({node, ...props}) => <h2 className="text-xl font-semibold text-slate-200 mt-6 mb-3 flex items-center gap-2" {...props} />,
                h3: ({node, ...props}) => <h3 className="text-lg font-medium text-slate-300 mt-4 mb-2" {...props} />,
                p: ({node, ...props}) => <p className="text-sm text-slate-300 leading-relaxed my-3" {...props} />,
                ul: ({node, ...props}) => <ul className="list-disc pl-5 my-3 space-y-1 text-sm text-slate-350" {...props} />,
                ol: ({node, ...props}) => <ol className="list-decimal pl-5 my-3 space-y-1 text-sm text-slate-350" {...props} />,
                li: ({node, ...props}) => <li className="my-1" {...props} />,
                code: ({node, inline, ...props}) => 
                  inline 
                    ? <code className="bg-slate-800 text-accent-cyan px-1.5 py-0.5 rounded font-mono text-xs" {...props} />
                    : <pre className="bg-dark-bg/80 border border-white/5 rounded-xl p-4 overflow-x-auto font-mono text-xs text-slate-200" {...props} />,
                a: ({node, ...props}) => <a className="text-primary-500 hover:underline hover:text-primary-600 inline-flex items-center gap-0.5" target="_blank" rel="noreferrer" {...props} />
              }}
            >
              {report}
            </ReactMarkdown>
          </article>
        ) : (
          <div className="space-y-6">
            <div className="flex items-center gap-2 mb-4 bg-slate-900/50 p-4 rounded-xl border border-white/5">
              <ShieldCheck className="w-5 h-5 text-accent-cyan" />
              <p className="text-xs text-slate-400">
                The Confidence Map displays claims cross-verified across independent sources. High-confidence claims are backed by multiple resources, medium-confidence by a single source, and contradictions are highlighted below.
              </p>
            </div>

            {/* Claims list grouped by confidence */}
            <div className="space-y-4 text-left">
              {/* High Confidence */}
              {highConfClaims.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-accent-emerald mb-2 flex items-center gap-1.5">
                    <CheckCircle className="w-4 h-4" />
                    <span>High Confidence Claims (Verified — {highConfClaims.length})</span>
                  </h4>
                  <div className="grid gap-3">
                    {highConfClaims.map((item, idx) => (
                      <div key={idx} className="bg-accent-emerald/5 border border-accent-emerald/20 rounded-xl p-4">
                        <span className="text-xs font-semibold text-slate-200 block mb-1">{item.topic}</span>
                        <ul className="space-y-2">
                          {item.claims.map((c, cIdx) => (
                            <li key={cIdx} className="text-sm text-slate-300">
                              <p className="italic">"{c.claim}"</p>
                              <div className="mt-2 flex items-center gap-3 text-xs text-slate-500">
                                <span className="text-accent-emerald font-semibold">Verified Source:</span>
                                <a href={c.source_url} target="_blank" rel="noreferrer" className="hover:underline hover:text-slate-300 flex items-center gap-0.5 truncate max-w-[250px]">
                                  {c.source_url} <ExternalLink className="w-3 h-3" />
                                </a>
                              </div>
                            </li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Medium Confidence */}
              {medConfClaims.length > 0 && (
                <div className="mt-6">
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-accent-amber mb-2 flex items-center gap-1.5">
                    <HelpCircle className="w-4 h-4" />
                    <span>Medium Confidence Claims (Single Source — {medConfClaims.length})</span>
                  </h4>
                  <div className="grid gap-3">
                    {medConfClaims.map((item, idx) => (
                      <div key={idx} className="bg-accent-amber/5 border border-accent-amber/20 rounded-xl p-4">
                        <span className="text-xs font-semibold text-slate-200 block mb-1">{item.topic}</span>
                        {item.claims.map((c, cIdx) => (
                          <div key={cIdx} className="text-sm text-slate-300">
                            <p className="italic">"{c.claim}"</p>
                            <div className="mt-2 flex items-center gap-3 text-xs text-slate-500">
                              <span className="text-accent-amber font-semibold">Source URL:</span>
                              <a href={c.source_url} target="_blank" rel="noreferrer" className="hover:underline hover:text-slate-300 flex items-center gap-0.5 truncate max-w-[250px]">
                                {c.source_url} <ExternalLink className="w-3 h-3" />
                              </a>
                            </div>
                          </div>
                        ))}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Low Confidence */}
              {lowConfClaims.length > 0 && (
                <div className="mt-6">
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-accent-crimson mb-2 flex items-center gap-1.5">
                    <AlertTriangle className="w-4 h-4" />
                    <span>Low Confidence Claims (Contradiction — {lowConfClaims.length})</span>
                  </h4>
                  <div className="grid gap-3">
                    {lowConfClaims.map((item, idx) => (
                      <div key={idx} className="bg-accent-crimson/5 border border-accent-crimson/20 rounded-xl p-4">
                        <span className="text-xs font-semibold text-slate-200 block mb-1">{item.topic}</span>
                        <div className="grid gap-4 mt-2">
                          {item.claims.map((c, cIdx) => (
                            <div key={cIdx} className="border-l-2 border-accent-crimson/50 pl-3">
                              <p className="text-sm text-slate-300">"{c.claim}"</p>
                              <div className="mt-2 flex items-center gap-3 text-xs text-slate-500">
                                <span className="text-accent-crimson font-semibold">Source:</span>
                                <a href={c.source_url} target="_blank" rel="noreferrer" className="hover:underline hover:text-slate-300 flex items-center gap-0.5 truncate max-w-[250px]">
                                  {c.source_url} <ExternalLink className="w-3 h-3" />
                                </a>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
