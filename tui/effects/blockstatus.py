from tui.effects.cursor import Cursor
from asciimatics.renderers import DynamicRenderer
from tui.debug import debug


class BlockStatusRenderer(DynamicRenderer):

    def __init__(self, _node):
        super(BlockStatusRenderer, self).__init__(1, 40)
        self.node = _node

    def _render_now(self):
        if not self.node.syncing:
            images = ['[synced: block ' + self.node.block + ']'
                     ]
        else:
            images = [ '[syncing:  ' + str(self.node.blocksBehind) + ' blocks to ' + str(self.node.syncing['highestBlock']) + ']' ]
        return images, None


# class DynamicSourceCursor
class BlockStatusCursor(Cursor):

    def __init__(self, screen, node, x, y, **kwargs):
        super(BlockStatusCursor, self).__init__(screen, BlockStatusRenderer(node), x, y, **kwargs)
        self._previous_buffer = ['']
        self._current_buffer = None

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
            self.reset()

        return self._current_buffer




    def _update(self, frame_no):
        #if frame_no % 100 == 0:
        #    self.reset()

        '''
        image, colours = self._renderer.rendered_text

        if len(self._previous_image) > len(image[self.image_index]) :


            for i in range(len(image[0])):
                if self.char < len(self._previous_image):
                    self._screen.print_at(' ', self._x, self._y, self._colour)
                    self._x += 1
                    self.char += 1
                    # only print the cursor if there's one more char to go
                    if self.char < len(self._previous_image) - 1:
                        self._screen.print_at(self.CURSOR, self._x, self._y, self._colour)


            self.reset()    


        if len(self._previous_image) != len(image[0]):
            self._previous_image = image[0]
        '''
            
        super(BlockStatusCursor, self)._update(frame_no)
        return


