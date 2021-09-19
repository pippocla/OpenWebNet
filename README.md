# ReOpenWebNet

ReOpenWebNet is a library communicating with an OpenWebNet gateway. It supports event sessions and command sessions.
OpenWebNet is a communication protocol developed by Bticino, to enable communication between devices of its home automation product suite 'MyHome'.  For more information about OpenWebNet, see https://www.myopen-legrandgroup.com/developers/

This project started as a fork from https://github.com/pippocla/openwebnet

## Features

- Asynchronous components for interacting with the gateway.
- A bridge between openwebnet and mqtt; At the moment only light switches/actuators ('who=1') are supported. If you want to see support for other things, please reach out via GitHub. 

## Example scripts

Note: before running these examples, change the constants declared at the top of these script.

- `examples/event_session.py`: When running this script you should see openwebnet events being logged to the command line as they happen.
- `examples/command_session.py`: Running the script should toggle a light on and off 5 times with 1 second intervals. 

## MQTT Bridge

See `bin/openwebnet-mqtt-bridge`.

This bridge communicates with an openwebnet service over http and and mqtt service.
This should make it easier to interact with openwebnet in various tools (OpenHAB, Homeassistant, Node-Red)

### Configuration

The MQTT bridge is configured via $HOME/.reopenwebnet/config.yaml
See reopenwebnet_config.yml.sample for an example

## Releasing

    git tag x.y.z
    python setup.py build
    twine upload dist/reopenwebnet-x.y.z-py2.py3-none-any.whl
