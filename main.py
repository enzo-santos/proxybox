# proxybox create <scope> <host> <port>
# proxybox read <scope>
# proxybox update <scope> <host> <port>
# proxybox delete <scope>
# proxybox enable <scope>
# proxybox disable [scope]
# proxybox check <scope>

# domains: Windows, npm, http[s]_proxy

import re
import logging
import argparse

import appdirs

DIRS = appdirs.AppDirs('proxybox', 'EnzoSantos')

HOST_REGEXP = re.compile(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')

def check_host(host: str) -> None:
    if HOST_REGEXP.match(host):
        return

    logging.error(f'Invalid host: {host}')
    exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(prog='proxybox')
    subparsers = parser.add_subparsers(required=True, dest='command')

    create_subparser = subparsers.add_parser('create')
    create_subparser.add_argument('scope')
    create_subparser.add_argument('--host', required=True)
    create_subparser.add_argument('--port', required=True, type=int)
    create_subparser.add_argument('--force', action='store_true')

    read_subparser = subparsers.add_parser('read')
    read_subparser.add_argument('scope')
    
    update_subparser = subparsers.add_parser('update')
    update_subparser.add_argument('scope')
    update_subparser.add_argument('--host', required=True)
    update_subparser.add_argument('--port', required=True, type=int)

    delete_subparser = subparsers.add_parser('delete')
    delete_subparser.add_argument('scope')

    enable_subparser = subparsers.add_parser('enable')
    enable_subparser.add_argument('scope')

    disable_subparser = subparsers.add_parser('disable')
    disable_subparser.add_argument('scope', nargs='?')

    check_subparser = subparsers.add_parser('check')
    check_subparser.add_argument('scope')

    namespace = parser.parse_args()
    match namespace.command:
        case 'create':

            print('a')

        case 'read':
            print('a')

        case 'update':
            print('a')


if __name__ == '__main__':
    main()