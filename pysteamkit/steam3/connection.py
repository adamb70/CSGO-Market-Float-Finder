import binascii
import gevent
import StringIO
import struct
import traceback
import zipfile
from gevent import socket, sleep

from pysteamkit.crypto import CryptoUtil
from pysteamkit.protobuf import steammessages_base_pb2, steammessages_clientserver_pb2
from pysteamkit.steamid import SteamID
from pysteamkit.steam_base import EMsg, EUniverse, EResult
from pysteamkit.steam3 import msg_base
from pysteamkit.util import Util


class ProtocolError(Exception):
    """
    Raised when an error has occurred in the Steam protocol
    """

class SocketException(Exception):
    """
    Socket error occurred
    """

class NetEncryption():
    def __init__(self, key):
        self.key = key

    def process_incoming(self, data):
        return CryptoUtil.symmetric_decrypt(data, self.key)

    def process_outgoing(self, data):
        return CryptoUtil.symmetric_encrypt(data, self.key)

class Connection(object):
    def __init__(self, client):
        self.client = client

        self.connected = False
        self.user_abort = False

        self.netfilter = None
        self.heartbeat = None

        self.session_id = None
        self.steamid = None

        self.client.register_message(EMsg.ChannelEncryptResult, msg_base.Message, msg_base.MsgHdr, msg_base.ChannelEncryptResult)

    def cleanup(self):
        if not self.connected:
            return

        if self.heartbeat:
            self.heartbeat.kill()

        self.connected = False
        self.netfilter = None
        self.session_id = None
        self.steamid = None

    def connect(self, address):
        self.connected = False
        self.user_abort = False
        pass

    def disconnect(self):
        self.user_abort = True
        pass

    def write(self, message):
        pass

    def get_bound_address(self):
        pass

    def send_message(self, msg):
        if self.session_id:
            msg.header.session_id = self.session_id
        if self.steamid:
            msg.header.steamid = self.steamid.steamid

        msg = msg.serialize()
        if self.netfilter:
            msg = self.netfilter.process_outgoing(msg)
        self.write(msg)

    def dispatch_message(self, msg):
        emsg_real, = struct.unpack_from('<I', msg)
        emsg = Util.get_msg(emsg_real)

        if emsg == EMsg.ChannelEncryptRequest:
            gevent.spawn(self.channel_encrypt_request, msg)
        elif emsg == EMsg.ClientLogOnResponse:
            self.logon_response(msg)
        elif emsg == EMsg.Multi:
            self.split_multi_message(msg)

        self.client.handle_message(emsg_real, msg)

    def channel_encrypt_request(self, msg):
        message = msg_base.Message(msg_base.MsgHdr, msg_base.ChannelEncryptRequest)
        message.parse(msg)

        if message.body.protocol_version != 1:
            raise ProtocolError('Unexpected channel encryption protocol')

        if message.body.universe != EUniverse.Public:
            raise ProtocolError('Unexpected universe in encryption request')

        session_key = CryptoUtil.create_session_key()
        crypted_key = CryptoUtil.rsa_encrypt(session_key)
        key_crc = binascii.crc32(crypted_key) & 0xFFFFFFFF

        response = msg_base.Message(msg_base.MsgHdr, msg_base.ChannelEncryptResponse, EMsg.ChannelEncryptResponse)
        response.body.protocol_version = 1
        response.body.key_size = len(crypted_key)
        response.payload = crypted_key + struct.pack('II', key_crc, 0)

        self.send_message(response)

        encrypt_result = self.client.wait_for_message(EMsg.ChannelEncryptResult)

        if encrypt_result.body.result != EResult.OK:
            raise ProtocolError('Unable to negotiate channel encryption')

        self.netfilter = NetEncryption(session_key)
        self.client.handle_connected()

    def _heartbeat(self, time):
        while self.socket:
            sleep(time)
            message = msg_base.ProtobufMessage(steammessages_clientserver_pb2.CMsgClientHeartBeat, EMsg.ClientHeartBeat)
            self.send_message(message)

    def logon_response(self, msg):
        message = msg_base.ProtobufMessage(steammessages_clientserver_pb2.CMsgClientLogonResponse)
        message.parse(msg)

        if message.body.eresult == EResult.OK:
            self.session_id = message.proto_header.client_sessionid
            self.steamid = SteamID(message.proto_header.steamid)

            delay = message.body.out_of_game_heartbeat_seconds
            self.heartbeat = gevent.spawn(self._heartbeat, delay)

    def split_multi_message(self, msg):
        message = msg_base.ProtobufMessage(steammessages_base_pb2.CMsgMulti)
        message.parse(msg)

        payload = message.body.message_body

        if message.body.size_unzipped > 0:
            zip_buffer = StringIO.StringIO(message.body.message_body)
            with zipfile.ZipFile(zip_buffer, 'r') as zip:
                payload = zip.read('z')

        i = 0
        while i < len(payload):
            sub_size, = struct.unpack_from('<I', payload, i)
            self.dispatch_message(payload[i+4:i+4+sub_size])
            i += sub_size + 4

class TCPConnection(Connection):
    def __init__(self, client):
        super(TCPConnection, self).__init__(client)
        self.socket = None
        self.write_buffer = []
        self.read_buffer = ''
        self.net_read = None
        self.net_write = None

    def connect(self, address):
        super(TCPConnection, self).connect(address)
        self.socket = socket.socket()

        with gevent.Timeout(5, False) as timeout:
            self.socket.connect(address)
            self.net_read = gevent.spawn(self.__read_data)
            self.connected = True
            return True
        return False

    def disconnect(self):
        super(TCPConnection, self).disconnect()
        self.cleanup()

    def write(self, message):
        message = struct.pack('I4s', len(message), 'VT01') + message
        self.write_buffer.append(message)

        if not self.net_write:
            self.net_write = gevent.spawn(self.__write_data)

    def cleanup(self):
        super(TCPConnection, self).cleanup()

        self.write_buffer = []
        self.read_buffer = ''
        if self.socket:
            self.socket.close()
            self.socket = None
        if self.net_read:
            self.net_read.kill()
            self.net_read = None
        if self.net_write:
            self.net_write.kill()
            self.net_write = None

        if not self.connected:
            return

        self.client.handle_disconnected(self.user_abort)

    def __write_data(self):
        while len(self.write_buffer) > 0:
            try:
                buffer = self.write_buffer[0]
                self.socket.sendall(buffer)
            except IOError as e:
                self.net_write = None
                self.cleanup()
                return

            self.write_buffer.pop(0)

        self.net_write = None

    def __read_data(self):
        while self.socket:
            try:
                data = self.socket.recv(4096)
            except IOError as e:
                self.net_read = None
                self.cleanup()
                return

            if len(data) == 0:
                self.cleanup()
                return

            self.data_received(data)

    def data_received(self, data):
        self.read_buffer += data

        while len(self.read_buffer) >= 8:
            length, magic = struct.unpack_from('<I4s', self.read_buffer)

            if magic != 'VT01':
                raise ProtocolError('Invalid packet magic')
            if len(self.read_buffer) < length + 8:
                break

            buffer = self.read_buffer[8:length+8]
            if self.netfilter:
                buffer = self.netfilter.process_incoming(buffer)

            try:
                self.dispatch_message(buffer)
            except Exception:
                print traceback.format_exc()

            self.read_buffer = self.read_buffer[length+8:]
