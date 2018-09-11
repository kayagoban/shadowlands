from abc import ABC, abstractmethod

class AbstractMethodError(Exception):
    pass

class SLDapp(ABC):
    def __init__(self, eth_node):
        self._node = eth_node
        self._screen = None
        self.initialize()

    def tui(self, screen):
        self._screen = screen
        screen.play(self.scenes, stop_on_resize=True)

    @property
    def node(self):
        return self._node

    @abstractmethod
    def initialize(self):
        raise AbstractMethodError("You must override this method, even if it does nothing.")


    # This must return a list of Scenes
    @property
    @abstractmethod
    def scenes(self, screen):
        raise AbstractMethodError("You must override this and return a list of Scenes.  See the ENS Dapp example.")

