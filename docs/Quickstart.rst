
Quickstart
=============

To start your own Dapp, open the dapps menu within the shadowlands application. 

.. image:: dapps-menu.png
  :width: 800
  :alt: Dapps Menu

Next, set the local dapp directory to your desired location.

.. image:: dapps-menu-change-directory.png
  :width: 800
  :alt: Change Local Dapp directory

Inside your chosen local dapp directory, create a new subdirectory with the name of your dapp.  Inside, create a file called ``__init__.py``.


Your first SLDapp
-----------------

Import ``SLDapp`` at the top of your ``__init__.py`` file in your dapp's subdirectory. We'll also import ``SLFrame`` and ``SLContract``.

    .. code-block:: python

        from shadowlands.sl_dapp import SLDapp
        from shadowlands.sl_frame import SLFrame

Create a class named ``Dapp`` that subclasses ``SLDapp``.  The class must be named ``Dapp`` in 
order for the shadowlands plugin system to detect your dapp.  Override the 
``initialize()`` method, and do any necessary preperation within.  Then, add an ``SLFrame`` subclass (which you need to provide) with ``add_frame()``.  This step begins the user interface.

    .. code-block:: python

        class Dapp(SLDapp):
            def initialize(self):
                # Define any variables that will be useful to you, such as contracts.
                # Any other setup steps go here

                # add a frame to begin the user interface
                self.add_frame(MyMenuFrame, height=10, width=60)

        class MyMenuFrame(SLFrame):
            def initialize(self):
                


