from odoo import models, fields, api


class VanBanHistory(models.Model):
    _name = 'van_ban_history'
    _description = 'Lịch sử thay đổi văn bản'
    _rec_name = 'van_ban_id'
    _order = 'ngay_thay_doi desc'

    van_ban_id = fields.Many2one('van_ban', string="Văn bản", required=True, ondelete='cascade')
    ngay_thay_doi = fields.Datetime("Ngày thay đổi", default=fields.Datetime.now, readonly=True)
    nguoi_thay_doi_id = fields.Many2one('res.users', string="Người thay đổi", 
                                         default=lambda self: self.env.user, readonly=True)
    noi_dung_cu = fields.Text("Nội dung cũ")
    noi_dung_moi = fields.Text("Nội dung mới")
    loai_thay_doi = fields.Selection([
        ('create', 'Tạo mới'),
        ('update', 'Cập nhật'),
        ('status_change', 'Thay đổi trạng thái'),
        ('delete', 'Xóa')
    ], string="Loại thay đổi", default='update')
    ghi_chu = fields.Text("Ghi chú")
