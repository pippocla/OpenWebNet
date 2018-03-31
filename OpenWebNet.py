#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket

"""
Read Write class for OpenWebNet bus
"""

class OpenWebNet(object):

    #OK message from bus
    ACK = '*#*1##'
    #Non OK message from bus
    NACK = '*#*0##'
    #OpenWeb string for open a command session
    CMD_SESSION = '*99*0##'
    #OpenWeb string for open an event session
    EVENT_SESSION = '*99*1##'

    #Init metod
    def __init__(self,host,port,password):
        self._host = host
        self._port = int(port)
        self._psw = password
        self._session = False
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    #Connection with host
    def connection(self):
        self._socket.connect((self._host,self._port))
        print('connection')

    #Send data to host
    def send_data(self,data):
        self._socket.send(data.encode())

    #Read data from host
    def read_data(self):
        return str(self._socket.recv(1024).decode())

#Calculate the password to start operation
    def calculated_psw (self, nonce):
        m_1 = 0xFFFFFFFF
        m_8 = 0xFFFFFFF8
        m_16 = 0xFFFFFFF0
        m_128 = 0xFFFFFF80
        m_16777216 = 0XFF000000
        flag = True
        num1 = 0
        num2 = 0
        self._psw = int(self._psw)

        for c in nonce:
            num1 = num1 & m_1
            num2 = num2 & m_1
            if c == '1':
                length = not flag
                if not length:
                    num2 = self._psw
                num1 = num2 & m_128
                num1 = num1 >> 7
                num2 = num2 << 25
                num1 = num1 + num2
                flag = False
            elif c == '2':
                length = not flag
                if not length:
                    num2 = self._psw
                num1 = num2 & m_16
                num1 = num1 >> 4
                num2 = num2 << 28
                num1 = num1 + num2
                flag = False
            elif c == '3':
                length = not flag
                if not length:
                    num2 = self._psw
                num1 = num2 & m_8
                num1 = num1 >> 3
                num2 = num2 << 29
                num1 = num1 + num2
                flag = False
            elif c == '4':
                length = not flag

                if not length:
                    num2 = self._psw
                num1 = num2 << 1
                num2 = num2 >> 31
                num1 = num1 + num2
                flag = False
            elif c == '5':
                length = not flag
                if not length:
                    num2 = self._psw
                num1 = num2 << 5
                num2 = num2 >> 27
                num1 = num1 + num2
                flag = False
            elif c == '6':
                length = not flag
                if not length:
                    num2 = self._psw
                num1 = num2 << 12
                num2 = num2 >> 20
                num1 = num1 + num2
                flag = False
            elif c == '7':
                length = not flag
                if not length:
                    num2 = self._psw
                num1 = num2 & 0xFF00
                num1 = num1 + (( num2 & 0xFF ) << 24 )
                num1 = num1 + (( num2 & 0xFF0000 ) >> 16 )
                num2 = ( num2 & m_16777216 ) >> 8
                num1 = num1 + num2
                flag = False
            elif c == '8':
                length = not flag
                if not length:
                    num2 = self._psw
                num1 = num2 & 0xFFFF
                num1 = num1 << 16
                num1 = num1 + ( num2 >> 24 )
                num2 = num2 & 0xFF0000
                num2 = num2 >> 8
                num1 = num1 + num2
                flag = False
            elif c == '9':
                length = not flag
                if not length:
                    num2 = self._psw
                num1 = ~num2
                flag = False
            else:
                num1 = num2
            num2 = num1
        return num1 & m_1

    #Open command session
    def cmd_session(self):
        #create the connection
        self.connection()

        #if the bus answer with a NACK report the error
        if self.read_data() == OpenWebNet.NACK :
            _LOGGER.exception("Non posso inizializzare la comunicazione con il gateway")

        #open commanc session
        self.send_data(OpenWebNet.CMD_SESSION)

        answer = self.read_data()
        #if the bus answer with a NACK report the error
        if answer == OpenWebNet.NACK:
            _LOGGER.exception("Il gateway rifiuta la sessione comandi")
            return False

        #calculate the psw
        psw_open = '*#' + str(self.calculated_psw(answer)) + '##'

        #send the password
        self.send_data(psw_open)

        #if the bus answer with a NACK report the error
        if self.read_data() == OpenWebNet.NACK:
             _LOGGER.exception("Password errata")

        #othefwise set the variable to True
        else:
            self._session = True
            print('cmd_session')


    #Extractor for the answer from the bus
    def extractor(self,answer):
        value_list = []
        print('estrattore riceve',answer)
        #scan on all the caracters on the answer
        index = 0
        while index <= len(answer) - 1:
            print('index',index)
            if answer[index] != '*' and answer[index] != '#':
                lenght = 0
                val = ''
                while lenght <= len(answer) - 1 - index:
                    if answer[index + lenght] != '*' and answer[index + lenght] != '#':
                        lenght = lenght +1
                        print('lenght',lenght)
                    else:
                        break
                print('aggiungo a val',answer[index:index + lenght])
                val = val + answer[index:index + lenght]
                print('val',val)
                value_list.append(val)
                print('value_list',value_list)
                index = index + lenght
                lenght = 0
            index = index + 1
        print(value_list)
        return value_list


    #Check that bus send al the data
    def check_answer (self,message):
        #if final part of the message is not and ACK or NACK
        end_message = ''
        print('message ricevuto da check answer', message)
        print('OpenWebNet.ACK',OpenWebNet.ACK)
        if message[len(message)- 6:] != OpenWebNet.ACK and message[len(message)- 6:] != OpenWebNet.NACK:
            #the answer is not completed, read again from bus
            print('message -len',message[len(message)-6:])
            end_message = self.read_data()
            #add it

            print('message +end message',message + end_message)
            return message + end_message

        #check if I get a NACK
        if message[len(message)- 6:] == OpenWebNet.NACK:
            _LOGGER.exception("Errore Comando non effettuato")


        return message


    #Normal request to BUS
    def normal_request(self,who,where,what):

        #if the command session is not active
        if not self._session:
            self.cmd_session()

        #prepare the request
        normal_request = '*' + who + '*' + what + '*' + where + '##'

        #and send
        self.send_data(normal_request)

        #read the answer
        message = self.read_data()

        #check if I get a NACK
        if message == OpenWebNet.NACK:
            _LOGGER.exception("Errore Comando non effettuato")


    #Request of state of a components on the bus
    def stato_request(self,who,where):
        print('stato request)')
        #if the command session is not active
        if not self._session:
            self.cmd_session()

        #preparo la richiesta
        stato_request = '*#' + who + '*' + where + '##'
        print('richiesta',stato_request)
        #e la Invio
        self.send_data(stato_request)

        #e leggo la risposta
        message = self.read_data()
        print('messagge',message)
        #verifico se il bus ha trasmesso tutti i dati
        check_message = self.check_answer(message)

        #verifico se ho ricevuto un NACK
        if message[len(message)- 6:] == OpenWebNet.NACK:
            _LOGGER.exception("Errore Comando non effettuato")
        #o un ACK
        else:
            #nel qual caso estraggo i dati della risposta e li restituisco sotto forma di lista
            return self.extractor(check_message[:len(check_message) - 6])

    #Richiesta grandezza
    def grandezza_request(self,who,where, grandezza):
        #Se non è attiva apro sessione comandi
        if not self._session:
            self.cmd_session()

        #preparo la richiesta
        grandezza_request = '*#' + who + '*' + where + '*' + grandezza + '##'

        #e la Invio
        self.send_data(grandezza_request)

        #e leggo la risposta
        message = self.read_data()

        #verifico se il bus ha trasmesso tutti i dati
        check_message = self.check_answer(message)

        #verifico se ho ricevuto un NACK
        if message[len(message)- 6:] == OpenWebNet.NACK:
            _LOGGER.exception("Errore Comando non effettuato")
        #o un ACK
        else:
            #nel qual caso estraggo i dati della risposta e li restituisco sotto forma di lista
            return self.extractor(check_message[:len(check_message) - 6])

    #Scrittura di una grandezza
    def grandezza_write(self,who,where,grandezza,valori):
        #Se non è attiva apro sessione comandi
        if not self._session:
            self.cmd_session()

        #preparo la richiesta
        val =''
        for item in valori:
            val = '*' + val[item]

        grandezza_write = '*#' + who + '*' + where + '*#' + grandezza + val + '##'

        #e la Invio
        self.send_data(stato_request)

        #e leggo la risposta
        return self.read_data()

    #metodo che invia il comando di accensione della luce where sul bus
    def luce_on (self,where):
        self.normal_request('1',where,'1')

    #metodo che invia il comandi di spegnimento della luce where sul bus
    def luce_off(self,where):
        self.normal_request('1',where,'0')

    #metodo per la richiesta dello stato della luce where sul bus
    def stato_luce(self,where):
        print('stato_luce')
        stato = self.stato_request('1',where)

        if stato[1] == '1':
            return True
        else:
            return False

    #Metodo per la lettura della temperatura
    def read_temperature(self,where):
        print('lettura temperatura')
        temperatura = self.grandezza_request('4',where,'0')
        return float(temperatura[3])/10.0

    #Metodo per la lettura della temperatura settata  nella sonda
    def read_setTemperature(self,where):
        print('lettura set temperature')
        setTemperatura = self.grandezza_request('4',where,'14')
        return float(setTemperatura[3])/10.0

    #Metodo per la lettura dello stato della elettrovalvola
    def read_sondaStatus(self,where):
        print('lettura stato sonda temperature')
        stato_sonda = self.grandezza_request('4',where,'19')
        print('stato sonda',stato_sonda[4])
        if stato_sonda[4] == '0':
            return 'OFF'
        else:
            return 'ON'
