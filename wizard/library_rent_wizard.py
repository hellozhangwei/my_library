from odoo import models, fields

# TransientModel只存在如下的变化：
# 1. 记录在数据库中会定时地删除，因此临时模型的数据表不会随时间不停增大。
# 2. 在引用普通模型的TransientModel实例中不能定义One2many字段，因为这将在持久化模型中添加关联到临时数据的列。在这种情况下使用Many2many关联。当然，可以在临时模型之间定义Many2one和One2many字段关联。
class LibraryRentWizard(models.TransientModel):
    _name = 'library.rent.wizard'
    borrower_id = fields.Many2one('res.partner', string='Borrower')
    book_ids = fields.Many2many('library.book', string='Books')

    def add_book_rents(self):
        rentModel = self.env['library.book.rent']
        for wiz in self:
            for book in wiz.book_ids:
                rentModel.create({
                  'borrower_id': wiz.borrower_id.id,
                  'book_id': book.id
                })

        members = self.mapped('borrower_id')
        action = members.get_formview_action()
        if len(members.ids) > 1:
            action['domain'] = [('id', 'in', tuple(members.ids))]
            action['view_mode'] = 'tree,form'
        return action