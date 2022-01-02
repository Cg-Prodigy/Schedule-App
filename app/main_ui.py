from datetime import date, datetime, timedelta
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
# kivymd
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.picker import MDDatePicker, MDTimePicker
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFillRoundFlatButton, MDRoundFlatButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.label import MDLabel

# database
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb_serialization import SerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer

# TinyDB

serialization = SerializationMiddleware(JSONStorage)
serialization.register_serializer(DateTimeSerializer(), 'TinyDate')
db = TinyDB('tasks.json', storage=serialization)
qry = Query()


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
            taskbox = TaskBox()
            title = TaskLabel(text='Title : {}'.format(db.all()[i]['Title']))
            sdate = TaskLabel(text='Start Date : {}'.format(
                db.all()[i]['Start Date']))
            edate = TaskLabel(text='End Date : {}'.format(
                db.all()[i]['End Date']))
            stime = TaskLabel(text='Start Time : {}'.format(
                db.all()[i]['Start Time']))
            etime = TaskLabel(text='End Time : {}'.format(
                db.all()[i]['End Time']))
            taskbox.add_widget(title)
            taskbox.add_widget(sdate)
            taskbox.add_widget(edate)
            taskbox.add_widget(stime)
            taskbox.add_widget(etime)
            self.task_list.add_widget(taskbox)

    def home_screen_drop(self, instance):
        item = [
            {
                'text': f'{i}',
                'viewclass': 'OneLineListItem',
                'divider': None,
                'height': dp(40),
                'theme_text_color': 'Custom',
                'text_color': get_color_from_hex('FFD369'),
                'on_release': lambda x=f'{i}': self.pick_selection(x)
            } for i in ['Settings', 'About', 'Share', 'Donate']
        ]
        if not self.h_drop:
            self.h_drop = MDDropdownMenu(
                items=item,
                width_mult=2,
                caller=instance,
                background_color=get_color_from_hex('393E46')
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
    d_category = None
    d_reminder = None
    task_list = ObjectProperty()

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
                    self.t_title = 'None'
                else:
                    self.t_title = str(instance.text).strip().title()
                return
            elif instance.hint_text == 'Description':
                if str(instance.text).strip() == '':
                    self.t_details = 'None'
                else:
                    self.t_details = str(instance.text).strip().title()
                return
            elif instance.hint_text == 'Room/Location':
                if str(instance.text).strip() == '':
                    self.t_location = 'None'
                else:
                    self.t_location = str(instance.text).strip().title()

    # date
    def set_date_today(self, instance):
        if instance.state == 'down':
            self.s_date.text = str(datetime.now().date())
            self.start_date = datetime.now().date()
        else:
            self.s_date.text = 'YY-MM-DD'
            self.start_date = None

    def open_date_dialog(self):
        self.d_check.state = 'normal'
        self.date_picker.bind(on_save=self.get_set_date,
                              on_cancel=self.reset_date)
        self.date_picker.open()

    def get_set_date(self, instance, value, date_range):
        if value < datetime.now().date():
            self.s_date.text = 'Invalid selection. Cannot go back in time.'
            self.start_date = None
        else:
            self.s_date.text = str(value)
            self.start_date = value

    def reset_date(self, instance, value):
        self.s_date.text = 'YY-MM-DD'
    # time

    def open_time_dialog(self):
        time_picker = MDTimePicker(
            am_pm=str(datetime.now().time().strftime('%p')).lower()
        )
        time_picker.set_time(datetime.now().time())
        time_picker.bind(on_save=self.get_set_time,
                         on_cancel=self.reset_time)
        time_picker.open()

    def get_set_time(self, instance, time):
        if self.start_date == None and time < datetime.now().time():
            self.s_time.text = 'Invalid time selection. Cannot go back in time'
            self.start_time = None
        else:
            self.start_time = time
            self.s_time.text = str(self.start_time.strftime("%H:%M:%p"))

    def reset_time(self, *args):
        self.s_time.text = 'HH-MM-AM/PM'

    # end time and date
    def compute_end_datetime(self):
        if not (self.start_date and self.start_time):
            alert = MDDialog(
                title='Error!',
                text='Cannot compute end date or end time without valid start time and start date.',
                buttons=[
                    MDRoundFlatButton(
                        text='Ok', on_release=lambda x: alert.dismiss())
                ],
                radius=[dp(10)]
            )
            alert.open()
        elif self.dd == 0 and self.mm == 0 and self.hh == 0:
            alert = MDDialog(
                title='Error!',
                text='Atlease one field is required to compute the end date and end time',
                buttons=[
                    MDRoundFlatButton(
                        text='Ok', on_release=lambda x: alert.dismiss())
                ],
                radius=[dp(10)]
            )
            alert.open()
        elif self.dd == None or self.mm == None or self.hh == None:
            alert = MDDialog(
                title='Error!',
                text='Invalid entry. Cannot compute end date and end time for the task',
                buttons=[
                    MDRoundFlatButton(
                        text='Ok', on_release=lambda x: alert.dismiss())
                ],
                radius=[dp(10)]
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
                'text_color': get_color_from_hex('FFD369'),
                'on_release': lambda x=f'{i}': self.pick_selection(x, instance)
            } for i in ['Work', 'Family', 'Leisure', 'Personal', 'Business', 'Study']
        ]
        if not self.d_category:
            self.d_category = MDDropdownMenu(
                items=item,
                width_mult=3,
                caller=instance,
                background_color=get_color_from_hex('393E46')
            )
        self.d_category.open()

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
                'text_color': get_color_from_hex('FFD369'),
                'on_release': lambda x=f'{i}': self.pick_reminder(x, instance)
            } for i in ['No reminder',
                        'On Time',
                        '5 minutes before time',
                        '10 minutes before time', '15 minutes before time'
                        ]
        ]
        if not self.d_reminder:
            self.d_reminder = MDDropdownMenu(
                items=item,
                width_mult=4,
                caller=instance,
                background_color=get_color_from_hex('393E46')
            )
        self.d_reminder.open()

    def pick_reminder(self, value, instance):
        instance.text = value
        self.t_category = value
        self.d_reminder.dismiss()

    #  final validation
    def validate_task_values(self):
        if not(self.t_title and self.start_date and self.start_time):
            error_dialog = MDDialog(
                title='Error',
                text='Unsuccesful. Please Review task details and correct the errors',
                buttons=[
                    MDRoundFlatButton(
                        text='Ok',
                        on_release=lambda x:error_dialog.dismiss()
                    ),
                ]
            )
            error_dialog.open()
            return
        elif db.search(qry['Title'] == self.t_title):
            error_dialog = MDDialog(
                title='Error',
                text='Unsuccesful. A task with the same title already exists',
                buttons=[
                    MDRoundFlatButton(
                        text='Ok',
                        on_release=lambda x:error_dialog.dismiss()
                    ),
                ]
            )
            error_dialog.open()
            return
        else:
            self.task_values['Title'] = self.t_title
            self.task_values['Description'] = self.t_details
            self.task_values['Room/Location'] = self.t_location
            self.task_values['Start Date Time'] = datetime.combine(
                self.start_date, self.start_time)
            self.task_values['End Date Time'] = datetime.combine(
                self.end_date, self.end_time)
            self.task_values['Start Date'] = str(self.start_date)
            self.task_values['End Date'] = str(self.end_date)
            self.task_values['Start Time'] = str(self.start_time)
            self.task_values['End Time'] = str(self.end_time)
            self.task_values['Task Category'] = self.t_category
            self.task_values['Reminder'] = self.t_reminder
            db.insert(self.task_values)
            taskbox = TaskBox()
            title = TaskLabel(
                text='Title : {}'.format(self.task_values['Title']))
            sdate = TaskLabel(text='Start Date : {}'.format(
                self.task_values['Start Date']))
            edate = TaskLabel(text='End Date : {}'.format(
                self.task_values['End Date']))
            stime = TaskLabel(text='Start Time : {}'.format(
                self.task_values['Start Time']))
            etime = TaskLabel(text='End Time : {}'.format(
                self.task_values['End Time']))
            taskbox.add_widget(title)
            taskbox.add_widget(sdate)
            taskbox.add_widget(edate)
            taskbox.add_widget(stime)
            taskbox.add_widget(etime)
            self.task_list.add_widget(taskbox)
            self.manager.current = 'home screen'
            self.manager.transition.direction = 'right'


class TaskBox(MDBoxLayout):
    pass


class TaskLabel(MDLabel):
    pass
