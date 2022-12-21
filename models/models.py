# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class my_library(models.Model):
#     _name = 'my_library.my_library'
#     _description = 'my_library.my_library'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100


from odoo import models, fields

class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'
    _order = 'date_release desc, name'
    _rec_name = 'short_name' #this is over write by name_get
    name = fields.Char('Title', required=True)
    short_name = fields.Char('Short Title', required=True, translate=True, index=True)
    date_release = fields.Date('Release Date')
    author_ids = fields.Many2many('res.partner', string='Authors')
    notes = fields.Text('Internal Notes')

    #need to restart odoo
    state = fields.Selection([('draft', 'Not Available'), ('available', 'Available'), ('lost', 'Lost')], 'State', default="draft")
    description = fields.Html('Description', sanitize=True, strip_style=False)
    cover = fields.Binary('Book Cover')
    out_of_print = fields.Boolean('Out of Print?')
    date_updated = fields.Datetime('Last Updated')
    pages = fields.Integer('Number of Pages', groups='base.group_user', states={'lost': [('readonly', True)]}, help='Total book page count', company_dependent=False)
    reader_rating = fields.Float('Reader Average Rating', digits=(14, 4)) # Optional precision (total, decimals)

    #用于对记录启用存档/取消存档功能
    active = fields.Boolean('Active', default=True)

    cost_price = fields.Float('Book Cost', digits='Book Price')
    currency_id = fields.Many2one('res.currency', string='Currency')
    retail_price = fields.Monetary('Retail Price', currency_field='currency_id',)

    publisher_id = fields.Many2one(
        'res.partner', string='Publisher',
        # optional:
        ondelete='set null',
        context={},
        domain=[],
    )

    #need to restart odoo to pick up name_get
    def name_get(self):
        result = []
        for record in self:
            rec_name = "%s (%s)" % (record.name, record.date_release)
            result.append((record.id, rec_name))
        return result

    class ResPartner(models.Model):
        _inherit = 'res.partner'
        published_book_ids = fields.One2many('library.book', 'publisher_id', string='Published Books')