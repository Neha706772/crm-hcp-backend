import React, { useState, useEffect, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  fetchHCPs,
  createInteraction,
  updateInteraction,
  fetchInteractions,
  sendChatMessage,
  addUserMessage,
  clearChat,
  setCurrentInteraction,
} from '../store/store';

// ── Styles ────────────────────────────────────────────────────────────────────

const styles = {
  page: {
    fontFamily: "'Inter', sans-serif",
    background: '#f5f7fa',
    minHeight: '100vh',
    padding: '0',
  },
  header: {
    background: '#fff',
    borderBottom: '1px solid #e8eaed',
    padding: '0 32px',
    height: '60px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  headerTitle: {
    fontSize: '18px',
    fontWeight: '600',
    color: '#1a1a2e',
    margin: 0,
  },
  headerBadge: {
    background: '#e8f5e9',
    color: '#2e7d32',
    padding: '4px 12px',
    borderRadius: '20px',
    fontSize: '12px',
    fontWeight: '500',
  },
  body: {
    display: 'grid',
    gridTemplateColumns: '1fr 380px',
    gap: '24px',
    padding: '24px 32px',
    maxWidth: '1400px',
    margin: '0 auto',
  },
  card: {
    background: '#fff',
    borderRadius: '12px',
    border: '1px solid #e8eaed',
    padding: '24px',
  },
  cardTitle: {
    fontSize: '15px',
    fontWeight: '600',
    color: '#1a1a2e',
    marginBottom: '20px',
    paddingBottom: '14px',
    borderBottom: '1px solid #f0f0f0',
  },
  formRow: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '16px',
    marginBottom: '16px',
  },
  formGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  },
  label: {
    fontSize: '13px',
    fontWeight: '500',
    color: '#5f6368',
  },
  input: {
    padding: '10px 14px',
    borderRadius: '8px',
    border: '1px solid #e0e3e8',
    fontSize: '14px',
    color: '#1a1a2e',
    outline: 'none',
    transition: 'border-color 0.15s',
    fontFamily: "'Inter', sans-serif",
  },
  select: {
    padding: '10px 14px',
    borderRadius: '8px',
    border: '1px solid #e0e3e8',
    fontSize: '14px',
    color: '#1a1a2e',
    outline: 'none',
    background: '#fff',
    fontFamily: "'Inter', sans-serif",
  },
  textarea: {
    padding: '10px 14px',
    borderRadius: '8px',
    border: '1px solid #e0e3e8',
    fontSize: '14px',
    color: '#1a1a2e',
    outline: 'none',
    resize: 'vertical',
    minHeight: '90px',
    fontFamily: "'Inter', sans-serif",
  },
  sentimentGroup: {
    display: 'flex',
    gap: '12px',
    alignItems: 'center',
  },
  sentimentBtn: (active, color) => ({
    padding: '6px 16px',
    borderRadius: '20px',
    border: `1px solid ${active ? color : '#e0e3e8'}`,
    background: active ? color + '15' : '#fff',
    color: active ? color : '#5f6368',
    fontSize: '13px',
    fontWeight: active ? '600' : '400',
    cursor: 'pointer',
    transition: 'all 0.15s',
  }),
  primaryBtn: {
    background: '#1a73e8',
    color: '#fff',
    border: 'none',
    borderRadius: '8px',
    padding: '11px 24px',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
    fontFamily: "'Inter', sans-serif",
    transition: 'background 0.15s',
  },
  secondaryBtn: {
    background: '#fff',
    color: '#1a73e8',
    border: '1px solid #1a73e8',
    borderRadius: '8px',
    padding: '11px 24px',
    fontSize: '14px',
    fontWeight: '500',
    cursor: 'pointer',
    fontFamily: "'Inter', sans-serif",
  },
  aiTag: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '5px',
    fontSize: '12px',
    color: '#1a73e8',
    fontWeight: '500',
    marginBottom: '8px',
  },
  aiSuggestion: {
    background: '#f0f7ff',
    borderRadius: '8px',
    padding: '12px 16px',
    fontSize: '13px',
    color: '#1565c0',
    marginTop: '12px',
  },
  // Chat Panel
  chatPanel: {
    background: '#fff',
    borderRadius: '12px',
    border: '1px solid #e8eaed',
    display: 'flex',
    flexDirection: 'column',
    height: '800px',
  },
  chatHeader: {
    padding: '16px 20px',
    borderBottom: '1px solid #f0f0f0',
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
  },
  aiDot: {
    width: '10px',
    height: '10px',
    borderRadius: '50%',
    background: '#34a853',
  },
  chatTitle: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#1a1a2e',
  },
  chatSubtitle: {
    fontSize: '12px',
    color: '#9aa0a6',
  },
  chatMessages: {
    flex: 1,
    overflowY: 'auto',
    padding: '16px',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  chatBubbleUser: {
    background: '#1a73e8',
    color: '#fff',
    borderRadius: '16px 16px 4px 16px',
    padding: '10px 14px',
    fontSize: '13px',
    maxWidth: '85%',
    alignSelf: 'flex-end',
    lineHeight: '1.5',
  },
  chatBubbleAI: {
    background: '#f8f9fa',
    color: '#1a1a2e',
    borderRadius: '16px 16px 16px 4px',
    padding: '10px 14px',
    fontSize: '13px',
    maxWidth: '90%',
    alignSelf: 'flex-start',
    lineHeight: '1.5',
    border: '1px solid #e8eaed',
  },
  chatInputRow: {
    padding: '12px 16px',
    borderTop: '1px solid #f0f0f0',
    display: 'flex',
    gap: '8px',
    alignItems: 'flex-end',
  },
  chatInput: {
    flex: 1,
    padding: '10px 14px',
    borderRadius: '20px',
    border: '1px solid #e0e3e8',
    fontSize: '13px',
    outline: 'none',
    fontFamily: "'Inter', sans-serif",
    resize: 'none',
    maxHeight: '100px',
  },
  sendBtn: {
    background: '#1a73e8',
    border: 'none',
    borderRadius: '20px',
    padding: '10px 18px',
    color: '#fff',
    fontSize: '13px',
    fontWeight: '600',
    cursor: 'pointer',
    fontFamily: "'Inter', sans-serif",
  },
  placeholder: {
    fontSize: '13px',
    color: '#9aa0a6',
    textAlign: 'center',
    padding: '24px 12px',
    lineHeight: '1.6',
  },
  tagRow: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '6px',
    marginTop: '4px',
  },
  tag: {
    background: '#e8f0fe',
    color: '#1a73e8',
    borderRadius: '4px',
    padding: '3px 10px',
    fontSize: '12px',
    fontWeight: '500',
  },
  followUpItem: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '8px',
    padding: '8px 0',
    borderBottom: '1px solid #f5f5f5',
    fontSize: '13px',
    color: '#1a1a2e',
  },
  checkIcon: {
    color: '#34a853',
    fontSize: '14px',
    marginTop: '2px',
    flexShrink: 0,
  },
};

// ── Helpers ───────────────────────────────────────────────────────────────────

const INTERACTION_TYPES = ['meeting', 'call', 'email', 'conference', 'webinar'];
const SENTIMENT_OPTIONS = [
  { value: 'positive', label: '😊 Positive', color: '#34a853' },
  { value: 'neutral', label: '😐 Neutral', color: '#f9ab00' },
  { value: 'negative', label: '😔 Negative', color: '#ea4335' },
];

const AI_FOLLOW_UP_EXAMPLES = [
  '→ Schedule follow-up meeting in 2 weeks',
  '→ Send OncoBrand Phase III PDF',
  '→ Add Dr. to advisory board invite list',
];

// ── Component ─────────────────────────────────────────────────────────────────

export default function LogInteractionScreen() {
  const dispatch = useDispatch();
  const { list: hcps, loading: hcpLoading } = useSelector(s => s.hcps);
  const { list: interactions } = useSelector(s => s.interactions);
  const { messages: chatMessages, loading: chatLoading } = useSelector(s => s.chat);

  const chatEndRef = useRef(null);
  const chatInputRef = useRef(null);

  // Form state
  const [form, setForm] = useState({
    hcp_id: '',
    interaction_type: 'meeting',
    date: new Date().toISOString().split('T')[0],
    time: new Date().toTimeString().slice(0, 5),
    attendees: '',
    topics_discussed: '',
    sentiment: 'neutral',
    outcomes: '',
  });
  const [chatInput, setChatInput] = useState('');
  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [activeTab, setTab] = useState('form'); // 'form' | 'history'

  useEffect(() => { dispatch(fetchHCPs()); dispatch(fetchInteractions()); }, [dispatch]);
  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [chatMessages]);

  const handleFormChange = (field) => (e) => setForm(prev => ({ ...prev, [field]: e.target.value }));

  const handleSubmitForm = async () => {
    if (!form.hcp_id || !form.date) return alert('Please select an HCP and date.');
    setSaving(true);
    try {
      await dispatch(createInteraction({
        ...form,
        date: new Date(form.date + 'T' + form.time).toISOString(),
        attendees: form.attendees ? form.attendees.split(',').map(s => s.trim()) : [],
      })).unwrap();
      setSuccessMsg('Interaction logged successfully!');
      setTimeout(() => setSuccessMsg(''), 3000);
      setForm(prev => ({ ...prev, topics_discussed: '', outcomes: '', attendees: '' }));
    } catch (e) {
      alert('Error: ' + e.message);
    } finally {
      setSaving(false);
    }
  };

  const handleSendChat = async () => {
    if (!chatInput.trim() || chatLoading) return;
    const msg = chatInput.trim();
    setChatInput('');
    dispatch(addUserMessage(msg));
    const history = chatMessages.map(m => ({ role: m.role, content: m.content }));
    dispatch(sendChatMessage({
      message: msg,
      hcpId: form.hcp_id || null,
      history,
    }));
  };

  const handleChatKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSendChat(); }
  };

  return (
    <div style={styles.page}>
      {/* Google Inter font */}
      <link rel="preconnect" href="https://fonts.googleapis.com" />
      <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />

      {/* Header */}
      <header style={styles.header}>
        <h1 style={styles.headerTitle}>🏥 Log HCP Interaction</h1>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <span style={styles.headerBadge}>AI-Powered CRM</span>
          <button style={styles.secondaryBtn} onClick={() => { dispatch(clearChat()); dispatch(fetchInteractions()); }}>
            Refresh
          </button>
        </div>
      </header>

      <div style={styles.body}>
        {/* LEFT — Form / History */}
        <div>
          {/* Tab Bar */}
          <div style={{ display: 'flex', gap: '4px', marginBottom: '16px' }}>
            {['form', 'history'].map(t => (
              <button key={t} onClick={() => setTab(t)} style={{
                padding: '8px 20px', borderRadius: '8px', border: 'none',
                background: activeTab === t ? '#1a73e8' : '#fff',
                color: activeTab === t ? '#fff' : '#5f6368',
                fontFamily: "'Inter', sans-serif", fontSize: '13px', fontWeight: '500', cursor: 'pointer',
              }}>
                {t === 'form' ? '📋 Log Interaction' : '📂 Interaction History'}
              </button>
            ))}
          </div>

          {activeTab === 'form' ? (
            <div style={styles.card}>
              <div style={styles.cardTitle}>Interaction Details</div>

              {successMsg && (
                <div style={{ background: '#e8f5e9', color: '#2e7d32', padding: '12px 16px', borderRadius: '8px', marginBottom: '16px', fontSize: '13px', fontWeight: '500' }}>
                  ✅ {successMsg}
                </div>
              )}

              {/* HCP + Type */}
              <div style={styles.formRow}>
                <div style={styles.formGroup}>
                  <label style={styles.label}>HCP Name *</label>
                  <select style={styles.select} value={form.hcp_id} onChange={handleFormChange('hcp_id')}>
                    <option value="">Search or select HCP...</option>
                    {hcps.map(h => (
                      <option key={h.id} value={h.id}>{h.name} — {h.specialty}</option>
                    ))}
                  </select>
                </div>
                <div style={styles.formGroup}>
                  <label style={styles.label}>Interaction Type</label>
                  <select style={styles.select} value={form.interaction_type} onChange={handleFormChange('interaction_type')}>
                    {INTERACTION_TYPES.map(t => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
                  </select>
                </div>
              </div>

              {/* Date + Time */}
              <div style={styles.formRow}>
                <div style={styles.formGroup}>
                  <label style={styles.label}>Date</label>
                  <input type="date" style={styles.input} value={form.date} onChange={handleFormChange('date')} />
                </div>
                <div style={styles.formGroup}>
                  <label style={styles.label}>Time</label>
                  <input type="time" style={styles.input} value={form.time} onChange={handleFormChange('time')} />
                </div>
              </div>

              {/* Attendees */}
              <div style={{ ...styles.formGroup, marginBottom: '16px' }}>
                <label style={styles.label}>Attendees</label>
                <input style={styles.input} placeholder="Enter names or search... (comma-separated)" value={form.attendees} onChange={handleFormChange('attendees')} />
              </div>

              {/* Topics */}
              <div style={{ ...styles.formGroup, marginBottom: '16px' }}>
                <label style={styles.label}>Topics Discussed</label>
                <textarea style={styles.textarea} placeholder="Enter key discussion points..." value={form.topics_discussed} onChange={handleFormChange('topics_discussed')} />
              </div>

              {/* Sentiment */}
              <div style={{ ...styles.formGroup, marginBottom: '16px' }}>
                <label style={styles.label}>Observed HCP Sentiment</label>
                <div style={styles.sentimentGroup}>
                  {SENTIMENT_OPTIONS.map(s => (
                    <button
                      key={s.value}
                      style={styles.sentimentBtn(form.sentiment === s.value, s.color)}
                      onClick={() => setForm(prev => ({ ...prev, sentiment: s.value }))}
                    >
                      {s.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Outcomes */}
              <div style={{ ...styles.formGroup, marginBottom: '20px' }}>
                <label style={styles.label}>Outcomes</label>
                <textarea style={styles.textarea} placeholder="Key outcomes or agreements..." value={form.outcomes} onChange={handleFormChange('outcomes')} />
              </div>

              {/* AI Follow-up Suggestions */}
              <div>
                <div style={styles.aiTag}>✨ AI Suggested Follow-ups</div>
                <div style={styles.aiSuggestion}>
                  {AI_FOLLOW_UP_EXAMPLES.map((item, i) => (
                    <div key={i} style={{ marginBottom: i < AI_FOLLOW_UP_EXAMPLES.length - 1 ? '6px' : 0 }}>{item}</div>
                  ))}
                </div>
              </div>

              {/* Submit */}
              <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
                <button style={styles.primaryBtn} onClick={handleSubmitForm} disabled={saving}>
                  {saving ? 'Saving...' : '💾 Save Interaction'}
                </button>
                <button style={styles.secondaryBtn} onClick={() => setForm(prev => ({ ...prev, topics_discussed: '', outcomes: '', attendees: '' }))}>
                  Clear
                </button>
              </div>
            </div>
          ) : (
            /* Interaction History */
            <div style={styles.card}>
              <div style={styles.cardTitle}>Recent Interactions ({interactions.length})</div>
              {interactions.length === 0 ? (
                <p style={{ color: '#9aa0a6', fontSize: '14px' }}>No interactions logged yet.</p>
              ) : interactions.map(intr => (
                <div key={intr.id} style={{ padding: '14px 0', borderBottom: '1px solid #f5f5f5' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <div style={{ fontWeight: '600', fontSize: '14px', color: '#1a1a2e' }}>
                        {hcps.find(h => h.id === intr.hcp_id)?.name || 'HCP'}
                        <span style={{ ...styles.tag, marginLeft: '8px' }}>{intr.interaction_type}</span>
                      </div>
                      <div style={{ fontSize: '12px', color: '#9aa0a6', marginTop: '3px' }}>
                        {new Date(intr.date).toLocaleDateString()}
                      </div>
                      {intr.ai_summary && (
                        <div style={{ fontSize: '13px', color: '#5f6368', marginTop: '6px', fontStyle: 'italic' }}>
                          "{intr.ai_summary}"
                        </div>
                      )}
                    </div>
                    <span style={{
                      fontSize: '12px', padding: '3px 10px', borderRadius: '20px',
                      background: intr.sentiment === 'positive' ? '#e8f5e9' : intr.sentiment === 'negative' ? '#fce8e6' : '#fef9e7',
                      color: intr.sentiment === 'positive' ? '#2e7d32' : intr.sentiment === 'negative' ? '#c62828' : '#e65100',
                    }}>
                      {intr.sentiment}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* RIGHT — AI Chat Panel */}
        <div style={styles.chatPanel}>
          <div style={styles.chatHeader}>
            <div style={styles.aiDot} />
            <div>
              <div style={styles.chatTitle}>🤖 AI Assistant</div>
              <div style={styles.chatSubtitle}>Log interaction via chat</div>
            </div>
          </div>

          <div style={styles.chatMessages}>
            {chatMessages.length === 0 ? (
              <div style={styles.placeholder}>
                Log interaction details here (e.g., <em>"Met Dr. Smith, discussed Product X efficacy, positive sentiment, shared brochure"</em>) or ask for help.
              </div>
            ) : (
              chatMessages.map((msg, i) => (
                <div key={i} style={msg.role === 'user' ? styles.chatBubbleUser : styles.chatBubbleAI}>
                  {msg.content}
                </div>
              ))
            )}
            {chatLoading && (
              <div style={{ ...styles.chatBubbleAI, color: '#9aa0a6' }}>
                ✨ Thinking...
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          <div style={styles.chatInputRow}>
            <textarea
              ref={chatInputRef}
              style={styles.chatInput}
              placeholder="Describe interaction..."
              value={chatInput}
              onChange={e => setChatInput(e.target.value)}
              onKeyDown={handleChatKeyDown}
              rows={2}
            />
            <button style={styles.sendBtn} onClick={handleSendChat} disabled={chatLoading}>
              ➤ Log
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
