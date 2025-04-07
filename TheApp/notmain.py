# # import kivy
# from kivy.app import App
# from kivy.lang import Builder
# from kivy.uix.screenmanager import ScreenManager
# from kivy.uix.boxLayout import BoxLayout
# from kivy.uix.label import Label
# # from settingsScreen import SettingsScreen
# # from homeScreen import HomeScreen
# # from resultsScreen import ResultsScreen
# # from appData import AppData
# # from bluetooth import AndroidBluetoothClass

# class TestApp(App):
#     INSTANCE = None
    
#     menu = None
#     settings = None
#     results = None
#     sm = None
#     data = None
#     bluetooth = None

#     screen_file_names = ["homeScreen", "settingsScreen", "resultsScreen"]

#     def build(self):
#         # try:
#         #     assert 1==3
#             # kivy_string = ""
#             # for kivy_file in self.screen_file_names:
#             #     with open(f"{kivy_file}.kv") as f:
#             #         kivy_string += f.read()
            
#             # Builder.load_string(kivy_string)

#             # self.data = AppData()
#             # self.bluetooth = AndroidBluetoothClass(lambda string : print(string))

#             # self.menu = HomeScreen(name='home')
#             # self.settings = SettingsScreen(name='settings')
#             # self.results = ResultsScreen(name = 'results')

#             # self.sm = ScreenManager()
#             # self.sm.add_widget(self.menu)
#             # self.sm.add_widget(self.settings)
#             # self.sm.add_widget(self.results)

#             # TestApp.INSTANCE = self
#             # self.menu.INSTANCE = self
#             # self.settings.INSTANCE = self
#             # self.results.INSTANCE = self
#         # except Exception as e:
#         layout = BoxLayout(orientation='vertical')
#         exceptionLabel = Label(text="pls")
#         layout.add_widget(exceptionLabel)

#         return layout

#         # return self.sm

# if __name__ == "__main__":
#     TestApp().run()