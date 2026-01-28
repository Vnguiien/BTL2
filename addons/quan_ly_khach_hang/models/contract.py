from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date

class Contract(models.Model):
    _name = 'contract'
    _description = 'Hợp đồng khách hàng'
    _rec_name = 'contract_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc'

    contract_id = fields.Char("Mã hợp đồng", required=True, index=True, copy=False, default="New")
    contract_name = fields.Char("Tên hợp đồng", required=True)
    customer_id = fields.Many2one('customer', string="Khách hàng", required=True, ondelete='cascade', tracking=True)
    
    # Nhân viên phụ trách từ module nhan_su
    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên phụ trách", ondelete='set null', tracking=True)
    
    # Thời gian
    start_date = fields.Date("Ngày bắt đầu", required=True, tracking=True)
    end_date = fields.Date("Ngày kết thúc", required=True, tracking=True)
    sign_date = fields.Date("Ngày ký", tracking=True)
    
    # Giá trị hợp đồng
    contract_value = fields.Float("Giá trị hợp đồng", tracking=True)
    currency_id = fields.Many2one('res.currency', string="Tiền tệ", 
                                   default=lambda self: self.env.company.currency_id)
    payment_term = fields.Selection([
        ('one_time', 'Thanh toán một lần'),
        ('monthly', 'Hàng tháng'),
        ('quarterly', 'Hàng quý'),
        ('yearly', 'Hàng năm'),
        ('milestone', 'Theo tiến độ')
    ], string="Điều khoản thanh toán", default='one_time')
    
    # Loại hợp đồng
    contract_type = fields.Selection([
        ('service', 'Hợp đồng dịch vụ'),
        ('product', 'Hợp đồng sản phẩm'),
        ('maintenance', 'Hợp đồng bảo trì'),
        ('consulting', 'Hợp đồng tư vấn'),
        ('license', 'Hợp đồng bản quyền'),
        ('other', 'Khác')
    ], string="Loại hợp đồng", default='service')
    
    # Trạng thái
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('pending', 'Chờ ký'),
        ('active', 'Đang hoạt động'),
        ('ended', 'Đã kết thúc'),
        ('cancelled', 'Đã hủy')
    ], string="Trạng thái", default='draft', tracking=True)
    
    # Điều khoản
    terms = fields.Text("Điều khoản hợp đồng")
    notes = fields.Text("Ghi chú")
    
    # File đính kèm
    file_attachment = fields.Binary("File hợp đồng", attachment=True)
    file_name = fields.Char("Tên file")
    
    # Liên kết với báo giá
    quotation_id = fields.Many2one('quotation', string="Báo giá gốc", ondelete='set null')
    
    # Computed
    days_remaining = fields.Integer("Số ngày còn lại", compute="_compute_days_remaining")
    is_expiring_soon = fields.Boolean("Sắp hết hạn", compute="_compute_is_expiring_soon", store=True)
    
    active = fields.Boolean("Active", default=True)

    _sql_constraints = [
        ('contract_id_unique', 'unique(contract_id)', 'Mã hợp đồng phải là duy nhất!'),
        ('check_dates', 'CHECK(end_date IS NULL OR start_date <= end_date)', 
         'Ngày kết thúc phải sau ngày bắt đầu!'),
    ]

    @api.depends('end_date')
    def _compute_days_remaining(self):
        today = date.today()
        for record in self:
            if record.end_date:
                record.days_remaining = (record.end_date - today).days
            else:
                record.days_remaining = 0

    @api.depends('end_date', 'state')
    def _compute_is_expiring_soon(self):
        today = date.today()
        for record in self:
            if record.end_date and record.state == 'active':
                days_left = (record.end_date - today).days
                record.is_expiring_soon = 0 <= days_left <= 30
            else:
                record.is_expiring_soon = False

    @api.model
    def create(self, vals):
        if vals.get('contract_id', 'New') == 'New':
            vals['contract_id'] = self.env['ir.sequence'].next_by_code('contract.sequence') or 'HD001'
        return super(Contract, self).create(vals)

    # Đặt tên hiển thị cho bản ghi
    def name_get(self):
        result = []
        for record in self:
            name = f"[{record.contract_id}] {record.contract_name}"
            result.append((record.id, name))
        return result
    
    # Actions
    def action_send_for_signature(self):
        self.write({'state': 'pending'})
    
    def action_activate(self):
        self.write({'state': 'active', 'sign_date': date.today()})
    
    def action_end(self):
        self.write({'state': 'ended'})
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})
    
    def action_draft(self):
        self.write({'state': 'draft'})
