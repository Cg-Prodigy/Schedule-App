from kivy.factory import Factory
from kaki.app import App
# from android.storage import app_storage_path
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.app import MDApp

# from app_dir.main_ui import COLOR_CONST, DBtn, ErrorDialog, Manager

# Builder.load_file('app_dir/main_ui.kv')
# Builder.load_file('app_dir/defaults.kv')


class HotReload(App, MDApp):
    CLASSES = {'Manager': 'app_dir.main_ui'}
    KV_FILES = ['app_dir/main_ui.kv',
                'app_dir/defaults.kv', 'app_dir/create_task.kv']
    AUTORELOADER_PATHS = [('./app_dir', {'recursive': True})]

    def build_app(self):
        return Factory.Manager()

    # def build(self):
    #     Window.bind(on_keyboard=self.close_app)
    #     return Manager

    # def on_start(self):
    #     settings_path = app_storage_path()
    #     print(Manager.current)
    #     return True

    # def on_pause(self):
    #     return True

    # def close_app(self, window, key, scancode, codepoint, modifier):
    #     if key == 27:
    #         if Manager.current != 'home screen':
    #             Manager.current = 'home screen'
    #         else:
    #             close_dialog = ErrorDialog(
    #                 text='[color=0D7377]Are you sure you want to exit application?[/color]',
    #                 buttons=[
    #                     DBtn(
    #                         text='Cancel',
    #                         on_release=lambda x:close_dialog.dismiss(),
    #                     ),
    #                     DBtn(
    #                         text='Ok',
    #                         on_release=lambda x:self.stop()
    #                     )
    #                 ],
    #                 radius=[dp(10)],
    #                 md_bg_color=COLOR_CONST['f_ground']
    #             )
    #             close_dialog.open()
    #             return True


if __name__ == '__main__':
    HotReload().run()
