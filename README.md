# Tor Requests
A wrapper for the `requests` package that proxies all traffic through Tor.

## Installation
First, you need to install Tor and add it to your `PATH`.

Then, you can install `tor_with_requests` using the following command:
```
pip install tor_with_requests
```

## How to use
You can use `tor_with_requests` directly like `requests`:
```
import tor_with_requests
response = tor_with_requests.get('https://www.example.com')
```

Alternatively, you can use a `Session` object, which will maintain the same IP address throughout the session:
```
from tor_with_requests import Session

session = Session()
print(session.get_ip()) # a new function to get the current ip address of the session
response = session.get('https://www.example.com')
```