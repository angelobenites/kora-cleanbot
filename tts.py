import asyncio
import edge_tts
import os
import contextlib

with contextlib.redirect_stdout(None):
    import pygame

pygame.mixer.init()

VOICE = "es-MX-DaliaNeural"
FILE_AUDIO = "output_kora.mp3"

def _reproducir_audio(file_route):
    pygame.mixer.music.load(file_route)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.music.unload()

async def _hablar_async(text):
    communicate = edge_tts.Communicate(
        text, 
        VOICE, 
        rate="+15%", 
        pitch="+5Hz"
    )
    await communicate.save(FILE_AUDIO)
    _reproducir_audio(FILE_AUDIO)
    if os.path.exists(FILE_AUDIO):
        os.remove(FILE_AUDIO)

def kora_voice(message):
    asyncio.run(_hablar_async(message))
