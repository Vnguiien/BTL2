from odoo import models, fields, api
from datetime import datetime

class ProjectTask(models.Model):
    _name = 'project_task'
    _description = 'Bảng chứa thông tin nhiệm vụ'
    _rec_name = 'name'
    _order = 'deadline, priority desc'

    project_task_id = fields.Char("Mã nhiệm vụ", required=True, index=True, copy=False, default="New")
    customer_id = fields.Many2one('customer', string="Khách hàng", required=True, ondelete='cascade')
    name = fields.Char("Tên nhiệm vụ", required=True)
    description = fields.Text("Mô tả chi tiết")
    deadline = fields.Date("Hạn chót", required=True)
    actual_completion_date = fields.Date("Thời gian hoàn thành thực tế")
    
    # Link đến nhân viên từ module nhan_su
    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên phụ trách", ondelete='set null')
    
    # Ưu tiên và trạng thái
    priority = fields.Selection([
        ('0', 'Thấp'),
        ('1', 'Bình thường'),
        ('2', 'Cao'),
        ('3', 'Khẩn cấp')
    ], string="Độ ưu tiên", default='1')
    
    state = fields.Selection([
        ('new', 'Mới'),
        ('in_progress', 'Đang thực hiện'),
        ('done', 'Hoàn thành'),
        ('cancelled', 'Đã hủy')
    ], string="Trạng thái", default='new')
    
    # Computed
    is_overdue = fields.Boolean("Quá hạn", compute="_compute_is_overdue", store=True)
    days_remaining = fields.Integer("Số ngày còn lại", compute="_compute_days_remaining")
    
    active = fields.Boolean("Active", default=True)

    # Trường tính toán để xác định nhiệm vụ có bị quá hạn hay không
    @api.depends('deadline', 'actual_completion_date', 'state')
    def _compute_is_overdue(self):
        today = fields.Date.today()
        for record in self:
            if record.state == 'done':
                record.is_overdue = record.actual_completion_date and record.actual_completion_date > record.deadline
            else:
                record.is_overdue = record.deadline and record.deadline < today and record.state != 'cancelled'

    @api.depends('deadline')
    def _compute_days_remaining(self):
        today = fields.Date.today()
        for record in self:
            if record.deadline:
                record.days_remaining = (record.deadline - today).days
            else:
                record.days_remaining = 0

    @api.model
    def create(self, vals):
        if vals.get('project_task_id', 'New') == 'New':
            vals['project_task_id'] = self.env['ir.sequence'].next_by_code('project_task.sequence') or 'TASK001'
        return super(ProjectTask, self).create(vals)

    # Đặt tên hiển thị cho bản ghi
    def name_get(self):
        result = []
        for record in self:
            name = f"[{record.project_task_id}] {record.name}"
            result.append((record.id, name))
        return result
    
    # Actions
    def action_start(self):
        self.write({'state': 'in_progress'})
    
    def action_done(self):
        self.write({
            'state': 'done',
            'actual_completion_date': fields.Date.today()
        })
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})
