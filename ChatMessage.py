import pickle
class ChatMessage:
    def __init__(self, command, isEncrypted, payload):
        # Command e.g. NICK, MASTER, KEY
        self.command = command
        # Typically payload is encrypted by a symmetric key
        # The server doesn't know about this symmetric key
        self.isEncrypted = isEncrypted
        self.payload = payload
    # Serialize ChatMessage objects to bytes for transmitting
    def to_bytes(self):
        return pickle.dumps(self)
    @staticmethod
    # Rebuild ChatMessage object from bytes
    def from_bytes(messageBytes):
        return pickle.loads(messageBytes)
        
