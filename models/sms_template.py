from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class SmsTemplate(models.Model):
    """SMS Templates for automated notifications"""
    _name = 'sms.template'
    _description = 'SMS Template'
    _order = 'name'
    
    # Câmpuri SIMPLE, fără related sau complicated
    name = fields.Char(
        string='Template Name',
        required=True,
        help='e.g., "Repair Started", "Repair Completed"'
    )
    
    template_type = fields.Selection([
        ('repair_start', 'Repair Start'),
        ('repair_done', 'Repair Done'),
        ('repair_custom', 'Custom Repair'),
        ('general', 'General')
    ], string='Template Type', default='general', required=True)
    
    body = fields.Text(
        string='Message Body',
        required=True,
        default='Hello {customer_name}, your repair #{repair_name} is ready.',
        help='''Available variables: {repair_name}, {customer_name}, {product_name}, 
        {repair_time}, {amount_total}, {technician}, {date_start}, {date_done}'''
    )
    
    active = fields.Boolean(
        string='Active',
        default=True
    )
    
    # Metoda pentru template-uri default
    @api.model
    def create_default_templates(self):
        """Create default SMS templates"""
        if not self.search_count([]):
            default_templates = [
                {
                    'name': 'Repair Started',
                    'template_type': 'repair_start',
                    'body': 'Hello {customer_name}, repair #{repair_name} has started. Estimated time: {repair_time}.'
                },
                {
                    'name': 'Repair Completed', 
                    'template_type': 'repair_done',
                    'body': 'Hello {customer_name}, repair #{repair_name} is completed. Total: {amount_total}. Thank you!'
                }
            ]
            
            for vals in default_templates:
                self.create(vals)
            
            _logger.info("Created default SMS templates")
        
        return True
    
    def render_template(self, context=None):
        """Render template with context variables"""
        self.ensure_one()
        
        if not context:
            context = {}
        
        # Simple string replacement
        rendered = self.body
        for key, value in context.items():
            placeholder = '{' + key + '}'
            rendered = rendered.replace(placeholder, str(value))
        
        return rendered
