# Práctica 4-Integración
## Introducción
En esta práctica se ha hecho un programa que recoge aspectos de las tres prácticas anteriores para hacer un juego para el cual si quieres jugar tienes que hacer un inicio de sesión previo.
## Explicación del código
En este apartado sólo se comentará los cambios relevantes respecto los códigos presentados anteriormente. cabe recalcar que las partidas son de 2 jugadores y 5 preguntas.

### 1.Login para jugar
Lo que se ha hecho es que una vez un jugador realice el login de manera correcta el jugador entre a buscar partida automáticamente.
### 2. Tiempo máximo de 20 segundos para contestar y puntuación ponderada:
Para ello en la función que se encarga de recoger las respuestas de los usuarios `listen_answers(sock, num_jugadores)` se ha cambiado y ha quedado de esta manera:
```
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

```
y tambien se ha creado la función `calculate_points`

```
def calculate_points(elapsed_time):
    puntos=10*(1-(elapsed_time/20))
    return puntos```
```
Con estas dos funciones se consigue saber cuanto tarda un usuario en contestar además de premiarlo por contestar rápido. Otra cosa que se hace es no otorgar puntos a los jugadores que tarden más de 20 segundos en responder ya que se les considera como una pregunta no contestada.


## Ejecución del código 
1. Abre una terminal o línea de comandos en tu sistema.

2. Clona el repositorio con el siguiente comando:

    ```
    git clone https://github.com/202006359/Practica-4-Integracion.git
    ```

3. Inicializa el servidor Jupyter Notebook desde Anaconda.
<img width="249" alt="image" src="https://github.com/202006359/Practica-1-UDP/assets/113789409/8347b6ac-c6fb-42b4-8620-f8b7634689c4">

  
5. Esto abrirá una ventana del navegador web con el panel de control de Jupyter Notebook. Desde aquí, dirigite a la proyecto Practica-3-Multicast y picha en la carpeta "Entregable". A continuación, abre el archivo "server.ipynb", "player1.ipynb" y "player2.ipynb" (la partida a modo de tutorial será con dos jugadores).  

6. Ejecuta el código del servidor en Jupyter Notebook ejecutando todas las celdas de código en "server.ipynb". Selecciona el numero de jugadores (2 para este tutorial) y el numero de preguntas que deberan resolver los jugadores antes de que finalize la partida.

7. Ejecuta el código del cliente en Jupyter Notebook ejecutando todas las celdas de código en "Cliente1.ipynb". Registrese como usuario si no tiene cuenta. Si tiene cuenta inicie sesión para jugar.
   
9. Escriba un mensaje que diga "Ready to play" para esperar a un oponente con quien jugar o "abandono" para acabar.

10. Repita los pasos 7 y 8 pero con el código de "Cliente2.ipynb".

13. Una vez los jugadores hayan respondido todas las preguntas, recibirán el ranking final y se terminará la partida.

## Capturas de pantalla
### Player 1

![image](https://github.com/202006359/Practica-4-Integracion/assets/52907821/ed79816f-b942-408b-b79d-ab06a2619b8f)

![image](https://github.com/202006359/Practica-4-Integracion/assets/52907821/218acdff-a440-4fdc-a99c-0861b2b98408)

### Player 2

![image](https://github.com/202006359/Practica-4-Integracion/assets/52907821/b7a0e576-53ee-40d2-bad5-cfb289b6f6ee)

![image](https://github.com/202006359/Practica-4-Integracion/assets/52907821/4f348d3d-e517-4093-94f5-2000e19c5d46)


### Servidor

![image](https://github.com/202006359/Practica-4-Integracion/assets/52907821/a4d2c928-e0c0-492a-9efb-c1d0f50b8a8a)

![image](https://github.com/202006359/Practica-4-Integracion/assets/52907821/e7b26b29-606e-4ead-adb8-c5e8f9bbea1a)

