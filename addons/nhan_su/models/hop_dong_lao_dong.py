from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date


class HopDongLaoDong(models.Model):
    _name = 'hop_dong_lao_dong'
    _description = 'Hợp đồng lao động'
    _rec_name = 'ma_hop_dong'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'ngay_bat_dau desc'

    # Thông tin cơ bản
    ma_hop_dong = fields.Char("Mã hợp đồng", required=True, index=True, copy=False, default="New", tracking=True)
    ten_hop_dong = fields.Char("Tên hợp đồng", compute="_compute_ten_hop_dong", store=True)
    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên", required=True, ondelete='cascade', tracking=True)
    
    # Loại hợp đồng
    loai_hop_dong = fields.Selection([
        ('thu_viec', 'Thử việc'),
        ('co_thoi_han_1', 'Có thời hạn 1 năm'),
        ('co_thoi_han_3', 'Có thời hạn 3 năm'),
        ('khong_xac_dinh', 'Không xác định thời hạn'),
        ('thoi_vu', 'Thời vụ/Khoán việc')
    ], string="Loại hợp đồng", required=True, tracking=True)
    
    # Thời hạn
    ngay_bat_dau = fields.Date("Ngày bắt đầu", required=True, tracking=True)
    ngay_ket_thuc = fields.Date("Ngày kết thúc", tracking=True)
    ngay_ky = fields.Date("Ngày ký hợp đồng", tracking=True)
    
    # Thông tin lương
    luong_co_ban = fields.Float("Lương cơ bản", required=True, tracking=True)
    phu_cap = fields.Float("Phụ cấp", default=0.0)
    thuong = fields.Float("Thưởng", default=0.0)
    tong_thu_nhap = fields.Float("Tổng thu nhập", compute="_compute_tong_thu_nhap", store=True)
    
    # Chi tiết phụ cấp
    phu_cap_an_trua = fields.Float("Phụ cấp ăn trưa", default=0.0)
    phu_cap_di_lai = fields.Float("Phụ cấp đi lại", default=0.0)
    phu_cap_dien_thoai = fields.Float("Phụ cấp điện thoại", default=0.0)
    phu_cap_khac = fields.Float("Phụ cấp khác", default=0.0)
    
    # Thông tin công việc
    chuc_vu_id = fields.Many2one('chuc_vu', string="Chức vụ", tracking=True)
    phong_ban_id = fields.Many2one('phong_ban', string="Phòng ban", tracking=True)
    noi_lam_viec = fields.Char("Nơi làm việc")
    mo_ta_cong_viec = fields.Text("Mô tả công việc")
    
    # Bảo hiểm
    dong_bhxh = fields.Boolean("Đóng BHXH", default=True)
    dong_bhyt = fields.Boolean("Đóng BHYT", default=True)
    dong_bhtn = fields.Boolean("Đóng BHTN", default=True)
    ty_le_bhxh = fields.Float("Tỷ lệ BHXH (%)", default=8.0)
    ty_le_bhyt = fields.Float("Tỷ lệ BHYT (%)", default=1.5)
    ty_le_bhtn = fields.Float("Tỷ lệ BHTN (%)", default=1.0)
    
    # Trạng thái
    trang_thai = fields.Selection([
        ('draft', 'Nháp'),
        ('pending', 'Chờ ký'),
        ('active', 'Đang hiệu lực'),
        ('expired', 'Hết hạn'),
        ('terminated', 'Đã chấm dứt'),
        ('renewed', 'Đã gia hạn')
    ], string="Trạng thái", default='draft', tracking=True)
    
    # File đính kèm
    file_hop_dong = fields.Binary("File hợp đồng", attachment=True)
    file_name = fields.Char("Tên file")
    
    # Thông tin gia hạn
    hop_dong_goc_id = fields.Many2one('hop_dong_lao_dong', string="Hợp đồng gốc", ondelete='set null')
    hop_dong_gia_han_ids = fields.One2many('hop_dong_lao_dong', 'hop_dong_goc_id', string="Các lần gia hạn")
    so_lan_gia_han = fields.Integer("Số lần gia hạn", compute="_compute_so_lan_gia_han", store=True)
    
    # Ghi chú
    ghi_chu = fields.Text("Ghi chú")
    dieu_khoan_khac = fields.Text("Điều khoản khác")
    active = fields.Boolean("Active", default=True)
    
    # Computed
    so_ngay_con_lai = fields.Integer("Số ngày còn lại", compute="_compute_so_ngay_con_lai")
    sap_het_han = fields.Boolean("Sắp hết hạn", compute="_compute_sap_het_han", store=True)

    # SQL Constraints
    _sql_constraints = [
        ('ma_hop_dong_unique', 'unique(ma_hop_dong)', 'Mã hợp đồng phải là duy nhất!'),
        ('check_dates', 'CHECK(ngay_ket_thuc IS NULL OR ngay_bat_dau <= ngay_ket_thuc)', 
         'Ngày kết thúc phải sau ngày bắt đầu!'),
    ]

    @api.depends('nhan_vien_id', 'loai_hop_dong', 'ngay_bat_dau')
    def _compute_ten_hop_dong(self):
        loai_map = dict(self._fields['loai_hop_dong'].selection)
        for record in self:
            if record.nhan_vien_id and record.loai_hop_dong:
                record.ten_hop_dong = f"HĐ {loai_map.get(record.loai_hop_dong, '')} - {record.nhan_vien_id.ho_ten}"
            else:
                record.ten_hop_dong = record.ma_hop_dong

    @api.depends('luong_co_ban', 'phu_cap', 'thuong', 'phu_cap_an_trua', 'phu_cap_di_lai', 'phu_cap_dien_thoai', 'phu_cap_khac')
    def _compute_tong_thu_nhap(self):
        for record in self:
            record.tong_thu_nhap = (record.luong_co_ban + record.phu_cap + record.thuong + 
                                     record.phu_cap_an_trua + record.phu_cap_di_lai + 
                                     record.phu_cap_dien_thoai + record.phu_cap_khac)

    @api.depends('hop_dong_gia_han_ids')
    def _compute_so_lan_gia_han(self):
        for record in self:
            record.so_lan_gia_han = len(record.hop_dong_gia_han_ids)

    @api.depends('ngay_ket_thuc')
    def _compute_so_ngay_con_lai(self):
        today = date.today()
        for record in self:
            if record.ngay_ket_thuc:
                record.so_ngay_con_lai = (record.ngay_ket_thuc - today).days
            else:
                record.so_ngay_con_lai = -1  # Không xác định

    @api.depends('ngay_ket_thuc', 'trang_thai')
    def _compute_sap_het_han(self):
        today = date.today()
        for record in self:
            if record.ngay_ket_thuc and record.trang_thai == 'active':
                days_left = (record.ngay_ket_thuc - today).days
                record.sap_het_han = 0 <= days_left <= 30
            else:
                record.sap_het_han = False

    @api.model
    def create(self, vals):
        if vals.get('ma_hop_dong', 'New') == 'New':
            vals['ma_hop_dong'] = self.env['ir.sequence'].next_by_code('hop_dong_lao_dong.sequence') or 'HDLD001'
        return super(HopDongLaoDong, self).create(vals)

    def name_get(self):
        result = []
        for record in self:
            name = f"[{record.ma_hop_dong}] {record.ten_hop_dong or ''}"
            result.append((record.id, name))
        return result

    # Actions
    def action_confirm(self):
        """Xác nhận hợp đồng - chuyển sang chờ ký"""
        for record in self:
            record.trang_thai = 'pending'

    def action_activate(self):
        """Kích hoạt hợp đồng"""
        for record in self:
            record.trang_thai = 'active'
            # Cập nhật thông tin cho nhân viên
            if record.nhan_vien_id:
                record.nhan_vien_id.write({
                    'loai_hop_dong': record.loai_hop_dong,
                    'chuc_vu_id': record.chuc_vu_id.id if record.chuc_vu_id else False,
                    'phong_ban_id': record.phong_ban_id.id if record.phong_ban_id else False,
                })

    def action_terminate(self):
        """Chấm dứt hợp đồng"""
        for record in self:
            record.trang_thai = 'terminated'

    def action_renew(self):
        """Gia hạn hợp đồng - tạo hợp đồng mới"""
        self.ensure_one()
        self.trang_thai = 'renewed'
        
        # Tạo hợp đồng mới
        new_contract = self.copy({
            'hop_dong_goc_id': self.id,
            'trang_thai': 'draft',
            'ma_hop_dong': 'New',
            'ngay_bat_dau': self.ngay_ket_thuc,
            'ngay_ket_thuc': False,
            'file_hop_dong': False,
        })
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Hợp đồng gia hạn',
            'res_model': 'hop_dong_lao_dong',
            'res_id': new_contract.id,
            'view_mode': 'form',
        }

    def action_draft(self):
        """Đặt về nháp"""
        for record in self:
            record.trang_thai = 'draft'

    @api.model
    def check_expired_contracts(self):
        """Scheduled action: Kiểm tra và cập nhật hợp đồng hết hạn"""
        today = date.today()
        expired_contracts = self.search([
            ('trang_thai', '=', 'active'),
            ('ngay_ket_thuc', '<', today)
        ])
        expired_contracts.write({'trang_thai': 'expired'})
        return True
