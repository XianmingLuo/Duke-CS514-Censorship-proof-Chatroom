from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization

from cryptography.hazmat.primitives.asymmetric.x448 import X448PrivateKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
#X448 Key exchange
private_key = X448PrivateKey.generate()
print(type(private_key), private_key.private_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PrivateFormat.Raw,
    encryption_algorithm=serialization.NoEncryption()
))
peer_public_key = X448PrivateKey.generate().public_key()
print(type(peer_public_key), peer_public_key)
shared_key = private_key.exchange(peer_public_key)
print(type(shared_key), shared_key)


print(type(private_key))
# Can also load the key from file

key = Fernet.generate_key()
print("key", key)
f = Fernet(key)
plaintext = b"A really secret message. Not for prying eyes."
print("plaintext", plaintext)
ciphertext = f.encrypt(plaintext)
print("ciphertext", ciphertext)

decrypted_plaintext = f.decrypt(ciphertext)
print("decrypted plaintext", decrypted_plaintext)

