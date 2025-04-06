# import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from settingsScreen import SettingsScreen
from homeScreen import HomeScreen
from resultsScreen import ResultsScreen
from appData import AppData

class TestApp(App):
    INSTANCE = None
    
    menu = None
    settings = None
    results = None
    sm = None
    data = None

    screen_file_names = ["homeScreen", "settingsScreen", "resultsScreen"]

    def build(self):
        kivy_string = ""
        for kivy_file in self.screen_file_names:
            with open(f"kv/{kivy_file}.kv") as f:
                kivy_string += f.read()
        
        Builder.load_string(kivy_string)

        self.data = AppData()

        self.menu = HomeScreen(name='home')
        self.settings = SettingsScreen(name='settings')
        self.results = ResultsScreen(name = 'results')

        self.sm = ScreenManager()
        self.sm.add_widget(self.menu)
        self.sm.add_widget(self.settings)
        self.sm.add_widget(self.results)

        TestApp.INSTANCE = self
        self.menu.INSTANCE = self
        self.settings.INSTANCE = self

        return self.sm

if __name__ == "__main__":
    TestApp().run()