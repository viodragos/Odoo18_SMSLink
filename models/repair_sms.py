from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class RepairOrderSimpleSMS(models.Model):
    """SIMPLE SMS integration for Repair Orders - NO TEMPLATES"""
    _inherit = 'repair.order'
    
    # DOAR un câmp pentru tracking
    sms_sent_count = fields.Integer(
        string='SMS Sent',
        readonly=True,
        default=0
    )
    
    def _get_company_name(self):
        """Get company name from Odoo settings"""
        return self.env.company.name or "Our Company"
    
    def _prepare_start_sms_message(self):
        """Prepare start SMS message with details"""
        company = self._get_company_name()
        customer = self.partner_id.name if self.partner_id else "Customer"
        product = self.product_id.name if self.product_id else "product"
        
        # Mesaj îmbunătățit cu detalii
        message = (
            f"{company}: Draga {customer}, "
            f"Reparatia {product} (#{self.name}) a inceput. "
            f"Te vom notifica cand reparatia este finalizata."
            f"Acesta este un mesaj automat, te rugam sa nu raspunzi."
        )
        
        """ # Verifică lungimea (SMS-urile au limită de caractere)
        if len(message) > 160:
            # Versiune scurtată dacă e prea lung
            message = (
                f"{company}: Repair #{self.name} for {product} started. "
                f"We'll notify you when done."
            ) """
        
        return message
    
    def _prepare_done_sms_message(self):
        """Prepare completion SMS message with details"""
        company = self._get_company_name()
        customer = self.partner_id.name if self.partner_id else "Customer"
        product = self.product_id.name if self.product_id else "product"
        #total = self.amount_total or 0
        
        # Mesaj îmbunătățit cu detalii
        message = (
            f"{company}: Draga {customer}, "
            f"Reparatia pentru {product} (#{self.name}) este finalizata. "
            f"Te rugam sa ridici produsul de la sediul nostru."
            f"Acesta este un mesaj automat, te rugam sa nu raspunzi."
        )
        
        # Verifică lungimea
        """ if len(message) > 160:
            message = (
                f"{company}: Repair #{self.name} for {product} completed. "
                f"Total: {total:.2f} RON. Thank you!"
            ) """
        
        return message
    
    # DOAR două metode simple
    def action_send_start_sms_simple(self):
        """Send simple start SMS - NO TEMPLATES"""
        self.ensure_one()
        
        if not self.partner_id:
            raise UserError(_("No customer assigned!"))
        
        phone = self.partner_id.mobile or self.partner_id.phone
        if not phone:
            raise UserError(_("Customer has no phone number!"))
        
         # Folosește mesajul îmbunătățit
        message = self._prepare_start_sms_message()
        
        # Găsește configurația
        sms_config = self.env['sms.link.config'].search([('active', '=', True)], limit=1)
        if not sms_config:
            raise UserError(_("SMSLink not configured!"))
        
        # Trimite SMS
        success, response, history_id = sms_config.send_sms(
            phone_number=phone,
            message=message
        )
        
        if success:
            # Actualizează counter
            self.sms_sent_count += 1
            
            # Adaugă în chatter
            self.message_post(
                body=f"SMS sent to {phone}: Repair started",
                subject="SMS Notification"
            )
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('SMS sent successfully!'),
                    'type': 'success',
                }
            }
        else:
            raise UserError(_('Failed: %s') % response)
    
    def action_send_done_sms_simple(self):
        """Send simple completion SMS - NO TEMPLATES"""
        self.ensure_one()
        
        if not self.partner_id:
            raise UserError(_("No customer assigned!"))
        
        phone = self.partner_id.mobile or self.partner_id.phone
        if not phone:
            raise UserError(_("Customer has no phone number!"))
        
        # Folosește mesajul îmbunătățit
        message = self._prepare_done_sms_message()
        
        # Găsește configurația
        sms_config = self.env['sms.link.config'].search([('active', '=', True)], limit=1)
        if not sms_config:
            raise UserError(_("SMSLink not configured!"))
        
        # Trimite SMS
        success, response, history_id = sms_config.send_sms(
            phone_number=phone,
            message=message
        )
        
        if success:
            # Actualizează counter
            self.sms_sent_count += 1
            
            # Adaugă în chatter
            self.message_post(
                body=f"SMS sent to {phone}: Repair completed",
                subject="SMS Notification"
            )
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('SMS sent successfully!'),
                    'type': 'success',
                }
            }
        else:
            raise UserError(_('Failed: %s') % response)
