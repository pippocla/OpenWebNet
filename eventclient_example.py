from openwebnet import EventClient


def handle_connect():
    print("Connected")

def handle_event(event):
    print("I got an event", event)


client = EventClient('192.168.1.10', 20000, '951753', handle_connect, handle_event)
client.start()
