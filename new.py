#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import os
import random
import requests
import six
import sys
import time

# from Crypto.Cipher import AES
# import base64
# import hashlib

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

LOG = logging.getLogger(__name__)

START_CHAT_COMTENTS = ['出来聊天啦！', '冒泡', '[发呆]', '天气不错[微笑]', '出来尬聊了~', ]
LAST_CHAT_CONTENT = random.sample(START_CHAT_COMTENTS, 1)[0]


class Client(object):
    """HTTP client.
    """

    def _json_request(self, method, path, **kwargs):
        url = ''.join([path])
        url_info = "Request url ...%s" % url
        LOG.debug(url_info)

        response = requests.request(method, url, **kwargs)
        response_info = "Got response:%s" % response
        LOG.debug(response_info)

        body = response.content
        try:
            body = json.loads(body)
        except ValueError:
            LOG.debug('Could not decode response body as JSON')

        return response, body

    def get(self, url, **kwargs):
        return self._json_request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self._json_request("POST", url, **kwargs)

    def put(self, url, **kwargs):
        return self._json_request("PUT", url, **kwargs)

    def delete(self, url, **kwargs):
        return self._json_request('DELETE', url, **kwargs)


class genarate_pos():
    def __init__(self):
        """
        左上角坐标: 114.391847,30.518829
        """
        self.start_x = 114.511
        self.start_y = 30.561398
        self.max_offset_x = 0.003426
        self.max_offset_y = 0.003284

    def get_random_pos(self):
        return (self.start_x + random.uniform(-self.max_offset_x, self.max_offset_x),
                self.start_y + random.uniform(-self.max_offset_y, self.max_offset_y))


def translate_pos(c, x, y):
    baidu_url = "http://api.map.baidu.com/geocoder/v2/?ak=Es0Zdh4LrqUwnh" \
                "8ylnxCXd44oNFZhcxA&location=" \
                "%s,%s&output=json&pois=1" % (y, x)
    resp, body = c.get(baidu_url)
    # return body["result"]["pois"][0]["name"]
    return body["result"]["formatted_address"]


def setup_log():
    timestruct = time.localtime(time.time())
    timestr = time.strftime('%Y-%m-%d %H:%M:%S', timestruct)
    logfilename = "sign_youqu_%s.log" % timestr

    LOG_FILE = os.path.join(os.path.split(os.path.abspath(__file__))[0],
                            logfilename)

    FORMAT = '%(asctime)s | %(levelname)s | %(lineno)04d | %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=FORMAT,
        filemode='a',
        filename=LOG_FILE,
    )

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter(FORMAT)
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


def sign(c, user_name, user_id, imei, group_id, pos_name, x, y):
    url = "http://msp.iyouqu.com.cn:19443/app/huanxin/service.do"
    pos_str = "在%s签到啦！" % pos_name.encode('utf-8')
    # pos_str = "在悉尼歌剧院签到啦！"
    params = {
        "groupId": group_id,
        "imei": imei,
        "userName": user_name,
        "userId": user_id,
        "msgId": "SIGN_HUANXIN",
        "position": pos_str,
        "longitude": round(x, 6),
        "latitude": round(y, 6),
        "province": "湖北省",
    }
    data = json.dumps(params, sort_keys=False, separators=(',', ':'),
                      ensure_ascii=False)
    LOG.info(data)
    body = {"text": data}
    return c.post(url, data=body)


def chat_in_group(c, group_id, user_id, content):
    url = "http://msp.iyouqu.com.cn:19443/app/group/service.do"
    # url = "http://common.msp.iyouqu.com.cn:19443/app/group/service.do"
    params = {
        "content": content,
        "userId": user_id,
        "msgId": "GET_OFFLINEMSG",
        "isOriginal": True,
        "groupId": group_id,
        "type": 1,
        "isForward": False
    }
    data = json.dumps(params, sort_keys=False, separators=(',', ':'),
                      ensure_ascii=False)
    print data
    body = {"text": data}
    return c.post(url, data=body)



def get_newest_activities(c, user_id):
    url = "http://msp.iyouqu.com.cn:19443/app/newsActivity/service.do"
    params = {
        "userId": user_id,
        "msgId": "APP150",
        "department": "02AJ1043",
        "index": 0,
        "categoryType": 0,
        "categoryId": -1,
        "isComplete": False,
    }
    data = json.dumps(params, sort_keys=False, separators=(',', ':'),
                      ensure_ascii=False)
    body = {"text": data}
    resp, body = c.post(url, data=body)
    # LOG.info("resp: %(resp)s, body: %(body)s", {'resp': resp,
    #                                             'body': body})
    return body["resultMap"]["objectList"]


def view_activities(c, user_id, objectId):
    url = "http://msp.iyouqu.com.cn:19443/app/newsActivity/service.do"
    params = {
        "userId": user_id,
        "msgId": "APP009",
        "objectId": objectId,
        "opinion": 0,
    }
    data = json.dumps(params, sort_keys=False, separators=(',', ':'),
                      ensure_ascii=False)
    body = {"text": data}
    return c.post(url, data=body)


def comment_activities(c, user_id, targetId):
    url = "http://msp.iyouqu.com.cn:19443/app/service.do"
    Content = ['good！手动点赞', '更加强大[微笑]', '加油[微笑][微笑][微笑]再接再厉', '公司越来越强大[微笑]，再接再厉！', '真棒','厉害了','愈强大','wonderful','good']
    our_content = random.sample(Content, 1)[0]
    params = {
        "userId": user_id,
        "msgId": "APP039",
        "content": our_content,
        "targetId": targetId,
        "targetType": 2,
    }
    data = json.dumps(params, sort_keys=False, separators=(',', ':'),
                      ensure_ascii=False)
    body = {"text": data}
    return c.post(url, data=body)


def get_user_info(c, user_id):
    """
    获取用户信息
    :param c:
    :return:
    """
    url = "http://msp.iyouqu.com.cn:19443/app/service.do"
    params = {'msgId': 'APP093', 'userId': user_id}
    data = json.dumps(params, sort_keys=False, separators=(',', ':'),
                      ensure_ascii=False)
    # print data
    body = {"text": data}
    return c.post(url, data=body)


def get_group_info(c, group_id, user_id):
    """
    获取用户信息
    :param c:
    :return:
    """
    url = "http://msp.iyouqu.com.cn:19443/app/huanxin/service.do"
    params = {'groupId': group_id, 'msgId': 'GET_GROUPUSERINFO_HUANXIN'}
    data = json.dumps(params, sort_keys=False, separators=(',', ':'),
                      ensure_ascii=False)
    # print data
    body = {"text": data}
    return c.post(url, data=body)


def set_up():
    setup_log()
    return Client()


def getimei(imei_map):
    fp = open("imei.txt", "r")
    imeis = []
    data = fp.readlines()
    for line in data:
        imeis.append(line.strip())

    fp.close()

    for _, v in imei_map.items():
        if v in imeis:
            imeis.remove(v)

    if len(imeis) > 0:
        return imeis[0]
    else:
        return "Joo9/nT8JkasBcA6gB4+ZA\u003d\u003d"


def sign_all_user_in_group(c, userlist, group_id, interval):
    filename = "userid_imei_map.txt";
    if not os.path.exists(filename):
        fp = open(filename, "w");
        fp.write("{}")
        fp.close()

    fp = open(filename, "r")
    b = fp.readline()
    fp.close()
    imei_map = json.loads(b)

    try:
        userlist = random.sample(userlist, len(userlist))
        for user in userlist:

            time.sleep(random.randint(2, interval))

            username = user["userName"].encode('utf-8')
            userid = user["userId"].encode('utf-8')

            if not imei_map.has_key(userid) or not bool(imei_map[userid]):
                imei_map[userid] = getimei(imei_map)

            userimei = imei_map[userid].encode('utf-8')

            x, y = genarate_pos().get_random_pos()
            pos_name = translate_pos(c, x, y)
            sign_resp, sign_body = sign(c, username, userid, userimei,
                                        group_id, pos_name, x, y)
            # zh_body = json.dumps(sign_body).decode("unicode_escape")
            LOG.info("User %(name)s :sign in youqu, resp: %(resp)s, "
                     "body: %(body)s", {'name': user['userName'],
                                        'resp': sign_resp,
                                        'body': sign_body})

    except Exception, e:
        LOG.error("except: %s", e.message)

        fp = open(filename, "w")
        fp.write(json.dumps(imei_map))
        fp.close()


def chat_all_user_in_group(c, userlist, group_id, interval):
    global LAST_CHAT_CONTENT
    try:
        userlist = random.sample(userlist, len(userlist))
        for user in userlist:
            username = user["userName"].encode('utf-8')
            userid = user["userId"].encode('utf-8')

            chat_resp, chat_body = chat_in_group(c, group_id,userid, LAST_CHAT_CONTENT)
            LOG.info("User %(userName)s :chat in youqu, resp: %(resp)s, "
                     "body: %(body)s", {'userName': username,'resp': chat_resp,'body': chat_body})

            time.sleep(random.randint(2, interval))

            LAST_CHAT_CONTENT = chat_tuling(c, LAST_CHAT_CONTENT)

    except Exception, e:
        LOG.error("except: %s", e.message)


def chat_tuling(c, content):
    '''
    图灵机器人， 自行设置 apiKey userId
    :param c:
    :param content:
    :return:
    '''
    url = "http://openapi.tuling123.com/openapi/api/v2"
    params = {
        "perception": {
            "inputText": {
                "text": content
            }
        },
        "userInfo": {
            "apiKey": "b718dc38fa2c40a4a5a39569729d70ff",
            "userId": "403238"
        }
    }
    data = json.dumps(params, sort_keys=False, separators=(',', ':'),
                      ensure_ascii=False)

    chat_resp, chat_body = c.post(url, data=data)
    try:
        return chat_body['results'][0]['values']['text'].encode('utf-8')
    except Exception, e:
        return "[发呆]"

    # return chat_resp, chat_body


class YOUQU:
    #设置这两个参数
    group_id = "77526748692482"
    user_id = "10148"

    sign_interval = 30
    chat_interval = 20
    comment_interval = 10

    def __init__(self):
        self.c = set_up()
        resp, body = get_group_info(self.c, self.group_id, self.user_id)
        self.userlist = body["resultMap"]["userInfo"]

        self.newest_activities = get_newest_activities(self.c, self.user_id)


    def sign_all(self, args=None):
        sign_all_user_in_group(self.c, self.userlist, self.group_id,
                               self.sign_interval)

    def chat_all(self, args=None):
        """
        参数 1 ： 每个人发言的数量
        参数 1 ： 每个人发言的数量
        """
        ulist = []
        try:
            count = int(args[0])
            if count > 0:
                for i in range(count):
                    ulist.extend(random.sample(self.userlist, len(self.userlist)))

        except Exception as e:
            LOG.error(e.message)
            ulist = self.userlist
        chat_all_user_in_group(self.c, ulist, self.group_id,
                               self.chat_interval)

    def comment_all(self, args=None):
        try:
            userlist = random.sample(self.userlist, len(self.userlist))
            for user in userlist:
                # time.sleep(random.randint(10, self.comment_interval))

                userid = user["userId"].encode('utf-8')

                n = 1

                activities = random.sample(self.newest_activities, n)
                for activity in activities:
                    resp, body = view_activities(self.c, userid, activity['id'])
                    LOG.info("resp: %(resp)s, body: %(body)s", {'resp': resp,
                                                                'body': body})
                    time.sleep(random.randint(3, self.comment_interval))
                    resp, body = comment_activities(self.c, userid, activity['id'])
                    LOG.info("resp: %(resp)s, body: %(body)s", {'resp': resp,
                                                                'body': body})



        except Exception, e:
            LOG.error("except: %s", e.message)

    def help(self, args=None):
        print filter(lambda x: callable(getattr(self, x)), dir(self))


if __name__ == "__main__":
    youqu = YOUQU()

    # youqu.comment_all()

    #################################################

    if len(sys.argv) < 2:
        youqu.help()
        exit(1)

    command = sys.argv[1]

    args = sys.argv[2:]

    if not hasattr(youqu, command):
        youqu.help()
        exit(1)

    ret = getattr(youqu, command)

    ret(args)
