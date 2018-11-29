import os, pickle, random
os.environ
from lib.create_db import Street
from kivy.app import App
from kivy.metrics import dp
from kivy.uix.carousel import Carousel
from kivy.uix.pagelayout import PageLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.graphics import Rectangle, Quad
from kivy.properties import ListProperty, ObjectProperty, StringProperty,\
                            NumericProperty, ReferenceListProperty
from kivy.animation import Animation
from kivy.clock import Clock
from functools import partial

PERCENTAGE = 0.3
MINIMUM = 2
TEMPLATE = "[size={f_size}]{start}-{stop}[/size] {street} {type}"
DB_PATH = '.\\routes.pickle'
WIDTH = '600'
HEIGHT = '900'
RIB_PAD = 20
MARGIN = 30
SLIDEOUTDUR = 1.5
SLIDEINDUR = .2
COL_TEXT_FRONT = (225/255, 96/255, 54/255)
COL_FLASH = (255/255,236/255,145/255)
COL_BACK_FLASH  = (77/255, 47/255, 89/255)
COL_TOP = (255/255, 248/255, 214/255)
COL_BACK = (35/255, 1/255, 21/255)
COL_BTN_UP = (107/255, 124/255, 124/255)

with open(DB_PATH, 'rb') as f:
    database = pickle.load(f)

from kivy.config import Config
Config.set('graphics', 'width', WIDTH)
Config.set('graphics', 'height', HEIGHT)

class MainView(Carousel):
    deckview = ObjectProperty(None)
    optionview = ObjectProperty(None)
    pages = ListProperty()
    total_pages = NumericProperty(1)
    current_page = NumericProperty(0)
    page_info = ReferenceListProperty(current_page, total_pages)

    def parse_selected(self):
        selected = []
        for child in self.optionview.optiongrid.children:
            if child.state == 'down':
                selected.append(child.text)
        return selected

    def parse_streets(self, crids):
        for crid in crids:
            streetlist = (street for street in database[crid])
            for street in streetlist:
                yield street

    def scramble(self, str):
        pass

    def add_chars(self, charlist, str, start):
        for char in str:
            charlist.append(char)
            return start+len(str)-1

    def find_whitespace(self, filter, start, str):
        i = str.find(' ',start)
        if i != -1:
            filter.append(i)
            if i <= len(str)-1:
                self.find_whitespace(filter, i+1, str)


    def add_to_pages(self, pages, items, perpage):
        indicesrange = [i for i in range(0,len(items)-1,perpage)]
        if len(indicesrange) == 0 or indicesrange[-1] < len(items)-1:
            indicesrange.append(len(items)-1)
        if indicesrange[-1] == indicesrange[-2]:
            indicesrange.pop()
            
        print(indicesrange)
        lasti = 0
        indices = []
        for i in indicesrange[1:]:
            indices.append((lasti, i))
            lasti = i
        print(indices)
        for start, stop in indices:
            page = items[start:stop+1]
            print('appending', page)
            pages.append(page)

        ###
        #indices = []
        #lasti = 0
        #endi = len(items)-1
        #for i in range(0,len(items),perpage):
        #    end = i if i <= endi else endi
        #    indices.append((lasti, i))
        #    lasti = i
        #for start, stop in indices:
#
#            page = [item for item in items[start:stop]]
#            pages.append(page)

    def write_deck(self):
        selected = self.parse_selected()
        app = App.get_running_app()
        perpage = len(app.root.deckview.deck.children)
        if (self.optionview.focus_btn.state == 'down') and (
                len(selected) > 0):
            app.root.pages = []
            items = []
            streets = [st for st in self.parse_streets(selected)]
            streets.sort(key=lambda st: st.name)
            for street in streets:
                template = "{start}-{stop} {name} {type}"
                filled = template.format(
                    start = street.start,
                    stop = street.stop,
                    name = street.name,
                    type = street.type
                )
                filled = filled.strip('- ')
                filled = filled.rstrip()
                filter = []
                self.find_whitespace( filter, 0, filled)
                hidden = ['*' for char in filled]
                hidden_chars = int(PERCENTAGE * len(filled))
                if hidden_chars < MINIMUM:
                    hidden_chars = MINIMUM
                revealed_indexes = random.sample(
                    [i for i in range(0,len(filled)) if
                     i not in filter],
                    hidden_chars)
                for index in revealed_indexes:
                    hidden[index] = filled[index]
                for index in filter:
                    hidden[index] = '  '
                hidden = ''.join(hidden)
                item = (filled, hidden)
                items.append(item)
            self.add_to_pages(app.root.pages, items, perpage)
        elif self.optionview.focus_btn.state == 'down':
            pass

    def on_pages(self, obj, event):
        if len(self.pages) != 0:
            self.total_pages = len(self.pages)
            self.deckview.deck.load_page(self.current_page)

class DeckScreen(BoxLayout):
    deck = ObjectProperty(None)

class DeckLayout(BoxLayout):
    reset = Animation(x=10,duration=.2)

    def load_page(self, pagenum):
        app = App.get_running_app()
        blank = ['','']
        page = app.root.pages[pagenum]
        diff = len(self.children)-len(page)
        for i in range(0,diff):
            page.append(blank)
        for child, item in zip(self.children[::-1], page):
            child.front_text = item[1]
            child.back_text = item[0]
        app.root.deckview.deck.cycle_ribbons()

    def create_deck(self):
        Clock.schedule_once(self.filling_deck)

    def trimming_deck(self, dt):
        self.remove_widget(self.children[-1])
        if self.children[-1].top > self.parent.top:
            Clock.schedule_once(self.trimming_deck)
            pass

    def filling_deck(self, dt):
        self.add_widget(Card())
        if self.children[-1].top > self.parent.top:
            Clock.schedule_once(self.trimming_deck)
        else:
            Clock.schedule_once(self.filling_deck)

            #if self.minimum_height > self.parent.height:
            #    self.remove_widget(self.children[-1])

    def call_animation(self, wgt, *largs):
        Animation.cancel_all(wgt)
        for rib in wgt.children:
            Animation.cancel_all(rib)
        self.reset.start(wgt)

    def cycle_ribbons(self):
        delay_offset = 0.05
        delay = 0
        for wgt in self.children[::-1]:
            wgt.x = self.right - MARGIN
            wgt.revealed = False
            Clock.schedule_once(partial(self.call_animation, wgt),delay)
            delay += delay_offset


class StatusBar(BoxLayout):
    pass

class Card(ButtonBehavior, Widget):
    front_ribbon = ObjectProperty(None)
    back_ribbon = ObjectProperty(None)
    front_text = StringProperty('')
    back_text = StringProperty('')
    revealed = False
    #rest = Animation(x=self.right + 30)
    #extend = Animation(x=self.pos[0])

    def do_flash(self, target, col, revert=False):
        if target == 'front':
            if not revert:
                self.front_ribbon.rib_color = col
                Clock.schedule_once(lambda dt: 
                                    self.do_flash('front', COL_TOP,revert=True),
                                    .1)
            else:
                self.front_ribbon.rib_color = col
        elif target == 'back':
            if not revert:
                self.back_ribbon.rib_color = col
                Clock.schedule_once(lambda dt:
                                    self.do_flash('back',COL_BACK, revert=True),
                                    .1)
            else:
                self.back_ribbon.rib_color = col


    def on_press(self):
        if not self.revealed:
            Animation.cancel_all(self.front_ribbon)
            self.do_flash('front', COL_FLASH)
            self.retract.start(self.front_ribbon)
#            self.front_ribbon.retract()
            self.revealed = True
        else:
#            self.front_ribbon.extend()
            Animation.cancel_all(self.front_ribbon)
            self.do_flash('back', COL_BACK_FLASH)
            self.extend.start(self.front_ribbon)
            self.revealed = False

    def update_anim(self):
        self.retract = Animation(x=self.right-MARGIN,
                                 duration=SLIDEOUTDUR,
                                 t='out_elastic')
        self.extend = Animation(x=self.pos[0]+RIB_PAD,
                                duration=SLIDEINDUR)

    def on_pos(self, instance, value):
        self.update_anim()

    def on_size(self, instance, value):
        self.update_anim()

class Ribbon(Widget):
    rib_label = ObjectProperty(None)
    rib_color = ListProperty([1,1,1])
    text_color = ListProperty([1,1,1])
    text = StringProperty('Testing')
    alignment = StringProperty('right')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = kwargs.get('text', 'Testing')

class PageButton(ButtonBehavior, Widget):
    btn_color = ListProperty([1,1,1])

    def on_press(self):
        self.do_flash()

    def stop_flash(self):
        self.btn_color = COL_TEXT_FRONT

    def do_flash(self):
        self.btn_color = COL_FLASH
        Clock.schedule_once(lambda dt: self.stop_flash(),.2)

class UtilityWidget(BoxLayout):

    def do_action(self):
        pass

class UtilitySelect(UtilityWidget):

    def do_action(self):
        app = App.get_running_app()
        app.root.optionview.optiongrid.select_all()

class UtilityDeselect(UtilityWidget):

    def do_action(self):
        self.parent.parent.optiongrid.deselect_all()

class UtilityButton(ButtonBehavior, Widget):
    bevel = NumericProperty(10)
    bevel_out = Animation(bevel=0,
                          btn_color=COL_TEXT_FRONT,
                          duration=.2)
    bevel_in = Animation(bevel=10,
                         btn_color=COL_BTN_UP,
                         duration=.2)
    btn_color = ListProperty(COL_BTN_UP)

    def __init__(self, *largs, **kwrds):
        super().__init__(*largs, **kwrds)
        self.bevel_out.bind(on_complete=self.out_complete)

    def pressed(self):
        self.bevel_out.start(self)

    def out_complete(self, anim, widget):
        self.bevel_in.start(self)

class LPageButton(PageButton):

    def cycle_left(self, root):
        root.current_page -= 1
        if root.current_page < 0:
            root.current_page = root.total_pages-1
        root.deckview.deck.load_page(root.current_page)

class RPageButton(PageButton):

    def cycle_right(self, root):
        root.current_page += 1
        if root.current_page > root.total_pages-1:
            root.current_page = 0
        root.deckview.deck.load_page(root.current_page)

class OptionsScreen(BoxLayout):
    optiongrid = ObjectProperty(None)
    focus_btn = ObjectProperty(None)
    quiz_btn = ObjectProperty(None)

    def on_optiongrid(self, event, obj):
        db_keys = list(database.keys())
        db_keys.sort()
        for crid in db_keys:
            self.optiongrid.add_widget(ModeButton(text=crid,group='crid'))

    def set_group(self, state):
        if state == 'normal':
            pass
        for child in self.optiongrid.children:
            child.state = 'normal'
            child.group = 'crid'

    def unset_group(self, state):
        if state == 'normal':
            pass
        for child in self.optiongrid.children:
            child.group = None

class OptionsGrid(GridLayout):

    def deselect_all(self):
        for child in self.children:
            child.state = 'normal'

    def select_all(self):
        app = App.get_running_app()
        if app.root.optionview.focus_btn.state != 'down':
            for child in self.children:
                child.state = 'down'

class PageLabel(Label):
    pass

class Spacer(Widget):
    pass

class SchemeApp(App):

    def build(self):
        main = MainView()
        main.deckview.deck.create_deck()
        return main

class ModeButton(ToggleButton):
    def handle_state(self):
        if self.state == 'normal':
            self.background_color = (COL_BTN_UP[0], COL_BTN_UP[1],
                                     COL_BTN_UP[2], 1)
        else:
            self.background_color = (COL_TEXT_FRONT[0], COL_TEXT_FRONT[1],
                                     COL_TEXT_FRONT[2], 1)
if __name__ == '__main__':
    SchemeApp().run()
