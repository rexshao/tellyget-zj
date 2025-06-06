import re
import requests
import socket
import time
from requests_toolbelt.adapters import socket_options
from urllib.parse import urlunparse, urlparse

from tellyget.utils.authenticator import Authenticator


class Auth:
    def __init__(self, args):
        self.args = args
        self.session = None
        self.base_url = ''
        self.token = ''
        self.stbid = ''

    def authenticate(self):
        self.session = self.get_session()
        self.base_url = self.get_base_url()
        print('base_url: ' + self.base_url)
        self.login()

    def get_session(self):
        session = requests.Session()
        if self.args.interface is not None:
            options = [(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, self.args.interface.encode())]
            adapter = socket_options.SocketOptionsAdapter(socket_options=options)
            session.mount("http://", adapter)
        session.headers = {
            'User-Agent': 'webkit;Resolution(PAL,720P,1080P)',
            'X-Requested-With': 'com.android.smart.terminal.iptv',
        }
        return session

    def get_base_url(self):
        params = {'UserID': self.args.user, 'Action': 'Login'}
        for i in range(3):
            try:
                response = self.session.get(self.args.authurl, params=params, allow_redirects=False)
                url = response.headers.get('Location')
                # noinspection PyProtectedMember
                return urlunparse(urlparse(url)._replace(path='', query=''))
            except Exception:
                time.sleep(3)

    def login(self):
        token = self.get_encrypt_token()
        authenticator = Authenticator(self.args.passwd).build(token, self.args.user, self.args.imei,
                                                              self.args.address, self.args.mac)
        params = {
            'UserID': self.args.user,
            'Lang': '1',
            'SupportHD': '1',
            'NetUserID': '',
            'Authenticator': authenticator,
            'STBType': self.args.model,
            'STBVersion': self.args.soft_version,
            'conntype': '',
            'STBID': self.args.imei,
            'templateName': '',
            'areaId': '',
            'userToken': token,
            'userGroupId': '',
            'productPackageId': '',
            'mac': self.args.mac,
            'UserField': '',
            'SoftwareVersion': self.args.soft_version,
            'IsSmartStb': '0',
            'desktopId': '2',
            'stbmaker': '',
            'VIP': '',
        }
        for i in range(5):
            try:
                response = self.session.post(self.base_url + '/EPG/jsp/ValidAuthenticationHWCTC.jsp', params=params)
                # match = re.search(r'Authentication.CTCSetConfig(\'SessionID\',\'([^\'+]))\')', response.text)

                re_token = re.search(r'UserToken\" value\=\"([^"]+?)\".+?stbid\" value\=\"([^"].+?)\"', res.text, re.DOTALL)
                self.token = match.group(1)
                self.stbid = match.group(2)
                return
            except Exception:
                time.sleep(3)

    def get_encrypt_token(self):
        for i in range(5):
            try:
                params = {
                    'VIP': '',
                    'UserID': self.args.user,
                }
                response = self.session.post(f'{self.base_url}/EPG/jsp/authLoginHWCTC.jsp?UserID={self.args.user}&SampleId=',
                                             params=params)
                match = re.search(r'var EncryptToken = "([^"]*)"', response.text)

                return match.group(1)
            except Exception:
                time.sleep(3)
