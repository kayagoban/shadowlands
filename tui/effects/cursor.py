from asciimatics.effects import Effect
from asciimatics.screen import Screen
from asciimatics.exceptions import NextScene
from asciimatics.event import KeyboardEvent
from random import random
from tui.debug import debug
from time import sleep
import curses
import sys

CURSOR = u"\u2588"

#debug(self._screen._screen); import pdb; pdb.set_trace()
class Cursor(Effect):

    """
    Special effect to make bits of the specified text appear over time.  This
    text is automatically centred on the screen.
    """

    def __init__(self, screen, renderer, x, y, colour=Screen.COLOUR_GREEN, speed=1, no_blink=False, **kwargs):
        """
        :param screen: The Screen being used for the Scene.
        :param renderer: The renderer to be displayed.
        :param y: The line (y coordinate) for the start of the text.
        :param colour: The colour attribute to use for the text.

        Also see the common keyword arguments in :py:obj:`.Effect`.
        """
        #debug(screen._screen); import pdb; pdb.set_trace()
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
        self._speed = speed
        self._no_blink = no_blink
    

    def reset(self):
        #debug(self._screen._screen); import pdb; pdb.set_trace()
        image, colours = self._renderer.rendered_text
        self.char = 0
        self._x = self.origin_x
        self._y = self.origin_y
        self.image_index = 0

    def _update(self, frame_no):
#        if frame_no % 40 == 0:
            #debug(self._screen._screen); import pdb; pdb.set_trace()
        
        image, colours = self._renderer.rendered_text

        if not self._no_blink:
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

        for i in range(self._speed):
            # If rendering more than one char per pass, we have to force update.
            if self._speed > 1:
                self._screen.force_update()

            # Stop if we came to the end of the line.
            if self.char < len(image[self.image_index]):
                self._screen.print_at(image[self.image_index][self.char], self._x, self._y, self._colour)
                self._x += 1
                self.char += 1
                # only print the cursor if there's one more char to go
                if self.char < len(image[self.image_index]) - 1:
                    self._screen.print_at(CURSOR, self._x, self._y, self._colour)

    @property
    def stop_frame(self):
        return self._stop_frame


class LoadingScreenCursor(Cursor):

    #def _update(self, frame_no):
    #    if frame_no % 2 == 0:
    #        return
    #    super(LoadingScreenCursor, self)._update(frame_no)
        #debug(self._screen._screen); import pdb; pdb.set_trace()
 
    def process_event(self, event):

        if type(event) != KeyboardEvent:
            return None

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





