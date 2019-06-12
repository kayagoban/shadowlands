# shadowlands-core
A Python3 based, TextUI Dapp platform for Ethereum

This is the core of the shadowlands platform.

Periodically, zipped copies of this repo are put in the releases section.  Those zip files are registered with their sha256 checksums under the app.shadowlands.eth address, in the [sloader.shadowlands.eth](https://etherscan.io/address/sloader.shadowlands.eth) package management contract.

## Installation
The shadowlands installer is hosted under the ['shadowlands'](https://github.com/kayagoban/shadowlands) project.

## License
Shadowlands is free to read, use and modify as you see fit, under the MIT license.

## Contributor setup

```py
git clone git@github.com:kayagoban/shadowlands-core.git
cd shadowlands-core
python3 -m venv venv
. venv/bin/activate
pip install -U pip
pip install -r shadowlands/requirements.txt
```

### Launch

```py
python -m shadowlands
```

### Debian-specific setup

You may be missing some required system header files, getting errors like:

     hidapi/libusb/hid.c:47:10: fatal error: libusb.h: No such file or directory
     #include <libusb.h>
              ^~~~~~~~~~
    compilation terminated.
    error: command 'x86_64-linux-gnu-gcc' failed with exit status 1

Install the header files with:

```sh
sudo apt-get install libusb-1.0-0-dev libudev-dev build-essential autoconf libssl-dev xclip xsel
```
