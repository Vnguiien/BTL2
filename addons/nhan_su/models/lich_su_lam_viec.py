from odoo import models, fields, api


class LichSuLamViec(models.Model):
    _name = 'lich_su_lam_viec'
    _description = 'Bảng chứa thông tin lịch sử làm việc'
    _rec_name = 'mo_ta'

    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên", required=True)
    chuc_vu_id = fields.Many2one('chuc_vu', string="Chức vụ")
    phong_ban_id = fields.Many2one('phong_ban', string="Phòng ban")
    ngay_bat_dau = fields.Date("Ngày bắt đầu", required=True)
    ngay_ket_thuc = fields.Date("Ngày kết thúc")
    mo_ta = fields.Char("Mô tả công việc")
    ghi_chu = fields.Text("Ghi chú")
    la_cong_viec_hien_tai = fields.Boolean("Công việc hiện tại", default=False)

    _sql_constraints = [
        ('check_dates', 'CHECK(ngay_ket_thuc IS NULL OR ngay_bat_dau <= ngay_ket_thuc)',
         'Ngày kết thúc phải sau ngày bắt đầu!'),
    ]