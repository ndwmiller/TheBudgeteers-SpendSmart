from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import StringProperty
import os


Builder.load_file(os.path.abspath(os.path.dirname(os.path.abspath(__file__))) + '\\goals_screen.kv')