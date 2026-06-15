import asyncio
import edge_tts
import os
from colorama import Fore, Back, Style, init
import contextlib

init()

with contextlib.redirect_stdout(None):
    import pygame

pygame.mixer.init()

VOICE = "es-MX-DaliaNeural"
FILE_AUDIO = "output_kora.mp3"

def _reproducir_audio(file_route):
    """Reproduce el audio de forma síncrona asegurando liberar el archivo."""
    try:
        pygame.mixer.music.load(file_route)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload() 
        
        
        if os.path.exists(file_route):
            os.remove(file_route)
    except Exception:
        pass 

async def _hablar_async(text):
    """Únicamente genera y guarda el archivo MP3."""
    communicate = edge_tts.Communicate(
        text, 
        VOICE, 
        rate="+15%", 
        pitch="+5Hz"
    )
    await communicate.save(FILE_AUDIO)

def kora_voice(message):
    try:
        
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        
        loop.run_until_complete(_hablar_async(message))
        loop.close()
        
        
        _reproducir_audio(FILE_AUDIO)
        
    except (PermissionError, RuntimeError):
        
        
        print(Fore.WHITE + Back.BLUE + "System:" + Style.RESET_ALL + " Kora está ocupada hablando. Detección omitida.")
        
    except Exception as e:
        
        print(Fore.WHITE + Back.YELLOW + "System:" + Style.RESET_ALL + f" Error al reproducir el audio: {e}")
