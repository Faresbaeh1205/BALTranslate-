from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from gtts import gTTS
from deep_translator import GoogleTranslator
import io

app = FastAPI(title="BALTranslate SaaS")

class TranslationRequest(BaseModel):
    text: str
    source_lang: str = "auto"
    target_lang: str

@app.post("/api/translate")
def translate_text(req: TranslationRequest):
    try:
        translated = GoogleTranslator(source=req.source_lang, target=req.target_lang).translate(req.text)
        return {"original": req.text, "translated": translated, "target_lang": req.target_lang}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tts")
def text_to_speech(text: str, lang: str = "en"):
    try:
        tts = gTTS(text=text, lang=lang)
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return StreamingResponse(mp3_fp, media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
def serve_gui():
    return """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BALTranslate - 50+ Langues</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-900 text-white min-h-screen p-6 flex flex-col items-center">
        <h1 class="text-3xl font-bold mb-6 text-blue-400">BALTranslate</h1>
        
        <div class="w-full max-w-2xl bg-gray-800 p-6 rounded-xl shadow-lg space-y-4">
            <textarea id="inputText" placeholder="Entrez votre texte ici..." class="w-full p-3 bg-gray-700 rounded border border-gray-600 focus:outline-none h-32"></textarea>
            
            <div class="flex gap-4">
                <select id="targetLang" class="bg-gray-700 p-3 rounded border border-gray-600 w-full">
                    <option value="en">Anglais</option>
                    <option value="es">Espagnol</option>
                    <option value="ar">Arabe</option>
                    <option value="de">Allemand</option>
                    <option value="zh-CN">Chinois</option>
                    <option value="ru">Russe</option>
                    <option value="it">Italien</option>
                    <option value="pt">Portugais</option>
                    <option value="tr">Turc</option>
                    <option value="ja">Japonais</option>
                </select>
                <button onclick="translateAndPlay()" class="bg-blue-600 hover:bg-blue-500 font-bold px-6 py-3 rounded">Traduire & Écouter</button>
            </div>

            <div class="mt-4 p-4 bg-gray-700 rounded border border-gray-600">
                <h2 class="text-sm font-semibold text-gray-400">Traduction :</h2>
                <p id="outputText" class="text-lg mt-1 text-green-400">Le résultat s'affichera ici...</p>
            </div>
            
            <audio id="audioPlayer" controls class="w-full hidden mt-2"></audio>
        </div>

        <script>
            async function translateAndPlay() {
                const text = document.getElementById('inputText').value;
                const lang = document.getElementById('targetLang').value;
                if(!text) return;

                const res = await fetch('/api/translate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text: text, source_lang: 'auto', target_lang: lang})
                });
                const data = await res.json();
                document.getElementById('outputText').innerText = data.translated;

                const audio = document.getElementById('audioPlayer');
                audio.src = `/api/tts?text=${encodeURIComponent(data.translated)}&lang=${lang}`;
                audio.classList.remove('hidden');
                audio.play();
            }
        </script>
    </body>
    </html>
    """
