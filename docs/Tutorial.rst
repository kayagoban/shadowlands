
Tutorial
=============

To start your own Dapp, open the dapps menu by pressing 'd' or 'D'  within the shadowlands application. 

.. highlight:: python
   :linenothreshold: 5

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

For our example, let's become Trogdor the Burninator, the wingaling dragon.  
We will burninate peasants in the kingdom of peasantry.  In our case, peasants will be PSNT Erc20 tokens (visible at peasantcoin.eth)

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
		self.add_sl_frame(MyMenuFrame(self, height=5, width=40, title="Trogdooooor!"))

	class MyMenuFrame(SLFrame):
	    def initialize(self):
		self.add_divider()
		self.add_button(self.close, "Close")

The line ``self.add_frame(MyMenuFrame(self, height=5, width=40, title="Trogdooooor!"))``, referenced from ``initialize()``, will load an SLFrame instance with the listed parameters when the dapp loads.

Like SLDapp instances, SLFrame instances execute ``initialize()`` when they are created, and you must implement this abstract method.  Our SLFrame will add a one-line divider with ``self.add_divider()`` and then add a close button with ``self.add_button(self.close, "Close")``.  The first parameter to ``self.add_button`` is a function to be executed upon the button press action, in this case ``self.close()``.

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

Debugging
---------

Now, let's make a few changes.  

.. code-block:: python

	from shadowlands.sl_dapp import SLDapp
	from shadowlands.sl_frame import SLFrame
	from shadowlands.sl_contract.erc20 import Erc20
	from shadowlands.tui.debug import debug, end_debug
	import pdb

	class Dapp(SLDapp):
	    def initialize(self):
		# Define any variables that will be useful to you, such as contracts.
		# Any other setup steps go here
		debug(); pdb.set_trace()

		PEASANT_ADDRESS = '0x8B654789353b0B622667F105eAEF9E97d3C33F44'
		peasant_contract = Erc20(self.node, address=PEASANT_ADDRESS)
		self.add_sl_frame(MyMenuFrame(self, height=5, width=40, title="Trogdooooor!"))

		# add a frame to begin the user interface

	class MyMenuFrame(SLFrame):
	    def initialize(self):
		self.add_divider()
		self.add_button(self.close, "Close")

Here you can see we've set up some debugging tools with a few import 
statements.  The functions debug() and end_debug() 
will give us a way to escape from the curses library that's controlling
the screen and let pdb work.

You can also see I defined ``PEASANT_ADDRESS`` which is the ethereum 
mainnet address of a simple ERC20 contract.  We load the contract with
the ``Erc20(self.node, address=PEASANT_ADDRESS)`` constuctor.  ``self.node`` is a reference to the ``Node`` object that the Dapp object has 
access to.

The important line ``debug(); pdb.set_trace()`` is something you should
become familiar with when writing a shadowlands app.  Running pdb without
escaping from the user interface will be a maddening experience, so don't forget to run ``debug()`` before you get pdb running.

Now, when you run your dapp, you'll see:

.. image:: trogdor-debug-1.png
  :width: 800
  :alt: Debugging Trogdor

Here you can see some of the methods that the Erc20 class provides.  You can also access the underlying web3.py contract object by accessing ``peasant_contract._contract``.

To escape from the debug session and get back to your app, type ``end_debug();; continue``.  This incantation will restore control of the screen to the curses library and end the session.

Handling user input
-------------------

Let's get some user input and do something, er... useful?

.. code-block:: python

        from shadowlands.sl_dapp import SLDapp
        from shadowlands.sl_frame import SLFrame
        from shadowlands.sl_contract.erc20 import Erc20
        from decimal import Decimal
        from shadowlands.tui.debug import debug, end_debug
        import pdb

        class Dapp(SLDapp):
            def initialize(self):
                PEASANT_ADDRESS = '0x8B654789353b0B622667F105eAEF9E97d3C33F44'
                self.peasant_contract = Erc20(self.node, address=PEASANT_ADDRESS)
                self.peasants = self.peasant_contract.my_balance() / Decimal(10**18)
		self.add_sl_frame(MyMenuFrame(self, height=10, width=70, title="Trogdooooor!"))
                
        class MyMenuFrame(SLFrame):
            def initialize(self):
                self.add_label("Trogdor the wingaling dragon intends to burninate peasants.")
                self.add_label("Trogdor has {} peasants in need of burnination.".format(self.peasants_str))
                self.text_value = self.add_textbox("How many?")
                self.add_divider()
                self.add_button_row([
                    ("Burninate!", self.burninate, 0),
                    ("Close", self.close, 1)
                ])

            @property
            def peasants_str(self):
                return "{:f}".format(self.dapp.peasants)[:8]

            def burninate(self):
                try:
                    peasants_to_burninate = Decimal(self.text_value())
                except:
                    self.dapp.add_message_dialog("That number of peasants doesn't make sense.")
                    return

                if peasants_to_burninate > 100000:   
                    self.dapp.add_message_dialog("You monster! Leave some for later.")
                    return
                elif peasants_to_burninate > self.dapp.peasants:
                    self.dapp.add_message_dialog("You don't even *have* that many peasants!")
                    return
                elif peasants_to_burninate < 0.5:
                    self.dapp.add_message_dialog("This will not satisfy Trogdor.")
                    return



We've add some height and width to our SLFrame on line 13, added labels and a textbox on lines 17 - 19, and traded in our simple button for ``add_button_row()`` on line 21.  All of the widgets available to display are documented on the ``SLFrame`` page.

On line 12, we divide the number of peasantcoins by (10 ** 18) to account for the 18 decimal places of precision of this coin.

We're doing some simple input sanitization here, as well as some restrictions as to how many peasants can be burninated in one go.

Note that ``add_message_dialog()`` is a method belonging to Dapp, which is always accessible from an ``SLFrame`` instance via ``self.dapp``.


So, let's see how we did.

.. image:: trogdor-run-2.png
  :width: 800
  :alt: Running Trogdor

Below we see the result of failing the input validation.

.. image:: trogdor-validate-fail.png
  :width: 800
  :alt: Input validation fail


Transactions
------------

Let's get on to burninating some peasants.  

.. code-block:: python

        from shadowlands.sl_dapp import SLDapp
        from shadowlands.sl_frame import SLFrame
        from shadowlands.sl_contract.erc20 import Erc20
        from decimal import Decimal
        from shadowlands.tui.debug import debug, end_debug
        import pdb

        class Dapp(SLDapp):
            def initialize(self):
                PEASANT_ADDRESS = '0x8B654789353b0B622667F105eAEF9E97d3C33F44'
                self.peasant_contract = Erc20(self.node, address=PEASANT_ADDRESS)
                self.peasants = Decimal(self.peasant_contract.my_balance() / (10 ** 18))
                self.add_sl_frame(MyMenuFrame(self, height=10, width=70, title="Trogdooooor!"))

        class MyMenuFrame(SLFrame):
            def initialize(self):
                self.add_label("Trogdor the wingaling dragon intends to burninate peasants.")
                self.add_label("Trogdor has {} peasants in need of burnination.".format(self.peasants_str))
                self.text_value = self.add_textbox("How many?")
                self.add_divider()
                self.add_button_row([
                    ("Burninate!", self.burninate, 0),
                    ("Close", self.close, 1)
                ])

            @property
            def peasants_str(self):
                return "{:f}".format(self.dapp.peasants)[:8]

            def peasants_validated(self):
                try:
                    self.peasants_to_burninate = Decimal(self.text_value())
                except:
                    self.dapp.add_message_dialog("That number of peasants doesn't make sense.")
                    return False

                if self.peasants_to_burninate > 100000:   
                    self.dapp.add_message_dialog("You monster! Leave some for later.")
                    return False
                elif self.peasants_to_burninate > self.dapp.peasants:
                    self.dapp.add_message_dialog("You don't even *have* that many peasants!")
                    return False
                elif self.peasants_to_burninate < 0.5:
                    self.dapp.add_message_dialog("This will not satisfy Trogdor.")
                    return False

                return True


            def burninate(self):
                if not self.peasants_validated():
                    return

                peasantcoins_to_burninate = self.peasants_to_burninate * Decimal(10 ** 18)

                burn_fn = self.dapp.peasant_contract.transfer(
                    '0x00000000000000000000000000000000DeaDBeef', 
                    int(peasantcoins_to_burninate)
                )

                self.dapp.add_transaction_dialog(
                    burn_fn, 
                    title="Trogdor burninates the peasantcoins", 
                    gas_limit=56000
                )

                self.close()


I've refactored our input validation to the method ``peasants_validated`` on line 30.

So, the time has come for the peasants to meet their final, fiery farewell at the nostrils of
the mighty Trogdor.

Note on line 56 that ``peasant_contract.transfer()`` returns a method, which we will feed 
into ``add_transaction_dialog()`` on line 61.

Let's see how this looks in practice.

.. image:: trogdor-run-3.png
  :width: 800
  :alt: Running Trogdor

And so, we see there are a few less peasants in the kingdom of peasantry.

.. image:: trogdor-run-4.png
  :width: 800
  :alt: Running Trogdor

Subclassing Erc20 and SLContract
--------------------------------

Trogdor is distraught to discover that the peasants have not actually been burninated,
but only banished to the cave of 0xdeadbeef.  He demands true burnination.

Luckily, the PSNT contract supports burn(), although this is not a standard Erc20
function.  Let's subclass Erc20 and use some of the features of SLContract to make
our lives easier.

.. code-block:: python

	from shadowlands.sl_contract.erc20 import Erc20

	class PeasantCoin(Erc20):
	    MAINNET='0x8B654789353b0B622667F105eAEF9E97d3C33F44'
	    ABI='''
		[
			{
				"constant": true,
				"inputs": [],

		..(ABI truncated for brevity)...


		]
		'''

First we create a file called ``peasant_coin.py`` in our ``trogdor`` directory to house our subclass.

``PeasantCoin`` subclasses ``Erc20``.  The default ABI for the 
``Erc20`` subclass doesn't understand burn(), so we need to supply our own ABI.  

Subclassing ``SLContract`` (the superclass of ``Erc20``) works the same way - you can 
define MAINNET, KOVAN, and other network names that are defined by ``Node.NETWORK_DICT``, 
and set these to the deployment address of the contract.

We also can paste the ABI here. See the documentation for ``SLContract`` and ``Erc20`` to 
fully understand everything they provide.


.. code-block:: python

	from shadowlands.sl_dapp import SLDapp
	from shadowlands.sl_frame import SLFrame
	from trogdor.peasant_coin import PeasantCoin
	from decimal import Decimal
	from shadowlands.tui.debug import debug, end_debug
	import pdb

	class Dapp(SLDapp):
	    def initialize(self):
		self.peasant_contract = PeasantCoin(self.node)
		self.peasants = Decimal(self.peasant_contract.my_balance() / (10 ** 18))
		self.total_peasants =  Decimal(self.peasant_contract.totalSupply() / (10 ** 18))
		self.add_sl_frame(MyMenuFrame(self, height=12, width=70, title="Trogdooooor!"))

	class MyMenuFrame(SLFrame):
	    def initialize(self):
		self.add_label("Trogdor the wingaling dragon intends to burninate peasants.")
		self.add_label("There are {} peasants (PSNT) in the world.".format(
			self.peasant_decorator(self.dapp.total_peasants)
		))
		self.add_label("Trogdor has {} peasants in need of burnination.".format(
			self.peasant_decorator(self.dapp.peasants)
		))
		self.text_value = self.add_textbox("How many?")
		self.add_divider()
		self.add_button_row([
		    ("Burninate!", self.burninate, 0),
		    ("Close", self.close, 1)
		])

	    def peasant_decorator(self, peasants):
		return "{:f}".format(peasants)[:12]

We import ``PeasantCoin`` on line 3 and instantiate it on line 10.  We also grab the ``totalSupply()`` on line 12.  
Some refactoring into a decorator on line 31 makes things a little nicer.


.. code-block:: python

	def burninate(self):
   	    if not self.peasants_validated():
	        return

       	    peasantcoins_to_burninate = self.peasants_to_burninate * Decimal(10 ** 18)

	    burn_fn = self.dapp.peasant_contract.functions.burn(
	        int(peasantcoins_to_burninate)
	    )

	    self.dapp.add_transaction_dialog(
	        burn_fn, 
	        title="Trogdor burninates the peasantcoins", 
	        gas_limit=56000
	    )

	    self.close()

On line 7, we access the underlying function generated by web3.py with the ``functions()`` method.
Now when we burn PSNT tokens, they will be taken out of the ``totalSupply()``.

Uniswap Integration
-------------------

Uh-oh, Trogdor has run out of peasants to burninate.  What to do?

Shadowlands has native API integration with Uniswap, so let's add a button to acquire 
more PeasantCoin.


.. code-block:: python

	class MyMenuFrame(SLFrame):
	    def initialize(self):
		self.add_label("Trogdor the wingaling dragon intends to burninate peasants.")
		self.add_label("There are {} peasants (PSNT) in the world.".format(
		    self.peasant_decorator(self.dapp.total_peasants)
		))
		self.add_label("Trogdor has {} peasants.".format(
		    self.peasant_decorator(self.dapp.peasants)
		))
		self.text_value = self.add_textbox("How many?")
		self.add_divider()
		self.add_button_row([
		    ("Burninate!", self.burninate, 0),
		    ("Get More Peasants", self.get_peasants, 1),
		    ("Close", self.close, 2)
		], layout=[30, 40, 30]
		)

	    def get_peasants(self):
		self.dapp.add_uniswap_frame(self.dapp.peasant_contract.address)


.. image:: trogdor-run-5.png
  :width: 800
  :alt: Running Trogdor


.. image:: trogdor-run-7.png
  :width: 800
  :alt: Running Trogdor





The source code for the ``trogdor`` app is available on github.

Feel free to download it and replace the peasantcoin Erc20 address with the address of your
least favorite token.  Burninating them is strangely liberating.


Disclaimer
----------

No peasants were harmed during the writing of this tutorial.



