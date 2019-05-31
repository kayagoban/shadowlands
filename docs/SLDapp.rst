SLDapp
===========

.. py:module:: shadowlands
.. py:class:: SLDapp


``SLDapp`` is the class which defines a Shadowlands Dapp.

Properties
----------

``SLDapp`` provides many useful properties and methods to make writing dapps easier.

.. py:attribute:: SLDapp.w3

    A web3 object as provided by the web3.py framework.

.. py:attribute:: SLDapp.node 

    A (hopefully, connected) instance of ``shadowlands.Node`` Ethereum Node object.

.. py:attribute:: SLDapp.config_key

    Key to use for storing config properties.  Defaults to  ``self.__module__``.
    Feel free to change this to something very unique at the top of your ``SLDapp.initialize()`` method.

.. py:attribute:: SLDapp.config_properties

    A persistent dictionary of properties specific to your dapp



Methods
-------


.. py:method:: SLDapp.save_config_property(property_key, value)

    Save a serializable object to the persistent data store specific to this dapp

.. py:method:: SLDapp.load_config_property(property_key, value)

    Save a serializable object to 


.. py:method:: SLDapp.add_frame(cls, height=None, width=None, title=None, **kwargs)
  
    Display a custom frame.  cls is the Class name of a subclass of ``SLFrame``.  
    ``height`` and ``width`` are integers (reasonable defaults if none given).  
    ``title`` is a string. You may pass in kwargs which apply to ``asciimatics.Frame``.

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

