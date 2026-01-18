from odoo import models, fields, api, _
from odoo.exceptions import UserError


# În noul fișier sms_compose_contact_wizard.py
class ContactSmsWizard(models.TransientModel):
    _name = 'contact.sms.wizard'
    _description = 'Trimite SMS din Contact'

    partner_id = fields.Many2one('res.partner', string='Contact')
    mobile = fields.Char(string='Număr Telefon', required=True)
    body = fields.Text(string='Mesaj', required=True)

    def action_send_sms(self):
        # Aici apelăm logica ta de trimitere deja salvată în repo
        sms_config = self.env['sms.link.config'].search([('active', '=', True)], limit=1)
        if not sms_config:
            raise UserError("SMSLink nu este configurat!")
            
        success, response, history_id = sms_config.send_sms(
            phone_number=self.mobile,
            message=self.body
        )
        if success:
            self.partner_id.message_post(body=f"SMS trimis via SMSLink: {self.body}")
            return {'type': 'ir.actions.client', 'tag': 'display_notification', 
                    'params': {'title': 'Succes', 'message': 'SMS trimis!', 'type': 'success'}}
