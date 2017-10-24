import web
from antislapp import index


class Debug:
    def __init__(self):
        pass

    def GET(self):
        env = web.ctx.env
        self_vars = self.__dict__.copy()
        l_session = dict(index.session)
        l_session['status'] = "Session variable is working correctly" if 'session_id' in index.session else "Session is not working."
        config = dict(web.config)
        context = web.ctx

        return index.render.debug(sorted, env, self_vars, l_session, config, context)