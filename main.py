import argparse
import os
import urllib.parse

from proxy_manager import ProxyOperation
from proxy_manager.manager import Manager, RegistryManager, EnvironmentManager, SshManager, StorageManager
from proxy_manager.service_manager import ServiceManager


class _ServiceManager(ServiceManager):
    def registry(self, operation: ProxyOperation) -> Manager:
        return RegistryManager(operation=operation)

    def environment(self) -> Manager:
        return EnvironmentManager()

    def ssh(self) -> Manager:
        return SshManager(path=os.path.expanduser('~/.ssh/config'))

    def storage(self) -> Manager:
        return StorageManager(path='.box')


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Proxy Selector')

    subparsers = parser.add_subparsers(dest='command', help='Sub-command help')

    # Create sub-command
    create_parser = subparsers.add_parser('create', help='Create a new proxy')
    create_parser.add_argument('name', type=str, help='Name of the proxy')
    create_parser.add_argument('url', type=str, help='URL of the proxy server')

    # Read sub-command
    read_parser = subparsers.add_parser('read', help='Read an existing proxy')
    read_parser.add_argument('name', type=str, help='Name of the proxy')

    # Delete sub-command
    delete_parser = subparsers.add_parser('delete', help='Delete an existing proxy')
    delete_parser.add_argument('name', type=str, help='Name of the proxy')

    # Clear sub-command
    clear_parser = subparsers.add_parser('clear', help='Clear all existing proxies')

    # Apply sub-command
    apply_parser = subparsers.add_parser('apply', help='Apply a proxy')
    apply_parser.add_argument('name', type=str, nargs='?', help='Name of the proxy (optional)')
    args = parser.parse_args()

    manager = _ServiceManager()
    match args.command:
        case 'create':
            name = args.name
            url = args.url
            manager.storage()[name] = url
        case 'read':
            name = args.name
            print(manager.storage()[name])
        case 'delete':
            name = args.name
            manager.storage().pop(name)
        case 'clear':
            manager.storage().clear()
        case 'apply':
            name = args.name
            url = manager.storage().get(name)
            if name is not None and not url:
                return
            operation = ProxyOperation.disable if name is None else ProxyOperation.enable
            for netloc in manager.operate_proxy(operation, uri=urllib.parse.urlparse(url)):
                if netloc is None:
                    print('disconnected')
                else:
                    print(f'connected with {netloc}')


if __name__ == '__main__':
    main()
