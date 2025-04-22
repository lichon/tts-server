import pathlib
import tts

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()
tts_service = tts.LocalTTSService()

@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(content=pathlib.Path("index.html").read_text('utf-8'), status_code=200)

@app.get("/tts")
def tts(txt: str):
    tts_service.speak_to_file(txt)
    return "OK"

@app.head("/tts")
def head_tts():
    return
