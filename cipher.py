from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from base64 import urlsafe_b64encode, urlsafe_b64decode
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, padding
import os

def encrypt(data, key):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data.encode('utf-8')) + padder.finalize()
    encryptor = cipher.encryptor()
    ct = encryptor.update(padded_data) + encryptor.finalize()
    return urlsafe_b64encode(iv + ct)

def decrypt(encrypted_data, key):
    encrypted_data = urlsafe_b64decode(encrypted_data)
    iv = encrypted_data[:16]
    ct = encrypted_data[16:]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    decryptor = cipher.decryptor()
    decrypted_bytes = decryptor.update(ct) + decryptor.finalize()
    unpadded_bytes = unpadder.update(decrypted_bytes) + unpadder.finalize()
    return unpadded_bytes.decode('utf-8')