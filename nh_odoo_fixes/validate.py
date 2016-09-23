# -*- coding: utf-8 -*-
from datetime import datetime

from openerp.exceptions import ValidationError
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


def not_in_the_future(*args):
    for arg in args:
        not_in_the_future(arg)

def not_in_the_future(date_time):
    if isinstance(date_time, basestring):
        date_time = datetime.strptime(date_time, DTF)
    elif isinstance(date_time, datetime):
        pass
    else:
        raise ValueError("Method only accepts str or datetime objects.")

    now = datetime.now()
    if date_time > now:
        raise ValidationError("Date cannot be in the future.")
