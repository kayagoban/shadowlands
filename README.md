# Shadowlands

A 100% Python, TextUI Dapp platform for ethereum, built on Python3.5+, [web3.py](https://github.com/ethereum/web3.py) and [asciimatics](https://github.com/peterbrittain/asciimatics)

### But why would you do that?

I like the idea of using Ethereum to its fullest potiential without ever launching a web browser.  People should be able to make dapps in Python, without needing any CSS, HTML or Javascript.  Text interfaces can be remarkably efficient and can actually create a better user experience.  I believe Shadowlands can become a rapid application development platform; a launching ground and proving ground for Dapps which may later be turned into full Web GUI experiences.

### A thrilling demo

(click on the image below to see a live demo)
 [![Alt text](https://github.com/kayagoban/shadowlands/blob/master/demo_screenshot.png?raw=true)](https://asciinema.org/a/zZeRkHwWUYk7QDOlSBdziUjeR)
 

## Quickstart

#### MacOS
1. Install a modern Python3 from the official repo: [Python for MacOS](https://www.python.org/downloads/mac-osx/) 
2. The Python MacOS installer includes a folder that has a script that fixes your SSL certificates.  MacOS hosed the certs a while ago, and if it's not fixed, pip will not work.  Run that script, and the other one that sets up your shell environment.
3. [Install homebrew](https://brew.sh).   

Then,

```
$ brew tap kayagoban/shadowlands
$ brew install shadowlands
$ shadowlands
```

#### Debian-based linuxes
Use the provided .deb package [on the releases page](https://github.com/kayagoban/shadowlands/releases) 

Ubuntu 16.04 LTS will first need a modern python3 - here are instructions on how to set up python 3.6 on Ubuntu 16.04 LTS: http://ubuntuhandbook.org/index.php/2017/07/install-python-3-6-1-in-ubuntu-16-04-lts/

## How the loading script works

What you get here is a loading script, which creates a virtual python environment in ~/.shadowlands.  The script also bootstraps the Shadowlands application from a very simple package management smart contract at [sloader.shadowlands.eth](https://etherscan.io/address/sloader.shadowlands.eth).   You can find the source code to the shadowlands app itself under [shadowlands-core project](https://github.com/kayagoban/shadowlands-core)

The script will install dependences from pip into the shadowlands python environment, and then execute the program.  Every time you run shadowlands, the newest version of the software registered to app.shadowlands.eth is downloaded and executed.  This is similar to the on-demand nature of a website, which allows rapid deployment of new features and bugfixes.  Most of the time, your cached version of shadowlands will match the sha256 checksum registered with sloader.shadowlands.  If it you don't have a cached file that matches, the new version will be retrieved and loaded.

## The exciting part

You can write, deploy and register your own python based dapp modules that can be loaded within shadowlands, without any HTML, CSS or Javascript.  My example dapp is registered in sloader.shadowlands under ens.shadowlands.  A copy of this dapp is included with the installation for you to tinker with.  

A public repo of the [ens.shadowlands app is available in the example-dapps-shadowlands project. ](https://github.com/kayagoban/example-dapps-shadowlands)

[sl_dapp.eth](https://github.com/kayagoban/shadowlands-core/blob/master/shadowlands/sl_dapp.py) provides the APIs that are used for writing these shadowlands dapps.

You can load the ens.shadowlands dapp by selecting the Dapps menu, choosing "Run Network Dapp", and typing ens.shadowlands as the Dapp location.  It allows you to manage auctions and manipulate your owned ENS domains.

Like the shadowlands app itself, the freshest version of your network dapp is loaded, and checked against its registered sha256 checksum on the sloader.shadowlands contract.

## You're gonna need a credstick.


Shadowlands requires a credstick (which some people call a hardware wallet) to function.  The following hardware has been tested: Ledger Nano S, Ledger Blue, Trezor original and Trezor T.   [note: passphrase feature is not yet supported on the Trezor]


If you have a local node, you will probably want to run the parity node with ```--no-hardware-wallets``` or your geth node with ```--no-usb``` or else the node may interfere with shadowlands communicating with your hardware.  



Why does shadowlands require a credstick?  Because it's a basic precaution that everyone needs to take, and there's no excuse not to have one - especially if you're downloading software and running it on your computer, which all of us do.

## This is a free software project

Every component of Shadowlands is freely available under the MIT license.  This is not a not-for-profit project - its only aim is to create a great new way to interact with Ethereum. 

# This is a Proof of Concept release, not production software!

Many things need to be done and added.  Among them:

* better handling of hardware wallets that go to sleep
* tests
* play nicer with clients that also access the wallet
* a more elegant version of the text UI api
* tons of documentation
* more tests

