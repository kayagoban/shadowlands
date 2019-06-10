Node
======

.. py:class:: Node

The :class:`Node` class provides ethereum networking functions and
other useful properties.


Obtaining the Node object
-------------------------

You do not need to instantiate the Node object.  You can get it by calling :attr:`SLDapp.node`, :attr:`SLContract.node` or :attr:`Erc20.node`.


Properties
----------

.. py:attribute:: Node.ens

Returns the :class:`Web3.ens` object.  Useful for calling ``ens.resolve(name)`` to perform a lookup  or ``ens.name(address)`` to perform reverse lookup.

.. py:attribute:: Node.best_block

Returns the highest known block.

.. py:attribute:: Node.blocks_behind

Returns the number of blocks behind, or None if synced.

.. py:attribute:: Node.eth_price 

Returns the current eth price in USD, as listed in the Maker contract oracle used by the CDP/DAI system.

.. py:attribute:: Node.network_name

Returns the uppercase network name string.  Returns a string value of the network ID if not recognized.

.. py:attribute:: Node.eth_balance

Returns the decimal ether value of the user's current address.

.. py:attribute:: Node.ens_domain

Return reverse lookup ENS domain of the user's current address, or None.

Low Level Methods
------------------

These are low level methods that do not generate any UI.


.. py:method:: Node.push(contract_function, gas_price, gas_limit=None, value=0, nonce=None)

Pushes a Tx function directly to the credstick for signing and publishing on the network.

``value`` is the integer-value of wei to send with Tx.  ``gas_price`` is an integer wei value.  You need to set ``gas_limit`` on this method.  If ``nonce`` is not set, it will be automatically calculated for the next valid nonce on the current user address.

.. py:method:: Node.send_ether(destination, amount, gas_price, nonce=None)

Requests an ether send for credstick signing and publishing on the network.

``destination`` is a string ethereum address.  ``amount`` is the ether value in decimal format.  ``gas_price`` is an integer wei value.  If ``nonce`` is not set, it will be automatically calculated for the next valid nonce on the current user address.

.. py:method:: Node.send_erc20(token, destination, amount, gas_price, nonce=None)

Requests an Erc20 send for signing and publishing on the network.  

``token`` is an :class:`Erc20` or :class:`SLContract` object which has an Erc20 compatible :func:`transfer` function.

``destination`` is an address.  ``amount`` is a human-friendly decimal amount.  ``gas_price`` is an integer wei value.  If ``nonce`` is not set, it will be automatically calculated for the next valid nonce on the current user address.


