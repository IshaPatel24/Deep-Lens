import React, { useState } from 'react';
import { Search, Compass, Sliders, Zap } from 'lucide-react';

const SUGGESTIONS = [
  {
    title: "Solid-State vs Lithium-ion (2026)",
    query: "What are the environmental and economic tradeoffs of solid-state batteries vs lithium-ion for EVs in 2026?"
  },
  {
    title: "Multi-Agent Graph Workflows",
    query: "What is the performance and accuracy difference between LangGraph multi-agent systems and single-prompt agent systems in 2026?"
  }
];

export default function QueryInput({ onSubmit, isLoading }) {
  const [query, setQuery] = useState('');
  const [depth, setDepth] = useState(3);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;
    onSubmit(query.trim(), depth);
  };

  return (
    <div className="glass-panel rounded-2xl p-6 md:p-8 mb-8 border border-white/5 shadow-2xl relative overflow-hidden">
      {/* Decorative background glow */}
      <div className="absolute -top-20 -right-20 w-48 h-48 bg-primary-500/10 rounded-full blur-3xl pointer-events-none"></div>
      
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2.5 bg-primary-600/20 text-accent-cyan rounded-lg">
          <Compass className="w-6 h-6 animate-pulse-slow" />
        </div>
        <div>
          <h2 className="text-xl font-semibold bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
            Ask DeepLens Research Engine
          </h2>
          <p className="text-sm text-slate-400">
            Formulate any research query. DeepLens runs an autonomous agent workflow.
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., What are the economic tradeoffs of solid-state battery packs in 2026?"
            className="w-full bg-dark-bg/60 text-slate-100 placeholder-slate-500 border border-slate-700/80 rounded-xl pl-12 pr-4 py-4 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500/20 transition-all font-sans shadow-inner text-base"
            disabled={isLoading}
          />
          <Search className="absolute left-4 top-4.5 text-slate-500 w-5.5 h-5.5" />
        </div>

        {/* Depth Slider */}
        <div className="bg-dark-bg/30 rounded-xl p-4 border border-white/5 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Sliders className="w-4.5 h-4.5 text-primary-500" />
            <div>
              <span className="text-sm font-medium text-slate-300 block">Research Depth</span>
              <span className="text-xs text-slate-500 block">Controls sub-question expansion count</span>
            </div>
          </div>
          
          <div className="flex items-center gap-4 w-full md:w-64">
            <input
              type="range"
              min="1"
              max="5"
              value={depth}
              onChange={(e) => setDepth(Number(e.target.value))}
              className="w-full accent-primary-500 h-1 bg-slate-700 rounded-lg cursor-pointer"
              disabled={isLoading}
            />
            <span className="text-sm font-mono font-bold text-accent-cyan bg-primary-500/15 px-2.5 py-0.5 rounded-md border border-primary-500/20 w-12 text-center">
              {depth} Qs
            </span>
          </div>
        </div>

        {/* Action Button */}
        <button
          type="submit"
          disabled={isLoading || !query.trim()}
          className="w-full py-4 px-6 rounded-xl bg-gradient-to-r from-primary-600 via-primary-500 to-indigo-600 hover:from-primary-500 hover:to-indigo-500 text-white font-semibold flex items-center justify-center gap-2 shadow-lg shadow-primary-500/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed group"
        >
          <Zap className="w-5 h-5 text-accent-amber fill-accent-amber animate-bounce group-hover:scale-110 transition-transform" />
          {isLoading ? 'Agents Orchestrating...' : 'Launch Autonomous Research'}
        </button>
      </form>

      {/* Suggested Queries */}
      <div className="mt-6 pt-5 border-t border-white/5">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 block mb-3">
          Popular Queries
        </span>
        <div className="flex flex-col gap-2">
          {SUGGESTIONS.map((item, index) => (
            <button
              key={index}
              type="button"
              onClick={() => setQuery(item.query)}
              className="text-left text-sm text-slate-400 hover:text-primary-100 hover:bg-white/5 py-2 px-3.5 rounded-lg border border-transparent hover:border-white/5 transition-all w-full flex items-center justify-between"
              disabled={isLoading}
            >
              <span>{item.title}</span>
              <span className="text-xs text-primary-500 group-hover:underline">Use Query →</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
