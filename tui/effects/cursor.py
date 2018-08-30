from asciimatics.effects import Effect
from asciimatics.screen import Screen
from asciimatics.exceptions import NextScene
from random import random
import curses
from tui.debug import debug
from time import sleep
import sys

CURSOR = u"\u2588"

#debug(self._screen._screen); import pdb; pdb.set_trace()
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
        self.origin_x = x
        self._y = y
        self.origin_y = y
        self._colour = colour
        self.line = 0
        self.char = 0
        self.blink = False
        self.current_line = None


    def reset(self):
        image, colours = self._renderer.rendered_text
        self.char = 0
        self._x = self.origin_x
        self._y = self.origin_y
        self.image_index = 0

    def _update(self, frame_no):
        image, colours = self._renderer.rendered_text
        if self.char >= len(image[self.image_index]):
            sleep(0.5)
            if self.blink is True:
                self._screen.print_at(CURSOR, self._x, self._y, self._colour)
            else:
                self._screen.print_at(' ', self._x, self._y, self._colour)

            self.blink = not self.blink
            return

        # If the nex char is going to go off the screen, wrap to next line.
        if self._x >= self._screen.width:
            self._x = self.origin_x
            self._y += 1

        #debug(self._screen._screen); import pdb; pdb.set_trace()

        self._screen.print_at(image[self.image_index][self.char], self._x, self._y, self._colour)
        self._screen.print_at(CURSOR, self._x+1, self._y, self._colour)
        # u"\u2588" '█'

        #self._screen.print_at(chr(randint(33, 126)), x, y, self._colour)
        self._x += 1
        #self._y += 1
        self.char += 1

    @property
    def stop_frame(self):
        return self._stop_frame



class LoadingScreenCursor(Cursor):
    def process_event(self, event):
        # if user just hits enter, give them some extra info

        #debug(self._screen._screen); import pdb; pdb.set_trace()
        if event.key_code == 10:
            # blank the cursor if it's there.
            image, colours = self._renderer.rendered_text
            if len(image) == (self.image_index + 1):
                sys.exit(0)
            self._screen.print_at(' ', self._x, self._y, self._colour)

            # move 2 lines down and prepare to render the next line of text
            self.image_index += 1
            self._x = self.origin_x
            self._y += 2
            self.char = 0
            return None

        elif event.key_code == 110:
            raise NextScene("MainMenu")
        else:
            return None
        return event



