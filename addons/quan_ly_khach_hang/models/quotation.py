from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date, timedelta

class Quotation(models.Model):
    _name = 'quotation'
    _description = 'Báo giá'
    _rec_name = 'quotation_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    quotation_id = fields.Char("Mã báo giá", required=True, index=True, copy=False, default="New")
    quotation_name = fields.Char("Tên báo giá", compute="_compute_quotation_name", store=True)
    customer_id = fields.Many2one('customer', string="Khách hàng", required=True, ondelete='cascade', tracking=True)
    
    # Nhân viên lập báo giá từ module nhan_su
    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên lập báo giá", ondelete='set null', tracking=True)
    
    # Thời gian
    create_date = fields.Datetime("Ngày tạo", default=fields.Datetime.now, readonly=True)
    validity_date = fields.Date("Ngày hết hiệu lực", required=True, 
                                 default=lambda self: date.today() + timedelta(days=30), tracking=True)
    
    # Chi tiết báo giá
    quotation_line_ids = fields.One2many('quotation_line', 'quotation_id', string="Chi tiết báo giá")
    
    # Giá trị
    amount_untaxed = fields.Float("Thành tiền chưa thuế", compute="_compute_amount", store=True)
    amount_tax = fields.Float("Thuế", compute="_compute_amount", store=True)
    amount_total = fields.Float("Tổng giá trị", compute="_compute_amount", store=True, tracking=True)
    currency_id = fields.Many2one('res.currency', string="Tiền tệ", 
                                   default=lambda self: self.env.company.currency_id)
    
    # Chiết khấu tổng
    global_discount = fields.Float("Chiết khấu tổng (%)", default=0.0)
    global_discount_amount = fields.Float("Số tiền chiết khấu", compute="_compute_amount", store=True)
    amount_after_discount = fields.Float("Tổng sau chiết khấu", compute="_compute_amount", store=True)
    
    # Điều khoản thanh toán
    payment_term = fields.Selection([
        ('immediate', 'Thanh toán ngay'),
        ('15_days', '15 ngày'),
        ('30_days', '30 ngày'),
        ('45_days', '45 ngày'),
        ('60_days', '60 ngày'),
        ('custom', 'Tùy chỉnh')
    ], string="Điều khoản thanh toán", default='30_days')
    payment_term_note = fields.Text("Chi tiết điều khoản thanh toán")
    
    # Trạng thái
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('sent', 'Đã gửi'),
        ('accepted', 'Được chấp nhận'),
        ('rejected', 'Bị từ chối'),
        ('expired', 'Hết hạn'),
        ('cancelled', 'Đã hủy')
    ], string="Trạng thái", default='draft', tracking=True)
    
    # Điều kiện và ghi chú
    terms_conditions = fields.Text("Điều khoản và điều kiện")
    notes = fields.Text("Ghi chú")
    
    # File đính kèm
    file_attachment = fields.Binary("File báo giá", attachment=True)
    file_name = fields.Char("Tên file")
    
    # Liên kết
    sale_order_ids = fields.One2many('sale_order', 'quotation_id', string="Đơn hàng tạo từ báo giá")
    contract_ids = fields.One2many('contract', 'quotation_id', string="Hợp đồng tạo từ báo giá")
    
    # Computed
    is_expired = fields.Boolean("Đã hết hạn", compute="_compute_is_expired", store=True)
    days_until_expiry = fields.Integer("Số ngày còn hiệu lực", compute="_compute_days_until_expiry")
    
    active = fields.Boolean("Active", default=True)

    _sql_constraints = [
        ('quotation_id_unique', 'unique(quotation_id)', 'Mã báo giá phải là duy nhất!'),
    ]

    @api.depends('customer_id', 'quotation_id')
    def _compute_quotation_name(self):
        for record in self:
            if record.customer_id:
                record.quotation_name = f"Báo giá - {record.customer_id.customer_name}"
            else:
                record.quotation_name = f"Báo giá {record.quotation_id}"

    @api.depends('quotation_line_ids.subtotal', 'quotation_line_ids.tax_amount', 'global_discount')
    def _compute_amount(self):
        for record in self:
            amount_untaxed = sum(record.quotation_line_ids.mapped('subtotal'))
            amount_tax = sum(record.quotation_line_ids.mapped('tax_amount'))
            total_before_discount = amount_untaxed + amount_tax
            global_discount_amount = total_before_discount * record.global_discount / 100
            
            record.amount_untaxed = amount_untaxed
            record.amount_tax = amount_tax
            record.amount_total = total_before_discount
            record.global_discount_amount = global_discount_amount
            record.amount_after_discount = total_before_discount - global_discount_amount

    @api.depends('validity_date', 'state')
    def _compute_is_expired(self):
        today = date.today()
        for record in self:
            if record.validity_date and record.state not in ['accepted', 'rejected', 'cancelled']:
                record.is_expired = record.validity_date < today
            else:
                record.is_expired = False

    @api.depends('validity_date')
    def _compute_days_until_expiry(self):
        today = date.today()
        for record in self:
            if record.validity_date:
                record.days_until_expiry = (record.validity_date - today).days
            else:
                record.days_until_expiry = 0

    @api.model
    def create(self, vals):
        if vals.get('quotation_id', 'New') == 'New':
            vals['quotation_id'] = self.env['ir.sequence'].next_by_code('quotation.sequence') or 'BG001'
        return super(Quotation, self).create(vals)

    # Đặt tên hiển thị cho bản ghi
    def name_get(self):
        result = []
        for record in self:
            name = f"[{record.quotation_id}] {record.quotation_name or ''}"
            result.append((record.id, name))
        return result
    
    # Actions
    def action_send(self):
        """Gửi báo giá cho khách hàng"""
        self.write({'state': 'sent'})
    
    def action_accept(self):
        """Khách hàng chấp nhận báo giá"""
        self.write({'state': 'accepted'})
    
    def action_reject(self):
        """Khách hàng từ chối báo giá"""
        self.write({'state': 'rejected'})
    
    def action_cancel(self):
        """Hủy báo giá"""
        self.write({'state': 'cancelled'})
    
    def action_draft(self):
        """Đưa về nháp"""
        self.write({'state': 'draft'})
    
    def action_create_sale_order(self):
        """Tạo đơn hàng từ báo giá"""
        self.ensure_one()
        if self.state != 'accepted':
            raise ValidationError("Chỉ có thể tạo đơn hàng từ báo giá đã được chấp nhận!")
        
        # Tạo order lines
        order_lines = []
        for line in self.quotation_line_ids:
            order_lines.append((0, 0, {
                'product_name': line.product_name,
                'description': line.description,
                'quantity': line.quantity,
                'uom': line.uom,
                'unit_price': line.unit_price,
                'discount': line.discount,
                'tax_rate': line.tax_rate,
            }))
        
        sale_order = self.env['sale_order'].create({
            'customer_id': self.customer_id.id,
            'nhan_vien_id': self.nhan_vien_id.id if self.nhan_vien_id else False,
            'quotation_id': self.id,
            'order_line_ids': order_lines,
            'note': self.notes,
        })
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Đơn hàng',
            'res_model': 'sale_order',
            'res_id': sale_order.id,
            'view_mode': 'form',
        }
    
    def action_create_contract(self):
        """Tạo hợp đồng từ báo giá"""
        self.ensure_one()
        if self.state != 'accepted':
            raise ValidationError("Chỉ có thể tạo hợp đồng từ báo giá đã được chấp nhận!")
        
        contract = self.env['contract'].create({
            'customer_id': self.customer_id.id,
            'nhan_vien_id': self.nhan_vien_id.id if self.nhan_vien_id else False,
            'quotation_id': self.id,
            'contract_value': self.amount_after_discount,
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=365),
            'terms': self.terms_conditions,
        })
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Hợp đồng',
            'res_model': 'contract',
            'res_id': contract.id,
            'view_mode': 'form',
        }

    def action_view_orders(self):
        """Xem đơn hàng được tạo từ báo giá này"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Đơn hàng từ {self.quotation_id}',
            'res_model': 'sale_order',
            'view_mode': 'tree,form',
            'domain': [('quotation_id', '=', self.id)],
            'context': {'default_quotation_id': self.id, 'default_customer_id': self.customer_id.id}
        }
    
    def action_view_contracts(self):
        """Xem hợp đồng được tạo từ báo giá này"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Hợp đồng từ {self.quotation_id}',
            'res_model': 'contract',
            'view_mode': 'tree,form',
            'domain': [('quotation_id', '=', self.id)],
            'context': {'default_quotation_id': self.id, 'default_customer_id': self.customer_id.id}
        }

    @api.model
    def check_expired_quotations(self):
        """Scheduled action: Kiểm tra và cập nhật báo giá hết hạn"""
        today = date.today()
        expired_quotations = self.search([
            ('state', 'in', ['draft', 'sent']),
            ('validity_date', '<', today)
        ])
        expired_quotations.write({'state': 'expired'})
        return True


class QuotationLine(models.Model):
    _name = 'quotation_line'
    _description = 'Chi tiết báo giá'
    
    quotation_id = fields.Many2one('quotation', string="Báo giá", required=True, ondelete='cascade')
    sequence = fields.Integer("Thứ tự", default=10)
    product_name = fields.Char("Tên sản phẩm/Dịch vụ", required=True)
    description = fields.Text("Mô tả")
    quantity = fields.Float("Số lượng", default=1.0)
    uom = fields.Char("Đơn vị", default="Cái")
    unit_price = fields.Float("Đơn giá", required=True)
    discount = fields.Float("Chiết khấu (%)", default=0.0)
    tax_rate = fields.Float("Thuế VAT (%)", default=10.0)
    
    subtotal = fields.Float("Thành tiền", compute="_compute_subtotal", store=True)
    tax_amount = fields.Float("Tiền thuế", compute="_compute_subtotal", store=True)
    total = fields.Float("Tổng cộng", compute="_compute_subtotal", store=True)
    
    @api.depends('quantity', 'unit_price', 'discount', 'tax_rate')
    def _compute_subtotal(self):
        for record in self:
            price_after_discount = record.unit_price * (1 - record.discount / 100)
            subtotal = record.quantity * price_after_discount
            tax_amount = subtotal * record.tax_rate / 100
            record.subtotal = subtotal
            record.tax_amount = tax_amount
            record.total = subtotal + tax_amount
