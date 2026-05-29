from software_functions import kora_detect
from colorama import Fore, Back, Style, init

init()

def detected_person():
     print(Fore.WHITE + Back.BLUE + "System:" + Style.RESET_ALL + " Persona detectada.")
     kora_detect("person")

def detected_waste():
     print(Fore.WHITE + Back.BLUE + "System:" + Style.RESET_ALL + " Basura detectada.")
     kora_detect("waste")

def detected_completed():
     print(Fore.WHITE + Back.BLUE + "System:" + Style.RESET_ALL + " Contenedor Lleno.")
     kora_detect("completed")


detected_completed()