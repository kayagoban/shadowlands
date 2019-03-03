SLDapp
===========

.. py:module:: shadowlands
.. py:class:: SLDapp


SLDapp is the class which defines a Shadowlands Dapp.

First Steps
-----------

First, subclass ``SLDapp``, overriding the ``initialize()`` method, and do any necessary 
preperation within.  Then, add an ``SLFrame`` with ``add_frame()``, which will 
begin the user interface.

    .. code-block:: python

        class MySLDapp(SLDapp):
            
            def initialize(self):
                # define any instance variables that will be useful to you, such as contracts.
                self.my_contract = MyContract(self.node)

                # add a frame to begin the user interface
                self.add_frame(MenuFrame, height=10, width=60)

Properties
----------

.. py:attribute:: SLDapp.node 

    A (hopefully, connected) instance of ``shadowlands.Node`` Ethereum Node object.

.. py:attribute:: SLDapp.config

    The ``shadowlands.SLConfig`` object to access settings.

.. py:attribute:: SLDapp.price_poller

    The ``shadowlands.PricePoller`` object with current price information.


Methods
-------

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

