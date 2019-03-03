SLFrame
===========

.. py:module:: shadowlands
.. py:class:: SLFrame


``SLFrame`` provides a 'window' for interacting with users in your ``SLDapp``.  Create a 
subclass of ``SLFrame`` and then add widgets to it in the ``initialize()`` method.

    .. code-block:: python
        :caption: Example

        class AskClipboardFrame(SLFrame):

            def initialize(self):
                self.add_ok_cancel_buttons(self._copy_digest, cancel_fn=self.close)

            def _copy_digest(self):
                pyperclip.copy(self.dapp.rx)
                self.dapp.rx = None
                self.close()


Properties
----------

.. py:attribute:: SLFrame.dapp

    The instance of ``SLDapp`` which the ``SLFrame`` belongs to.


Methods
-------

.. py:method:: SLFrame.add_button(fn, text, layout_distribution=[100], layout_index=0)

    Add a single button to your SLFrame.  ``fn`` is a function to run (lambdas are
    useful for this) when the button is pressed.  You can place a string within the
    button by setting ``text``.  The optional ``layout_distribution`` and ``layout_index``
    variables follow the ``asciimatics`` widget layout rules (see `asciimatics layout`_ docs for details)

        .. code-block:: python
            :caption: Example

            self.add_button(self.close, "Cancel") 
 
.. py:method:: SLFrame.add_ok_cancel_buttons(fn, cancel_fn=None, ok_text="OK")

    Add an ok and cancel pair of buttons.  `fn` will be called when the OK button is 
    pressed.  `cancel_fn` will be called when the Cancel button is pressed - by default,
    the cancel button will close the current SLFrame.  The `ok_text` string controls the
    text on the OK button.

        .. code-block:: python
            :caption: Example

            self.add_ok_cancel_buttons(self.set_owner, self.close, ok_text="Set Domain Owner")


.. py:method:: SLFrame.add_checkbox(text, on_change=None, **kwargs)

    Add a checkbox for boolean input.  A string variable ``text`` will appear alongside the checkbox.  
    You can supply a function to ``on_change`` which will be executed when the checkbox changes state.
    The function returns a method which you can call later, to retrieve the value in the checkbox.

        .. code-block:: python
            :caption: Example

            self.boxvalue = self.add_checkbox("sometext")

            # User impacts with UI
            # ...
            # And a little while later, in some other method....
            print("The value of the box was ", self.boxvalue())



.. _asciimatics layout: https://asciimatics.readthedocs.io/en/stable/widgets.html#displaying-your-ui
