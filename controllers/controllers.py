# -*- coding: utf-8 -*-
from odoo import http

# class SmgCreateUser(http.Controller):
#     @http.route('/smg_create_user/smg_create_user/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/smg_create_user/smg_create_user/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('smg_create_user.listing', {
#             'root': '/smg_create_user/smg_create_user',
#             'objects': http.request.env['smg_create_user.smg_create_user'].search([]),
#         })

#     @http.route('/smg_create_user/smg_create_user/objects/<model("smg_create_user.smg_create_user"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('smg_create_user.object', {
#             'object': obj
#         })