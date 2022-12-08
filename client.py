import socket
import ssl
import threading
import traceback
from cryptography.fernet import Fernet
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

# Symmetric key of the chatroom, room master is in charge of producing it
# Server has no idea of this key
key = b'gsZvk0k2izs9Mt-jOn_ddvo4gKPAZPjWJT55-nMzlss='
f = Fernet(key)


# Listening to Server and Sending Nickname
def receive():
    while True:
        try:
            # Receive Message From Server
            messageBytes = client.recv(1024)
            chatMessage = ChatMessage.from_bytes(messageBytes)
            command = chatMessage.command
            if command == 'NICK':
                response = ChatMessage('NICK', False, nickname.encode('ascii'))
                client.send(response.to_bytes())
            elif command == 'KEY':
                # Generate Asymmetric Key pair for end-to-end key exchange
                #client.send(public_key)
                #client.recv(encrypted_symmetric chatroom key)
                #store the key
                pass
            elif command == 'MASTER':
                print("I am the master..?")
                # Generate Symmetric Chatroom key
            else :
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

write_thread = threading.Thread(target=write)
write_thread.start()

