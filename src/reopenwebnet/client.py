# -*- coding: utf-8 -*-
import socket
from logging import getLogger
import threading

from reopenwebnet import messages
from reopenwebnet.password import calculate_password

_LOGGER = getLogger(__name__)

""" Terminology:
   request = string sent to gateway
   response = string sent from gateway
   frame = a string representing a single frame as defined in the openwebnet documentation
   decoded frame = all the values in a frame converted to tuple. e.g. *#4*#0*#0*0250*1## becomes ('#4', '#0', '#0', '0250', '1')
"""

class CommandClient:
    def __init__(self, host, port, password, timeout=3.0):
        self._host = host
        self._port = int(port)
        self._password = password
        self._session = False
        self._timeout = timeout
        self._lock = threading.Lock()

    def normal_request(self, who, where, what):
        """ Handles a normal request.  Throws an exception when response does ends with NACK """
        who,where,what = str(who),str(where),str(what)
        request = '*' + who + '*' + what + '*' + where + '##'
        frames = self._execute_request(request)

        if frames is None:
            return None

        if frames[-1] == messages.NACK:
            _LOGGER.exception("Error: command execution failed")
            return False
        return True

    def request_state(self, who, where):
        who,where = str(who),str(where)
        frames = self.request_state_multi(who, where)

        if frames is None:
            return None

        if len(frames) != 1:
            _LOGGER.error('single state request yielded multiple messages')
            return None

        frame = frames[0]

        if (frame[0] != who or frame[2] != where):
            _LOGGER.error("requested status for %s/%s but got response for %s/%s"%(who, where, frame[0], frame[2]))
            return None

        return frame[1]
            
    def request_state_multi(self, who, where):
        who,where=str(who),str(where)
        request = '*#' + who + '*' + where + '##'
        frames = self._execute_request(request)

        if frames is None:
            return None

        if frames[-1] != messages.ACK:
            _LOGGER.error('response does not end with ACK')
            return None

        return self.convert_frames_to_tuples(frames[:-1])

    def _execute_request(self, request):
        """ sends a request and returns a list of frames sent back by the gateway"""
        response = None

        with self._lock:
            try:
                if not self._session:
                    self.cmd_session() 

                if not self._session:
                    return None
                _LOGGER.debug('about to send request')
                self.send_data(request)
                response = self._read_complete_response() 
            except (IOError, OSError, socket.timeout) as e:
                self._session = False 
                self._socket.close()

        if response is None:
            return response

        frames =  [ x + "##" for x in response.split("##")[:-1]]
        if frames[-1] != messages.ACK:
            _LOGGER.error("response did not end with ACK frame: " + frames)

        return frames

    def cmd_session(self):
        connected = self.connect()
        if not connected:
            _LOGGER.info("socket connection failed")
            return

        _LOGGER.debug("reading for cmd session setup")
        if self.read_data() == messages.NACK:
            _LOGGER.exception("Could not initialize connection with the gateway")

        self.send_data(messages.CMD_SESSION)

        answer = self.read_data()
        if answer == messages.NACK:
            _LOGGER.exception("The gateway refused the session command")
            return

        self.send_password(answer)

        if self.read_data() == messages.NACK:
            _LOGGER.exception("Password refused")
        else:
            self._session = True

    def connect(self):
        _LOGGER.debug("connecting with %s:%s",self._host, self._port)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(self._timeout)
        try:
            self._socket.connect((self._host, self._port))
            return True
        except IOError as e:
            _LOGGER.exception("Could not connect")
            self._socket.close()
        return False

    def send_password(self, nonce):
        psw_open = '*#' + str(calculate_password(self._password, nonce)) + '##'
        self.send_data(psw_open)

    def send_data(self, data):
        _LOGGER.debug("---> %s", data)
        self._socket.send(data.encode())

    def read_data(self):
        data = str(self._socket.recv(1024).decode())
        _LOGGER.debug("<--- %s", data)
        return data

    def extract_values(self, answer):
        value_list = []
        index = 0
        while index <= len(answer) - 1:
            if answer[index] != '*' and answer[index] != '#':
                length = 0
                val = ''
                while length <= len(answer) - 1 - index:
                    if answer[index + length] != '*' and answer[index + length] != '#':
                        length = length + 1
                    else:
                        break
                val = val + answer[index:index + length]
                value_list.append(val)
                index = index + length
            index = index + 1
        return value_list

    def _read_complete_response(self):
        response = self.read_data()
        while response[-6:] != messages.ACK and response[-6:] != messages.NACK:
            response += self.read_data()

        return response

    def dimension_read_request(self, who, where, dimension):
        if not self._session:
            self.cmd_session()

        dimension_request = '*#' + who + '*' + where + '*' + dimension + '##'
        frames = self._execute_request(dimension_request)

        return frames

    def dimension_write_request(self, who, where, dimension, values):
        if not self._session:
            self.cmd_session()

        write_values = ''.join(['*%s'%item for item in values])
        write_request = '*#' + who + '*' + where + '*#' + dimension + write_values + '##'
        frames = self._execute_request(write_request)

        # TODO: check / parse frames
        return frames

    def convert_frames_to_tuples(self, frames):
        return [self.convert_frame_to_tuple(frame) for frame in frames]

    def convert_frame_to_tuple(self, frame):
        return frame[:-2].split("*")[1:]

    def light_command(self, where, what):
        self.normal_request('1', str(where), str(what))

    def light_on(self, where):
        self.light_command(where, 1)

    def light_off(self, where):
        self.light_command(where, 0)

    def light_status(self, where):
        return self.request_state('1', where)

    def read_temperature(self, where):
        temperature = self.dimension_read_request('4', where, '0')
        return float(temperature[3]) / 10.0

    def read_set_temperature(self, where):
        temperature = self.dimension_read_request('4', where, '14')
        return float(temperature[3]) / 10.0

    def read_valve_status(self, where):
        valve_status = self.dimension_read_request('4', where, '19')
        if valve_status[4] == '0':
            return 'OFF'
        else:
            return 'ON'

