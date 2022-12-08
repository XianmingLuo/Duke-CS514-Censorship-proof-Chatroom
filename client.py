import socket
import ssl
import threading
import traceback
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from ChatMessage import ChatMessage
# Choosing Nickname
nickname = input("Choose your nickname: ")

# SSL Context
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
context.load_default_certs()

# Connecting To Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client = context.wrap_socket(client)
client.connect(('127.0.0.1', 55555))
# Also acting as a key server
# meaning room masters will also serve symmetric key requests
# TODO: Not using TLS for now
keyServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Use the next port for keyServer
keyServer.bind((client.getsockname()[0], client.getsockname()[1]+1))
keyServer.listen()
# Symmetric key of the chatroom, room master is in charge of producing it
# Server has no idea of this key
key = None
f = None

# Dedicated thread and socket to distribute the key
def distribute(key):
    print("[KeyServer] Waiting for Connection...")
    keyClient, address = keyServer.accept()
    print("[KeyServer] Connected with {}".format(str(address)))
    while True:
        messageBytes = keyClient.recv(1024)
        print("[KeyServer] Recieved Message {}".format(messageBytes))
        # TODO: Encrypt the symmetric key with requester's public key
        requester_pk = serialization.load_pem_public_key(
            messageBytes,
            backend=default_backend()
        )
        encryptedKey = requester_pk.encrypt(
            key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        keyClient.send(encryptedKey)
        print("[KeyServer] Sent Key {}".format(encryptedKey))

        
        
# Listening to Server and Sending Nickname
def receive():
    global key
    global f
    isMaster = False
    while True:
        try:
            # Receive Message From Server
            messageBytes = client.recv(1024)
            chatMessage = ChatMessage.from_bytes(messageBytes)
            command = chatMessage.command
            print(command)
            print(chatMessage.payload)
            if command == 'NICK':
                response = ChatMessage('NICK',
                                       False,
                                       nickname.encode('ascii'))
                client.send(response.to_bytes())
            elif command == 'KEY':
                # TODO: Generate Asymmetric Key pair for end-to-end key exchange
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048,
                    backend=default_backend()
                )
                public_key = private_key.public_key()
                # TODO: Password for private key encryption?
                public_bytes = public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
                print("[Handshake] Public Key To Transmit {}".format(public_bytes))
                response = ChatMessage('KEY',
                                       False,
                                       public_bytes)
                client.send(response.to_bytes())
            elif command == 'MASTER':
                isMaster = True
                # Generate Symmetric Chatroom key
                # If there is already a valid symmetric key
                # Continue using it
                if not key:
                    key = Fernet.generate_key()
                    f = Fernet(key)
                    print("[Client] Generated Symmetric Key {}".format(key))
                    # We are the first one,
                    # Impossible to get the distribute command
                    write_thread = threading.Thread(target=write)
                    write_thread.start()
                    
                # TODO: Racing condition
                # What is server try to connect to keyServer before it starts accepting?
                distributeThread = threading.Thread(target=distribute, args=(key,))
                distributeThread.start()
                # Set up another socket with the server
                # For dedicated key distribution
            elif command == 'DISTRIBUTE':
                # Get the key distributed
                key = private_key.decrypt(
                    chatMessage.payload,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                f = Fernet(key)
                print("[DEBUG]: Key recieved")
                print(key.decode('ascii'))
                write_thread = threading.Thread(target=write)
                write_thread.start()

            else:
                if (chatMessage.isEncrypted):
                    print("ciphertext:", chatMessage.payload.decode('ascii'))
                    # Decrypt Chatroom Message using Symmetric Chatroom key
                    print("plaintext:", f.decrypt(chatMessage.payload).decode('ascii'))
                else:
                    print("Notification:", chatMessage.payload.decode('ascii'))
        except Exception as e:
            # Close Connection When Error
            print("An error occured!", e)
            traceback.print_exc()
            client.close()
            break

# Sending Messages To Server
def write():
    global f
    while True:
        message = '{}: {}'.format(nickname, input(''))
        messageBytes = message.encode('ascii')
        # Encrypt message using symmetric chatroom key
        encryptedMessageBytes = f.encrypt(messageBytes)
        chatMessage = ChatMessage(command = None,
                                  isEncrypted = True,
                                  payload = encryptedMessageBytes)
        try:
            client.send(chatMessage.to_bytes())
        except Exception as e:
            print("An error occured!", str(e))
            client.close()
            break
# Starting Threads For Listening And Writing
receive_thread = threading.Thread(target=receive)
receive_thread.start()


