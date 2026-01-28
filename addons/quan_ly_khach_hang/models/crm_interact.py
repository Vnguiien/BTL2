from odoo import models, fields, api

class CrmInteract(models.Model):
    _name = 'crm_interact'
    _description = 'Bảng chứa thông tin tương tác'
    _rec_name = 'crm_interact_name'
    _order = 'date desc'

    crm_interact_id = fields.Char("Mã tương tác", required=True, index=True, copy=False, default="New")
    crm_interact_name = fields.Char("Tên tương tác")
    customer_id = fields.Many2one('customer', string="Khách hàng", required=True, ondelete='cascade')
    interaction_type = fields.Selection([
        ('call', 'Cuộc gọi'),
        ('email', 'Email'),
        ('meeting', 'Cuộc họp'),
        ('visit', 'Thăm khách hàng'),
        ('demo', 'Demo sản phẩm'),
        ('support', 'Hỗ trợ kỹ thuật'),
        ('other', 'Khác')
    ], string="Loại tương tác", required=True)
    date = fields.Datetime("Ngày tương tác", required=True, default=fields.Datetime.now)
    duration = fields.Float("Thời lượng (phút)")
    note = fields.Text("Ghi chú về tương tác")
    result = fields.Selection([
        ('positive', 'Tích cực'),
        ('neutral', 'Trung tính'),
        ('negative', 'Tiêu cực')
    ], string="Kết quả")
    
    # Link đến nhân viên từ module nhan_su
    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên phụ trách", ondelete='set null')
    
    # Theo dõi
    next_action = fields.Text("Hành động tiếp theo")
    next_action_date = fields.Date("Ngày hành động tiếp theo")
    
    active = fields.Boolean("Active", default=True)

    @api.model
    def create(self, vals):
        if vals.get('crm_interact_id', 'New') == 'New':
            vals['crm_interact_id'] = self.env['ir.sequence'].next_by_code('crm_interact.sequence') or 'INT001'
        return super(CrmInteract, self).create(vals)

    # Đặt tên hiển thị cho bản ghi
    def name_get(self):
        result = []
        for record in self:
            name = f"[{record.crm_interact_id}] {record.crm_interact_name or record.interaction_type}"
            result.append((record.id, name))
        return result
