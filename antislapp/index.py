#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import web
BASE_FOLDER = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_FOLDER, 'sessions', 'sqlite.db')
if not os.path.exists(os.path.dirname(DB_PATH)):
    os.makedirs(os.path.dirname(DB_PATH))
sys.path.append(os.path.join(BASE_FOLDER, os.path.pardir))  # this could be executed from any directory


def parse_sql_string(script, replacements):
    # break into lines
    lines = script.splitlines(True)
    # remove comment lines
    lines = [i for i in lines if not i.startswith("--")]
    # join into one long string
    script = " ".join(lines)
    # do any necessary string replacements
    if replacements:
        script = script.format(**replacements)
    # split string into a list of commands
    commands = script.split(";")
    # ignore empty statements (like trailing newlines)
    commands = filter(lambda x: bool(x.strip()), commands)
    return commands


def parse_sql_file(path, replacements):
    with open(path, 'r') as f:
        sql = f.read()
    return parse_sql_string(sql, replacements)


def join_list(items):
    count = len(items)
    if count == 0:
        joined = ''
    elif count == 1:
        joined = items[0]
    elif count == 2:
        joined = "{} and {}".format(*items)
    else:
        joined = "{}, and {}".format(", ".join(items[:-1]), items[-1])
    return joined


urls = ("/fulfill", "pages.fulfill.Fulfill",
        "/converse", "pages.converse.Converse",
#        "/debug", "pages.debug.Debug",
        "/.*", "pages.home.Home")
app = web.application(urls, globals())
render = web.template.render(os.path.join(BASE_FOLDER, 'templates'))

# session
web.config.session_parameters['cookie_path'] = "/"
old_debug = web.config.debug
web.config.debug = False  # to quiet stderr output
db = web.database(dbn='sqlite', db=DB_PATH)
web.config.debug = old_debug
del old_debug
for command in parse_sql_file(os.path.join(BASE_FOLDER, 'tables.sql'), {}):
    db.query(command)


if web.config.get('_session') is None:
    # session_store = web.session.DiskStore(os.path.join(BASE_FOLDER, 'sessions'))
    session_store = web.session.DBStore(db, 'sessions')
    session = web.session.Session(app, session_store, initializer={'count': 0})
    web.config._session = session
else:
    session = web.config._session

if __name__ == "__main__":
    try:
        web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
        app.run()
    except:
        web.runwsgi(app.wsgifunc())
