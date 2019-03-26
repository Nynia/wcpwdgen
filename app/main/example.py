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
from app.utils.master import update_rel, get_rel_by_keyword_and_account, get_rels_by_keyword, get_rels_by_openid
from app.utils.user import *
from app.utils.record import add_new_record
import string
import math


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
        event = xml_rec.find('Event').text
        print([touser, fromuser, content, event])
        if event == 'subscribe':
            content = 'help'
        xml_rep = '''<xml>
                    <ToUserName><![CDATA[%s]]></ToUserName>
                    <FromUserName><![CDATA[%s]]></FromUserName>
                    <CreateTime>%s</CreateTime>
                    <MsgType><![CDATA[text]]></MsgType>
                    <Content><![CDATA[%s]]></Content>
                    <FuncFlag>0</FuncFlag>
                    </xml>
                '''
        # record
        add_new_record(fromuser, content)

        restr = ''
        if content == 'help':
            xml_rep = '''<xml>
                        <ToUserName><![CDATA[%s]]></ToUserName>
                        <FromUserName><![CDATA[%s]]></FromUserName>
                        <CreateTime>%s</CreateTime>
                        <MsgType><![CDATA[image]]></MsgType>
                        <Image>
                            <MediaId><![CDATA[%s]]></MediaId>
                        </Image>
                        </xml>
                        '''
            media_id = 'ck87880KC8H90pszDj6Xoz7uFjGFX0KCOTNP4aAIWNs'
            response = make_response(xml_rep % (fromuser, touser, str(int(time.time())), media_id))
            response.content_type = 'application/xml'
            return response
        elif content == 'list':
            items = get_rels_by_openid(fromuser)
            for item in items:
                restr += item.keyword + '\n' + item.account + '\n---------------------\n'
            response = make_response(xml_rep % (fromuser, touser, str(int(time.time())), restr))
            response.content_type = 'application/xml'
            return response
        elif content.startswith('add'):
            content_splited = content.split(' ')
            label1 = None
            label2 = None
            if len(content_splited) < 2:
                restr = "参数错误"
            else:
                keyword = content_splited[1]
                if len(content_splited) > 2:
                    label1 = content_splited[2]
                if len(content_splited) > 3:
                    label2 = content_splited[3]
                add_keyword(keyword, label1, label2)
                restr = "成功"
            response = make_response(xml_rep % (fromuser, touser, str(int(time.time())), restr))
            response.content_type = 'application/xml'
            return response
        elif content.startswith('set'):
            content_splited = content.split(' ')
            if len(content_splited) > 2:
                email = content_splited[1]
                mode = content_splited[2]
                add_new_user(fromuser, email, mode)
                restr = "设置成功"
            elif len(content_splited) > 1:
                if content_splited[1].isnumeric():
                    mode = content_splited[1]
                    email = None
                else:
                    email = content_splited[1]
                    mode = None
                add_new_user(fromuser, email, mode)
                restr = "设置成功"
            else:
                restr = "参数错误"
            response = make_response(xml_rep % (fromuser, touser, str(int(time.time())), restr))
            response.content_type = 'application/xml'
            return response
        elif content.startswith("old"):
            content_splited = content.split(' ')
            content = content_splited[1]
            password = gen_password(hashlib.sha1((content + touser).encode('utf-8')).hexdigest(), sumof(fromuser))
            response = make_response(xml_rep % (fromuser, touser, str(int(time.time())), password))
            response.content_type = 'application/xml'
            return response
        else:
            content_splited = content.split(' ')
            keyword = content_splited[0]
            if len(content_splited) > 2:
                account = content_splited[1]
                mode = content_splited[2]
            elif len(content_splited) > 1:
                if content_splited[1].isnumeric():
                    mode = content_splited[1]
                    account = None
                else:
                    account = content_splited[1]
                    mode = None
            else:
                account = None
                mode = None
            if keyword.startswith('http://'):
                keyword = keyword[7:]
            print([keyword, account, mode])

            if account is None:
                items = get_rels_by_keyword(fromuser, keyword)
                if len(items) == 0:
                    user = get_user_by_openid(fromuser)
                    if not user:
                        restr = "请先初始化默认账户 init XXX@mail.com"
                        response = make_response(xml_rep % (fromuser, touser, str(int(time.time())), restr))
                        response.content_type = 'application/xml'
                        return response
                    else:
                        account = user.email
                        if mode is None:
                            mode = user.mode
                elif len(items) == 1:
                    account = items[0].account
                    if mode is None:
                        mode = items[0].mode
                else:
                    restr = "存在多个账号，请具体指定:"
                    for item in items:
                        restr += "\n%s" % item.account
                    response = make_response(xml_rep % (fromuser, touser, str(int(time.time())), restr))
                    response.content_type = 'application/xml'
                    return response
            else:
                item = get_rel_by_keyword_and_account(fromuser, keyword, account)
                if item is None:
                    user = get_user_by_openid(fromuser)
                    if not user:
                        restr = "请先初始化默认账户 init XXX@mail.com"
                        response = make_response(xml_rep % (fromuser, touser, str(int(time.time())), restr))
                        response.content_type = 'application/xml'
                        return response
                    else:
                        mode = user.mode
                else:
                    if mode is None:
                        mode = item.mode

            keywords = get_all_keywords()
            match = search_best_match(keywords, keyword)
            print(match)
            if match[0] == 0:
                # 数据库有完全匹配的记录
                if len(match[1]) == 1:
                    restr = match[1][0] + '\n' + account + '\n' + gen_password2(match[1][0] + account + fromuser,
                                                                                int(mode))
                else:
                    for i in range(len(match[1])):
                        restr += match[1][i] + '\n'
                update_rel(fromuser, keyword, account, mode)

            elif match[0] == 1:
                # 数据库有不完全匹配的记录
                restr = "Do you mean?\n"
                for i in range(len(match[1])):
                    restr += match[1][i] + '\n'
            else:
                # 首次出现
                restr = keyword + '\n' + account + '\n' + gen_password2(keyword + account + fromuser, int(mode))
                # update数据库
                add_keyword(keyword, None, None)
                update_rel(fromuser, keyword, account, mode)

            response = make_response(xml_rep % (fromuser, touser, str(int(time.time())), restr))
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


def gen_password2(s, mode):
    digest = hashlib.sha1(s.encode('utf-8')).hexdigest()
    digest += ' ' + digest[1:] + digest[0]
    password = ''
    print(digest)
    special_symbol_list = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '+', '~']
    length = mode // 100
    if mode % 10 == 1:
        # 纯数字
        repeat = False
        for i in range(0, 80, 2):
            print(digest[i:i + 2])
            number = str(int(digest[i:i + 2], 16) % 10)
            if len(password) == length:
                break
            if repeat and number in password:
                continue
            if number in password:
                repeat = True
            password += str(int(digest[i:i + 2], 16) % 10)
    elif mode % 10 == 2:
        # 数字+小写字母
        lowercase_number = length // 2
        digit_number = length - lowercase_number
        digit_repeat = False
        lowercase_repeat = False
        c = 0
        for i in range(0, 80, 2):
            digit = str(int(digest[i:i + 2], 16) % 10)
            if len(password) == digit_number:
                c = i + 2
                break
            if digit_repeat and digit in password:
                continue
            if digit in password:
                digit_repeat = True
            password += digit
        for i in range(c, 80, 2):
            lowercase = string.ascii_lowercase[(int(digest[i:i + 2], 16) % 26)]
            if len(password) == length:
                break
            if lowercase_repeat and lowercase in password:
                continue
            if lowercase in password:
                lowercase_repeat = True
            password += lowercase
    elif mode % 10 == 3:
        digit_number = 3 + (length - 3) // 4
        lowercase_number = 2 + (length - 4) // 4
        uppercase_number = 1 + (length - 5) // 4
        c = 0
        for i in range(0, digit_number * 2, 2):
            digit = str(int(digest[i:i + 2], 16) % 10)
            password += digit
            c = i + 2
        for i in range(c, c + lowercase_number * 2, 2):
            lowercase = string.ascii_lowercase[(int(digest[i:i + 2], 16) % 26)]
            password += lowercase
            c = i + 2
        for i in range(c, c + uppercase_number * 2, 2):
            uppercase = string.ascii_uppercase[(int(digest[i:i + 2], 16) % 26)]
            password += uppercase

    elif mode % 10 == 4:
        # 数字+字母+特殊符号
        digit_number = 2 + (length - 3) // 4
        lowercase_number = 2 + (length - 4) // 4
        uppercase_number = 1 + (length - 5) // 4
        special_symbol_number = 1 + (length - 6) // 4
        c = 0
        for i in range(0, digit_number * 2, 2):
            digit = str(int(digest[i:i + 2], 16) % 10)
            password += digit
            c = i + 2
        for i in range(c, c + lowercase_number * 2, 2):
            lowercase = string.ascii_lowercase[(int(digest[i:i + 2], 16) % 26)]
            password += lowercase
            c = i + 2
        for i in range(c, c + uppercase_number * 2, 2):
            uppercase = string.ascii_uppercase[(int(digest[i:i + 2], 16) % 26)]
            password += uppercase
            c = i + 2
        for i in range(c, c + special_symbol_number * 2, 2):
            special_symbol_number = special_symbol_list[(int(digest[i:i + 2], 16) % 13)]
            password += special_symbol_number
    permutation_list = []
    gen_permutation(password, '', permutation_list)
    residual = sum([ord(i) for i in digest]) % math.factorial(length)

    return permutation_list[residual]


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
            print(k)
            l1 = k.label1
            if not l1:
                continue
            if naive_string_match(l1, w2) == 0:
                return 0, [k.keyword]
            for i in range(1, len(w2)):
                if naive_string_match(l1, w2, i) == 0:
                    return 1, [k.keyword]

    return result
