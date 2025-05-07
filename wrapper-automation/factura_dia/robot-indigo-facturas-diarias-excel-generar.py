from dotenv import load_dotenv
import os
import sys
# Get the absolute path of the parent folder
parent_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Add the parent folder to sys.path
sys.path.append(parent_folder)
import pyautogui
from core import robotClick
import time
from pywinauto import Application
from datetime import datetime
import uiautomation as auto
import mysql.connector
import subprocess

