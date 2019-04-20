from asciimatics.exceptions import NextScene, ResizeScreenError
from asciimatics.screen import Screen
from shadowlands.tui.scenes.loading import LoadingScene
from shadowlands.sl_dapp import ExitDapp, RunDapp
from shadowlands.tui.errors import ExitTuiError, PriceError
from shadowlands.tui.scenes.main import MainScene
from shadowlands.tui.debug import debug
import pdb
from shadowlands.credstick import Credstick
import sys

#debug(self._screen._screen); import pdb; pdb.set_trace()
#debug(screen._screen); import pdb; pdb.set_trace()

class Interface():
    
    def __init__(self, _eth_node, price_poller, config, preloaded_dapp=None):
        self._node = _eth_node
        self._config = config
        self._screen = None
        self._price_poller = price_poller
        self._credstick = None
        self._loading_scene = True
        self._load_dapp = preloaded_dapp
        # State change variables to handle switching between scenes
        self._credstick_removed = False
        self._credstick_inserted = False
        self.last_scene = None
        
    @property
    def credstick(self):
        return self._credstick

    @credstick.setter
    def credstick(self, credstick):
        self._credstick = credstick

    @property
    def node(self):
        return self._node

    @property
    def config(self):
        return self._config
        
    @property
    def price_poller(self):
        return self._price_poller


    def tui(self, screen):
        self._screen = screen
        scenes = []

        self.loading_scene = LoadingScene(self._screen, "LoadingScene", self)
        self.main_scene = MainScene(self._screen, "Main", self)

        scenes.append(self.loading_scene)
        scenes.append(self.main_scene)
        screen.play(scenes, stop_on_resize=True)

    def load(self):
        current_dapp = None

        while True:
            try:
                #raise RunDapp
                screen = Screen.wrapper(self.tui)
                break
            except ResizeScreenError as e:
                #debug(); import pdb; pdb.set_trace()
                # TODO make ResizeScreenError just raise NextScene
                #debug(); pdb.set_trace()
                #self.reload_scene = e.scene.name
                debug()
                print("You have discovered Shadowlands' achilles heel.\nSHADOWLANDS DOES NOT LIKE TO BE RESIZED.\nNext time try 80x24 and leave it there.\nExiting...\nJerk.")
                break
                      
            except RunDapp:
                print("switching to dapp...")
                # load dapp from wherever it is
                from dapp import Dapp
                current_dapp = Dapp(screen, self.node)         
            except ExitDapp:
                del(sys.modules['dapp'])
            except ExitTuiError:
                print("Shutting it all down...")
                break

