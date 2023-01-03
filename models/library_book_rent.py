from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _

class LibraryBookRent(models.Model):
    _name = 'library.book.rent'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    book_id = fields.Many2one('library.book', 'Book', required=True)
    borrower_id = fields.Many2one('res.partner', 'Borrower',
    required=True)
    state = fields.Selection([('ongoing', 'Ongoing'),
                            ('returned', 'Returned'),('lost', 'Lost')],
                            'State', default='ongoing',
                            required=True)
    rent_date = fields.Date(default=fields.Date.today)
    return_date = fields.Date()
    expected_return_date = fields.Date()

    def book_return(self):
        self.ensure_one()
        #self.book_id.make_available()
        self.write({'state': 'returned', 'return_date': fields.Date.today()})

    #管理员在图书表单视图中报告为遗失时，图书记录的状态会变为 lost，书会被存档。
    #普通用户在租借记录中报告图书为遗失时，记录状态会变为 lost，图书不会存档，这样管理员可以稍后查看。
    def book_lost(self):
        self.ensure_one()
        self.state = 'lost'
        book_with_different_context = self.book_id.with_context(avoid_deactivate=True)
        book_with_different_context.make_lost()