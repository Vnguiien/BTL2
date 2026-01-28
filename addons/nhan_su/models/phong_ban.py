from odoo import models, fields, api


class PhongBan(models.Model):
    _name = 'phong_ban'
    _description = 'Bảng chứa thông tin phòng ban'
    _rec_name = 'ten_phong_ban'
    _order = 'sequence, ma_phong_ban'

    # Thông tin cơ bản
    ma_phong_ban = fields.Char("Mã phòng ban", required=True, index=True, copy=False)
    ten_phong_ban = fields.Char("Tên phòng ban", required=True)
    mo_ta = fields.Text("Mô tả")
    sequence = fields.Integer("Thứ tự", default=10)
    active = fields.Boolean("Active", default=True)

    # Cấu trúc tổ chức
    parent_id = fields.Many2one('phong_ban', string="Phòng ban cấp trên", ondelete='set null')
    child_ids = fields.One2many('phong_ban', 'parent_id', string="Phòng ban trực thuộc")
    truong_phong_id = fields.Many2one('nhan_vien', string="Trưởng phòng", ondelete='set null')
    
    # Thông tin liên quan
    nhan_vien_ids = fields.One2many('nhan_vien', 'phong_ban_id', string="Danh sách nhân viên")
    
    # Computed fields
    so_luong_nhan_vien = fields.Integer("Số lượng nhân viên", compute="_compute_so_luong_nhan_vien", store=True)
    complete_name = fields.Char("Tên đầy đủ", compute="_compute_complete_name", store=True, recursive=True)

    # SQL Constraints
    _sql_constraints = [
        ('ma_phong_ban_unique', 'unique(ma_phong_ban)', 'Mã phòng ban phải là duy nhất!'),
    ]

    @api.depends('nhan_vien_ids')
    def _compute_so_luong_nhan_vien(self):
        for record in self:
            record.so_luong_nhan_vien = len(record.nhan_vien_ids.filtered(lambda x: x.trang_thai == 'active'))

    @api.depends('ten_phong_ban', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for record in self:
            if record.parent_id:
                record.complete_name = f"{record.parent_id.complete_name} / {record.ten_phong_ban}"
            else:
                record.complete_name = record.ten_phong_ban

    def name_get(self):
        result = []
        for record in self:
            name = f"[{record.ma_phong_ban}] {record.ten_phong_ban}"
            result.append((record.id, name))
        return result

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise models.ValidationError("Không thể tạo phòng ban lồng vào chính nó!")