from requests import Session as _Session
from socket import socket, AF_INET, SOCK_STREAM
from subprocess import Popen, DEVNULL
from os import mkdir
from os.path import join, exists
from shutil import which, rmtree
from ipaddress import ip_address as ip_address_parse


# settings
INSTANCES_FOLDER = 'instances'


# tor exception list
class TorNotInPathError(Exception): pass


# tor session object
class Session(_Session):

    # create a session
    def __init__(self, tor_path:str|None=None, *args, **kwargs):

        # init the tor session
        self._tor_process = None
        self._tor_path = tor_path

        # check if tor is in the PATH
        if self._tor_path is None:
            self._tor_path = which('tor')
            if self._tor_path is None:
                raise TorNotInPathError
        
        # configure the tor proxy
        self._tor_port = self._select_tor_port()
        self._create_folder(INSTANCES_FOLDER)
        self._tor_data_path = join(INSTANCES_FOLDER, f"instance_{self._tor_port}")
        self._create_folder(self._tor_data_path)
            
        # start the tor proxy
        command = [self._tor_path, '--SocksPort', str(self._tor_port), '--DataDirectory', self._tor_data_path]
        self._tor_process = Popen(command, stdout=DEVNULL, stderr=DEVNULL)

        # save the proxy infos
        proxies = {
            'http': f'socks5h://127.0.0.1:{self._tor_port}',
            'https': f'socks5h://127.0.0.1:{self._tor_port}',
        }
        self._tor_proxies = proxies if self._tor_port is not None else None

        # init the requests session
        super().__init__(*args, **kwargs)

    # delete a session
    def __del__(self):
        if self._tor_process:
            self._tor_process.kill()
        self._delete_folder(self._tor_data_path)
    
    # select a free port
    def _select_tor_port(self):
        with socket(AF_INET, SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]
        return None

    # create a folder
    def _create_folder(self, folder_name):
        if exists(folder_name) == False:
            mkdir(folder_name)

    # delete a folder
    def _delete_folder(self, folder_name):
        if exists(folder_name) == True:
            rmtree(folder_name)
    
    # get the ip address of the session
    def get_ip(self):
        response = self.get("https://check.torproject.org/api/ip")
        if response.status_code != 200:
            return self._get_ip_from_mademoe()
        ip_address = response.json()['IP']
        if self._is_valid_ip(ip_address) == False:
            return self._get_ip_from_mademoe()
        return ip_address
    
    # get the ip address from an other source
    def _get_ip_from_mademoe(self):
        response = self.get("http://ip.mademoe.com/ip")
        if response.status_code != 200:
            return None
        ip_address = response.text.strip()
        if self._is_valid_ip(ip_address) == False:
            return None
        return ip_address
    
    # check if an ip address is valid
    def _is_valid_ip(self, ip_address):
        try:
            ip_address_parse(ip_address)
        except ValueError:
            return False
        return True

    # send a GET request
    def get(self, *args, **kwargs):
        return super().get(proxies=self._tor_proxies, *args, **kwargs)

    # send a POST request
    def post(self, *args, **kwargs):
        return super().post(proxies=self._tor_proxies, *args, **kwargs)

    # send a PUT request
    def put(self, *args, **kwargs):
        return super().put(proxies=self._tor_proxies, *args, **kwargs)

    # send a PATCH request
    def patch(self, *args, **kwargs):
        return super().patch(proxies=self._tor_proxies, *args, **kwargs)

    # send a HEAD request
    def head(self, *args, **kwargs):
        return super().head(proxies=self._tor_proxies, *args, **kwargs)

    # send a DELETE request
    def delete(self, *args, **kwargs):
        return super().delete(proxies=self._tor_proxies, *args, **kwargs)

    # send a OPTIONS request
    def options(self, *args, **kwargs):
        return super().options(proxies=self._tor_proxies, *args, **kwargs)
    

# GET method
def get(*args, **kwargs):
    Session().get(*args, **kwargs)

# POST method
def post(*args, **kwargs):
    Session().post(*args, **kwargs)

# PUT method
def put(*args, **kwargs):
    Session().put(*args, **kwargs)

# PATCH method
def patch(*args, **kwargs):
    Session().patch(*args, **kwargs)

# HEAD method
def head(*args, **kwargs):
    Session().head(*args, **kwargs)

# DELETE method
def delete(*args, **kwargs):
    Session().delete(*args, **kwargs)

# OPTIONS method
def options(*args, **kwargs):
    Session().options(*args, **kwargs)

