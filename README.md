# YA-RPC
Yet-Another Light Weight RPC Framework Written in & for Python3.



## Features

* **Easy-to-Use**
* **Dependency Free**: No third-party dependencies are required.
* **Transparent**: Almost the same as calling local procedures.
* **Thread Safe**: Feel free to use the same Client object in different thread simultaneously.
* **Polling Free**: Block the thread before getting the result from the server instead of exhaustedly polling the status.



## Usage

**Server:**

```python
# import Listener
from rpc.listener import Listener

# define your own procedures
def sum(a, b):
    return a + b


def upper(string):
    return str.upper(string)


def lower(string):
    return str.lower(string)

# instantiate a Listener object
listener = Listener(ip, port, backlog)

# register your procedures
listener.register_procedure(sum)
listener.register_procedure(upper)
listener.register_procedure(lower)

# start serving, press `Ctrl+C` (maybe twice) to terminate the program
listener.listen()
```

**Client：**

```python
# import Client
from rpc.client import Client

# instantiate a Client object
client = Client(ip, port)

# RPC
client.sum(1.0, 2.0)
client.upper("hello world!")
client.lower("HELLO WORLD!")
# Using keyword arguments
client.sum(a=1.0, b=2.0)
```



## Try Something Else

1. trying to call a non-registered procedure:

   ```python
   # trying to call a non-registered procedure
   client.sin(3.14)
   ```

   ```shell
   # outcomes
   Traceback (most recent call last):
       client.sin(3.14)
   AttributeError: 'Client' object has no attribute 'sin'
   ```

2. trying to pass illegal arguments to the call:

   ```python
   # trying to pass illegal arguments to the call
   client.upper(1.0)
   ```

   ```shell
   # outcomes
   Traceback (most recent call last):
       client.upper(1.0)
     File "YA-RPC\rpc\client.py", line 94, in func
       raise ret
   TypeError: descriptor 'upper' requires a 'str' object but received a 'float'
   ```

3. trying to pass mismatched number of arguments:

   ```python
   # trying to pass mismatched number of arguments
   client.sum(1.0)
   ```

   ```shell
   # outcomes
   Traceback (most recent call last):
       client.sum(1.0)
     File "YA-RPC\rpc\client.py", line 94, in func
       raise ret
   TypeError: sum() missing 1 required positional argument: 'b'
   ```

