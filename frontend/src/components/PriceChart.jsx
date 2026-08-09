import React, { useState, useMemo } from 'react';
import { TrendingUp, TrendingDown, Maximize2, RefreshCw, BarChart2, Activity } from 'lucide-react';

export default function PriceChart({ ticker = 'NVDA', basePrice = 223.96, changePct = 2.27, isUp = true }) {
  const [timeframe, setTimeframe] = useState('1M');
  const [chartType, setChartType] = useState('area'); // 'area' | 'candle'
  const [hoverIndex, setHoverIndex] = useState(null);

  // Generate deterministic realistic historical price points based on ticker and timeframe
  const dataPoints = useMemo(() => {
    const count = timeframe === '1D' ? 30 : timeframe === '1W' ? 40 : timeframe === '1M' ? 50 : 60;
    const points = [];
    let current = basePrice * (timeframe === '1D' ? 0.98 : timeframe === '1M' ? 0.88 : 0.75);
    const volatility = basePrice * 0.015;

    for (let i = 0; i < count; i++) {
      const trend = (i / count) * (basePrice - current) * 0.8;
      const noise = (Math.sin(i * 0.5) + Math.cos(i * 0.8)) * volatility + (Math.random() - 0.45) * volatility;
      const price = Math.max(10, current + trend + noise);
      const high = price + Math.random() * (volatility * 0.6);
      const low = price - Math.random() * (volatility * 0.6);
      const open = i === 0 ? price : points[i - 1].close;
      const close = price;
      const volume = Math.floor(100000 + Math.random() * 900000);
      
      points.push({
        idx: i,
        time: `${i + 1}`,
        open,
        high,
        low,
        close,
        volume,
        ema20: price * (0.98 + Math.sin(i * 0.2) * 0.01),
        ema50: price * (0.95 + Math.cos(i * 0.1) * 0.02)
      });
    }
    // Ensure last point matches live price
    if (points.length > 0) {
      points[points.length - 1].close = basePrice;
    }
    return points;
  }, [ticker, timeframe, basePrice]);

  const minPrice = useMemo(() => Math.min(...dataPoints.map(d => d.low)) * 0.99, [dataPoints]);
  const maxPrice = useMemo(() => Math.max(...dataPoints.map(d => d.high)) * 1.01, [dataPoints]);
  const maxVolume = useMemo(() => Math.max(...dataPoints.map(d => d.volume)), [dataPoints]);

  const width = 680;
  const height = 260;
  const chartHeight = 180;
  const volumeHeight = 60;

  // Scale functions
  const getX = (idx) => (idx / (dataPoints.length - 1)) * (width - 40) + 20;
  const getY = (price) => chartHeight - ((price - minPrice) / (maxPrice - minPrice)) * (chartHeight - 30) - 15;
  const getVolY = (vol) => height - (vol / maxVolume) * volumeHeight;

  // SVG Area Path
  const areaPath = useMemo(() => {
    if (dataPoints.length === 0) return '';
    const firstX = getX(0);
    const lastX = getX(dataPoints.length - 1);
    const lineParts = dataPoints.map((d, i) => `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getY(d.close)}`).join(' ');
    return `${lineParts} L ${lastX} ${chartHeight} L ${firstX} ${chartHeight} Z`;
  }, [dataPoints, minPrice, maxPrice]);

  const linePath = useMemo(() => {
    return dataPoints.map((d, i) => `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getY(d.close)}`).join(' ');
  }, [dataPoints, minPrice, maxPrice]);

  const ema20Path = useMemo(() => {
    return dataPoints.map((d, i) => `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getY(d.ema20)}`).join(' ');
  }, [dataPoints, minPrice, maxPrice]);

  const currentHoverPoint = hoverIndex !== null && dataPoints[hoverIndex] ? dataPoints[hoverIndex] : dataPoints[dataPoints.length - 1];

  const strokeColor = isUp ? '#10B981' : '#EF4444';
  const gradientId = `grad-${ticker.replace(/[^a-zA-Z0-9]/g, '')}`;

  return (
    <div className="glass-card" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
      
      {/* Chart Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#FFF' }}>{ticker}</h3>
              <span style={{ fontSize: '0.7rem', padding: '0.15rem 0.45rem', borderRadius: '4px', background: 'rgba(0, 242, 254, 0.15)', color: 'var(--accent-cyan)', fontWeight: 700 }}>
                LIVE CANDLES
              </span>
            </div>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem', marginTop: '0.2rem' }}>
              <span style={{ fontSize: '1.4rem', fontWeight: 800, color: '#FFF', fontFamily: 'var(--font-mono)' }}>
                ${currentHoverPoint ? currentHoverPoint.close.toFixed(2) : basePrice.toFixed(2)}
              </span>
              <span style={{ fontSize: '0.8rem', fontWeight: 700, color: isUp ? 'var(--gain)' : 'var(--loss)' }}>
                {changePct >= 0 ? `+${changePct}%` : `${changePct}%`}
              </span>
            </div>
          </div>
        </div>

        {/* Timeframe & Chart Style Selectors */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <div style={{ display: 'flex', background: 'rgba(0,0,0,0.4)', borderRadius: '8px', padding: '0.2rem', border: '1px solid var(--border)' }}>
            {['1D', '1W', '1M', '1Y', 'ALL'].map((tf) => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                style={{
                  padding: '0.25rem 0.55rem',
                  borderRadius: '6px',
                  border: 'none',
                  background: timeframe === tf ? 'rgba(255,255,255,0.12)' : 'transparent',
                  color: timeframe === tf ? '#FFF' : 'var(--text-muted)',
                  fontSize: '0.7rem',
                  fontWeight: 700,
                  cursor: 'pointer'
                }}
              >
                {tf}
              </button>
            ))}
          </div>

          <div style={{ display: 'flex', background: 'rgba(0,0,0,0.4)', borderRadius: '8px', padding: '0.2rem', border: '1px solid var(--border)' }}>
            <button
              onClick={() => setChartType('area')}
              style={{
                padding: '0.25rem 0.5rem',
                borderRadius: '6px',
                border: 'none',
                background: chartType === 'area' ? 'rgba(0, 242, 254, 0.2)' : 'transparent',
                color: chartType === 'area' ? 'var(--accent-cyan)' : 'var(--text-muted)',
                fontSize: '0.7rem',
                fontWeight: 700,
                cursor: 'pointer'
              }}
            >
              Area
            </button>
            <button
              onClick={() => setChartType('candle')}
              style={{
                padding: '0.25rem 0.5rem',
                borderRadius: '6px',
                border: 'none',
                background: chartType === 'candle' ? 'rgba(0, 242, 254, 0.2)' : 'transparent',
                color: chartType === 'candle' ? 'var(--accent-cyan)' : 'var(--text-muted)',
                fontSize: '0.7rem',
                fontWeight: 700,
                cursor: 'pointer'
              }}
            >
              Candles
            </button>
          </div>
        </div>
      </div>

      {/* SVG Chart Surface */}
      <div 
        style={{ width: '100%', height: `${height}px`, position: 'relative', overflow: 'hidden' }}
        onMouseLeave={() => setHoverIndex(null)}
      >
        <svg 
          viewBox={`0 0 ${width} ${height}`} 
          style={{ width: '100%', height: '100%', overflow: 'visible' }}
          onMouseMove={(e) => {
            const rect = e.currentTarget.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const normalizedX = (mouseX / rect.width) * width;
            const idx = Math.min(dataPoints.length - 1, Math.max(0, Math.round(((normalizedX - 20) / (width - 40)) * (dataPoints.length - 1))));
            setHoverIndex(idx);
          }}
        >
          <defs>
            <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={strokeColor} stopOpacity="0.4" />
              <stop offset="60%" stopColor={strokeColor} stopOpacity="0.08" />
              <stop offset="100%" stopColor={strokeColor} stopOpacity="0.0" />
            </linearGradient>
          </defs>

          {/* Grid Lines */}
          <line x1="20" y1={chartHeight * 0.25} x2={width - 20} y2={chartHeight * 0.25} stroke="rgba(255,255,255,0.04)" strokeDasharray="3 3" />
          <line x1="20" y1={chartHeight * 0.5} x2={width - 20} y2={chartHeight * 0.5} stroke="rgba(255,255,255,0.04)" strokeDasharray="3 3" />
          <line x1="20" y1={chartHeight * 0.75} x2={width - 20} y2={chartHeight * 0.75} stroke="rgba(255,255,255,0.04)" strokeDasharray="3 3" />
          <line x1="20" y1={chartHeight} x2={width - 20} y2={chartHeight} stroke="rgba(255,255,255,0.08)" />

          {/* Volume Bars */}
          {dataPoints.map((d, i) => {
            const barX = getX(i) - 2;
            const barY = getVolY(d.volume);
            const barH = height - barY;
            const isGreen = d.close >= d.open;
            return (
              <rect
                key={`vol-${i}`}
                x={barX}
                y={barY}
                width="4"
                height={barH}
                fill={isGreen ? 'rgba(16, 185, 129, 0.25)' : 'rgba(239, 68, 68, 0.25)'}
                rx="1"
              />
            );
          })}

          {chartType === 'area' ? (
            <>
              {/* Area Gradient Fill */}
              <path d={areaPath} fill={`url(#${gradientId})`} />
              
              {/* EMA 20 Moving Average */}
              <path d={ema20Path} fill="none" stroke="rgba(139, 92, 246, 0.4)" strokeWidth="1.5" strokeDasharray="4 2" />
              
              {/* Main Line */}
              <path d={linePath} fill="none" stroke={strokeColor} strokeWidth="2.5" strokeLinecap="round" />
            </>
          ) : (
            <>
              {/* Candlesticks */}
              {dataPoints.map((d, i) => {
                const cx = getX(i);
                const highY = getY(d.high);
                const lowY = getY(d.low);
                const openY = getY(d.open);
                const closeY = getY(d.close);
                const isGreen = d.close >= d.open;
                const bodyY = Math.min(openY, closeY);
                const bodyH = Math.max(2, Math.abs(openY - closeY));
                return (
                  <g key={`candle-${i}`}>
                    {/* Wick */}
                    <line x1={cx} y1={highY} x2={cx} y2={lowY} stroke={isGreen ? 'var(--gain)' : 'var(--loss)'} strokeWidth="1" />
                    {/* Body */}
                    <rect
                      x={cx - 3.5}
                      y={bodyY}
                      width="7"
                      height={bodyH}
                      fill={isGreen ? 'var(--gain)' : 'var(--loss)'}
                      rx="1"
                    />
                  </g>
                );
              })}
            </>
          )}

          {/* Crosshair & Tooltip on Hover */}
          {hoverIndex !== null && dataPoints[hoverIndex] && (
            <g>
              <line 
                x1={getX(hoverIndex)} 
                y1="10" 
                x2={getX(hoverIndex)} 
                y2={height} 
                stroke="rgba(255,255,255,0.3)" 
                strokeDasharray="2 2" 
              />
              <circle 
                cx={getX(hoverIndex)} 
                y={getY(dataPoints[hoverIndex].close)} 
                r="4.5" 
                fill="#FFF" 
                stroke={strokeColor} 
                strokeWidth="2.5" 
              />
            </g>
          )}
        </svg>

        {/* Legend Overlay */}
        <div style={{ position: 'absolute', bottom: '6px', left: '10px', display: 'flex', gap: '1rem', fontSize: '0.65rem', color: 'var(--text-muted)' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: strokeColor }}></span> Price Action
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <span style={{ width: '8px', height: '2px', background: 'rgba(139, 92, 246, 0.7)' }}></span> EMA (20)
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <span style={{ width: '8px', height: '6px', background: 'rgba(16, 185, 129, 0.4)' }}></span> Volume
          </span>
        </div>
      </div>
    </div>
  );
}
