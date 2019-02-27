SLDapp
===========

.. py:module:: shadowlands
.. py:class:: SLDapp


SLDapp is the class which defines a Shadowlands Dapp.

First Steps
-----------

The first thing to do is to inherit from the ``SLDapp`` class, overriding the ``initialize()`` method, and do any necessary preperation within.  Then, add an ``SLFrame`` instance with ``add_frame()``, which will kick off the user interface.

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
  
    Add a frame to the top of the stack.
