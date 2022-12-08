import socket
import ssl
import threading

from cryptography.fernet import Fernet

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


# Listening to Server and Sending Nickname
def receive():
    while True:
        try:
            # Receive Message From Server
            # If 'NICK' Send Nickname
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
            elif message == 'KEY':
                # Generate Asymmetric Key pair for end-to-end key exchange
                #client.send(public_key)
                #client.recv(encrypted_symmetric chatroom key)
                #store the key
                pass
            elif message == 'MASTER':
                print("I am the master..?")
                # Generate Symmetric Chatroom key
            else:
                # Decrypt Chatroom Message using Symmetric Chatroom key
                print(message)
        except:
            # Close Connection When Error
            print("An error occured!")
            client.close()
            break

# Sending Messages To Server
def write():
    while True:
        message = '{}: {}'.format(nickname, input(''))
        # Encrypt message using symmetric chatroom key
        try:
            client.send(message.encode('ascii'))
        except Exception as e:
            print("An error occured!")
            client.close()
            break
# Starting Threads For Listening And Writing
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()

