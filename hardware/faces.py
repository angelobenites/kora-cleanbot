import time
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw

# ==============================================================================
# 1. CONFIGURACIÓN DE HARDWARE (Tus parámetros exactos)
# ==============================================================================
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'regular'
options.disable_hardware_pulsing = True  # --led-no-hardware-pulse
options.gpio_slowdown = 4                # --led-slowdown-gpio=4

matrix = RGBMatrix(options=options)

# ==============================================================================
# 2. FUNCIONES DE EXPRESIONES ANIMADAS (64x32 píxeles)
# ==============================================================================

def animacion_alegre(duracion_seg=3):
    """Ojos sonrientes (arcos) que rebotan suavemente."""
    tiempo_inicio = time.time()
    offset = 0
    direccion = 1

    while (time.time() - tiempo_inicio) < duracion_seg:
        img = Image.new('RGB', (64, 32), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Color Amarillo/Verde brillante
        color = (0, 255, 100)
        
        # Ojo Izquierdo y Derecho (Arcos de sonrisa "^ ^")
        y = 12 + offset
        draw.arc([12, y, 26, y + 12], start=200, end=340, fill=color, width=3)
        draw.arc([38, y, 52, y + 12], start=200, end=340, fill=color, width=3)

        # Boca sonriente abajo
        draw.arc([24, 20, 40, 28], start=0, end=180, fill=color, width=2)

        matrix.SetImage(img)
        
        # Animación de rebote suave
        offset += direccion
        if offset > 2 or offset < 0:
            direccion *= -1
            
        time.sleep(0.12)


def animacion_enojado(duracion_seg=3):
    """Ojos rectangulares con cejas inclinadas hacia adentro e iluminación roja."""
    tiempo_inicio = time.time()
    
    while (time.time() - tiempo_inicio) < duracion_seg:
        img = Image.new('RGB', (64, 32), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        rojo = (255, 0, 0)

        # Ojos (Rectángulos)
        draw.rectangle([12, 12, 24, 24], fill=rojo)
        draw.rectangle([40, 12, 52, 24], fill=rojo)

        # Cejas enojadas (Líneas diagonales cortando la mirada)
        draw.line([10, 8, 26, 15], fill=(0, 0, 0), width=3)
        draw.line([54, 8, 38, 15], fill=(0, 0, 0), width=3)

        # Boca recta e inclinada
        draw.line([26, 26, 38, 25], fill=rojo, width=2)

        matrix.SetImage(img)
        time.sleep(0.1)


def animacion_triste(duracion_seg=3):
    """Ojos caídos con pupilas mirando hacia abajo y una lágrima parpadeante."""
    tiempo_inicio = time.time()
    mostrar_lagrima = True

    while (time.time() - tiempo_inicio) < duracion_seg:
        img = Image.new('RGB', (64, 32), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        azul = (0, 120, 255)

        # Ojos Tristes (Mirando abajo)
        draw.rectangle([12, 10, 24, 20], outline=azul, width=2)
        draw.rectangle([40, 10, 52, 20], outline=azul, width=2)
        
        # Pupilas abajo
        draw.rectangle([15, 16, 21, 20], fill=azul)
        draw.rectangle([43, 16, 49, 20], fill=azul)

        # Boca triste (Arco invertido)
        draw.arc([26, 22, 38, 28], start=180, end=360, fill=azul, width=2)

        # Lágrima animada en el ojo derecho
        if mostrar_lagrima:
            draw.line([40, 22, 40, 25], fill=(0, 200, 255), width=2)

        matrix.SetImage(img)
        mostrar_lagrima = not mostrar_lagrima
        time.sleep(0.3)


def animacion_sorprendido(duracion_seg=3):
    """Ojos circulares grandes que se dilatan y boca en forma de 'O'."""
    tiempo_inicio = time.time()
    radio_extra = 0
    creciendo = True

    while (time.time() - tiempo_inicio) < duracion_seg:
        img = Image.new('RGB', (64, 32), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        blanco = (255, 255, 255)

        r = radio_extra
        # Ojos dilatándose
        draw.ellipse([12 - r, 8 - r, 24 + r, 20 + r], fill=blanco)
        draw.ellipse([40 - r, 8 - r, 52 + r, 20 + r], fill=blanco)

        # Boca en 'O'
        draw.ellipse([28, 21, 36, 29], outline=blanco, width=2)

        matrix.SetImage(img)

        # Efecto de dilatación
        if creciendo:
            radio_extra += 1
            if radio_extra >= 2: creciendo = False
        else:
            radio_extra -= 1
            if radio_extra <= 0: creciendo = True

        time.sleep(0.15)


def animacion_serio(duracion_seg=3):
    """Ojos rectangulares neutros con parpadeo ocasional."""
    tiempo_inicio = time.time()
    
    while (time.time() - tiempo_inicio) < duracion_seg:
        img = Image.new('RGB', (64, 32), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        cyan = (0, 255, 255)

        # Ojos normales
        draw.rectangle([12, 10, 24, 20], fill=cyan)
        draw.rectangle([40, 10, 52, 20], fill=cyan)
        # Boca recta
        draw.line([26, 25, 38, 25], fill=cyan, width=2)

        matrix.SetImage(img)
        time.sleep(2.0)  # Mantiene la mirada fija

        # Animación de Parpadeo rápido
        img_parpadeo = Image.new('RGB', (64, 32), (0, 0, 0))
        draw_p = ImageDraw.Draw(img_parpadeo)
        draw_p.line([12, 15, 24, 15], fill=cyan, width=2)
        draw_p.line([40, 15, 52, 15], fill=cyan, width=2)
        draw_p.line([26, 25, 38, 25], fill=cyan, width=2)
        
        matrix.SetImage(img_parpadeo)
        time.sleep(0.12)

# ==============================================================================
# 3. BUCLE PRINCIPAL / SECUENCIA DEL ROBOT
# ==============================================================================
# try:
#     print("Iniciando expresiones del robot. Presiona Ctrl+C para salir.")
#     while True:
#         print("Expresión: Alegre")
#         animacion_alegre(duracion_seg=4)

#         print("Expresión: Sorprendido")
#         animacion_sorprendido(duracion_seg=3)

#         print("Expresión: Enojado")
#         animacion_enojado(duracion_seg=3)

#         print("Expresión: Triste")
#         animacion_triste(duracion_seg=4)

#         print("Expresión: Serio")
#         animacion_serio(duracion_seg=4)

# except KeyboardInterrupt:
#     print("\nApagando expresión...")
#     matrix.Clear()