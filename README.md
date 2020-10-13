# AIL -feeder from JSON
Aggregate json log lines and push to AIL

This AIL feeder is a generic software to feed JSON logs lines stored in a folder to AIL.

# Installation

On a debian/ubuntu launch `./setup.sh`

# Usage

- first activate virtualenv:
`. ./venv/bin/activate`

- then use:
~~~shell
(venv) ➜  ail-feeder-jsonlogs git:(main) ✗ ./bin/jsonfeeder.py --h
usage: jsonfeeder.py [-h] [--dry]

optional arguments:
  -h, --help  show this help message and exit
  --dry       dry run - output to stdout
(venv) ➜  ail-feeder-jsonlogs git:(main) ✗ 
~~~

# Configuration
```
[ail]
url = https://127.0.0.1:7020/api/v1/import/json/item
apikey = <YOURAPIKEY>
ailfeedertype = 
# use uuidgen
uuid = 

[folder]
# basedir is the logs root folder
basedir = .
# a prefix can be prepended
prefix =
# a suffix can be appended
suffix =
# Leave datapattern empty to inspect all basedir's subfolders
datepattern =
# Set datepattern to a date pattern if you need a daily output
# an instance with datepattern = %Y%m%d on the 12/10/2020 will
# look into basedir/prefix20201012suffix
# datepattern follows 1989 C standard

# selector follows jmespath grammar
# it should follow the multi-select hash spec
# add u_ in front of keys to have these set together as keyid (this will be unique per exec)
# for instance sending only one line to AIL for several client requests on a webserver would look like that:
[selector]
selector = "{u_request: request , u_remote_ip: ip, time: time}"

[input]
encoding = utf-8
```

# JSON output format to AIL

- `source` is the name of the AIL json feeder module
- `source-uuid` is the UUID of the feeder (unique per feeder)
- `data` is the JSON data
- `data-sha256` is the SHA256 value JSON data 

## ail_feeder_jsonlogs

~~~~json
{
    "data": {
        "host": "example.com",
        "remote_ip": "127.0.0.1",
        "time": "31/Aug/2020:15:15:13 +0200"
    },
    "data-sha256": "1650da45f2480a5bb95e40b1306280157f5efd9d71fe2858d1b1879969d6d41f",
    "default-encoding": "UTF-8",
    "source": "my_ail_feeder",
    "source-uuid": "c0e2aa8a-7b41-4156-803e-ec5f364b4a1e"
}
~~~~

