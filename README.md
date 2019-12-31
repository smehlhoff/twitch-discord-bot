## Quick Start

1) Rename `config-example.json` to `config.json`.

2) Setup EC2 instance

3) Install Python 3.6

```
    $ sudo add-apt-repository ppa:deadsnakes/ppa
    $ sudo apt-get update
    $ sudo apt-get install build-essential libssl-dev libffi-dev python3-dev python3.6 python3.6-dev
    $ sudo apt-get install virtualenv
```

4) Create virtual environment

```
    $ virtualenv -p python3.6 env
```

5) Install dependencies

```
    $ source env/bin/activate
    $ pip install -r requirements.txt
    $ pip install uvloop
    $ pip install -U git+https://github.com/Rapptz/discord.py@rewrite
```

6) Run bot in background

```
    $ nohup python bot.py &
```