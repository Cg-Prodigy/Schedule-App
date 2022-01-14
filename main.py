# from kivy.factory import Factory
# from kaki.app import App
from android import loadingscreen
from android.storage import app_storage_path
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.app import MDApp

from app_dir.main_ui import COLOR_CONST, DBtn, ErrorDialog, Manager

Builder.load_file('app_dir/main_ui.kv')
Builder.load_file('app_dir/defaults.kv')
Builder.load_file('app_dir/create_task.kv')


class HotReload(MDApp):
    # CLASSES = {'Manager': 'app_dir.main_ui'}
    # KV_FILES = ['app_dir/main_ui.kv',
    #             'app_dir/defaults.kv', 'app_dir/create_task.kv']
    # AUTORELOADER_PATHS = [('.', {'recursive': True})]

    # def build_app(self):
    #     return Factory.Manager()
    def on_start(self):
        loadingscreen.hide_loading_screen()
        settings_path = app_storage_path()
        return True

    def on_pause(self):
        return True

    def close_app(self, window, key, scancode, codepoint, modifier):
        if key == 27:
            close_dialog = ErrorDialog(
                text='[color=0D7377]Are you sure you want to exit application?[/color]',
                buttons=[
                    DBtn(
                        text='Cancel',
                        on_release=lambda x:close_dialog.dismiss(),
                    ),
                    DBtn(
                        text='Ok',
                        on_release=lambda x:self.stop()
                    )
                ],
                radius=[dp(10)],
                md_bg_color=COLOR_CONST['f_ground']
            )
            close_dialog.open()
            return True

    def build(self):
        Window.bind(on_keyboard=self.close_app)
        return Manager()


if __name__ == '__main__':
    HotReload().run()
