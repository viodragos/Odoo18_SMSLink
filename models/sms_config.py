from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import requests
import logging

_logger = logging.getLogger(__name__)

class SmsLinkConfig(models.Model):
    _name = 'sms.link.config'
    _description = 'SMSLink Configuration'
    _rec_name = 'connection_id'
    
    # Câmpuri pentru configurație
    connection_id = fields.Char(
        string='Connection ID',
        required=True,
        help='Connection ID obținut de pe SMSLink.ro'
    )
    
    password = fields.Char(
        string='Password',
        required=True,
        help='Parola pentru conexiunea SMSLink'
    )
    
    sender = fields.Char(
        string='Sender',
        default='SMSLink',
        help='Numele expeditorului (max 11 caractere)'
    )
    
    use_ssl = fields.Boolean(
        string='Use SSL',
        default=False,
        help='Folosește conexiune securizată HTTPS'
    )
    
    credit = fields.Float(
        string='Credit Available',
        readonly=True,
        digits=(16, 2),
        help='Credit rămas în cont (actualizat periodic)'
    )
    
    last_check = fields.Datetime(
        string='Last Credit Check',
        readonly=True
    )
    
    active = fields.Boolean(
        string='Active',
        default=True
    )

    test_phone = fields.Char(string="Test Phone", help="Phone number for test SMS")
    test_message = fields.Char(string="Test Message", default="Test SMS from Odoo")

    def action_send_test(self):
        """Trimite SMS de test folosind câmpurile de test"""
        for config in self:
            if not config.test_phone:
                raise ValidationError(_("Please enter a test phone number!"))
            
            message = config.test_message or "Test SMS from Odoo SMSLink"
            
            success, response, history_id = config.send_sms(
                phone_number=config.test_phone,
                message=message
            )
            
            if success:
                # Mesaj de succes
                pass
    
    # Validare sender
    @api.constrains('sender')
    def _check_sender_length(self):
        for config in self:
            if config.sender and len(config.sender) > 11:
                raise ValidationError(_('Sender name cannot exceed 11 characters!'))
    
    # Funcția principală de trimitere SMS
    def send_sms(self, phone_number, message, config_id=None):
        """
        Trimite un SMS prin SMSLink API
        
        :param phone_number: Numărul de telefon (format: 07xxxxxxxx)
        :param message: Conținutul mesajului
        :param config_id: ID-ul configurației (dacă None, folosește prima activă)
        :return: Tuple (success, response_text, sms_history_id)
        """
        # Găsește configurația
        if config_id:
            config = self.browse(config_id)
        else:
            config = self.search([('active', '=', True)], limit=1)
        
        if not config:
            return False, _('No active SMSLink configuration found!'), None
        
        # Pregătește URL-ul API
        base_url = 'https://secure.smslink.ro' if config.use_ssl else 'http://www.smslink.ro'
        api_url = f"{base_url}/sms/gateway/communicate/index.php"
        
        # Parametrii pentru API
        params = {
            'connection_id': config.connection_id,
            'password': config.password,
            'to': phone_number,
            'message': message
        }
        
        # Adaugă sender dacă este specificat
        if config.sender:
            params['sender'] = config.sender
        
        _logger.info(f"Sending SMS to {phone_number}: {message[:50]}...")
        
        try:
            # Trimite cererea către API
            response = requests.get(api_url, params=params, timeout=30)
            response_text = response.text.strip()
            
            # Verifică răspunsul
            if response.status_code == 200:
                # Aici facem defalcarea sugerată de tine
                if response_text.startswith('MESSAGE'):
                    final_status = 'sent'
                    success = True
                else:
                    # Acoperă ERROR;... dar și orice alt răspuns dubios la 200
                    final_status = 'failed'
                    success = False
                # Log 200
                _logger.info(f"SMSLink API 200 - Final Status: {final_status}. Response: {response_text}")
                
                # Creează înregistrare în istoric
                history_id = self.env['sms.history'].create({
                    'config_id': config.id,
                    'phone_number': phone_number,
                    'message': message,
                    'response': response_text,
                    'status': final_status,
                    'credit_used': self._calculate_credit_used(message) if final_status == 'sent' else 0.0
                })
                
                return success, response_text, history_id.id
            else:
                _logger.error(f"SMS sending failed. Status: {response.status_code}, Response: {response_text}")
                
                # Log error
                self.env['sms.history'].create({
                    'config_id': config.id,
                    'phone_number': phone_number,
                    'message': message,
                    'response': f"Error {response.status_code}: {response_text}",
                    'status': 'failed'
                })
                
                return False, response_text, None
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            _logger.error(error_msg)
            
            self.env['sms.history'].create({
                'config_id': config.id,
                'phone_number': phone_number,
                'message': message,
                'response': error_msg,
                'status': 'failed'
            })
            
            return False, error_msg, None
    
    # Funcție pentru calcularea creditului folosit
    def _calculate_credit_used(self, message):
        """Calculează creditul necesar pentru un mesaj"""
        # SMSLink tarifează pe segment de 160 caractere
        # (Ajustează conform politicii lor de preț)
        segments = len(message) / 160
        if len(message) % 160 > 0:
            segments += 1
        return segments  # sau alt factor de cost
    
    # Funcție pentru verificarea creditului
    @api.model  # ADAUGĂ ACEST DECORATOR
    def check_credit(self):
        """
        Verifică creditul disponibil în contul SMSLink
        (Această funcție va necesita implementare specifică 
        bazată pe API-ul SMSLink pentru verificare credit)
        """
        for config in self:
            try:
                # EXEMPLU - adaptează la API-ul real pentru credit
                # În acest moment, SMSLink nu oferă un endpoint public pentru credit
                # Poți implementa prin scraping sau cerere către suport
                
                # Pentru moment, returnează valoarea existentă
                _logger.info(f"Credit check for config {config.connection_id}")
                
                # Poți seta un credit estimat sau lăsa manual
                # config.write({'last_check': fields.Datetime.now()})
                
                return True
                
            except Exception as e:
                _logger.error(f"Error checking credit: {str(e)}")
                return False
    
    # Funcție pentru a trimite SMS către o înregistrare Odoo
    def send_sms_to_record(self, record, phone_field, message_template, config_id=None):
        """
        Trimite SMS către o înregistrare Odoo
        
        :param record: Înregistrarea Odoo (ex: repair.order)
        :param phone_field: Numele câmpului cu numărul de telefon
        :param message_template: Șablon mesaj (poate conține {field})
        :param config_id: ID configurație
        """
        if not hasattr(record, phone_field):
            return False, _('Phone field not found!'), None
        
        phone_number = getattr(record, phone_field)
        if not phone_number:
            return False, _('No phone number provided!'), None
        
        # Înlocuiește placeholder-ele din șablon
        message = message_template
        for field in record._fields:
            placeholder = '{' + field + '}'
            if placeholder in message:
                field_value = getattr(record, field, '')
                message = message.replace(placeholder, str(field_value))
        
        return self.send_sms(phone_number, message, config_id)
    
    def send_test_sms(self):
        """Trimite un SMS de test către un număr specificat"""
        for config in self:
            # Număr de test implicit sau poți adăuga un câmp în interfață
            test_phone = "07xxxxxxxx"  # Înlocuiește cu un număr real
            
            success, response, history_id = self.send_sms(
                phone_number=test_phone,
                message="Test SMS from Odoo SMSLink Integration",
                config_id=config.id
            )
            
            if success:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Success',
                        'message': f'Test SMS sent successfully! Response: {response}',
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise ValidationError(f'Failed to send test SMS: {response}')