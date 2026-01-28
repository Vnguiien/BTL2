from odoo import models, fields, api
import os


class VanBanAttachment(models.Model):
    _name = 'van_ban_attachment'
    _description = 'File đính kèm văn bản'
    _rec_name = 'name'
    _order = 'ngay_upload desc'

    name = fields.Char("Tên file", required=True)
    van_ban_id = fields.Many2one('van_ban', string="Văn bản", required=True, ondelete='cascade')
    file = fields.Binary("File", required=True, attachment=True)
    file_name = fields.Char("Tên file gốc")
    file_size = fields.Float("Kích thước (KB)", compute="_compute_file_size", store=True)
    loai_file = fields.Char("Loại file", compute="_compute_loai_file", store=True)
    mo_ta = fields.Text("Mô tả")
    ngay_upload = fields.Datetime("Ngày upload", default=fields.Datetime.now, readonly=True)
    nguoi_upload_id = fields.Many2one('res.users', string="Người upload", 
                                       default=lambda self: self.env.user, readonly=True)
    active = fields.Boolean("Active", default=True)

    @api.depends('file')
    def _compute_file_size(self):
        for record in self:
            if record.file:
                # Tính kích thước từ base64
                import base64
                try:
                    file_data = base64.b64decode(record.file)
                    record.file_size = len(file_data) / 1024  # Convert to KB
                except:
                    record.file_size = 0
            else:
                record.file_size = 0

    @api.depends('file_name')
    def _compute_loai_file(self):
        for record in self:
            if record.file_name:
                _, ext = os.path.splitext(record.file_name)
                record.loai_file = ext.upper().replace('.', '') if ext else 'Unknown'
            else:
                record.loai_file = 'Unknown'

    @api.onchange('file_name')
    def _onchange_file_name(self):
        if self.file_name and not self.name:
            self.name = self.file_name
