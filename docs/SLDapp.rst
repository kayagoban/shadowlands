SLDapp
===========

.. py:class:: SLDapp


Abstract
--------
:class:`SLDapp` is the class which defines a Shadowlands Dapp.  


Properties
----------

:class:`SLDapp` provides many useful properties and methods to make writing dapps easier.


.. py:attribute:: SLDapp.w3

    A web3 object as provided by the web3.py framework.
    https://web3py.readthedocs.io/en/stable/web3.main.html#web3.Web3

.. py:attribute:: SLDapp.node 

    An instance of :class:`Node`.

    .. code-block:: python

        # Find your address
        my_address = self.node.credstick.address

.. py:attribute:: SLDapp.config_key

    A string to use as a key for storing config properties.  Defaults to the name of your dapp module.

    Feel free to change this to something very unique at the top of your :func:`initialize` method.

.. py:attribute:: SLDapp.config_properties

    A persistent dictionary of properties specific to your dapp



Methods
-------

.. py:method:: SLDapp.initialize()

    An abstract callback that you must implement.  It wil fire upon the initialization of the SLDapp object.  
    Do your setup here and add SLFrames or other dialogs.

.. py:method:: SLDapp.new_block_callack()

    An optional callback that you may implement.  It will be fired when new blocks appear.

.. py:method:: SLDapp.save_config_property(property_key, value)

    Save a serializable object to the persistent data store.

.. py:method:: SLDapp.load_config_property(property_key, value)

    Load a serializable object from the persistent data store.

.. py:method:: SLDapp.add_sl_frame(sl_frame)
  
    Display a custom frame. Takes an instantiated subclass of :class:`SLFrame` as the sole argument.

.. py:method:: SLDapp.add_message_dialog(message, **kwargs)

    Display a message dialog with the string supplied by ``message``.  You may pass in kwargs 
    which apply to ``asciimatics.Frame``.

.. py:method:: SLDapp.add_transaction_dialog(tx_fn, tx_value=0, gas_limit=None, destroy_window=None, title="Sign & Send Transaction", **kwargs)

    Display a transaction dialog, which allows the user to select gas price and gives a gas cost 
    estimate.  You must pass in a transaction function to ``tx_fn`` (see example below).  You can 
    provide a ``tx_value`` Decimal value denominated in Ether if the transaction will pass Ether. 
    You may pass in an integer ``gas_limit``, but if you do not, it will be set by an attempt will 
    be made to estimate the the gas (which defaults to 1000000 if the attempt to estimate fails).  
    If there is a frame which needs to be programmatically destroyed upon the exit of the 
    transaction dialog, pass the object into ``destroy_window``.  A string ``title`` can be set.
    You may pass in kwargs which apply to ``asciimatics.Frame``.

        .. code-block:: python
            :caption: Example

            self.dapp.add_transaction_dialog(
              tx_fn=lambda: self.dapp.ens_resolver_contract.set_address(self.dapp.name, self.dapp.node.credstick.address),
              title="Set domain to current address",
              gas_limit=55000
            )

.. py:method:: SLDapp.show_wait_frame()

    Display a wait message frame, in case you have a thread doing work which will take time.
    The user will not be able to remove this frame; it needs to be programmatically removed by 
    calling ``SLDapp.hide_wait_frame()``

.. py:method:: SLDapp.hide_wait_frame()

    Remove the wait message frame.  If it is not currently displayed, this method is a no-op.

.. py:method:: SLDapp.quit()

    Destroy the SLDapp object and return to the Shadowlands main screen.

