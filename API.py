import random
import requests

# 1. Llamamos a la API de preguntas y respuestas
url = 'https://the-trivia-api.com/v2/questions'

response = requests.get(url)

if response.status_code == 200:
    api_preguntas = response.json()
    #print(api_preguntas)
else:
    print('Error:', response.status_code)

# 2. Guardamos las preguntas y respuestas en un diccionario
preguntas_dict = {}
for item in api_preguntas:
    pregunta_texto = item['question']['text']
    respuesta_correcta = item['correctAnswer']
    respuestas_incorrectas = item['incorrectAnswers']
    preguntas_dict[pregunta_texto] = {
        "Correct Answer": respuesta_correcta,
        "Incorrect Answers": respuestas_incorrectas
    }
    #print("Question:", item['question']['text'])
    #print("Correct Answer:", item['correctAnswer'])
    #print("Incorrect Answers:", item['incorrectAnswers'])
    #print()  # Adding a blank line for better readability between items

# 3. Creamos una funcion que nos devuelva el diccionario
def get_preguntas():
    return preguntas_dict

def get_pregunta_aleatoria():
    pregunta_texto = random.choice(list(preguntas_dict.keys()))
    pregunta_info = preguntas_dict[pregunta_texto]
    posibles_respuestas = [pregunta_info["Correct Answer"]] + pregunta_info["Incorrect Answers"]
    respuesta_correcta = pregunta_info["Correct Answer"]
    random.shuffle(posibles_respuestas)  # Mezclamos las respuestas para que no siempre estén en el mismo orden
    return {
        "Pregunta": pregunta_texto,
        "Posibles Respuestas": posibles_respuestas,
        "Respuesta Correcta": respuesta_correcta
    }

def check_respuesta(pregunta, respuesta):
    pregunta_info = preguntas_dict[pregunta]
    return respuesta == pregunta_info["Correct Answer"]
    