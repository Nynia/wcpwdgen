from . import main
from flask import jsonify, request, make_response
import json
import xml.etree.ElementTree as ET
import hashlib
import time
import urllib.request
import urllib.parse
from config import TOKEN, APPID, APPSECRET


@main.route('/test', methods=['GET'])
def test():
    return jsonify(
        {
            'code': 0,
            'msg': 'main test'
        }
    )


@main.route('/', methods=['GET', 'POST'])
def wechat_auth():
    if request.method == 'GET':
        token = TOKEN
        signature = request.args.get('signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        echostr = request.args.get('echostr', '')

        str = [timestamp, nonce, token]
        print(str)
        str.sort()
        str = ''.join(str)
        print(str)
        hashlib.sha1(str).hexdigest()

        if hashlib.sha1(str).hexdigest() == signature:
            return make_response(echostr)
    else:
        rec = request.stream.read()
        xml_rec = ET.fromstring(rec)
        touser = xml_rec.find('ToUserName').text
        fromuser = xml_rec.find('FromUserName').text
        content = xml_rec.find('Content').text
        print([touser, fromuser, content])

        print(sumof(fromuser + touser))
        password = gen_password(hashlib.sha1(content + touser).hexdigest(), sumof(fromuser))
        print(password)
        xml_rep = '''<xml>
            <ToUserName><![CDATA[%s]]></ToUserName>
            <FromUserName><![CDATA[%s]]></FromUserName>
            <CreateTime>%s</CreateTime>
            <MsgType><![CDATA[text]]></MsgType>
            <Content><![CDATA[%s]]></Content>
            <FuncFlag>0</FuncFlag>
            </xml>
        '''
        response = make_response(xml_rep % (fromuser, touser, str(int(time.time())), password))
        response.content_type = 'application/xml'
        return response


def get_access_token():
    url = 'https://api.weixin.qq.com/cgi-bin/token'
    payload = {
        'grant_type': 'client_credential',
        'appid': 'wx0c3b0b616cc6e6f7',
        'secret': 'b581d3bb9f90737ce1322da5bd79699b'
    }
    data = urllib.parse.urlencode(payload)
    req = urllib.request.Request(url, data)
    response = urllib.request.urlopen(req)
    result = json.loads(response.read())
    return result.get('access_token')


def gen_password(str, openid):
    alpha = []
    for i in range(48, 58):
        alpha.append(chr(i))
    for i in range(65, 91):
        alpha.append((chr(i)))
    for i in range(97, 123):
        alpha.append((chr(i)))
    for i in ['!', '@', '#', '$', '^', '&', '%', '+']:
        alpha.append(i)
    seq = ''.join(['{:0=8b}'.format(ord(i)) for i in str]).lstrip('0')
    result = ''
    i = 0
    slice = seq[i:i + 10]
    slice_int = int(slice, base=2)
    result += alpha[slice_int % 10]
    i += 10

    while i < len(seq) and seq[i] == '0':
        i += 1
    slice = seq[i:i + 10]
    slice_int = int(slice, base=2)
    result += alpha[slice_int % 10]
    i += 10

    while i < len(seq) and seq[i] == '0':
        i += 1
    slice = seq[i:i + 10]
    slice_int = int(slice, base=2)
    result += alpha[slice_int % 26 + 10]
    i += 10

    while i < len(seq) and seq[i] == '0':
        i += 1
    slice = seq[i:i + 10]
    slice_int = int(slice, base=2)
    result += alpha[slice_int % 26 + 36]
    i += 10

    while i < len(seq) and seq[i] == '0':
        i += 1
    slice = seq[i:i + 10]
    slice_int = int(slice, base=2)
    result += alpha[slice_int % 26 + 36]
    i += 10

    while i < len(seq) and seq[i] == '0':
        i += 1
    slice = seq[i:i + 10]
    slice_int = int(slice, base=2)
    result += alpha[slice_int % 8 + 62]
    i += 10

    permutation_list = []
    gen_permutation('123456', '', permutation_list)
    residual = openid % 64
    return ''.join([result[int(i) - 1] for i in permutation_list[residual]])


def gen_permutation(s1, s2, result):
    if len(s1) == 1:
        result.append(str(s1) + str(s2))
    else:
        for i in s1:
            tmp_list = list(s1[:])
            tmp_list.remove(i)
            gen_permutation(''.join(tmp_list), s2 + i, result)


def sumof(str):
    result = 0
    for i in str:
        result += ord(i)
    return result
