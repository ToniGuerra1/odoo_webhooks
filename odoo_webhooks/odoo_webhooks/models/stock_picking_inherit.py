from odoo import api, fields, models
import requests
import json
from datetime import datetime, date
from odoo.exceptions import ValidationError, UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    webhook_config_id = fields.Many2one(
        'webhook.config',
        string='Webhook',
        help='Selecciona el Webhook que quieres enviar para este movimiento de stock.'
    )

    def action_send_webhook_from_picking(self):
        """ Envía un webhook con los datos del movimiento de stock. """

        license_status = self.env['ir.config_parameter'].sudo().get_param('webhook.license_status', 'invalid')
        if license_status != 'valid':
            raise UserError("La licencia no es válida. No se puede enviar el Webhook.")
        
        for picking in self:
            if picking.webhook_config_id:
                config = picking.webhook_config_id
                data = {}

                for f in config.field_ids:
                    value = getattr(picking, f.name, False)
                    data[f.name] = self._convert_to_serializable(value)

                json_data = json.dumps(data, indent=4)
                headers = {'Content-Type': 'application/json'}

                try:
                    response = requests.post(config.endpoint, data=json_data.encode('utf-8'), headers=headers, timeout=config.timeout)
                    if response.status_code == 200:
                        picking.message_post(body="Webhook enviado con éxito.")
                    else:
                        picking.message_post(body=f"Error al enviar webhook. Código: {response.status_code}")
                except requests.exceptions.RequestException as e:
                    picking.message_post(body=f"Error al enviar webhook: {e}")
            else:
                picking.message_post(body="No se ha seleccionado ningún Webhook Config.")

    def _convert_to_serializable(self, value):
        """Convierte valores Odoo a formatos serializables en JSON."""
        if isinstance(value, models.Model):
            return value.id if value else False  # Retornamos ID si es un modelo Odoo

        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d %H:%M:%S')  # Formato legible para JSON

        if isinstance(value, date):
            return value.strftime('%Y-%m-%d')  # Formato fecha sin hora

        return value  # Para otros tipos, se retorna tal cual
