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
# Or
client.light_on('10')

# Prints the status of the light with id '11'
print(client.request_state('1', '11'))
# Or
print(client.light_status('11'))

# Fit the electric shutters with id '20'
client.shutter_on('20')
```

### Resume:

Command | Description
------- | ----------
normal_request(who, what, where) | Send a request
request_state(who, where) | Send a state request
light_on(where) | Turn on the light
light_off(where) | Turn off the light
light_status(where) | Get the status of the light
read_temperature(where) | Get the temperature
read_set_temperature(where) | Get the temperature set
read_valve_status(where) | Get the status of temperature valve
shutter_off(where) | Lower the electric shutters
shutter_on(where) | Fit the electric shutters
shutter_stop(where) | Stop the electric shutters

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
