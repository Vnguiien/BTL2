from odoo import models, fields, api

class Feedback(models.Model):
    _name = 'feedback'
    _description = 'Bảng chứa thông tin phản hồi khách hàng'
    _rec_name = 'feedback_name'
    _order = 'feedback_date desc'

    feedback_id = fields.Char("Mã phản hồi", required=True, index=True, copy=False, default="New")
    feedback_name = fields.Char("Tiêu đề phản hồi")
    customer_id = fields.Many2one('customer', string="Khách hàng", required=True, ondelete='cascade')
    feedback = fields.Text("Nội dung phản hồi", required=True)
    feedback_date = fields.Datetime("Ngày phản hồi", required=True, default=fields.Datetime.now)
    
    rating = fields.Selection([
        ('1', '1 sao - Rất không hài lòng'),
        ('2', '2 sao - Không hài lòng'),
        ('3', '3 sao - Bình thường'),
        ('4', '4 sao - Hài lòng'),
        ('5', '5 sao - Rất hài lòng')
    ], string="Đánh giá", required=True)
    
    # Link đến nhân viên từ module nhan_su
    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên tiếp nhận", ondelete='set null')
    
    # Phân loại phản hồi
    feedback_type = fields.Selection([
        ('product', 'Sản phẩm'),
        ('service', 'Dịch vụ'),
        ('support', 'Hỗ trợ'),
        ('delivery', 'Giao hàng'),
        ('price', 'Giá cả'),
        ('other', 'Khác')
    ], string="Loại phản hồi")
    
    # Trạng thái xử lý
    state = fields.Selection([
        ('new', 'Mới'),
        ('processing', 'Đang xử lý'),
        ('resolved', 'Đã giải quyết'),
        ('closed', 'Đã đóng')
    ], string="Trạng thái", default='new')
    
    response = fields.Text("Phản hồi của công ty")
    response_date = fields.Datetime("Ngày trả lời")
    
    active = fields.Boolean("Active", default=True)

    @api.model
    def create(self, vals):
        if vals.get('feedback_id', 'New') == 'New':
            vals['feedback_id'] = self.env['ir.sequence'].next_by_code('feedback.sequence') or 'FB001'
        return super(Feedback, self).create(vals)

    # Đặt tên hiển thị cho bản ghi
    def name_get(self):
        result = []
        for record in self:
            name = f"[{record.feedback_id}] {record.feedback_name or 'Phản hồi'}"
            result.append((record.id, name))
        return result
