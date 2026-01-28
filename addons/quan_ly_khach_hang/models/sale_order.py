from odoo import models, fields, api

class SaleOrder(models.Model):
    _name = 'sale_order'
    _description = 'Đơn hàng / Lịch sử giao dịch'
    _rec_name = 'sale_order_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_order desc'

    sale_order_id = fields.Char("Mã đơn hàng", required=True, index=True, copy=False, default="New")
    sale_order_name = fields.Char("Tên đơn hàng")
    customer_id = fields.Many2one('customer', string="Khách hàng", required=True, ondelete='cascade', tracking=True)
    date_order = fields.Datetime("Ngày đặt hàng", required=True, default=fields.Datetime.now, tracking=True)
    
    # Nhân viên bán hàng từ module nhan_su
    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên bán hàng", ondelete='set null', tracking=True)
    
    # Giá trị đơn hàng
    amount_untaxed = fields.Float("Thành tiền chưa thuế", compute="_compute_amount", store=True)
    amount_tax = fields.Float("Thuế", compute="_compute_amount", store=True)
    amount_total = fields.Float("Tổng giá trị", compute="_compute_amount", store=True, tracking=True)
    currency_id = fields.Many2one('res.currency', string="Tiền tệ", 
                                   default=lambda self: self.env.company.currency_id)
    
    # Chi tiết đơn hàng
    order_line_ids = fields.One2many('sale_order_line', 'order_id', string="Chi tiết đơn hàng")
    
    # Thanh toán
    payment_method = fields.Selection([
        ('cash', 'Tiền mặt'),
        ('bank_transfer', 'Chuyển khoản'),
        ('credit_card', 'Thẻ tín dụng'),
        ('cod', 'COD'),
        ('other', 'Khác')
    ], string="Phương thức thanh toán", default='bank_transfer')
    
    payment_state = fields.Selection([
        ('not_paid', 'Chưa thanh toán'),
        ('partial', 'Thanh toán một phần'),
        ('paid', 'Đã thanh toán')
    ], string="Trạng thái thanh toán", default='not_paid', tracking=True)
    
    # Trạng thái đơn hàng
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã xác nhận'),
        ('processing', 'Đang xử lý'),
        ('shipped', 'Đã giao'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Đã hủy')
    ], string="Trạng thái", default='draft', tracking=True)
    
    # Liên kết
    quotation_id = fields.Many2one('quotation', string="Báo giá gốc", ondelete='set null')
    contract_id = fields.Many2one('contract', string="Hợp đồng liên quan", ondelete='set null')
    
    # Ghi chú
    note = fields.Text("Ghi chú")
    
    active = fields.Boolean("Active", default=True)

    _sql_constraints = [
        ('sale_order_id_unique', 'unique(sale_order_id)', 'Mã đơn hàng phải là duy nhất!'),
    ]

    @api.depends('order_line_ids.subtotal', 'order_line_ids.tax_amount')
    def _compute_amount(self):
        for record in self:
            amount_untaxed = sum(record.order_line_ids.mapped('subtotal'))
            amount_tax = sum(record.order_line_ids.mapped('tax_amount'))
            record.amount_untaxed = amount_untaxed
            record.amount_tax = amount_tax
            record.amount_total = amount_untaxed + amount_tax

    @api.model
    def create(self, vals):
        if vals.get('sale_order_id', 'New') == 'New':
            vals['sale_order_id'] = self.env['ir.sequence'].next_by_code('sale_order.sequence') or 'SO001'
        return super(SaleOrder, self).create(vals)

    # Đặt tên hiển thị cho bản ghi
    def name_get(self):
        result = []
        for record in self:
            name = f"[{record.sale_order_id}] {record.sale_order_name or record.customer_id.customer_name}"
            result.append((record.id, name))
        return result
    
    # Actions
    def action_confirm(self):
        self.write({'state': 'confirmed'})
    
    def action_process(self):
        self.write({'state': 'processing'})
    
    def action_ship(self):
        self.write({'state': 'shipped'})
    
    def action_complete(self):
        self.write({'state': 'completed', 'payment_state': 'paid'})
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})


class SaleOrderLine(models.Model):
    _name = 'sale_order_line'
    _description = 'Chi tiết đơn hàng'
    
    order_id = fields.Many2one('sale_order', string="Đơn hàng", required=True, ondelete='cascade')
    product_name = fields.Char("Tên sản phẩm/Dịch vụ", required=True)
    description = fields.Text("Mô tả")
    quantity = fields.Float("Số lượng", default=1.0)
    uom = fields.Char("Đơn vị", default="Cái")
    unit_price = fields.Float("Đơn giá", required=True)
    discount = fields.Float("Chiết khấu (%)", default=0.0)
    tax_rate = fields.Float("Thuế (%)", default=10.0)
    
    subtotal = fields.Float("Thành tiền", compute="_compute_subtotal", store=True)
    tax_amount = fields.Float("Tiền thuế", compute="_compute_subtotal", store=True)
    
    @api.depends('quantity', 'unit_price', 'discount', 'tax_rate')
    def _compute_subtotal(self):
        for record in self:
            price_after_discount = record.unit_price * (1 - record.discount / 100)
            subtotal = record.quantity * price_after_discount
            record.subtotal = subtotal
            record.tax_amount = subtotal * record.tax_rate / 100
