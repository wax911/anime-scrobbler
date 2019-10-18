# Contents Requirement

A simple json file named `credentials.json` will be required 
for plex with the following structure:

```json
{
  "transmission": {
    "host": "your_transmission_host_name",
    "port": "transmission_rpc_port_as_a_number",
    "username": "your_transmission_username",
    "password": "_your_transmission_password"
  },
  "url": "http://your_plex_server_address:32400",
  "token": "your_plex_token"
}
```

> Please note that the transmission field is optional, 
> only include it if you want to automatically add downloaded 
> torrent files to transmission via the rpc

If you don't know how to find your plex token please read instructions 
[here](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/).