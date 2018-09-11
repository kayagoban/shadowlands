from abc import ABC, abstractmethod
from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, Button



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
        pass


    # This must return a list of Scenes
    @property
    @abstractmethod
    def scenes(self, screen):
        raise AbstractMethodError("You must override this and return a list of Scenes.  See the ENS Dapp example.")





class SLFrame(Frame):
    def __init__(self, dapp, height, width, **kwargs):
        self._dapp = dapp
        self._screen = dapp._screen

        super(SLFrame, self).__init__(self._screen,
                                      height,
                                      width,
                                      can_scroll=False,
                                      is_modal=True,
                                      **kwargs)
                                      #hover_focus=True,


        self.set_theme('shadowlands')

        self.initialize()

        #divider_layout = Layout([100])
        #self.add_layout(divider_layout)
        #divider_layout.add_widget(Divider(draw_line=True))

        layout = Layout([1, 1, 1, 1])
        self.add_layout(layout)
        layout.add_widget(Button("OK", self._ok), 0)
        layout.add_widget(Button("Cancel", self._cancel), 3)
        self.fix()


        self.fix()
 
    def add_textbox(self, name, label_text):
        layout = Layout([100])
        self.add_layout(layout)
        layout.add_widget(Text(label_text, name))
        layout.add_widget(Divider(draw_line=False))
         
            
