from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from gtts import gTTS
from deep_translator import GoogleTranslator
import io
import google.generativeai as genai

app = FastAPI(title="BALTranslate Ultimate")

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
    "ja": "Japonais",
    "ko": "Coréen",
    "pt": "Portugais",
    "nl": "Néerlandais",
    "tr": "Turc"
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
            full_prompt = f"Contexte scanné :\n{req.context_text}\n\nQuestion : {req.prompt}"
            
        response = model.generate_content(full_prompt)
        return {"response": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur BalIA: {str(e)}")

@app.get("/", response_class=HTMLResponse)
def get_web_interface():
    options_html = "".join([f'<option value="{k}">{v}</option>' for k, v in LANGUAGES.items()])
    options_target = "".join([f'<option value="{k}">{v}</option>' for k, v in LANGUAGES.items() if k != "auto"])

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>BALTranslate Pro</title>
    <script src="https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js"></script>
    <style>
        :root {{
            --bg: #030712;
            --card-bg: rgba(17, 24, 39, 0.85);
            --neon-purple: #8b5cf6;
            --neon-blue: #3b82f6;
            --neon-glow: 0 0 20px rgba(139, 92, 246, 0.4);
            --text: #f9fafb;
            --text-muted: #9ca3af;
            --border: #1f2937;
        }}
        * {{ box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        body {{
            background-color: var(--bg);
            background-image: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #030712 70%);
            color: var(--text);
            margin: 0;
            padding: 12px;
            display: flex;
            justify-content: center;
            min-height: 100vh;
        }}
        .container {{
            width: 100%;
            max-width: 500px;
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            padding: 20px;
            border-radius: 24px;
            border: 1px solid rgba(139, 92, 246, 0.3);
            box-shadow: 0 10px 40px rgba(0,0,0,0.8), var(--neon-glow);
        }}
        .header h1 {{
            font-size: 1.8rem;
            margin: 0 0 4px 0;
            text-align: center;
            background: linear-gradient(135deg, #a78bfa, #60a5fa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 900;
        }}
        .subtitle {{ text-align: center; color: var(--text-muted); font-size: 0.8rem; margin-bottom: 18px; }}
        
        .nav-tabs {{
            display: flex;
            background: #090d16;
            padding: 4px;
            border-radius: 14px;
            gap: 6px;
            margin-bottom: 18px;
            border: 1px solid var(--border);
        }}
        .tab-btn {{
            flex: 1;
            padding: 12px;
            border: none;
            background: transparent;
            color: var(--text-muted);
            border-radius: 10px;
            font-weight: 700;
            font-size: 0.88rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        .tab-btn.active {{
            background: linear-gradient(135deg, var(--neon-purple), var(--neon-blue));
            color: #fff;
            box-shadow: var(--neon-glow);
        }}

        .section {{ display: none; }}
        .section.active {{ display: block; }}

        label {{ display: block; font-size: 0.75rem; font-weight: 700; color: #a78bfa; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; }}
        
        textarea, input[type="text"], input[type="password"], select {{
            width: 100%;
            background: #090d16;
            border: 1px solid var(--border);
            color: #fff;
            border-radius: 12px;
            padding: 12px;
            font-size: 0.92rem;
            outline: none;
            transition: border-color 0.3s;
        }}
        textarea {{ height: 110px; resize: none; }}
        textarea:focus, select:focus, input:focus {{ border-color: var(--neon-purple); box-shadow: 0 0 10px rgba(139, 92, 246, 0.3); }}

        .controls {{ display: flex; gap: 8px; margin: 10px 0; }}

        .file-upload-btn {{
            width: 100%;
            padding: 12px;
            background: #111827;
            border: 1px dashed var(--neon-purple);
            border-radius: 12px;
            color: #a78bfa;
            font-weight: 600;
            text-align: center;
            cursor: pointer;
            margin-bottom: 12px;
            display: block;
        }}

        .btn {{
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, var(--neon-purple), var(--neon-blue));
            color: white;
            border: none;
            border-radius: 12px;
            font-weight: 700;
            font-size: 0.95rem;
            cursor: pointer;
            box-shadow: var(--neon-glow);
        }}
        .btn:active {{ transform: scale(0.97); }}

        .chat-box {{
            height: 250px;
            overflow-y: auto;
            background: #090d16;
            border-radius: 12px;
            padding: 12px;
            border: 1px solid var(--border);
            margin-bottom: 10px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .msg {{ padding: 10px 12px; border-radius: 12px; max-width: 85%; font-size: 0.88rem; line-height: 1.4; }}
        .msg.user {{ background: linear-gradient(135deg, var(--neon-purple), var(--neon-blue)); color: white; align-self: flex-end; }}
        .msg.ai {{ background: #1f2937; color: var(--text); align-self: flex-start; border: 1px solid var(--border); }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>BALTranslate Pro ✨</h1>
            <div class="subtitle">Galerie • Traduction • Agent BalIA</div>
        </div>

        <div class="nav-tabs">
            <button class="tab-btn active" id="btnTransTab">🌐 Traducteur</button>
            <button class="tab-btn" id="btnAiTab">🤖 Agent BalIA</button>
        </div>

        <!-- TAB 1 -->
        <div id="transTab" class="section active">
            <label>📁 Galerie d'images :</label>
            <input type="file" id="imageInput" accept="image/*" style="display:none;">
            <label for="imageInput" class="file-upload-btn">🖼️ Importer une photo depuis la galerie</label>
            
            <div id="ocrStatus" style="text-align:center; font-size:0.8rem; color:#60a5fa; margin-bottom:8px;"></div>

            <label>Texte source :</label>
            <textarea id="sourceText" placeholder="Entrez votre texte ici ou importez une image..."></textarea>
            
            <div class="controls">
                <select id="sourceLang">{options_html}</select>
                <select id="targetLang">{options_target}</select>
            </div>

            <button class="btn" id="btnTranslate">Traduire maintenant</button>

            <label style="margin-top: 12px;">Résultat :</label>
            <textarea id="resultText" readonly placeholder="La traduction s'affichera ici..."></textarea>
        </div>

        <!-- TAB 2 -->
        <div id="aiTab" class="section">
            <label>Clé API Gemini :</label>
            <input type="password" id="geminiKey" placeholder="Collez votre clé API Gemini..." style="margin-bottom: 10px;">
            
            <div class="chat-box" id="chatBox">
                <div class="msg ai">مَرْحَبًا ! Je suis <b>BalIA</b>. Posez-moi vos questions !</div>
            </div>

            <div style="display: flex; gap: 6px;">
                <input type="text" id="aiInput" placeholder="Posez une question...">
                <button class="btn" id="btnSendAi" style="width: 80px;">OK</button>
            </div>
        </div>
    </div>

    <script>
        // Attendre que le DOM soit chargé pour attacher les événements proprement
        document.addEventListener('DOMContentLoaded', function() {{
            
            const btnTransTab = document.getElementById('btnTransTab');
            const btnAiTab = document.getElementById('btnAiTab');
            const transTab = document.getElementById('transTab');
            const aiTab = document.getElementById('aiTab');
            
            // Gestion du changement d'onglets
            btnTransTab.addEventListener('click', function() {{
                transTab.classList.add('active');
                aiTab.classList.remove('active');
                btnTransTab.classList.add('active');
                btnAiTab.classList.remove('active');
            }});

            btnAiTab.addEventListener('click', function() {{
                aiTab.classList.add('active');
                transTab.classList.remove('active');
                btnAiTab.classList.add('active');
                btnTransTab.classList.remove('active');
            }});

            // OCR via la Galerie
            document.getElementById('imageInput').addEventListener('change', async function() {{
                const status = document.getElementById('ocrStatus');
                if (!this.files || !this.files[0]) return;

                status.innerText = "⚡ Lecture de l'image en cours...";
                try {{
                    const worker = await Tesseract.createWorker('fra+eng');
                    const ret = await worker.recognize(this.files[0]);
                    document.getElementById('sourceText').value = ret.data.text;
                    status.innerText = "✅ Texte extrait avec succès !";
                    await worker.terminate();
                }} catch (e) {{
                    status.innerText = "❌ Erreur de lecture.";
                }}
            }});

            // Traduction
            document.getElementById('btnTranslate').addEventListener('click', async function() {{
                const text = document.getElementById('sourceText').value;
                const src = document.getElementById('sourceLang').value;
                const tgt = document.getElementById('targetLang').value;

                if (!text.trim()) {{
                    alert("Veuillez entrer du texte.");
                    return;
                }}

                document.getElementById('resultText').value = "Traduction en cours...";

                try {{
                    const res = await fetch('/translate', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{ text: text, source_lang: src, target_lang: tgt }})
                    }});
                    const data = await res.json();
                    document.getElementById('resultText').value = data.translated_text || data.detail;
                }} catch(e) {{
                    alert("Erreur de connexion lors de la traduction.");
                }}
            }});

            // Envoi à l'agent IA BalIA
            async function askAI() {{
                const input = document.getElementById('aiInput');
                const key = document.getElementById('geminiKey').value;
                const prompt = input.value.trim();
                const context = document.getElementById('sourceText').value;

                if (!prompt) return;
                if (!key) {{
                    alert("Veuillez saisir votre clé API Gemini.");
                    return;
                }}

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
                        chatBox.innerHTML += `<div class="msg ai">${{data.response.replace(/\\n/g, '<br>')}}</div>`;
                    }} else {{
                        chatBox.innerHTML += `<div class="msg ai" style="color:#ef4444;">${{data.detail}}</div>`;
                    }}
                }} catch (e) {{
                    chatBox.innerHTML += `<div class="msg ai" style="color:#ef4444;">Erreur réseau.</div>`;
                }}
                chatBox.scrollTop = chatBox.scrollHeight;
            }}

            document.getElementById('btnSendAi').addEventListener('click', askAI);
            document.getElementById('aiInput').addEventListener('keypress', function(e) {{
                if (e.key === 'Enter') askAI();
            }});
        }});
    </script>
</body>
</html>"""
