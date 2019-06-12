from shadowlands.tui.effects.cursor import Cursor
from shadowlands.tui.debug import debug
import pdb


class DynamicSourceCursor(Cursor):
    def __init__(self, screen, renderer, x, y, refresh_period=None, **kwargs):
        super(DynamicSourceCursor, self).__init__(screen, renderer, x, y, **kwargs)
        self._previous_buffer = ['']
        self._current_buffer = ['']
        self._previous_colours = [()]
        self._current_colours = [()]
        self._refresh_period = refresh_period

    def need_new_buffer(self):
        return self._current_buffer == None or (self.char >= len(self._current_buffer[self.image_index]) and self._current_buffer != self._renderer.rendered_text[0])


    def get_buffer(self):
        # if current buffer is unset, grab the rendered text.
        # also, if we have already reached the end of the text,
        # go ahead and grab another buffer from the renderer.
        if self.need_new_buffer():
            image, colours = self._renderer.rendered_text
            self._previous_buffer = self._current_buffer
            self._current_buffer = image
            self._previous_colours = self._current_colours
            self._current_colours = colours
            self.reset()


        #debug(); pdb.set_trace()

        return self._current_buffer, self._current_colours


    def _update(self, frame_no):
        if not self.need_new_buffer:
            return
 
        if self._refresh_period:
            if frame_no % self._refresh_period == 0:
                self.reset()
          
        super(DynamicSourceCursor, self)._update(frame_no)

        # Now we overwrite with spaces the difference between the sizes
        # of the current and previous buffer, if the prev buffer was
        # larger.
        size_difference = len(self._previous_buffer[self.image_index]) - len(self._current_buffer[self.image_index])

        if size_difference > 0:
            #spaces = ' ' * size_difference
            for i in range(size_difference):
                self.print_space(i)
                if i < size_difference - 1:
                    self.print_cursor(i)

    def print_space(self, i):
        self._screen.print_at(' ', self._x+i, self._y, self._colour)

    def print_cursor(self, i):
        self._screen.print_at(self.CURSOR, self._x+i+1, self._y, self._colour)

 
