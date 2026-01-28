from odoo import models, fields, api


class ChucVu(models.Model):
    _name = 'chuc_vu'
    _description = 'Bảng chứa thông tin chức vụ'
    _rec_name = 'ten_chuc_vu'
    _order = 'cap_bac desc, sequence'

    # Thông tin cơ bản
    ma_chuc_vu = fields.Char("Mã chức vụ", required=True, index=True, copy=False)
    ten_chuc_vu = fields.Char("Tên chức vụ", required=True)
    mo_ta = fields.Text("Mô tả công việc")
    sequence = fields.Integer("Thứ tự", default=10)
    active = fields.Boolean("Active", default=True)

    # Cấp bậc và lương
    cap_bac = fields.Integer("Cấp bậc", default=1, help="Cấp bậc cao hơn = quyền hạn lớn hơn")
    muc_luong_co_ban = fields.Float("Mức lương cơ bản", help="Mức lương tối thiểu cho chức vụ này")
    phu_cap = fields.Float("Phụ cấp chức vụ", default=0.0)
    
    # Phòng ban cho phép
    phong_ban_ids = fields.Many2many('phong_ban', string="Phòng ban áp dụng", 
                                      help="Để trống nếu áp dụng cho tất cả phòng ban")
    
    # Thông tin liên quan
    nhan_vien_ids = fields.One2many('nhan_vien', 'chuc_vu_id', string="Danh sách nhân viên")
    
    # Computed fields
    so_luong_nhan_vien = fields.Integer("Số lượng nhân viên", compute="_compute_so_luong_nhan_vien", store=True)

    # SQL Constraints
    _sql_constraints = [
        ('ma_chuc_vu_unique', 'unique(ma_chuc_vu)', 'Mã chức vụ phải là duy nhất!'),
    ]

    @api.depends('nhan_vien_ids')
    def _compute_so_luong_nhan_vien(self):
        for record in self:
            record.so_luong_nhan_vien = len(record.nhan_vien_ids.filtered(lambda x: x.trang_thai == 'active'))

    def name_get(self):
        result = []
        for record in self:
            name = f"[{record.ma_chuc_vu}] {record.ten_chuc_vu}"
            if record.cap_bac:
                name += f" (Cấp {record.cap_bac})"
            result.append((record.id, name))
        return result