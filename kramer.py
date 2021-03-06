# Copyright (c) 2014
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS
# ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE FOUNDATION OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
#              * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
#              * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
import socket

import struct
from enum import Enum
import logging


class Device(object):
    """This class describe a tcp kramer matrix connection.
    """

    def __init__(self, ip="192.168.1.30", port="acc", machine_number=1, buffer_size=1024):
        """Initiate a link to a kramer matrix. This won't actually open the connection.
        @param ip : the matrix ip
        @param port : the matrix port
        @param machine_numer : the machine index in a aggregate of machines.
        @param buffer_size : the buffer size used when reading the response from the matrix
        """
        self.ip = ip
        self.port = port
        self.machine_number = machine_number
        self.buffer_size = buffer_size

    def __str__(self):
        return "<kramer.Device on tcp://{!s}:{!s}>".format(self.ip, self.port)

    def switch_audio(self, input, output):
        """Create a link between input <input> and output <output>
        """
        self.__send_instruction(Instructions.switch_audio, input, output)

    def store_audio_status(self, preset_index):
        self.__send_instruction(Instructions.store_audio_status, preset_index, 0)

    def delete_audio_status(self, preset_index):
        self.__send_instruction(Instructions.store_audio_status, preset_index, 1)

    def reset_audio(self):
        self.__send_instruction(Instructions.reset_audio, 0, 0)

    def __send_instruction(self, instruction, input, output):
        # set the two first bit to 0
        # first one is fixed
        # second one is a bit set if we talk to the matrice as oposition to
        # from the matrix.
        instruction_byte = 0b00111111 & instruction.value
        # set the first bit to one
        input_byte = 0b10000000 | input
        # set the first bit to one
        output_byte = 0b10000000 | output
        # set the first bit to one
        machine_number_byte = 0b10000000 | self.machine_number

        logging.debug("instruction byte {:0=2x}".format(instruction_byte))
        logging.debug("input byte {:0=2x}".format(input_byte))
        logging.debug("output byte {:0=2x}".format(output_byte))
        logging.debug("machine number byte {:0=2x}".format(machine_number_byte))

        payload = struct.pack('!BBBB', instruction_byte, input_byte, output_byte, machine_number_byte)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.ip, self.port,))
        sock.send(payload)

        response = sock.recv(self.buffer_size)
        response_instruction_byte, response_input_byte, response_output_byte, response_machine_number_byte = struct.unpack('!BBBB')

        sock.close()
        logging.debug("received from the Device :{!s}".format(response))

        # We mask the bit we don't need.
        instruction_return = response_instruction_byte & 0b00111111
        input_return = response_input_byte & 0b011111111
        output_return = response_output_byte & 0b01111111
        machine_return = response_machine_number_byte & 0b01111111

        if instruction_return != instruction:
            raise Exception("returned instruction doesn't match the sent one")

        return (instruction_return, output_return, input_return, machine_return,)


class Instructions(Enum):
    switch_audio = 2
    request_size = 14
    reset_audio = 18
    store_audio_status = 19
    recall_audio_status = 20

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    Device(ip="127.0.0.1", port=8080).switch_audio(1,2)
