{
    'name': 'Webhook Integration',
    'version': '1.0',
    'author': 'Toni Guerra',
    'category': 'Tools',
    'description': 'Destinado a poder enviar webhooks customizados desde '
        'distintos modulos [account.move, product.product, purchase_order, res_partner, sale_order, stock_picking]'
        'y logs que registran el mensaje y la respuesta del webhook enviado',
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
    ],
    'installable': True,
    'application': True,
    'license': 'OPL-1',  # Odoo Proprietary License
    'price': 99.00,  # Set a price for the module
    'currency': 'EUR',  # Currency for the price
}
