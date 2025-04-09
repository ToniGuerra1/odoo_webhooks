{
    'name': 'Webhook Integration',
    'version': '1.0',
    'author': 'Toni Guerra',
    'category': 'Tools',
    'description': """
🔗 Webhook Integration for Odoo

Send real-time data from Odoo to any external system using Webhooks. Ideal for API integrations, workflow automation with tools like Zapier or Make, or syncing with external CRMs and ERPs.

🎯 Supported Models:
- Sales Orders (sale.order)
- Purchase Orders (purchase.order)
- Invoices (account.move)
- Stock Transfers (stock.picking)
- Products (product.product)
- Contacts (res.partner)

🧩 Key Features:
- Centralized configuration for multiple webhooks
- Select which fields to send and generate JSON dynamically
- Manual send button available per record
- Supports multiple endpoints
- Handles relational fields and date formatting
- Configurable timeout per webhook

⚙️ Installation:
1. Download the .zip file from apps.odoo.com
2. Extract the folder into your Odoo addons directory
3. Restart the Odoo server
4. Update the Apps list
5. Search and install "Webhook Integration"

📄 License: OPL-1 (Odoo Proprietary License v1.0)
- Valid for one production database per license
- Code is non-distributable and non-editable
- No support or warranty included
- Provided "as is", no refunds

🧑‍💻 Author: Toni Guerra
""",


    'depends': [
        'base',
        'product',
        'sale',
        'account',
        'stock',
        'purchase',
        'contacts',
    ],
    'data': [
        'security/webhook_config_access.xml',
        'views/webhook_config_views.xml',
        'views/product_product_views.xml',
        'views/sale_order_inherit_views.xml',
        'views/purchase_order_inherit_views.xml',
        'views/res_partner_inherit_views.xml',
        'views/stock_picking_inherit_views.xml',
        'views/account_move_inherit_views.xml',
        'views/webhook_log_views.xml',
        'views/webhook_config_validate_views.xml',
        'static/description/icon.png',
    ],
    'installable': True,
    'application': True,
    'license': 'OPL-1',  # Odoo Proprietary License
    'price': 99.00,  # Set a price for the module
    'currency': 'EUR',  # Currency for the price
}
