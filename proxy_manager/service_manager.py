import abc
import os.path
import shutil
import typing
import urllib.parse

from proxy_manager import ProxyOperation
from proxy_manager.manager import Manager


class ServiceManager(abc.ABC):
    def __init__(self, *, operation: ProxyOperation):
        self.operation = operation

    @abc.abstractmethod
    def registry(self) -> Manager:
        pass

    @abc.abstractmethod
    def environment(self) -> Manager:
        pass

    @abc.abstractmethod
    def ssh(self) -> Manager:
        pass

    def operate_proxy(self, *, uri: typing.Optional[urllib.parse.ParseResult]) -> typing.Iterable[str]:
        with self.registry() as registry:
            if self.operation == ProxyOperation.read or self.operation == ProxyOperation.update:
                is_enabled = registry['ProxyEnable']
                if is_enabled:
                    netloc = registry['ProxyServer']
                    yield netloc
                else:
                    yield None

            if self.operation != ProxyOperation.read:
                will_enable: bool
                if self.operation == ProxyOperation.update:
                    will_enable = not is_enabled
                elif self.operation == ProxyOperation.enable:
                    will_enable = True
                elif self.operation == ProxyOperation.disable:
                    will_enable = False

                # Updating registry
                if will_enable:
                    registry['ProxyEnable'] = 1
                    registry['ProxyServer'] = f'{uri.hostname}:{uri.port}'
                else:
                    registry['ProxyEnable'] = 0
                    registry.pop('ProxyServer', None)

                # Updating environment variables
                with self.environment() as environment:
                    if will_enable:
                        environment['http_proxy'] = uri._replace(scheme='http').geturl()
                        environment['https_proxy'] = uri._replace(scheme='https').geturl()
                    else:
                        environment.pop('http_proxy', None)
                        environment.pop('https_proxy', None)

                # Updating SSH
                with self.ssh() as ssh:
                    for host_name, host_data in ssh.items():
                        host_url = host_data['HostName']
                        if host_url == 'gitlab.com' or host_url.endswith('.gitlab.com'):
                            if will_enable:
                                host_data['HostName'] = 'altssh.gitlab.com'
                                host_data['Port'] = '443'
                                host_data['TCPKeepAlive'] = 'yes'

                                git_path = shutil.which('git')
                                git_dir = os.path.dirname(os.path.dirname(git_path))
                                connect_path = os.path.join(git_dir, 'mingw64', 'bin', 'connect.exe')
                                if os.path.exists(connect_path):
                                    host_data['ProxyCommand'] = f'{connect_path} ' \
                                                                f'-H {uri.username}@{uri.hostname}:{uri.port} %h %p'

                            else:
                                host_data['HostName'] = 'gitlab.com'
                                host_data.pop('Port', None)
                                host_data.pop('TCPKeepAlive', None)
                                host_data.pop('ProxyCommand', None)

                yield f'{uri.hostname}:{uri.port}' if will_enable else None
