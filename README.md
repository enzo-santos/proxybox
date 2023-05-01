# proxybox

A tool to storage and manage proxies on Windows.

## Usage

### Installing

Clone this repository:

```shell
git clone https://github.com/enzo-santos/proxybox.git
cd proxybox
```

Create a virtual environment (ignore this code block if you do not want to create one):

```shell
python -m venv venv
venv\Scripts\activate
```

Install the dependencies:

```shell
python -m pip install -r requirements.txt
```

### Using

Your proxy box will start empty. To create a new one, add a proxy to it:

```shell
> python main.py create <name> <proxy>
$ python main.py create personal https://personaluser:personalpass@10.0.0.1:8888
$ python main.py create work https://workuser:workpass@192.168.1.1:8080
``` 

Calling `create` on a name already on the box will overwrite the previous value.

If you want to read a proxy from the box, use the following syntax:

```shell
> python main.py read <name>
$ python main.py read personal
https://personaluser:personalpass@10.0.0.1:8888
$ python main.py read work
https://workuser:workpass@192.168.1.1:8080
```


To delete a proxy from the box, use the following syntax:

```shell
> python main.py delete <name>
$ python main.py delete personal
$ python main.py delete work
```

To clear your box, just use `clear`:

```shell
$ python main.py clear
```

Once your box has enough values, you can apply the proxy associated with a name:

```shell
> python main.py apply [name]
$ python main.py apply personal
$ python main.py apply work
```

To disable a proxy, just call `apply` without a name:

```shell
$ python main.py apply
```

This library handles

- the `http_proxy` and `https_proxy` environment variables (used by many command-line tools and applications to route 
  HTTP and HTTPS traffic through a proxy server.)
- the settings used by SSH when connecting to a remote server (used by
  Git, for example) - at the moment, this feature only changes the connection to GitLab
- the hostname and port into the Windows registry, removing the need of  manually altering them on Wi-Fi icon > Network 
  and internet settings > Proxy
