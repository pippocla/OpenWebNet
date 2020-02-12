TYPE_OTHER = 'OTHER'
TYPE_ACK = 'ACK'
TYPE_NACK = 'NACK'
TYPE_NORMAL = 'NORMAL'
TYPE_STATUS_REQUEST = 'STATUS_REQUEST'
TYPE_DIMENSION_REQUEST = 'DIMENSION_REQUEST'
TYPE_DIMENSION_WRITING = 'DIMENSION_WRITING'

class FixedMessage:
    def __init__(self, value, message_type):
        self.value = value
        self.type = message_type

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"{self.type} : {self}"


class NormalMessage:
    def __init__(self, who, what, where):
        self.who = who
        self.what = what
        self.where = where
        self.type = TYPE_NORMAL

    def __str__(self):
        return f"*{self.who}*{self.what}*{self.where}##"

    def __repr__(self):
        return f"{self.type} : {self}"


class StatusRequestMessage:
    def __init__(self, who, where):
        self.who = who
        self.where = where
        self.type = TYPE_STATUS_REQUEST

    def __str__(self):
        return f"*#{self.who}*{self.where}##"

    def __repr__(self):
        return f"{self.type} : {self}"


class DimensionRequestMessage:
    def __init__(self, who, where, dimension):
        self.who = who
        self.where = where
        self.dimension = dimension
        self.type = TYPE_DIMENSION_REQUEST

    def __str__(self):
        return f"*#{self.who}*{self.where}*{self.dimension}##"

    def __repr__(self):
        return f"{self.type} : {self}"


class DimensionWritingMessage:
    def __init__(self, who, where, dimension, values):
        self.who = who
        self.where = where
        self.dimension = dimension
        self.values = values
        self.type = TYPE_DIMENSION_WRITING

    def __str__(self):
        values = "*".join(self.values)
        return f"*#{self.who}*{self.where}*#{self.dimension}*{values}##"

    def __repr__(self):
        return f"{self.type} : {self}"


# OpenWeb string for opening a command session
CMD_SESSION = FixedMessage('*99*0##', TYPE_OTHER)
# OpenWeb string for opening an event session
EVENT_SESSION = FixedMessage('*99*1##', TYPE_OTHER)

ACK = FixedMessage('*#*1##', TYPE_ACK)
NACK = FixedMessage('*#*0##', TYPE_NACK)


def bad_message(data):
    raise Exception('Improperly formatted message:', data)


def parse_message(data):
    if data == str(ACK):
        return ACK
    if data == str(NACK):
        return NACK

    if not data.startswith("*"):
        raise Exception(f"data does not start with *: {data}")
    if not data.endswith("##"):
        raise Exception(f"data does not end with ##: {data}")

    parts = data[1:-2].split("*")
    if not parts[0].startswith("#"):
        if len(parts) != 3:
            bad_message(data)
        return NormalMessage(parts[0], parts[1], parts[2])

    if len(parts) < 1:
        return bad_message(data)

    if len(parts) == 1:
        return FixedMessage(data, TYPE_OTHER)

    if len(parts) == 2:
        return StatusRequestMessage(parts[0][1:], parts[1])

    if len(parts) == 3:
        return DimensionRequestMessage(parts[0][1:], parts[1], parts[2])

    if not parts[2].startswith("#"):
        bad_message(data)

    return DimensionWritingMessage(parts[0][1:], parts[1], parts[2][1:], parts[3:])


def parse_messages(data):
    if "##" not in data:
        return [], data

    parts = data.split("##")

    messages = list(map(lambda part: parse_message(part + '##'), parts[:-1]))

    if len(parts[-1]) == 0:
        return messages, None

    return messages, parts[-1]
