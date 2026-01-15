from odoo import models, fields, api

class SmsHistory(models.Model):
    _name = 'sms.history'
    _description = 'SMS History'
    _order = 'send_date desc'
    
    config_id = fields.Many2one(
        'sms.link.config',
        string='SMSLink Config',
        required=True,
        ondelete='cascade'
    )
    
    phone_number = fields.Char(
        string='Phone Number',
        required=True
    )
    
    message = fields.Text(
        string='Message',
        required=True
    )
    
    response = fields.Text(
        string='API Response'
    )
    
    status = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('delivered', 'Delivered')
    ], string='Status', default='draft')
    
    send_date = fields.Datetime(
        string='Send Date',
        default=fields.Datetime.now
    )
    
    credit_used = fields.Float(
        string='Credit Used',
        digits=(16, 3)
    )
    
    related_model = fields.Char(
        string='Related Model'
    )
    
    related_record_id = fields.Integer(
        string='Related Record ID'
    )
    
    # Funcție pentru reîncercare
    def retry_send(self):
        """Reîncearcă trimiterea unui SMS eșuat"""
        for history in self:
            if history.status == 'failed':
                success, response, new_history_id = history.config_id.send_sms(
                    history.phone_number,
                    history.message
                )
                
                if success:
                    history.status = 'sent'
                    history.response = response
                    history.send_date = fields.Datetime.now()
