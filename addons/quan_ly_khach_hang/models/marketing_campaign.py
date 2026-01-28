from odoo import models, fields, api

class MarketingCampaign(models.Model):
    _name = 'marketing_campaign'
    _description = 'Bảng chứa thông tin chiến dịch marketing'
    _rec_name = 'marketing_campaign_name'
    _order = 'start_date desc'

    marketing_campaign_id = fields.Char("Mã chiến dịch", required=True, index=True, copy=False, default="New")
    marketing_campaign_name = fields.Char("Tên chiến dịch", required=True)
    description = fields.Text("Mô tả chiến dịch")
    start_date = fields.Date("Ngày bắt đầu", required=True)
    end_date = fields.Date("Ngày kết thúc", required=True)
    
    # Khách hàng tham gia
    customer_ids = fields.Many2many('customer', string="Khách hàng mục tiêu")
    
    # Link đến nhân viên từ module nhan_su
    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên phụ trách", ondelete='set null')
    team_ids = fields.Many2many('nhan_vien', 'marketing_campaign_team_rel', 
                                 'campaign_id', 'nhan_vien_id', string="Đội ngũ thực hiện")
    
    # Ngân sách và chi phí
    budget = fields.Float("Ngân sách dự kiến")
    actual_cost = fields.Float("Chi phí thực tế")
    
    # Kênh marketing
    channel = fields.Selection([
        ('email', 'Email Marketing'),
        ('social', 'Mạng xã hội'),
        ('sms', 'SMS'),
        ('event', 'Sự kiện'),
        ('ads', 'Quảng cáo'),
        ('mixed', 'Đa kênh')
    ], string="Kênh marketing")
    
    # Trạng thái
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('planned', 'Đã lên kế hoạch'),
        ('running', 'Đang chạy'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Đã hủy')
    ], string="Trạng thái", default='draft')
    
    # Kết quả
    target_reach = fields.Integer("Mục tiêu tiếp cận")
    actual_reach = fields.Integer("Thực tế tiếp cận")
    conversion_rate = fields.Float("Tỷ lệ chuyển đổi (%)")
    
    # Computed
    customer_count = fields.Integer("Số KH mục tiêu", compute="_compute_customer_count", store=True)
    
    active = fields.Boolean("Active", default=True)

    @api.depends('customer_ids')
    def _compute_customer_count(self):
        for record in self:
            record.customer_count = len(record.customer_ids)

    @api.model
    def create(self, vals):
        if vals.get('marketing_campaign_id', 'New') == 'New':
            vals['marketing_campaign_id'] = self.env['ir.sequence'].next_by_code('marketing_campaign.sequence') or 'MKT001'
        return super(MarketingCampaign, self).create(vals)

    # Đặt tên hiển thị cho bản ghi
    def name_get(self):
        result = []
        for record in self:
            name = f"[{record.marketing_campaign_id}] {record.marketing_campaign_name}"
            result.append((record.id, name))
        return result
    
    # Actions
    def action_plan(self):
        self.write({'state': 'planned'})
    
    def action_start(self):
        self.write({'state': 'running'})
    
    def action_complete(self):
        self.write({'state': 'completed'})
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})
