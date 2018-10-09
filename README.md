# Shadowlands

A 100% Python, TextUI Dapp platform for ethereum, built on Python3.5+, [web3.py](https://github.com/ethereum/web3.py) and [asciimatics](https://github.com/peterbrittain/asciimatics)

### A thrilling demo

 [![Alt text](https://github.com/kayagoban/shadowlands/blob/master/demo_screenshot.png?raw=true)](https://asciinema.org/a/zZeRkHwWUYk7QDOlSBdziUjeR)
 

## Quickstart

On MacOS:

```
brew tap kayagoban/shadowlands
brew install shadowlands
```

Modern debian-based linux distributions can [use the provided .deb package](https://github.com/kayagoban/shadowlands/releases/download/v0.12a/shadowlands_1_all.deb)

Ubuntu 16.04 LTS will first need a modern python3 - here are instructions on how to set up python 3.6 on Ubuntu 16.04 LTS: http://ubuntuhandbook.org/index.php/2017/07/install-python-3-6-1-in-ubuntu-16-04-lts/

## How the loading script works

What you see here is a loading script, which creates a virtual python environment in ~/.shadowlands.  The script also bootstraps the Shadowlands application from a very simple package management smart contract at [sloader.shadowlands.eth](https://etherscan.io/address/sloader.shadowlands.eth).   You can find the source code to the shadowlands app itself under [shadowlands-core project](https://github.com/kayagoban/shadowlands-core)

The script will install dependences from pip into the shadowlands python environment, and then execute the program.  Every time you run shadowlands, the newest version of the software registered to app.shadowlands.eth is downloaded and executed.  This is similar to a website, which allows rapid deployment of new features and bugfixes.  Most of the time, your cached version of shadowlands will match the sha256 checksum registered with sloader.shadowlands.  If it you don't have a cached file that matches, the new version will be retrieved and loaded.

## The exciting part

You can write, deploy and register your own python based dapp modules that can be loaded within shadowlands, without any HTML, CSS or Javascript.  My example dapp is registered in sloader.shadowlands under ens.shadowlands.  A copy of this dapp is included with the installation for you to tinker with.  

A public repo of the [ens.shadowlands app is available in the example-dapps-shadowlands project. ](https://github.com/kayagoban/example-dapps-shadowlands)

sl_dapp.eth provides the APIs that are used for writing these shadowlands dapps.

You can load the ens.shadowlands dapp by selecting the Dapps menu, choosing "Run Network Dapp", and typing ens.shadowlands as the Dapp location.  It allows you to manage auctions and manipulate your owned ENS domains.

## You're gonna need a credstick.

Shadowlands requires a credstick (which some people call a hardware wallet) to function.  All major hardware wallets are supported: Ledger Nano S, Ledger Blue, Trezor original and Trezor T.   If you have a local node, you will probably want to run the parity node with ```--no-hardware-wallets``` or your geth node with ```--no-usb``` or else the node may interfere with shadowlands communicating with your hardware.  

# This is a Proof of Concept release, not production software!

Many things need to be done and added.  Among them:

* better handling of hardware wallets that go to sleep
* tests
* play nicer with clients that also access the wallet
* a more elegant version of the text UI api
* tons of documentation
* more tests

