# sale_order_inherit.py
from odoo import api, fields, models
import requests
import json
from datetime import datetime, date
from odoo.exceptions import ValidationError, UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    webhook_config_id = fields.Many2one(
        'webhook.config',
        string='Webhook',
        help='Selecciona el Webhook que quieres enviar para este pedido.'
    )

    def action_send_webhook_from_sale(self):
        """ Envía un webhook con los datos de la orden de venta. """
        license_status = self.env['ir.config_parameter'].sudo().get_param('webhook.license_status', 'invalid')
        if license_status != 'valid':
            raise UserError("La licencia no es válida. No se puede enviar el Webhook.")
        
        for order in self:
            if order.webhook_config_id:
                config = order.webhook_config_id
                data = {}
                # Obtener los campos seleccionados en field_ids
                for f in config.field_ids:
                    value = getattr(order, f.name, False)
                    data[f.name] = self._convert_to_serializable(value)

                json_data = json.dumps(data, indent=4)
                endpoint = config.endpoint
                timeout = config.timeout
                headers = {'Content-Type': 'application/json'}

                try:
                    response = requests.post(
                        endpoint,
                        data=json_data.encode('utf-8'),
                        headers=headers,
                        timeout=timeout
                    )
                    # Crear registro en webhook.log
                    self.env['webhook.log'].create({
                        'webhook_config_id': config.id,
                        'endpoint': endpoint,
                        'request_payload': json_data,
                        'response_content': response.text,
                        'status_code': response.status_code,
                        'success': (response.status_code == 200),
                        'error_message': ''
                    })

                    if response.status_code == 200:
                        order.message_post(body="Webhook enviado con éxito.")
                    else:
                        order.message_post(body=f"No se pudo enviar el webhook. Código: {response.status_code}")
                except requests.exceptions.RequestException as e:
                    # Registrar el error
                    self.env['webhook.log'].create({
                        'webhook_config_id': config.id,
                        'endpoint': endpoint,
                        'request_payload': json_data,
                        'response_content': '',
                        'status_code': 0,
                        'success': False,
                        'error_message': str(e),
                    })
                    order.message_post(body=f"Error al enviar webhook: {e}")
            else:
                order.message_post(body="No se ha seleccionado ningún Webhook Config.")

    def _convert_to_serializable(self, value):
        """Convierte valores Odoo a formatos serializables en JSON."""
        if isinstance(value, models.Model):
            return value.id if value else False  # Retornamos ID si es un modelo Odoo
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d %H:%M:%S')  # Formato legible para JSON
        if isinstance(value, date):
            return value.strftime('%Y-%m-%d')  # Formato fecha sin hora
        return value  # Para otros tipos, se retorna tal cual
