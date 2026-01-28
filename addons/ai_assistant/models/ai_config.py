from odoo import models, fields, api


class AIConfig(models.Model):
    """Cấu hình AI Settings - Sử dụng OpenRouter"""
    _name = 'ai.config'
    _description = 'Cấu hình AI'
    _rec_name = 'name'

    name = fields.Char("Tên cấu hình", default="AI Configuration", required=True)
    api_key = fields.Char("OpenRouter API Key", required=True, 
                          help="Nhập API Key từ openrouter.ai/keys")
    ai_model = fields.Selection([
        ('xiaomi/mimo-v2-flash:free', 'Xiaomi MiMo V2 Flash (Miễn phí)'),
        ('google/gemini-2.0-flash-exp:free', 'Google Gemini 2.0 Flash (Miễn phí)'),
        ('meta-llama/llama-3.3-70b-instruct:free', 'Meta Llama 3.3 70B (Miễn phí)'),
        ('qwen/qwen-2.5-72b-instruct:free', 'Qwen 2.5 72B (Miễn phí)'),
        ('deepseek/deepseek-chat-v3-0324:free', 'DeepSeek Chat V3 (Miễn phí)'),
        ('openai/gpt-3.5-turbo', 'OpenAI GPT-3.5 Turbo (Trả phí)'),
        ('openai/gpt-4-turbo', 'OpenAI GPT-4 Turbo (Trả phí)'),
        ('anthropic/claude-3-haiku', 'Claude 3 Haiku (Trả phí)'),
    ], string="Mô hình AI", default='xiaomi/mimo-v2-flash:free', required=True)
    
    max_tokens = fields.Integer("Max Tokens", default=1000,
                                help="Số token tối đa cho mỗi response")
    temperature = fields.Float("Temperature", default=0.7,
                               help="Độ sáng tạo của AI (0-1)")
    
    is_active = fields.Boolean("Kích hoạt", default=True)
    
    # Thống kê sử dụng
    total_requests = fields.Integer("Tổng số request", default=0, readonly=True)
    last_request_date = fields.Datetime("Lần request cuối", readonly=True)
    
    # Giới hạn
    daily_limit = fields.Integer("Giới hạn/ngày", default=100)
    monthly_limit = fields.Integer("Giới hạn/tháng", default=3000)

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Chỉ được phép có một cấu hình AI!')
    ]

    def action_test_connection(self):
        """Test kết nối API"""
        self.ensure_one()
        ai_service = self.env['ai.service']
        result = ai_service.call_ai("Xin chào, hãy trả lời ngắn gọn bằng tiếng Việt: Bạn là AI gì?")
        
        # Update thống kê
        self.write({
            'total_requests': self.total_requests + 1,
            'last_request_date': fields.Datetime.now()
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Kết quả test kết nối OpenRouter',
                'message': result[:300] if len(result) > 300 else result,
                'type': 'success' if not result.startswith('❌') else 'warning',
                'sticky': True,
            }
        }

    @api.model
    def get_config(self):
        """Lấy cấu hình hiện tại"""
        config = self.search([('is_active', '=', True)], limit=1)
        if not config:
            config = self.search([], limit=1)
        return config
