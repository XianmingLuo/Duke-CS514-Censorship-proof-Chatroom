FreeChat: A Censorship-Proof TLS Chat Room
==========================================

About
-----

This is a chat server that uses end-to-end encryption for communication. The server can not see the message in plaintext, which prevent authority from performing censorship.

Installation:
-------------
    git clone https://github.com/szt1112/CS514-Final-Project.git

For server:
-----------
    python3 server.py

For clients:
-----------
    python3 client.py
    
Note:
-----
Currently we are using loopback ip address, meaning the server's address is 127.0.0.1:55555 and the client's address is 127.0.0.1:random_port. Because of that, client and server have to be on the same machine for now. However, it is quite easy to use public ip addresses.
