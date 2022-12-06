import socket
import ssl
import threading

from cryptography.fernet import Fernet

# Choosing Nickname
nickname = input("Choose your nickname: ")

# SSL Context
context = ssl.create_default_context(purpose = ssl.Purpose.SERVER_AUTH)
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
#print(context.protocol)
#print(context.get_ciphers())

# Connecting To Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#client = context.wrap_socket(client)
client.connect(('127.0.0.1', 55555))

#print(client.version())
#print(client.cipher())

# Listening to Server and Sending Nickname
def receive():
    while True:
        try:
            # Receive Message From Server
            # If 'NICK' Send Nickname
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
            else:
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
        client.send(message.encode('ascii'))


# Starting Threads For Listening And Writing
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()

