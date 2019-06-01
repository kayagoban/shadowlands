
Quickstart
=============

To start your own Dapp, open the dapps menu by pressing 'd' or 'D'  within the shadowlands application. 

.. image:: dapps-menu.png
  :width: 800
  :alt: Dapps Menu

Next, set the local dapp directory to your desired location.

.. image:: dapps-menu-change-directory.png
  :width: 800
  :alt: Change Local Dapp directory

Inside your chosen local dapp directory, create a new subdirectory with the name of your dapp.  Inside, create a file called ``__init__.py``.

.. image:: make-__init__.py.png
  :width: 800
  :alt: Create __init__.py

Your first SLDapp
-----------------

Import ``SLDapp`` at the top of your ``__init__.py`` file in your dapp's subdirectory. We'll also import ``SLFrame`` and ``SLContract``.

    .. code-block:: python

        from shadowlands.sl_dapp import SLDapp
        from shadowlands.sl_frame import SLFrame
        from shadowlands.sl_contract import SLContract

Create a class named ``Dapp`` that subclasses ``SLDapp``.  The class must be named ``Dapp`` in 
order for the shadowlands plugin system to detect your dapp.  Override the 
``initialize()`` method, and do any necessary preperation within.  Then, add an ``SLFrame`` subclass (which you need to provide) with ``add_frame()``.  This step begins the user interface.

    .. code-block:: python

	from shadowlands.sl_dapp import SLDapp
	from shadowlands.sl_frame import SLFrame
	from shadowlands.sl_contract import SLContract

	class Dapp(SLDapp):
	    def initialize(self):
		# Define any variables that will be useful to you, such as contracts.
		# Any other setup steps go here

		# add a frame to begin the user interface
		self.add_frame(MyMenuFrame, height=5, width=40, title="Trogdooooor!")

	class MyMenuFrame(SLFrame):
	    def initialize(self):
		self.add_divider()
		self.add_button(self.close, "Close")

The line ``self.add_frame(MyMenuFrame, height=5, width=40, title="Trogdooooor!")``, referenced from ``initialize()``, will load an SLFrame instance with the listed parameters when the dapp loads.

SLFrame instances also execute ``initialize()`` when they are created.  Our SLFrame will add a one-line divider with ``self.add_divider()`` and then add a close button with ``self.add_button(self.close, "Close")``.  The first parameter to ``self.add_button`` is a function to be executed upon the button press action, in this case ``self.close()``.

Now, let's run our first dapp.  Open the dapps menu and choose to run a local dapp:

.. image:: dapps-run-local.png
  :width: 800
  :alt: Run local dapp menu

Now, choose your dapp from the list:

.. image:: dapps-run-dapp.png
  :width: 800
  :alt: Run dapp

And this is the output:

.. image:: trogdor-run-1.png
  :width: 800
  :alt: Running Trogdor


