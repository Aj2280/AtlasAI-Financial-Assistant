import React, { useState } from 'react';
import { PieChart, DollarSign, Layers } from 'lucide-react';

export default function PortfolioDonut({ 
  totalValue = 64250, 
  allocations = [
    { label: 'Mega-Cap Tech', ticker: 'NVDA, MSFT', pct: 45, value: 28912, color: '#00F2FE' },
    { label: 'EV & Mobility', ticker: 'TSLA', pct: 25, value: 16062, color: '#3B82F6' },
    { label: 'Digital Assets', ticker: 'BTC, ETH', pct: 18, value: 11565, color: '#8B5CF6' },
    { label: 'Commodities', ticker: 'GOLD, OIL', pct: 12, value: 7710, color: '#10B981' }
  ] 
}) {
  const [hoveredIdx, setHoveredIdx] = useState(null);

  const radius = 55;
  const strokeWidth = 16;
  const circumference = 2 * Math.PI * radius;

  let cumulativePct = 0;

  return (
    <div className="glass-card" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <PieChart size={16} color="var(--accent-cyan)" />
          <span style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Portfolio Allocation
          </span>
        </div>
        <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#FFF', fontFamily: 'var(--font-mono)' }}>
          ${totalValue.toLocaleString()} Total
        </span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-around', gap: '1rem' }}>
        {/* SVG Donut Chart */}
        <div style={{ position: 'relative', width: '130px', height: '130px', flexShrink: 0 }}>
          <svg width="130" height="130" viewBox="0 0 130 130" style={{ transform: 'rotate(-90deg)' }}>
            {allocations.map((alloc, idx) => {
              const strokeDasharray = `${(alloc.pct / 100) * circumference} ${circumference}`;
              const strokeDashoffset = - (cumulativePct / 100) * circumference;
              cumulativePct += alloc.pct;
              const isHovered = hoveredIdx === idx;

              return (
                <circle
                  key={idx}
                  cx="65"
                  cy="65"
                  r={radius}
                  fill="transparent"
                  stroke={alloc.color}
                  strokeWidth={isHovered ? strokeWidth + 4 : strokeWidth}
                  strokeDasharray={strokeDasharray}
                  strokeDashoffset={strokeDashoffset}
                  style={{
                    transition: 'all 0.3s ease',
                    cursor: 'pointer',
                    opacity: hoveredIdx === null || isHovered ? 1 : 0.4
                  }}
                  onMouseEnter={() => setHoveredIdx(idx)}
                  onMouseLeave={() => setHoveredIdx(null)}
                />
              );
            })}
          </svg>

          {/* Center Text */}
          <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', pointerEvents: 'none' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 800, color: '#FFF', fontFamily: 'var(--font-mono)' }}>
              {hoveredIdx !== null ? `${allocations[hoveredIdx].pct}%` : `${allocations.length} Assets`}
            </span>
            <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>
              {hoveredIdx !== null ? allocations[hoveredIdx].label.slice(0, 10) : 'Diversified'}
            </span>
          </div>
        </div>

        {/* Legend */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', flex: 1 }}>
          {allocations.map((alloc, idx) => (
            <div 
              key={idx}
              style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center', 
                fontSize: '0.75rem',
                cursor: 'pointer',
                opacity: hoveredIdx === null || hoveredIdx === idx ? 1 : 0.5,
                transition: 'opacity 0.2s ease'
              }}
              onMouseEnter={() => setHoveredIdx(idx)}
              onMouseLeave={() => setHoveredIdx(null)}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: alloc.color }}></span>
                <span style={{ color: 'var(--text-secondary)' }}>{alloc.label}</span>
              </div>
              <span style={{ fontWeight: 700, color: '#FFF', fontFamily: 'var(--font-mono)' }}>
                {alloc.pct}%
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
