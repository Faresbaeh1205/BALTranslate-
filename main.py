from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from gTTS import gTTS
from deep_translator import GoogleTranslator
from google import genai
import io
import os

app = FastAPI(title="BALTranslate Pro & BalIA")

# Configuration du nouveau client officiel Google GenAI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AQ.Ab8RN6IsHJrC90Pxq5Ovn_T-s5TM4IGFmyWPyKQl0qBMzXRl1w")
client = genai.Client(api_key=GEMINI_API_KEY)

# Dictionnaire complet des langues supportées
LANGUAGES = {
    "auto": "Détection automatique", "af": "Afrikaans", "sq": "Albanais", "am": "Amharique", 
    "ar": "Arabe", "hy": "Arménien", "az": "Azerbaïdjanais", "eu": "Basque", "be": "Biélorusse", 
    "bn": "Bengali", "bs": "Bosnien", "bg": "Bulgare", "ca": "Catalan", "ceb": "Cebuanos", 
    "ny": "Chichewa", "zh-CN": "Chinois (Simplifié)", "zh-TW": "Chinois (Traditionnel)", 
    "co": "Corse", "hr": "Croate", "cs": "Tchèque", "da": "Danois", "nl": "Néerlandais", 
    "en": "Anglais", "eo": "Espéranto", "et": "Estonien", "tl": "Filipino", "fi": "Finnois", 
    "fr": "Français", "fy": "Frison", "gl": "Galicien", "ka": "Géorgien", "de": "Allemand", 
    "el": "Grec", "gu": "Gujarati", "ht": "Créole Haïtien", "ha": "Haoussa", "haw": "Hawaïen", 
    "iw": "Hébreu", "hi": "Hindi", "hmn": "Hmong", "hu": "Hongrois", "is": "Islandais", 
    "ig": "Igbo", "id": "Indonésien", "ga": "Irlandais", "it": "Italien", "ja": "Japonais", 
    "jw": "Javanais", "kn": "Kannada", "kk": "Kazakh", "km": "Khmer", "rw": "Kinyarwanda", 
    "ko": "Coréen", "ku": "Kurde", "ky": "Kirghize", "lo": "Lao", "la": "Latin", 
    "lv": "Letton", "lt": "Lituanien", "lb": "Luxembourgeois", "mk": "Macédonien", 
    "mg": "Malgache", "ms": "Malais", "ml": "Malayalam", "mt": "Maltais", "mi": "Maori", 
    "mr": "Marathi", "mn": "Mongol", "my": "Birman", "ne": "Népalais", "no": "Norvégien", 
    "or": "Odia", "ps": "Pachto", "fa": "Persan", "pl": "Polonais", "pt": "Portugais", 
    "pa": "Punjabi", "ro": "Roumains", "ru": "Russe", "sm": "Samoan", "gd": "Gaélique Écossais", 
    "sr": "Serbe", "st": "Sesotho", "sn": "Shona", "sd": "Sindhi", "si": "Cinghalais", 
    "sk": "Slovaque", "sl": "Slovène", "so": "Somali", "es": "Espagnol", "su": "Sundanais", 
    "sw": "Swahili", "sv": "Suédois", "tg": "Tadjik", "ta": "Tamoul", "tt": "Tatar", 
    "te": "Télougou", "th": "Thaï", "tr": "Turc", "tk": "Turkmène", "uk": "Ukrainien", 
    "ur": "Ourdou", "ug": "Ouïghour", "uz": "Ouzbek", "vi": "Vietnamien", "cy": "Gallois", 
    "xh": "Xhosa", "yi": "Yiddish", "yo": "Yoruba", "zu": "Zoulou"
}

class TranslationRequest(BaseModel):
    text: str
    source_lang: str = "auto"
    target_lang: str

class AIRequest(BaseModel):
    prompt: str
    context_text: str = ""

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
        tts_lang = lang if lang in ["fr", "en", "ar", "es", "de", "it", "ru", "zh-CN", "ja", "ko", "pt", "tr"] else "en"
        tts = gTTS(text=text, lang=tts_lang, slow=False)
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
        
    full_prompt = req.prompt
    if req.context_text.strip():
        full_prompt = f"Contexte scanné / texte actuel :\n{req.context_text}\n\nQuestion de l'utilisateur : {req.prompt}"

    # Appel via le nouveau SDK google-genai
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=full_prompt,
        )
        return {"response": response.text}
    except Exception:
        try:
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=full_prompt,
            )
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
    <title>BALTranslate Pro & BalIA</title>
    <script src="https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js"></script>
    <style>
        :root {{
            --bg: #030712;
            --card-bg: rgba(15, 23, 42, 0.85);
            --neon-purple: #a855f7;
            --neon-blue: #06b6d4;
            --neon-glow: 0 0 25px rgba(168, 85, 247, 0.35);
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --border: rgba(255, 255, 255, 0.12);
        }}
        * {{ box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        
        body {{
            background: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 12px;
            display: flex;
            justify-content: center;
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
        }}

        body::before {{
            content: '';
            position: fixed;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle at 20% 20%, #4c1d95 0%, transparent 40%),
                        radial-gradient(circle at 80% 80%, #0891b2 0%, transparent 40%),
                        radial-gradient(circle at 50% 50%, #831843 0%, transparent 50%);
            z-index: -1;
            animation: pulseBg 14s infinite alternate ease-in-out;
            filter: blur(65px);
        }}

        @keyframes pulseBg {{
            0% {{ transform: rotate(0deg) scale(1); }}
            100% {{ transform: rotate(8deg) scale(1.08); }}
        }}

        .container {{
            width: 100%;
            max-width: 500px;
            background: var(--card-bg);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            padding: 22px;
            border-radius: 28px;
            border: 1px solid var(--border);
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.9), var(--neon-glow);
        }}

        .header h1 {{
            font-size: 1.8rem;
            margin: 0 0 4px 0;
            text-align: center;
            background: linear-gradient(135deg, #c084fc, #38bdf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 900;
            letter-spacing: -0.5px;
        }}
        .subtitle {{ text-align: center; color: var(--text-muted); font-size: 0.8rem; margin-bottom: 18px; }}
        
        .nav-tabs {{
            display: flex;
            background: rgba(0, 0, 0, 0.4);
            padding: 4px;
            border-radius: 16px;
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
            border-radius: 12px;
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

        label {{ display: block; font-size: 0.75rem; font-weight: 700; color: #c084fc; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; }}
        
        textarea, input[type="text"], select {{
            width: 100%;
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid var(--border);
            color: #fff;
            border-radius: 14px;
            padding: 12px;
            font-size: 0.92rem;
            outline: none;
            transition: border-color 0.3s;
        }}
        textarea {{ height: 100px; resize: none; }}
        textarea:focus, select:focus, input:focus {{ border-color: var(--neon-purple); box-shadow: 0 0 12px rgba(168, 85, 247, 0.4); }}

        .controls {{ display: flex; gap: 8px; margin: 10px 0; }}

        .file-upload-btn {{
            width: 100%;
            padding: 12px;
            background: rgba(168, 85, 247, 0.1);
            border: 1px dashed var(--neon-purple);
            border-radius: 14px;
            color: #c084fc;
            font-weight: 600;
            text-align: center;
            cursor: pointer;
            margin-bottom: 12px;
            display: block;
            transition: 0.3s;
        }}
        .file-upload-btn:active {{ transform: scale(0.98); background: rgba(168, 85, 247, 0.2); }}

        .btn {{
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, var(--neon-purple), var(--neon-blue));
            color: white;
            border: none;
            border-radius: 14px;
            font-weight: 700;
            font-size: 0.95rem;
            cursor: pointer;
            box-shadow: var(--neon-glow);
            transition: 0.2s;
        }}
        .btn:active {{ transform: scale(0.97); }}

        .audio-btn {{
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid var(--border);
            color: #fff;
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 0.8rem;
            cursor: pointer;
            margin-top: 4px;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}

        .chat-box {{
            height: 280px;
            overflow-y: auto;
            background: rgba(0, 0, 0, 0.4);
            border-radius: 14px;
            padding: 12px;
            border: 1px solid var(--border);
            margin-bottom: 10px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .msg {{ padding: 10px 12px; border-radius: 14px; max-width: 85%; font-size: 0.88rem; line-height: 1.4; word-wrap: break-word; }}
        .msg.user {{ background: linear-gradient(135deg, var(--neon-purple), var(--neon-blue)); color: white; align-self: flex-end; }}
        .msg.ai {{ background: rgba(255, 255, 255, 0.08); color: var(--text); align-self: flex-start; border: 1px solid var(--border); }}
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
            
            <div id="ocrStatus" style="text-align:center; font-size:0.8rem; color:#38bdf8; margin-bottom:8px;"></div>

            <div style="display: flex; justify-content: space-between; align-items: center;">
                <label style="margin: 0;">Texte source :</label>
                <button class="audio-btn" id="btnPlaySourceAudio">🔊 Écouter</button>
            </div>
            <textarea id="sourceText" placeholder="Entrez votre texte ici ou importez une image..." style="margin-top: 6px;"></textarea>
            
            <div class="controls">
                <select id="sourceLang">{options_html}</select>
                <select id="targetLang">{options_target}</select>
            </div>

            <button class="btn" id="btnTranslate">Traduire maintenant</button>

            <div style="margin-top: 14px; display: flex; justify-content: space-between; align-items: center;">
                <label style="margin: 0;">Résultat :</label>
                <button class="audio-btn" id="btnPlayAudio">🔊 Écouter</button>
            </div>
            <textarea id="resultText" readonly placeholder="La traduction s'affichera ici..." style="margin-top: 6px;"></textarea>
        </div>

        <!-- TAB 2 -->
        <div id="aiTab" class="section">
            <div class="chat-box" id="chatBox">
                <div class="msg ai">مَرْحَبًا ! Je suis <b>BalIA</b>. Posez-moi toutes vos questions !</div>
            </div>

            <div style="display: flex; gap: 6px;">
                <input type="text" id="aiInput" placeholder="Posez une question à BalIA...">
                <button class="btn" id="btnSendAi" style="width: 80px;">OK</button>
            </div>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const btnTransTab = document.getElementById('btnTransTab');
            const btnAiTab = document.getElementById('btnAiTab');
            const transTab = document.getElementById('transTab');
            const aiTab = document.getElementById('aiTab');
            
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

            // OCR via Galerie d'images
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
                    status.innerText = "❌ Erreur de lecture de l'image.";
                }}
            }});

            // Envoi de la demande de traduction
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

            // Lecture Audio de la Traduction
            document.getElementById('btnPlayAudio').addEventListener('click', function() {{
                const text = document.getElementById('resultText').value;
                const lang = document.getElementById('targetLang').value;

                if (!text.trim() || text === "La traduction s'affichera ici...") {{
                    alert("Aucun texte à lire.");
                    return;
                }}

                const audioUrl = `/tts?text=${{encodeURIComponent(text)}}&lang=${{lang}}`;
                const audio = new Audio(audioUrl);
                audio.play();
            }});

            // Lecture Audio du Texte Source
            document.getElementById('btnPlaySourceAudio').addEventListener('click', function() {{
                const text = document.getElementById('sourceText').value;
                const lang = document.getElementById('sourceLang').value;

                if (!text.trim()) {{
                    alert("Aucun texte à lire.");
                    return;
                }}

                const audioUrl = `/tts?text=${{encodeURIComponent(text)}}&lang=${{lang}}`;
                const audio = new Audio(audioUrl);
                audio.play();
            }});

            // Discussion avec l'Agent BalIA
            async function askAI() {{
                const input = document.getElementById('aiInput');
                const prompt = input.value.trim();
                const context = document.getElementById('sourceText').value;

                if (!prompt) return;

                const chatBox = document.getElementById('chatBox');
                chatBox.innerHTML += `<div class="msg user">${{prompt}}</div>`;
                input.value = '';
                chatBox.scrollTop = chatBox.scrollHeight;

                try {{
                    const res = await fetch('/ai-chat', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{ prompt: prompt, context_text: context }})
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
