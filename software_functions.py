import json
from colorama import Fore, Back, Style, init
from tts import kora_voice

init()

route = "models/kora-local-cleanbot.json"

def kora_detect(object="person"):
     if object == "person":
          print(" ")
          with open(route, 'r', encoding='utf-8') as file:
               data = json.load(file)
               kora_voice(data["greet"] or "Hola, por el momento no puedo hablar.")
               print(Back.MAGENTA + Fore.WHITE + "Kora:" + Style.RESET_ALL + " " + data["greet"] or "Hola, por el momento no puedo hablar.")
               
     elif object == "waste":
          print(" ")
          with open(route, 'r', encoding='utf-8') as file:
               data = json.load(file)
               kora_voice(data["waste"] or "Hola, por el momento no puedo hablar.")
               print(Back.MAGENTA + Fore.WHITE + "Kora:" + Style.RESET_ALL + " " + data["waste"] or "Hola, por el momento no puedo hablar.")

     elif object == "completed":
          print(" ")
          with open(route, 'r', encoding='utf-8') as file:
               data = json.load(file)
               kora_voice(data["download"] or "Hola, por el momento no puedo hablar.")
               print(Back.MAGENTA + Fore.WHITE + "Kora:" + Style.RESET_ALL + " " + data["download"] or "Hola, por el momento no puedo hablar.")

