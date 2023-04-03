#############################################
# Bluetooth Scanner
#############################################
from kivy.app import App
from kivy.clock import mainthread
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

from android import mActivity
from android.broadcast import BroadcastReceiver
from jnius import autoclass, cast

from android_permissions import AndroidPermissions

BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
BluetoothManager = autoclass('android.bluetooth.BluetoothManager')
BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')

class MyApp(App):
    
    def build(self):
        self.label = Label(text='Press the button...')
        b = Button(text='Start Bluetooth Scan', on_press=self.check_permission)
        box = BoxLayout(orientation='vertical')
        box.add_widget(self.label)
        box.add_widget(b)
        return box

    def on_start(self):
        self.scan_num = 0
        self.FOUND = BluetoothDevice.ACTION_FOUND
        self.STARTED = BluetoothAdapter.ACTION_DISCOVERY_STARTED
        self.FINISHED = BluetoothAdapter.ACTION_DISCOVERY_FINISHED
        self.ba = None

    def check_permission(self, b):
        self.dont_gc = AndroidPermissions(self.start_scan)
        
    def start_scan(self):
        self.dont_gc = None
        if not self.ba:
            if not BluetoothAdapter.getDefaultAdapter().isEnabled():
                self.update_label('The Bluetooth Adapter is not enabled.')
                return
            actions = [self.FOUND, self.STARTED, self.FINISHED]
            self.br = BroadcastReceiver(self.on_broadcast, actions=actions)
            self.br.start()
            self.bm = cast(BluetoothManager,
                           mActivity.getSystemService(BluetoothManager))
            self.ba = self.bm.getAdapter()
            if not self.ba.startDiscovery():
                self.update_label('Bluetooth Scan Failed.')

    def on_broadcast(self, context, intent):
        action = intent.getAction()
        
        if action == self.STARTED:
            self.result = ['Looking for devices (Scan #' +\
                           str(self.scan_num) + '):']
            self.scan_num += 1
            self.build_text(self.result)
            
        elif action == self.FOUND:
            self.result.append('\n'+intent.getExtra(BluetoothDevice.EXTRA_NAME))
            self.build_text(self.result)

        elif action == self.FINISHED:
            self.ba.cancelDiscovery()
            self.ba = None
            self.br.stop()
            self.br = None
            self.result.append('\nFinished')
            self.build_text(self.result)

    def build_text(self, result):
        text = ''
        for d in result:
            text = text + d 
        self.update_label(text)

    @mainthread
    def update_label(self,text):
        self.label.text = text

MyApp().run()