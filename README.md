# ReOpenWebNet

ReOpenWebNet is a client library for communicating with an OpenWebNet gateway.

OpenWebNet is a communication protocol developed by Bticino, to enable communication between devices of its home automation product suite 'MyHome'.  For more information about OpenWebNet, see https://www.myopen-legrandgroup.com/developers/

This project started as a fork from https://github.com/pippocla/openwebnet

## Features

Asynchronous components for interacting with the gateway.

The author's OpenWebNet gateway doesn't respond well to sending commands

Low level components:
  - CommandClient: establishes command sessions and lets you send commands and read the gateway's responses.  The CommandClient does simple rate limiting because the OpenWebNet gateway seems to misbehave if you send too many commands in a short time.
  - EventClient: establishes event sessions.

Both components automatically reconnect in case of connection loss.

Higher level components:
 - ClientFactory: reads configuration from file and can create CommandClient and EventClient instances
 - GatewayProxy: Creates a CommandClient and an EventClient and keeps state in sync.

## Examples

See examples/ for examples on the various components

## Testing

To run the test suite:

    python setup.py test

## Releasing

    git tag x.y.z
    python setup.py build
    twine upload dist/reopenwebnet-x.y.z-py2.py3-none-any.whl
