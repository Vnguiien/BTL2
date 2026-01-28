from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date
import re


class NhanVien(models.Model):
    _name = 'nhan_vien'
    _description = 'Bảng chứa thông tin nhân viên'
    _rec_name = 'ho_ten'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'ma_dinh_danh'

    # Thông tin cơ bản
    ma_dinh_danh = fields.Char("Mã định danh", required=True, index=True, copy=False, default="New", tracking=True)
    ho_ten_dem = fields.Char("Họ tên đệm", tracking=True)
    ten = fields.Char("Tên", tracking=True)
    ho_ten = fields.Char("Họ tên", compute='_compute_ho_ten', store=True)
    ngay_sinh = fields.Date("Ngày sinh", tracking=True)
    tuoi = fields.Integer(string='Tuổi', compute='_compute_tuoi', store=True)
    que_quan = fields.Char("Quê quán")
    dia_chi = fields.Char("Địa chỉ hiện tại")
    email = fields.Char("Email cá nhân")
    email_cong_ty = fields.Char("Email công ty")
    so_dien_thoai = fields.Char("Số điện thoại")
    so_dien_thoai_khan_cap = fields.Char("SĐT liên hệ khẩn cấp")
    nguoi_lien_he_khan_cap = fields.Char("Người liên hệ khẩn cấp")

    gioi_tinh = fields.Selection([
        ('male', 'Nam'),
        ('female', 'Nữ'),
        ('other', 'Khác')
    ], string="Giới tính", tracking=True)

    # Thông tin CMND/CCCD
    so_cmnd = fields.Char("CMND/CCCD", tracking=True)
    ngay_cap_cmnd = fields.Date("Ngày cấp")
    noi_cap_cmnd = fields.Char("Nơi cấp")
    
    # Thông tin học vấn
    trinh_do_hoc_van = fields.Selection([
        ('pho_thong', 'Phổ thông'),
        ('trung_cap', 'Trung cấp'),
        ('cao_dang', 'Cao đẳng'),
        ('dai_hoc', 'Đại học'),
        ('thac_si', 'Thạc sĩ'),
        ('tien_si', 'Tiến sĩ')
    ], string="Trình độ học vấn", tracking=True)
    chuyen_nganh = fields.Char("Chuyên ngành")
    truong_hoc = fields.Char("Trường tốt nghiệp")
    nam_tot_nghiep = fields.Integer("Năm tốt nghiệp")
    
    # Kỹ năng và kinh nghiệm
    ky_nang = fields.Text("Kỹ năng")
    kinh_nghiem_lam_viec = fields.Text("Kinh nghiệm làm việc")
    chung_chi = fields.Text("Chứng chỉ đạt được")
    
    # Thông tin ngân hàng
    so_tai_khoan = fields.Char("Số tài khoản ngân hàng")
    ten_ngan_hang = fields.Char("Tên ngân hàng")
    chi_nhanh_ngan_hang = fields.Char("Chi nhánh")
    
    # Thông tin bảo hiểm
    so_bhxh = fields.Char("Số sổ BHXH")
    so_bao_hiem_y_te = fields.Char("Số thẻ BHYT")
    ma_so_thue_ca_nhan = fields.Char("Mã số thuế cá nhân")

    # Thông tin công việc
    chuc_vu_id = fields.Many2one('chuc_vu', string="Chức vụ", tracking=True)
    phong_ban_id = fields.Many2one('phong_ban', string="Phòng ban", tracking=True)
    quan_ly_id = fields.Many2one('nhan_vien', string="Quản lý trực tiếp", ondelete='set null')
    nhan_vien_quan_ly_ids = fields.One2many('nhan_vien', 'quan_ly_id', string="Nhân viên trực thuộc")
    ngay_bat_dau_lam = fields.Date("Ngày bắt đầu làm việc", tracking=True)
    ngay_ket_thuc = fields.Date("Ngày kết thúc làm việc")
    trang_thai = fields.Selection([
        ('active', 'Đang làm việc'),
        ('inactive', 'Đã nghỉ việc'),
        ('probation', 'Thử việc'),
        ('maternity', 'Nghỉ thai sản'),
        ('suspended', 'Tạm ngưng')
    ], string="Trạng thái", default="active", tracking=True)
    
    loai_hop_dong = fields.Selection([
        ('thu_viec', 'Thử việc'),
        ('co_thoi_han_1', 'Có thời hạn 1 năm'),
        ('co_thoi_han_3', 'Có thời hạn 3 năm'),
        ('khong_xac_dinh', 'Không xác định thời hạn')
    ], string="Loại hợp đồng hiện tại", tracking=True)

    # Thông tin liên kết
    lich_su_lam_viec_ids = fields.One2many('lich_su_lam_viec', inverse_name='nhan_vien_id', string="Lịch sử làm việc")
    hop_dong_lao_dong_ids = fields.One2many('hop_dong_lao_dong', 'nhan_vien_id', string="Hợp đồng lao động")
    
    # Link đến user Odoo
    user_id = fields.Many2one('res.users', string="Tài khoản người dùng", ondelete='set null')

    # Thông tin bổ sung
    ghi_chu = fields.Text("Ghi chú")
    anh_dai_dien = fields.Binary("Ảnh đại diện", attachment=True)
    active = fields.Boolean("Active", default=True)
    
    # Computed fields
    so_nam_lam_viec = fields.Float("Số năm làm việc", compute="_compute_so_nam_lam_viec", store=True)
    hop_dong_hien_tai_id = fields.Many2one('hop_dong_lao_dong', string="Hợp đồng hiện tại", 
                                            compute="_compute_hop_dong_hien_tai", store=True)

    # SQL Constraints
    _sql_constraints = [
        ('ma_dinh_danh_unique', 'unique(ma_dinh_danh)', 'Mã định danh phải là duy nhất!'),
        ('so_cmnd_unique', 'unique(so_cmnd)', 'Số CMND/CCCD phải là duy nhất!'),
    ]

    # Computed fields
    @api.depends("ho_ten_dem", "ten")
    def _compute_ho_ten(self):
        for record in self:
            if record.ho_ten_dem and record.ten:
                record.ho_ten = record.ho_ten_dem + ' ' + record.ten
            elif record.ten:
                record.ho_ten = record.ten
            else:
                record.ho_ten = record.ho_ten_dem or ''

    @api.depends("ngay_sinh")
    def _compute_tuoi(self):
        today = date.today()
        for record in self:
            if record.ngay_sinh:
                record.tuoi = today.year - record.ngay_sinh.year - (
                    (today.month, today.day) < (record.ngay_sinh.month, record.ngay_sinh.day)
                )
            else:
                record.tuoi = 0

    @api.depends("ngay_bat_dau_lam")
    def _compute_so_nam_lam_viec(self):
        today = date.today()
        for record in self:
            if record.ngay_bat_dau_lam:
                delta = today - record.ngay_bat_dau_lam
                record.so_nam_lam_viec = round(delta.days / 365, 1)
            else:
                record.so_nam_lam_viec = 0

    @api.depends("hop_dong_lao_dong_ids", "hop_dong_lao_dong_ids.trang_thai")
    def _compute_hop_dong_hien_tai(self):
        for record in self:
            hop_dong = record.hop_dong_lao_dong_ids.filtered(lambda x: x.trang_thai == 'active')
            record.hop_dong_hien_tai_id = hop_dong[0] if hop_dong else False

    # Validation
    @api.constrains('email')
    def _check_email(self):
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        for record in self:
            if record.email and not re.match(email_pattern, record.email):
                raise ValidationError("Email không hợp lệ: %s" % record.email)

    @api.constrains('so_dien_thoai')
    def _check_phone(self):
        phone_pattern = r'^(\+84|0)[1-9]\d{8,9}$'
        for record in self:
            if record.so_dien_thoai and not re.match(phone_pattern, record.so_dien_thoai):
                raise ValidationError("Số điện thoại không hợp lệ!")

    @api.constrains('ngay_sinh')
    def _check_ngay_sinh(self):
        today = date.today()
        for record in self:
            if record.ngay_sinh and record.ngay_sinh > today:
                raise ValidationError("Ngày sinh không được trong tương lai!")

    @api.onchange("ho_ten_dem", "ten")
    def _onchange_ten(self):
        for record in self:
            if record.ho_ten_dem and record.ten:
                # Tự động tạo mã định danh nếu chưa có
                if not record.ma_dinh_danh or record.ma_dinh_danh == 'New':
                    record.ma_dinh_danh = record.ten.upper()

    @api.model
    def create(self, vals):
        if vals.get('ma_dinh_danh', 'New') == 'New':
            vals['ma_dinh_danh'] = self.env['ir.sequence'].next_by_code('nhan_vien.sequence') or 'NV001'
        return super(NhanVien, self).create(vals)

    def name_get(self):
        result = []
        for record in self:
            name = f"[{record.ma_dinh_danh}] {record.ho_ten}"
            result.append((record.id, name))
        return result
    
    def action_view_hop_dong(self):
        """Mở danh sách hợp đồng của nhân viên"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Hợp đồng của {self.ho_ten}',
            'res_model': 'hop_dong_lao_dong',
            'view_mode': 'tree,form',
            'domain': [('nhan_vien_id', '=', self.id)],
            'context': {'default_nhan_vien_id': self.id}
        }