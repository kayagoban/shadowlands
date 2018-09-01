from asciimatics.effects import Effect
from asciimatics.screen import Screen
from random import random
import curses
from tui.debug import debug
#from tui.effect_responder import ResponsiveEffect

class Materialize(Effect):

    DEMATERIALIZE=0
    MATERIALIZE=1

    MATERIALIZED_CHAR=1

    """
    Special effect to make bits of the specified text appear over time.  This
    text is automatically centred on the screen.
    """

    def __init__(self, screen, renderer, x, y, colour=Screen.COLOUR_GREEN, signal_step=-0.04, signal_acceleration_factor=1.2, **kwargs):
        """
        :param screen: The Screen being used for the Scene.
        :param renderer: The renderer to be displayed.
        :param y: The line (y coordinate) for the start of the text.
        :param colour: The colour attribute to use for the text.

        Also see the common keyword arguments in :py:obj:`.Effect`.
        """
        super(Materialize, self).__init__(screen, **kwargs)
        self._renderer = renderer
        self._x = x
        self._y = y
        self._colour = colour
        self._signal_strength = 1.0
        self._signal_step = signal_step
        self._signal_acceleration_factor = signal_acceleration_factor
        
    def reset(self):
        #self._signal_strength = 1.0
        #self._signal_step = -0.05
        image, colours = self._renderer.rendered_text
        line = None

    def _update(self, frame_no):
        if frame_no % 2 == 0:
            return

        y = self._y
        image, colours = self._renderer.rendered_text

        #debug(self._screen._screen); import pdb; pdb.set_trace()
        for i, line in enumerate(image):
            if self._screen.is_visible(0, y):
                # Start each line at the x we specified
                x = self._x
                for j, c in enumerate(line):
                    if random() > self._signal_strength:
                        if colours[i][j][0] is not None:
                            self._screen.print_at(c, x, y, colours[i][j][0], colours[i][j][1])
                        else:
                            self._screen.print_at(c, x, y, self._colour)
                    else:
                        self._screen.print_at(' ', x, y)
                        # print random ass character
                        #self._screen.print_at(chr(randint(33, 126)), x, y, self._colour)

                    x += 1
            y += 1

        # Tune the signal
        self._signal_strength += self._signal_step
        self._signal_step = self._signal_step * self._signal_acceleration_factor

        # If we have reached full signal, set the stop frame to 4 from now.
        if self._signal_strength < 0:
            self._stop_frame = frame_no + 4


    @property
    def stop_frame(self):
        return self._stop_frame



