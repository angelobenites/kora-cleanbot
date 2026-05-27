from software_functions import kora_detected_person
from colorama import Fore, Back, Style, init

init()

def detected_person():
     print(Fore.WHITE + Back.BLUE + "System:" + Style.RESET_ALL + " Personal detectada.")
     kora_detected_person()