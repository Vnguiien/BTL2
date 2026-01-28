from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date


class VanBan(models.Model):
    _name = 'van_ban'
    _description = 'Văn bản'
    _rec_name = 'ten_van_ban'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'ngay_ban_hanh desc, ma_van_ban'

    # Thông tin cơ bản
    ma_van_ban = fields.Char("Mã văn bản", required=True, index=True, copy=False, default="New", tracking=True)
    ten_van_ban = fields.Char("Tên/Tiêu đề văn bản", required=True, tracking=True)
    so_hieu = fields.Char("Số hiệu văn bản", tracking=True)
    category_id = fields.Many2one('van_ban_category', string="Danh mục", tracking=True)
    
    # Loại văn bản
    loai_van_ban = fields.Selection([
        ('hop_dong', 'Hợp đồng'),
        ('bao_gia', 'Báo giá'),
        ('phap_ly', 'Tài liệu pháp lý'),
        ('van_ban_den', 'Văn bản đến'),
        ('van_ban_di', 'Văn bản đi'),
        ('noi_bo', 'Văn bản nội bộ'),
        ('bieu_mau', 'Biểu mẫu'),
        ('tai_lieu', 'Tài liệu kỹ thuật'),
        ('khac', 'Khác')
    ], string="Loại văn bản", required=True, default='khac', tracking=True)
    
    # Thời gian
    ngay_ban_hanh = fields.Date("Ngày ban hành", tracking=True)
    ngay_hieu_luc = fields.Date("Ngày có hiệu lực", tracking=True)
    ngay_het_han = fields.Date("Ngày hết hạn", tracking=True)
    
    # Liên kết đối tượng
    customer_id = fields.Many2one('customer', string="Khách hàng liên quan", ondelete='set null', tracking=True)
    nhan_vien_id = fields.Many2one('nhan_vien', string="Người tạo/Phụ trách", ondelete='set null', tracking=True)
    contract_id = fields.Many2one('contract', string="Hợp đồng liên quan", ondelete='set null')
    quotation_id = fields.Many2one('quotation', string="Báo giá liên quan", ondelete='set null')
    
    # Nội dung
    trich_yeu = fields.Text("Trích yếu nội dung")
    noi_dung = fields.Html("Nội dung chi tiết")
    
    # File đính kèm
    attachment_ids = fields.One2many('van_ban_attachment', 'van_ban_id', string="File đính kèm")
    attachment_count = fields.Integer("Số file đính kèm", compute="_compute_attachment_count", store=True)
    
    # Lịch sử thay đổi
    history_ids = fields.One2many('van_ban_history', 'van_ban_id', string="Lịch sử thay đổi")
    
    # Trạng thái
    trang_thai = fields.Selection([
        ('draft', 'Nháp'),
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('expired', 'Hết hiệu lực'),
        ('cancelled', 'Đã hủy')
    ], string="Trạng thái", default='draft', tracking=True)
    
    # Người duyệt
    nguoi_duyet_id = fields.Many2one('nhan_vien', string="Người duyệt", ondelete='set null')
    ngay_duyet = fields.Date("Ngày duyệt")
    
    # Thông tin bổ sung
    do_mat = fields.Selection([
        ('cong_khai', 'Công khai'),
        ('noi_bo', 'Nội bộ'),
        ('mat', 'Mật'),
        ('tuyet_mat', 'Tuyệt mật')
    ], string="Độ mật", default='cong_khai')
    
    do_khan = fields.Selection([
        ('binh_thuong', 'Bình thường'),
        ('khan', 'Khẩn'),
        ('thuong_khan', 'Thượng khẩn'),
        ('hoa_toc', 'Hỏa tốc')
    ], string="Độ khẩn", default='binh_thuong')
    
    ghi_chu = fields.Text("Ghi chú")
    active = fields.Boolean("Active", default=True)
    
    # Computed fields
    is_expired = fields.Boolean("Đã hết hạn", compute="_compute_is_expired", store=True)
    days_until_expiry = fields.Integer("Số ngày còn hiệu lực", compute="_compute_days_until_expiry")

    _sql_constraints = [
        ('ma_van_ban_unique', 'unique(ma_van_ban)', 'Mã văn bản phải là duy nhất!'),
    ]

    @api.depends('attachment_ids')
    def _compute_attachment_count(self):
        for record in self:
            record.attachment_count = len(record.attachment_ids)

    @api.depends('ngay_het_han', 'trang_thai')
    def _compute_is_expired(self):
        today = date.today()
        for record in self:
            if record.ngay_het_han and record.trang_thai == 'approved':
                record.is_expired = record.ngay_het_han < today
            else:
                record.is_expired = False

    @api.depends('ngay_het_han')
    def _compute_days_until_expiry(self):
        today = date.today()
        for record in self:
            if record.ngay_het_han:
                record.days_until_expiry = (record.ngay_het_han - today).days
            else:
                record.days_until_expiry = -1

    @api.model
    def create(self, vals):
        if vals.get('ma_van_ban', 'New') == 'New':
            vals['ma_van_ban'] = self.env['ir.sequence'].next_by_code('van_ban.sequence') or 'VB001'
        return super(VanBan, self).create(vals)

    def write(self, vals):
        # Lưu lịch sử thay đổi
        for record in self:
            if 'noi_dung' in vals or 'trich_yeu' in vals:
                self.env['van_ban_history'].create({
                    'van_ban_id': record.id,
                    'nguoi_thay_doi_id': self.env.user.id,
                    'noi_dung_cu': record.noi_dung or record.trich_yeu,
                    'noi_dung_moi': vals.get('noi_dung') or vals.get('trich_yeu'),
                    'ghi_chu': 'Cập nhật nội dung văn bản',
                })
        return super(VanBan, self).write(vals)

    def name_get(self):
        result = []
        for record in self:
            name = f"[{record.ma_van_ban}] {record.ten_van_ban}"
            result.append((record.id, name))
        return result
    
    # Actions
    def action_submit(self):
        """Gửi duyệt văn bản"""
        self.write({'trang_thai': 'pending'})
    
    def action_approve(self):
        """Duyệt văn bản"""
        self.write({
            'trang_thai': 'approved',
            'nguoi_duyet_id': self.env.user.employee_id.id if hasattr(self.env.user, 'employee_id') else False,
            'ngay_duyet': date.today()
        })
    
    def action_cancel(self):
        """Hủy văn bản"""
        self.write({'trang_thai': 'cancelled'})
    
    def action_draft(self):
        """Đưa về nháp"""
        self.write({'trang_thai': 'draft'})
    
    def action_view_attachments(self):
        """Xem file đính kèm"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'File đính kèm - {self.ten_van_ban}',
            'res_model': 'van_ban_attachment',
            'view_mode': 'tree,form',
            'domain': [('van_ban_id', '=', self.id)],
            'context': {'default_van_ban_id': self.id}
        }

    @api.model
    def check_expired_documents(self):
        """Scheduled action: Kiểm tra và cập nhật văn bản hết hạn"""
        today = date.today()
        expired_docs = self.search([
            ('trang_thai', '=', 'approved'),
            ('ngay_het_han', '<', today)
        ])
        expired_docs.write({'trang_thai': 'expired'})
        return True
