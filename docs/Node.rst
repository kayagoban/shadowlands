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

Returns the :module:`Web3.ens` object.  Useful for calling ``ens.resolve(name)`` to perform a lookup  or ``ens.name(address)`` to perform reverse lookup.

.. py:attribute:: Node.eth_price 

Returns the current eth price in USD, as listed in the Maker contract oracle used by the CDP/DAI system.

.. py:attribute:: Node.network_name

Returns the uppercase network name string.  Returns a string value of the network ID if not recognized.

.. py:attribute:: Node.eth_balance

Returns the decimal ether value of the user's current address.

.. py:attribute:: Node.ens_domain

Return reverse lookup ENS domain of the user's current address, or None.

.. py:attribute:: Node.
.. py:attribute:: Node.
.. py:attribute:: Node.
.. py:attribute:: Node.


Methods
-------

.. py:method:: Node.
.. py:method:: Node.
.. py:method:: Node.
.. py:method:: Node.
.. py:method:: Node.
.. py:method:: Node.
.. py:method:: Node.
.. py:method:: Node.

