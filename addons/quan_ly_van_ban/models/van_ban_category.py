from odoo import models, fields, api


class VanBanCategory(models.Model):
    _name = 'van_ban_category'
    _description = 'Danh mục văn bản'
    _rec_name = 'ten_danh_muc'
    _order = 'sequence, ma_danh_muc'
    _parent_store = True

    # Thông tin cơ bản
    ma_danh_muc = fields.Char("Mã danh mục", required=True, index=True, copy=False)
    ten_danh_muc = fields.Char("Tên danh mục", required=True)
    mo_ta = fields.Text("Mô tả")
    sequence = fields.Integer("Thứ tự", default=10)
    color = fields.Integer("Màu sắc")
    active = fields.Boolean("Active", default=True)

    # Cấu trúc phân cấp
    parent_id = fields.Many2one('van_ban_category', string="Danh mục cha", ondelete='cascade')
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many('van_ban_category', 'parent_id', string="Danh mục con")
    
    # Liên kết văn bản
    van_ban_ids = fields.One2many('van_ban', 'category_id', string="Văn bản trong danh mục")
    
    # Computed
    complete_name = fields.Char("Tên đầy đủ", compute="_compute_complete_name", store=True, recursive=True)
    van_ban_count = fields.Integer("Số lượng văn bản", compute="_compute_van_ban_count", store=True)

    _sql_constraints = [
        ('ma_danh_muc_unique', 'unique(ma_danh_muc)', 'Mã danh mục phải là duy nhất!'),
    ]

    @api.depends('ten_danh_muc', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for record in self:
            if record.parent_id:
                record.complete_name = f"{record.parent_id.complete_name} / {record.ten_danh_muc}"
            else:
                record.complete_name = record.ten_danh_muc

    @api.depends('van_ban_ids')
    def _compute_van_ban_count(self):
        for record in self:
            record.van_ban_count = len(record.van_ban_ids)

    def name_get(self):
        result = []
        for record in self:
            name = record.complete_name or record.ten_danh_muc
            result.append((record.id, name))
        return result

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise models.ValidationError("Không thể tạo danh mục lồng vào chính nó!")
