import collections.abc
import contextlib
import json
import os
import typing
import winreg

import sshconf

from proxy_manager import ProxyOperation

T = typing.TypeVar('T')


# noinspection PyAbstractClass
class Manager(contextlib.AbstractContextManager, typing.Generic[T], collections.abc.MutableMapping[str, T]):
    pass


class StorageManager(Manager[str]):
    def __init__(self, path = '.box'):
        self.path = path

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def _read(self):
        data: dict
        try:
            with open(self.path, encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _write(self, data):
        with open(self.path, 'w+', encoding='utf-8') as f:
            json.dump(data, f)

    def __setitem__(self, k: str, v: str) -> None:
        data = self._read()
        data[k] = v
        self._write(data)

    def __delitem__(self, k: str) -> None:
        data = self._read()
        data.pop(k)
        self._write(data)

    def __getitem__(self, k: str) -> typing.Optional[str]:
        return self._read().get(k)

    def __len__(self) -> int:
        raise len(self._read())

    def __iter__(self) -> typing.Iterator[str]:
        return iter(self._read())


class RegistryManager(Manager[typing.Union[str, int]]):
    def __init__(self, *, operation: ProxyOperation):
        access_flag: int
        if operation == ProxyOperation.read:
            access_flag = winreg.KEY_READ
        elif operation == ProxyOperation.update:
            access_flag = winreg.KEY_READ | winreg.KEY_SET_VALUE
        elif operation == ProxyOperation.enable:
            access_flag = winreg.KEY_SET_VALUE
        elif operation == ProxyOperation.disable:
            access_flag = winreg.KEY_READ | winreg.KEY_SET_VALUE
        else:
            raise RuntimeError()

        self._proxy_key: typing.Optional[int] = None
        self._access_flag: int = access_flag

    def __enter__(self):
        path = 'Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings'
        self._proxy_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, self._access_flag)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        proxy_key = self._proxy_key
        if proxy_key is None:
            return

        winreg.CloseKey(proxy_key)
        self._proxy_key = None

    def __setitem__(self, k: str, v: typing.Union[str, int]) -> None:
        proxy_key = self._proxy_key
        if proxy_key is None:
            return

        reg_type: int
        if isinstance(v, int):
            reg_type = winreg.REG_DWORD
        elif isinstance(v, str):
            reg_type = winreg.REG_SZ
        else:
            return

        winreg.SetValueEx(proxy_key, k, 0, reg_type, v)

    def __delitem__(self, k: str) -> None:
        proxy_key = self._proxy_key
        if proxy_key is None:
            return

        try:
            winreg.DeleteKeyEx(proxy_key, k)
        except FileNotFoundError:
            return

    def __getitem__(self, k: str) -> typing.Optional[typing.Union[str, int]]:
        proxy_key = self._proxy_key
        if proxy_key is None:
            return

        value, _ = winreg.QueryValueEx(proxy_key, k)
        return value

    def __len__(self) -> int:
        raise NotImplementedError()

    def __iter__(self) -> typing.Iterator[str]:
        raise NotImplementedError()


class EnvironmentManager(Manager[str]):
    def __init__(self):
        self._wrapped = os.environ

    def __setitem__(self, k: str, v: str) -> None:
        self._wrapped[k] = v

    def __delitem__(self, k: str) -> None:
        del self._wrapped[k]

    def __getitem__(self, k: str) -> str:
        return self._wrapped[k]

    def __len__(self) -> int:
        return len(self._wrapped)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __iter__(self) -> typing.Iterator[str]:
        return iter(self._wrapped)


class SshHostManager(Manager[str]):
    def __init__(self, file: sshconf.SshConfigFile, name: str):
        self._file = file
        self._name = name

    def __setitem__(self, k: str, v: str) -> None:
        return self._file.set(self._name, **{k: v})

    def __delitem__(self, k: str) -> None:
        raise NotImplementedError()

    def __getitem__(self, k: str) -> str:
        return self._file.host(self._name)[k.lower()]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __len__(self) -> int:
        return len(self._file.host(self._name))

    def __iter__(self) -> typing.Iterator[str]:
        return iter(self._file.host(self._name))


class SshManager(Manager[SshHostManager]):
    def __init__(self, path: str):
        self._config: typing.Optional[sshconf.SshConfigFile] = None
        self._path = path

    def __enter__(self):
        self._config = sshconf.read_ssh_config_file(self._path)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._config.write(os.path.expanduser('~/.ssh/config2'))

    def __setitem__(self, k: str, v: object) -> None:
        raise NotImplementedError()

    def __delitem__(self, k: str) -> None:
        return self._config.remove(k)

    def __getitem__(self, k: str) -> object:
        return SshHostManager(self._config, k)

    def __len__(self) -> int:
        return len(self._config.hosts())

    def __iter__(self) -> typing.Iterator[str]:
        return iter(self._config.hosts())
