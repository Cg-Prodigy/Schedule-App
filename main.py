# from kivy.factory import Factory
# from kaki.app import App
from android.storage import app_storage_path
from kivy.core.window import Window
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.dialog import MDDialog

from app.main_ui import Manager

Builder.load_file('app/main_ui.kv')
Builder.load_file('app/defaults.kv')
Builder.load_file('app/create_task.kv')


class HotReload(MDApp):
    # CLASSES = {'Manager': 'app.main_ui'}
    # KV_FILES = ['app/main_ui.kv', 'app/defaults.kv', 'app/create_task.kv']
    # AUTORELOADER_PATHS = [('./app', {'recursive': True})]

    # def build_app(self):
    #     return Factory.Manager()

    def build(self):
        Window.bind(on_keyboard=self.close_app)
        return Manager()

    def on_start(self):
        settings_path = app_storage_path()

    def on_pause(self):
        return True

    def close_app(self, window, key, scancode, codepoint, modifier):
        if key == 27:
            close_dialog = MDDialog(
                title='Exit',
                text='Are you sure you want to exit application?',
                buttons=[
                    MDFillRoundFlatButton(
                        text='Cancel',
                        on_release=lambda x:close_dialog.dismiss()
                    ),
                    MDFillRoundFlatButton(
                        text='Ok',
                        on_release=lambda x:self.stop()
                    )
                ]
            )
            close_dialog.open()
            return True


if __name__ == '__main__':
    HotReload().run()
