import { configureStore, createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// ── HCP Slice ─────────────────────────────────────────────────────────────────

export const fetchHCPs = createAsyncThunk('hcps/fetchAll', async (search = '') => {
  const res = await axios.get(`${API}/hcps`, { params: search ? { search } : {} });
  return res.data;
});

export const createHCP = createAsyncThunk('hcps/create', async (data) => {
  const res = await axios.post(`${API}/hcps`, data);
  return res.data;
});

const hcpSlice = createSlice({
  name: 'hcps',
  initialState: { list: [], loading: false, error: null },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchHCPs.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(fetchHCPs.fulfilled, (state, action) => { state.loading = false; state.list = action.payload; })
      .addCase(fetchHCPs.rejected, (state, action) => { state.loading = false; state.error = action.error.message; })
      .addCase(createHCP.fulfilled, (state, action) => { state.list.push(action.payload); });
  },
});

// ── Interaction Slice ─────────────────────────────────────────────────────────

export const fetchInteractions = createAsyncThunk('interactions/fetchAll', async (hcpId = null) => {
  const res = await axios.get(`${API}/interactions`, { params: hcpId ? { hcp_id: hcpId } : {} });
  return res.data;
});

export const createInteraction = createAsyncThunk('interactions/create', async (data) => {
  const res = await axios.post(`${API}/interactions`, data);
  return res.data;
});

export const updateInteraction = createAsyncThunk('interactions/update', async ({ id, data }) => {
  const res = await axios.patch(`${API}/interactions/${id}`, data);
  return res.data;
});

const interactionSlice = createSlice({
  name: 'interactions',
  initialState: { list: [], loading: false, error: null, currentInteraction: null },
  reducers: {
    setCurrentInteraction: (state, action) => { state.currentInteraction = action.payload; },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchInteractions.pending, (state) => { state.loading = true; })
      .addCase(fetchInteractions.fulfilled, (state, action) => { state.loading = false; state.list = action.payload; })
      .addCase(fetchInteractions.rejected, (state, action) => { state.loading = false; state.error = action.error.message; })
      .addCase(createInteraction.fulfilled, (state, action) => { state.list.unshift(action.payload); state.currentInteraction = action.payload; })
      .addCase(updateInteraction.fulfilled, (state, action) => {
        const idx = state.list.findIndex(i => i.id === action.payload.id);
        if (idx !== -1) state.list[idx] = action.payload;
      });
  },
});

export const { setCurrentInteraction } = interactionSlice.actions;

// ── Chat Slice ────────────────────────────────────────────────────────────────

export const sendChatMessage = createAsyncThunk('chat/send', async ({ message, hcpId, history }) => {
  const res = await axios.post(`${API}/agent/chat`, {
    message,
    hcp_id: hcpId,
    conversation_history: history,
  });
  return res.data;
});

const chatSlice = createSlice({
  name: 'chat',
  initialState: { messages: [], loading: false, error: null },
  reducers: {
    addUserMessage: (state, action) => {
      state.messages.push({ role: 'user', content: action.payload });
    },
    clearChat: (state) => { state.messages = []; },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendChatMessage.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(sendChatMessage.fulfilled, (state, action) => {
        state.loading = false;
        state.messages.push({ role: 'assistant', content: action.payload.response });
      })
      .addCase(sendChatMessage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
        state.messages.push({ role: 'assistant', content: '⚠️ Sorry, something went wrong. Please try again.' });
      });
  },
});

export const { addUserMessage, clearChat } = chatSlice.actions;

// ── Store ─────────────────────────────────────────────────────────────────────

export const store = configureStore({
  reducer: {
    hcps: hcpSlice.reducer,
    interactions: interactionSlice.reducer,
    chat: chatSlice.reducer,
  },
});
