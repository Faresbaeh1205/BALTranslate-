from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from gtts import gTTS
from deep_translator import GoogleTranslator
import io
import google.generativeai as genai

app = FastAPI(title="BALTranslate SaaS - BalIA")

# Dictionnaire des langues (100+ langues via deep-translator)
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
        raise HTTPException(status_code=400, detail="Le texte ne peut pas être vide.")
    try:
        translated = GoogleTranslator(source=req.source_lang, target=req.target_lang).translate(req.text)
        return {"translated_text": translated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tts")
def text_to_speech(text: str, lang: str = "fr"):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Le texte ne peut pas être vide.")
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
        raise HTTPException(status_code=400, detail="La question ne peut pas être vide.")
    
    api_key = req.api_key.strip()
    if not api_key:
        raise HTTPException(status_code=400, detail="Veuillez fournir une clé API.")
        
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
        <title>BALTranslate Pro & BalIA</title>
        <script src="https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js"></script>
        <style>
            :root {{
                --bg: #0f172a;
                --card: #1e293b;
                --accent: #6366f1;
                --accent-hover: #4f46e5;
                --text: #f8fafc;
                --text-sub: #94a3b8;
                --border: #334155;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background-color: var(--bg);
                color: var(--text);
                margin: 0;
                padding: 15px;
                display: flex;
                justify-content: center;
            }}
            .container {{
                width: 100%;
                max-width: 650px;
                background: var(--card);
                padding: 20px;
                border-radius: 20px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.5);
                border: 1px solid var(--border);
            }}
            h1 {{
                text-align: center;
                font-size: 1.5rem;
                margin-bottom: 5px;
                background: linear-gradient(to right, #818cf8, #c084fc);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            .subtitle {{
                text-align: center;
                color: var(--text-sub);
                font-size: 0.85rem;
                margin-bottom: 20px;
            }}
            .tabs {{
                display: flex;
                gap: 10px;
                margin-bottom: 15px;
            }}
            .tab-btn {{
                flex: 1;
                padding: 10px;
                border: none;
                background: #0f172a;
                color: var(--text-sub);
                border-radius: 10px;
                font-weight: bold;
                cursor: pointer;
            }}
            .tab-btn.active {{
                background: var(--accent);
                color: white;
            }}
            .section {{ display: none; }}
            .section.active {{ display: block; }}
            
            textarea {{
                width: 100%;
                height: 100px;
                background: #0f172a;
                border: 1px solid var(--border);
                color: white;
                border-radius: 12px;
                padding: 10px;
                box-sizing: border-box;
                font-size: 0.95rem;
                resize: vertical;
            }}
            .controls {{
                display: flex;
                gap: 10px;
                margin: 10px 0;
            }}
            select, input[type="file"], input[type="text"], input[type="password"] {{
                flex: 1;
                background: #0f172a;
                border: 1px solid var(--border);
                color: white;
                padding: 10px;
                border-radius: 10px;
                font-size: 0.9rem;
            }}
            button.btn {{
                width: 100%;
                padding: 12px;
                background: var(--accent);
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: bold;
                font-size: 1rem;
                cursor: pointer;
                margin-top: 5px;
            }}
            button.btn:active {{ background: var(--accent-hover); }}
            .status {{
                text-align: center;
                font-size: 0.85rem;
                color: #818cf8;
                margin-top: 5px;
            }}
            .chat-box {{
                height: 200px;
                overflow-y: auto;
                background: #0f172a;
                border-radius: 12px;
                padding: 10px;
                border: 1px solid var(--border);
                margin-bottom: 10px;
                display: flex;
                flex-direction: column;
                gap: 8px;
            }}
            .msg {{
                padding: 8px 12px;
                border-radius: 10px;
                max-width: 85%;
                font-size: 0.9rem;
            }}
            .msg.user {{ background: var(--accent); align-self: flex-end; }}
            .msg.ai {{ background: #334155; align-self: flex-start; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>BALTranslate Pro ✨</h1>
            <div class="subtitle">Scanner instantané, Traduction & Assistant BalIA</div>

            <div class="tabs">
                <button class="tab-btn active" onclick="switchTab(event, 'transTab')">🌐 Traducteur & OCR</button>
                <button class="tab-btn" onclick="switchTab(event, 'aiTab')">🤖 Agent BalIA</button>
            </div>

            <!-- ONGLET 1: TRADUCTION & OCR -->
            <div id="transTab" class="section active">
                <label style="font-size: 0.8rem; color: var(--text-sub);">Scanner un document (Caméra / Galerie) :</label>
                <div class="controls">
                    <input type="file" id="imageInput" accept="image/*" capture="environment" onchange="processOCR()">
                </div>
                <div id="ocrStatus" class="status"></div>

                <textarea id="sourceText" placeholder="Entrez votre texte ou scannez un document..."></textarea>
                
                <div class="controls">
                    <select id="sourceLang">{options_html}</select>
                    <select id="targetLang">{options_target}</select>
                </div>

                <button class="btn" onclick="translateText()">Traduire maintenant</button>

                <h3 style="margin-top: 15px; font-size: 1rem;">Résultat :</h3>
                <textarea id="resultText" readonly placeholder="La traduction s'affichera ici..."></textarea>

                <div class="controls">
                    <button class="btn" style="background: #10b981;" onclick="playAudio()">🔊 Écouter</button>
                    <button class="btn" style="background: #8b5cf6;" onclick="openBalIA()">💬 Poser une question à BalIA</button>
                </div>
                <audio id="audioPlayer" style="display:none;"></audio>
            </div>

            <!-- ONGLET 2: AGENT BALIA -->
            <div id="aiTab" class="section">
                <input type="password" id="geminiKey" placeholder="Entrez votre clé API BalIA / Gemini" style="width:100%; margin-bottom: 10px;">
                
                <div class="chat-box" id="chatBox">
                    <div class="msg ai">Bonjour ! Je suis BalIA, votre assistant virtuel. Posez-moi des questions sur vos documents scannés ou tout autre sujet.</div>
                </div>

                <div style="display: flex; gap: 5px;">
                    <input type="text" id="aiInput" placeholder="Posez votre question à BalIA..." onkeypress="if(event.key==='Enter') askAI()">
                    <button class="btn" style="width: auto; padding: 0 15px;" onclick="askAI()">Envoyer</button>
                </div>
            </div>
        </div>

        <script>
            function switchTab(evt, tabId) {{
                document.querySelectorAll('.section').forEach(el => el.classList.remove('active'));
                document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
                document.getElementById(tabId).classList.add('active');
                if (evt && evt.target) {{
                    evt.target.classList.add('active');
                }}
            }}

            async function processOCR() {{
                const fileInput = document.getElementById('imageInput');
                const status = document.getElementById('ocrStatus');
                if (!fileInput.files[0]) return;

                status.innerText = "⚡ Lecture du document en cours (OCR local)...";
                try {{
                    const worker = await Tesseract.createWorker('fra+eng');
                    const ret = await worker.recognize(fileInput.files[0]);
                    document.getElementById('sourceText').value = ret.data.text;
                    status.innerText = "✅ Lecture terminée avec succès !";
                    await worker.terminate();
                }} catch (e) {{
                    status.innerText = "❌ Erreur lors de la lecture de l'image.";
                }}
            }}

            async function translateText() {{
                const text = document.getElementById('sourceText').value;
                const src = document.getElementById('sourceLang').value;
                const tgt = document.getElementById('targetLang').value;

                if (!text.trim()) return alert("Veuillez saisir du texte.");

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
                if (!text.trim()) return alert("Aucun texte à lire.");

                const player = document.getElementById('audioPlayer');
                player.src = `/tts?text=${{encodeURIComponent(text)}}&lang=${{lang}}`;
                player.play();
            }}

            function openBalIA() {{
                const tabBtns = document.querySelectorAll('.tab-btn');
                switchTab(null, 'aiTab');
                tabBtns[1].classList.add('active');
                tabBtns[0].classList.remove('active');
                document.getElementById('aiInput').focus();
            }}

            async function askAI() {{
                const input = document.getElementById('aiInput');
                const key = document.getElementById('geminiKey').value;
                const prompt = input.value.trim();
                const context = document.getElementById('sourceText').value;

                if (!prompt) return;
                if (!key) return alert("Veuillez saisir votre clé API pour utiliser BalIA.");

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
                    chatBox.innerHTML += `<div class="msg ai" style="color:#ef4444;">Erreur de connexion avec BalIA.</div>`;
                }}
                chatBox.scrollTop = chatBox.scrollHeight;
            }}
        </script>
    </body>
    </html>
    """
    return html_content
