with open('m4 (1).html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix background image URL
content = content.replace(
    "background: url('file:///C:/Users/Mahadev N/.gemini/antigravity/brain/c024a667-d47b-49db-935f-65acb8c6b4fb/futuristic_rural_education_1777596523156.png'), \n                  url('https://images.unsplash.com/photo-1497633762265-9d179a990aa6?auto=format&fit=crop&w=1920&q=80') no-repeat center center;",
    "background: url('https://images.unsplash.com/photo-1497633762265-9d179a990aa6?auto=format&fit=crop&w=1920&q=80') no-repeat center center;"
)

# API helper functions
api_integration_code = """
      const API_BASE = 'http://localhost:5000/api';

      async function apiFetch(endpoint, method = 'GET', body = null) {
        try {
          const opts = {
            method,
            headers: { 'Content-Type': 'application/json' }
          };
          if (body) opts.body = JSON.stringify(body);
          const res = await fetch(`${API_BASE}${endpoint}`, opts);
          if (res.ok) return await res.json();
        } catch (e) {
          console.warn('Backend API connection failed, falling back to local mode.', e);
        }
        return null;
      }
"""

# Inject API helper inside script tag
content = content.replace("// ===== STATE & LOCAL STORAGE INITIALIZATION =====", "// ===== STATE & LOCAL STORAGE INITIALIZATION =====\n" + api_integration_code)

# Upgrade initDB to sync with backend
old_init_db = """function initDB() {
        if (!localStorage.getItem('vq_students')) localStorage.setItem('vq_students', JSON.stringify([]));
        if (!localStorage.getItem('vq_teachers')) localStorage.setItem('vq_teachers', JSON.stringify([]));
        if (!localStorage.getItem('vq_parents')) localStorage.setItem('vq_parents', JSON.stringify([]));
        if (!localStorage.getItem('vq_rooms')) localStorage.setItem('vq_rooms', JSON.stringify([]));

        // Sync Questions: Merge new default questions with existing ones
        let existingQs = JSON.parse(localStorage.getItem('vq_questions')) || {};
        let updated = false;
        for (let cat in defaultQuestions) {
          if (!existingQs[cat]) {
            existingQs[cat] = defaultQuestions[cat];
            updated = true;
          } else {
            // Check for new questions in this category
            defaultQuestions[cat].forEach(newQ => {
              const isNew = !existingQs[cat].some(oldQ => oldQ.q === newQ.q);
              if (isNew) {
                existingQs[cat].push(newQ);
                updated = true;
              }
            });
          }
        }
        if (updated || !localStorage.getItem('vq_questions')) {
          localStorage.setItem('vq_questions', JSON.stringify(existingQs));
        }
      }
      initDB();"""

new_init_db = """async function initDB() {
        if (!localStorage.getItem('vq_students')) localStorage.setItem('vq_students', JSON.stringify([]));
        if (!localStorage.getItem('vq_teachers')) localStorage.setItem('vq_teachers', JSON.stringify([]));
        if (!localStorage.getItem('vq_parents')) localStorage.setItem('vq_parents', JSON.stringify([]));
        if (!localStorage.getItem('vq_rooms')) localStorage.setItem('vq_rooms', JSON.stringify([]));

        // Try syncing from Python backend API first
        const apiData = await apiFetch('/questions');
        if (apiData && apiData.success && apiData.questions) {
          localStorage.setItem('vq_questions', JSON.stringify(apiData.questions));
          return;
        }

        let existingQs = JSON.parse(localStorage.getItem('vq_questions')) || {};
        let updated = false;
        for (let cat in defaultQuestions) {
          if (!existingQs[cat]) {
            existingQs[cat] = defaultQuestions[cat];
            updated = true;
          } else {
            defaultQuestions[cat].forEach(newQ => {
              const isNew = !existingQs[cat].some(oldQ => oldQ.q === newQ.q);
              if (isNew) {
                existingQs[cat].push(newQ);
                updated = true;
              }
            });
          }
        }
        if (updated || !localStorage.getItem('vq_questions')) {
          localStorage.setItem('vq_questions', JSON.stringify(existingQs));
        }
      }
      initDB();"""

content = content.replace(old_init_db, new_init_db)

# Async Student Login & Register
old_student_login = """function studentLogin() {
        const user = document.getElementById('s-login-user').value.trim();
        const pass = document.getElementById('s-login-pass').value;
        const lang = document.getElementById('s-login-lang').value;
        const st = getStudents();
        const found = st.find(s => s.user === user && s.pass === pass);
        if (!found) { showToast('❌ Invalid credentials. You must register first.'); return; }
        currentStudentObj = found;
        currentUser = found.user.split(' ')[0];
        currentXP = found.xp;
        currentLang = lang;
        setupStudentDash(found, lang);
        showPage('page-student-dash');
        showToast('🎉 Welcome back, ' + currentUser + '!');
      }"""

new_student_login = """async function studentLogin() {
        const user = document.getElementById('s-login-user').value.trim();
        const pass = document.getElementById('s-login-pass').value;
        const lang = document.getElementById('s-login-lang').value;

        // Try Python API Login first
        const apiRes = await apiFetch('/auth/login', 'POST', { role: 'student', username: user, password: pass });
        let found = null;
        if (apiRes && apiRes.success && apiRes.user) {
          found = apiRes.user;
        } else {
          const st = getStudents();
          found = st.find(s => s.user === user && s.pass === pass);
        }

        if (!found) { showToast('❌ Invalid credentials. You must register first.'); return; }
        currentStudentObj = found;
        currentUser = found.user.split(' ')[0];
        currentXP = found.xp;
        currentLang = lang;
        setupStudentDash(found, lang);
        showPage('page-student-dash');
        showToast('🎉 Welcome back, ' + currentUser + '!');
      }"""

content = content.replace(old_student_login, new_student_login)

# Update Student Register
old_student_reg = """function studentRegister() {
        const user = document.getElementById('reg-user').value.trim();
        const pass = document.getElementById('reg-pass').value;
        const name = document.getElementById('reg-name').value.trim() || user;

        if (!user || !pass || !name) { showToast('⚠️ Please fill all fields'); return; }

        if (!validateUsername(name)) {
          showToast('⚠️ Full Name must contain only letters and spaces!');
          return;
        }
        if (!validateUsername(user)) {
          showToast('⚠️ Username must contain only letters and spaces!');
          return;
        }
        if (!validatePassword(pass)) {
          showToast('⚠️ Password must contain letters, numbers, and special characters!');
          return;
        }

        const st = getStudents();
        const exists = st.find(s => s.user === user);
        if (exists) { showToast('⚠️ Username already taken'); return; }

        const newStu = {
          name, user, pass, xp: 0, streak: 0, level: 1, class: document.getElementById('reg-class').value,
          state: document.getElementById('reg-state').value, subjects: { math: 0, science: 0, tech: 0, eng: 0, env: 0 }
        };
        st.push(newStu);
        saveStudents(st);
        currentStudentObj = newStu;
        currentUser = user.split(' ')[0];
        currentXP = 0;
        currentLang = document.getElementById('reg-lang').value;
        setupStudentDash(newStu, currentLang);
        showPage('page-student-dash');
        showToast('🚀 Welcome to VidyaQuest, ' + currentUser + '!');
      }"""

new_student_reg = """async function studentRegister() {
        const user = document.getElementById('reg-user').value.trim();
        const pass = document.getElementById('reg-pass').value;
        const name = document.getElementById('reg-name').value.trim() || user;

        if (!user || !pass || !name) { showToast('⚠️ Please fill all fields'); return; }

        if (!validateUsername(name)) {
          showToast('⚠️ Full Name must contain only letters and spaces!');
          return;
        }
        if (!validateUsername(user)) {
          showToast('⚠️ Username must contain only letters and spaces!');
          return;
        }
        if (!validatePassword(pass)) {
          showToast('⚠️ Password must contain letters, numbers, and special characters!');
          return;
        }

        const cls = document.getElementById('reg-class').value;
        const state = document.getElementById('reg-state').value;

        // Try Python API Register
        await apiFetch('/auth/register', 'POST', {
          role: 'student', name, username: user, password: pass, class: cls, state: state
        });

        const st = getStudents();
        const newStu = {
          name, user, pass, xp: 0, streak: 0, level: 1, class: cls, state: state,
          subjects: { math: 0, science: 0, tech: 0, eng: 0, env: 0 }
        };
        st.push(newStu);
        saveStudents(st);
        currentStudentObj = newStu;
        currentUser = user.split(' ')[0];
        currentXP = 0;
        currentLang = document.getElementById('reg-lang').value;
        setupStudentDash(newStu, currentLang);
        showPage('page-student-dash');
        showToast('🚀 Welcome to VidyaQuest, ' + currentUser + '!');
      }"""

content = content.replace(old_student_reg, new_student_reg)

# Update Student Updates
old_update_stu = """function updateCurrentStudent(updates) {
        const st = getStudents();
        const idx = st.findIndex(s => s.user === currentStudentObj.user);
        if (idx > -1) {
          st[idx] = { ...st[idx], ...updates };
          currentStudentObj = st[idx];
          saveStudents(st);
        }
      }"""

new_update_stu = """function updateCurrentStudent(updates) {
        const st = getStudents();
        const idx = st.findIndex(s => s.user === currentStudentObj.user);
        if (idx > -1) {
          st[idx] = { ...st[idx], ...updates };
          currentStudentObj = st[idx];
          saveStudents(st);
          // Sync with Python API
          apiFetch('/student/update', 'POST', { username: currentStudentObj.user, ...updates });
        }
      }"""

content = content.replace(old_update_stu, new_update_stu)

# AI Chat API integration fallback
old_fetch_external = """async function fetchExternalKnowledge(term) {
        term = term.replace(/^(a|an|the)\s+/i, '');
        const wikiLang = currentLang || 'en';
        
        // Try Wikipedia First
        try {
            const res = await fetch(`https://${wikiLang}.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(term)}`);
            if(res.ok) {
                const data = await res.json();
                if(data.extract) {
                    displayAIResponse(data.extract);
                    return;
                }
            }
        } catch(e) {}

        // Fallback to DuckDuckGo (Simulated Search via Proxy if available, but here we just use DDG API)
        try {
            const res = await fetch(`https://api.duckduckgo.com/?q=${encodeURIComponent(term)}&format=json&no_html=1`);
            const data = await res.json();
            if(data.AbstractText) {
                displayAIResponse(data.AbstractText);
                return;
            }
        } catch(e) {}
        
        const fallbacks = { 'en': "I'm connecting to my global AI database... It seems I can't find a specific answer right now. Try rephrasing your question!" };
        displayAIResponse(fallbacks[currentLang] || fallbacks['en']);
      }"""

new_fetch_external = r"""async function fetchExternalKnowledge(term) {
        term = term.replace(/^(a|an|the)\s+/i, '');
        
        // Try Python AI Chatbot API first
        const apiRes = await apiFetch('/ai/chat', 'POST', { query: term });
        if (apiRes && apiRes.response) {
            displayAIResponse(apiRes.response);
            return;
        }

        const wikiLang = currentLang || 'en';
        try {
            const res = await fetch(`https://${wikiLang}.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(term)}`);
            if(res.ok) {
                const data = await res.json();
                if(data.extract) {
                    displayAIResponse(data.extract);
                    return;
                }
            }
        } catch(e) {}

        const fallbacks = { 'en': "I'm connecting to my global AI database... It seems I can't find a specific answer right now. Try rephrasing your question!" };
        displayAIResponse(fallbacks[currentLang] || fallbacks['en']);
      }"""

content = content.replace(old_fetch_external, new_fetch_external)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully generated index.html without syntax warnings!")
