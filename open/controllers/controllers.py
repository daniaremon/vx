# -*- coding: utf-8 -*-
from odoo import http

# class Open(http.Controller):
#     @http.route('/open/open/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/open/open/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('open.listing', {
#             'root': '/open/open',
#             'objects': http.request.env['open.open'].search([]),
#         })

#     @http.route('/open/open/objects/<model("open.open"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('open.object', {
#             'object': obj
#         })