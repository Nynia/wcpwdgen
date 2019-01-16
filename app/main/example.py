from . import main
from flask import jsonify, request, make_response
import xml.etree.ElementTree as ET
import hashlib
import time
import urllib.request
import urllib.parse
from config import TOKEN
import json
from app.utils.keyword import get_all_keywords, add_keyword


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
        payload = [timestamp, nonce, token]
        print(payload)
        payload.sort()
        payload = ''.join(payload)
        hashlib.sha1(payload).hexdigest()

        if hashlib.sha1(payload.encode('utf-8')).hexdigest() == signature:
            return make_response(echostr)
    else:
        rec = request.stream.read()
        xml_rec = ET.fromstring(rec)

        touser = xml_rec.find('ToUserName').text
        fromuser = xml_rec.find('FromUserName').text
        content = xml_rec.find('Content').text.strip()
        print([touser, fromuser, content])

        password = gen_password(hashlib.sha1((content + touser).encode('utf-8')).hexdigest(), sumof(fromuser))
        xml_rep = '''<xml>
                    <ToUserName><![CDATA[%s]]></ToUserName>
                    <FromUserName><![CDATA[%s]]></FromUserName>
                    <CreateTime>%s</CreateTime>
                    <MsgType><![CDATA[text]]></MsgType>
                    <Content><![CDATA[%s]]></Content>
                    <FuncFlag>0</FuncFlag>
                    </xml>
                '''
        restr = ''
        if content == 'help':
            pass
        elif content == 'list':
            pass
        elif content == 'history':
            pass
        else:
            content_splited = content.split(' ')
            keyword = content_splited[0]
            account = content_splited[1] if len(content_splited) > 1 else ''
            mode = content_splited[2] if len(content_splited) > 2 else ''

            if keyword.startswith('http://'):
                keyword = keyword[7:]

            print([keyword, account, mode])
            keywords = get_all_keywords()
            print(keywords)
            match = search_best_match(keywords, keyword)
            print(match)
            if match[0] == 0:
                # 数据库有完全匹配的记录
                if len(match[1]) == 1:
                    restr = match[1][0] + '----' + password
                else:
                    for i in range(len(match[1])):
                        restr += match[1][i] + '\n'

            elif match[0] == 1:
                # 数据库有不完全匹配的记录
                for i in range(len(match[1])):
                    restr += match[1][i] + '\n'
            else:
                # 首次出现
                restr = keyword + '----' + password
                # keyword 添加到数据库
                add_keyword(keyword)


            response = make_response(xml_rep % (fromuser, touser, str(int(time.time())), restr))
            response.content_type = 'application/xml'
            return response

        # print(sumof(fromuser + touser))

        # print(password)
        #
        # response = make_response(xml_rep % (fromuser, touser, str(int(time.time())), password))
        # response.content_type = 'application/xml'
        # return response


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


def naive_string_match(T, P, idx=-1):
    n = len(T)
    m = len(P)

    for s in range(0, n - m + 1):
        k = 0
        for i in range(0, m):
            if T[s + i] != P[i] and idx != i:
                break
            else:
                k += 1
        if k == m:
            return s
    return -1


def search_best_match(rsp, w2):
    result = (-1, [])
    if '.' not in w2:
        for k in rsp:
            w1 = k.keyword
            if naive_string_match(w1, w2) >= 0:
                if result[0] == 0:
                    result[1].append(w1)
                else:
                    result = (0, [w1])
            if result[0] == 0:
                continue
            for i in range(1, len(w2)):
                if naive_string_match(w1, w2, i) >= 0:
                    if result[0] == -1:
                        result = (1, [w1])
                    else:
                        result[1].append(w1)
    else:
        for k in rsp:
            w1 = k.keyword
            if naive_string_match(w1, w2) == 0:
                return 0, [w1]
            for i in range(1, len(w2)):
                if naive_string_match(w1, w2, i) == 0:
                    return 1, [w1]
    if result[0] == -1:
        # 搜索标签
        for k in rsp:
            l1 = k.label1
            if not l1:
                continue
            if naive_string_match(l1, w2) == 0:
                return 0, [k['keyword']]
            for i in range(1, len(w2)):
                if naive_string_match(l1, w2, i) == 0:
                    return 1, [k['keyword']]

    return result
