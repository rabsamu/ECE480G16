from kivy.uix.screenmanager import Screen
import pickle

class HomeScreen(Screen):
    INSTANCE = None

    def save_settings(self):
        with open("configs.txt", "wb") as f:
            pickle.dump(self.INSTANCE.data, f)

    def load_settings(self):
        with open("configs.txt", "rb") as f:
            self.INSTANCE.data = pickle.load(f)