from odoo import api, fields, models
import requests
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class WebhookConfigValidate(models.Model):
    _name = 'webhook.config.validate'
    _description = 'Validación de Webhooks'

    license_key = fields.Char("License Key")
    email = fields.Char("Email")
    license_status = fields.Selection([
        ('valid', 'Valid'),
        ('invalid', 'Invalid'),
    ], string='License Status', readonly=True, default='invalid')

    def action_check_license(self):
        """Llama al endpoint WP para activar la licencia (si está disponible + email coincide)."""
        if not self.license_key or not self.email:
            raise UserError("Por favor, ingresa la clave y el email.")

        validation_url = "https://cursosmanresa.es/wp-json/license-api/v1/activate"  # Ajustar
        payload = {
            'license_key': self.license_key,
            'email': self.email,
            'product': 'toni_webhook'
        }
        try:
            response = requests.post(validation_url, json=payload, timeout=10)
            _logger.info("Activating license: code=%s, text=%s", response.status_code, response.text)

            if response.status_code == 200:
                # WP devolvió OK => Marcamos la licencia como válida
                self.license_status = 'valid'
                # Guardamos en ir.config_parameter, etc.
                self.env['ir.config_parameter'].sudo().set_param('webhook.license_key', self.license_key)
                self.env['ir.config_parameter'].sudo().set_param('webhook.license_status', 'valid')
                return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': "Licencia activada con éxito.",
                        'type': 'rainbow_man',
                    },
                    'type': 'ir.actions.act_window_close',
                }
            else:
                # 400 => no se activó
                self.license_status = 'invalid'
                self.env['ir.config_parameter'].sudo().set_param('webhook.license_key', self.license_key)
                self.env['ir.config_parameter'].sudo().set_param('webhook.license_status', 'invalid')
                raise UserError("La licencia no se pudo activar. Verifica que esté 'Disponible' y que el email coincida.")

        except requests.exceptions.RequestException as e:
            self.license_status = 'invalid'
            raise UserError(f"Error de conexión: {e}")