from odoo import api, fields, models

class OdooAPISynchroServer(models.Model):

    _name = "api.odoo.synchro.server"
    _description = "Synchronized server"

    name = fields.Char(string='Server name', required=True)
    server_url = fields.Char(required=True)
    server_port = fields.Integer(required=True, default=8069)
    server_db = fields.Char('Server Database', required=True)
    login = fields.Char('User Name', required=True)
    password = fields.Char(required=True)
    obj_ids = fields.One2many('api.odoo.synchro.obj', 'server_id', 'Models',
                              ondelete='cascade')


class OdooAPISynchroObj(models.Model):
    _name = "api.odoo.synchro.obj"
    _description = "Register Class"
    _order = 'sequence'

    name = fields.Char(required=True)
    domain = fields.Char(required=True, default='[]')
    server_id = fields.Many2one('api.odoo.synchro.server', 'Server',
                                required=True, ondelete='cascade')
    model_id = fields.Many2one('ir.model', 'Object to synchronize',
                               required=True)
    action = fields.Selection(
        [('d', 'Download'),
         ('u', 'Upload'),
         ('b', 'Both')], 'Synchronization direction', required=True,
        default='d')
    sequence = fields.Integer()
    active = fields.Boolean(default=True)
    synchronize_date = fields.Datetime('Latest Synchronization')
    line_id = fields.One2many('api.odoo.synchro.obj.line', 'obj_id',
                              'IDs Affected', ondelete='cascade')
    avoid_ids = fields.One2many('api.odoo.synchro.obj.avoid', 'obj_id',
                                'Fields Not Sync.')

    @api.model
    def get_ids(self, obj, dt, domain=None, action=None):
        action = {} if action is None else action
        if dt:
            domain = domain + ['|', ('write_date', '>=', dt),
                               ('create_date', '>=', dt)]
        return [(o.write_date or o.create_date, o.id,
                 action.get('action', 'd'))
                for o in self.env[obj].search(domain)]


class OdooAPISynchroObjAvoid(models.Model):
    _name = "api.odoo.synchro.obj.avoid"
    _description = "Fields to not synchronize"

    field_id = fields.Many2one('ir.model.fields')
    name = fields.Char('Field Name', related='field_id.name', store=True)
    obj_id = fields.Many2one('api.odoo.synchro.obj', 'Object',
                             required=True, ondelete='cascade')
    model_id = fields.Many2one('ir.model')

class OdooAPISynchroObjLine(models.Model):
    _name = "api.odoo.synchro.obj.line"
    _description = "Synchronized instances"

    name = fields.Datetime('Date', required=True,
                           default=fields.Datetime.now())
    obj_id = fields.Many2one('api.odoo.synchro.obj', 'Object',
                             ondelete='cascade')
    local_id = fields.Integer(readonly=True)
    remote_id = fields.Integer(readonly=True)
