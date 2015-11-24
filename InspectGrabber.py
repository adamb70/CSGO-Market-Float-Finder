# encoding: utf-8
from ctypes import *
from ctypes.wintypes import *
import psutil
from bs4 import BeautifulSoup
import requests
from requests import exceptions
import json
from collections import OrderedDict


class MODULEENTRY32(Structure):
    _fields_ = [( 'dwSize', DWORD),
                ( 'th32ModuleID', DWORD),
                ( 'th32ProcessID', DWORD),
                ( 'GlblcntUsage', DWORD),
                ( 'ProccntUsage', DWORD),
                ( 'modBaseAddr', POINTER(BYTE)),
                ( 'modBaseSize', DWORD),
                ( 'hModule', HMODULE),
                ( 'szModule', c_char * 256),
                ( 'szExePath', c_char * 260)]


CreateToolhelp32Snapshot = windll.kernel32.CreateToolhelp32Snapshot
Module32First = windll.kernel32.Module32First
Module32Next = windll.kernel32.Module32Next
CloseHandle = windll.kernel32.CloseHandle
TH32CS_SNAPMODULE = 0x00000008
TH32CS_SNAPMODULE32 = 0x00000010



def getpid(processname):
    for proc in psutil.process_iter():
        if str(processname) in str(proc.name):
            return proc.pid


def GetModuleByName(name, PID):
    snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE32 | TH32CS_SNAPMODULE, PID)

    entry = MODULEENTRY32()
    entry.dwSize = sizeof(MODULEENTRY32)

    if Module32First(snapshot, byref(entry)):
            while Module32Next(snapshot, byref(entry)):
                if entry.szModule == name:
                    CloseHandle(snapshot)
                    return hex(addressof(entry.modBaseAddr.contents))
    CloseHandle(snapshot)
    return None


def read_process_memory(pid, address, type=INT):
    OpenProcess = windll.kernel32.OpenProcess
    ReadProcessMemory = windll.kernel32.ReadProcessMemory
    CloseHandle = windll.kernel32.CloseHandle

    PROCESS_VM_READ = 0x0010
    buffer = c_char_p(b"The data goes here")

    if type == FLOAT:
        val = c_float()
    else:
        val = c_int()

    bufferSize = sizeof(c_uint())
    bytesRead = c_ulong(0)

    processHandle = OpenProcess(PROCESS_VM_READ, False, pid)
    if ReadProcessMemory(processHandle, address, buffer, bufferSize, byref(bytesRead)):
        memmove(byref(val), buffer, sizeof(val))
        CloseHandle(processHandle)
        return val.value
    else:
        CloseHandle(processHandle)
        return None


def getFloat(pid, dllBase, initialoffset, offsets):
    baseAddr = hex(int(dllBase.rstrip('L'), 16) + initialoffset)
    pointerVal = read_process_memory(pid, int(baseAddr, 16))

    for i in offsets[0:-1]:
        temp = pointerVal + int(i)
        pointerVal = read_process_memory(pid, temp)

    temp = pointerVal + int(offsets[-1])
    return read_process_memory(pid, temp, type=FLOAT)


def getMarketItems(url, count, currency, start=0):
    if not url.startswith('http://'):
        url = 'http://' + url

    if currency == 'GBP':
        curr = 2
    elif currency == 'RUB':
        curr = 5
    elif currency == 'CAD':
        curr = 20
    elif currency == 'EUR':
        curr = 3
    elif currency == 'BRL':
        curr = 7
    else:
        curr = 1   # USD

    urlextender = '/render/?query=&start=%s&count=%s&currency=%s' % (start, count, curr)
    try:
        request = requests.get(url+urlextender)
    except requests.ConnectionError:
        return 'Could not connect. Check URL and make sure you can connect to the internet.', None
    except exceptions.InvalidURL:
        return 'URL is invalid, please check your market URL.', None

    if request.status_code == 404:
        return 'Could not connect to Steam. Retry in a few minutes and check URL.', None
    if len(request.text) < 1000:
        return 'Response from Steam contains no skin data, URL is probably invalid.', None
    if request.url != url+urlextender:
        return 'Page redirected to %s, so no skins were found. Check your market URL.' % request.url, None

    data = request.text.split('"listinginfo":')[1].split(',"assets":')[0]
    try:
        data = json.loads(data, object_pairs_hook=OrderedDict)
    except ValueError:
        return 'Response from Steam contains no skin data, URL is probably invalid.', None

    datadic = OrderedDict()
    soldcount = 0
    for marketID in data:
        try:
            price = int(data[marketID]['converted_price'])+int(data[marketID]['converted_fee'])
            padded = "%03d" % (price,)
            price = padded[0:-2] + '.' + padded[-2:]
        except KeyError:
            price = 'SOLD'
            soldcount += 1
            continue   # Delete this line to keep SOLD ITEMS in the result
        link = data[marketID]['asset']['market_actions'][0]['link']
        assetID = data[marketID]['asset']['id']
        datadic[assetID] = [marketID, link.replace('%assetid%', assetID).replace('%listingid%', marketID), price]

    return datadic, soldcount


PID = getpid('csgo.exe')

baseHex = GetModuleByName('studiorender.dll', PID)


print getFloat(PID, baseHex, initialoffset=0x00097C38, offsets=[0xC, 0x278, 0x0, 0x14])
#getMarketItems('http://steamcommunity.com/market/listings/730/MAG-7%20%7C%20Heat%20%28Field-Tested%29', 100, 'GBP')