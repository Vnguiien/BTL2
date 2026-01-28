# -*- coding: utf-8 -*-
{
    'name': "AI Assistant",

    'summary': """
        Tích hợp AI vào hệ thống quản lý - Sử dụng OpenRouter""",

    'description': """
        Module AI Assistant cung cấp các tính năng:
        
        * AI Tóm tắt văn bản thông minh
        * AI Đề xuất nội dung email cho khách hàng
        * AI Phân tích cơ hội bán hàng
        * AI Đề xuất hành động tiếp theo
        * Tích hợp OpenRouter API (Hỗ trợ nhiều model miễn phí)
        
        Các model miễn phí được hỗ trợ:
        - Xiaomi MiMo V2 Flash
        - Google Gemini 2.0 Flash
        - Meta Llama 3.3 70B
        - Qwen 2.5 72B
        - DeepSeek Chat V3
    """,

    'author': "Doanh nghiệp",
    'website': "http://www.yourcompany.com",
    'license': 'LGPL-3',

    'category': 'Productivity',
    'version': '15.0.1.0.1',

    # Phụ thuộc vào các module khác
    'depends': ['base', 'mail', 'quan_ly_khach_hang', 'quan_ly_van_ban'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ai_config.xml',
        'views/ai_assistant.xml',
        'views/customer_ai.xml',
        'views/van_ban_ai.xml',
        'views/menu.xml',
    ],
    
    'demo': [],
    
    'application': True,
    'installable': True,
    'auto_install': False,
    
    # Chỉ cần requests, đã có sẵn trong Python
    'external_dependencies': {
        'python': ['requests'],
    },
}
