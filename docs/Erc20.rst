Erc20 
=========

.. py:class:: Erc20

Abstract
--------

A subclass of :class:`SLContract` specialized to handle contracts
which conform to the Erc20 standard.

Integer vs. Decimal values
--------------------------

Integer values are the base denomination of a token, similar to Wei.
Decimal values are the human readable denomination of a token, similar to Ether.

You can convert using :func:`Erc20.convert_to_decimal` or :func:`Erc20.convert_to_integer`

Constructor
-----------
.. py:method:: Erc20(node, address=None)

Initialize an Erc20 by passing it the :class:`Node` object.

The Erc20 must be fed an address, but you have options for how to do this:

Usually you will pass the string keyword arg ``address`` to the constuctor, or optionally you can subclass Erc20 and assign the address to constants such as ``MAINNET``, ``ROPSTEN``, ``KOVAN``, and other etherum network names.

.. code-block:: python
        :caption: Example 1

        contract_address='0x89d24A6b4CcB1B6fAA2625fE562bDD9a23260359'
        ''' then, get the node and...'''
        token = Erc20(node, address=contract_address)



Properties
----------

.. py:attribute:: Erc20.decimal_balance

Returns the current address holder's token balance, normalized in a
human-readable Decimal.  This is like getting the balance in Ether instead of in Wei.


Methods
-------

.. py:method:: Erc20.my_balance()

Returns the current address holder's token balance, as an integer.
This is like getting the balance in Wei instead of in Ether.


.. py:method:: Erc20.totalSupply()

Returns integer value of the total supply.

.. py:method:: Erc20.allowance(owner, proxy)

Returns integer value of tokens that address ``proxy`` is allowed to access on behalf of address ``owner``. 

.. py:method:: Erc20.self_allowance(proxy)

Returns integer value of tokens that address ``proxy`` is allowed to access on behalf of the user's current address. 

.. py:method:: Erc20.symbol()

Returns string symbol of token.

.. py:method:: Erc20.decimals()

Returns integer number of decimals supported by token.

.. py:method:: Erc20.balanceOf(target)

Returns integer value of tokens owned by address ``target``.

.. py:method:: Erc20.my_balance()

Returns integer value of tokens owned by user's current address.

.. py:method:: Erc20.convert_to_decimal(amount)

Returns decimal token value of integer ``amount``

.. py:method:: Erc20.convert_to_integer(amount)

Returns integer token value of decimal ``amount``

.. py:method:: Erc20.my_balance_str(length=18)

Returns string interpretation of user's decimal token value, truncated to ``length`` characters.

Tx function generators
-----------------------

.. py:method:: Erc20.approve(proxy_address, value)

Returns Tx function that will approve ``proxy_address`` to spend integer ``value`` amount of tokens on behalf of the current user address.

.. py:method:: Erc20.approve_unlimited(proxy_address)

Returns Tx function that will approve ``proxy_address`` to spend an unlimited amount of tokens on behalf of the current user address.

.. py:method:: Erc20.transfer(target, value)

Returns Tx function that will transfer integer ``value`` amount of tokens to address ``target``





