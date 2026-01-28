from odoo import models, fields, api


class CustomerVanBan(models.Model):
    """Extend Customer để thêm liên kết với Văn bản - Số hóa hồ sơ"""
    _inherit = 'customer'

    # Liên kết với văn bản (Số hóa hồ sơ tập trung)
    van_ban_ids = fields.One2many('van_ban', inverse_name='customer_id', string="Hồ sơ văn bản")
    
    # Thống kê văn bản
    total_van_ban = fields.Integer("Tổng số văn bản", compute="_compute_total_van_ban", store=True)

    @api.depends('van_ban_ids')
    def _compute_total_van_ban(self):
        for record in self:
            record.total_van_ban = len(record.van_ban_ids)

    def action_view_van_ban(self):
        """Xem tất cả văn bản của khách hàng"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Hồ sơ văn bản - ' + (self.customer_name or ''),
            'res_model': 'van_ban',
            'view_mode': 'tree,form,kanban',
            'domain': [('customer_id', '=', self.id)],
            'context': {
                'default_customer_id': self.id,
                'search_default_customer_id': self.id,
            },
        }

    def action_create_van_ban(self):
        """Tạo văn bản mới cho khách hàng"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tạo văn bản mới',
            'res_model': 'van_ban',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_customer_id': self.id,
            },
        }
