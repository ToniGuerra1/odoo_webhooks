# webhook_log.py
import json
from odoo import api, fields, models

class WebhookLog(models.Model):
    _name = 'webhook.log'
    _description = 'Registro de Webhooks Enviados'
    _order = 'create_date desc'

    name = fields.Char(string='Nombre', required=True)
    endpoint = fields.Char(string='Endpoint', required=True)
    json_data = fields.Text(string='JSON Enviado')
    status_code = fields.Integer(string='Código de Respuesta')
    response_text = fields.Text(string='Respuesta')
    success = fields.Boolean(string='¿Envío Exitoso?', default=False)
    error_message = fields.Text(string='Mensaje de Error')
    create_date = fields.Datetime(string='Fecha de Envío', default=fields.Datetime.now, readonly=True)

    @api.model
    def create_log(self, name, endpoint, json_data,
                   status_code=None, response_text=None,
                   success=False, error_message=None):
        """
        Helper para crear un registro de log.
        Recibe el JSON como dict (recomendado) o cualquier tipo que sea serializable
        """
        if not isinstance(json_data, (dict, list)):
            # Si recibimos un string, lo dejamos tal cual
            json_str = str(json_data)
        else:
            # Convertimos a texto con identado
            json_str = json.dumps(json_data, indent=4)

        return self.create({
            'name': name,
            'endpoint': endpoint,
            'json_data': json_str,
            'status_code': status_code,
            'response_text': response_text,
            'success': success,
            'error_message': error_message,
        })
