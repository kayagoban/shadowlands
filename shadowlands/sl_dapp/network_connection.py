from shadowlands.sl_dapp import SLDapp, SLFrame
import pyperclip, os
import schedule
from shadowlands.tui.debug import debug
import pdb

class NetworkConnection(SLDapp):
  def initialize(self):
    self.add_sl_frame( NetworkStrategies(self, 10, 26, title="Network Options"))
    self.connection_strategy = None

  def attempt_connection(self):
    fn = self._interface.node.__getattribute__(self.conn_fn)
    self._interface.node.thread_shutdown = True
    self._interface.node.heartbeat_thread.join()
    self._interface.node.thread_shutdown = False

    try:
        if len(self.args) > 0:
            return fn(self.args)
        else:
            return fn()
    except StaleBlockchain:
        self._scene.add_effect( MessageDialog(self._screen, "Stale blockchain on selected Node"))
        return
    self._interface.node.start_heartbeat_thread()

     
class NetworkStrategies(SLFrame):
  def initialize(self):
    options = [
        ('Local node', 'connect_w3_local'), 
        ('Custom infura', 'connect_w3_custom_infura'),
        ('Custom http', 'connect_w3_custom_http'), 
        ('Custom websocket', 'connect_w3_custom_websocket'),
        ('Custom ipc', 'connect_w3_custom_ipc'),
    ]
    self.listbox_value = self.add_listbox(
      5, options, on_select=self._select 
      #default_value=self.dapp.config.connection_strategy
    )
    self.add_button(self.close, "Cancel")

  def _select(self):
    connect_fn = self.listbox_value()
    self.dapp.connection_strategy = connect_fn

    if connect_fn == 'connect_w3_custom_http':
      self.dapp.add_sl_frame(CustomHttpUri(self.dapp, 5, 30, title="Custom Http URI"))
    elif connect_fn == 'connect_w3_custom_ipc':
      self.dapp.add_sl_frame(CustomIpc(self.dapp, 5, 30, title="Custom IPC path"))
    elif connect_fn == 'connect_w3_custom_websocket':
      self.dapp.add_sl_frame(CustomWebsocket(self.dapp, 5, 30, title="Custom Websocket URI"))
    elif connect_fn == 'connect_w3_custom_infura':
      self.dapp.add_sl_frame(CustomInfura(self.dapp, 12, 45, title="Custom Infura Credentials"))
      self.close()


class CustomInfura(SLFrame):
  def initialize(self):
    self.add_divider()
    self.add_label(" WEB3_INFURA_PROJECT_ID")
    self.id_value = self.add_textbox(
      '',
      default_value=os.environ.get('WEB3_INFURA_PROJECT_ID')
    ) 
    self.add_label(" WEB3_INFURA_API_SECRET")

    self.secret_value = self.add_textbox(
      '',
      default_value=os.environ.get('WEB3_INFURA_API_SECRET')
    ) 
    self.add_button_row(
      [
        ("Connect", self._connect, 0),
        ("Cancel", self.close, 3)
      ]
    )

  def _connect(self):
    id_value = self.id_value()
    secret_value = self.secret_value()
    self.dapp.config.connection_args = (self.id_value(), self.secret_value())
    self.dapp.config.connection_strategy = self.dapp.connection_strategy
    #debug(); pdb.set_trace()
    schedule.once().do(self.dapp.node.poll)
    self.close()


class CustomHttpUri(SLFrame):
  def initialize(self):
    self.add_label("Ex: http://192.168.1.150:8545")
    self.text_value = self.add_textbox() 
    self.add_button(self.close,"Cancel")

class CustomIpc(SLFrame):
  def initialize(self):
    self.add_label("Ex: http://192.168.1.150:8545")
    self.text_value = self.add_textbox() 
    self.add_button(self.close,"Cancel")

class CustomWebsocket(SLFrame):
  def initialize(self):
    self.add_label("Ex: http://192.168.1.150:8545")
    self.text_value = self.add_textbox() 
    self.add_button(self.close,"Cancel")



