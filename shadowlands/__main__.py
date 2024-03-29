#!/usr/bin/env python

import sys

from shadowlands.credstick import Credstick
from shadowlands.sl_config import SLConfig
from shadowlands.sl_node import Node
from shadowlands.tui.tui import Interface

import pdb
from shadowlands.tui.debug import debug
from shadowlands.credstick.trezor_ethdriver import TrezorEthDriver
from decimal import Decimal
from time import sleep

import os
import logging

try:
    level = os.environ['SL_DEBUG']
    if level == 'DEBUG':
        logging.basicConfig(level = logging.DEBUG, filename = "/tmp/shadowlands.log")
    elif level == 'INFO':
        logging.basicConfig(level = logging.INFO, filename = "/tmp/shadowlands.log")

except KeyError:
    pass

load_dapp = None

def main(mock_address=None, dapp=None, hdpath_base=None, hdpath_index=None):
    if mock_address:
        Credstick.mock_address = mock_address

    global load_dapp

    # Skip to hd path on detect credstick
    if hdpath_base and hdpath_index:
        Credstick.hdpath_base = hdpath_base
        Credstick.hdpath_index = hdpath_index

    if load_dapp:
       load_dapp = dapp

    # Read from config file
    sl_config = SLConfig()

    # Start network subsystem
    eth_node = Node(sl_config=sl_config)

    # create user interface 
    interface = Interface(eth_node, sl_config, preloaded_dapp=dapp)

    # Begin interface
    interface.load()

    # Shut it all down.
    if interface.credstick is not None:
        interface.credstick.close()

    print("Closing credstick poller...")
    Credstick.stop_detect_thread()

    print("Shutdown block listener")
    try:
        eth_node._block_listener.shut_down()
    except AttributeError:
        #shutdown might occur before _block_listener is defined
        pass


    print("Closing connection to ethereum node...")
    eth_node.stop_thread()

    sys.exit(0)


if __name__ == "__main__":
    # execute only if run as a script
    main()

