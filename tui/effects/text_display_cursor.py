from tui.effects.cursor import Cursor

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


