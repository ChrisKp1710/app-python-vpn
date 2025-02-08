from Crypto.Cipher import AES
import base64

SECRET_KEY = b"0123456789abcdef"  # Deve essere lungo 16, 24 o 32 bytes

def encrypt_data(data):
    """Cripta i dati con AES"""
    cipher = AES.new(SECRET_KEY, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data.encode("utf-8"))
    return base64.b64encode(cipher.nonce + ciphertext).decode("utf-8")

def decrypt_data(data):
    """Decripta i dati con AES"""
    try:
        data = base64.b64decode(data.encode("utf-8"))
        nonce, ciphertext = data[:16], data[16:]
        cipher = AES.new(SECRET_KEY, AES.MODE_EAX, nonce=nonce)
        return cipher.decrypt(ciphertext).decode("utf-8")
    except Exception:
        return None  # Se fallisce la decodifica, ritorna None
