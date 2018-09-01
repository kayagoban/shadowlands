from asciimatics.effects import Effect
from asciimatics.screen import Screen
from asciimatics.exceptions import NextScene
from asciimatics.event import KeyboardEvent
from random import random
from tui.debug import debug
from time import sleep
import logging
import threading
import curses
import sys


logging.basicConfig(filename='shadow.log', filemode='w', level=logging.INFO)

#debug(self._screen._screen); import pdb; pdb.set_trace()
class Cursor(Effect):

    """
    Special effect to make bits of the specified text appear over time.  This
    text is automatically centred on the screen.
    """

    CURSOR = u"\u2588"

    def __init__(self, screen, renderer, x, y, colour=Screen.COLOUR_GREEN, speed=1, no_blink=False, thread=False, **kwargs):
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
        self._blink_state = False
        self.current_line = None
        self._speed = speed
        self._no_blink = no_blink
        self._thread = thread
    

    def reset(self):
        #debug(self._screen._screen); import pdb; pdb.set_trace()
        image, colours = self._renderer.rendered_text
        self.char = 0
        self._x = self.origin_x
        self._y = self.origin_y
        self.image_index = 0
        #debug(self._screen._screen); import pdb; pdb.set_trace()
        #logging.info([self.char, len(image[self.image_index])])


    def render_multiple_chars(self, image):
        for i in range(self._speed):
            #logging.info('in for loop')
            #logging.info([self.char, len(image[self.image_index])])
            self._screen.print_at(image[self.image_index][self.char], self._x, self._y, self._colour)
            self._x += 1
            self.char += 1

            # Force rendering if more than one char per pass
            if self._speed > 1:
                self._screen.force_update()

            # only print the cursor if there's one more char to go
            if self.char >= len(image[self.image_index]) - 1:
                break

            self._screen.print_at(self.CURSOR, self._x, self._y, self._colour)
            # Force rendering if more than one char per pass
            if self._speed > 1:
                self._screen.force_update()


    def blink(self):
        sleep(0.5)
        if self._blink_state is True:
            self._screen.print_at(self.CURSOR, self._x, self._y, self._colour)
        else:
            self._screen.print_at(' ', self._x, self._y, self._colour)

        self._blink_state = not self._blink_state

    def wrap_if_needed(self):
        # If the nex char is going to go off the screen, wrap to next line.
        if self._x >= self._screen.width:
            self._x = self.origin_x
            self._y += 1


    def _update_thread(self, frame_no):
        
        image, colours = self._renderer.rendered_text

        # Exit if we are already at the end of the line
        if self.char >= len(image[self.image_index]):
            if not self._no_blink:
                self.blink()
            return

        self.wrap_if_needed()

        self.render_multiple_chars(image)


            

    
    def _update(self, frame_no):
        if self._thread:
            t = threading.Thread(target=self._update_thread, args=[frame_no])
            t.start()
        else:
            self._update_thread(frame_no)

    @property
    def stop_frame(self):
        return self._stop_frame


class LoadingScreenCursor(Cursor):

    #def _update(self, frame_no):
    #    if frame_no % 10  == 0:
    #        return
    #
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
        # Test 'n' to continue to main
        #elif event.key_code == 110:
        #    raise NextScene("Main")
        else:
            return None
        return event





