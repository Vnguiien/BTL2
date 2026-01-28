# -*- coding: utf-8 -*-
{
    'name': "Quản lý Khách hàng",

    'summary': """
        Module quản lý khách hàng và CRM toàn diện""",

    'description': """
        Module Quản lý Khách hàng cung cấp các tính năng:
        
        * Quản lý thông tin khách hàng (cá nhân và doanh nghiệp)
        * Quản lý cơ hội bán hàng (CRM Lead)
        * Theo dõi tương tác với khách hàng
        * Quản lý báo giá
        * Quản lý đơn hàng
        * Quản lý hợp đồng khách hàng
        * Quản lý phản hồi và đánh giá
        * Quản lý chiến dịch Marketing
        * Tích hợp với module Nhân sự
        * Tích hợp với module Quản lý Văn bản
    """,

    'author': "Doanh nghiệp",
    'website': "http://www.yourcompany.com",
    'license': 'LGPL-3',

    'category': 'Sales/CRM',
    'version': '15.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'nhan_su'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/email_template.xml',
        'data/cron.xml',
        'views/customer.xml',
        'views/crm_lead.xml',
        'views/crm_stage.xml',
        'views/crm_interact.xml',
        'views/contract.xml',
        'views/sale_order.xml',
        'views/quotation.xml',
        'views/note.xml',
        'views/feedback.xml',
        'views/project_task.xml',
        'views/marketing_campaign.xml',
        'views/reports.xml',
        'views/menu.xml',
        'data/demo.xml',  # Dữ liệu mẫu
    ],
    
    'assets': {
        'web.assets_backend': [
            'quan_ly_khach_hang/static/src/css/custom.css',
        ],
    },
    
    # only loaded in demonstration mode
    'demo': [],
    
    'application': True,
    'installable': True,
    'auto_install': False,
}

