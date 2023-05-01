import unittest
import urllib.parse
from typing import Iterator

from main import ServiceManager, Manager, ProxyOperation


class _DictManager(Manager[object]):
    def __setitem__(self, k: str, v: object) -> None:
        self.value[k] = v

    def __delitem__(self, k: str) -> None:
        del self.value[k]

    def __getitem__(self, k: str) -> object:
        return self.value[k]

    def __len__(self) -> int:
        return len(self.value)

    def __iter__(self) -> Iterator[str]:
        return iter(self.value)

    def __init__(self):
        self.value = {}

    def __repr__(self):
        return repr(self.value)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class _ServiceManager(ServiceManager):
    def __init__(self):
        self._registry = _DictManager()
        self._environment = _DictManager()
        self._ssh = _DictManager()
        self._storage = _DictManager()

    def registry(self, operation: ProxyOperation) -> _DictManager:
        return self._registry

    def environment(self) -> _DictManager:
        return self._environment

    def ssh(self) -> _DictManager:
        return self._ssh

    def storage(self) -> Manager:
        return self._storage


class Test(unittest.TestCase):
    def test_enable(self):
        manager = _ServiceManager()
        uri = urllib.parse.urlparse('https://username:password@1.2.3.4:5555')
        manager.operate_proxy(ProxyOperation.enable, uri=uri)

        self.assertEqual({
            'ProxyEnable': 1,
            'ProxyServer': '1.2.3.4:5555',
        }, manager.registry(ProxyOperation.enable).value)

        self.assertEqual({
            'http_proxy': 'http://username:password@1.2.3.4:5555',
            'https_proxy': 'https://username:password@1.2.3.4:5555'
        }, manager.environment().value)

    def test_disable(self):
        manager = _ServiceManager()
        uri = urllib.parse.urlparse('https://username:password@1.2.3.4:5555')
        manager.operate_proxy(ProxyOperation.disable, uri=uri)

        self.assertEqual({
            'ProxyEnable': 0,
        }, manager.registry(ProxyOperation.disable).value)

        self.assertEqual({}, manager.environment().value)
