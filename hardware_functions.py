from software_functions import kora_detect
from colorama import Fore, Back, Style, init
from gpiozero import OutputDevice
import time

init()
# motor = OutputDevice(17)

def clean_off():
     motor.off()
     print(Fore.WHITE + Back.RED + "System:" + Style.RESET_ALL + " Motor apagado.")

def clean(seg=7):
     try:
          print(Fore.WHITE + Back.GREEN + "System:" + Style.RESET_ALL + " Iniciando ciclo de limpieza...")
          motor.on()
          time.sleep(seg)
          clean_off()
     except KeyboardInterrupt:
          clean_off()
          print(Fore.WHITE + Back.YELLOW + "System:" + Style.RESET_ALL + " Limpieza interrumpida por el usuario.")


def detected_person():
     print(Fore.WHITE + Back.BLUE + "System:" + Style.RESET_ALL + " Persona detectada.")
     kora_detect("person")

def detected_waste():
     print(Fore.WHITE + Back.BLUE + "System:" + Style.RESET_ALL + " Basura detectada.")
     kora_detect("waste")

def detected_completed():
     print(Fore.WHITE + Back.BLUE + "System:" + Style.RESET_ALL + " Contenedor Lleno.")
     kora_detect("completed")