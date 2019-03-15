# OK message from bus
ACK = '*#*1##'
# Non OK message from bus
NACK = '*#*0##'
# OpenWeb string for open a command session
CMD_SESSION = '*99*0##'
# OpenWeb string for open an event session
EVENT_SESSION = '*99*1##'


def extract_messages(data):
    if not data.startswith("*"):
        raise Exception("data does not start with *")
    if not data.endswith("##"):
        raise Exception('data does not end with ##')
    parts = [part + "##" for part in data.split("##")[:-1]]
    return parts


def extract_single(message):
    return message[2:-2]


def generate_single(message):
    return "*#%s##" % message
