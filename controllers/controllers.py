from odoo import http
from odoo.http import request

class Main(http.Controller):
    @http.route(['/my_library/books'], type='http', auth='public')
    def books(self):
        books = request.env['library.book'].sudo().search([])
        html_result = '<html><body><ul>'
        for book in books:
            html_result += "<li> %s </li>" % book.name
        html_result += '</ul></body></html>'
        return html_result


    @http.route('/my_library/books/json', type='json', auth='public')
    def books_json(self):
        records = request.env['library.book'].sudo().search([])
        return records.read(['name'])

# -*- coding: utf-8 -*-
# from odoo import http


# class MyLibrary(http.Controller):
#     @http.route('/my_library/my_library', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/my_library/my_library/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('my_library.listing', {
#             'root': '/my_library/my_library',
#             'objects': http.request.env['my_library.my_library'].search([]),
#         })

#     @http.route('/my_library/my_library/objects/<model("my_library.my_library"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('my_library.object', {
#             'object': obj
#         })
