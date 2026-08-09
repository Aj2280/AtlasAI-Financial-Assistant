import React from 'react';
import { Activity, ShieldCheck, TrendingUp, AlertTriangle, Zap } from 'lucide-react';

export default function MarketGauge({ score = 72, vix = 14.8, advanceRatio = '68% / 32%' }) {
  const getSentimentLabel = (val) => {
    if (val >= 75) return { label: 'Extreme Greed', color: '#10B981' };
    if (val >= 55) return { label: 'Greed', color: '#34D399' };
    if (val >= 45) return { label: 'Neutral', color: '#F59E0B' };
    if (val >= 25) return { label: 'Fear', color: '#F87171' };
    return { label: 'Extreme Fear', color: '#EF4444' };
  };

  const sentiment = getSentimentLabel(score);

  // SVG Gauge Calculations
  const radius = 70;
  const circumference = Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="glass-card" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <Activity size={16} color="var(--accent-cyan)" />
          <span style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Market Pulse & Sentiment
          </span>
        </div>
        <span style={{ fontSize: '0.65rem', padding: '0.15rem 0.45rem', borderRadius: '4px', background: 'rgba(16, 185, 129, 0.15)', color: 'var(--gain)', fontWeight: 700 }}>
          LIVE MOMENTUM
        </span>
      </div>

      {/* Semi-Circle SVG Gauge */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', position: 'relative' }}>
        <svg width="180" height="105" viewBox="0 0 180 105">
          {/* Background Arc */}
          <path
            d="M 20 95 A 70 70 0 0 1 160 95"
            fill="none"
            stroke="rgba(255, 255, 255, 0.08)"
            strokeWidth="14"
            strokeLinecap="round"
          />
          {/* Progress Arc */}
          <path
            d="M 20 95 A 70 70 0 0 1 160 95"
            fill="none"
            stroke={sentiment.color}
            strokeWidth="14"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 0.8s cubic-bezier(0.16, 1, 0.3, 1)' }}
          />
        </svg>

        {/* Center Score */}
        <div style={{ position: 'absolute', bottom: '0', textAlign: 'center' }}>
          <span style={{ fontSize: '1.6rem', fontWeight: 900, color: '#FFF', fontFamily: 'var(--font-mono)' }}>
            {score}
          </span>
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: sentiment.color }}>
            {sentiment.label}
          </div>
        </div>
      </div>

      {/* Market Breadth & Volatility Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.6rem', borderTop: '1px solid rgba(255, 255, 255, 0.06)', paddingTop: '0.75rem', fontSize: '0.75rem' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.15rem' }}>
          <span style={{ color: 'var(--text-muted)' }}>VIX Volatility:</span>
          <strong style={{ color: vix < 20 ? 'var(--gain)' : 'var(--loss)', fontFamily: 'var(--font-mono)' }}>
            {vix} ({vix < 20 ? 'Low Vol' : 'Elevated'})
          </strong>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.15rem' }}>
          <span style={{ color: 'var(--text-muted)' }}>Market Breadth:</span>
          <strong style={{ color: '#FFF', fontFamily: 'var(--font-mono)' }}>
            {advanceRatio}
          </strong>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.15rem' }}>
          <span style={{ color: 'var(--text-muted)' }}>Put/Call Ratio:</span>
          <strong style={{ color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>
            0.78 (Bullish)
          </strong>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.15rem' }}>
          <span style={{ color: 'var(--text-muted)' }}>S&P 500 RSI:</span>
          <strong style={{ color: '#FFF', fontFamily: 'var(--font-mono)' }}>
            62.4 (Neutral)
          </strong>
        </div>
      </div>
    </div>
  );
}
