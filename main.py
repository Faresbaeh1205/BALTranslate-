from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from gTTS import gTTS
from deep_translator import GoogleTranslator
import io

app = FastAPI(title="BALTranslate SaaS - OCR Scanner & 100+ Langues")

# Dictionnaire des 100+ langues
LANGUAGES = {
    "auto": "Détection automatique",
    "fr": "Français",
    "en": "Anglais (English)",
    "ar": "Arabe (Arabic)",
    "es": "Espagnol (Spanish)",
    "de": "Allemand (German)",
    "it": "Italien (Italian)",
    "pt": "Portugais (Portuguese)",
    "ru": "Russe (Russian)",
    "zh-CN": "Chinois Simplifié",
    "ja": "Japonais (Japanese)",
    "tr": "Turc (Turkish)",
    "nl": "Néerlandais (Dutch)",
    "pl": "Polonais (Polish)",
    "af": "Afrikaans", "sq": "Albanais", "am": "Amharique", "hy": "Arménien", "az": "Azéri", 
    "eu": "Basque", "be": "Bélarusse", "bn": "Bengali", "bs": "Bosniaque", "bg": "Bulgare", 
    "ca": "Catalan", "ceb": "Cebuan", "ny": "Chichewa", "zh-TW": "Chinois Traditionnel", 
    "co": "Corse", "hr": "Croate", "cs": "Tchèque", "da": "Danois", "eo": "Espéranto", 
    "et": "Estonien", "tl": "Filipino", "fi": "Finnois", "fy": "Frison", "gl": "Galicien", 
    "ka": "Géorgien", "el": "Grec", "gu": "Goudjarati", "ht": "Créole Haïtien", "ha": "Haoussa", 
    "haw": "Hawaïen", "he": "Hébreu", "hi": "Hindi", "hmn": "Hmong", "hu": "Hongrois", 
    "is": "Islandais", "ig": "Igbo", "id": "Indonésien", "ga": "Irlandais", "jv": "Javanais", 
    "kn": "Kannada", "kk": "Kazakh", "km": "Khmer", "rw": "Kinyarwanda", "ko": "Coréen", 
    "ku": "Kurde", "ky": "Kirghize", "lo": "Lao", "la": "Latin", "lv": "Letton", 
    "lt": "Lituanien", "lb": "Luxembourgeois", "mk": "Macédonien", "mg": "Malgache", 
    "ms": "Malais", "ml": "Malayalam", "mt": "Maltais", "mi": "Maori", "mr": "Marathi", 
    "mn": "Mongol", "my": "Birman", "ne": "Népalais", "no": "Norvégien", "or": "Odia", 
    "ps": "Pashto", "fa": "Persan", "pa": "Pendjabi", "ro": "Roumain", "sm": "Samoan", 
    "gd": "Gaélique Écossais", "sr": "Serbe", "st": "Sesotho", "sn": "Shona", "sd": "Sindhi", 
    "si": "Cinghalais", "sk": "Slovaque", "sl": "Slovène", "so": "Somali", "su": "Sundanais", 
    "sw": "Swahili", "sv": "Suédois", "tg": "Tadjik", "ta": "Tamoul", "tt": "Tatar", 
    "te": "Télougou", "th": "Thaï", "tk": "Turkmène", "uk": "Ukrainien", "ur": "Ourdou", 
    "ug": "Ouïghour", "uz": "Ouzbek", "vi": "Vietnamien", "cy": "Gallois", "xh": "Xhosa", 
    "yi": "Yiddish", "yo": "Yoruba", "zu": "Zoulou"
}

class TranslationRequest(BaseModel):
    text: str
    source_lang: str = "auto"
    target_lang: str = "fr"

@app.post("/api/translate")
def translate_text(req: TranslationRequest):
    if not req.text.strip():
        return {"original": "", "translated": "", "target_lang": req.target_lang}
    try:
        translated = GoogleTranslator(source=req.source_lang, target=req.target_lang).translate(req.text)
        return {"original": req.text, "translated": translated, "target_lang": req.target_lang}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de traduction: {str(e)}")

@app.get("/api/tts")
def text_to_speech(text: str, lang: str = "fr"):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Texte vide")
    try:
        clean_lang = lang.split('-')[0] if '-' in lang else lang
        tts = gTTS(text=text, lang=clean_lang)
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return StreamingResponse(mp3_fp, media_type="audio/mpeg")
    except Exception:
        try:
            tts = gTTS(text=text, lang="en")
            mp3_fp = io.BytesIO()
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)
            return StreamingResponse(mp3_fp, media_type="audio/mpeg")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur d'audio: {str(e)}")

@app.get("/", response_class=HTMLResponse)
def serve_gui():
    source_options = "".join([f'<option value="{code}" {"selected" if code=="auto" else ""}>{name}</option>' for code, name in LANGUAGES.items()])
    target_options = "".join([f'<option value="{code}" {"selected" if code=="fr" else ""}>{name}</option>' for code, name in LANGUAGES.items() if code != "auto"])

    return f"""
    <!DOCTYPE html>
    <html lang="fr" class="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BALTranslate - Scanner IA & Traduction 100+ Langues</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            body {{ font-family: 'Inter', sans-serif; }}
            .custom-scrollbar::-webkit-scrollbar {{ width: 6px; }}
            .custom-scrollbar::-webkit-scrollbar-track {{ background: #1f2937; }}
            .custom-scrollbar::-webkit-scrollbar-thumb {{ background: #374151; border-radius: 3px; }}
        </style>
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col items-center justify-between p-4 md:p-8">
        
        <header class="w-full max-w-5xl flex items-center justify-between py-4 border-b border-slate-800 mb-6">
            <div class="flex items-center space-x-3">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center shadow-lg shadow-indigo-500/30">
                    <i class="fa-solid fa-camera-rotate text-white text-xl"></i>
                </div>
                <div>
                    <h1 class="text-xl font-bold bg-gradient-to-r from-indigo-400 to-pink-400 bg-clip-text text-transparent">BALTranslate AI</h1>
                    <p class="text-xs text-slate-400">Scanner Caméra & Traducteur Vocal Multi-Langues</p>
                </div>
            </div>
            <span class="px-3 py-1 text-xs font-semibold rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                PRO + OCR
            </span>
        </header>

        <main class="w-full max-w-5xl bg-slate-900/80 backdrop-blur-md rounded-2xl border border-slate-800 p-4 md:p-6 shadow-2xl space-y-6">
            
            <!-- Controls Bar -->
            <div class="grid grid-cols-1 md:grid-cols-[1fr,auto,1fr] gap-3 items-center">
                <div class="relative">
                    <label class="block text-xs font-medium text-slate-400 mb-1">Langue source</label>
                    <select id="sourceLang" class="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-indigo-500 transition-colors custom-scrollbar">
                        {source_options}
                    </select>
                </div>

                <div class="flex justify-center md:pt-5">
                    <button onclick="swapLanguages()" title="Inverser les langues" class="w-10 h-10 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 flex items-center justify-center text-slate-300 transition-all hover:scale-105 active:scale-95">
                        <i class="fa-solid fa-arrows-rotate"></i>
                    </button>
                </div>

                <div class="relative">
                    <label class="block text-xs font-medium text-slate-400 mb-1">Langue cible</label>
                    <select id="targetLang" class="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-indigo-500 transition-colors custom-scrollbar">
                        {target_options}
                    </select>
                </div>
            </div>

            <!-- Translation Boxes Grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                
                <!-- Input Box -->
                <div class="flex flex-col bg-slate-950/60 border border-slate-800 rounded-xl p-4 focus-within:border-indigo-500/50 transition-colors">
                    <div class="flex justify-between items-center mb-2">
                        <span class="text-xs font-medium text-slate-400">Texte ou Document Photo</span>
                        <span id="charCount" class="text-xs text-slate-500">0 / 5000</span>
                    </div>

                    <textarea id="inputText" maxlength="5000" placeholder="Saisissez votre texte ou scannez un document..." class="w-full h-44 bg-transparent resize-none border-none focus:outline-none text-slate-200 placeholder-slate-600 custom-scrollbar text-base"></textarea>
                    
                    <div class="flex justify-between items-center pt-2 border-t border-slate-800/60 gap-2">
                        <!-- Camera Scanner Input -->
                        <label class="cursor-pointer bg-slate-800 hover:bg-slate-700 text-indigo-400 border border-indigo-500/30 hover:border-indigo-500 font-medium px-3 py-2 rounded-lg text-xs transition-all flex items-center gap-1.5 active:scale-95">
                            <i class="fa-solid fa-camera"></i>
                            <span>Scanner Photo</span>
                            <input type="file" id="cameraInput" accept="image/*" capture="environment" class="hidden" onchange="scanDocument(event)">
                        </label>

                        <div class="flex items-center gap-2">
                            <button onclick="clearText()" class="text-xs text-slate-500 hover:text-slate-300 transition-colors px-2 py-2">
                                <i class="fa-solid fa-trash"></i>
                            </button>
                            <button onclick="translateText()" class="bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-4 py-2 rounded-lg text-xs transition-all shadow-lg shadow-indigo-600/20 active:scale-95 flex items-center gap-1.5">
                                <span>Traduire</span>
                                <i class="fa-solid fa-arrow-right"></i>
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Output Box -->
                <div class="flex flex-col bg-slate-950/60 border border-slate-800 rounded-xl p-4 relative">
                    <div class="flex justify-between items-center mb-2">
                        <span class="text-xs font-medium text-indigo-400 flex items-center gap-1.5">
                            <i class="fa-solid fa-sparkles text-xs"></i> Traduction
                        </span>
                        <div class="flex items-center gap-2">
                            <button id="ttsBtn" onclick="playAudio()" title="Écouter la prononciation" class="hidden text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5">
                                <i class="fa-solid fa-volume-high text-indigo-400"></i> Écouter
                            </button>
                            <button id="copyBtn" onclick="copyResult()" title="Copier le texte" class="hidden text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5">
                                <i class="fa-regular fa-copy"></i> Copier
                            </button>
                        </div>
                    </div>
                    
                    <div id="outputContainer" class="w-full h-44 overflow-y-auto custom-scrollbar text-base text-slate-200 py-1">
                        <span class="text-slate-600 italic">Prenez une photo d'un document ou tapez du texte...</span>
                    </div>

                    <!-- Loaders -->
                    <div id="loader" class="hidden absolute inset-0 bg-slate-950/85 backdrop-blur-sm rounded-xl flex flex-col items-center justify-center gap-2">
                        <div class="w-8 h-8 border-3 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                        <span id="loaderMsg" class="text-xs text-slate-300 font-medium">Traduction en cours...</span>
                    </div>
                </div>
            </div>

            <audio id="audioPlayer" class="hidden"></audio>
        </main>

        <footer class="mt-8 text-center text-xs text-slate-500">
            BALTranslate SaaS &copy; 2026 — Scanner OCR & IA Multilingue.
        </footer>

        <script>
            const inputText = document.getElementById('inputText');
            const outputContainer = document.getElementById('outputContainer');
            const sourceLang = document.getElementById('sourceLang');
            const targetLang = document.getElementById('targetLang');
            const charCount = document.getElementById('charCount');
            const loader = document.getElementById('loader');
            const loaderMsg = document.getElementById('loaderMsg');
            const ttsBtn = document.getElementById('ttsBtn');
            const copyBtn = document.getElementById('copyBtn');
            const audioPlayer = document.getElementById('audioPlayer');

            let currentTranslation = "";

            inputText.addEventListener('input', () => {{
                charCount.innerText = `${{inputText.value.length}} / 5000`;
            }});

            async function scanDocument(event) {{
                const file = event.target.files[0];
                if (!file) return;

                loader.classList.remove('hidden');
                loaderMsg.innerText = "Analyse OCR de l'image en cours...";

                try {{
                    const worker = await Tesseract.createWorker('eng+fra+spa+ara');
                    const ret = await worker.recognize(file);
                    await worker.terminate();

                    const extractedText = ret.data.text.trim();
                    if(extractedText) {{
                        inputText.value = extractedText;
                        charCount.innerText = `${{extractedText.length}} / 5000`;
                        await translateText();
                    }} else {{
                        alert("Aucun texte lisible détecté sur l'image.");
                    }}
                }} catch (err) {{
                    alert("Erreur lors du scan du document: " + err.message);
                }} finally {{
                    loader.classList.add('hidden');
                }}
            }}

            async function translateText() {{
                const text = inputText.value.trim();
                if(!text) return;

                loader.classList.remove('hidden');
                loaderMsg.innerText = "Traduction en cours...";

                try {{
                    const res = await fetch('/api/translate', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{
                            text: text,
                            source_lang: sourceLang.value,
                            target_lang: targetLang.value
                        }})
                    }});

                    const data = await res.json();
                    if(res.ok) {{
                        currentTranslation = data.translated;
                        outputContainer.innerHTML = `<p class="whitespace-pre-wrap">${{data.translated}}</p>`;
                        ttsBtn.classList.remove('hidden');
                        copyBtn.classList.remove('hidden');
                    }} else {{
                        outputContainer.innerHTML = `<span class="text-red-400">Erreur: ${{data.detail}}</span>`;
                    }}
                }} catch(err) {{
                    outputContainer.innerHTML = `<span class="text-red-400">Erreur de connexion au serveur</span>`;
                }} finally {{
                    loader.classList.add('hidden');
                }}
            }}

            async function playAudio() {{
                if(!currentTranslation) return;
                const lang = targetLang.value;
                ttsBtn.innerHTML = `<i class="fa-solid fa-spinner animate-spin text-indigo-400"></i> Chargement...`;
                
                audioPlayer.src = `/api/tts?text=${{encodeURIComponent(currentTranslation)}}&lang=${{lang}}`;
                
                audioPlayer.play().then(() => {{
                    ttsBtn.innerHTML = `<i class="fa-solid fa-volume-high text-indigo-400"></i> Écouter`;
                }}).catch(() => {{
                    ttsBtn.innerHTML = `<i class="fa-solid fa-volume-high text-indigo-400"></i> Écouter`;
                }});
            }}

            function copyResult() {{
                if(!currentTranslation) return;
                navigator.clipboard.writeText(currentTranslation);
                copyBtn.innerHTML = `<i class="fa-solid fa-check text-green-400"></i> Copié!`;
                setTimeout(() => {{
                    copyBtn.innerHTML = `<i class="fa-regular fa-copy"></i> Copier`;
                }}, 2000);
            }}

            function swapLanguages() {{
                if(sourceLang.value === 'auto') return;
                const temp = sourceLang.value;
                sourceLang.value = targetLang.value;
                targetLang.value = temp;
                if(inputText.value.trim()) translateText();
            }}

            function clearText() {{
                inputText.value = "";
                outputContainer.innerHTML = `<span class="text-slate-600 italic">Prenez une photo d'un document ou tapez du texte...</span>`;
                charCount.innerText = "0 / 5000";
                ttsBtn.classList.add('hidden');
                copyBtn.classList.add('hidden');
                currentTranslation = "";
            }}
        </script>
    </body>
    </html>
    """
