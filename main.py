from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from gtts import gTTS
from deep_translator import GoogleTranslator
import io
import google.generativeai as genai

app = FastAPI(title="BALTranslate Premium & BalIA")

# Dictionnaire complet des langues supportées
LANGUAGES = {
    "auto": "Détection automatique",
    "fr": "Français",
    "en": "Anglais",
    "ar": "Arabe",
    "es": "Espagnol",
    "de": "Allemand",
    "it": "Italien",
    "ru": "Russe",
    "zh-CN": "Chinois (Simplifié)",
    "zh-TW": "Chinois (Traditionnel)",
    "ja": "Japonais",
    "ko": "Coréen",
    "pt": "Portugais",
    "nl": "Néerlandais",
    "tr": "Turc",
    "pl": "Polonais",
    "uk": "Ukrainien",
    "ro": "Roumain",
    "el": "Grec",
    "hu": "Hongrois",
    "cs": "Tchèque",
    "sv": "Suédois",
    "da": "Danois",
    "fi": "Finnois",
    "no": "Norvégien",
    "hi": "Hindi",
    "bn": "Bengali",
    "id": "Indonésien",
    "vi": "Vietnamien",
    "th": "Thaï",
    "fa": "Persan",
    "ur": "Ourdou",
    "he": "Hébreu"
}

class TranslationRequest(BaseModel):
    text: str
    source_lang: str = "auto"
    target_lang: str

class AIRequest(BaseModel):
    prompt: str
    context_text: str = ""
    api_key: str = ""

@app.post("/translate")
def translate_text(req: TranslationRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Texte vide")
    try:
        translated = GoogleTranslator(source=req.source_lang, target=req.target_lang).translate(req.text)
        return {"translated_text": translated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tts")
def text_to_speech(text: str, lang: str = "fr"):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Texte vide")
    try:
        tts = gTTS(text=text, lang=lang if lang != "auto" else "fr", slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return StreamingResponse(fp, media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai-chat")
def ai_chat(req: AIRequest):
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Question vide")
    
    api_key = req.api_key.strip()
    if not api_key:
        raise HTTPException(status_code=400, detail="Veuillez fournir votre clé API Gemini")
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        full_prompt = req.prompt
        if req.context_text.strip():
            full_prompt = f"Contexte du document scanné/traduit :\n\"\"\"{req.context_text}\"\"\"\n\nQuestion de l'utilisateur : {req.prompt}"
            
        response = model.generate_content(full_prompt)
        return {"response": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur BalIA: {str(e)}")

@app.get("/", response_class=HTMLResponse)
def get_web_interface():
    options_html = "".join([f'<option value="{k}">{v}</option>' for k, v in LANGUAGES.items()])
    options_target = "".join([f'<option value="{k}">{v}</option>' for k, v in LANGUAGES.items() if k != "auto"])

    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BALTranslate Pro & Agent BalIA</title>
        <script src="https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js"></script>
        <style>
            :root {{
                --bg: #090d16;
                --card: #131c2e;
                --card-border: #1e293b;
                --accent: #6366f1;
                --accent-gradient: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
                --accent-hover: #4f46e5;
                --text: #f8fafc;
                --text-sub: #94a3b8;
                --border: #334155;
            }}
            * {{
                box-sizing: border-box;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background-color: var(--bg);
                color: var(--text);
                margin: 0;
                padding: 15px;
                display: flex;
                justify-content: center;
                min-height: 100vh;
            }}
            .container {{
                width: 100%;
                max-width: 680px;
                background: var(--card);
                padding: 24px;
                border-radius: 24px;
                box-shadow: 0 20px 50px rgba(0,0,0,0.6);
                border: 1px solid var(--border);
                display: flex;
                flex-direction: column;
            }}
            .header {{
                text-align: center;
                margin-bottom: 20px;
            }}
            h1 {{
                font-size: 1.8rem;
                margin: 0 0 6px 0;
                background: linear-gradient(to right, #818cf8, #c084fc, #f472b6);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-weight: 800;
                letter-spacing: -0.5px;
            }}
            .subtitle {{
                color: var(--text-sub);
                font-size: 0.88rem;
            }}
            
            /* Navigation par Onglets */
            .nav-tabs {{
                display: flex;
                background: #0b1120;
                padding: 5px;
                border-radius: 16px;
                gap: 6px;
                margin-bottom: 20px;
                border: 1px solid var(--border);
            }}
            .tab-btn {{
                flex: 1;
                padding: 12px;
                border: none;
                background: transparent;
                color: var(--text-sub);
                border-radius: 12px;
                font-weight: 700;
                font-size: 0.95rem;
                cursor: pointer;
                transition: all 0.25s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
            }}
            .tab-btn.active {{
                background: var(--accent-gradient);
                color: #ffffff;
                box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
            }}

            .section {{ display: none; }}
            .section.active {{ display: block; }}

            /* Formulaires & Textareas */
            label {{
                display: block;
                font-size: 0.82rem;
                font-weight: 600;
                color: var(--text-sub);
                margin-bottom: 6px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            textarea {{
                width: 100%;
                height: 120px;
                background: #0b1120;
                border: 1px solid var(--border);
                color: white;
                border-radius: 14px;
                padding: 12px;
                font-size: 0.95rem;
                resize: vertical;
                outline: none;
                transition: border-color 0.2s;
            }}
            textarea:focus {{
                border-color: #818cf8;
            }}
            .controls {{
                display: flex;
                gap: 10px;
                margin: 12px 0;
            }}
            select, input[type="file"], input[type="text"], input[type="password"] {{
                flex: 1;
                background: #0b1120;
                border: 1px solid var(--border);
                color: white;
                padding: 12px;
                border-radius: 12px;
                font-size: 0.9rem;
                outline: none;
            }}
            select:focus, input:focus {{
                border-color: #818cf8;
            }}

            /* Boutons */
            .btn {{
                width: 100%;
                padding: 14px;
                background: var(--accent-gradient);
                color: white;
                border: none;
                border-radius: 14px;
                font-weight: 700;
                font-size: 1rem;
                cursor: pointer;
                transition: opacity 0.2s, transform 0.1s;
                box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
            }}
            .btn:active {{
                transform: scale(0.98);
            }}
            .btn-action {{
                flex: 1;
                padding: 12px;
                border: none;
                border-radius: 12px;
                font-weight: 700;
                font-size: 0.9rem;
                cursor: pointer;
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 6px;
            }}

            .status {{
                text-align: center;
                font-size: 0.85rem;
                color: #818cf8;
                margin: 6px 0;
                font-weight: 500;
            }}

            /* Chat BalIA & Animations */
            .chat-box {{
                height: 270px;
                overflow-y: auto;
                background: #0b1120;
                border-radius: 14px;
                padding: 14px;
                border: 1px solid var(--border);
                margin-bottom: 12px;
                display: flex;
                flex-direction: column;
                gap: 10px;
            }}
            .msg {{
                padding: 10px 14px;
                border-radius: 14px;
                max-width: 85%;
                font-size: 0.92rem;
                line-height: 1.4;
            }}
            .msg.user {{
                background: var(--accent-gradient);
                color: white;
                align-self: flex-end;
                border-bottom-right-radius: 4px;
            }}
            .msg.ai {{
                background: #1e293b;
                color: var(--text);
                align-self: flex-start;
                border-bottom-left-radius: 4px;
                border: 1px solid var(--border);
            }}
            .typing-cursor {{
                display: inline-block;
                width: 6px;
                height: 14px;
                background-color: #818cf8;
                margin-left: 4px;
                animation: blink 0.8s infinite;
                vertical-align: middle;
            }}
            @keyframes blink {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>BALTranslate Pro ✨</h1>
                <div class="subtitle">Scanner Ultra-Rapide, Traduction Universelle & Agent BalIA</div>
            </div>

            <!-- BOUTONS / ONGLETS DE NAVIGATION PRINCIPAUX -->
            <div class="nav-tabs">
                <button class="tab-btn active" id="btnTransTab" onclick="switchTab('transTab', 'btnTransTab')">
                    🌐 Traduction & Scanner
                </button>
                <button class="tab-btn" id="btnAiTab" onclick="switchTab('aiTab', 'btnAiTab')">
                    🤖 Agent IA BalIA
                </button>
            </div>

            <!-- PAGE 1: TRADUCTION & OCR SCANNER -->
            <div id="transTab" class="section active">
                <label>📷 Scanner un document (Caméra / Galerie) :</label>
                <div class="controls">
                    <input type="file" id="imageInput" accept="image/*" capture="environment" onchange="processOCR()">
                </div>
                <div id="ocrStatus" class="status"></div>

                <label style="margin-top: 10px;">Texte source :</label>
                <textarea id="sourceText" placeholder="Saisissez du texte ou utilisez le scanner d'image ci-dessus..."></textarea>
                
                <div class="controls">
                    <select id="sourceLang">{options_html}</select>
                    <select id="targetLang">{options_target}</select>
                </div>

                <button class="btn" onclick="translateText()">Traduire maintenant</button>

                <label style="margin-top: 15px;">Résultat de traduction :</label>
                <textarea id="resultText" readonly placeholder="La traduction s'affichera ici instantanément..."></textarea>

                <div class="controls">
                    <button class="btn-action" style="background: #10b981;" onclick="playAudio()">🔊 Écouter</button>
                    <button class="btn-action" style="background: #8b5cf6;" onclick="askBalIAAboutDoc()">💬 Poser une question à BalIA</button>
                </div>
                <audio id="audioPlayer" style="display:none;"></audio>
            </div>

            <!-- PAGE 2: ESPACE AGENT IA BALIA -->
            <div id="aiTab" class="section">
                <label>Clé API (Gemini) :</label>
                <input type="password" id="geminiKey" placeholder="Entrez votre clé API pour activer BalIA..." style="width:100%; margin-bottom: 12px;">
                
                <div class="chat-box" id="chatBox">
                    <div class="msg ai" id="dynamicWelcome">
                        <span id="welcomeGreeting" style="font-weight:bold; color:#818cf8;"></span>
                        <br>
                        <span id="welcomeSubtext"></span><span class="typing-cursor"></span>
                    </div>
                </div>

                <div style="display: flex; gap: 8px;">
                    <input type="text" id="aiInput" placeholder="Posez une question à BalIA..." onkeypress="if(event.key==='Enter') askAI()">
                    <button class="btn-action" style="background: var(--accent-gradient); flex: none; width: 100px;" onclick="askAI()">Envoyer</button>
                </div>
            </div>
        </div>

        <script>
            // Animation des salutations en temps réel pour BalIA
            const greetings = ["Bonjour ! 👋", "Welcome ! 🌍", "Guten Tag ! ✨", "Bienvenido ! 🚀", "Marhaban ! 💬", "Konnichiwa ! 🌸"];
            const subtexts = [
                "Je suis L'Agent BalIA. En quoi puis-je vous aider aujourd'hui ?",
                "L'Agent BalIA répond à toutes vos questions instantanément !",
                "Posez-moi vos questions ou demandez-moi d'analyser vos documents scannés."
            ];

            let greetIndex = 0;
            let subIndex = 0;

            function updateWelcomeMessage() {{
                const greetEl = document.getElementById('welcomeGreeting');
                const subEl = document.getElementById('welcomeSubtext');
                
                if (greetEl && subEl) {{
                    greetEl.innerText = greetings[greetIndex];
                    
                    let text = subtexts[subIndex];
                    let charIndex = 0;
                    subEl.innerText = "";
                    
                    let typingInterval = setInterval(() => {{
                        if (charIndex < text.length) {{
                            subEl.innerText += text.charAt(charIndex);
                            charIndex++;
                        }} else {{
                            clearInterval(typingInterval);
                        }}
                    }}, 35);

                    greetIndex = (greetIndex + 1) % greetings.length;
                    subIndex = (subIndex + 1) % subtexts.length;
                }}
            }}

            window.onload = function() {{
                updateWelcomeMessage();
                setInterval(updateWelcomeMessage, 8000);
            }};

            function switchTab(tabId, btnId) {{
                document.querySelectorAll('.section').forEach(el => el.classList.remove('active'));
                document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
                
                document.getElementById(tabId).classList.add('active');
                document.getElementById(btnId).classList.add('active');
            }}

            // OCR instantané côté client avec Tesseract.js
            async function processOCR() {{
                const fileInput = document.getElementById('imageInput');
                const status = document.getElementById('ocrStatus');
                if (!fileInput.files[0]) return;

                status.innerText = "⚡ Analyse instantanée du document en cours...";
                try {{
                    const worker = await Tesseract.createWorker('fra+eng');
                    const ret = await worker.recognize(fileInput.files[0]);
                    document.getElementById('sourceText').value = ret.data.text;
                    status.innerText = "✅ Document lu avec succès !";
                    await worker.terminate();
                }} catch (e) {{
                    status.innerText = "❌ Erreur de lecture de l'image.";
                }}
            }}

            async function translateText() {{
                const text = document.getElementById('sourceText').value;
                const src = document.getElementById('sourceLang').value;
                const tgt = document.getElementById('targetLang').value;

                if (!text.trim()) return alert("Veuillez d'abord entrer du texte ou scanner un document.");

                const res = await fetch('/translate', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{ text: text, source_lang: src, target_lang: tgt }})
                }});
                const data = await res.json();
                document.getElementById('resultText').value = data.translated_text || data.detail;
            }}

            function playAudio() {{
                const text = document.getElementById('resultText').value || document.getElementById('sourceText').value;
                const lang = document.getElementById('targetLang').value;
                if (!text.trim()) return alert("Aucun texte disponible à lire.");

                const player = document.getElementById('audioPlayer');
                player.src = `/tts?text=${{encodeURIComponent(text)}}&lang=${{lang}}`;
                player.play();
            }}

            function askBalIAAboutDoc() {{
                switchTab('aiTab', 'btnAiTab');
                const aiInput = document.getElementById('aiInput');
                aiInput.value = "Peux-tu me résumer et m'expliquer ce document ?";
                aiInput.focus();
            }}

            async function askAI() {{
                const input = document.getElementById('aiInput');
                const key = document.getElementById('geminiKey').value;
                const prompt = input.value.trim();
                const context = document.getElementById('sourceText').value;

                if (!prompt) return;
                if (!key) return alert("Veuillez saisir votre clé API pour échanger avec BalIA.");

                const chatBox = document.getElementById('chatBox');
                chatBox.innerHTML += `<div class="msg user">${{prompt}}</div>`;
                input.value = '';
                chatBox.scrollTop = chatBox.scrollHeight;

                try {{
                    const res = await fetch('/ai-chat', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{ prompt: prompt, context_text: context, api_key: key }})
                    }});
                    const data = await res.json();
                    
                    if(data.response) {{
                        chatBox.innerHTML += `<div class="msg ai">${{data.response.replace(/\n/g, '<br>')}}</div>`;
                    }} else {{
                        chatBox.innerHTML += `<div class="msg ai" style="color:#ef4444;">Erreur: ${{data.detail}}</div>`;
                    }}
                }} catch (e) {{
                    chatBox.innerHTML += `<div class="msg ai" style="color:#ef4444;">Erreur de connexion avec l'agent BalIA.</div>`;
                }}
                chatBox.scrollTop = chatBox.scrollHeight;
            }}
        </script>
    </body>
    </html>
    """
    return html_content
