from kivy.uix.screenmanager import Screen
from kivy.clock import Clock


class ResultsScreen(Screen):
    def start_process(self):
        self.event = Clock.schedule_interval(self.process, 2)

    def process(self, dt):
        self.layout.mainContent.graph.reload()

    def stop_process(self):
        self.event.cancel()