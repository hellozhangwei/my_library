from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _

class LibraryBookRent(models.Model):
    _name = 'library.book.rent'

    book_id = fields.Many2one('library.book', 'Book', required=True)
    borrower_id = fields.Many2one('res.partner', 'Borrower',
    required=True)
    state = fields.Selection([('ongoing', 'Ongoing'),
                            ('returned', 'Returned')],
                            'State', default='ongoing',
                            required=True)
    rent_date = fields.Date(default=fields.Date.today)
    return_date = fields.Date()

    def book_return(self):
        self.ensure_one()
        self.book_id.make_available()
        self.write({'state': 'returned', 'return_date': fields.Date.today()})