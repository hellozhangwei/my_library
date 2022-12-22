from odoo import models, fields, api
from odoo.exceptions import ValidationError

class BaseArchive(models.AbstractModel):
    _name = 'base.archive'
    active = fields.Boolean(default=True)

    def do_archive(self):
        for record in self:
            record.active = not record.active

class BookCategory(models.Model):
    _name = 'library.book.category'
    _inherit = ['base.archive']
    name = fields.Char('Category Name')
    description = fields.Text(' Category Description')
    parent_id = fields.Many2one('library.book.category', string='Parent Category', ondelete='restrict', index=True)

    #By convention, One2many fields have the _ids suffix.
    child_ids = fields.One2many('library.book.category', 'parent_id', string='Child Categories')

    _parent_store = True
    _parent_name = "parent_id"  # optional if field is 'parent_id'
    parent_path = fields.Char(index=True)

    @api.constrains('parent_id')
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise models.ValidationError('Error! You cannot create recursive categories.')