from odoo import models, fields, api


class VanBanTemplate(models.Model):
    _name = 'van_ban_template'
    _description = 'Mẫu văn bản'
    _rec_name = 'ten_mau'
    _order = 'sequence, ma_mau'

    # Thông tin cơ bản
    ma_mau = fields.Char("Mã mẫu", required=True, index=True, copy=False)
    ten_mau = fields.Char("Tên mẫu", required=True)
    mo_ta = fields.Text("Mô tả mẫu")
    sequence = fields.Integer("Thứ tự", default=10)
    
    # Phân loại
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
    ], string="Loại văn bản", required=True)
    
    category_id = fields.Many2one('van_ban_category', string="Danh mục")
    
    # Nội dung mẫu
    noi_dung_mau = fields.Html("Nội dung mẫu", 
                                help="Sử dụng các biến: ${customer_name}, ${company_name}, ${date}, ${amount}, v.v.")
    
    # File mẫu
    file_mau = fields.Binary("File mẫu", attachment=True)
    file_name = fields.Char("Tên file")
    
    active = fields.Boolean("Active", default=True)

    _sql_constraints = [
        ('ma_mau_unique', 'unique(ma_mau)', 'Mã mẫu phải là duy nhất!'),
    ]

    def name_get(self):
        result = []
        for record in self:
            name = f"[{record.ma_mau}] {record.ten_mau}"
            result.append((record.id, name))
        return result
    
    def action_use_template(self):
        """Sử dụng mẫu để tạo văn bản mới"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tạo văn bản từ mẫu',
            'res_model': 'van_ban',
            'view_mode': 'form',
            'context': {
                'default_loai_van_ban': self.loai_van_ban,
                'default_category_id': self.category_id.id if self.category_id else False,
                'default_noi_dung': self.noi_dung_mau,
            }
        }
