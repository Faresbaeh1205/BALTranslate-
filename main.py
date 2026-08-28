from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from gtts import gTTS
from deep_translator import GoogleTranslator
import io

app = FastAPI(title="BALTranslate Pro")

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

@app.get("/", response_class=HTMLResponse)
def get_web_interface():
    options_html = "".join([f'<option value="{k}">{v}</option>' for k, v in LANGUAGES.items()])
    options_target = "".join([f'<option value="{k}">{v}</option>' for k, v in LANGUAGES.items() if k != "auto"])

    html_content = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>BALTranslate Pro</title>
    <script src="https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
    <style>
        :root {
            --bg: #030712;
            --card-bg: rgba(15, 23, 42, 0.85);
            --neon-purple: #a855f7;
            --neon-blue: #06b6d4;
            --neon-glow: 0 0 25px rgba(168, 85, 247, 0.35);
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --border: rgba(255, 255, 255, 0.12);
        }
        * { box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        
        body {
            background: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 12px;
            display: flex;
            justify-content: center;
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
        }

        body::before {
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
        }

        @keyframes pulseBg {
            0% { transform: rotate(0deg) scale(1); }
            100% { transform: rotate(8deg) scale(1.08); }
        }

        .container {
            width: 100%;
            max-width: 520px;
            background: var(--card-bg);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            padding: 22px;
            border-radius: 28px;
            border: 1px solid var(--border);
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.9), var(--neon-glow);
        }

        .header h1 {
            font-size: 1.9rem;
            margin: 0 0 4px 0;
            text-align: center;
            background: linear-gradient(135deg, #c084fc, #38bdf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 900;
            letter-spacing: -0.5px;
        }
        .subtitle { text-align: center; color: var(--text-muted); font-size: 0.82rem; margin-bottom: 18px; }

        label { display: block; font-size: 0.75rem; font-weight: 700; color: #c084fc; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; }
        
        textarea, select {
            width: 100%;
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid var(--border);
            color: #fff;
            border-radius: 14px;
            padding: 12px;
            font-size: 0.92rem;
            outline: none;
            transition: border-color 0.3s;
        }
        textarea { height: 95px; resize: none; }
        textarea:focus, select:focus { border-color: var(--neon-purple); box-shadow: 0 0 12px rgba(168, 85, 247, 0.4); }

        .controls { display: flex; gap: 8px; margin: 10px 0; }

        .action-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            margin-bottom: 12px;
        }

        .file-upload-btn, .mic-btn {
            padding: 10px;
            background: rgba(168, 85, 247, 0.1);
            border: 1px dashed var(--neon-purple);
            border-radius: 14px;
            color: #c084fc;
            font-weight: 600;
            text-align: center;
            cursor: pointer;
            font-size: 0.85rem;
            transition: 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
        }
        .mic-btn.recording {
            background: rgba(239, 68, 68, 0.2);
            border-color: #ef4444;
            color: #fca5a5;
            animation: pulse 1s infinite;
        }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }

        .btn {
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
        }
        .btn:active { transform: scale(0.97); }

        .tool-bar {
            display: flex;
            gap: 6px;
            margin-top: 6px;
        }
        .tool-btn {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid var(--border);
            color: #fff;
            padding: 6px 10px;
            border-radius: 8px;
            font-size: 0.78rem;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }
        .tool-btn:hover { background: rgba(255, 255, 255, 0.15); }

        .history-box {
            margin-top: 18px;
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 10px;
            max-height: 120px;
            overflow-y: auto;
        }
        .history-item {
            font-size: 0.78rem;
            padding: 6px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            cursor: pointer;
            color: var(--text-muted);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .history-item:hover { color: #fff; background: rgba(255,255,255,0.05); }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>BALTranslate Pro ✨</h1>
            <div class="subtitle">Dictée Vocale • Scan Galerie • Export PDF</div>
        </div>

        <div class="action-grid">
            <input type="file" id="imageInput" accept="image/*" style="display:none;">
            <label for="imageInput" class="file-upload-btn">🖼️ Galerie photo</label>
            <button class="mic-btn" id="btnMic">🎙️ Dictée vocale</button>
        </div>

        <div id="ocrStatus" style="text-align:center; font-size:0.8rem; color:#38bdf8; margin-bottom:8px;"></div>

        <div style="display: flex; justify-content: space-between; align-items: center;">
            <label style="margin: 0;">Texte original :</label>
            <button class="tool-btn" id="btnPlaySourceAudio">🔊 Écouter</button>
        </div>
        <textarea id="sourceText" placeholder="Tapez votre texte ou dites une phrase..." style="margin-top: 6px;"></textarea>
        
        <div class="controls">
            <select id="sourceLang">__OPTIONS_SOURCE__</select>
            <select id="targetLang">__OPTIONS_TARGET__</select>
        </div>

        <button class="btn" id="btnTranslate">Traduire instantanément</button>

        <div style="margin-top: 14px; display: flex; justify-content: space-between; align-items: center;">
            <label style="margin: 0;">Résultat :</label>
            <div class="tool-bar">
                <button class="tool-btn" id="btnPlayAudio">🔊 Écouter</button>
                <button class="tool-btn" id="btnCopy">📋 Copier</button>
                <button class="tool-btn" id="btnPdf">📄 Export PDF</button>
            </div>
        </div>
        <textarea id="resultText" readonly placeholder="La traduction s'affichera ici..." style="margin-top: 6px;"></textarea>

        <div style="margin-top: 14px;">
            <label style="margin-bottom: 4px;">📜 Historique récent :</label>
            <div class="history-box" id="historyBox">
                <div style="font-size: 0.75rem; color: var(--text-muted); text-align: center;">Aucun historique pour le moment</div>
            </div>
        </div>
    </div>

    <div id="pdfTemplate" style="display:none; padding:20px; font-family:Arial; color:#1e293b;">
        <h2 style="color:#7c3aed; border-bottom:2px solid #7c3aed; padding-bottom:5px;">Rapport de Traduction - BALTranslate Pro</h2>
        <p style="font-size:12px; color:#64748b;">Généré automatiquement</p>
        <hr>
        <h3 style="color:#0f172a;">Texte Original :</h3>
        <p id="pdfSource" style="background:#f1f5f9; padding:12px; border-radius:8px; font-size:14px;"></p>
        <h3 style="color:#0f172a;">Traduction :</h3>
        <p id="pdfTarget" style="background:#f3e8ff; padding:12px; border-radius:8px; font-size:14px; color:#581c87;"></p>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const sourceText = document.getElementById('sourceText');
            const resultText = document.getElementById('resultText');
            const historyBox = document.getElementById('historyBox');

            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (SpeechRecognition) {
                const recognition = new SpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = false;
                
                const btnMic = document.getElementById('btnMic');
                btnMic.addEventListener('click', () => {
                    recognition.lang = document.getElementById('sourceLang').value === 'ar' ? 'ar-SA' : 'fr-FR';
                    try {
                        recognition.start();
                        btnMic.classList.add('recording');
                        btnMic.innerText = '🔴 Écoute en cours...';
                    } catch (e) {
                        recognition.stop();
                    }
                });

                recognition.onresult = (event) => {
                    sourceText.value = event.results[0][0].transcript;
                    btnMic.classList.remove('recording');
                    btnMic.innerText = '🎙️ Dictée vocale';
                };

                recognition.onerror = () => {
                    btnMic.classList.remove('recording');
                    btnMic.innerText = '🎙️ Dictée vocale';
                };

                recognition.onend = () => {
                    btnMic.classList.remove('recording');
                    btnMic.innerText = '🎙️ Dictée vocale';
                };
            } else {
                document.getElementById('btnMic').style.display = 'none';
            }

            document.getElementById('imageInput').addEventListener('change', async function() {
                const status = document.getElementById('ocrStatus');
                if (!this.files || !this.files[0]) return;

                status.innerText = "⚡ Lecture de l'image en cours...";
                try {
                    const worker = await Tesseract.createWorker('fra+eng');
                    const ret = await worker.recognize(this.files[0]);
                    sourceText.value = ret.data.text;
                    status.innerText = "✅ Texte extrait avec succès !";
                    await worker.terminate();
                } catch (e) {
                    status.innerText = "❌ Erreur de lecture de l'image.";
                }
            });

            document.getElementById('btnTranslate').addEventListener('click', async function() {
                const text = sourceText.value;
                const src = document.getElementById('sourceLang').value;
                const tgt = document.getElementById('targetLang').value;

                if (!text.trim()) {
                    alert("Veuillez entrer du texte.");
                    return;
                }

                resultText.value = "Traduction en cours...";

                try {
                    const res = await fetch('/translate', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ text: text, source_lang: src, target_lang: tgt })
                    });
                    const data = await res.json();
                    const translated = data.translated_text || data.detail;
                    resultText.value = translated;
                    
                    saveToHistory(text, translated);
                } catch(e) {
                    alert("Erreur lors de la traduction.");
                }
            });

            function saveToHistory(src, tgt) {
                let history = JSON.parse(localStorage.getItem('bal_history') || '[]');
                history.unshift({ src, tgt });
                if (history.length > 5) history.pop();
                localStorage.setItem('bal_history', JSON.stringify(history));
                renderHistory();
            }

            function renderHistory() {
                let history = JSON.parse(localStorage.getItem('bal_history') || '[]');
                if (history.length === 0) return;
                historyBox.innerHTML = '';
                history.forEach(item => {
                    const div = document.createElement('div');
                    div.className = 'history-item';
                    div.innerText = `▪ ${item.src} ➔ ${item.tgt}`;
                    div.onclick = () => {
                        sourceText.value = item.src;
                        resultText.value = item.tgt;
                    };
                    historyBox.appendChild(div);
                });
            }
            renderHistory();

            document.getElementById('btnCopy').addEventListener('click', () => {
                if (resultText.value) {
                    navigator.clipboard.writeText(resultText.value);
                    alert("Traduction copiée !");
                }
            });

            document.getElementById('btnPdf').addEventListener('click', () => {
                if (!resultText.value || resultText.value === "La traduction s'affichera ici...") {
                    alert("Veuillez d'abord effectuer une traduction.");
                    return;
                }
                document.getElementById('pdfSource').innerText = sourceText.value;
                document.getElementById('pdfTarget').innerText = resultText.value;
                
                const element = document.getElementById('pdfTemplate');
                element.style.display = 'block';
                html2pdf().from(element).save('Traduction_BALTranslate.pdf').then(() => {
                    element.style.display = 'none';
                });
            });

            document.getElementById('btnPlayAudio').addEventListener('click', function() {
                const text = resultText.value;
                const lang = document.getElementById('targetLang').value;
                if (!text.trim()) return;
                new Audio(`/tts?text=${encodeURIComponent(text)}&lang=${lang}`).play();
            });

            document.getElementById('btnPlaySourceAudio').addEventListener('click', function() {
                const text = sourceText.value;
                const lang = document.getElementById('sourceLang').value;
                if (!text.trim()) return;
                new Audio(`/tts?text=${encodeURIComponent(text)}&lang=${lang}`).play();
            });
        });
    </script>
</body>
</html>"""

    html_content = html_content.replace("__OPTIONS_SOURCE__", options_html)
    html_content = html_content.replace("__OPTIONS_TARGET__", options_target)
    
    return HTMLResponse(content=html_content)
