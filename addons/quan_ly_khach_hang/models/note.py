from odoo import models, fields, api

class Note(models.Model):
    _name = 'note'
    _description = 'Bảng chứa thông tin ghi chú'
    _rec_name = 'note_name'
    _order = 'date desc'

    note_id = fields.Char("Mã ghi chú", required=True, index=True, copy=False, default="New")
    note_name = fields.Char("Tiêu đề ghi chú")
    customer_id = fields.Many2one('customer', string="Khách hàng", required=True, ondelete='cascade')
    note = fields.Text("Nội dung ghi chú", required=True)
    date = fields.Datetime("Ngày tạo ghi chú", required=True, default=fields.Datetime.now)
    
    # Link đến nhân viên từ module nhan_su
    nhan_vien_id = fields.Many2one('nhan_vien', string="Người tạo", ondelete='set null')
    
    # Phân loại
    note_type = fields.Selection([
        ('general', 'Chung'),
        ('important', 'Quan trọng'),
        ('follow_up', 'Cần theo dõi'),
        ('reminder', 'Nhắc nhở')
    ], string="Loại ghi chú", default='general')
    
    is_pinned = fields.Boolean("Ghim", default=False)
    active = fields.Boolean("Active", default=True)

    @api.model
    def create(self, vals):
        if vals.get('note_id', 'New') == 'New':
            vals['note_id'] = self.env['ir.sequence'].next_by_code('note.sequence') or 'NOTE001'
        return super(Note, self).create(vals)

    # Đặt tên hiển thị cho bản ghi
    def name_get(self):
        result = []
        for record in self:
            name = f"[{record.note_id}] {record.note_name or 'Ghi chú'}"
            result.append((record.id, name))
        return result
