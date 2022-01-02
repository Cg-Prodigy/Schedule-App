from kivy.factory import Factory
from kaki.app import App
# from android.storage import app_storage_path
from kivy.core.window import Window
from kivy.lang import Builder
from kivymd.app import MDApp

from app.main_ui import Manager

# Builder.load_file('app/main_ui.kv')
# Builder.load_file('app/defaults.kv')
# Builder.load_file('app/create_task.kv')


class HotReload(App, MDApp):
    CLASSES = {'Manager': 'app.main_ui'}
    KV_FILES = ['app/main_ui.kv', 'app/defaults.kv', 'app/create_task.kv']
    AUTORELOADER_PATHS = [('.', {'recursive': True})]

    def build_app(self):
        return Factory.Manager()

    # def build(self):
    #     Window.bind(on_keyboard=self.close_app)
    #     return Manager()

    # def on_pause(self):
    #     return True

    # def close_app(self, window, key, scancode, codepoint, modifier):
    #     if key == 27:
    #         self.stop()
    #     return True

    # def on_start(self):
    #     settings_path = app_storage_path()


if __name__ == '__main__':
    HotReload().run()
