import logging
import json
from collections import defaultdict

from ddconnector.decoder import encode

waiters = defaultdict(list)

async def randompwd(protocol, msg):
    """
    处理开门
    """
    if 'isClient' in msg:
        # 发起开门
        logging.info("收到下发开门密码请求！guid: %s", msg['guid'])
        request_message = {'cmd': 'randomPwd',
                           'request_id': msg['guid'],
                           'response_params': 
                                {'data': [json.loads(msg['data'])],
                                 'message': '',
                                 'success': True,
                                 'totalCount': '0'},
                           'response_type': False,
                           'token_id': ''}
        request_message = encode(request_message)
        protocol.server.transports[msg['guid']].write(request_message)
        # 建立guid => [等待回复者列表]建立关系，方便门禁返回时回复
        waiters[msg['guid']].append(protocol.transport)
    else:
        # 收到门禁开门回复
        logging.info("收到下发开门密码回复！guid: %s", msg['guid'])
        response_message = {'cmd': 'randomPwd',
                             'request_id': msg['guid'],
                             'response_params': {'data': [],
                                                 'message': '',
                                                 'success': True,
                                                 'totalCount': '0'},
                             'response_type': True,
                             'token_id': ''}
        response_message = encode(response_message)
        # 根据之前的门禁guid => [等候者列表]关系进行回包
        for transport in waiters[msg['guid']]:
            transport.write(response_message)
        
        try:
            del waiters[msg['guid']]
        except KeyError:
            pass