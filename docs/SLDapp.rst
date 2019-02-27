SLDapp API
===========

.. py:module:: shadowlands
.. py:class:: SLDapp


SLDapp is the class which defines a Shadowlands Dapp.

The first thing to do is to inherit from the SLDapp class, overriding the ``initialize()`` method, and do any necessary preperation.  Then, add a frame with ``add_frame()``, which will kick off the user interface.

    .. code-block:: python

        class EthPMDapp(SLDapp):
            
            def initialize(self):
                # define any instance variables that will be useful to you, such as contracts.
                self.ethpm = EthPMContract(self.node)
                # add a frame to begin the user interface
                self.add_frame(MenuFrame, height=10, width=60)


