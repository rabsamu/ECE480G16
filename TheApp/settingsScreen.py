from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout

class SettingsScreen(Screen):
    INSTANCE = None
    mode = ""
    test_param_dict = {
        "asv" : ["voltage 1", "time 1", "voltage 2", "time 2"],
        "dpasv" : ["start voltage", "stop voltage", "voltage 1", "time 1", "voltage 2", "time 2"]
    } 

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
            textinput = TextInput()
            if(not values[i] == 0):
                textinput.text = (str)(values[i])
            row.add_widget(textinput)
            self.layout.mainContent.paramList.add_widget(row)

    def unload(self):
        self.layout.mainContent.paramList.clear_widgets()

    def save_config(self):
        config = []
        for i in range(len(self.layout.mainContent.paramList.children)):
            i2 = len(self.layout.mainContent.paramList.children) - 1 - i
            row = self.layout.mainContent.paramList.children[i2]
            if(len(row.children) == 2):
                config.append((float)(row.children[0].text))
        if(self.mode == "asv"):
            print(config)
            self.INSTANCE.data.configASV = config
        