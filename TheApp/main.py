from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.label import Label
from jnius import autoclass, JavaException
from kivy.uix.screenmanager import ScreenManager
from bluetooth import AndroidBluetoothClass
from homeScreen import HomeScreen
from settingsScreen import SettingsScreen
from resultsScreen import ResultsScreen
from appData import AppData

class BluetoothApp(App):
    INSTANCE = None
    data = None

    menu = None
    settings = None
    bluetooth = None

    screen_file_names = ["homeScreen", "settingsScreen", "resultsScreen"]

    def build(self):
        # self.status_label = Label(text='Welcome to Bluetooth App')
        # connect_btn = Button(text='Connect to HC-06')
        # send_btn = Button(text='Send Message')
        # receive_btn = Button(text='Receive Message')
        # layout = BoxLayout(orientation='vertical')
        # layout.add_widget(self.status_label)
        # layout.add_widget(connect_btn)
        # layout.add_widget(send_btn)
        # layout.add_widget(receive_btn)

        # self.bluetooth = AndroidBluetoothClass(self.update_status)

        # connect_btn.bind(on_press=lambda x: self.bluetooth.getAndroidBluetoothSocket('HC-06'))
        # send_btn.bind(on_press=lambda x: self.bluetooth.BluetoothSend(b'1'))
        # receive_btn.bind(on_press=lambda x: self.bluetooth.BluetoothReceive())


        kivy_string = ""
        for kivy_file in self.screen_file_names:
            with open(f"{kivy_file}.kv") as f:
                kivy_string += f.read()
        
        Builder.load_string(kivy_string)

        self.data = AppData()
        self.bluetooth = AndroidBluetoothClass(lambda string : print(string))

        self.menu = HomeScreen(name='home')
        self.settings = SettingsScreen(name='settings')
        self.results = ResultsScreen(name = 'results')

        self.sm = ScreenManager()
        self.sm.add_widget(self.menu)
        self.sm.add_widget(self.settings)
        self.sm.add_widget(self.results)

        BluetoothApp.INSTANCE = self
        self.menu.INSTANCE = self
        self.settings.INSTANCE = self
        self.results.INSTANCE = self

        return self.sm

    def update_status(self, message):
        self.status_label.text = message

if __name__ == '__main__':
    BluetoothApp().run()