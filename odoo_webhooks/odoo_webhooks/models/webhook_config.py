from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError
import json
import requests
from datetime import datetime, date

class WebhookConfig(models.Model):
    _name = 'webhook.config'
    _description = 'Webhooks Configuration'

    name = fields.Char(string='Name', required=True)
    endpoint = fields.Char(string='Endpoint', required=True)
    model_id = fields.Many2one("ir.model", help="Model Id", string="Model")

    field_ids = fields.Many2many('ir.model.fields', string='Fields',
                                 domain="[('model_id', '=', model_id), ('store', '=', True)]")
    json_editable = fields.Text(string='JSON Example')
    timeout = fields.Integer(string='Timeout (s)', default=30)
    
    @api.onchange('field_ids') 
    def _onchange_field_ids(self):
        """Al cambiar los campos seleccionados, regeneramos el JSON."""
        if self.model_id and self.field_ids:
            model_obj = self.env[self.model_id.model]
            # Tomamos el primer registro del modelo para mostrar ejemplo 
            # o dejamos un dict vacío si no hay registros.
            record = model_obj.search([], limit=1)
            data = {}
            for f in self.field_ids:
                value = getattr(record, f.name, False) if record else False
                # Convertir a un tipo serializable
                data[f.name] = self._convert_to_serializable(value)
            self.json_editable = json.dumps(data, indent=4)
        else:
            self.json_editable = "{}"
    
    def _convert_to_serializable(self, value):
        """Convierte valores Odoo a formatos serializables en JSON."""
        if isinstance(value, models.Model):
            return value.id if value else False  # Retornamos ID si es un modelo Odoo

        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d %H:%M:%S')  # Formato legible para JSON

        if isinstance(value, date):
            return value.strftime('%Y-%m-%d')  # Formato fecha sin hora

        return value  # Para otros tipos, se retorna tal cual

    def action_send_webhook(self):
        """Método para enviar el webhook con el JSON actual."""
        # Aquí se podría usar el módulo requests de Odoo (disponible en Odoo 17).
        # Ejemplo con la librería interna de Odoo:


    

        import requests
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(
                self.endpoint,
                data=self.json_editable.encode('utf-8'),
                headers=headers,
                timeout=self.timeout
            )
            # Podrías agregar lógica para manejar respuesta
            if response.status_code == 200:
                # Hacer algo si el webhook se envía con éxito
                pass
            else:
                # Registrar error o mensaje
                pass
        except requests.exceptions.RequestException as e:
            # Manejo de errores de conexión o timeout
            pass

