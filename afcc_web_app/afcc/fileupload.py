import os
import pandas as pd

from flask import request
from flask import redirect
from flask import url_for

from flask import jsonify
from flask import Blueprint
from flask import render_template

from afcc import maproutes
from afcc import data_conversion

fileupload_bp = Blueprint("fileupload", __name__, url_prefix='/fileupload', template_folder='templates', static_folder='static')
