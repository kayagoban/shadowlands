class AbstractMethodError(Exception):
    pass

class SLDapp():
    def __init__(self, eth_node):
        self._node = eth_node
        self._screen = None

    def tui(self, screen):
        self._screen = screen
        screen.play(self.scenes, stop_on_resize=True)

    # This must return a list of Scenes
    @property
    def scenes(self, screen):
        raise AbstractMethodError("You must override this and return a list of Scenes.  See the ENS Dapp example.")

