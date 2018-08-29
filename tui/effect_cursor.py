from asciimatics.effects import Effect
from asciimatics.screen import Screen
from random import random
import curses
from tui.debug import debug
from time import sleep

CURSOR = u"\u2588"

class Cursor(Effect):

    """
    Special effect to make bits of the specified text appear over time.  This
    text is automatically centred on the screen.
    """

    def __init__(self, screen, renderer, x, y, colour=Screen.COLOUR_GREEN, **kwargs):
        """
        :param screen: The Screen being used for the Scene.
        :param renderer: The renderer to be displayed.
        :param y: The line (y coordinate) for the start of the text.
        :param colour: The colour attribute to use for the text.

        Also see the common keyword arguments in :py:obj:`.Effect`.
        """
        super(Cursor, self).__init__(screen, **kwargs)
        self._renderer = renderer
        self._x = x
        self._y = y
        self._colour = colour
        self.line = 0
        self.char = 0
        self.blink = False

    def reset(self):
        image, colours = self._renderer.rendered_text
        self.char = 0
        self._x = 0

    def _update(self, frame_no):


        x = self._x
        y = self._y
        image, colours = self._renderer.rendered_text

        if self.char >= len(image[0]):
            sleep(0.5)


            if self.blink is True:
                self._screen.print_at(CURSOR, x, y, self._colour)
            else:
                self._screen.print_at(' ', x, y, self._colour)

            self.blink = not self.blink
            return


        #debug(self._screen._screen); import pdb; pdb.set_trace()
        self._screen.print_at(image[0][self.char], x, y, self._colour)
        self._screen.print_at(CURSOR, x+1, y, self._colour)
        # u"\u2588" '█'

        #self._screen.print_at(chr(randint(33, 126)), x, y, self._colour)
        self._x += 1
        #self._y += 1
        self.char += 1


    @property
    def stop_frame(self):
        return self._stop_frame



