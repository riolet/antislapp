#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import web
BASE_FOLDER = os.path.dirname(__file__)


urls = ("/fulfill", "pages.fulfill.Fulfill",
        "/.*", "pages.debug.Debug")
app = web.application(urls, globals())
render = web.template.render(os.path.join(BASE_FOLDER, 'templates'))
web.config.session_parameters['cookie_path'] = "/"

if web.config.get('_session') is None:
    session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'count': 0})
    web.config._session = session
else:
    session = web.config._session

if __name__ == "__main__":
    try:
        web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
        app.run()
    except:
        web.runwsgi(app.wsgifunc())
