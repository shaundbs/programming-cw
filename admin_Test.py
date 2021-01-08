import logging
import sys
import os
import re

from admin_func.admin import Admin
from patient_func.patients import Patient
from gp_func.gp import Gp
from patient_func.patient_database import Database
import bcrypt
import cli_ui as ui

if __name__ == "__main__":
    Admin(2)