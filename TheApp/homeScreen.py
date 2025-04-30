from kivy.uix.screenmanager import Screen
import pickle

class HomeScreen(Screen):
    
    INSTANCE = None

    def save_settings(self):
        with open("configs.pickle", "wb") as f:
            pickle.dump(self.INSTANCE.data, f)

    def load_settings(self):
        with open("configs.pickle", "rb") as f:
            self.INSTANCE.data = pickle.load(f)
