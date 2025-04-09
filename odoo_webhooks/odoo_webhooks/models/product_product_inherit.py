# product_product_inherit.py
import requests
import json
import logging
from datetime import datetime, date
from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = 'product.product'

    webhook_config_id = fields.Many2one(
        'webhook.config',
        string='Webhook',
        help='Selecciona el Webhook que quieres enviar para este producto.'
    )

    def action_send_webhook_from_product(self):
        """Envía el webhook configurado en webhook_config_id y crea un registro en webhook.log."""

        
        for product in self:
            if product.webhook_config_id:
                config = product.webhook_config_id
                data = {}

                # Construimos el dict 'data' en base a los campos configurados
                for f in config.field_ids:
                    value = getattr(product, f.name, False)
                    data[f.name] = self._convert_to_serializable(value)

                json_data_str = json.dumps(data, indent=4)

                endpoint = config.endpoint
                timeout = config.timeout
                headers = {'Content-Type': 'application/json'}

                status_code = None
                response_text = None
                success = False
                error_message = None

                try:
                    response = requests.post(
                        endpoint,
                        data=json_data_str.encode('utf-8'),
                        headers=headers,
                        timeout=timeout
                    )
                    status_code = response.status_code
                    response_text = response.text
                    success = (status_code == 200)

                    if success:
                        product.message_post(body="Webhook enviado con éxito.")
                        _logger.info("Webhook enviado con éxito para el producto %s (ID %s)",
                                     product.display_name, product.id)
                    else:
                        product.message_post(body=f"No se pudo enviar el webhook. Código: {status_code}")
                        _logger.warning("No se pudo enviar el webhook para el producto %s (ID %s). Código: %s",
                                        product.display_name, product.id, status_code)
                except requests.exceptions.RequestException as e:
                    error_message = str(e)
                    product.message_post(body=f"Error al enviar el webhook: {error_message}")
                    _logger.error("Error al enviar el webhook para el producto %s (ID %s): %s",
                                  product.display_name, product.id, error_message)

                # Registrar el envío en webhook.log
                self.env['webhook.log'].create_log(
                    name=f"Envio Webhook Product: {product.id}",
                    endpoint=endpoint,
                    json_data=data,
                    status_code=status_code,
                    response_text=response_text,
                    success=success,
                    error_message=error_message
                )
            else:
                product.message_post(body="No se ha seleccionado ningún Webhook Config.")

    def _convert_to_serializable(self, value):
        """Convierte valores Odoo a formatos serializables en JSON."""
        if isinstance(value, models.Model):
            return value.id if value else False  # Retornamos ID si es un modelo Odoo

        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d %H:%M:%S')  # Formato legible para JSON

        if isinstance(value, date):
            return value.strftime('%Y-%m-%d')  # Formato fecha sin hora

        return value  # Para otros tipos, se retorna tal cual
