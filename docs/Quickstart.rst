
Quickstart
=============

Shadowlands is a python-based platform for writing Ethereum Dapps without a web browser.

Shadowlands Dapps inherit from the ``SLDapp`` class, and make use of the ``SLFrame`` class to set up
a user interface.  Also very useful are the ``Node``, ``SLConfig`` and ``PricePoller`` classes.

To start your own Dapp, set the local dapp directory within shadowlands, and then create a
new subdirectory with the name of your dapp.  Inside, create a file called ``__init__.py`` and 
override ``SLDapp`` to begin.  See the documentation for ``SLDapp``, and also look the source code 
for existing dapps, such as the ENS Dapp, for guidance.
