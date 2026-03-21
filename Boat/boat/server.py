# main.py
import json
import ssl
import pika
import asyncio
import threading
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
clients = set()

# Autoriser CORS pour ton frontend (ajuste l'URL si besoin)
origins = [
    "http://localhost:8000",  # si tu testes localement
    "http://localhost:3000",
    "https://ec2-15-237-116-133.eu-west-3.compute.amazonaws.com:8443",  # URL front hébergée en HTTPS
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- WEBSOCKET --------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    print("Client connecté")
    try:
        while True:
            await websocket.receive_text()  # keep-alive (ne fait rien, juste pour garder connexion)
    except WebSocketDisconnect:
        clients.remove(websocket)
        print("Client déconnecté")

async def broadcast(message: dict):
    dead_clients = []
    for client in clients:
        try:
            # Envoyer tous les types de messages (OFFRE, ACHAT, OFFRE_SUPPRIMEE) au front
            await client.send_json(message)
        except Exception as e:
            print(f"Erreur d'envoi WS : {e}")
            dead_clients.append(client)
    for dc in dead_clients:
        clients.remove(dc)

# -------- RABBITMQ --------
USERNAME = "Devosaur"
PASSWORD = "002642c2-bbb1-497d-abe2-059e060ba711"
QUEUE_NAME = "user.002642c2-bbb1-497d-abe2-059e060ba711"
BROKER_URL = "b-a5095b9b-3c4d-4fe7-8df1-8031e8808618.mq.eu-west-3.on.aws"
BROKER_PORT = 5671

def start_rabbitmq(loop):
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    ssl_context.verify_mode = ssl.CERT_NONE  # À sécuriser en prod !

    credentials = pika.PlainCredentials(USERNAME, PASSWORD)
    parameters = pika.ConnectionParameters(
        host=BROKER_URL,
        port=BROKER_PORT,
        credentials=credentials,
        ssl_options=pika.SSLOptions(context=ssl_context)
    )

    def callback(ch, method, properties, body):
        try:
            message = json.loads(body)
        except Exception:
            message = {"raw": body.decode()}

        print("Message reçu:", message)
        asyncio.run_coroutine_threadsafe(broadcast(message), loop)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
    print("RabbitMQ connecté")
    channel.start_consuming()

@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()
    threading.Thread(target=start_rabbitmq, args=(loop,), daemon=True).start()