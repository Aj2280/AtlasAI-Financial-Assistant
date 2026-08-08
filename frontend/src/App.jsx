import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, Mic, Image, FileText, Bot, User, Bell, Sparkles, TrendingUp, 
  Layers, ShieldAlert, Cpu, CheckCircle2, RefreshCw, Plus, Calendar, Table, FileSpreadsheet, SendHorizontal, Key
} from 'lucide-react';

export default function App() {
  const [messages, setMessages] = useState([
    {
      id: '1',
      sender: 'bot',
      channel: 'text',
      content: "Hello! I'm **Atlas**, your conversational financial analyst. I track live stock quotes, SEC EDGAR filings, macro news, and your portfolio memory. What company or sector are we looking at today?",
      intent: 'onboarding',
      sources: ['Atlas Engine v1.0'],
      timestamp: '10:40 AM'
    }
  ]);
  
  const [inputText, setInputText] = useState('');
  const [selectedChannel, setSelectedChannel] = useState('text');
  const [loading, setLoading] = useState(false);
  const [profile, setProfile] = useState(null);
  const [tickerQuery, setTickerQuery] = useState('NVDA');
  const [liveQuote, setLiveQuote] = useState(null);
  const [briefStatus, setBriefStatus] = useState(null);
  const [newTicker, setNewTicker] = useState('');
  const [showTokenModal, setShowTokenModal] = useState(false);
  const [botToken, setBotToken] = useState('');
  const [botConnected, setBotConnected] = useState(false);
  const chatEndRef = useRef(null);

  const telegramId = 1001;

  useEffect(() => {
    fetchProfile();
    fetchLiveQuote('NVDA');
    checkBotStatus();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const checkBotStatus = async () => {
    try {
      const res = await fetch('/api/telegram/bot-status');
      if (res.ok) {
        const data = await res.json();
        setBotConnected(data.connected);
      }
    } catch (e) {
      console.error("Bot status check error", e);
    }
  };

  const handleSetToken = async () => {
    if (!botToken.trim()) return;
    try {
      const res = await fetch('/api/telegram/set-token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bot_token: botToken.trim() })
      });
      if (res.ok) {
        setShowTokenModal(false);
        setBotConnected(true);
        alert("✅ Connected to Real Telegram Bot! Atlas is now live on Telegram.");
      }
    } catch (e) {
      alert("Failed to connect Telegram Bot token");
    }
  };

  const fetchProfile = async () => {
    try {
      const res = await fetch(`/api/profile/${telegramId}`);
      if (res.ok) {
        const data = await res.json();
        setProfile(data);
      }
    } catch (e) {
      console.error("Profile fetch error", e);
    }
  };

  const fetchLiveQuote = async (ticker) => {
    try {
      const res = await fetch(`/api/market/quote/${ticker}`);
      if (res.ok) {
        const data = await res.json();
        setLiveQuote(data);
      }
    } catch (e) {
      console.error("Quote fetch error", e);
    }
  };

  const handleSendMessage = async (textToSend = inputText, channel = selectedChannel) => {
    if (!textToSend.trim() && channel === 'text') return;
    
    const userMsg = {
      id: Date.now().toString(),
      sender: 'user',
      channel: channel,
      content: textToSend || (channel === 'voice' ? '[Voice Note]' : '[Document Photo]'),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    
    setMessages(prev => [...prev, userMsg]);
    setInputText('');
    setLoading(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          telegram_id: telegramId,
          content: textToSend,
          channel: channel
        })
      });

      if (res.ok) {
        const data = await res.json();
        const botMsg = {
          id: (Date.now() + 1).toString(),
          sender: 'bot',
          channel: data.channel,
          content: data.response,
          intent: data.intent,
          sources: data.sources || [],
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        setMessages(prev => [...prev, botMsg]);
        fetchProfile();
      }
    } catch (e) {
      console.error("Send message error", e);
    } finally {
      setLoading(false);
    }
  };

  const triggerDailyBrief = async (force = false) => {
    setLoading(true);
    try {
      const res = await fetch('/api/brief/trigger', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ telegram_id: telegramId, force })
      });
      if (res.ok) {
        const data = await res.json();
        setBriefStatus(data);
        if (data.sent && data.content) {
          const briefMsg = {
            id: Date.now().toString(),
            sender: 'bot',
            channel: 'proactive_brief',
            content: data.content,
            intent: 'proactive_brief',
            sources: ['Proactive Intelligence Engine'],
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          };
          setMessages(prev => [...prev, briefMsg]);
        }
      }
    } catch (e) {
      console.error("Brief trigger error", e);
    } finally {
      setLoading(false);
    }
  };

  const handleAddWatchlist = async () => {
    if (!newTicker.trim()) return;
    try {
      const res = await fetch('/api/watchlist/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ telegram_id: telegramId, ticker: newTicker.trim() })
      });
      if (res.ok) {
        setNewTicker('');
        fetchProfile();
      }
    } catch (e) {
      console.error("Add watchlist error", e);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', backgroundColor: 'var(--bg-dark)' }}>
      
      {/* Top Header */}
      <header className="glass" style={{ padding: '0.85rem 1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border)', zIndex: 10 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ background: 'linear-gradient(135deg, #00F2FE 0%, #4FACFE 100%)', width: '38px', height: '38px', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 15px rgba(0, 242, 254, 0.4)' }}>
            <Cpu size={22} color="#000" />
          </div>
          <div>
            <h1 style={{ fontSize: '1.2rem', fontWeight: 800, letterSpacing: '-0.02em', background: 'linear-gradient(90deg, #FFFFFF, #94A3B8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              ATLAS AI
            </h1>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Conversational Financial Analyst for Telegram
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          
          {/* Real Telegram Status Button */}
          <button 
            onClick={() => setShowTokenModal(true)}
            className="glass-pill"
            style={{ 
              padding: '0.45rem 0.9rem', 
              borderRadius: '8px', 
              border: botConnected ? '1px solid #10B981' : '1px solid var(--accent-cyan)', 
              background: botConnected ? 'rgba(16, 185, 129, 0.15)' : 'rgba(0, 242, 254, 0.1)',
              color: 'var(--text-main)', 
              cursor: 'pointer', 
              display: 'flex', 
              alignItems: 'center', 
              gap: '0.4rem', 
              fontSize: '0.8rem', 
              fontWeight: 600 
            }}
          >
            <SendHorizontal size={14} color={botConnected ? "#10B981" : "var(--accent-cyan)"} />
            <span>{botConnected ? "Real Telegram Bot: ACTIVE" : "Connect Real Telegram Bot"}</span>
          </button>

          <button 
            onClick={() => triggerDailyBrief(false)}
            className="glass-pill"
            style={{ padding: '0.45rem 0.9rem', borderRadius: '8px', border: '1px solid var(--border)', color: 'var(--text-main)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem', fontWeight: 600 }}
          >
            <Bell size={14} color="var(--accent-cyan)" />
            <span>Test Proactive Silence</span>
          </button>
        </div>
      </header>

      {/* Real Telegram Bot Token Modal */}
      {showTokenModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(8px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
          <div className="glass" style={{ width: '480px', padding: '1.75rem', borderRadius: '16px', border: '1px solid var(--border)', background: '#121824' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
              <Key size={20} color="var(--accent-cyan)" />
              <h2 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Connect Real Telegram Bot Token</h2>
            </div>
            
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem', lineHeight: '1.4' }}>
              To connect Atlas to your actual Telegram account:
              <br />1. Search for <b>@BotFather</b> on Telegram.
              <br />2. Send <code>/newbot</code> to create your bot and copy the <b>API Token</b>.
              <br />3. Paste the Bot Token below to activate instant long-polling!
            </p>

            <input 
              type="text"
              placeholder="e.g. 123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ"
              value={botToken}
              onChange={(e) => setBotToken(e.target.value)}
              style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '8px', background: '#090C10', border: '1px solid var(--border)', color: '#FFF', fontSize: '0.85rem', marginBottom: '1.25rem', fontFamily: 'var(--font-mono)' }}
            />

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
              <button 
                onClick={() => setShowTokenModal(false)}
                style={{ padding: '0.5rem 1rem', borderRadius: '8px', background: 'transparent', border: '1px solid var(--border)', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '0.85rem' }}
              >
                Cancel
              </button>
              <button 
                onClick={handleSetToken}
                style={{ padding: '0.5rem 1.25rem', borderRadius: '8px', background: 'linear-gradient(135deg, #00F2FE, #4FACFE)', border: 'none', color: '#000', fontWeight: 700, cursor: 'pointer', fontSize: '0.85rem' }}
              >
                Connect Live Bot
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Content Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', flex: 1, overflow: 'hidden' }}>
        
        {/* Left Column: Telegram Chat Interface */}
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', borderRight: '1px solid var(--border)', background: '#0D1117' }}>
          
          {/* Chat Messages */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            
            {messages.map((msg) => (
              <div 
                key={msg.id}
                style={{
                  display: 'flex',
                  justify: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                  gap: '0.75rem'
                }}
              >
                {msg.sender === 'bot' && (
                  <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'linear-gradient(135deg, #3B82F6, #6366F1)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                    <Bot size={18} color="#FFF" />
                  </div>
                )}

                <div style={{ maxWidth: '80%' }}>
                  <div 
                    style={{
                      padding: '1rem 1.25rem',
                      borderRadius: msg.sender === 'user' ? '16px 16px 2px 16px' : '16px 16px 16px 2px',
                      background: msg.sender === 'user' ? 'linear-gradient(135deg, #2563EB, #1D4ED8)' : 'rgba(22, 30, 46, 0.9)',
                      border: msg.sender === 'user' ? 'none' : '1px solid var(--border)',
                      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
                      color: 'var(--text-main)',
                      fontSize: '0.9rem'
                    }}
                  >
                    {/* Channel & Intent Badges */}
                    {msg.sender === 'bot' && (
                      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem', alignItems: 'center' }}>
                        {msg.intent && (
                          <span style={{ fontSize: '0.65rem', padding: '0.15rem 0.5rem', borderRadius: '4px', background: 'rgba(0, 242, 254, 0.15)', color: 'var(--accent-cyan)', fontWeight: 600, textTransform: 'uppercase' }}>
                            {msg.intent}
                          </span>
                        )}
                        {msg.channel && msg.channel !== 'text' && (
                          <span style={{ fontSize: '0.65rem', padding: '0.15rem 0.5rem', borderRadius: '4px', background: 'rgba(255, 255, 255, 0.1)', color: 'var(--text-muted)' }}>
                            {msg.channel}
                          </span>
                        )}
                      </div>
                    )}

                    {/* Message Body rendering */}
                    <div className="prose-atlas" style={{ whiteSpace: 'pre-wrap' }}>
                      {msg.content}
                    </div>

                    {/* Citations / Sources */}
                    {msg.sources && msg.sources.length > 0 && (
                      <div style={{ marginTop: '0.75rem', paddingTop: '0.5rem', borderTop: '1px solid rgba(255, 255, 255, 0.08)', fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                        <CheckCircle2 size={12} color="var(--accent-cyan)" />
                        <span>Backed by: {msg.sources.join(', ')}</span>
                      </div>
                    )}
                  </div>
                  
                  <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: '0.25rem', display: 'block', textAlign: msg.sender === 'user' ? 'right' : 'left' }}>
                    {msg.timestamp}
                  </span>
                </div>

                {msg.sender === 'user' && (
                  <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: '#334155', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                    <User size={18} color="#94A3B8" />
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'linear-gradient(135deg, #3B82F6, #6366F1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Bot size={18} color="#FFF" />
                </div>
                <div className="glass" style={{ padding: '0.75rem 1.25rem', borderRadius: '16px', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                  <Sparkles size={16} className="animate-pulse-glow" color="var(--accent-cyan)" />
                  <span>Atlas is analyzing real-time financial data & filings...</span>
                </div>
              </div>
            )}

            <div ref={chatEndRef} />
          </div>

          {/* Quick Prompts Bar */}
          <div style={{ padding: '0.5rem 1.5rem', display: 'flex', gap: '0.5rem', overflowX: 'auto', background: 'rgba(0,0,0,0.2)', borderTop: '1px solid var(--border)' }}>
            {[
              { label: "Tell me about Apple", icon: Sparkles, text: "Tell me about Apple" },
              { label: "MSFT vs GOOGL", icon: Table, text: "Compare MSFT vs GOOGL" },
              { label: "Meeting Prep NVDA", icon: Calendar, text: "Prep me for my meeting on NVDA" },
              { label: "10-K Report Risks", icon: FileText, text: "Analyze 10-K report risks" },
              { label: "Sheets Anomaly Review", icon: FileSpreadsheet, text: "Analyze portfolio Google Sheet for anomalies" }
            ].map((qp, i) => {
              const Icon = qp.icon;
              return (
                <button
                  key={i}
                  onClick={() => handleSendMessage(qp.text, 'text')}
                  className="glass-pill"
                  style={{ padding: '0.4rem 0.75rem', borderRadius: '6px', cursor: 'pointer', whiteSpace: 'nowrap', border: '1px solid var(--border)', color: 'var(--text-main)', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}
                >
                  <Icon size={12} color="var(--accent-cyan)" />
                  <span>{qp.label}</span>
                </button>
              );
            })}
          </div>

          {/* Input Controls */}
          <div style={{ padding: '1rem 1.5rem', background: '#090C10', borderTop: '1px solid var(--border)' }}>
            
            {/* Input Channel Selector */}
            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem' }}>
              {[
                { id: 'text', icon: FileText, label: 'Text' },
                { id: 'voice', icon: Mic, label: 'Voice Note (Whisper)' },
                { id: 'image', icon: Image, label: 'Document / OCR' }
              ].map((ch) => {
                const Icon = ch.icon;
                const isSel = selectedChannel === ch.id;
                return (
                  <button
                    key={ch.id}
                    onClick={() => setSelectedChannel(ch.id)}
                    style={{
                      padding: '0.3rem 0.75rem',
                      borderRadius: '6px',
                      border: isSel ? '1px solid var(--accent-cyan)' : '1px solid var(--border)',
                      background: isSel ? 'rgba(0, 242, 254, 0.1)' : 'transparent',
                      color: isSel ? 'var(--accent-cyan)' : 'var(--text-muted)',
                      fontSize: '0.75rem',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.35rem',
                      fontWeight: isSel ? 600 : 400
                    }}
                  >
                    <Icon size={12} />
                    <span>{ch.label}</span>
                  </button>
                );
              })}
            </div>

            {/* Input Form */}
            <form 
              onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }}
              style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}
            >
              <input
                type="text"
                placeholder={
                  selectedChannel === 'voice' ? "Simulate voice note recording..." :
                  selectedChannel === 'image' ? "Upload financial document or chart screenshot..." :
                  "Ask Atlas anything about markets, filings, or your portfolio..."
                }
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                style={{
                  flex: 1,
                  padding: '0.85rem 1rem',
                  borderRadius: '10px',
                  background: 'rgba(18, 24, 36, 0.9)',
                  border: '1px solid var(--border)',
                  color: 'var(--text-main)',
                  fontSize: '0.9rem',
                  outline: 'none'
                }}
              />
              <button
                type="submit"
                disabled={loading}
                style={{
                  padding: '0.85rem 1.25rem',
                  borderRadius: '10px',
                  background: 'linear-gradient(135deg, #00F2FE, #4FACFE)',
                  border: 'none',
                  color: '#000',
                  fontWeight: 700,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  boxShadow: '0 0 15px rgba(0, 242, 254, 0.3)'
                }}
              >
                <span>Send</span>
                <Send size={16} />
              </button>
            </form>
          </div>
        </div>

        {/* Right Sidebar: Real-Time Market & Compounding Memory Inspector */}
        <div style={{ padding: '1.25rem', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1.25rem', background: '#0B0F17' }}>
          
          {/* Live Market Ticker Card */}
          <div className="glass" style={{ padding: '1rem', borderRadius: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <TrendingUp size={16} color="var(--accent-cyan)" />
                <h3 style={{ fontSize: '0.85rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Realtime Market</h3>
              </div>
              <button onClick={() => fetchLiveQuote(tickerQuery)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                <RefreshCw size={14} />
              </button>
            </div>

            {liveQuote && (
              <div>
                <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '1.4rem', fontWeight: 800, fontFamily: 'var(--font-mono)' }}>{liveQuote.ticker}</span>
                  <span style={{ fontSize: '1.2rem', fontWeight: 700, color: liveQuote.change >= 0 ? 'var(--gain)' : 'var(--loss)' }}>
                    ${liveQuote.price}
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                  <span>Prev Close: ${liveQuote.previous_close}</span>
                  <span style={{ color: liveQuote.change >= 0 ? 'var(--gain)' : 'var(--loss)', fontWeight: 600 }}>
                    {liveQuote.change >= 0 ? '+' : ''}{liveQuote.change} ({liveQuote.change_percent}%)
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Proactive Intelligence Status */}
          <div className="glass" style={{ padding: '1rem', borderRadius: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.75rem' }}>
              <ShieldAlert size={16} color="var(--accent-indigo)" />
              <h3 style={{ fontSize: '0.85rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Silence as a Feature</h3>
            </div>
            
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
              Atlas daily brief engine says nothing on quiet days — logging deliberate no-ops to protect your inbox from noise.
            </p>

            <button 
              onClick={() => triggerDailyBrief(true)}
              style={{
                width: '100%',
                padding: '0.5rem',
                borderRadius: '6px',
                background: 'rgba(99, 102, 241, 0.2)',
                border: '1px solid var(--accent-indigo)',
                color: '#FFF',
                fontSize: '0.75rem',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              Simulate Material Event Brief
            </button>

            {briefStatus && (
              <div style={{ marginTop: '0.75rem', padding: '0.5rem', borderRadius: '6px', background: 'rgba(255, 255, 255, 0.03)', fontSize: '0.7rem' }}>
                <span style={{ color: briefStatus.is_quiet_day ? 'var(--text-muted)' : 'var(--gain)', fontWeight: 600 }}>
                  {briefStatus.is_quiet_day ? '🔇 Quiet Day Logged (No Message)' : '🔔 Material Alert Triggered'}
                </span>
              </div>
            )}
          </div>

          {/* Compounding Memory & Watchlist */}
          <div className="glass" style={{ padding: '1rem', borderRadius: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <Layers size={16} color="var(--accent-cyan)" />
                <h3 style={{ fontSize: '0.85rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Focus Watchlist</h3>
              </div>
            </div>

            {/* Watchlist list */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', marginBottom: '0.75rem' }}>
              {profile?.watchlist?.map((item, idx) => (
                <div 
                  key={idx} 
                  onClick={() => fetchLiveQuote(item.ticker)}
                  style={{ display: 'flex', justifyContent: 'space-between', padding: '0.4rem 0.6rem', borderRadius: '6px', background: 'rgba(255,255,255,0.04)', fontSize: '0.75rem', cursor: 'pointer' }}
                >
                  <span style={{ fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{item.ticker}</span>
                  <span style={{ color: 'var(--text-muted)' }}>{item.sector}</span>
                </div>
              ))}
            </div>

            {/* Add Watchlist input */}
            <div style={{ display: 'flex', gap: '0.4rem' }}>
              <input 
                type="text" 
                placeholder="Add ticker (e.g. AMZN)" 
                value={newTicker}
                onChange={(e) => setNewTicker(e.target.value)}
                style={{ flex: 1, padding: '0.35rem 0.6rem', borderRadius: '6px', border: '1px solid var(--border)', background: 'transparent', color: '#FFF', fontSize: '0.75rem' }}
              />
              <button 
                onClick={handleAddWatchlist}
                style={{ padding: '0.35rem 0.6rem', borderRadius: '6px', background: 'var(--accent-cyan)', border: 'none', color: '#000', fontWeight: 700, cursor: 'pointer' }}
              >
                <Plus size={14} />
              </button>
            </div>
          </div>

          {/* Memory Facts Inspector */}
          <div className="glass" style={{ padding: '1rem', borderRadius: '12px' }}>
            <h3 style={{ fontSize: '0.85rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.5rem' }}>
              Compounding Memory Facts
            </h3>
            {profile?.facts?.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                {profile.facts.map((f, i) => (
                  <div key={i} style={{ fontSize: '0.7rem', color: 'var(--text-muted)', padding: '0.35rem', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '4px' }}>
                    • {f}
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                As you chat, Atlas extracts structured facts and remembers your preferences.
              </p>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}
