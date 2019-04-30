# ReOpenWebNet

ReOpenWebNet is a client library for communicating with an OpenWebNet server over tcp.

OpenWebNet is a communication protocol developed by Bticino, to enable communication between devices of its home automation product suite 'MyHome'
For more information about OpenWebNet, see https://www.myopen-legrandgroup.com/developers/

ReOpenWebNet provides a synchronous client for so-called command sessions and an asynchronous client for event sessions.

This is a fork from https://github.com/pippocla/openwebnet

## Example usage:

### CommandClient

The CommandClient connects to the gateway and establishes a comand session.
The CommandClient works synchronously.

```
from reopenwebnet.client import CommandClient

host, port, password = 'localhost', 20000, '123456'

client = CommandClient(host, port, password)

# Turns on the light with id '10'
client.normal_request('1', '10', '1')

# Prints the status of the light with id '11'
print(client.request_state('1', '11'))
```

### EventClient

The EventClient connects to the gateway and establishes an event session.
The EventClient works asynchronously.

See `examples/eventclient.py` for an example

## Testing

To run the test suite:

    python setup.py test

## Releasing

    git tag x.y.z
    python setup.py build
    twine upload dist/reopenwebnet-x.y.z-py2.py3-none-any.whl
