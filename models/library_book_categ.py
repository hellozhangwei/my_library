from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

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
        _logger.info('==========_check_hierarchy==update===2==========')
        if not self._check_recursion():
            raise models.ValidationError('Error! You cannot create recursive categories.')

    def create_categories(self):
        categ1 = {
            'name': 'Child category 1',
            'description': 'Description for child 1'
        }

        categ2 = {
            'name': 'Child category 2',
            'description': 'Description for child 2'
        }

        parent_category_val = {
            'name': 'Parent category',
            'description': 'Description for parent category',
            'child_ids': [
                (0, 0, categ1),
                (0, 0, categ2),
            ]
        }

        record = self.env['library.book.category'].create(parent_category_val)