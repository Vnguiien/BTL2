from odoo import models, fields, api
import re


class VanBanAI(models.Model):
    """Extend Văn bản model với AI Features"""
    _inherit = 'van_ban'

    # AI Generated Fields
    ai_summary = fields.Text("Tóm tắt AI", readonly=True)
    ai_suggested_category = fields.Char("Danh mục đề xuất AI", readonly=True)
    ai_key_points = fields.Text("Điểm chính AI", readonly=True)
    ai_last_update = fields.Datetime("Cập nhật AI lần cuối", readonly=True)

    def _reload_form(self):
        """Helper để reload form sau khi AI xử lý"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'van_ban',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_ai_summarize(self):
        """AI tóm tắt nội dung văn bản"""
        self.ensure_one()
        
        ai_service = self.env['ai.service']
        
        # Lấy nội dung cần tóm tắt
        content = self.noi_dung or self.trich_yeu or ""
        
        # Loại bỏ HTML tags nếu có
        clean_content = re.sub(r'<[^>]+>', '', content)
        
        if not clean_content.strip():
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '⚠️ Không có nội dung',
                    'message': 'Văn bản chưa có nội dung để tóm tắt',
                    'type': 'warning',
                }
            }
        
        result = ai_service.summarize_text(clean_content)
        
        self.write({
            'ai_summary': result,
            'ai_last_update': fields.Datetime.now()
        })
        
        # Reload form để hiển thị kết quả ngay
        return self._reload_form()

    def action_ai_classify(self):
        """AI phân loại văn bản tự động"""
        self.ensure_one()
        
        ai_service = self.env['ai.service']
        
        # Lấy nội dung để phân loại
        content = f"""
        Tiêu đề: {self.ten_van_ban}
        Số hiệu: {self.so_hieu or 'N/A'}
        Trích yếu: {self.trich_yeu or 'N/A'}
        Nội dung: {re.sub(r'<[^>]+>', '', self.noi_dung or '')[:1000]}
        """
        
        suggested_type = ai_service.classify_document(content)
        
        # Map sang tên tiếng Việt
        type_names = {
            'hop_dong': 'Hợp đồng',
            'bao_gia': 'Báo giá',
            'phap_ly': 'Tài liệu pháp lý',
            'van_ban_den': 'Văn bản đến',
            'van_ban_di': 'Văn bản đi',
            'noi_bo': 'Văn bản nội bộ',
            'tai_lieu': 'Tài liệu kỹ thuật',
            'khac': 'Khác'
        }
        
        self.write({
            'ai_suggested_category': f"{type_names.get(suggested_type, 'Khác')} ({suggested_type})",
            'ai_last_update': fields.Datetime.now()
        })
        
        # Reload form để hiển thị kết quả ngay
        return self._reload_form()

    def action_ai_extract_key_points(self):
        """AI trích xuất điểm chính từ văn bản"""
        self.ensure_one()
        
        ai_service = self.env['ai.service']
        
        content = self.noi_dung or self.trich_yeu or ""
        clean_content = re.sub(r'<[^>]+>', '', content)
        
        if not clean_content.strip():
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '⚠️ Không có nội dung',
                    'message': 'Văn bản chưa có nội dung để phân tích',
                    'type': 'warning',
                }
            }
        
        prompt = f"""Phân tích văn bản sau và trích xuất:
        1. Các điểm chính (bullet points)
        2. Các bên liên quan
        3. Các mốc thời gian quan trọng (nếu có)
        4. Các số liệu quan trọng (nếu có)
        
        Văn bản:
        {clean_content[:3000]}
        """
        
        result = ai_service.call_ai(
            prompt,
            "Bạn là chuyên gia phân tích văn bản. Trích xuất thông tin quan trọng bằng tiếng Việt."
        )
        
        self.write({
            'ai_key_points': result,
            'ai_last_update': fields.Datetime.now()
        })
        
        # Reload form để hiển thị kết quả ngay
        return self._reload_form()

    def action_ai_apply_classification(self):
        """Áp dụng phân loại AI đề xuất"""
        self.ensure_one()
        
        if not self.ai_suggested_category:
            return
        
        # Trích xuất loại từ đề xuất
        match = re.search(r'\((\w+)\)', self.ai_suggested_category)
        if match:
            suggested_type = match.group(1)
            if suggested_type in dict(self._fields['loai_van_ban'].selection).keys():
                self.write({'loai_van_ban': suggested_type})
                
                # Reload form để hiển thị kết quả ngay
                return self._reload_form()
