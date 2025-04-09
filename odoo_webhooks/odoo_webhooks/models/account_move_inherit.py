from odoo import api, fields, models
import requests
import json
from datetime import datetime, date
from odoo.exceptions import ValidationError, UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    webhook_config_id = fields.Many2one(
        'webhook.config',
        string='Webhook',
        help='Selecciona el Webhook que quieres enviar para esta factura.'
    )

    def action_send_webhook_from_invoice(self):
        """ Envía un webhook con los datos de la factura y registra el log. """
        
        for invoice in self:
            if invoice.webhook_config_id:
                config = invoice.webhook_config_id
                data = {}

                # Construimos el diccionario de datos
                for f in config.field_ids:
                    value = getattr(invoice, f.name, False)
                    data[f.name] = self._convert_to_serializable(value)

                json_data = json.dumps(data, indent=4)
                headers = {'Content-Type': 'application/json'}

                try:
                    response = requests.post(
                        config.endpoint,
                        data=json_data.encode('utf-8'),
                        headers=headers,
                        timeout=config.timeout
                    )

                    # Crear registro en webhook.log sea éxito o error
                    self.env['webhook.log'].create({
                        'webhook_config_id': config.id,
                        'endpoint': config.endpoint,
                        'request_payload': json_data,
                        'response_content': response.text,
                        'status_code': response.status_code,
                        'success': (response.status_code == 200),
                        'error_message': '',
                    })

                    if response.status_code == 200:
                        invoice.message_post(body="Webhook enviado con éxito.")
                    else:
                        invoice.message_post(body=f"Error al enviar webhook. Código: {response.status_code}")

                except requests.exceptions.RequestException as e:
                    # Registrar en el log si hubo excepción (error de conexión, timeout, etc.)
                    self.env['webhook.log'].create({
                        'webhook_config_id': config.id,
                        'endpoint': config.endpoint,
                        'request_payload': json_data,
                        'response_content': '',
                        'status_code': 0,
                        'success': False,
                        'error_message': str(e),
                    })
                    invoice.message_post(body=f"Error al enviar webhook: {e}")
            else:
                invoice.message_post(body="No se ha seleccionado ningún Webhook Config.")

    def _convert_to_serializable(self, value):
        """Convierte valores Odoo a formatos serializables en JSON."""
        if isinstance(value, models.Model):
            return value.id if value else False  # Retorna ID si es un registro de Odoo
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(value, date):
            return value.strftime('%Y-%m-%d')
        return value
