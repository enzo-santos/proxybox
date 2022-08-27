import argparse
import os
import urllib.parse

from proxy_manager import ProxyOperation
from proxy_manager.manager import Manager, RegistryManager, EnvironmentManager, SshManager
from proxy_manager.service_manager import ServiceManager


class _ServiceManager(ServiceManager):
    def registry(self) -> Manager:
        return RegistryManager(operation=self.operation)

    def environment(self) -> Manager:
        return EnvironmentManager()

    def ssh(self) -> Manager:
        return SshManager(path=os.path.expanduser('~/.ssh/config'))


def main():
    preparser = argparse.ArgumentParser(add_help=False)
    preparser.add_argument(
        'action',
        action='store',
        nargs='?',
        default=ProxyOperation.read,
        type=ProxyOperation.__getitem__,
        choices=[operation for operation in ProxyOperation],
        help='indicates the action to be executed on the proxy (default: %(default)s)',
    )
    preargs, _ = preparser.parse_known_args()
    operation: ProxyOperation = preargs.action

    parser = argparse.ArgumentParser(
        description='A program that manages SESMA\'s proxy',
        parents=[preparser],
    )
    if operation == ProxyOperation.update or operation == ProxyOperation.enable:
        parser.add_argument(
            '-u', '--uri',
            action='store',
            required=True,
            type=str,
            help='indicates the URL to be used as a proxy, in format `https://username:password@hostname:port`',
        )

    args = parser.parse_args(namespace=argparse.Namespace(uri=None))
    uri: str = args.uri

    manager = _ServiceManager(operation=operation)
    for netloc in manager.operate_proxy(uri=urllib.parse.urlparse(uri)):
        if netloc is None:
            print('disconnected')
        else:
            print(f'connected with {netloc}')


if __name__ == '__main__':
    main()
