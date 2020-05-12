from asciimatics.widgets import Frame, Layout, Text, Button, CheckBox, Divider, ListBox, RadioButtons, Label
import os
from shadowlands.tui.effects.text_request_dialog import TextRequestDialog
from shadowlands.tui.effects.message_dialog import MessageDialog
from asciimatics.exceptions import NextScene

from web3.exceptions import BadFunctionCallOutput, StaleBlockchain
from websockets.exceptions import InvalidStatusCode, ConnectionClosed

class NetworkOptions(Frame):
    def __init__(self, screen, interface):
        super(NetworkOptions, self).__init__(screen, 8, 26, y=2, has_shadow=True, is_modal=True, name="networkopts", title="Network Options", can_scroll=False)
        self.set_theme('shadowlands')
        self._interface = interface

        #debug(); pdb.set_trace()
    
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        #layout.add_widget(Divider(draw_line=False))

        self._node = self._interface.node

        options = [
            ('Local node', 'connect_w3_local'), 
            ('Infura', 'connect_w3_infura'),
            #('Public infura', 'connect_w3_public_infura'),
            ('Custom http', 'connect_w3_custom_http'), 
            ('Custom websocket', 'connect_w3_custom_websocket'),
            ('Custom ipc', 'connect_w3_custom_ipc'),
            #('Custom Infura API Key', 'connect_w3_custom_infura'),
        ]
        listbox = ListBox(4, options, on_select=self._ok, name='netpicker')

        # Set listbox to match stored options
        for i, option in enumerate(options):
            if option[1] == self._interface._config.default_method:
                listbox._value = option[1]
                listbox._selection = i

        layout.add_widget(listbox)

        layout2 = Layout([1, 1])
        self.add_layout(layout2)

        layout2.add_widget(Button("Cancel", self._cancel))
        #layout2.add_widget(Button("Connect", self._ok), 0)
        self.fix()

    def _ok(self):
        network_option = self.find_widget('netpicker')
        connect_fn = network_option._value

        try:
            os.environ['WEB3_INFURA_API_KEY']
            no_infura_key = False
        except KeyError:
            no_infura_key = True 

        if connect_fn == 'connect_w3_custom_http':
            self._prompt_custom_http_uri()
        elif connect_fn == 'connect_w3_custom_ipc':
            self._prompt_custom_ipc_path()
        elif connect_fn == 'connect_w3_custom_websocket':
            self._prompt_custom_websocket_uri()
        elif connect_fn == 'connect_w3_custom_infura' and no_infura_key:
            self._scene.add_effect( MessageDialog(self._screen, "Set WEB3_INFURA_API_KEY in your ENV and restart.", width=60, destroy_window=self))
        else:
            connected = self._attempt_connection(connect_fn)

            if connected:
                connect_str = "{} connected via {}".format(self._interface.node.network_name, self._interface.node.connection_type)
                self._scene.add_effect( MessageDialog(self._screen, connect_str, destroy_window=self, width=(len(connect_str)+6) ) )
            else:
                self._scene.add_effect( MessageDialog(self._screen, "Connection failure", destroy_window=self))

    def _attempt_connection(self, fn_name, arg=None):
        fn = self._interface.node.__getattribute__(fn_name)
        self._interface.node.thread_shutdown = True
        self._interface.node.heartbeat_thread.join()
        self._interface.node.thread_shutdown = False
        try:
            #debug(); pdb.set_trace()
            if arg:
                return fn(arg)
            else:
                return fn()
        except StaleBlockchain:
            self._scene.add_effect( MessageDialog(self._screen, "Stale blockchain on selected Node"))
            return
        #except (AttributeError, InvalidStatusCode, ConnectionClosed, TimeoutError, OSError) as e: #Timeout
        #    self._scene.add_effect( MessageDialog(self._screen, "Could not connect to node ({})".format(str(e.__class__))))
        #    return
 
        self._interface.node.start_heartbeat_thread()


    def _continue_function(self, text, calling_frame):
        network_option = self.find_widget('netpicker')
        connect_fn = network_option._value
        try:
            connected = self._attempt_connection(connect_fn, arg=text)
        except StaleBlockchain:
            self._scene.add_effect( MessageDialog(self._screen, "Stale blockchain on selected node", destroy_window=calling_frame))
            return

        if connected:
            self._scene.add_effect( MessageDialog(self._screen, "{} connected".format(self._interface.node.network_name), destroy_window=calling_frame))
        else:
            self._scene.add_effect( MessageDialog(self._screen, "Connection failure", destroy_window=calling_frame))



    def _cancel(self):
        self._scene.remove_effect(self)
        raise NextScene(self._scene.name)

    def _prompt_custom_http_uri(self):
        dialog = TextRequestDialog(
            self._screen, 
            label_prompt_text="Ex: http://127.0.0.1:8545", 
            label_align="<",
            width=40,
            continue_button_text="Connect", 
            name="dialog_custom_http_uri", 
            title="Custom HTTP URI", 
            text_label="URI: ",
            text_default_value=self._interface._config.http_uri,
            destroy_window=self,
            continue_function=self._continue_function,
            next_scene="Main"
        )
        self._scene.add_effect(dialog)

    def _prompt_custom_websocket_uri(self):
        dialog = TextRequestDialog(
            self._screen, 
            label_prompt_text="Ex:  ws://127.0.0.1:8546  |  wss://ssl.my.com", 
            label_align="<",
            width=55,
            continue_button_text="Connect", 
            name="dialog_custom_websocket_uri", 
            title="Custom Websockets URI", 
            text_label="URI: ",
            text_default_value=self._interface._config.websocket_uri,
            destroy_window=self,
            continue_function=self._continue_function,
            next_scene="Main"
        )
        self._scene.add_effect(dialog)


    def _prompt_custom_ipc_path(self):
        dialog = TextRequestDialog(
            self._screen, 
            label_prompt_text="Ex: /path/to/your/node.ipc", 
            label_align="<",
            width=40,
            continue_button_text="Connect", 
            name="dialog_custom_ipc_path", 
            title="Custom IPC Path", 
            text_label="Path: ",
            text_default_value=self._interface._config.ipc_path,
            destroy_window=self,
            continue_function=self._continue_function,
            next_scene="Main"
        )
        self._scene.add_effect(dialog)


