from datetime import datetime, timedelta
from functools import partial

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager
from kivy.utils import get_color_from_hex
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

# TinyDB

serialization = SerializationMiddleware(JSONStorage)
serialization.register_serializer(DateTimeSerializer(), 'TinyDate')
db = TinyDB('tasks.json', storage=serialization)
qry = Query()

# constants
COLOR_CONST = {
    'i_nrml': get_color_from_hex('14FFEC'),
    't_nrml': get_color_from_hex('0D7377'),
    'f_ground':  get_color_from_hex('323232'),
    'bg_color': get_color_from_hex('212121')
}
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
        for i in range(len(db.all())):
            self.task_box = TaskBox()
            self.task_box.tt.text = '{}'.format(
                db.all()[i]['Title'])
            self.task_box.td.text = 'Task Description ---- {}'.format(
                db.all()[i]['Description'])
            self.task_box.tl.text = 'Task Location ---- {}'.format(
                db.all()[i]['Room/Location']
            )
            self.task_box.sd.text = 'Start Date ---- {}'.format(
                db.all()[i]['Start Date']
            )
            self.task_box.ed.text = 'End Date ---- {}'.format(
                db.all()[i]['End Date']
            )
            self.task_box.st.text = 'Start Time ---- {}'.format(
                db.all()[i]['Start Time']
            )
            self.task_box.et.text = 'End Time ---- {}'.format(
                db.all()[i]['End Time']
            )
            self.task_box.tc.text = 'Category ---- {}'.format(
                db.all()[i]['Task Category']
            )
            self.task_box.tr.text = 'Reminder ---- {}'.format(
                db.all()[i]['Reminder']
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
        self.t_details = 'None'
        self.t_location = 'None'
        self.start_date = None
        self.end_date = None
        self.start_time = None
        self.end_time = None
        self.t_category = 'None'
        self.t_reminder = 'No reminder'
        self.dd = 0
        self.hh = 0
        self.mm = 0
        self.date_picker = MDDatePicker(
            year=datetime.now().date().year,
            month=datetime.now().date().month,
            day=datetime.now().date().day,
        )
        self.time_picker = MDTimePicker(
            am_pm=str(datetime.now().time().strftime('%p')).lower(),
            animation_duration=0.01,
        )
        self.time_picker.set_time(datetime.now().time())
        self.time_picker.bind(on_save=self.get_set_time,
                              on_cancel=self.reset_time)
        self.task_values = {}
    #     Clock.schedule_once(self.exp, 0)

    # def exp(self, time):
    #     print(type(self.manager.children[0]))
    # validate input values

    def validate_value(self, instance):
        if instance.focus:
            if instance.hint_text == 'Title *':
                instance.helper_text = 'required'
        if not instance.focus:
            if instance.hint_text == 'Title *':
                if str(instance.text).strip() == '':
                    self.t_title = None
                else:
                    self.t_title = str(instance.text).strip().title()
            if instance.hint_text == 'Description':
                if str(instance.text).strip() == '':
                    self.t_details = None
                else:
                    self.t_details = str(instance.text).strip().title()
            if instance.hint_text == 'Room/Location':
                if str(instance.text).strip() == '':
                    self.t_location = None
                else:
                    self.t_location = str(instance.text).strip().title()
    # date

    def set_date_today(self, instance):
        if instance.state == 'down':
            self.s_date.text = str(datetime.now().date())
            self.start_date = datetime.now().date()
            self.s_date.text_color = COLOR_CONST['i_nrml']
            return
        else:
            self.s_date.text = 'YY-MM-DD'
            self.start_date = None
            self.s_date.text_color = COLOR_CONST['t_nrml']

    def open_date_dialog(self):
        self.d_check.state = 'normal'
        self.date_picker.bind(on_save=self.get_set_date,
                              on_cancel=self.reset_date)
        self.date_picker.open()

    def get_set_date(self, instance, value, date_range):
        if value < datetime.now().date():
            self.s_date.text = 'Invalid selection. Cannot go back in time.'
            self.start_date = value
            self.s_date.text_color = get_color_from_hex('ff4500')
            return
        else:
            self.s_date.text = str(value)
            self.start_date = value
            self.s_date.text_color = COLOR_CONST['i_nrml']

    def reset_date(self, instance, value):
        self.s_date.text = 'YY-MM-DD'
    # time

    def open_time_dialog(self):
        self.time_picker.open()

    def get_set_time(self, instance, time):
        if self.start_date <= datetime.now().date() and time < datetime.now().time():
            self.s_time.text = 'Select a time value higher than the current time'
            self.s_time.text_color = get_color_from_hex('ff4500')
            self.start_time = None
            return
        else:
            self.start_time = time
            self.s_time.text = str(self.start_time.strftime("%H:%M:%p"))
            self.s_time.text_color = COLOR_CONST['i_nrml']

    def reset_time(self, *args):
        self.s_time.text = 'HH-MM-AM/PM'
    # end time and date

    def compute_end_datetime(self):
        if not (self.start_date and self.start_time):
            alert = ErrorDialog(
                text="[color=14FFEC][b]Error![/b]\nCannot compute end date or end time without valid start time and start date.[/color]",
                buttons=[
                    MDRoundFlatButton(
                        text='Ok',
                        on_release=lambda x: alert.dismiss(),
                    )
                ]
            )
            alert.open()
        elif self.dd == 0 and self.mm == 0 and self.hh == 0:
            alert = ErrorDialog(
                text='[color=14FFEC][b]Error![/b]\nAtlease one field is required to compute the end date and end time[/color]',
                buttons=[
                    MDRoundFlatButton(
                        text='Ok',
                        on_release=lambda x: alert.dismiss(),
                    )
                ]
            )
            alert.open()
        elif self.dd == None or self.mm == None or self.hh == None:
            alert = ErrorDialog(
                text='[color=14FFEC][b]Error![/b]\nInvalid entry. Cannot compute end date and end time for the task[/color]',
                buttons=[
                    MDRoundFlatButton(
                        text='Ok',
                        on_release=lambda x: alert.dismiss(),
                    )
                ]
            )
            alert.open()
        else:
            combine_duration = datetime.combine(
                self.start_date, self.start_time)+timedelta(days=self.dd, hours=self.hh, minutes=self.mm)
            self.end_time = combine_duration.time()
            self.e_time.text = str(self.end_time.strftime('%H:%M:%p'))
            self.end_date = combine_duration.date()
            if combine_duration.date() == datetime.now().date():
                self.e_date.text = 'Today'
            else:
                self.e_date.text = str(self.end_date)

    def durations(self, instance):
        if instance.focus:
            pass
        else:
            if instance.text == '':
                instance.icon_left = ''
                if instance.hint_text == 'DD':
                    self.dd = 0
                if instance.hint_text == 'HH':
                    self.hh = 0
                if instance.hint_text == 'MM':
                    self.mm = 0
            else:
                try:
                    int_value = abs(int(instance.text))
                    instance.icon_left = 'check-all'
                    if instance.hint_text == 'DD':
                        self.dd = int_value
                    if instance.hint_text == 'HH':
                        self.hh = int_value
                    if instance.hint_text == 'MM':
                        self.mm = int_value
                except Exception:
                    instance.icon_left = 'close-circle-outline'
                    if instance.hint_text == 'DD':
                        self.dd = None
                    if instance.hint_text == 'HH':
                        self.hh = None
                    if instance.hint_text == 'MM':
                        self.mm = None
    #  category

    def set_category(self, instance):
        item = [
            {
                'text': f'{i}',
                'divider': None,
                'height': dp(40),
                'viewclass': 'OneLineListItem',
                'theme_text_color': 'Custom',
                'text_color': COLOR_CONST['i_nrml'],
                'on_release': lambda x=f'{i}': self.pick_selection(x, instance)
            } for i in ['Work', 'Family', 'Leisure', 'Personal', 'Business', 'Study']
        ]
        if not self.d_category:
            self.d_category = MDDropdownMenu(
                items=item,
                width_mult=3,
                caller=instance,
                background_color=COLOR_CONST['f_ground']
            )
        self.d_category.open()
        return

    def pick_selection(self, value, instance):
        instance.text = value
        self.t_category = value
        self.d_category.dismiss()
    # reminder

    def set_reminder(self, instance):
        item = [
            {
                'text': f'{i}',
                'divider': None,
                'height': dp(40),
                'viewclass': 'OneLineListItem',
                'theme_text_color': 'Custom',
                'text_color': COLOR_CONST['i_nrml'],
                'on_release': lambda x=f'{i}': self.pick_reminder(x, instance)
            } for i in ['No reminder',
                        'On Time',
                        '5 minutes before time',
                        '10 minutes before time', '15 minutes before time'
                        ]
        ]
        self.d_reminder = MDDropdownMenu(
            items=item,
            width_mult=4,
            caller=instance,
            background_color=COLOR_CONST['f_ground']
        )
        self.d_reminder.open()

    def pick_reminder(self, value, instance):
        instance.text = value
        self.t_reminder = value
        self.d_reminder.dismiss()
    #  final validation

    def validate_task_values(self):
        if not self.t_title:
            error_dialog = ErrorDialog(
                text='[color=14FFEC][b]Unsuccesful. A title is required[/b]\n[/color]',
                buttons=[
                    DBtn(
                        text='Ok',
                        on_release=lambda x:error_dialog.dismiss()
                    ),
                ]
            )
            error_dialog.open()
            return
        elif not self.start_date:
            error_dialog = ErrorDialog(
                text='[color=14FFEC][b]Unsuccesful. A start date is required[/b]\n[/color]',
                buttons=[
                    DBtn(
                        text='Ok',
                        on_release=lambda x:error_dialog.dismiss(),
                    ),
                ]
            )
            error_dialog.open()
            return
        elif not self.start_time:
            error_dialog = ErrorDialog(
                text='[color=14FFEC][b]Unsuccesful. A start time is required[/b]\n[/color]',
                buttons=[
                    DBtn(
                        text='Ok',
                        on_release=lambda x:error_dialog.dismiss(),
                    ),
                ]
            )
            error_dialog.open()
            return
        elif not (self.dd or self.hh or self.mm):
            error_dialog = ErrorDialog(
                text='[color=14FFEC][b]Unsuccesful. Task duration is required[/b]\n[/color]',
                buttons=[
                    DBtn(
                        text='Ok',
                        on_release=lambda x:error_dialog.dismiss(),
                    ),
                ]
            )
            error_dialog.open()
            return
        elif not (self.end_date and self.end_time):
            error_dialog = ErrorDialog(
                text='[color=14FFEC][b]Unsuccesful. End date and end time have not been computed[/b]\n[/color]',
                buttons=[
                    DBtn(
                        text='Ok',
                        on_release=lambda x:error_dialog.dismiss(),
                    ),
                ]
            )
            error_dialog.open()
            return
        elif db.search(qry['Title'] == self.t_title):
            error_dialog = ErrorDialog(
                title='Error',
                text='Unsuccesful. A task with the same title already exists',
                buttons=[
                    DBtn(
                        text='Ok',
                        on_release=lambda x:error_dialog.dismiss(),
                    ),
                ]
            )
            error_dialog.open()
            return
        else:
            self.task_values['Title'] = str(self.t_title)
            self.task_values['Description'] = str(self.t_details)
            self.task_values['Room/Location'] = str(self.t_location)
            self.task_values['Start Date Time'] = datetime.combine(
                self.start_date, self.start_time)
            self.task_values['End Date Time'] = datetime.combine(
                self.end_date, self.end_time)
            self.task_values['Start Date'] = str(
                self.start_date.strftime("%Y - %B - %d"))
            self.task_values['End Date'] = str(
                self.end_date.strftime("%Y - %B - %d"))
            self.task_values['Start Time'] = str(
                self.start_time.strftime("%I:%M:%p"))
            self.task_values['End Time'] = str(
                self.end_time.strftime("%I:%M:%p"))
            self.task_values['Task Category'] = self.t_category
            self.task_values['Reminder'] = self.t_reminder
            # adding new task to the list
            self.task_box = TaskBox()
            self.task_box.tt.text = '{}'.format(
                self.task_values['Title'])
            self.task_box.td.text = 'Task Description ---- {}'.format(
                self.task_values['Description'])
            self.task_box.tl.text = 'Task Location ---- {}'.format(
                self.task_values['Room/Location']
            )
            self.task_box.sd.text = 'Start Date ---- {}'.format(
                self.task_values['Start Date']
            )
            self.task_box.ed.text = 'End Date ---- {}'.format(
                self.task_values['End Date']
            )
            self.task_box.st.text = 'Start Time ---- {}'.format(
                self.task_values['Start Time']
            )
            self.task_box.et.text = 'End Time ---- {}'.format(
                self.task_values['End Time']
            )
            self.task_box.tc.text = 'Category ---- {}'.format(
                self.task_values['Task Category']
            )
            self.task_box.tr.text = 'Reminder ---- {}'.format(
                self.task_values['Reminder']
            )
            Clock.schedule_once(self.reset_inputs, 0)
            # reset everything back to default
            self.t_title = None
            self.t_details = 'None'
            self.t_location = 'None'
            self.start_date = None
            self.end_date = None
            self.start_time = None
            self.end_time = None
            self.t_category = 'None'
            self.t_reminder = 'No reminder'
            self.dd = 0
            self.hh = 0
            self.mm = 0
            # add widget to home screen and return to homescreen
            self.task_list.add_widget(self.task_box)
            self.manager.current = 'home screen'
            self.manager.transition.direction = 'right'
            self.d_check.state = 'normal'
            self.s_date.text = 'YY-MM-DD'
            self.s_time.text = 'HH-MM-AM/PM'
            self.e_date.text = 'End Date'
            self.e_time.text = 'End Time'
            self.dt_reminder.text = 'No Reminder'
            self.dt_category.text = 'None'

    def reset_inputs(self, time):
        self.t_dd.hint_text = 'DD'
        self.t_hh.hint_text = 'HH'
        self.t_mm.hint_text = 'MM'
        self.title.hint_text = 'Title *'
        self.details.hint_text = 'Description'
        self.room.hint_text = 'Room/Location'


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
            text='[color=14FFEC][b]Alert![/b] Are you sure you want to delete task [b]{}[/b] [/color]'.format(
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
        db.remove(qry['Title'] == self.tt.text)
        dialog.dismiss()
        self.parent.remove_widget(self)


class TaskLabel(MDLabel):
    pass


class ErrorDialog(MDDialog):
    radius = [dp(10)]
    md_bg_color = COLOR_CONST['f_ground']


class DBtn(MDRoundFlatButton):
    pass
