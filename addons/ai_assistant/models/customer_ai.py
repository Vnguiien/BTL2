from odoo import models, fields, api
from odoo.exceptions import UserError


class CustomerAI(models.Model):
    """Extend Customer model với AI Features"""
    _inherit = 'customer'

    # AI Generated Fields
    ai_email_suggestion = fields.Text("Đề xuất email từ AI", readonly=True)
    ai_follow_up_suggestion = fields.Text("Đề xuất follow-up từ AI", readonly=True)
    ai_analysis = fields.Text("Phân tích AI", readonly=True)
    ai_last_update = fields.Datetime("Cập nhật AI lần cuối", readonly=True)

    def _reload_form(self):
        """Helper để reload form sau khi AI xử lý"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'customer',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_ai_suggest_email(self):
        """AI đề xuất nội dung email cho khách hàng"""
        self.ensure_one()
        
        ai_service = self.env['ai.service']
        
        # Xác định loại khách hàng
        customer_type = "Cá nhân" if self.customer_type == 'individual' else "Doanh nghiệp"
        
        # Xác định mục đích dựa trên trạng thái
        if self.customer_status == 'new':
            purpose = "Chào mừng khách hàng mới, giới thiệu dịch vụ"
        elif self.customer_status == 'active':
            if self.total_contracts > 0:
                purpose = "Cảm ơn và đề xuất gia hạn/nâng cấp dịch vụ"
            else:
                purpose = "Follow-up và đề xuất hợp tác"
        else:
            purpose = "Kích hoạt lại khách hàng, ưu đãi đặc biệt"
        
        result = ai_service.suggest_email_content(
            self.customer_name or "Quý khách",
            customer_type,
            purpose
        )
        
        self.write({
            'ai_email_suggestion': result,
            'ai_last_update': fields.Datetime.now()
        })
        
        # Reload form để hiển thị kết quả ngay
        return self._reload_form()

    def action_ai_suggest_follow_up(self):
        """AI đề xuất hành động follow-up"""
        self.ensure_one()
        
        ai_service = self.env['ai.service']
        
        # Thu thập thông tin khách hàng
        customer_info = f"""
        - Tên: {self.customer_name}
        - Loại: {'Cá nhân' if self.customer_type == 'individual' else 'Doanh nghiệp'}
        - Trạng thái: {dict(self._fields['customer_status'].selection).get(self.customer_status, '')}
        - Tổng hợp đồng: {self.total_contracts}
        - Tổng đơn hàng: {self.total_sale_orders}
        - Tổng doanh thu: {self.total_amount:,.0f} VNĐ
        - Số tương tác trong tháng: {self.recent_interactions}
        """
        
        # Lấy lịch sử tương tác gần đây
        recent_interactions = self.interact_ids[:5]
        interaction_history = "\n".join([
            f"- {i.date.strftime('%d/%m/%Y') if i.date else 'N/A'}: {i.subject or 'Không có tiêu đề'}"
            for i in recent_interactions
        ]) or "Chưa có tương tác nào"
        
        result = ai_service.suggest_follow_up(customer_info, interaction_history)
        
        self.write({
            'ai_follow_up_suggestion': result,
            'ai_last_update': fields.Datetime.now()
        })
        
        # Reload form để hiển thị kết quả ngay
        return self._reload_form()

    def action_ai_analyze_customer(self):
        """AI phân tích tổng quan khách hàng"""
        self.ensure_one()
        
        ai_service = self.env['ai.service']
        
        # Thu thập dữ liệu phân tích
        analysis_data = f"""
        THÔNG TIN KHÁCH HÀNG:
        - Mã KH: {self.customer_id}
        - Tên: {self.customer_name}
        - Loại: {'Cá nhân' if self.customer_type == 'individual' else 'Doanh nghiệp'}
        - Công ty: {self.company_name or 'N/A'}
        - Thu nhập: {dict(self._fields['income_level'].selection).get(self.income_level, 'Chưa xác định')}
        
        THỐNG KÊ:
        - Tổng hợp đồng: {self.total_contracts}
        - Tổng báo giá: {self.total_quotations}
        - Tổng đơn hàng: {self.total_sale_orders}
        - Tổng doanh thu: {self.total_amount:,.0f} VNĐ
        - Số tương tác: {self.total_interactions}
        
        Hãy phân tích:
        1. Đánh giá tổng quan khách hàng
        2. Tiềm năng phát triển
        3. Rủi ro cần lưu ý
        4. Chiến lược chăm sóc phù hợp
        """
        
        result = ai_service.call_ai(
            analysis_data,
            "Bạn là chuyên gia phân tích khách hàng. Hãy phân tích và đưa ra đánh giá chi tiết bằng tiếng Việt."
        )
        
        self.write({
            'ai_analysis': result,
            'ai_last_update': fields.Datetime.now()
        })
        
        # Reload form để hiển thị kết quả ngay
        return self._reload_form()

    def action_copy_ai_email(self):
        """Copy nội dung email AI đề xuất"""
        self.ensure_one()
        if not self.ai_email_suggestion:
            raise UserError("Chưa có đề xuất email. Hãy nhấn 'AI Đề xuất Email' trước.")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '📋 Đã copy nội dung',
                'message': 'Nội dung email đã được copy. Paste vào email của bạn.',
                'type': 'info',
            }
        }
