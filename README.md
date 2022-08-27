# Proxy Switch

A tool to read, switch, enable or disable a proxy on Windows.

## Usage

Reading the current proxy:

```shell
python main.py
# or
python main.py read

# If disabled: disconnected
#  If enabled: connected with 1.2.3.4:5555
```

Disabling the current proxy:

```shell
python main.py disable

# If disabled: disconnected
#  If enabled: disconnected
```

Enabling the current proxy:

```shell
python main.py enable -u https://username:password@1.2.3.4:5555

# If disabled: connected with 1.2.3.4:5555
#  If enabled: connected with 1.2.3.4:5555
```

Switching the current proxy:

```shell
python main.py update -u https://username:password@1.2.3.4:5555

# If disabled: connected with 1.2.3.4:5555
#  If enabled: disconnected
```

Updating the proxy handles

- the `http_proxy` and `https_proxy` environment variables (used by
  Python, for example)
- the settings used by SSH when connecting to a remote server (used by
  Git, for example): this feature only changes the connection to GitLab, 
  other servers such as GitHub are yet to be implemented
- the hostname and port into the registry, removing the need of
  manually altering them on Wi-Fi icon > Network and internet settings >
  Proxy
