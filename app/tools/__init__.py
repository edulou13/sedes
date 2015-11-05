#-*- coding: utf-8 -*-
from .url_handler import (url_handlers, Route as route)
from .shortcuts import (UTC as utc, CustomDict as cdict, BaseHandler, Modem, getLocals)
__all__ = ['url_handlers','route', 'utc','cdict','BaseHandler','Modem','getLocals']