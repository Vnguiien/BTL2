# -*- coding: utf-8 -*-
{
    'name': "Quản lý Văn bản",

    'summary': """
        Module số hóa và quản lý văn bản, hồ sơ, tài liệu""",

    'description': """
        Module Quản lý Văn bản cung cấp các tính năng:
        
        * Số hóa toàn bộ hồ sơ, hợp đồng, báo giá, tài liệu pháp lý
        * Gắn văn bản vào hồ sơ khách hàng để tra cứu tập trung
        * Quản lý văn bản đến/đi trong công ty
        * Phân loại văn bản theo danh mục
        * Quản lý mẫu văn bản
        * Theo dõi lịch sử thay đổi văn bản
        * Tích hợp với module Nhân sự và Quản lý Khách hàng
    """,

    'author': "Doanh nghiệp",
    'website': "http://www.yourcompany.com",
    'license': 'LGPL-3',

    'category': 'Document Management',
    'version': '15.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'nhan_su', 'quan_ly_khach_hang'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/category_data.xml',
        'views/van_ban.xml',
        'views/van_ban_category.xml',
        'views/van_ban_template.xml',
        'views/customer_van_ban.xml',
        'views/reports.xml',
        'views/menu.xml',
        'data/demo.xml',
    ],
    
    'assets': {
        'web.assets_backend': [
            'quan_ly_van_ban/static/src/css/custom.css',
        ],
    },
    
    # only loaded in demonstration mode
    'demo': [],
    
    'application': True,
    'installable': True,
    'auto_install': False,
}

