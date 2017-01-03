# -*- coding: utf-8 -*-

import os
import time
import struct
import json
import requests
from requests import exceptions
from werkzeug.urls import url_fix
from collections import OrderedDict

from pysteamkit.protobuf import steammessages_clientserver_pb2
from pysteamkit.steam_base import EMsg, EResult
from pysteamkit.steam3.client import SteamClient
from pysteamkit.steam3 import msg_base
from pysteamkit.util import Util

from CSGOproto import csgo_base, gcsdk_gcmessages_pb2, cstrike15_gcmessages_pb2
from gevent import sleep, Timeout

CURRENCY = OrderedDict([("USD", (1, u"$")),
                        ("GBP", (2, u"£")),
                        ("EUR", (3, u"€")),
                        ("CHF", (4, u"CHF")),
                        ("RUB", (5, u"pуб")),
                        ("BRL", (7, u"R$")),
                        ("JPY", (8, u"¥")),
                        ("SEK", (9, u"kr")),
                        ("IDR", (10, u"Rp")),
                        ("MYR", (11, u"RM")),
                        ("PHP", (12, u"P")),
                        ("SGD", (13, u"S$")),
                        ("THB", (14, u"฿")),
                        ("KRW", (16, u"₩")),
                        ("TRY", (17, u"TL")),
                        ("MXN", (19, u"Mex$")),
                        ("CAD", (20, u"CDN$")),
                        ("NZD", (22, u"NZ$")),
                        ("CNY", (23, u"¥")),
                        ("INR", (24, u"₹")),
                        ("CLP", (25, u"CLP$")),
                        ("PEN", (26, u"S")),
                        ("COP", (27, u"COL$")),
                        ("ZAR", (28, u"R")),
                        ("HKD", (29, u"HK$")),
                        ("TWD", (30, u"NT$")),
                        ("SRD", (31, u"SR")),
                        ("AED", (32, u"AED"))])

logging = 0
try:
    with open('settings.txt', 'r') as settings:
        for line in settings.readlines():
            if line.startswith('logging='):
                logging = int(line.replace('logging=', ''))
except IOError:
    logging = 1


def logEvent(text, forced=False):
    if logging > 0 or forced:
        t = time.strftime(">%H:%M:%S")
        with open('log.txt', 'a') as logfile:
            logfile.write('%s: %s\n' % (t, text))


class SteamClientHandler(object):
    def __init__(self, messageHandler):
        self.messageHandler = messageHandler
        self.auth_code = None
        self.two_factor_code = None
        self.firstlogin = False

    def try_initialize_connection(self, client):
        logEvent('Trying to initialize...')
        if not self.get_sentry_file(self.messageHandler.username):
            self.firstlogin = True

        logon_result = self.messageHandler.client.login(self.messageHandler.username, self.messageHandler.password,
                                                        auth_code=self.auth_code, two_factor_code=self.two_factor_code)
        logEvent('Logon result ' + str(logon_result.eresult))

        if logon_result.eresult == EResult.AccountLogonDenied:
            client.disconnect()
            # Steam Guard enabled, Steam sent authentication code to email

        if logon_result.eresult != EResult.OK:
            return logon_result.eresult

        return True

    def get_sentry_file(self, username):
        filename = 'sentry_%s.bin' % (username,)
        if not os.path.exists(filename):
            return None

        with open(filename, 'rb') as f:
            return f.read()

    def store_sentry_file(self, username, sentryfile):
        if not self.two_factor_code:
            filename = 'sentry_%s.bin' % (username,)
            with open(filename, 'wb') as f:
                f.write(sentryfile)

    def handle_message(self, emsg, msg):
        if logging == 2:
            logEvent('Received message ' + str(Util.get_msg(emsg)))
        pass

    def handle_disconnected(self, client, user_reason):
        if not user_reason:
            logEvent('Disconnected!')
            for x in range(5):
                time.sleep(x + 1)
                if client.initialize():
                    return True
        return False


class SteamGC(object):
    def __init__(self, client, appid):
        self.client = client
        self.appid = appid

    def gcSend(self, inputmsg):
        Type = inputmsg.header.emsg
        if logging == 2:
            logEvent('gcSend ' + str(Util.get_msg(Type)))

        message = msg_base.ProtobufMessage(steammessages_clientserver_pb2.CMsgGCClient, EMsg.ClientToGC)

        message.header.routing_appid = self.appid
        message.body.appid = self.appid
        message.body.msgtype = Type|0x80000000 if Util.is_proto(Type) else Type
        message.body.payload = inputmsg.serialize()

        self.client.connection.send_message(message)

    def gcFrom(self, data, protobufType):
        if logging == 2:
            logEvent('gcFrom ' + str(protobufType))
        message = msg_base.ProtobufMessage(protobufType)
        message.parse(data)
        return message.body


class CSGO(object):
    def __init__(self, gc=None):
        self.appid = 730
        self.gc = gc
        self.gc.client.register_listener(self)
        self.gc.client.register_message(csgo_base.GCConnectionStatus.GCConnectionStatus_HAVE_SESSION,
                                        msg_base.ProtobufMessage,
                                        cstrike15_gcmessages_pb2.CMsgGCCStrike15_v2_Client2GCEconPreviewDataBlockRequest)
        self.gc.client.register_message(csgo_base.ECSGOCMsg.k_EMsgGCCStrike15_v2_Client2GCEconPreviewDataBlockResponse,
                                        msg_base.ProtobufMessage,
                                        cstrike15_gcmessages_pb2.CMsgGCCStrike15_v2_Client2GCEconPreviewDataBlockResponse)
        self.gc.client.register_message(csgo_base.EGCBaseClientMsg.k_EMsgGCClientWelcome, msg_base.ProtobufMessage,
                                        gcsdk_gcmessages_pb2.CMsgClientWelcome)
        self.gc.client.register_message(EMsg.ClientPlayingSessionState, msg_base.ProtobufMessage,
                                        steammessages_clientserver_pb2.CMsgClientPlayingSessionState)
        self.gc.client.register_message(EMsg.ClientToGC, msg_base.ProtobufMessage,
                                        steammessages_clientserver_pb2.CMsgGCClient)
        self.gc.client.register_message(EMsg.ClientFromGC, msg_base.ProtobufMessage,
                                        steammessages_clientserver_pb2.CMsgGCClient)

    def handle_message(self, emsg, msg):
        emsg = Util.get_msg(emsg)

        if emsg == EMsg.ClientLoggedOff:
            # Game already started on account
            self.exit()

    def sendClientHello(self):
        message = msg_base.ProtobufMessage(gcsdk_gcmessages_pb2.CMsgClientHello,
                                           csgo_base.EGCBaseClientMsg.k_EMsgGCClientHello)

        self.gc.gcSend(message)
        response = self.gc.client.wait_for_message(EMsg.ClientFromGC)
        return response

    def launch(self):
        message = msg_base.ProtobufMessage(steammessages_clientserver_pb2.CMsgClientGamesPlayed, EMsg.ClientGamesPlayed)
        message.body.games_played.add(game_id=self.appid)
        self.gc.client.connection.send_message(message)

        time.sleep(3)
        response = self.sendClientHello()

        if Util.get_msg(response.body.msgtype) == csgo_base.EGCBaseClientMsg.k_EMsgGCClientWelcome:
            logEvent('Launch successful!')
            return True
        else:
            logEvent('Tried to launch, but got ' + str(Util.get_msg(response.body.msgtype)))
            return False

    def requestEconData(self, param_a, param_d, param_s=0, param_m=0):
        message = msg_base.ProtobufMessage(
            cstrike15_gcmessages_pb2.CMsgGCCStrike15_v2_Client2GCEconPreviewDataBlockRequest,
            csgo_base.ECSGOCMsg.k_EMsgGCCStrike15_v2_Client2GCEconPreviewDataBlockRequest)

        message.body.param_s = param_s  # SteamID
        message.body.param_a = param_a  # AssetID
        message.body.param_d = param_d
        message.body.param_m = param_m  # MarketID

        self.gc.gcSend(message)
        response = self.gc.client.wait_for_message(EMsg.ClientFromGC, timeout=5.0)
        if response == 'Timed Out':
            return 'Steam servers did not respond, your time delay is probably too small.'
        elif Util.get_msg(
                response.body.msgtype) == csgo_base.ECSGOCMsg.k_EMsgGCCStrike15_v2_Client2GCEconPreviewDataBlockResponse:
            econData = self.gc.gcFrom(response.body.payload,
                                      cstrike15_gcmessages_pb2.CMsgGCCStrike15_v2_Client2GCEconPreviewDataBlockResponse)
            return econData
        else:
            return 'Response was not of type EconPreviewDataBlockResponse'

    def exit(self):
        message = msg_base.ProtobufMessage(steammessages_clientserver_pb2.CMsgClientGamesPlayed, EMsg.ClientGamesPlayed)
        self.gc.client.connection.send_message(message)


class User(object):
    def __init__(self):
        sleep(0)
        self.username = None
        self.password = None
        self.client = SteamClient(SteamClientHandler(self))
        self.gc = SteamGC(self.client, 730)
        self.csgo = CSGO(self.gc)

    def login(self, username=None, password=None, authcode=None, two_factor_code=None):
        if username:
            self.username = username
        if password:
            self.password = password
        if authcode:
            self.client.callback.auth_code = authcode
        if two_factor_code:
            self.client.callback.two_factor_code = two_factor_code
        return self.client.initialize()

    def setState(self, state):
        message = msg_base.ProtobufMessage(steammessages_clientserver_pb2.CMsgClientChangeStatus, EMsg.ClientChangeStatus)
        message.body.persona_state = state
        self.client.connection.send_message(message)

    def disconnect(self):
        self.csgo.exit()
        self.client.disconnect()


def getfloat(paintwear):
    buf = struct.pack('i', paintwear)
    skinFloat = struct.unpack('f', buf)[0]
    return skinFloat


def getMarketItems(url, count, currency, start=0):
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://' + url

    url = url_fix(url)
    curr = CURRENCY[currency][0]
    urlextender = '/render/?query=&start=%s&count=%s&currency=%s' % (start, count, curr)

    try:
        request = requests.get(url + urlextender)
    except requests.ConnectionError:
        return 'Could not connect. Check URL and make sure you can connect to the internet.', None
    except exceptions.InvalidURL:
        return 'URL is invalid, please check your market URL.', None

    if request.status_code == 404:
        return 'Could not connect to Steam. Retry in a few minutes and check URL.', None
    if len(request.text) < 1000:
        return 'Response from Steam contains no skin data, URL is probably invalid.', None
    if request.url != url + urlextender:
        return 'Page redirected to %s, so no skins were found. Check your market URL.' % request.url, None

    data = request.text.split('"listinginfo":')[1].split(',"assets":')[0]
    try:
        data = json.loads(data, object_pairs_hook=OrderedDict)
    except ValueError:
        return 'Response from Steam contains no skin data, URL is probably invalid.', None

    # assetID => [marketID, inspect link, formatted price]
    datadic = OrderedDict()
    soldcount = 0
    for marketID in data:
        try:
            price = int(data[marketID]['converted_price']) + int(data[marketID]['converted_fee'])
            padded = "%03d" % (price,)
            price = padded[0:-2] + '.' + padded[-2:]
        except KeyError:
            price = 'SOLD'
            soldcount += 1
            continue  # Delete this line to keep SOLD ITEMS in the result
        link = data[marketID]['asset']['market_actions'][0]['link']
        assetID = data[marketID]['asset']['id']
        datadic[assetID] = [marketID, link.replace('%assetid%', assetID).replace('%listingid%', marketID), price]

    return datadic, soldcount
