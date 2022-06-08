# nginx-reverse-proxy-conf-builder

```text
$ python builder.py -h
usage: builder.py [-h] [-ssl SSL] [--copy-and-link] server_name proxy_pass

positional arguments:
  server_name
  proxy_pass

options:
  -h, --help       show this help message and exit
  -ssl SSL         Absolute Path to directory where 'fullchain.pem' and 'privkey.pem' files are stored
  --copy-and-link  Copies created config to '/etc/nginx/sites-available' and creates symbolic link (ln -s) between 'sites-available' and 'sites-enabled' config file
```
