from datetime import date, datetime, timedelta
from functools import partial
import re

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager
from kivy.utils import get_color_from_hex
from kivymd.uix import button
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRoundFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.picker import MDDatePicker, MDTimePicker
from kivymd.uix.screen import MDScreen
# database
from tinydb import Query, TinyDB
from tinydb.storages import JSONStorage
from tinydb_serialization import SerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer
# constants
COLOR_CONST = {
    'i_nrml': get_color_from_hex('14FFEC'),
    't_nrml': get_color_from_hex('0D7377'),
    'f_ground':  get_color_from_hex('323232'),
    'bg_color': get_color_from_hex('212121')
}
TIME = datetime.now().time()
DATE = datetime.now().date()
# database
serial = SerializationMiddleware(JSONStorage)
serial.register_serializer(DateTimeSerializer(), 'TinyDate')
DB = TinyDB('db.json', storage=serial)
QRY = Query()
# Entry Class


class Manager(ScreenManager):
    def return_home(self):
        self.current = 'home screen'
        self.transition.direction = 'right'


class HomeScreen(MDScreen):
    h_drop = None
    task_list = ObjectProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        Clock.schedule_once(self.add_tasks, 0)

    def add_tasks(self, time):
        for i in range(len(DB.all())):
            self.task_box = TaskBox()
            self.task_box.tt.text = '{}'.format(
                DB.all()[i]['Title'])
            self.task_box.td.text = 'Task Description ---- {}'.format(
                DB.all()[i]['Description'])
            self.task_box.tl.text = 'Task Location ---- {}'.format(
                DB.all()[i]['Room/Location']
            )
            self.task_box.sd.text = 'Start Date ---- {}'.format(
                DB.all()[i]['Start Date']
            )
            self.task_box.ed.text = 'End Date ---- {}'.format(
                DB.all()[i]['End Date']
            )
            self.task_box.st.text = 'Start Time ---- {}'.format(
                DB.all()[i]['Start Time']
            )

            self.task_box.et.text = 'End Time ---- {}'.format(
                DB.all()[i]['End Time']
            )
            self.task_box.tc.text = 'Category ---- {}'.format(
                DB.all()[i]['Category']
            )
            self.task_box.tr.text = 'Reminder ---- {}'.format(
                DB.all()[i]['Reminder']
            )
            self.task_list.add_widget(self.task_box)

    def home_screen_drop(self, instance):
        item = [
            {
                'text': f'{i}',
                'viewclass': 'OneLineListItem',
                'divider': None,
                'height': dp(40),
                'theme_text_color': 'Custom',
                'text_color': COLOR_CONST['i_nrml'],
                'on_release': lambda x=f'{i}': self.pick_selection(x)
            } for i in ['Settings', 'About', 'Share', 'Donate']
        ]
        if not self.h_drop:
            self.h_drop = MDDropdownMenu(
                items=item,
                width_mult=2,
                caller=instance,
                background_color=COLOR_CONST['f_ground']
            )
        self.h_drop.open()

    def pick_selection(self, item):
        self.h_drop.dismiss()


class CreateTask(MDScreen):
    title = ObjectProperty()
    details = ObjectProperty()
    room = ObjectProperty()
    d_check = ObjectProperty()
    s_date = ObjectProperty()
    s_time = ObjectProperty()
    e_date = ObjectProperty()
    e_time = ObjectProperty()
    task_list = ObjectProperty()
    t_dd = ObjectProperty()
    t_hh = ObjectProperty()
    t_mm = ObjectProperty()
    dt_reminder = ObjectProperty()
    dt_category = ObjectProperty()
    d_category = None
    d_reminder = None

    def __init__(self, **kw):
        super().__init__(**kw)
        self.t_title = None
        self.t_details = None
        self.t_location = None
        self.start_date = None
        self.end_date = None
        self.start_time = None
        self.end_time = None
        self.t_category = 'None'
        self.t_reminder = 'No reminder'
        self.dd = 0
        self.hh = 0
        self.mm = 0
        self.task_info = {}
        # pickers
        self.date_picker = DatePicker(
            primary_color=COLOR_CONST['f_ground'],
            text_toolbar_color=COLOR_CONST['i_nrml']
        )
        self.time_picker = TimePicker(
            animation_duration=0.0,
            am_pm=str(TIME.strftime('%p')).lower()
        )
    # task details and description

    def validate_value(self, instance):
        if instance.focus:
            pass
        else:
            value = str(instance.text).strip()
            if instance.hint_text == 'Title':
                if not value:
                    instance.helper_text = 'required'
                    self.t_title = None
                elif len(value) <= 10 and not DB.search(QRY['Title'] == value):
                    self.t_title = value
                    instance.helper_text = 'Valid title. Proceed'
                    return
                elif len(value) > 10:
                    instance.helper_text = 'Error! Your title is quite lengthy. Consider shortening it'
                    self.t_title = None
                else:
                    self.t_title = None
                    instance.helper_text = 'Error! A task with the same title exists'
                return
            elif instance.hint_text == 'Description':
                self.t_details = None if not value else value
            else:
                self.t_location = None if not value else value
    #  Date

    def set_date_today(self, instance):
        if instance.state == 'down':
            self.start_date = DATE
            self.s_date.text = str(DATE.strftime('%A %d-%B-%Y'))
        else:
            self.start_date = None
            self.s_date.text = 'DD-MM-YY'

    def open_date_dialog(self):
        self.date_picker.bind(on_save=self.return_select_date)
        self.date_picker.open()
        self.d_check.state = 'normal'
        self.s_date.text = 'DD-MM-YY'

    def return_select_date(self, instance, value, date_range):
        if value < DATE:
            self.s_date.text = '[color=ff3333]Cannot go back in time. Select a date value in the present or future[/color]'
            self.start_date = None
        else:
            self.s_date.text = str(value.strftime('%A %d-%B-%Y'))
            self.start_date = value
    # time

    def open_time_dialog(self):
        if not self.start_date:
            self.s_time.text = '[color=ff3333] Cannot select time without a valid date value.[/color]'
            return
        self.time_picker.set_time(TIME)
        self.s_time.text = 'HH-MM-AM/PM'
        self.time_picker.bind(on_save=self.return_select_time,
                              on_cancel=self.reset_time_value)
        self.time_picker.open()

    def return_select_time(self, instance, time):
        combine_datetime = datetime.combine(self.start_date, time)
        if combine_datetime < datetime.combine(DATE, TIME):
            self.s_time.text = '[color=ff3333] Selected time is behind current time. Select a valid time value[/color]'
            return
        self.start_time = time
        self.s_time.text = str(time.strftime('%I:%M:%p'))
        instance.set_time(TIME)

    def reset_time_value(self, instance, time):
        self.start_time = None
        instance.set_time(TIME)

    #  compute end date and time
    def durations(self, instance):
        if instance.focus:
            pass
        else:
            value = str(instance.text).strip()
            if value == '':
                instance.icon_left = ''
                if instance.hint_text == 'DD':
                    self.dd = 0
                elif instance.hint_text == 'HH':
                    self.hh = 0
                else:
                    self.mm = 0
                return
            try:
                value = int(value)
                instance.icon_left = 'check-all'
                if instance.hint_text == 'DD':
                    self.dd = value
                elif instance.hint_text == 'HH':
                    self.hh = value
                else:
                    self.mm = value
            except Exception as e:
                instance.icon_left = 'close-circle-outline'
                if instance.hint_text == 'DD':
                    self.dd = 0
                elif instance.hint_text == 'HH':
                    self.hh = 0
                else:
                    self.mm = 0

    def compute_end_datetime(self):
        if str(self.t_dd.text).strip() == '' and str(self.t_hh.text).strip() == '' and str(self.t_mm.text).strip() == '':
            error_dialog = ErrorDialog(
                text='[color=ff3333][size=13]At least one field is required to compute end date and time[/size][/color]',
                buttons=[
                    DBtn(text='Ok', on_release=lambda x:error_dialog.dismiss())
                ]
            )
            error_dialog.open()
            return
        if not self.start_date or not self.start_time:
            return
        if self.dd == 0 and self.mm == 0 and self.hh == 0:
            return
        combined_datetime = datetime.combine(self.start_date, self.start_time)
        try:
            end_datetime = combined_datetime + \
                timedelta(days=self.dd, hours=self.hh, minutes=self.mm)
        except OverflowError:
            error_dialog = ErrorDialog(
                text='[color=ff3333]The Time machine has met its limits. Its over![/color]',
                buttons=[
                    DBtn(text='Ok', on_release=lambda x:error_dialog.dismiss())
                ]
            )
            error_dialog.open()
            return
        self.end_date = end_datetime.date()
        self.end_time = end_datetime.time()
        self.e_date.text = str(self.end_date.strftime('%A %d-%B-%Y'))
        self.e_time.text = str(self.end_time.strftime('%I:%M:%p'))
    # category

    def set_category(self, instance):
        category = ['None', 'Work', 'Personal',
                    'Leisure', 'Social', 'Study', 'Formal']
        item = [
            {
                'text': f'{i}',
                'viewclass': 'OneLineListItem',
                'on_release': lambda x=f'{i}': self.set_type_category(x, d_menu, instance),
                'divider': None,
                'theme_text_color': 'Custom',
                'text_color': COLOR_CONST['i_nrml'],
                'height': dp(40),
            } for i in category
        ]
        d_menu = MDDropdownMenu(
            items=item,
            width_mult=3,
            caller=instance,
            background_color=COLOR_CONST['f_ground']
        )
        d_menu.open()

    def set_type_category(self, item, menu, instance):
        instance.text = item
        self.t_category = item
        menu.dismiss()

    def set_reminder(self, instance):
        if not(self.start_time or self.start_date):
            return
        else:
            time_diff = datetime.combine(
                self.start_date, self.start_time)-datetime.combine(DATE, TIME)
            m_diff = time_diff.seconds / 60
            print(self.drop_down_menu(m_diff))
            item = [
                {
                    'text': f'{i}',
                    'viewclass': 'OneLineListItem',
                    'on_release': lambda x=f'{i}': self.set_item_category(x, d_menu, instance),
                    'divider': None,
                    'theme_text_color': 'Custom',
                    'text_color': COLOR_CONST['i_nrml'],
                    'height': dp(40),
                } for i in self.drop_down_menu(m_diff)
            ]
            d_menu = MDDropdownMenu(
                items=item,
                width_mult=4,
                caller=instance,
                background_color=COLOR_CONST['f_ground']
            )
            d_menu.open()

    def set_item_category(self, item, menu, instance):
        instance.text = item
        self.t_reminder = item
        menu.dismiss()

    #  final step before pushing task details to the database

    def validate_task_values(self):
        if not (self.t_title and self.start_date and self.start_time and self.end_time and self.end_date):
            error_dialog = ErrorDialog(
                text='[color=ff3333]Cannot add task to the task list. Please review details and try again![/color]',
                buttons=[
                    DBtn(text='Ok', on_release=lambda x:error_dialog.dismiss())
                ]
            )
            error_dialog.open()
            return
        else:
            self.task_info['Title'] = self.t_title
            self.task_info['Description'] = self.t_details
            self.task_info['Room/Location'] = self.t_location
            self.task_info['Start Datetime'] = datetime.combine(
                self.start_date, self.start_time)
            self.task_info['End Datetime'] = datetime.combine(
                self.end_date, self.end_time)
            self.task_info['Start Date'] = str(
                self.start_date.strftime('%A %d-%B-%Y'))
            self.task_info['End Date'] = str(
                self.end_date.strftime('%A %d-%B-%Y'))
            self.task_info['Start Time'] = str(
                self.start_time.strftime('%I:%M:%p'))
            self.task_info['End Time'] = str(
                self.end_time.strftime('%I:%M:%p'))
            self.task_info['Reminder'] = self.t_reminder
            self.task_info['Category'] = self.t_category
            DB.insert(self.task_info)
            self.task_box = TaskBox()
            self.task_box.tt.text = '{}'.format(
                self.task_info['Title'])
            self.task_box.td.text = 'Task Description ---- {}'.format(
                self.task_info['Description'])
            self.task_box.tl.text = 'Task Location ---- {}'.format(
                self.task_info['Room/Location']
            )
            self.task_box.sd.text = 'Start Date ---- {}'.format(
                self.task_info['Start Date']
            )
            self.task_box.ed.text = 'End Date ---- {}'.format(
                self.task_info['End Date']
            )
            self.task_box.st.text = 'Start Time ---- {}'.format(
                self.task_info['Start Time']
            )

            self.task_box.et.text = 'End Time ---- {}'.format(
                self.task_info['End Time']
            )
            self.task_box.tc.text = 'Category ---- {}'.format(
                self.task_info['Category']
            )
            self.task_box.tr.text = 'Reminder ---- {}'.format(
                self.task_info['Reminder']
            )
            self.task_list.add_widget(self.task_box)
            self.t_title = None
            self.t_details = None
            self.t_location = None
            self.start_date = None
            self.end_date = None
            self.start_time = None
            self.end_time = None
            self.t_category = 'None'
            self.t_reminder = 'No reminder'
            self.dd = 0
            self.hh = 0
            self.mm = 0
            self.task_info = {}
            self.manager.current = 'home screen'
            self.manager.transition.direction = 'right'
            Clock.schedule_once(self.reset_values, .1)

    def reset_values(self, time):
        self.title.text = ''
        self.title.helper_text = 'required'
        self.details.text = ''
        self.room.text = ''
        self.d_check.state = 'normal'
        self.s_time.text = 'HH-MM-AM/PM'
        self.s_date.text = 'DD-MM-YY'
        self.t_dd.text = ''
        self.t_hh.text = ''
        self.t_mm.text = ''
        self.t_dd.icon_left = ''
        self.t_hh.icon_left = ''
        self.t_mm.icon_left = ''
        self.e_date.text = ''
        self.e_time.text = ''
        self.dt_category.text = 'None'
        self.dt_reminder.text = 'No reminder'
    #  static

    @staticmethod
    def drop_down_menu(c_time):
        item = ['No reminder', 'On time', '5 minutes before time',
                '10 minutes before time', '15 minutes before time']
        if c_time < 15:
            item = item[0:4]
        if c_time < 10:
            item = item[0:3]
        if c_time < 5:
            item = item[0:2]
        return item


class TaskBox(MDBoxLayout):
    tt = ObjectProperty()
    td = ObjectProperty()
    tl = ObjectProperty()
    sd = ObjectProperty()
    ed = ObjectProperty()
    st = ObjectProperty()
    et = ObjectProperty()
    tc = ObjectProperty()
    tr = ObjectProperty()

    def __init__(self, **kwargs):
        super(TaskBox, self).__init__(**kwargs)
        self.bind(
            on_touch_down=self.create_clock,
            on_touch_up=self.delete_clock
        )

    def create_clock(self, widget, touch, *args):
        if self.collide_point(touch.x, touch.y):
            callback = partial(self.createDialog, touch)
            Clock.schedule_once(callback, .7)
            touch.ud['event'] = callback
            return True

    def delete_clock(self, widget, touch, *args):
        if self.collide_point(touch.x, touch.y):
            Clock.unschedule(touch.ud['event'])
            return True

    def createDialog(self, touch, *args):
        delete_task = ErrorDialog(
            text='[color=14FFEC]Are you sure you want to delete task [b]{}[/b] [/color]'.format(
                self.tt.text),
            buttons=[
                DBtn(
                    text='No',
                    on_release=lambda x:delete_task.dismiss(),
                ),
                DBtn(
                    text='Yes',
                    on_release=lambda x:self.delete_selected_task(delete_task),
                )
            ]
        )
        delete_task.open()

    def delete_selected_task(self, dialog):
        DB.remove(QRY['Title'] == self.tt.text)
        dialog.dismiss()
        self.parent.remove_widget(self)


class TaskLabel(MDLabel):
    pass


class ErrorDialog(MDDialog):
    pass


class DBtn(MDRoundFlatButton):
    pass


class DatePicker(MDDatePicker):
    year = DATE.year,
    month = DATE.month,
    day = DATE.day


class TimePicker(MDTimePicker):
    pass
