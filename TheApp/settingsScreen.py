from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button

class SettingsScreen(Screen):
    
    INSTANCE = None
    mode = ""
    test_param_dict = {
        "asv" : ["gain", "low voltage", "times to sample", "time 1", "voltage 1", "time 2", "voltage 2", "sample rate"],
        "dpasv" : ["start voltage", "stop voltage", "voltage 1", "time 1", "voltage 2", "time 2"]
    } 
    test_param_types = {
        "asv" : ["gain", "", "", "", "", "", "", ""],
        "dpasv" : ["start voltage", "stop voltage", "voltage 1", "time 1", "voltage 2", "time 2"]
    }

    gain_options = []

    def load(self,test_type):
        self.mode = test_type
        if(self.mode == "asv"):
            
            values = self.INSTANCE.data.configASV
            print(values)
        if(not len(values) == len(self.test_param_dict[test_type])):
            values = [0] * len(self.test_param_dict[test_type])
            print(values)
        for i in range(len(self.test_param_dict[test_type])):
            row = BoxLayout(orientation="horizontal")
            label = Label(text = self.test_param_dict[test_type][i])
            row.add_widget(label)
            if(self.test_param_types[test_type][i] == "gain"):
                gainsDropdown = DropDown()
                for gain in self.gain_options:
                    btn = Button(text=gain)
                    btn.bind(on_release=lambda btn: gainsDropdown.select(btn.text))

                    # then add the button inside the dropdown
                    gainsDropdown.add_widget(btn)

                mainbutton = Button(text='Gain', size_hint=(None, None))
                mainbutton.bind(on_release=gainsDropdown.open)
                gainsDropdown.bind(on_select=lambda instance, x: setattr(mainbutton, 'text', x))
                row.add_widget(mainbutton)
            else:
                textinput = TextInput()
                if(not values[i] == 0):
                    textinput.text = (str)(values[i])
                row.add_widget(textinput)
            
            
            
            self.layout.mainContent.paramList.add_widget(row)

    def unload(self):
        self.layout.mainContent.paramList.clear_widgets()

    def send_config(self):
        try:
            if(self.mode == "asv"):
                message = "1,"
                for i in range(len(self.INSTANCE.data.configASV) - 1):
                    message += str(self.INSTANCE.data.configASV[i]) + ","
                message += str(self.INSTANCE.data.configASV[-1]) + "\n"
            
            self.INSTANCE.bluetooth.BluetoothSend(message.encode())
        except Exception as e:
            self.layout.topBar.mytext.text = e

    def save_config(self):
        config = []
        for i in range(len(self.layout.mainContent.paramList.children)):
            i2 = len(self.layout.mainContent.paramList.children) - 1 - i
            row = self.layout.mainContent.paramList.children[i2]
            if(len(row.children) == 2):
                config.append((float)(row.children[0].text))
        if(self.mode == "asv"):
            self.INSTANCE.data.configASV = config
            
        