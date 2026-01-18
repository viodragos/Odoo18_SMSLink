from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class PartnerSimpleSMS(models.Model):
    """SIMPLE SMS integration for Partner - NO TEMPLATES"""
    _inherit = 'res.partner'


    def action_open_contact_sms_wizard(self):
        self.ensure_one()
        return {
            'name': 'Trimite SMS (SMSLink)',
            'type': 'ir.actions.act_window',
            'res_model': 'contact.sms.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_partner_id': self.id,
                'default_mobile': self.mobile or self.phone,
            }
        }
