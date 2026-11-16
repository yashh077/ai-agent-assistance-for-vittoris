// Vittoris AI Autonomous Agent & Voice Controller
const sessionId = 'session_' + Math.random().toString(36).substring(2, 9);

let isVoiceCallActive = false;
let isVoiceMuted = false;
let callTimerInterval = null;
let callSeconds = 0;
let recognition = null;

document.addEventListener('DOMContentLoaded', () => {
  initChat();
  initVoiceCallControls();
  initSpeechRecognition();
  initTabs();
  initQuickPrompts();
  loadOfficialsStatus();
  loadSpecialists();
  loadCalendarData();
  loadDiagnostics();
  loadTickets();

  // Polling for live dashboard telemetry
  setInterval(loadDiagnostics, 15000);
  setInterval(loadOfficialsStatus, 10000);
  setInterval(loadSpecialists, 10000);
});

// Voice Call Mode Management
function initVoiceCallControls() {
  const toggleBtn = document.getElementById('voiceCallToggleBtn');
  const banner = document.getElementById('liveCallBanner');
  const endBtn = document.getElementById('endCallBtn');
  const muteBtn = document.getElementById('ttsVoiceToggle');
  const callBtnText = document.getElementById('callBtnText');

  toggleBtn.addEventListener('click', () => {
    if (!isVoiceCallActive) {
      startVoiceCall();
    } else {
      endVoiceCall();
    }
  });

  endBtn.addEventListener('click', endVoiceCall);

  muteBtn.addEventListener('click', () => {
    isVoiceMuted = !isVoiceMuted;
    muteBtn.textContent = isVoiceMuted ? '🔈 Unmute Voice' : '🔊 Mute Voice';
    if (isVoiceMuted && window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
  });

  function startVoiceCall() {
    isVoiceCallActive = true;
    toggleBtn.classList.add('in-call');
    callBtnText.textContent = 'In Call (Click to End)';
    banner.classList.remove('hidden');

    callSeconds = 0;
    updateCallTimer();
    callTimerInterval = setInterval(updateCallTimer, 1000);

    const welcome = "Thank you for calling Vittoris AI. I am your autonomous voice operations assistant. How can I assist you with our AI services, scheduling, or technical support today?";
    appendMessage('agent', `📞 **Live Voice Call Connected.**\n\n*${welcome}*`);
    speakVoice(welcome);
  }

  function endVoiceCall() {
    isVoiceCallActive = false;
    toggleBtn.classList.remove('in-call');
    callBtnText.textContent = 'Start Voice Call';
    banner.classList.add('hidden');

    if (callTimerInterval) clearInterval(callTimerInterval);
    if (window.speechSynthesis) window.speechSynthesis.cancel();

    appendMessage('system', '📞 *Voice call ended.*');
  }

  function updateCallTimer() {
    callSeconds++;
    const mins = String(Math.floor(callSeconds / 60)).padStart(2, '0');
    const secs = String(callSeconds % 60).padStart(2, '0');
    document.getElementById('callTimer').textContent = `${mins}:${secs}`;
  }
}

// Text-to-Speech (TTS)
function speakVoice(text) {
  if (isVoiceMuted || !('speechSynthesis' in window)) return;

  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 1.05;
  utterance.pitch = 1.0;

  const wave = document.getElementById('voiceWave');
  utterance.onstart = () => {
    if (wave) wave.classList.add('speaking');
  };
  utterance.onend = () => {
    if (wave) wave.classList.remove('speaking');
  };
  utterance.onerror = () => {
    if (wave) wave.classList.remove('speaking');
  };

  window.speechSynthesis.speak(utterance);
}

// Speech Recognition (Microphone Speech-to-Text)
function initSpeechRecognition() {
  const micBtn = document.getElementById('micBtn');
  const input = document.getElementById('userInput');

  const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRec) {
    micBtn.title = 'Speech Recognition not supported in this browser';
    micBtn.style.opacity = '0.5';
    return;
  }

  recognition = new SpeechRec();
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = 'en-US';

  let isListening = false;

  micBtn.addEventListener('click', () => {
    if (!isListening) {
      try {
        recognition.start();
        isListening = true;
        micBtn.classList.add('listening');
      } catch (e) {
        console.error(e);
      }
    } else {
      recognition.stop();
      isListening = false;
      micBtn.classList.remove('listening');
    }
  });

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    input.value = transcript;
    isListening = false;
    micBtn.classList.remove('listening');

    // Auto submit recognized voice input
    document.getElementById('chatForm').dispatchEvent(new Event('submit', { cancelable: true }));
  };

  recognition.onend = () => {
    isListening = false;
    micBtn.classList.remove('listening');
  };

  recognition.onerror = () => {
    isListening = false;
    micBtn.classList.remove('listening');
  };
}

// Chat Management
function initChat() {
  const form = document.getElementById('chatForm');
  const input = document.getElementById('userInput');
  const clearBtn = document.getElementById('clearChatBtn');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const msg = input.value.trim();
    if (!msg) return;

    appendMessage('user', msg);
    input.value = '';

    const typingMsg = appendMessage('agent', '⚡ *Autonomous voice agent analyzing request and operational telemetry...*');

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, message: msg })
      });
      const data = await res.json();

      typingMsg.remove();
      appendMessage('agent', data.text);

      // Play voice if in call
      if (isVoiceCallActive && data.voice_script) {
        speakVoice(data.voice_script);
      }

      // Check for actions
      if (data.action) {
        if (data.action.type && data.action.type.includes('booking')) {
          loadCalendarData();
        }
        if (data.action.type && data.action.type.includes('escalation')) {
          loadTickets();
        }
        if (data.action.type && data.action.type.includes('remediation')) {
          loadDiagnostics();
        }
        if (data.action.type && data.action.type.includes('warm_transfer')) {
          loadSpecialists();
        }
      }
    } catch (err) {
      typingMsg.remove();
      appendMessage('agent', '⚠️ Error contacting the agent server: ' + err.message);
    }
  });

  clearBtn.addEventListener('click', () => {
    const stream = document.getElementById('chatStream');
    stream.innerHTML = `
      <div class="message system-msg">
        <div class="msg-bubble">
          🔄 <strong>Session refreshed.</strong> Autonomous Agent ready.
        </div>
      </div>
    `;
  });
}

function appendMessage(sender, text) {
  const stream = document.getElementById('chatStream');
  const msgDiv = document.createElement('div');
  msgDiv.className = `message ${sender}-msg`;

  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';
  
  if (window.marked && typeof marked.parse === 'function') {
    bubble.innerHTML = marked.parse(text);
  } else {
    bubble.innerText = text;
  }

  msgDiv.appendChild(bubble);
  stream.appendChild(msgDiv);
  stream.scrollTop = stream.scrollHeight;
  return msgDiv;
}

// Quick Prompt Chips
function initQuickPrompts() {
  const chips = document.querySelectorAll('.chip');
  const input = document.getElementById('userInput');
  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      input.value = chip.getAttribute('data-prompt');
      input.focus();
    });
  });
}

// Tabs
function initTabs() {
  const tabBtns = document.querySelectorAll('.tab-btn');
  const panes = document.querySelectorAll('.tab-pane');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      panes.forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const targetId = btn.getAttribute('data-tab');
      document.getElementById(targetId).classList.add('active');
    });
  });

  document.getElementById('refreshRosterBtn').addEventListener('click', loadSpecialists);
  document.getElementById('refreshCalendarBtn').addEventListener('click', loadCalendarData);
  document.getElementById('runDiagBtn').addEventListener('click', loadDiagnostics);
  document.getElementById('refreshTicketsBtn').addEventListener('click', loadTickets);
  document.getElementById('saveOfficialStatusBtn').addEventListener('click', saveOfficialStatus);
}

// Specialists Roster & Warm Transfer
async function loadSpecialists() {
  const container = document.getElementById('specialistsList');
  try {
    const res = await fetch('/api/officials/roster');
    const data = await res.json();

    if (data.officials && data.officials.length > 0) {
      container.innerHTML = data.officials.map(o => `
        <div class="specialist-card ${o.is_available ? 'online' : 'busy'}">
          <div class="specialist-header">
            <div class="specialist-name-row">
              <span class="specialist-avatar">${o.avatar}</span>
              <div>
                <span class="specialist-name">${o.name}</span>
                <span style="font-size:10px; color:#9ca3af; margin-left:6px;">(${o.extension})</span>
              </div>
            </div>
            <span class="card-badge" style="background:${o.is_available ? '#065f46' : '#78350f'}; color:white;">
              ${o.status.replace(/_/g, ' ')}
            </span>
          </div>
          <div class="specialist-role">${o.role}</div>
          <div class="specialist-tags">
            ${o.specialties.slice(0, 5).map(s => `<span class="tag-badge">${s}</span>`).join('')}
          </div>
          <button class="transfer-btn" ${!o.is_available ? 'disabled' : ''} onclick="triggerWarmTransfer('${o.id}', '${o.name}')">
            📞 ${o.is_available ? 'Initiate Warm Transfer' : 'Official in Meetings (Unavailable)'}
          </button>
        </div>
      `).join('');
    }
  } catch (e) {
    container.innerHTML = '<p class="card-meta">Failed to load specialists directory.</p>';
  }
}

// Trigger Warm Transfer
async function triggerWarmTransfer(officialId, officialName) {
  appendMessage('user', `Please transfer me to ${officialName}.`);
  const typingMsg = appendMessage('agent', `⚡ *Agent initiating warm transfer protocol with ${officialName}...*`);

  try {
    const res = await fetch('/api/voice/transfer', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        official_id: officialId,
        name: 'Client',
        issue: 'Direct Warm Transfer Request'
      })
    });
    const data = await res.json();
    typingMsg.remove();

    if (data.transfer_status === 'CONNECTED') {
      const msg = `### 📞 Warm Call Transfer Connected!\n\n**Specialist:** ${data.official.name} (${data.official.extension})\n\n> *"${data.voice_announcement}"*\n\n---\n**Official Greeting:**\n*"${data.official_greeting}"*`;
      appendMessage('agent', msg);
      if (isVoiceCallActive) {
        speakVoice(`${data.voice_announcement} ${data.official_greeting}`);
      }
    } else {
      appendMessage('agent', `⚠️ ${data.voice_announcement}`);
      if (isVoiceCallActive) {
        speakVoice(data.voice_announcement);
      }
    }
  } catch (e) {
    typingMsg.remove();
    appendMessage('agent', 'Transfer error: ' + e.message);
  }
}

// Officials Status
async function loadOfficialsStatus() {
  try {
    const res = await fetch('/api/officials/status');
    const data = await res.json();
    const badgeText = document.getElementById('officialStatusText');
    const badge = document.getElementById('officialBadge');
    const dot = badge.querySelector('.status-dot');

    badgeText.textContent = `Officials: ${data.status.replace(/_/g, ' ')}`;

    if (data.status === 'AVAILABLE') {
      dot.className = 'status-dot active';
    } else {
      dot.className = 'status-dot warning';
    }
  } catch (e) {
    console.error('Error fetching official status:', e);
  }
}

async function saveOfficialStatus() {
  const selected = document.querySelector('input[name="officialStatusRadio"]:checked').value;
  try {
    await fetch('/api/officials/status', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: selected, notice: `Status updated to ${selected} via simulator.` })
    });
    loadOfficialsStatus();
    loadSpecialists();
    alert(`Officials status updated to: ${selected}`);
  } catch (e) {
    alert('Failed to update status: ' + e.message);
  }
}

// Calendar & Appointments Data
async function loadCalendarData() {
  const slotsDiv = document.getElementById('quickSlotsList');
  const confirmedDiv = document.getElementById('confirmedList');

  try {
    const [slotsRes, aptsRes] = await Promise.all([
      fetch('/api/slots?days=5'),
      fetch('/api/appointments')
    ]);
    const slotsData = await slotsRes.json();
    const aptsData = await aptsRes.json();

    if (slotsData.slots && slotsData.slots.length > 0) {
      slotsDiv.innerHTML = slotsData.slots.slice(0, 4).map(s => `
        <div class="card-item">
          <div class="card-title-row">
            <span class="card-title">🕒 ${s.formatted}</span>
            <span class="card-badge">Open Slot</span>
          </div>
          <div class="card-meta">Assigned: ${s.official} (${s.duration_minutes}m)</div>
        </div>
      `).join('');
    } else {
      slotsDiv.innerHTML = '<p class="card-meta">No open slots available.</p>';
    }

    if (aptsData.appointments && aptsData.appointments.length > 0) {
      confirmedDiv.innerHTML = aptsData.appointments.map(a => `
        <div class="card-item healthy">
          <div class="card-title-row">
            <span class="card-title">${a.customer_name}</span>
            <span class="card-badge" style="background:#065f46; color:#a7f3d0;">${a.id}</span>
          </div>
          <div class="card-meta">📧 ${a.customer_email}</div>
          <div class="card-meta">📅 ${a.slot_time}</div>
          <div class="card-meta" style="color:#6ee7b7; margin-top:4px;">Official: ${a.official_assigned}</div>
        </div>
      `).join('');
    } else {
      confirmedDiv.innerHTML = '<p class="card-meta" style="padding:8px 0;">No appointments booked yet. Ask the agent to schedule one!</p>';
    }
  } catch (e) {
    console.error('Error loading calendar data:', e);
  }
}

// Diagnostics Data
async function loadDiagnostics() {
  const container = document.getElementById('healthSummary');
  try {
    const res = await fetch('/api/diagnostics');
    const data = await res.json();

    let html = `
      <div style="margin-bottom:10px; display:flex; justify-content:space-between; align-items:center;">
        <span class="box-label">Global Telemetry Status</span>
        <span class="card-badge" style="background:${data.overall_status === 'OPERATIONAL' ? '#065f46' : '#7f1d1d'}; color:white;">
          ${data.overall_status}
        </span>
      </div>
    `;

    for (const [key, svc] of Object.entries(data.services)) {
      const isOk = svc.status === 'HEALTHY';
      html += `
        <div class="card-item ${isOk ? 'healthy' : 'danger'}">
          <div class="card-title-row">
            <span class="card-title">${svc.name}</span>
            <span class="card-badge">${svc.latency}</span>
          </div>
          <div class="card-meta">Uptime: ${svc.uptime} | ${svc.last_incident}</div>
        </div>
      `;
    }

    container.innerHTML = html;
  } catch (e) {
    container.innerHTML = '<p class="card-meta">Failed to reach diagnostics API.</p>';
  }
}

// Trigger Remediation Action
async function triggerRemediation(actionName) {
  try {
    const res = await fetch('/api/diagnostics/remediate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: actionName })
    });
    const data = await res.json();
    alert(`Autonomous Runbook Result:\n\n${data.result}`);
    loadDiagnostics();
  } catch (e) {
    alert('Remediation call failed: ' + e.message);
  }
}

// Escalation Tickets Data
async function loadTickets() {
  const container = document.getElementById('ticketsList');
  try {
    const res = await fetch('/api/tickets');
    const data = await res.json();

    if (data.tickets && data.tickets.length > 0) {
      container.innerHTML = data.tickets.map(t => `
        <div class="card-item warning">
          <div class="card-title-row">
            <span class="card-title">🚨 ${t.id} - ${t.category}</span>
            <span class="card-badge" style="background:#7c2d12; color:#fed7aa;">${t.urgency}</span>
          </div>
          <div class="card-meta" style="margin: 4px 0;"><strong>Customer:</strong> ${t.customer_name} (${t.customer_email})</div>
          <div class="card-meta"><strong>Assigned:</strong> ${t.assigned_official}</div>
          <div class="card-meta" style="margin-top:4px; font-style:italic;">"${t.summary}"</div>
        </div>
      `).join('');
    } else {
      container.innerHTML = '<p class="card-meta">No escalation tickets logged yet. Escalations trigger autonomously when official authority is required.</p>';
    }
  } catch (e) {
    container.innerHTML = '<p class="card-meta">Failed to load escalation tickets.</p>';
  }
}
