import os
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps


def MagerDicts(dict1, dict2):
    if isinstance(dict1, list) and isinstance(dict2, list):
        return dict1 + dict2
    elif isinstance(dict1, dict) and isinstance(dict2, dict):
        return dict(list(dict.items())+ list(dict2.items()))
    else:
        return False



def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
"""
def usd_value_API(self):
    # API for Dolar Blue
    URL = 'https://www.dolarsi.com/api/api.php?type=valoresprincipales'
    json = requests.get(URL).json()

    for index, emoji in enumerate(('🟢', '🔵')):
        compra = json[index]['casa']['compra'][:-1]
        venta = json[index]['casa']['venta'][:-1]

    return {
        "compra": json[index]['casa']['compra'][:-1],
        "venta": venta = json[index]['casa']['venta'][:-1]
    } 
    compra, venta
"""