import React, { useState, useEffect, useRef } from 'react';
import { Volume2, VolumeX, Play, Pause, Mic, Activity } from 'lucide-react';

export default function AudioVisualizer({ textToRead = '', isVoiceInput = false }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const canvasRef = useRef(null);
  const animationRef = useRef(null);

  // Web Speech API Synthesis
  const toggleSpeech = () => {
    if (!('speechSynthesis' in window)) {
      alert('Speech synthesis not supported in this browser.');
      return;
    }

    if (isPlaying) {
      window.speechSynthesis.cancel();
      setIsPlaying(false);
    } else {
      window.speechSynthesis.cancel();
      const cleanText = textToRead.replace(/[*_`#]/g, '').slice(0, 400);
      const utterance = new SpeechSynthesisUtterance(cleanText);
      utterance.rate = 1.05;
      utterance.pitch = 1.0;

      utterance.onend = () => setIsPlaying(false);
      utterance.onerror = () => setIsPlaying(false);

      window.speechSynthesis.speak(utterance);
      setIsPlaying(true);
    }
  };

  // Canvas Audio Waveform Animation
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let phase = 0;

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const bars = 18;
      const barWidth = 3;
      const spacing = 4;
      const startX = (canvas.width - (bars * (barWidth + spacing))) / 2;

      for (let i = 0; i < bars; i++) {
        const heightMultiplier = isPlaying || isVoiceInput 
          ? (Math.sin(phase + i * 0.4) * 0.5 + 0.5) * (Math.cos(phase * 0.8 + i * 0.2) * 0.5 + 0.5) 
          : 0.15;
        const barHeight = Math.max(4, heightMultiplier * 20);
        const x = startX + i * (barWidth + spacing);
        const y = (canvas.height - barHeight) / 2;

        const grad = ctx.createLinearGradient(0, y, 0, y + barHeight);
        grad.addColorStop(0, '#00F2FE');
        grad.addColorStop(1, '#6366F1');

        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.roundRect(x, y, barWidth, barHeight, 2);
        ctx.fill();
      }

      phase += 0.12;
      animationRef.current = requestAnimationFrame(render);
    };

    render();

    return () => {
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
      if (window.speechSynthesis) window.speechSynthesis.cancel();
    };
  }, [isPlaying, isVoiceInput]);

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', background: 'rgba(0,0,0,0.3)', padding: '0.3rem 0.6rem', borderRadius: '8px', border: '1px solid var(--border)' }}>
      <canvas ref={canvasRef} width="120" height="24" style={{ display: 'block' }} />

      <button
        onClick={toggleSpeech}
        style={{
          background: isPlaying ? 'rgba(0, 242, 254, 0.2)' : 'transparent',
          border: 'none',
          color: isPlaying ? 'var(--accent-cyan)' : 'var(--text-muted)',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          gap: '0.3rem',
          fontSize: '0.7rem',
          fontWeight: 700,
          padding: '0.2rem 0.4rem',
          borderRadius: '4px'
        }}
        title="Listen to Executive Briefing (Text-to-Speech)"
      >
        <Volume2 size={13} color={isPlaying ? 'var(--accent-cyan)' : 'var(--text-muted)'} />
        <span>{isPlaying ? 'Speaking...' : 'Voice'}</span>
      </button>
    </div>
  );
}
