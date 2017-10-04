#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import web
BASE_FOLDER = os.path.dirname(__file__)
sys.path.append(os.path.join(BASE_FOLDER, os.path.pardir))  # this could be executed from any directory


urls = ("/fulfill", "pages.fulfill.Fulfill",
        "/.*", "pages.debug.Debug")
app = web.application(urls, globals())
render = web.template.render(os.path.join(BASE_FOLDER, 'templates'))
web.config.session_parameters['cookie_path'] = "/"

if web.config.get('_session') is None:
    session_store = web.session.DiskStore(os.path.join(BASE_FOLDER, 'sessions'))
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
