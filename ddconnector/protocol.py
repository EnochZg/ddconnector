import asyncio
import json
import logging

from ddconnector.decoder import decode
from ddconnector.exceptions import (DecodeException, 
                                    UnkownCommandException,
                                    FormatException)
from ddconnector.processors import processors

DELIMITER = b'*'

class Protocol(asyncio.Protocol):
    def __init__(self, server):
        self.server = server
        self.guid = ''
        self._buffer = b''
    
    def connection_made(self, transport):
        self.transport = transport
    
    def data_received(self, data):
        '''
        收到包，使用DELIMITER(*)拆包
        :param data:
        '''
        self._buffer += data
        
        while True:
            try:
                line, self._buffer = self._buffer.split(
                    DELIMITER, 1)
            except ValueError:
                break
            else:
                self.message_received(line)
    
    def message_received(self, msg):
        '''
        拆包后进行解码，并找到cmd对应的processor
        :param msg:
        '''
        try:
            msg = decode(msg)
            processor = processors[msg['cmd']]
            task = self.server.loop.create_task(processor(self, msg))
            task.add_done_callback(self.done)
        except DecodeException:
            logging.error("%r => base64解码失败！", msg)
        except UnkownCommandException:
            logging.error("%r => 未知命令！", msg)
        except FormatException:
            logging.error("%r => 数据结构错误！", msg)
            
    def done(self, future):
        print(future.result())
            
    def connection_lost(self, error):
        if error:
            logging.error("Error: {}".format(error))
        else:
            logging.info("Closing")
            
    def eof_received(self):
        print("Received EOF")
        if self.transport.can_write_eof():
            self.transport.write_eof()
                
    
        
        