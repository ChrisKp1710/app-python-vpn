import socket
import threading
import sqlite3
from encryption import encrypt_data, decrypt_data  # ✅ Importiamo crittografia centralizzata
from database import register_user, login_user, initialize_database  # ✅ Importiamo il database

# Configurazione database
DB_NAME = "users.db"
server_running = True  
connected_clients = {}  # Dizionario {client_socket: username}

# 🟢 Inizializza il database all'avvio
initialize_database()

def broadcast(message, sender_socket=None):
    """Invia un messaggio a tutti gli utenti connessi"""
    to_remove = []
    for client, username in connected_clients.items():
        if client != sender_socket:
            try:
                client.send(encrypt_data(message).encode("utf-8"))
            except:
                client.close()
                to_remove.append(client)

    for client in to_remove:
        del connected_clients[client]

def handle_client(client_socket, addr):
    """Gestisce un client connesso"""
    global server_running
    username = None
    print(f"✅ Connessione accettata da {addr[0]}:{addr[1]}")

    try:
        encrypted_data = client_socket.recv(4096).decode("utf-8")
        data = decrypt_data(encrypted_data)
        if not data:
            client_socket.send(encrypt_data("❌ Errore: Messaggio non valido").encode("utf-8"))
            client_socket.close()
            return

        if data.startswith("REGISTER"):
            _, username, password = data.split(" ")
            response = register_user(username, password)
            client_socket.send(response.encode("utf-8"))

        elif data.startswith("LOGIN"):
            _, username, password = data.split(" ")
            response, role = login_user(username, password)
            client_socket.send(response.encode("utf-8"))
            if decrypt_data(response) == "SUCCESS":
                connected_clients[client_socket] = username
                broadcast(f"🔵 {username} si è unito alla chat.")

        while True:
            encrypted_data = client_socket.recv(4096).decode("utf-8")
            data = decrypt_data(encrypted_data)
            if not data or data == "/exit":
                break

            print(f"📩 {username}: {data}")
            broadcast(f"📩 [{username}]: {data}", sender_socket=client_socket)

    except Exception as e:
        print(f"❌ Errore con {addr}: {e}")
    finally:
        if client_socket in connected_clients:
            del connected_clients[client_socket]
        client_socket.close()

def start_server():
    """Avvia il server"""
    initialize_database()  # Inizializza il database all'avvio del server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 8080))
    server.listen(10)  
    print("🟢 Server VPN in ascolto su 0.0.0.0:8080")

    while server_running:
        client_socket, addr = server.accept()
        threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()
