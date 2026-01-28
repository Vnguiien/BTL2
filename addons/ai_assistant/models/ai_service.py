from odoo import models, fields, api
import logging
import requests
import json

_logger = logging.getLogger(__name__)

# OpenRouter API Endpoint
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


class AIService(models.AbstractModel):
    """Service class để gọi OpenRouter AI APIs"""
    _name = 'ai.service'
    _description = 'AI Service'

    def _get_api_key(self):
        """Lấy API key từ cấu hình"""
        config = self.env['ai.config'].search([], limit=1)
        return config.api_key if config else ''

    def _get_model(self):
        """Lấy model AI từ cấu hình"""
        config = self.env['ai.config'].search([], limit=1)
        return config.ai_model if config else 'xiaomi/mimo-v2-flash:free'

    def call_ai(self, prompt, system_message=None, max_tokens=1000):
        """
        Gọi API OpenRouter để xử lý prompt
        
        Args:
            prompt: Nội dung cần xử lý
            system_message: Chỉ dẫn cho AI
            max_tokens: Số token tối đa
            
        Returns:
            str: Kết quả từ AI
        """
        api_key = self._get_api_key()
        
        if not api_key:
            return "⚠️ Chưa cấu hình API Key. Vui lòng vào AI Assistant > Cấu hình > AI Settings để thiết lập OpenRouter API Key."
        
        try:
            model = self._get_model()
            
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8069",  # Odoo URL
                "X-Title": "Odoo AI Assistant"
            }
            
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.7,
            }
            
            response = requests.post(
                OPENROUTER_API_URL,
                headers=headers,
                data=json.dumps(payload),
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content'].strip()
                else:
                    return "❌ Không nhận được phản hồi từ AI."
            elif response.status_code == 401:
                return "❌ API Key không hợp lệ. Vui lòng kiểm tra lại OpenRouter API Key."
            elif response.status_code == 429:
                return "❌ Đã vượt quá giới hạn API. Vui lòng thử lại sau."
            else:
                error_msg = response.json().get('error', {}).get('message', response.text)
                return f"❌ Lỗi API ({response.status_code}): {error_msg}"
            
        except requests.exceptions.Timeout:
            return "❌ Timeout - AI đang quá tải, vui lòng thử lại."
        except requests.exceptions.ConnectionError:
            return "❌ Không thể kết nối tới OpenRouter. Kiểm tra kết nối mạng."
        except Exception as e:
            _logger.error(f"AI Error: {str(e)}")
            return f"❌ Lỗi khi gọi AI: {str(e)}"

    def summarize_text(self, text, language='vi'):
        """Tóm tắt văn bản"""
        if not text:
            return "Không có nội dung để tóm tắt."
            
        system_message = """Bạn là trợ lý AI chuyên tóm tắt văn bản. 
        Hãy tóm tắt ngắn gọn, súc tích và giữ lại các ý chính.
        Trả lời bằng tiếng Việt."""
        
        prompt = f"Hãy tóm tắt nội dung sau trong khoảng 3-5 câu:\n\n{text}"
        
        return self.call_ai(prompt, system_message)

    def suggest_email_content(self, customer_name, customer_type, purpose):
        """Đề xuất nội dung email cho khách hàng"""
        system_message = """Bạn là chuyên gia viết email kinh doanh chuyên nghiệp.
        Hãy viết email ngắn gọn, lịch sự và hiệu quả.
        Trả lời bằng tiếng Việt."""
        
        prompt = f"""Viết nội dung email cho khách hàng với thông tin sau:
        - Tên khách hàng: {customer_name}
        - Loại khách hàng: {customer_type}
        - Mục đích email: {purpose}
        
        Hãy viết email chuyên nghiệp, lịch sự và phù hợp với văn hóa Việt Nam."""
        
        return self.call_ai(prompt, system_message)

    def analyze_opportunity(self, lead_info):
        """Phân tích cơ hội bán hàng"""
        system_message = """Bạn là chuyên gia phân tích bán hàng.
        Hãy phân tích cơ hội và đưa ra đánh giá, đề xuất.
        Trả lời bằng tiếng Việt."""
        
        prompt = f"""Phân tích cơ hội bán hàng sau và đề xuất hành động:
        {lead_info}
        
        Hãy đưa ra:
        1. Đánh giá xác suất thành công (%)
        2. Điểm mạnh của cơ hội
        3. Rủi ro tiềm ẩn
        4. Đề xuất hành động tiếp theo"""
        
        return self.call_ai(prompt, system_message)

    def classify_document(self, document_content):
        """Phân loại văn bản tự động"""
        system_message = """Bạn là chuyên gia phân loại tài liệu.
        Hãy phân loại văn bản vào một trong các loại sau:
        - hop_dong: Hợp đồng
        - bao_gia: Báo giá
        - phap_ly: Tài liệu pháp lý
        - van_ban_den: Văn bản đến
        - van_ban_di: Văn bản đi
        - noi_bo: Văn bản nội bộ
        - tai_lieu: Tài liệu kỹ thuật
        - khac: Khác
        
        Chỉ trả lời bằng mã loại văn bản (VD: hop_dong)."""
        
        prompt = f"Phân loại văn bản sau:\n\n{document_content[:2000]}"
        
        result = self.call_ai(prompt, system_message, max_tokens=50)
        
        # Normalize kết quả
        valid_types = ['hop_dong', 'bao_gia', 'phap_ly', 'van_ban_den', 'van_ban_di', 'noi_bo', 'tai_lieu', 'khac']
        for vt in valid_types:
            if vt in result.lower():
                return vt
        return 'khac'

    def suggest_follow_up(self, customer_info, interaction_history):
        """Đề xuất hành động follow-up cho khách hàng"""
        system_message = """Bạn là chuyên gia CRM và chăm sóc khách hàng.
        Hãy đề xuất hành động tiếp theo dựa trên thông tin khách hàng.
        Trả lời bằng tiếng Việt."""
        
        prompt = f"""Dựa trên thông tin khách hàng sau, đề xuất hành động follow-up:
        
        Thông tin khách hàng:
        {customer_info}
        
        Lịch sử tương tác gần đây:
        {interaction_history}
        
        Hãy đề xuất:
        1. Hành động tiếp theo cần làm
        2. Thời điểm phù hợp
        3. Nội dung trao đổi gợi ý"""
        
        return self.call_ai(prompt, system_message)
