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


from odoo import models, fields, api
from datetime import timedelta

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

    #此处设置关联字段为只读，如果不这么做，字段将为可写，用户可能会修改其值。
    #关联字段实际上是计算字段，作为一个计算字段，意味着也可以使用store属性
    publisher_city = fields.Char(
        'Publisher City',
        related='publisher_id.city',
        readonly=True)

    category_id = fields.Many2one('library.book.category')

    #need to restart odoo to pick up name_get
    def name_get(self):
        result = []
        for record in self:
            rec_name = "%s (%s)" % (record.name, record.date_release)
            result.append((record.id, rec_name))
        return result

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Book title must be unique.'),
        ('positive_page', 'CHECK(pages>0)', 'No. of pages must be positive')
    ]

    @api.constrains('date_release')
    def _check_release_date(self):
        for record in self:
            if record.date_release and record.date_release > fields.Date.today():
                raise models.ValidationError('Release date must be in the past')

    age_days = fields.Float(
        string='Days Since Release',
        compute='_compute_age',
        inverse='_inverse_age',
        search='_search_age',
        store=False,  # optional 如果store=True，计算后字段值会存储到数据库中，借助@api.depends装饰器，ORM会知道何时需要重新计算并更新这些存储值。你可以把它看作一个持久缓存。如果在计算字段中使用store=True，则无需实再现search方法
        compute_sudo=False  # optional
    )

    #@depends装饰器来监测缓存值何时置为无效并重新计算
    @api.depends('date_release')
    def _compute_age(self):
        today = fields.Date.today()
        for book in self:
            if book.date_release:
                delta = today - book.date_release
                book.age_days = delta.days
            else:
                book.age_days = 0

    #计算字段的写操作通过实现inverse函数来添加，inverse是可选属性，如果不想让该计算字段可编辑，可以忽略它。
    def _inverse_age(self):
        today = fields.Date.today()
        for book in self.filtered('date_release'):
            d = today - timedelta(days=book.age_days)
            book.date_release = d

    def _search_age(self, operator, value):
        today = fields.Date.today()
        value_days = timedelta(days=value)
        value_date = today - value_days
        # 运算符转换：
        # age_days > value -> date < value_date
        operator_map = {
            '>': '<', '>=': '<=',
            '<': '>', '<=': '>=',
        }
        new_op = operator_map.get(operator, operator)
        return [('date_release', new_op, value_date)]

    class ResPartner(models.Model):
        _inherit = 'res.partner'
        published_book_ids = fields.One2many('library.book', 'publisher_id', string='Published Books')