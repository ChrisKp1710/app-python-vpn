import sys
import socket
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QMessageBox
)
from PyQt6.QtCore import QThread, pyqtSignal
from encryption import encrypt_data, decrypt_data  # ✅ Importiamo crittografia centralizzata

# Configurazione server
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8080

class ClientThread(QThread):
    message_received = pyqtSignal(str)

    def __init__(self, client_socket):
        super().__init__()
        self.client_socket = client_socket
        self.running = True

    def run(self):
        while self.running:
            try:
                encrypted_message = self.client_socket.recv(1024).decode("utf-8")
                message = decrypt_data(encrypted_message)
                if message:
                    self.message_received.emit(message)
            except ConnectionResetError:
                break

    def stop(self):
        self.running = False
        self.quit()

class ChatApp(QWidget):
    def __init__(self, client_socket, username):
        super().__init__()
        self.client_socket = client_socket
        self.username = username
        self.init_ui()

        self.thread = ClientThread(self.client_socket)
        self.thread.message_received.connect(self.display_message)
        self.thread.start()

    def init_ui(self):
        self.setWindowTitle("Chat Sicura - PyQt6")
        self.setGeometry(400, 200, 500, 400)

        layout = QVBoxLayout()

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        self.input_field = QLineEdit()
        layout.addWidget(self.input_field)

        self.send_button = QPushButton("Invia")
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_button)

        self.setLayout(layout)

    def display_message(self, message):
        self.chat_display.append(message)

    def send_message(self):
        message = self.input_field.text()
        if message:
            encrypted_message = encrypt_data(message)  # ✅ Crittografia messaggio
            self.client_socket.send(encrypted_message.encode("utf-8"))
            self.input_field.clear()

    def closeEvent(self, event):
        self.thread.stop()
        self.client_socket.close()
        event.accept()

class WelcomeWindow(QWidget):
    """Finestra iniziale per scegliere tra Login e Registrazione"""
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Benvenuto - Chat Sicura")
        self.setGeometry(450, 250, 350, 200)

        layout = QVBoxLayout()

        self.label = QLabel("Benvenuto! Scegli un'opzione:")
        layout.addWidget(self.label)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.open_login)
        layout.addWidget(self.login_button)

        self.register_button = QPushButton("Registrati")
        self.register_button.clicked.connect(self.open_register)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

    def open_login(self):
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

    def open_register(self):
        self.register_window = RegisterWindow()
        self.register_window.show()
        self.close()

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Login - Chat Sicura")
        self.setGeometry(450, 250, 350, 200)

        layout = QVBoxLayout()

        self.label = QLabel("Inserisci username:")
        layout.addWidget(self.label)

        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)

        self.label_password = QLabel("Inserisci password:")
        layout.addWidget(self.label_password)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Accedi")
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Errore", "Inserisci username e password validi.")
            return

        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((SERVER_HOST, SERVER_PORT))

            encrypted_data = encrypt_data(f"LOGIN {username} {password}")  # ✅ Crittografia dati login
            client_socket.send(encrypted_data.encode("utf-8"))

            response = client_socket.recv(1024).decode("utf-8")
            decrypted_response = decrypt_data(response)  # ✅ Decodifica risposta server

            if decrypted_response == "SUCCESS":
                self.chat_window = ChatApp(client_socket, username)
                self.chat_window.show()
                self.close()
            else:
                QMessageBox.warning(self, "Errore", decrypted_response)

        except ConnectionRefusedError:
            QMessageBox.critical(self, "Errore", "Impossibile connettersi al server.")

class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Registrazione - Chat Sicura")
        self.setGeometry(450, 250, 350, 200)

        layout = QVBoxLayout()

        self.label = QLabel("Scegli un username:")
        layout.addWidget(self.label)

        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)

        self.label_password = QLabel("Scegli una password:")
        layout.addWidget(self.label_password)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        self.register_button = QPushButton("Registrati")
        self.register_button.clicked.connect(self.handle_register)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

    def handle_register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Errore", "Inserisci username e password validi.")
            return

        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((SERVER_HOST, SERVER_PORT))

            encrypted_data = encrypt_data(f"REGISTER {username} {password}")  # ✅ Crittografia registrazione
            client_socket.send(encrypted_data.encode("utf-8"))

            response = client_socket.recv(1024).decode("utf-8")
            decrypted_response = decrypt_data(response)  # ✅ Decodifica risposta server

            if decrypted_response == "REGISTERED":
                QMessageBox.information(self, "Successo", "Registrazione completata! Ora puoi accedere.")
                self.login_window = LoginWindow()
                self.login_window.show()
                self.close()
            else:
                QMessageBox.warning(self, "Errore", decrypted_response)

            client_socket.close()

        except ConnectionRefusedError:
            QMessageBox.critical(self, "Errore", "Impossibile connettersi al server.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    welcome_window = WelcomeWindow()  # ✅ Mostra la schermata iniziale con le scelte Login/Registrazione
    welcome_window.show()
    sys.exit(app.exec())
