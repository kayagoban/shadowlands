```
   _____ __              __              __                __
  / ___// /_  ____ _____/ /___ _      __/ /___ _____  ____/ /____
  \__ \/ __ \/ __ `/ __  / __ \ | /| / / / __ `/ __ \/ __  / ___/
 ___/ / / / / /_/ / /_/ / /_/ / |/ |/ / / /_/ / / / / /_/ (__  )
/____/_/ /_/\__,_/\__,_/\____/|__/|__/_/\__,_/_/ /_/\__,_/____/
```

[![Join the chat at https://gitter.im/shadowlands-community/Lobby](https://badges.gitter.im/shadowlands-community/Lobby.svg)](https://gitter.im/shadowlands-community/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Documentation Status](https://readthedocs.org/projects/pip/badge/?version=stable)](http://pip.pypa.io/en/stable/?badge=stable)

Shadowlands is a 100% Python, TextUI Dapp platform for ethereum, built on Python3.5+, [web3.py](https://github.com/ethereum/web3.py) and [asciimatics](https://github.com/peterbrittain/asciimatics)

### Demo

(click on the image below to see a live demo)
 [![Alt text](https://asciinema.org/a/cq1y5pfFlDVaO0qIxDSMdGSw1.svg)](https://asciinema.org/a/cq1y5pfFlDVaO0qIxDSMdGSw1) 
 
## Quickstart

#### Credstick (hardware wallet) required

Supported hardware so far: 
* Ledger Nano S
* Ledger Blue
* Trezor original
* Trezor T.

#### Full node required
If you have access to a full node over HTTP or Websockets, you can connect to it.

Otherwise you'll need to install and sync the [Parity](https://github.com/paritytech/parity-ethereum/releases) or [Geth](https://geth.ethereum.org/downloads/) Ethereum client.

#### MacOS
1. Install a modern Python3 from the official repo: [Python for MacOS](https://www.python.org/downloads/mac-osx/) 
2. The Python MacOS installer includes a folder that has a script that fixes your SSL certificates.  Run that script, and the other one that sets up your shell environment.
3. [Install homebrew](https://brew.sh).   

Then, open a terminal and...

```
$ brew tap kayagoban/shadowlands
$ brew install shadowlands
$ shadowlands
```

#### Debian-based linuxes

Use the provided .deb package [on the releases page](https://github.com/kayagoban/shadowlands/releases) 

Ubuntu 16.04 LTS will first need a modern python3 - here are instructions on how to set up python 3.6 on Ubuntu 16.04 LTS: http://ubuntuhandbook.org/index.php/2017/07/install-python-3-6-1-in-ubuntu-16-04-lts/

Then, open a terminal and...

```
$ shadowlands
```

#### Other linux distros
1. Install a modern Python3
2. run ``git clone https://github.com/kayagoban/shadowlands.git`` in a terminal
3. Install [trezor udev rules](https://github.com/LedgerHQ/udev-rules/blob/master/20-hw1.rules) and [ledger udev rules](https://github.com/LedgerHQ/udev-rules/blob/master/20-hw1.rules)
4. edit line 5 of scripts/shadowlands to point the variable ``SL_DIR`` to where the repo was cloned to.
5. run ``scripts/shadowlands`` and watch pip install fail.
6. figure out what the pip modules need and do that.
7. goto 5


# Writing your own Dapps

You can write, deploy and register your own python based dapp modules that can be loaded within shadowlands, without any HTML, CSS or Javascript.  

### Documentation

API documentation is available at [ReadTheDocs](https://shadowlands.readthedocs.io).

[Read the tutorial](https://shadowlands.readthedocs.io/en/latest/Tutorial.html).

### Existing Shadowlands Dapps

There are two existing dapps on shadowlands - the [CDP manager dapp](https://github.com/kayagoban/shadowlands_cdp_manager) at cdp.shadowlands.eth, and [Burninator](https://github.com/kayagoban/burninator) at burninator.eth, the example dapp from the tutorial.

You can run either dapp by referencing the ens name they are registered under, within the "Run network dapp" option within Shadowlands.

The source code to both projects is available on Github (linked to their names above).

### Hire me to write your dapp

If your company needs a shadowlands dapp, I can be contracted to make one for you.  Contact me at cthomas@soykaf.digital to discuss the scope of your company's project.

## Security Audit (v0.16a)

Christopher M. Hobbs of Ascia Technologies performed a security audit on Shadowlands; [here is the report.](https://github.com/kayagoban/shadowlands/blob/master/shadowlands_v0.16a_audit.md) 

## Support Shadowlands

You can support Shadowlands directly by sending Ether and other things to shadowlands.eth
