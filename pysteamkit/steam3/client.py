from gevent.event import AsyncResult, Event

from pysteamkit.protobuf import steammessages_clientserver_pb2
from pysteamkit.steam_base import EMsg, EResult, EUniverse, EAccountType
from pysteamkit.steamid import SteamID
from pysteamkit.steam3 import msg_base
from pysteamkit.steam3.connection import TCPConnection
from pysteamkit.steam3.steamapps import SteamApps
from pysteamkit.util import Util

base_server_list = [('72.165.61.174', 27017), ('72.165.61.174', 27018),
                    ('72.165.61.175', 27017), ('72.165.61.175', 27018),
                    ('72.165.61.185', 27017), ('72.165.61.185', 27018),
                    ('72.165.61.187', 27017), ('72.165.61.187', 27018),
                    ('146.66.152.12', 27017), ('146.66.152.12', 27018),
                    ('209.197.29.196', 27017), ('209.197.29.197', 27018),
                    ('cm0.steampowered.com', 27017)]

class SteamClient():
    def __init__(self, callback):
        self.callback = callback
        self.listeners = []
        self.message_constructors = dict()
        self.message_events = dict()
        self.message_job_events = dict()

        self.username = None
        self.jobid = 0
        self.steam2_ticket = None
        self.session_token = None
        self.server_list = dict()
        self.account_type = None

        self.connection = TCPConnection(self)
        self.connection_event = Event()
        self.logon_event = Event()

        self.register_listener(callback)
        self.steamapps = SteamApps(self)

        self.register_message(EMsg.ClientLogOnResponse, msg_base.ProtobufMessage, steammessages_clientserver_pb2.CMsgClientLogonResponse)
        self.register_message(EMsg.ClientLoggedOff, msg_base.ProtobufMessage, steammessages_clientserver_pb2.CMsgClientLoggedOff)
        self.register_message(EMsg.ClientSessionToken, msg_base.ProtobufMessage, steammessages_clientserver_pb2.CMsgClientSessionToken)

    def initialize(self):
        self.connect(base_server_list)
        return self.callback.try_initialize_connection(self)

    def connect(self, addresses):
        self.connection_event.clear()
        self.logon_event.clear()

        for addr in addresses:
            if self.connection.connect(addr):
                self.connection_event.wait()
                return True
        return False

    def disconnect(self):
        if self.steamid:
            self.logout()

        self.connection.disconnect()

    def handle_connected(self):
        self.connection_event.set()

    def handle_disconnected(self, reason):
        self.connection_event.clear()
        self.logon_event.clear()

        # throw errors EVERYWHERE
        for k in self.message_events.keys():
            if self.message_events[k]:
                self.message_events[k].set_exception(Exception())
                self.message_events[k] = None
        for k in self.message_job_events.keys():
            if self.message_job_events[k]:
                self.message_job_events[k].set_exception(Exception())
                self.message_job_events[k] = None

        if self.callback.handle_disconnected(self, reason):
            return

        self.connection_event.set()
        self.logon_event.set()
        self.username = None
        self.jobid = 0
        self.steam2_ticket = None
        self.session_token = None

    def register_listener(self, listener):
        self.listeners.append(listener)

    def register_message(self, emsg, container, header, body=None):
        self.message_constructors[emsg] = (container, header, body)
        self.message_events[emsg] = None

    def wait_for_message(self, emsg):
        if not emsg in self.message_events:
            #print emsg, 'not registered!'
            return None

        while True:
            if emsg != EMsg.ChannelEncryptResult and emsg != EMsg.ClientLogOnResponse:
                self.logon_event.wait()

            if not self.connection.connected:
                raise Exception("Not connected, unable to send message")

            if self.message_events[emsg]:
                async_result = self.message_events[emsg]
            else:
                async_result = self.message_events[emsg] = AsyncResult()

            try:
                return async_result.get()
            except Exception:
                pass

    def wait_for_job(self, message, emsg):
        jobid = self.jobid
        self.jobid += 1
        message.header.source_jobid = jobid

        while True:
            self.logon_event.wait()

            if not self.connection.connected:
                raise Exception("Not connected, unable to send message")

            self.connection.send_message(message)
            async_result = self.message_job_events[jobid] = AsyncResult()

            try:
                return async_result.get()
            except Exception as e:
                pass

    @property
    def steamid(self):
        return self.connection.steamid

    def login_anonymous(self):
        message = msg_base.ProtobufMessage(steammessages_clientserver_pb2.CMsgClientLogon, EMsg.ClientLogon)

        message.proto_header.client_sessionid = 0
        message.proto_header.steamid = SteamID.make_from(0, 0, EUniverse.Public, EAccountType.AnonUser).steamid
        message.body.protocol_version = 65575
        message.body.client_os_type = 10
        message.body.machine_id = "OK"

        self.connection.send_message(message)

        logonResponse = self.wait_for_message(EMsg.ClientLogOnResponse)
        return logonResponse.body

    def login(self, username=None, password=None, login_key=None, auth_code=None, steamid=0, two_factor_code=None):
        self.username = username

        message = msg_base.ProtobufMessage(steammessages_clientserver_pb2.CMsgClientLogon, EMsg.ClientLogon)

        message.proto_header.client_sessionid = 0
        if steamid > 0:
            message.proto_header.steamid = steamid
        else:
            message.proto_header.steamid = SteamID.make_from(0, 0, EUniverse.Public, EAccountType.Individual).steamid
        message.body.protocol_version = 65575
        message.body.client_package_version = 1771
        message.body.client_os_type = 10
        message.body.client_language = "english"
        message.body.machine_id = "OK"

        message.body.account_name = username
        message.body.password = password
        if login_key:
            message.body.login_key = login_key
        if auth_code:
            message.body.auth_code = auth_code
        if two_factor_code:
            message.body.two_factor_code = two_factor_code

        sentryfile = self.callback.get_sentry_file(username)
        if sentryfile:
            message.body.sha_sentryfile = Util.sha1_hash(sentryfile)
            message.body.eresult_sentryfile = EResult.OK
        else:
            message.body.eresult_sentryfile = EResult.FileNotFound

        localip = self.connection.get_bound_address()
        message.body.obfustucated_private_ip = 1111

        self.connection.send_message(message)

        logonResponse = self.wait_for_message(EMsg.ClientLogOnResponse)

        if self.steamid:
            self.account_type = self.steamid.accounttype

        return logonResponse.body

    def logout(self):
        message = msg_base.ProtobufMessage(steammessages_clientserver_pb2.CMsgClientLogOff, EMsg.ClientLogOff)

        self.connection.send_message(message)
        return None


    def get_session_token(self):
        if self.session_token:
            return self.session_token

        # this also can't fit in a job because it's sent on login
        if self.account_type == EAccountType.Individual:
            self.wait_for_message(EMsg.ClientSessionToken)
            return self.session_token

        return None

    def handle_message(self, emsg_real, msg):
        emsg = Util.get_msg(emsg_real)
        #print "EMsg is", Util.lookup_enum(EMsg, emsg)
        if emsg == EMsg.ClientLogOnResponse:
            self.handle_client_logon(msg)
        elif emsg == EMsg.ClientUpdateMachineAuth:
            self.handle_update_machine_auth(msg)
        elif emsg == EMsg.ClientSessionToken:
            self.handle_session_token(msg)
        elif emsg == EMsg.ClientServerList:
            self.handle_server_list(msg)

        for listener in self.listeners:
            listener.handle_message(emsg_real, msg)

        if emsg in self.message_constructors:
            constructor = self.message_constructors[emsg]
            if constructor[2]:
                message = constructor[0](constructor[1], constructor[2])
            else:
                message = constructor[0](constructor[1])
            message.parse(msg)

            if self.message_events.get(emsg):
                self.message_events[emsg].set(message)
                self.message_events[emsg] = None
            if self.message_job_events.get(message.header.target_jobid):
                self.message_job_events[message.header.target_jobid].set(message)
                self.message_job_events[message.header.target_jobid] = None


    def handle_client_logon(self, msg):
        message = msg_base.ProtobufMessage(steammessages_clientserver_pb2.CMsgClientLogonResponse)
        message.parse(msg)

        if message.body.steam2_ticket:
            self.steam2_ticket = message.body.steam2_ticket

        self.logon_event.set()

    def handle_update_machine_auth(self, msg):
        message = msg_base.ProtobufMessage(steammessages_clientserver_pb2.CMsgClientUpdateMachineAuth)
        message.parse(msg)

        sentryfile = message.body.bytes
        hash = Util.sha1_hash(sentryfile)

        self.callback.store_sentry_file(self.username, sentryfile)

        response = msg_base.ProtobufMessage(steammessages_clientserver_pb2.CMsgClientUpdateMachineAuthResponse, EMsg.ClientUpdateMachineAuthResponse)
        response.header.target_jobid = message.header.source_jobid

        response.body.cubwrote = message.body.cubtowrite
        response.body.eresult = EResult.OK
        response.body.filename = message.body.filename
        response.body.filesize = message.body.cubtowrite
        response.body.getlasterror = 0
        response.body.offset = message.body.offset
        response.body.sha_file = hash
        response.body.otp_identifier = message.body.otp_identifier
        response.body.otp_type = message.body.otp_type

        self.connection.send_message(response)

    def handle_session_token(self, msg):
        message = msg_base.ProtobufMessage(steammessages_clientserver_pb2.CMsgClientSessionToken)
        message.parse(msg)

        self.session_token = message.body.token

    def handle_server_list(self, msg):
        message = msg_base.ProtobufMessage(steammessages_clientserver_pb2.CMsgClientServerList)
        message.parse(msg)

        for server in message.body.servers:
            if not server.server_type in self.server_list:
                self.server_list[server.server_type] = []

            self.server_list[server.server_type].append((Util.long2ip(server.server_ip), server.server_port))
