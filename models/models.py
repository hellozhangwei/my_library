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
from odoo.exceptions import UserError
from odoo.tools.translate import _

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
    state = fields.Selection([
                                ('draft', 'Not Available'),
                                ('available', 'Available'),
                                ('lost', 'Lost'),
                                ('borrowed', 'Borrowed'),
                              ],
                             'State', default="draft")
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

    #在编写一个新方法时，如果不使用装饰器，方法会对记录集执行。
    #@api.model类似于Python的@classmethod
    #api.model is used when you need to do something with model itself and don't need to modify/check some model's record/records.
    @api.model
    def is_allowed_transition(self, old_state, new_state):
        allowed = [('draft', 'available'),
                   ('available', 'borrowed'),
                   ('borrowed', 'available'),
                   ('available', 'lost'),
                   ('borrowed', 'lost'),
                   ('lost', 'available')]
        return (old_state, new_state) in allowed

    #For multiple records api.multi is used, where self is recordset and it can be iterated through all records to do something
    #@api.multi #'multi' is removed from Odoo 13.0 as it will be default
    def change_state(self, new_state):
        for book in self:
            if book.is_allowed_transition(book.state, new_state):
                book.state = new_state
            else:
                msg = _('Moving from %s to %s is not allowed') % (book.state, new_state)
                raise UserError(msg)

    # The following two are equivalent:
    # @api.one
    # def _compute_name(self):
    #     self.name = "Default Name"
    #
    # @api.multi
    # def print_self_multi(self):
    #     for record in self:
    #         record.name = "Default Name"

    def make_available(self):
        self.change_state('available')

    def make_borrowed(self):
        self.change_state('borrowed')

    def make_lost(self):
        self.change_state('lost')

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

    @api.model
    def _referencable_models(self):
        models = self.env['ir.model'].search([
            ('field_id.name', '=', 'message_ids')])
        return [(x.model, x.name) for x in models]

    ref_doc_id = fields.Reference(
        selection='_referencable_models',
        string='Reference Document')

    def log_all_library_members(self):
        library_member_model = self.env['library.member']  # 这是library.member的空记录集
        all_members = library_member_model.search([])
        print('ALL MEMBERS:', all_members)
        return True

    """
    Create Method: The create method creates new records. It takes a dictionary of values, applies any defaults we have specified and then inserts the record an returns the new ID.

    New Method: Return a new record instance attached to the current environment and initialized with the provided `value`. The record is *not* created in database, it only exists in memory.
    
    **************************************************************************************
    
    Write Method:The write method updates existing records. It takes a dictionary of values and applies to all of the ids you pass. 
    if you pass a list of ids, the values will be written to all ids. For updating a single record, pass a list of one entry, 
    if you want to do different updates to the records, you have to do multiple write calls. You can also manage related fields with a write.
    
    Update Method: Write do not work for records set which are not present in the database. Onchange method returns pseudo-records which do not exist in the database yet. 
    So set record's field using update() method as calling write() method gives an undefined behavior.
    """
    def change_release_date(self):
        self.ensure_one()
        self.date_release = fields.Date.today()
        # 或者用下面代码
        # self.update({
        #     'date_release': fields.Date.today()
        # })

    class ResPartner(models.Model):
        _inherit = 'res.partner'
        published_book_ids = fields.One2many('library.book', 'publisher_id', string='Published Books')

        authored_book_ids = fields.Many2many('library.book', string='Authored Books')
        count_books = fields.Integer('Number of Authored Books', compute='_compute_count_books')

        @api.depends('authored_book_ids')
        def _compute_count_books(self):
            for r in self:
                r.count_books = len(r.authored_book_ids)

    #原型继承，但在实践中鲜有使用, 此模型有其自己的数据表
    # class LibraryMember(models.Model):
    #     _inherit = 'res.partner'
    #     _name = 'library.member'

    #代理继承, _inherits, 根据已有模型创建一个新模型。它还支持多态继承，可以继承两个其它的模型。
    #图书会员，我们需要Partner模型中的所有身份和地址数据，也想保留一些有关会员的信息：起始日期、结束日期和会员卡号。
    #向Partner模型添加这些字段不是最好的方案，因为对于非会员的成员们无需使用到这些。使用一个带有额外字段的新模型继承Partner模型则会非常好。
    #会员记录自动关联到一个新的Partner记录。它仅是一个 many-to-one关联，但代理机制注入了一些魔力来让Partner的字段看起来就好像属于Member的记录一样，新的Partner记录会自动和新的会员记录一同创建。
    class LibraryMember(models.Model):
        _name = 'library.member'
        _inherits = {'res.partner': 'partner_id'}
        partner_id = fields.Many2one('res.partner', ondelete='cascade')

        date_start = fields.Date('Member Since')
        date_end = fields.Date('Termination Date')
        member_number = fields.Char()
        date_of_birth = fields.Date('Date of birth')

    #继承代理有一个快捷方式。代替创建一个_inherits字典，可以在Many2one字段定义中使用delegate=True属性。
    #关于代理继承一个值得注意的用例是用户模型 res.users。它继承自成员（res.partner）!!!
    # class LibraryMember(models.Model):
    #     _name = 'library.member'
    #     partner_id = fields.Many2one('res.partner', ondelete='cascade', delegate=True)
    #     date_start = fields.Date('Member Since')
    #     date_end = fields.Date('Termination Date')
    #     member_number = fields.Char()
    #     date_of_birth = fields.Date('Date of birth')