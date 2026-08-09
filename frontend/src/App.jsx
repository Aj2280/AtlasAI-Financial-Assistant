import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, Mic, Image, FileText, Bot, User, Bell, Sparkles, TrendingUp, TrendingDown,
  Layers, ShieldAlert, Cpu, CheckCircle2, RefreshCw, Plus, Calendar, Table, FileSpreadsheet, 
  SendHorizontal, Key, Database, Clock, Globe, PieChart, Share2, Download, ExternalLink, 
  Activity, Zap, Copy, Check, ChevronRight, BarChart2, Briefcase, MessageSquare, 
  ArrowUpRight, ArrowDownRight, Search, Sliders, Volume2, Command
} from 'lucide-react';

import PriceChart from './components/PriceChart';
import MarketGauge from './components/MarketGauge';
import PortfolioDonut from './components/PortfolioDonut';
import AudioVisualizer from './components/AudioVisualizer';
import CommandPalette from './components/CommandPalette';

const API_BASE = (import.meta.env.VITE_API_URL || '').replace(/\/+$/, '');

const DEFAULT_RIBBON = [
  { ticker: 'NVDA', name: 'Nvidia', price: '$223.96', change: '+2.27%', isUp: true, sparkline: ' ▂▃▅▇█' },
  { ticker: 'AAPL', name: 'Apple', price: '$313.33', change: '+0.29%', isUp: true, sparkline: '▃▄▄▅▅▆' },
  { ticker: 'MSFT', name: 'Microsoft', price: '$415.80', change: '+1.12%', isUp: true, sparkline: '▂▃▄▅▆▇' },
  { ticker: 'TSLA', name: 'Tesla', price: '$328.58', change: '+2.83%', isUp: true, sparkline: ' ▂▄▅▆█' },
  { ticker: 'BTC', name: 'Bitcoin', price: '$97,450', change: '+3.40%', isUp: true, sparkline: '▃▄▅▆▇█' },
  { ticker: 'ETH', name: 'Ethereum', price: '$3,420', change: '+2.10%', isUp: true, sparkline: '▂▃▄▅▆▇' },
  { ticker: 'GOLD', name: 'Gold Spot', price: '$2,780', change: '+0.85%', isUp: true, sparkline: '▄▄▅▅▆▆' },
  { ticker: 'CRUDE OIL', name: 'WTI Oil', price: '$76.40', change: '-0.50%', isUp: false, sparkline: '▆▅▄▃▂ ' },
  { ticker: 'NIFTY 50', name: 'NSE Nifty', price: '₹24,850', change: '+0.42%', isUp: true, sparkline: '▂▃▄▅▆▇' },
  { ticker: 'US10Y', name: '10-Yr Yield', price: '4.28%', change: '-0.03', isUp: false, sparkline: '▆▅▅▄▄▃' }
];

function renderFormattedContent(text) {
  if (!text) return null;
  
  let clean = text
    .replace(/<b>(.*?)<\/b>/gi, '**$1**')
    .replace(/<i>(.*?)<\/i>/gi, '*$1*')
    .replace(/<code>(.*?)<\/code>/gi, '`$1`')
    .replace(/<a\s+href=['"]([^'"]+)['"][^>]*>(.*?)<\/a>/gi, '$2 ($1)')
    .replace(/<[^>]+>/g, '');

  const lines = clean.split('\n');
  return lines.map((line, lineIdx) => {
    const parts = [];
    const regex = /(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g;
    let match;
    let lastIndex = 0;
    let keyIdx = 0;

    while ((match = regex.exec(line)) !== null) {
      if (match.index > lastIndex) {
        parts.push(line.substring(lastIndex, match.index));
      }
      const token = match[0];
      if (token.startsWith('**') && token.endsWith('**')) {
        parts.push(<strong key={keyIdx++} style={{ color: '#F8FAFC', fontWeight: 700 }}>{token.slice(2, -2)}</strong>);
      } else if (token.startsWith('*') && token.endsWith('*')) {
        parts.push(<em key={keyIdx++} style={{ color: '#94A3B8' }}>{token.slice(1, -1)}</em>);
      } else if (token.startsWith('`') && token.endsWith('`')) {
        parts.push(<code key={keyIdx++} style={{ background: 'rgba(255,255,255,0.1)', padding: '0.1rem 0.35rem', borderRadius: '4px', fontSize: '0.85em', color: 'var(--accent-cyan)' }}>{token.slice(1, -1)}</code>);
      }
      lastIndex = regex.lastIndex;
    }

    if (lastIndex < line.length) {
      parts.push(line.substring(lastIndex));
    }

    const isBullet = line.trim().startsWith('•') || line.trim().startsWith('-');
    const isHeading = line.trim().startsWith('#');

    return (
      <div 
        key={lineIdx} 
        style={{ 
          minHeight: line.trim() === '' ? '0.65rem' : 'auto', 
          paddingLeft: isBullet ? '0.6rem' : '0',
          marginBottom: isBullet ? '0.3rem' : (isHeading ? '0.6rem' : '0.2rem'),
          lineHeight: '1.6',
          color: isBullet ? '#E2E8F0' : (isHeading ? '#FFF' : '#CBD5E1'),
          fontWeight: isHeading ? 700 : 400
        }}
      >
        {parts.length > 0 ? parts : <span>&nbsp;</span>}
      </div>
    );
  });
}

export default function App() {
  // Navigation
  const [activeTab, setActiveTab] = useState('chat'); // 'chat' | 'sectors' | 'documents' | 'portfolio' | 'integrations'
  const [showCommandPalette, setShowCommandPalette] = useState(false);
  
  // Chat & Messaging
  const [messages, setMessages] = useState([
    {
      id: '1',
      sender: 'bot',
      channel: 'text',
      content: "Hello! I'm **Atlas**, your senior executive financial analyst and chief-of-staff.\n\nI deliver proactive financial intelligence, live multi-asset quotes across US/India/Crypto, 10-K/10-Q document synthesis, and automated watchlist monitoring with noise suppression.\n\nWhat company, macro sector, or financial report should we examine today?",
      intent: 'onboarding',
      sources: ['Atlas Core Engine v2.0', 'Finnhub Live API', 'SEC EDGAR'],
      timestamp: '10:40 AM'
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [selectedChannel, setSelectedChannel] = useState('text');
  const [loading, setLoading] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [copiedMsgId, setCopiedMsgId] = useState(null);

  // Profile, Market & Data
  const [profile, setProfile] = useState(null);
  const [tickerQuery, setTickerQuery] = useState('NVDA');
  const [liveQuote, setLiveQuote] = useState({
    ticker: 'NVDA',
    price: 223.96,
    change: 4.96,
    change_pct: 2.27,
    pe: '32.5x',
    gross_margin: '75.1%',
    moat: 'CUDA Software Ecosystem & High-End AI Accelerators',
    health_score: '8/10'
  });
  const [newTicker, setNewTicker] = useState('');
  const [briefStatus, setBriefStatus] = useState(null);

  // Modals & Sub-views
  const [showTokenModal, setShowTokenModal] = useState(false);
  const [botToken, setBotToken] = useState('');
  const [botConnected, setBotConnected] = useState(false);
  const [redisStatus, setRedisStatus] = useState(null);
  const [liveTime, setLiveTime] = useState(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
  const [userTz, setUserTz] = useState(Intl.DateTimeFormat().resolvedOptions().timeZone || 'Asia/Kolkata');

  // Sectors & Integrations
  const [sectorsList, setSectorsList] = useState([]);
  const [integrationsList, setIntegrationsList] = useState([]);

  // Document Intelligence
  const [activeDoc, setActiveDoc] = useState(null);
  const [docList, setDocList] = useState([]);
  const [docTitle, setDocTitle] = useState('');
  const [docContent, setDocContent] = useState('');
  const [docLoading, setDocLoading] = useState(false);
  const [docFeedback, setDocFeedback] = useState('');

  // Portfolio Management
  const [holdingsList, setHoldingsList] = useState([]);
  const [holdingTicker, setHoldingTicker] = useState('');
  const [holdingShares, setHoldingShares] = useState('');
  const [holdingCost, setHoldingCost] = useState('');
  const [holdingNotes, setHoldingNotes] = useState('');

  const chatEndRef = useRef(null);
  const telegramId = 1001;

  useEffect(() => {
    fetchProfile();
    fetchLiveQuote('NVDA');
    checkBotStatus();
    fetchConversationHistory();
    fetchRedisStatus();
    fetchSectors();
    fetchIntegrations();
    fetchDocuments();
    fetchHoldings();

    const timer = setInterval(() => {
      setLiveTime(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
    }, 1000);

    const handleGlobalKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setShowCommandPalette(prev => !prev);
      }
    };
    window.addEventListener('keydown', handleGlobalKeyDown);

    return () => {
      clearInterval(timer);
      window.removeEventListener('keydown', handleGlobalKeyDown);
    };
  }, []);

  useEffect(() => {
    if (activeTab === 'chat') {
      chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, activeTab]);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(''), 3500);
  };

  const copyToClipboard = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedMsgId(id);
    showToast('Copied analysis to clipboard!');
    setTimeout(() => setCopiedMsgId(null), 2000);
  };

  const fetchProfile = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/user/${telegramId}`);
      if (res.ok) {
        const data = await res.json();
        setProfile(data);
        if (data.timezone) setUserTz(data.timezone);
      }
    } catch (e) {
      console.error("Fetch profile error", e);
    }
  };

  const fetchLiveQuote = async (ticker) => {
    if (!ticker) return;
    try {
      const res = await fetch(`${API_BASE}/api/market/quote/${ticker}`);
      if (res.ok) {
        const data = await res.json();
        setLiveQuote(data);
      }
    } catch (e) {
      console.error("Fetch quote error", e);
    }
  };

  const fetchHoldings = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/database/holdings/${telegramId}`);
      if (res.ok) {
        const data = await res.json();
        setHoldingsList(data.holdings || []);
      }
    } catch (e) {
      console.error("Fetch holdings error", e);
    }
  };

  const handleAddHolding = async () => {
    if (!holdingTicker.trim() || !holdingShares) return;
    try {
      const res = await fetch(`${API_BASE}/api/database/holdings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          telegram_id: telegramId,
          ticker: holdingTicker.trim().toUpperCase(),
          shares: parseFloat(holdingShares),
          avg_cost: parseFloat(holdingCost) || 0.0,
          notes: holdingNotes.trim()
        })
      });
      if (res.ok) {
        showToast(`Added ${holdingShares} shares of ${holdingTicker.toUpperCase()}!`);
        setHoldingTicker('');
        setHoldingShares('');
        setHoldingCost('');
        setHoldingNotes('');
        fetchHoldings();
        fetchProfile();
      }
    } catch (e) {
      showToast(`Error: ${e.message}`);
    }
  };

  const fetchConversationHistory = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/history/${telegramId}`);
      if (res.ok) {
        const data = await res.json();
        if (data.messages && data.messages.length > 0) {
          const loaded = data.messages.map((m) => ({
            id: m.id.toString(),
            sender: m.role === 'assistant' ? 'bot' : 'user',
            channel: 'text',
            content: m.content,
            intent: 'financial_history',
            sources: m.role === 'assistant' ? ['Stored Memory DB'] : [],
            timestamp: m.created_at || 'Earlier'
          }));
          setMessages(loaded);
        }
      }
    } catch (e) {
      console.error("History fetch error", e);
    }
  };

  const fetchRedisStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/redis/status`);
      if (res.ok) {
        const data = await res.json();
        setRedisStatus(data);
      }
    } catch (e) {
      console.error("Redis status error", e);
    }
  };

  const fetchSectors = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/sectors`);
      if (res.ok) {
        const data = await res.json();
        setSectorsList(data.sectors || []);
      }
    } catch (e) {
      console.error("Fetch sectors error", e);
    }
  };

  const fetchIntegrations = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/integrations`);
      if (res.ok) {
        const data = await res.json();
        setIntegrationsList(data.platforms || []);
      }
    } catch (e) {
      console.error("Fetch integrations error", e);
    }
  };

  const fetchDocuments = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/documents/${telegramId}`);
      if (res.ok) {
        const data = await res.json();
        setActiveDoc(data.active_document);
        setDocList(data.documents || []);
      }
    } catch (e) {
      console.error("Fetch docs error", e);
    }
  };

  const checkBotStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/bot/status`);
      if (res.ok) {
        const data = await res.json();
        setBotConnected(data.connected);
      }
    } catch (e) {
      console.error("Bot status error", e);
    }
  };

  const handleSetToken = async () => {
    if (!botToken.trim()) return;
    try {
      const res = await fetch(`${API_BASE}/api/bot/set-token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: botToken.trim() })
      });
      const data = await res.json();
      if (res.ok && data.status === 'success') {
        setBotConnected(true);
        setShowTokenModal(false);
        showToast('Real Telegram Bot Token connected!');
      } else {
        alert(data.detail || 'Could not connect bot token.');
      }
    } catch (e) {
      alert(`Connection failed: ${e.message}`);
    }
  };

  const handleClearHistory = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/history/clear`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ telegram_id: telegramId })
      });
      if (res.ok) {
        setMessages([
          {
            id: Date.now().toString(),
            sender: 'bot',
            channel: 'text',
            content: "Memory cleared. How can I assist your financial analysis?",
            intent: 'reset',
            sources: ['Local SQLite DB'],
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }
        ]);
        showToast('Chat history & Redis cache cleared');
      }
    } catch (e) {
      console.error("Clear history error", e);
    }
  };

  const handleSendMessage = async (textToSend = inputText, channel = selectedChannel) => {
    if (!textToSend.trim()) return;

    const userMsg = {
      id: Date.now().toString(),
      sender: 'user',
      channel: channel,
      content: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText('');
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          telegram_id: telegramId,
          content: textToSend,
          channel: channel
        })
      });

      if (!res.ok) throw new Error('API server unavailable');

      const data = await res.json();

      const botMsg = {
        id: (Date.now() + 1).toString(),
        sender: 'bot',
        channel: channel,
        content: data.response,
        intent: data.intent,
        sources: data.sources || ['Finnhub Live API', 'Groq LLaMA 3.3 70B', 'SEC EDGAR'],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages((prev) => [...prev, botMsg]);
      if (data.user_profile) setProfile(data.user_profile);
      fetchRedisStatus();
    } catch (err) {
      const errorMsg = {
        id: (Date.now() + 1).toString(),
        sender: 'bot',
        channel: 'text',
        content: "⚠️ **Connection Notice**: Backend live engine reconnecting. Real-time data remains cached in local SQLite database.",
        intent: 'error',
        sources: ['Fallback Cache'],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const triggerDailyBrief = async (force = true) => {
    setBriefStatus('Synthesizing Morning Market Intelligence...');
    try {
      const res = await fetch(`${API_BASE}/api/brief/trigger`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ telegram_id: telegramId, force: force })
      });
      const data = await res.json();
      if (data.status === 'sent') {
        setBriefStatus('Morning Brief Delivered to Telegram & Web!');
        showToast('Morning Market Brief delivered!');
        const botMsg = {
          id: Date.now().toString(),
          sender: 'bot',
          channel: 'text',
          content: data.brief,
          intent: 'morning_brief',
          sources: ['Proactive Macro Engine', 'Finnhub Live API', 'SEC EDGAR'],
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        setMessages((prev) => [...prev, botMsg]);
      } else {
        setBriefStatus(`🔇 Noise Suppression Active: ${data.reason || 'Session flat with zero material catalysts.'}`);
        showToast('Noise Suppression: Silent mode active (No material move).');
      }
    } catch (e) {
      setBriefStatus('Trigger failed.');
    }
  };

  const handleUploadDoc = async (titleToUse = docTitle, contentToUse = docContent) => {
    if (!contentToUse.trim()) return;
    setDocLoading(true);
    setDocFeedback('Ingesting and parsing financial report...');
    try {
      const res = await fetch(`${API_BASE}/api/documents/upload`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          telegram_id: telegramId,
          filename: titleToUse.trim() || 'Annual_Report_2026.pdf',
          content: contentToUse.trim(),
          kind: 'report'
        })
      });
      if (res.ok) {
        const data = await res.json();
        setDocFeedback('✅ Document successfully parsed & loaded!');
        setActiveDoc(data.document);
        setDocTitle('');
        setDocContent('');
        fetchDocuments();
        showToast('Financial report loaded into conversational context!');
        
        const botMsg = {
          id: Date.now().toString(),
          sender: 'bot',
          channel: 'document_intelligence',
          content: data.executive_summary,
          intent: 'document_summary',
          sources: [`Loaded Document: ${data.document.name}`],
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        setMessages(prev => [...prev, botMsg]);
        setActiveTab('chat');
      }
    } catch (e) {
      setDocFeedback(`❌ Error: ${e.message}`);
    } finally {
      setDocLoading(false);
    }
  };

  const handleAnalyzeDocMode = async (mode = 'summary', question = null) => {
    setDocLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/documents/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          telegram_id: telegramId,
          mode: mode,
          custom_question: question
        })
      });
      if (res.ok) {
        const data = await res.json();
        const botMsg = {
          id: Date.now().toString(),
          sender: 'bot',
          channel: 'document_intelligence',
          content: data.analysis,
          intent: `document_${mode}`,
          sources: [`Report: ${data.document_name}`],
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        setMessages(prev => [...prev, botMsg]);
        setActiveTab('chat');
        showToast('Analysis added to chat stream!');
      }
    } catch (e) {
      alert(`Error analyzing document: ${e.message}`);
    } finally {
      setDocLoading(false);
    }
  };

  const handleCompareDocs = async () => {
    setDocLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/documents/compare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ telegram_id: telegramId })
      });
      if (res.ok) {
        const data = await res.json();
        const botMsg = {
          id: Date.now().toString(),
          sender: 'bot',
          channel: 'document_comparison',
          content: data.comparison,
          intent: 'document_comparison',
          sources: [`Comparative Delta: ${data.doc1} vs ${data.doc2}`],
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        setMessages(prev => [...prev, botMsg]);
        setActiveTab('chat');
        showToast('Comparative report delta generated!');
      }
    } catch (e) {
      alert(`Error comparing reports: ${e.message}`);
    } finally {
      setDocLoading(false);
    }
  };

  const handleAddWatchlist = async () => {
    if (!newTicker.trim()) return;
    try {
      const res = await fetch(`${API_BASE}/api/watchlist/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ telegram_id: telegramId, ticker: newTicker.trim().toUpperCase() })
      });
      if (res.ok) {
        fetchProfile();
        showToast(`Added ${newTicker.toUpperCase()} to watchlist!`);
        setNewTicker('');
      }
    } catch (e) {
      console.error(e);
    }
  };

  const downloadPortfolioCSV = () => {
    window.open(`${API_BASE}/api/export/portfolio-csv?telegram_id=${telegramId}`, '_blank');
    showToast('Exporting Portfolio & Sectors CSV...');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100vw', background: 'var(--bg-dark)', overflow: 'hidden' }}>
      
      {/* Toast Notification */}
      {toastMessage && (
        <div className="toast-banner">
          <Sparkles size={16} color="var(--accent-cyan)" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Command Palette Modal (Cmd+K) */}
      <CommandPalette 
        isOpen={showCommandPalette}
        onClose={() => setShowCommandPalette(false)}
        onSelectAction={(type, val) => {
          if (type === 'tab') setActiveTab(val);
          if (type === 'prompt') handleSendMessage(val);
          if (type === 'brief') triggerDailyBrief(true);
        }}
      />

      {/* Top Live Real-Time Market Ticker Ribbon */}
      <div className="ticker-ribbon">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--accent-cyan)', fontSize: '0.75rem', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.05em', paddingRight: '0.5rem', borderRight: '1px solid var(--border)' }}>
          <Activity size={14} className="animate-pulse-glow" />
          <span>Live Feeds</span>
        </div>

        {DEFAULT_RIBBON.map((item, idx) => (
          <div 
            key={idx} 
            className="ticker-chip"
            onClick={() => {
              setTickerQuery(item.ticker);
              fetchLiveQuote(item.ticker);
              handleSendMessage(`Give me a quick financial breakdown for ${item.ticker}`);
            }}
            title={`Click to analyze ${item.name} (${item.ticker})`}
          >
            <span style={{ fontWeight: 700, color: '#FFF' }}>{item.ticker}</span>
            <span style={{ color: 'var(--text-muted)' }}>{item.price}</span>
            <span style={{ color: item.isUp ? 'var(--gain)' : 'var(--loss)', fontWeight: 600, display: 'flex', alignItems: 'center' }}>
              {item.isUp ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
              {item.change}
            </span>
            <span style={{ color: item.isUp ? 'var(--gain)' : 'var(--loss)', opacity: 0.8, fontSize: '0.7rem' }}>{item.sparkline}</span>
          </div>
        ))}
      </div>

      {/* Main Header & Workspace Tabs */}
      <header style={{ padding: '0.75rem 1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(13, 17, 26, 0.85)', borderBottom: '1px solid var(--border)', backdropFilter: 'blur(16px)' }}>
        
        {/* Brand & Live Clock */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <div style={{ width: '38px', height: '38px', borderRadius: '10px', background: 'linear-gradient(135deg, #00F2FE 0%, #4FACFE 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 20px rgba(0, 242, 254, 0.35)' }}>
              <Zap size={22} color="#07090E" />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <h1 style={{ fontSize: '1.2rem', fontWeight: 800, letterSpacing: '-0.02em', background: 'linear-gradient(to right, #FFF, #94A3B8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                  ATLAS AI
                </h1>
                <span style={{ fontSize: '0.65rem', padding: '0.15rem 0.45rem', borderRadius: '4px', background: 'rgba(0, 242, 254, 0.15)', color: 'var(--accent-cyan)', fontWeight: 700, border: '1px solid rgba(0, 242, 254, 0.3)' }}>
                  v2.0 PRO
                </span>
              </div>
              <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Institutional Financial Assistant & Multi-Asset Terminal</p>
            </div>
          </div>

          {/* Quick Spotlight Trigger */}
          <button
            onClick={() => setShowCommandPalette(true)}
            className="glass-pill"
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.35rem 0.75rem', borderRadius: '8px', color: 'var(--text-muted)', fontSize: '0.75rem', cursor: 'pointer' }}
          >
            <Search size={13} color="var(--accent-cyan)" />
            <span>Search / Commands</span>
            <span style={{ fontSize: '0.65rem', padding: '0.1rem 0.3rem', borderRadius: '4px', background: 'rgba(255,255,255,0.08)', color: '#FFF', fontFamily: 'var(--font-mono)' }}>
              ⌘K
            </span>
          </button>

          {/* Clock Pill */}
          <div className="glass-pill" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', padding: '0.35rem 0.75rem', borderRadius: '8px', fontSize: '0.75rem', color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)' }}>
            <Clock size={12} color="var(--accent-cyan)" />
            <span>{liveTime}</span>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>({userTz.split('/')[1] || 'Local'})</span>
          </div>
        </div>

        {/* Workspace Navigation Tabs */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', background: 'rgba(0,0,0,0.35)', padding: '0.25rem', borderRadius: '12px', border: '1px solid var(--border)' }}>
          <button 
            onClick={() => setActiveTab('chat')}
            className={`nav-tab ${activeTab === 'chat' ? 'active' : ''}`}
          >
            <MessageSquare size={15} />
            <span>Analyst Chat</span>
          </button>
          
          <button 
            onClick={() => { fetchSectors(); setActiveTab('sectors'); }}
            className={`nav-tab ${activeTab === 'sectors' ? 'active' : ''}`}
          >
            <PieChart size={15} />
            <span>13 Sectors Heatmap</span>
          </button>

          <button 
            onClick={() => { fetchDocuments(); setActiveTab('documents'); }}
            className={`nav-tab ${activeTab === 'documents' ? 'active' : ''}`}
          >
            <FileText size={15} />
            <span>10-K & Deck Intel</span>
          </button>

          <button 
            onClick={() => { fetchHoldings(); setActiveTab('portfolio'); }}
            className={`nav-tab ${activeTab === 'portfolio' ? 'active' : ''}`}
          >
            <Briefcase size={15} />
            <span>Portfolio & Watchlist</span>
          </button>

          <button 
            onClick={() => { fetchIntegrations(); setActiveTab('integrations'); }}
            className={`nav-tab ${activeTab === 'integrations' ? 'active' : ''}`}
          >
            <Share2 size={15} />
            <span>Integrations Hub</span>
          </button>
        </div>

        {/* Quick Tools & Bot Token */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <button 
            onClick={() => setShowTokenModal(true)}
            className="glass-pill"
            style={{ 
              padding: '0.4rem 0.8rem', 
              borderRadius: '8px', 
              border: botConnected ? '1px solid #10B981' : '1px solid var(--accent-cyan)', 
              background: botConnected ? 'rgba(16, 185, 129, 0.15)' : 'rgba(0, 242, 254, 0.1)',
              color: 'var(--text-main)', 
              cursor: 'pointer', 
              display: 'flex', 
              alignItems: 'center', 
              gap: '0.4rem', 
              fontSize: '0.75rem', 
              fontWeight: 600 
            }}
          >
            <SendHorizontal size={13} color={botConnected ? "#10B981" : "var(--accent-cyan)"} />
            <span>{botConnected ? "Telegram: LIVE" : "Connect Telegram"}</span>
          </button>

          <button 
            onClick={() => triggerDailyBrief(true)}
            className="glass-pill"
            style={{ padding: '0.4rem 0.8rem', borderRadius: '8px', color: '#FFF', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.75rem', fontWeight: 600 }}
            title="Generate Morning Financial Brief"
          >
            <Bell size={13} color="var(--accent-cyan)" />
            <span>Morning Brief</span>
          </button>
        </div>
      </header>

      {/* Main Workspace Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 380px', flex: 1, overflow: 'hidden' }}>
        
        {/* Left Column: Active Tab Content */}
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', borderRight: '1px solid var(--border)', background: 'var(--bg-surface)', overflow: 'hidden' }}>
          
          {/* TAB 1: EXECUTIVE ANALYST CHAT */}
          {activeTab === 'chat' && (
            <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
              
              {/* Chat Message Stream */}
              <div style={{ flex: 1, overflowY: 'auto', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                {messages.map((msg) => (
                  <div 
                    key={msg.id}
                    className="animate-fade-in"
                    style={{
                      display: 'flex',
                      gap: '0.75rem',
                      justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start'
                    }}
                  >
                    {msg.sender === 'bot' && (
                      <div style={{ width: '36px', height: '36px', borderRadius: '10px', background: 'linear-gradient(135deg, #00F2FE 0%, #4FACFE 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, boxShadow: '0 4px 12px rgba(0, 242, 254, 0.25)' }}>
                        <Bot size={20} color="#07090E" />
                      </div>
                    )}

                    <div style={{ maxWidth: '85%' }}>
                      <div 
                        style={{
                          padding: '1.15rem 1.4rem',
                          borderRadius: msg.sender === 'user' ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
                          background: msg.sender === 'user' 
                            ? 'linear-gradient(135deg, #1E293B 0%, #0F172A 100%)' 
                            : 'rgba(18, 24, 38, 0.85)',
                          border: msg.sender === 'user' ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(255,255,255,0.08)',
                          boxShadow: 'var(--shadow-sm)',
                          backdropFilter: 'blur(12px)',
                          position: 'relative'
                        }}
                      >
                        {/* Top Action Bar on Message (Copy + Text-to-Speech) */}
                        {msg.sender === 'bot' && (
                          <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', gap: '0.5rem', marginBottom: '0.6rem' }}>
                            <AudioVisualizer textToRead={msg.content} />
                            
                            <button
                              onClick={() => copyToClipboard(msg.content, msg.id)}
                              style={{
                                background: 'rgba(255, 255, 255, 0.05)',
                                border: '1px solid var(--border)',
                                borderRadius: '6px',
                                padding: '0.25rem 0.45rem',
                                color: 'var(--text-muted)',
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.25rem',
                                fontSize: '0.7rem'
                              }}
                              title="Copy response to clipboard"
                            >
                              {copiedMsgId === msg.id ? <Check size={12} color="var(--gain)" /> : <Copy size={12} />}
                              <span>{copiedMsgId === msg.id ? 'Copied' : 'Copy'}</span>
                            </button>
                          </div>
                        )}

                        <div className="prose-atlas" style={{ fontSize: '0.875rem' }}>
                          {renderFormattedContent(msg.content)}
                        </div>

                        {/* Citations / Sources */}
                        {msg.sources && msg.sources.length > 0 && (
                          <div style={{ marginTop: '0.85rem', paddingTop: '0.6rem', borderTop: '1px solid rgba(255, 255, 255, 0.06)', fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                            <CheckCircle2 size={12} color="var(--accent-cyan)" />
                            <span>Backed by: {msg.sources.join(' · ')}</span>
                          </div>
                        )}
                      </div>
                      
                      <span style={{ fontSize: '0.65rem', color: 'var(--text-dim)', marginTop: '0.35rem', display: 'block', textAlign: msg.sender === 'user' ? 'right' : 'left' }}>
                        {msg.timestamp}
                      </span>
                    </div>

                    {msg.sender === 'user' && (
                      <div style={{ width: '36px', height: '36px', borderRadius: '10px', background: '#334155', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                        <User size={20} color="#94A3B8" />
                      </div>
                    )}
                  </div>
                ))}

                {loading && (
                  <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                    <div style={{ width: '36px', height: '36px', borderRadius: '10px', background: 'linear-gradient(135deg, #00F2FE, #4FACFE)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <Bot size={20} color="#07090E" />
                    </div>
                    <div className="glass" style={{ padding: '0.85rem 1.25rem', borderRadius: '16px', display: 'flex', alignItems: 'center', gap: '0.6rem', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                      <Sparkles size={16} className="animate-pulse-glow" color="var(--accent-cyan)" />
                      <span>Atlas is analyzing real-time financial feeds, fundamentals & SEC filings...</span>
                    </div>
                  </div>
                )}

                <div ref={chatEndRef} />
              </div>

              {/* Quick Prompts Bar */}
              <div style={{ padding: '0.5rem 1.5rem', display: 'flex', gap: '0.5rem', overflowX: 'auto', background: 'rgba(7, 9, 14, 0.7)', borderTop: '1px solid var(--border)', scrollbarWidth: 'none' }}>
                {[
                  { label: "Tell me about Apple", icon: Sparkles, text: "Tell me about Apple" },
                  { label: "Compare MSFT vs GOOGL", icon: Table, text: "Compare Microsoft and Google from an investment perspective based on revenue growth, profitability, and valuation." },
                  { label: "Track Tesla & SEC Filings", icon: TrendingUp, text: "Track Tesla and notify me whenever there's a major announcement or SEC filing." },
                  { label: "Schedule Team Earnings Meeting", icon: Calendar, text: "Schedule a meeting with my team tomorrow at 10 AM to discuss this earnings report." },
                  { label: "Nvidia 10-K Risk Analysis", icon: ShieldAlert, text: "Analyze Nvidia's recent 10-K and highlight the biggest operational and regulatory risks." }
                ].map((qp, i) => {
                  const Icon = qp.icon;
                  return (
                    <button
                      key={i}
                      onClick={() => handleSendMessage(qp.text, 'text')}
                      className="glass-pill"
                      style={{ padding: '0.35rem 0.75rem', borderRadius: '8px', cursor: 'pointer', whiteSpace: 'nowrap', color: 'var(--text-main)', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
                    >
                      <Icon size={12} color="var(--accent-cyan)" />
                      <span>{qp.label}</span>
                    </button>
                  );
                })}
              </div>

              {/* Chat Input Controls */}
              <div style={{ padding: '1rem 1.5rem', background: 'rgba(13, 17, 26, 0.95)', borderTop: '1px solid var(--border)' }}>
                <form 
                  onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }}
                  style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}
                >
                  <div style={{ flex: 1, position: 'relative', display: 'flex', alignItems: 'center' }}>
                    <input 
                      type="text" 
                      placeholder="Ask Atlas about any ticker, valuation, macro sector, earnings report, or scheduled meeting..." 
                      value={inputText}
                      onChange={(e) => setInputText(e.target.value)}
                      disabled={loading}
                      style={{
                        width: '100%',
                        padding: '0.85rem 1.25rem',
                        paddingRight: '3rem',
                        borderRadius: '12px',
                        background: 'rgba(18, 24, 38, 0.8)',
                        border: '1px solid var(--border)',
                        color: 'var(--text-main)',
                        fontSize: '0.875rem',
                        outline: 'none',
                        transition: 'all 0.2s ease'
                      }}
                      onFocus={(e) => e.target.style.borderColor = 'var(--accent-cyan)'}
                      onBlur={(e) => e.target.style.borderColor = 'var(--border)'}
                    />
                    <button
                      type="button"
                      onClick={() => handleSendMessage("Give me a comprehensive voice transcript overview of today's market movers.", 'voice')}
                      style={{ position: 'absolute', right: '0.75rem', background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
                      title="Simulate Voice Note / Whisper Transcription"
                    >
                      <Mic size={18} />
                    </button>
                  </div>

                  <button
                    type="submit"
                    disabled={loading || !inputText.trim()}
                    style={{
                      padding: '0.85rem 1.5rem',
                      borderRadius: '12px',
                      background: loading || !inputText.trim() ? 'rgba(255,255,255,0.05)' : 'linear-gradient(135deg, #00F2FE 0%, #4FACFE 100%)',
                      border: 'none',
                      color: loading || !inputText.trim() ? 'var(--text-dim)' : '#07090E',
                      fontWeight: 800,
                      cursor: loading || !inputText.trim() ? 'not-allowed' : 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      fontSize: '0.875rem',
                      boxShadow: loading || !inputText.trim() ? 'none' : '0 4px 15px rgba(0, 242, 254, 0.3)',
                      transition: 'all 0.2s ease'
                    }}
                  >
                    <Send size={16} />
                    <span>Send</span>
                  </button>
                </form>
              </div>
            </div>
          )}

          {/* TAB 2: FINANCIAL SECTORS HEATMAP */}
          {activeTab === 'sectors' && (
            <div style={{ padding: '1.5rem', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#FFF' }}>11 GICS Financial Sectors & Heatmap</h2>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Institutional live tracking across all 11 global market sectors, Crypto & Macro commodities</p>
                </div>
                <button 
                  onClick={fetchSectors}
                  className="glass-pill"
                  style={{ padding: '0.45rem 0.9rem', borderRadius: '8px', color: '#FFF', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem' }}
                >
                  <RefreshCw size={14} />
                  <span>Refresh Feeds</span>
                </button>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem' }}>
                {sectorsList.map((sec) => (
                  <div 
                    key={sec.id}
                    className="glass-card"
                    style={{ padding: '1.2rem', display: 'flex', flexDirection: 'column', gap: '0.75rem', cursor: 'pointer' }}
                    onClick={() => {
                      handleSendMessage(`Analyze the ${sec.name} sector (${sec.etf}) and give me the top constituents outlook.`);
                      setActiveTab('chat');
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <div>
                        <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#FFF' }}>{sec.name}</h3>
                        <span style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>{sec.etf}</span>
                      </div>
                      <span style={{ 
                        fontSize: '0.7rem', 
                        padding: '0.2rem 0.5rem', 
                        borderRadius: '6px', 
                        background: sec.change_pct >= 0 ? 'var(--gain-bg)' : 'var(--loss-bg)', 
                        color: sec.change_pct >= 0 ? 'var(--gain)' : 'var(--loss)', 
                        fontWeight: 700 
                      }}>
                        {sec.change_pct >= 0 ? `+${sec.change_pct}%` : `${sec.change_pct}%`}
                      </span>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem' }}>
                      <span style={{ color: 'var(--text-muted)' }}>ETF Price: <strong style={{ color: '#FFF' }}>${sec.etf_price}</strong></span>
                      <span style={{ 
                        fontSize: '0.65rem', 
                        padding: '0.15rem 0.45rem', 
                        borderRadius: '4px', 
                        background: sec.sentiment === 'Bullish' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)', 
                        color: sec.sentiment === 'Bullish' ? 'var(--gain)' : 'var(--loss)', 
                        fontWeight: 700,
                        textTransform: 'uppercase'
                      }}>
                        {sec.sentiment}
                      </span>
                    </div>

                    <div style={{ borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '0.5rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      Top Constituents: <span style={{ color: 'var(--text-secondary)' }}>{sec.constituents?.slice(0, 3).join(', ')}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: DOCUMENT & 10-K INTELLIGENCE */}
          {activeTab === 'documents' && (
            <div style={{ padding: '1.5rem', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#FFF' }}>Document & Report Intelligence Hub</h2>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Conversational analysis for Annual Reports (10-K), Earnings Presentations, Investment Decks & Due Diligence</p>
                </div>
              </div>

              {/* Active Document Card */}
              {activeDoc ? (
                <div className="glass-card" style={{ padding: '1.25rem 1.5rem', background: 'rgba(59, 130, 246, 0.08)', border: '1px solid rgba(59, 130, 246, 0.3)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.35rem' }}>
                      <span style={{ fontSize: '0.65rem', padding: '0.2rem 0.5rem', borderRadius: '4px', background: '#3B82F6', color: '#FFF', fontWeight: 800, textTransform: 'uppercase' }}>
                        Active Report
                      </span>
                      <h3 style={{ fontSize: '1.05rem', fontWeight: 800, color: '#FFF' }}>{activeDoc.name}</h3>
                    </div>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {(activeDoc.char_count || 0).toLocaleString()} characters loaded · Active in conversational memory
                    </span>
                  </div>

                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button
                      onClick={() => handleAnalyzeDocMode('summary')}
                      disabled={docLoading}
                      style={{ padding: '0.5rem 1rem', borderRadius: '8px', background: 'linear-gradient(135deg, #3B82F6, #1D4ED8)', border: 'none', color: '#FFF', fontSize: '0.8rem', fontWeight: 700, cursor: 'pointer' }}
                    >
                      📑 5-Pt Summary
                    </button>
                    <button
                      onClick={() => handleAnalyzeDocMode('risks')}
                      disabled={docLoading}
                      style={{ padding: '0.5rem 1rem', borderRadius: '8px', background: 'rgba(239, 68, 68, 0.2)', border: '1px solid rgba(239, 68, 68, 0.4)', color: '#FCA5A5', fontSize: '0.8rem', fontWeight: 700, cursor: 'pointer' }}
                    >
                      ⚠️ Extract Risks
                    </button>
                    {docList.length >= 2 && (
                      <button
                        onClick={handleCompareDocs}
                        disabled={docLoading}
                        style={{ padding: '0.5rem 1rem', borderRadius: '8px', background: 'rgba(16, 185, 129, 0.2)', border: '1px solid rgba(16, 185, 129, 0.4)', color: '#6EE7B7', fontSize: '0.8rem', fontWeight: 700, cursor: 'pointer' }}
                      >
                        🔄 Compare Reports
                      </button>
                    )}
                  </div>
                </div>
              ) : (
                <div style={{ padding: '1rem', borderRadius: '12px', background: 'rgba(255,255,255,0.02)', border: '1px dashed var(--border)', color: 'var(--text-muted)', textAlign: 'center', fontSize: '0.85rem' }}>
                  No active document loaded. Ingest a report below or choose a sample preset.
                </div>
              )}

              {/* Ingest Form */}
              <div className="glass-card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#FFF' }}>Ingest Report / Deck Text</h3>
                  
                  {/* Presets */}
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button
                      onClick={() => {
                        setDocTitle("Tesla_Q2_2026_Earnings_Call.txt");
                        setDocContent(`Tesla Q2 2026 Financial Results & Earnings Presentation:\n• Total Revenue: $25.5B (+8.4% YoY), driven by Megapack energy storage expansion and vehicle delivery stabilization.\n• Gross Margin: 18.2%, expanding 80 bps sequentially due to cost of goods sold per unit reductions.\n• Net Income: $2.45B; Adjusted EPS: $0.72 vs $0.65 consensus.\n• Operating Cash Flow: $3.8B; Free Cash Flow: $2.1B.\n• Energy Storage Deployments: 9.4 GWh in Q2 (record quarter).\n• Full Self-Driving (FSD) v13 rollout commenced across North American fleet.\n• Risk Factors: Automotive tariff uncertainties, commodity lithium price volatility, compute cluster CapEx ramp ($2.5B quarterly AI infrastructure spend), and Robotaxi regulatory clearance milestones.`);
                      }}
                      style={{ padding: '0.3rem 0.6rem', borderRadius: '6px', background: 'rgba(0, 242, 254, 0.1)', border: '1px solid rgba(0, 242, 254, 0.3)', color: 'var(--accent-cyan)', fontSize: '0.75rem', cursor: 'pointer' }}
                    >
                      Preset: Tesla Earnings Deck
                    </button>
                    <button
                      onClick={() => {
                        setDocTitle("Microsoft_FY25_10K_Annual_Report.txt");
                        setDocContent(`Microsoft Corporation Form 10-K Annual Report:\n• Total TTM Revenue: $245.1B (+15.2% YoY), with Microsoft Cloud generating $137B (+23% YoY).\n• Azure and other cloud services revenue grew 29% driven by enterprise AI consumption workloads.\n• Gross Margin: 69.8%; Operating Income: $109.4B (44.6% Operating Margin).\n• Capital Expenditures: $55.7B invested into datacenter infrastructure and GPU capacity.\n• Key Risk Factors: Substantial capital commitments in AI infrastructure before monetization maturity, global cybersecurity threats, antitrust scrutiny over multi-cloud licensing terms, and foreign exchange currency headwinds.`);
                      }}
                      style={{ padding: '0.3rem 0.6rem', borderRadius: '6px', background: 'rgba(139, 92, 246, 0.1)', border: '1px solid rgba(139, 92, 246, 0.3)', color: '#A78BFA', fontSize: '0.75rem', cursor: 'pointer' }}
                    >
                      Preset: Microsoft 10-K
                    </button>
                  </div>
                </div>

                <input 
                  type="text" 
                  placeholder="Document Title (e.g. Apple_FY26_Q3_10Q.pdf or Due_Diligence_Deck.pdf)" 
                  value={docTitle}
                  onChange={(e) => setDocTitle(e.target.value)}
                  style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '8px', border: '1px solid var(--border)', background: '#090C10', color: '#FFF', fontSize: '0.85rem' }}
                />

                <textarea
                  rows={8}
                  placeholder="Paste report text, 10-K MD&A section, earnings call transcript, or investment memo here..."
                  value={docContent}
                  onChange={(e) => setDocContent(e.target.value)}
                  style={{ width: '100%', padding: '0.85rem', borderRadius: '8px', border: '1px solid var(--border)', background: '#090C10', color: '#FFF', fontSize: '0.825rem', fontFamily: 'var(--font-mono)', lineHeight: '1.4' }}
                />

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.8rem', color: docFeedback.includes('✅') ? 'var(--gain)' : 'var(--text-muted)' }}>
                    {docFeedback || 'Supports 10-Ks, 10-Qs, Earnings Transcripts, Pitch Decks & Research Memos.'}
                  </span>

                  <button
                    onClick={() => handleUploadDoc(docTitle, docContent)}
                    disabled={docLoading || !docContent.trim()}
                    style={{ padding: '0.65rem 1.5rem', borderRadius: '10px', background: 'linear-gradient(135deg, #3B82F6, #1D4ED8)', border: 'none', color: '#FFF', fontWeight: 700, cursor: docLoading || !docContent.trim() ? 'not-allowed' : 'pointer', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
                  >
                    <FileText size={15} />
                    <span>{docLoading ? 'Analyzing Report...' : 'Ingest & Generate Executive Summary'}</span>
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: PORTFOLIO & WATCHLIST */}
          {activeTab === 'portfolio' && (
            <div style={{ padding: '1.5rem', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#FFF' }}>Portfolio Holdings & Asset Allocation</h2>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Relational positions tracked in local SQLite database with live Finnhub market quotes</p>
                </div>
                <button 
                  onClick={downloadPortfolioCSV}
                  className="glass-pill"
                  style={{ padding: '0.45rem 1rem', borderRadius: '8px', color: '#FFF', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem', background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(5, 150, 105, 0.2))', border: '1px solid rgba(16, 185, 129, 0.4)' }}
                >
                  <Download size={14} color="var(--gain)" />
                  <span>Export CSV</span>
                </button>
              </div>

              {/* Visual Asset Allocation Donut */}
              <PortfolioDonut totalValue={64250} />

              {/* Add Holding Form */}
              <div className="glass-card" style={{ padding: '1.25rem', display: 'flex', gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
                <input 
                  type="text" 
                  placeholder="Ticker (e.g. NVDA)" 
                  value={holdingTicker}
                  onChange={(e) => setHoldingTicker(e.target.value)}
                  style={{ flex: 1, minWidth: '120px', padding: '0.6rem 0.85rem', borderRadius: '8px', border: '1px solid var(--border)', background: '#090C10', color: '#FFF', fontSize: '0.85rem' }}
                />
                <input 
                  type="number" 
                  placeholder="Shares (e.g. 50)" 
                  value={holdingShares}
                  onChange={(e) => setHoldingShares(e.target.value)}
                  style={{ flex: 1, minWidth: '120px', padding: '0.6rem 0.85rem', borderRadius: '8px', border: '1px solid var(--border)', background: '#090C10', color: '#FFF', fontSize: '0.85rem' }}
                />
                <input 
                  type="number" 
                  placeholder="Cost Basis ($)" 
                  value={holdingCost}
                  onChange={(e) => setHoldingCost(e.target.value)}
                  style={{ flex: 1, minWidth: '120px', padding: '0.6rem 0.85rem', borderRadius: '8px', border: '1px solid var(--border)', background: '#090C10', color: '#FFF', fontSize: '0.85rem' }}
                />
                <input 
                  type="text" 
                  placeholder="Notes (e.g. Core Growth)" 
                  value={holdingNotes}
                  onChange={(e) => setHoldingNotes(e.target.value)}
                  style={{ flex: 1.5, minWidth: '160px', padding: '0.6rem 0.85rem', borderRadius: '8px', border: '1px solid var(--border)', background: '#090C10', color: '#FFF', fontSize: '0.85rem' }}
                />
                <button
                  onClick={handleAddHolding}
                  style={{ padding: '0.6rem 1.2rem', borderRadius: '8px', background: 'linear-gradient(135deg, #00F2FE, #4FACFE)', border: 'none', color: '#07090E', fontWeight: 800, cursor: 'pointer', fontSize: '0.85rem' }}
                >
                  Add Holding
                </button>
              </div>

              {/* Holdings Table */}
              <div className="glass-card" style={{ padding: '1rem', overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border)', color: 'var(--text-muted)' }}>
                      <th style={{ padding: '0.75rem' }}>Asset</th>
                      <th style={{ padding: '0.75rem' }}>Shares</th>
                      <th style={{ padding: '0.75rem' }}>Avg Cost</th>
                      <th style={{ padding: '0.75rem' }}>Notes</th>
                      <th style={{ padding: '0.75rem', textAlign: 'right' }}>Quick Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {holdingsList.length > 0 ? (
                      holdingsList.map((h) => (
                        <tr key={h.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                          <td style={{ padding: '0.75rem', fontWeight: 700, color: '#FFF' }}>{h.ticker}</td>
                          <td style={{ padding: '0.75rem' }}>{h.shares}</td>
                          <td style={{ padding: '0.75rem', fontFamily: 'var(--font-mono)' }}>${h.avg_cost}</td>
                          <td style={{ padding: '0.75rem', color: 'var(--text-muted)' }}>{h.notes || '—'}</td>
                          <td style={{ padding: '0.75rem', textAlign: 'right' }}>
                            <button
                              onClick={() => {
                                handleSendMessage(`Give me a detailed portfolio review for my ${h.shares} shares of ${h.ticker}.`);
                                setActiveTab('chat');
                              }}
                              style={{ padding: '0.3rem 0.6rem', borderRadius: '6px', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border)', color: 'var(--accent-cyan)', fontSize: '0.75rem', cursor: 'pointer' }}
                            >
                              Analyze Position
                            </button>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={5} style={{ padding: '1.5rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                          No holdings recorded yet. Add your first position above.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 5: INTEGRATIONS HUB */}
          {activeTab === 'integrations' && (
            <div style={{ padding: '1.5rem', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div>
                <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#FFF' }}>Multi-Platform Integrations Hub</h2>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Connect Telegram, Discord, Slack, TradingView Webhooks & Export Portfolio Data</p>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem' }}>
                {integrationsList.map((plat) => (
                  <div key={plat.id} className="glass-card" style={{ padding: '1.2rem', display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#FFF' }}>{plat.name}</h3>
                      <span style={{ fontSize: '0.65rem', padding: '0.2rem 0.5rem', borderRadius: '4px', background: plat.status === 'connected' ? 'var(--gain-bg)' : 'rgba(0, 242, 254, 0.15)', color: plat.status === 'connected' ? 'var(--gain)' : 'var(--accent-cyan)', fontWeight: 800, textTransform: 'uppercase' }}>
                        {plat.status}
                      </span>
                    </div>
                    <span style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)' }}>{plat.category}</span>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
                      {plat.description}
                    </p>
                  </div>
                ))}
              </div>

              {/* TradingView Webhook Instructions */}
              <div className="glass-card" style={{ padding: '1.25rem' }}>
                <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#FFF', marginBottom: '0.5rem' }}>TradingView Pine Script Inbound Webhook</h3>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.6rem' }}>
                  Set TradingView alert Webhook URL to: <code>http://127.0.0.1:8000/api/webhooks/tradingview</code> with message payload:
                </p>
                <pre style={{ fontSize: '0.75rem', padding: '0.75rem', background: '#090C10', borderRadius: '8px', color: '#38BDF8', fontFamily: 'var(--font-mono)' }}>
{`{
  "ticker": "{{ticker}}",
  "action": "BUY",
  "price": {{close}},
  "strategy": "RSI Bullish Divergence"
}`}
                </pre>
              </div>
            </div>
          )}

        </div>

        {/* Right Sidebar: Real-Time Intelligence & User Memory */}
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', padding: '1.25rem', gap: '1.25rem', overflowY: 'auto', background: 'var(--bg-dark)' }}>
          
          {/* Interactive Live Price Chart Preview */}
          <PriceChart 
            ticker={liveQuote.ticker || 'NVDA'} 
            basePrice={liveQuote.price || 223.96} 
            changePct={liveQuote.change_pct || 2.27}
            isUp={(liveQuote.change_pct || 0) >= 0}
          />

          {/* Market Pulse Gauge (Fear & Greed) */}
          <MarketGauge score={72} vix={14.8} advanceRatio="68% / 32%" />

          {/* Active Watchlist Card */}
          <div className="glass-card" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Active Watchlist ({profile?.watchlist?.length || 0})
            </span>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
              {profile?.watchlist && profile.watchlist.length > 0 ? (
                profile.watchlist.map((t, idx) => (
                  <span 
                    key={idx}
                    onClick={() => {
                      setTickerQuery(t);
                      fetchLiveQuote(t);
                      handleSendMessage(`Give me a live catalyst breakdown for ${t}`);
                      setActiveTab('chat');
                    }}
                    style={{ padding: '0.25rem 0.55rem', borderRadius: '6px', background: 'rgba(0, 242, 254, 0.1)', border: '1px solid rgba(0, 242, 254, 0.25)', color: 'var(--accent-cyan)', fontSize: '0.75rem', fontWeight: 700, cursor: 'pointer', fontFamily: 'var(--font-mono)' }}
                  >
                    ${t}
                  </span>
                ))
              ) : (
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>No tickers in watchlist</span>
              )}
            </div>

            <div style={{ display: 'flex', gap: '0.4rem' }}>
              <input 
                type="text" 
                placeholder="Add Ticker (e.g. AMD)" 
                value={newTicker}
                onChange={(e) => setNewTicker(e.target.value.toUpperCase())}
                style={{ flex: 1, padding: '0.4rem 0.6rem', borderRadius: '6px', border: '1px solid var(--border)', background: '#090C10', color: '#FFF', fontSize: '0.75rem', fontFamily: 'var(--font-mono)' }}
              />
              <button
                onClick={handleAddWatchlist}
                style={{ padding: '0.4rem 0.75rem', borderRadius: '6px', background: 'rgba(255,255,255,0.08)', border: '1px solid var(--border)', color: '#FFF', fontSize: '0.75rem', cursor: 'pointer' }}
              >
                + Add
              </button>
            </div>
          </div>

          {/* User Memory & Facts Card */}
          <div className="glass-card" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              User Memory Profile (SQLite)
            </span>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
              {profile?.facts && profile.facts.length > 0 ? (
                profile.facts.slice(-4).map((f, idx) => (
                  <div key={idx} style={{ padding: '0.4rem 0.6rem', borderRadius: '6px', background: 'rgba(0,0,0,0.3)', border: '1px solid rgba(255,255,255,0.04)' }}>
                    • {f}
                  </div>
                ))
              ) : (
                <span style={{ color: 'var(--text-muted)' }}>No facts recorded yet</span>
              )}
            </div>

            <button
              onClick={handleClearHistory}
              style={{ alignSelf: 'flex-start', background: 'transparent', border: 'none', color: 'var(--text-muted)', fontSize: '0.7rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.3rem', marginTop: '0.25rem' }}
            >
              <RefreshCw size={11} />
              <span>Reset Context Memory</span>
            </button>
          </div>

          {/* Engine Diagnostics */}
          <div className="glass-card" style={{ padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
            <span style={{ fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Engine Diagnostics</span>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Primary LLM:</span>
              <strong style={{ color: '#FFF' }}>Groq LLaMA 3.3 70B</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Cache Engine:</span>
              <strong style={{ color: 'var(--gain)' }}>Redis L1 Active</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Database:</span>
              <strong style={{ color: 'var(--accent-cyan)' }}>SQLite Local WAL</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Scheduler:</span>
              <strong style={{ color: '#FFF' }}>APScheduler (08:00 Briefs)</strong>
            </div>
          </div>

        </div>

      </div>

      {/* Bot Token Modal */}
      {showTokenModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(10px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '2rem' }}>
          <div className="glass" style={{ width: '480px', padding: '1.75rem', borderRadius: '16px', background: '#0F131D', border: '1px solid rgba(0, 242, 254, 0.3)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1rem' }}>
              <Key size={22} color="var(--accent-cyan)" />
              <h2 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#FFF' }}>Connect Real Telegram Bot Token</h2>
            </div>

            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1.25rem', lineHeight: '1.5' }}>
              To connect Atlas to your actual Telegram account:
              <br />1. Open <b>@BotFather</b> on Telegram.
              <br />2. Send <code>/newbot</code> to create your bot and copy your <b>HTTP API Token</b>.
              <br />3. Paste the Token below to activate real-time Telegram streaming!
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
                style={{ padding: '0.5rem 1.25rem', borderRadius: '8px', background: 'linear-gradient(135deg, #00F2FE, #4FACFE)', border: 'none', color: '#07090E', fontWeight: 800, cursor: 'pointer', fontSize: '0.85rem' }}
              >
                Connect Live Bot
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
