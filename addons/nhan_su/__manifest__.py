# -*- coding: utf-8 -*-
{
    'name': "Quản lý Nhân sự",

    'summary': """
        Module quản lý nhân sự toàn diện cho doanh nghiệp""",

    'description': """
        Module Quản lý Nhân sự cung cấp các tính năng:
        
        * Quản lý thông tin nhân viên đầy đủ
        * Quản lý phòng ban với cấu trúc phân cấp
        * Quản lý chức vụ và mức lương
        * Quản lý hợp đồng lao động
        * Theo dõi lịch sử làm việc
        * Tích hợp với các module khác trong hệ thống
    """,

    'author': "Doanh nghiệp",
    'website': "http://www.yourcompany.com",
    'license': 'LGPL-3',

    'category': 'Human Resources',
    'version': '15.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/nhan_vien.xml',
        'views/lich_su_lam_viec.xml',
        'views/chuc_vu.xml',
        'views/phong_ban.xml',
        'views/hop_dong_lao_dong.xml',
        'views/reports.xml',
        'views/menu.xml',
        'data/demo.xml',  # Dữ liệu mẫu
    ],
    
    'assets': {
        'web.assets_backend': [
            'nhan_su/static/src/css/custom.css',
        ],
    },
    
    # only loaded in demonstration mode
    'demo': [],
    
    'application': True,
    'installable': True,
    'auto_install': False,
}

