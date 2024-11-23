import speech_recognition as sr
import pyttsx3
import pygame
import requests
import threading
import time
import pyjokes
import webbrowser
from datetime import datetime
import random

# Configuración de la clave de API de Bing
api_key_bing = "e09520f150f24ebd863d98750e0a3980"

engine = pyttsx3.init()
engine.setProperty('rate', 150)

# Seleccionar la voz de Sabina en español
for voz in engine.getProperty('voices'):
    if "Microsoft Sabina Desktop - Spanish (Mexico)" in voz.name:
        engine.setProperty('voice', voz.id)
        break

# Rutas de imágenes de boca cerrada y abierta
ruta_imagen_normal = r"C:\Users\Edward\Downloads\cerrada boca.png"
ruta_imagen_hablando = r"C:\Users\Edward\Downloads\boca abierta.png"

# Tamaño de ventana de pygame
ancho, alto = 500, 500
pygame.init()
ventana = pygame.display.set_mode((ancho, alto))
pygame.display.set_caption('Animación de Voz - Felipe')
boca_abierta = pygame.image.load(ruta_imagen_hablando)
boca_cerrada = pygame.image.load(ruta_imagen_normal)

# Función para mostrar la boca abierta o cerrada
def mostrar_boca(abierta):
    ventana.fill((255, 255, 255))  # Fondo blanco
    if abierta:
        ventana.blit(boca_abierta, (ancho // 2 - boca_abierta.get_width() // 2, alto // 2 - boca_abierta.get_height() // 2))
    else:
        ventana.blit(boca_cerrada, (ancho // 2 - boca_cerrada.get_width() // 2, alto // 2 - boca_cerrada.get_height() // 2))
    pygame.display.flip()

# Animación de boca mientras habla
def animar_boca(duracion):
    tiempo_inicio = time.time()
    while time.time() - tiempo_inicio < duracion:
        mostrar_boca(True)
        time.sleep(0.25)
        mostrar_boca(False)
        time.sleep(0.25)
    mostrar_boca(False)

# Función para reproducir texto en voz y activar la animación
def hablar(texto):
    duracion_estimada = len(texto.split()) / 2  # Estima duración en segundos
    hilo_animacion = threading.Thread(target=animar_boca, args=(duracion_estimada,))
    hilo_animacion.start()
    
    engine.say(texto)
    engine.runAndWait()
    hilo_animacion.join()

# Función para abrir YouTube como música
def reproducir_musica():
    hablar("Abriendo YouTube para reproducir música")
    webbrowser.open("https://www.youtube.com")

# Función para contar un chiste
def contar_chiste():
    chiste = pyjokes.get_joke(language="es")
    hablar(chiste)

# Función para buscar el clima usando el API de Bing
def buscar_clima(ciudad):
    url = "https://api.bing.microsoft.com/v7.0/search"
    headers = {"Ocp-Apim-Subscription-Key": api_key_bing}
    params = {"q": f"clima en {ciudad}", "mkt": "es-ES", "count": 1}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        resultados = response.json()
        
        # Extrae el primer resultado
        resultado = resultados.get("webPages", {}).get("value", [])[0]
        descripcion = resultado["snippet"]
        
        hablar(f"Clima en {ciudad}: {descripcion}")
    except (requests.exceptions.RequestException, IndexError) as e:
        print(f"Error en la búsqueda de clima: {e}")
        hablar("Hubo un error al obtener el clima. Intenta de nuevo.")

# Función para dar consejos o frases motivacionales
def dar_consejo():
    consejos = [
        "Nunca es tarde para aprender algo nuevo.",
        "Recuerda que la perseverancia es la clave del éxito.",
        "Hoy es un buen día para empezar algo que te apasione.",
        "No te preocupes por los fracasos, aprende de ellos.",
        "A veces, solo necesitas dar un paso a la vez."
    ]
    consejo = random.choice(consejos)
    hablar(consejo)

# Función para mostrar menú de comandos
def mostrar_menu():
    comandos = [
        "1. Decir la hora actual. Di 'hora'.",
        "2. Buscar en Bing. Di 'buscar' seguido de lo que deseas buscar.",
        "3. Contar un chiste. Di 'chiste'.",
        "4. Reproducir música en YouTube. Di 'música'.",
        "5. Saber el clima en una ciudad. Di 'clima'.",
        "6. Recibir un consejo. Di 'consejo'.",
        "7. Salir. Di 'salir'."
    ]
    hablar("Estos son los comandos que puedes usar:")
    for comando in comandos:
        print(comando)
        hablar(comando)

# Función para escuchar la palabra clave "Felipe"
def escuchar_palabra_clave():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Esperando la palabra clave 'Felipe'...")

        while True:
            audio = recognizer.listen(source)
            try:
                texto = recognizer.recognize_google(audio, language="es-ES").lower()
                print(f"Escuchado: {texto}")

                if "felipe" in texto:
                    print("Palabra clave detectada.")
                    hablar("Hola, ¿cómo puedo ayudarte?")
                    mostrar_menu()  # Muestra el menú de comandos
                    escuchar_comando()  # Escucha el siguiente comando después de la activación
                    break
            except sr.UnknownValueError:
                print("No se entendió el audio.")
            except sr.RequestError:
                print("Error en el reconocimiento de voz.")

# Función para escuchar el comando después de activación
def escuchar_comando():
    while True:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Esperando el comando...")
            audio = recognizer.listen(source)

            try:
                comando = recognizer.recognize_google(audio, language="es-ES").lower()
                print(f"Comando detectado: {comando}")

                if "hora" in comando:
                    decir_hora()
                elif "buscar" in comando:
                    hablar("¿Qué te gustaría buscar?")
                    consulta = escuchar_respuesta()
                    if consulta:
                        buscar_bing(consulta)
                elif "chiste" in comando:
                    contar_chiste()
                elif "música" in comando:
                    reproducir_musica()
                elif "clima" in comando:
                    hablar("¿De qué ciudad quieres saber el clima?")
                    ciudad = escuchar_respuesta()
                    if ciudad:
                        buscar_clima(ciudad)
                elif "consejo" in comando:
                    dar_consejo()
                elif "salir" in comando:
                    hablar("Hasta luego.")
                    pygame.quit()
                    break
                else:
                    hablar("No entendí el comando.")
                
                # Pregunta si el usuario necesita algo más
                hablar("¿Necesitas algo más?")
                respuesta = escuchar_respuesta()
                
                if respuesta and "salir" in respuesta:
                    hablar("Hasta luego.")
                    pygame.quit()
                    break
                elif respuesta and "sí" in respuesta:
                    hablar("¿Qué deseas hacer?")
                    # Continúa el bucle para escuchar el próximo comando sin volver a activarse
                    continue
                else:
                    hablar("No entendí la respuesta.")
            except sr.UnknownValueError:
                hablar("No pude entender el comando.")
            except sr.RequestError:
                hablar("Error en el reconocimiento de voz.")
        return

# Función para escuchar una respuesta
def escuchar_respuesta():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Esperando respuesta...")
        audio = recognizer.listen(source)

        try:
            respuesta = recognizer.recognize_google(audio, language="es-ES").lower()
            print(f"Respuesta: {respuesta}")
            return respuesta
        except sr.UnknownValueError:
            hablar("No pude entender la respuesta.")
        except sr.RequestError:
            hablar("Error en el reconocimiento de voz.")
    return None

# Función para decir la hora actual
def decir_hora():
    hora_actual = datetime.now().strftime("%H:%M")
    hablar(f"La hora actual es {hora_actual}")

# Función para realizar búsquedas en Bing
def buscar_bing(consulta):
    url = "https://api.bing.microsoft.com/v7.0/search"
    headers = {"Ocp-Apim-Subscription-Key": api_key_bing}
    params = {"q": consulta, "mkt": "es-ES", "count": 1}  # Solo un resultado

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        resultados = response.json()

        # Toma el primer resultado
        resultado = resultados.get("webPages", {}).get("value", [])[0]
        titulo = resultado["name"]
        descripcion = resultado["snippet"]
        hablar(f"Título: {titulo}. Descripción: {descripcion}")
    except (requests.exceptions.RequestException, IndexError) as e:
        print(f"Error en la búsqueda de Bing: {e}")
        hablar("Hubo un error en la búsqueda. Intenta de nuevo.")

# Ejecutar el programa
escuchar_palabra_clave()
