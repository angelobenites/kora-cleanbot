import json

# import pyttsx4

# engine = pyttsx4.init()
route = "models/kora-local-wordbot.json"

def kora_detected_person():
     with open(route, 'r', encoding='utf-8') as file:
          data = json.load(file)
     print(data["greet"] or "Hola, por el momento no puedo hablar.")
     # engine.say(message)
     # engine.runAndWait()

kora_detected_person()