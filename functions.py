import socket
import struct
import time
import API as api
import pickle

MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007
fin_juego = False

def join_multicast_group():
    # Crear un socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Enlazar el socket al grupo de multidifusión
    sock.bind(('', MCAST_PORT))

    # Unirse al grupo de multidifusión
    mreq = struct.pack('4sl', socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    return sock

def send_multicast_message(sock, message):
    # Enviar un mensaje de saludo al grupo
    sock.sendto(pickle.dumps(message), (MCAST_GRP, MCAST_PORT))

def receive_multicast_messages(sock, stop_event):
    while not stop_event.is_set():
        # Recibir mensajes del grupo de multidifusión
        data, addr = sock.recvfrom(1024)
        message = pickle.loads(data)
        if message:  # Check if the message is not empty 
            print(message)
            if fin_juego:
                stop_event.set()
                break
            
def is_partida_terminada():
    return fin_juego
def calculate_points(elapsed_time):
    puntos=10*(1-(elapsed_time/20))
    return puntos
#Esperar a que se conecten los jugadores  
def wait_for_players(sock, num_jugadores):
    jugadores=[]
    print("Esperando a que se conecten los jugadores...")
    while len(jugadores) < num_jugadores:
        data, addr = sock.recvfrom(4096)
        message = pickle.loads(data)
        print(message)
        try:
            jugador = message.split(":")[0]
            if jugador not in jugadores:
                if message.split(":")[1].strip() == "Ready to play":
                    jugadores.append(jugador)
                    send_multicast_message(sock, f"Server: ¡Bienvenido a la partida {jugador}!")
                    print("Actualmente hay "+len(jugadores)+ "en espera.")
        except:
            continue
    send_multicast_message(sock, "\n¡Todos los jugadores están listos para jugar!\n")
    
def clear_current_connections():
    with open("current_connections.txt", 'w'):
        pass  # No es necesario escribir nada, el contenido se borra automáticamente
    return True

def init_game(sock, num_jugadores, num_preguntas):
    global puntuaciones
    puntuaciones = {}
    fin_juego = False
    send_multicast_message(sock, "Server: ¡El juego va a comenzar!\n")
    time.sleep(1)
    for i in range(num_preguntas):
        send_multicast_message(sock, f"\nRonda {i+1}/{num_preguntas}\n")
        time.sleep(1)
        #Enviar pregunta
        question, respuesta_correcta = send_question(sock)
        #Esperar respuestas
        respuestas = listen_answers(sock, num_jugadores)
        #Actualizar puntuaciones
        for jugador in respuestas.keys():
            respuesta = respuestas[jugador][0]
            elapsed_time=respuestas[jugador][1]
            if respuesta == respuesta_correcta:
                puntos=calculate_points(elapsed_time)
                if jugador in puntuaciones:
                    puntuaciones[jugador] += puntos
                else:
                    puntuaciones[jugador] = puntos
            else:
                if jugador in puntuaciones:
                    puntuaciones[jugador] += 0
                else:
                    puntuaciones[jugador] = 0
        send_multicast_message(sock, "Respuesta correcta: " + respuesta_correcta)
        #Enviar ranking
        send_ranking(sock, puntuaciones)
        time.sleep(1)
    ganador = get_ganador(puntuaciones)
    send_multicast_message(sock, "¡El juego ha terminado! El ganador es " + ganador)
    time.sleep(1)
    fin_juego = True

def send_question(sock):
    question_info = api.get_pregunta_aleatoria()
    question_text = question_info["Pregunta"]
    possible_answers = question_info["Posibles Respuestas"]
    correct_answer = question_info["Respuesta Correcta"]
    send_multicast_message(sock, question_text)
    send_multicast_message(sock, possible_answers)
    return question_text, correct_answer

def read_active_players():
    with open("current_connections.txt", 'r') as file:
        # Leer cada línea del archivo, eliminar espacios en blanco y saltos de línea
         return [line.strip().split(":")[0] for line in file if line.strip()]
    
def listen_answers(sock, num_jugadores):
    respuestas = {}
    print("Esperando a que los jugadores respondan...")
    sock.settimeout(20)  # Establece un tiempo de espera de 20 segundos para el socket
    jugadores_respondieron = set()
    lista_jugadores = read_active_players()

    start_time = time.time()  # Registrar el tiempo de inicio

    try:
        while len(respuestas) < len(lista_jugadores):
            data, addr = sock.recvfrom(1024)
            if data.strip():
                elapsed_time = time.time() - start_time  # Calcular el tiempo transcurrido
                message = pickle.loads(data)
                try:
                    jugador, respuesta = message.split(":")
                    jugador = jugador.split(":")[0].strip()
                    respuesta = respuesta.strip()
                    if jugador in lista_jugadores and respuesta:
                        respuestas[jugador] = [respuesta,elapsed_time]
                        jugadores_respondieron.add(jugador)
                        print(f"{jugador} respondió: {respuesta} en {elapsed_time:.2f} segundos")
                except:
                    continue
    except socket.timeout:
        print("Tiempo de espera alcanzado. Continuando con las respuestas recopiladas...")
        # Para cada jugador que no respondió, imprimir un mensaje
        for jugador in lista_jugadores:
            if jugador not in jugadores_respondieron:
                print(f"{jugador} se quedó sin tiempo para responder.")

    return respuestas

# def listen_answers(sock, num_jugadores):
#     respuestas = {}
#     print("Esperando a que los jugadores respondan...")

#     sock.settimeout(20)  # Establece un tiempo de espera de 20 segundos para el socket
#     jugadores_respondieron = set()
#     lista_jugadores=read_active_players()

#     try:
#         while len(respuestas) < len(lista_jugadores):
#             data, addr = sock.recvfrom(1024)
#             if data.strip():
#                 message = pickle.loads(data)
#                 try:
#                     jugador, respuesta = message.split(":")
#                     jugador = jugador.strip()
#                     respuesta = respuesta.strip()
#                     if jugador in lista_jugadores and respuesta:
#                         respuestas[jugador] = respuesta
#                         jugadores_respondieron.add(jugador)
#                         print(f"{jugador} respondió: {respuesta}")
#                 except:
#                     continue
#     except socket.timeout:
#         print("Tiempo de espera alcanzado. Continuando con las respuestas recopiladas...")
#         # Para cada jugador que no respondió, imprimir un mensaje
#         for jugador in lista_jugadores:
#             if jugador not in jugadores_respondieron:
#                 print(f"{jugador} se quedó sin tiempo para responder.")

#     return respuestas

    
# def listen_answers(sock, num_jugadores):
#     respuestas = {}
#     print("Esperando a que los jugadores respondan...")
#     while len(respuestas) < num_jugadores:
#         data, addr = sock.recvfrom(1024)
#         if data.strip():
#             message = pickle.loads(data)
#             if isinstance(message, str) and ":" in message:
#                 try:
#                     jugador, respuesta = message.split(":", 1)
#                     jugador = jugador.strip()
#                     respuesta = respuesta.strip()
#                     if jugador.startswith("user") and respuesta:
#                         respuestas[jugador] = respuesta
#                         print(f"{jugador} respondió: {respuesta}")
#                 except Exception as e:
#                     print(f"Error al procesar la respuesta: {e}")
#     return respuestas

def send_ranking(sock, puntuaciones):
    ranking = sorted(puntuaciones.items(), key=lambda x: x[1], reverse=True)
    message = "Ranking:\n"
    for i, (player, score) in enumerate(ranking):
        message += f"{i+1}. {player}: {score:.2f}\n"
    send_multicast_message(sock, message)

def get_ganador(puntuaciones):
    ganador = max(puntuaciones, key=puntuaciones.get)
    return ganador
#________________________________________________________________________________________________________________________________________
users_file = "application_users.txt"
connections_file="current_connections.txt"
#DEFINICIONES DE LAS FUNCIONES
# Función para comprobar si un usuario ya existe
def user_exists(username): #Función que busca si un usuario ya está guardado.
    with open(users_file, 'r') as file:
        for line in file:
            if username == line.strip().split(':')[0]: #Se busca linea por linea si ecxiste alguna coincidencia
                return True # Si se encuentra una coincidencia se sale del bucle y se devuelve True
    return False #Si no se encuentra ninguna coincidencia se sale con un False

# Función para registrar un nuevo usuario
def register_user(username, password):
    if user_exists(username):#Se checkea paar que no haya nombres duplicados
        return False
    else:
        with open(users_file, 'a') as file:
            file.write(f'{username}:{password}\n') # Si no hay un duplicado se añade una nueva linea con username:password
        return True

# Función para validar el login de un usuario
def login_user(username, password):
    with open(users_file, 'r') as file:
        for line in file: 
            user, passw = line.strip().split(':')
            if username == user and password == passw:  # Para cada linea se compara si la combinacion de usuario 
                                                        # mas contraseña existe en alguna línea
                return True                             # si existe alguna coincidencia se hace login.
    return False                                        # si no existe alguna coincidencia no se hace login.

def add_connection(username, client_address):
    with open(connections_file, 'a') as file:
        file.write(f'{username}:{client_address}\n') # Si no hay un duplicado se añade una nueva linea con username:password
    return True
def remove_connection(username, client_address):
    with open(connections_file, 'r') as file:
        lines = file.readlines()  # Leer todas las líneas del archivo
    
    # Filtrar las líneas para eliminar la correspondiente a la conexión que queremos borrar
    with open(connections_file, 'w') as file:
        for line in lines:
            if line.strip() != f'{username}:{client_address}':
                file.write(line)
    return True
