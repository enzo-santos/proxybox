import enum


class ProxyOperation(enum.Enum):
    read = 'read'
    update = 'update'
    enable = 'enable'
    disable = 'disable'
