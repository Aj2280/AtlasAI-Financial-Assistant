import React, { useState, useEffect } from 'react';
import { Search, Sparkles, TrendingUp, PieChart, FileText, Briefcase, Calendar, Zap, ArrowRight } from 'lucide-react';

export default function CommandPalette({ isOpen, onClose, onSelectAction }) {
  const [query, setQuery] = useState('');

  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        onClose(false);
      }
      if (e.key === 'Escape') {
        onClose(true);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  if (!isOpen) return null;

  const actions = [
    { label: "Analyze Nvidia (NVDA)", category: "Asset Analysis", icon: TrendingUp, action: () => onSelectAction("prompt", "Analyze Nvidia (NVDA) valuation and gross margin trajectory") },
    { label: "Compare Microsoft & Google", category: "Comparative Matrix", icon: Sparkles, action: () => onSelectAction("prompt", "Compare Microsoft and Google from an investment perspective based on revenue growth, profitability, and valuation.") },
    { label: "Track Tesla & SEC Filings", category: "Action Trigger", icon: Zap, action: () => onSelectAction("prompt", "Track Tesla and notify me whenever there's a major announcement or SEC filing.") },
    { label: "Schedule Team Earnings Meeting", category: "Calendar Action", icon: Calendar, action: () => onSelectAction("prompt", "Schedule a meeting with my team tomorrow at 10 AM to discuss this earnings report.") },
    { label: "Open 11 GICS Sectors Heatmap", category: "Navigation", icon: PieChart, action: () => onSelectAction("tab", "sectors") },
    { label: "Open 10-K & Deck Intelligence", category: "Navigation", icon: FileText, action: () => onSelectAction("tab", "documents") },
    { label: "Open Portfolio Holdings Manager", category: "Navigation", icon: Briefcase, action: () => onSelectAction("tab", "portfolio") },
    { label: "Generate Morning Market Brief", category: "Macro Intelligence", icon: Sparkles, action: () => onSelectAction("brief", null) }
  ];

  const filtered = actions.filter(a => a.label.toLowerCase().includes(query.toLowerCase()) || a.category.toLowerCase().includes(query.toLowerCase()));

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(12px)', display: 'flex', alignItems: 'flex-start', justifyContent: 'center', paddingTop: '12vh', zIndex: 9999 }}>
      <div className="glass" style={{ width: '560px', borderRadius: '16px', background: '#0F131D', border: '1px solid rgba(0, 242, 254, 0.3)', overflow: 'hidden', boxShadow: '0 20px 50px rgba(0,0,0,0.8)' }}>
        
        {/* Search Input */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '1rem 1.25rem', borderBottom: '1px solid var(--border)' }}>
          <Search size={18} color="var(--accent-cyan)" />
          <input
            type="text"
            placeholder="Search tickers, analysis prompts, commands (ESC to close)..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            autoFocus
            style={{ flex: 1, background: 'transparent', border: 'none', color: '#FFF', fontSize: '0.95rem', outline: 'none' }}
          />
          <span style={{ fontSize: '0.7rem', padding: '0.2rem 0.4rem', borderRadius: '4px', background: 'rgba(255,255,255,0.08)', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
            ESC
          </span>
        </div>

        {/* Results List */}
        <div style={{ maxHeight: '340px', overflowY: 'auto', padding: '0.5rem' }}>
          {filtered.length > 0 ? (
            filtered.map((item, idx) => {
              const Icon = item.icon;
              return (
                <div
                  key={idx}
                  onClick={() => { item.action(); onClose(true); }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '0.75rem 1rem',
                    borderRadius: '10px',
                    cursor: 'pointer',
                    transition: 'background 0.15s ease'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.06)'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <div style={{ width: '30px', height: '30px', borderRadius: '8px', background: 'rgba(0, 242, 254, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <Icon size={16} color="var(--accent-cyan)" />
                    </div>
                    <div>
                      <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#FFF' }}>{item.label}</div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{item.category}</div>
                    </div>
                  </div>
                  <ArrowRight size={14} color="var(--text-muted)" />
                </div>
              );
            })
          ) : (
            <div style={{ padding: '1.5rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              No matching commands or tickers found.
            </div>
          )}
        </div>

        <div style={{ padding: '0.6rem 1.25rem', borderTop: '1px solid var(--border)', background: 'rgba(0,0,0,0.3)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
          <span>Tip: Press <code>⌘K</code> anywhere to open Command Palette</span>
          <span>Atlas AI Executive Assistant</span>
        </div>
      </div>
    </div>
  );
}
