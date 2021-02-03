from odoo import api, fields, models, _
from xmlrpc.client import ServerProxy
from odoo.exceptions import Warning
import logging
import time
import threading

_logger = logging.getLogger(__name__)

class RPCProxyOne(object):

    def __init__(self, server, ressource):
        """Class to store one RPC proxy server."""
        self.server = server
        local_url = 'http://%s:%d/xmlrpc/common' % (server.server_url,
                                                    server.server_port)
        try:
            rpc = ServerProxy(local_url, allow_none=True)
            self.uid = rpc.login(server.server_db, server.login,
                                 server.password)
        except Exception as e:
            raise Warning(_(e))
        local_url = 'http://%s:%d/xmlrpc/object' % (server.server_url,
                                                    server.server_port)
        self.rpc = ServerProxy(local_url, allow_none=True)
        self.ressource = ressource

    def __getattr__(self, name):
        return lambda *args: self.rpc.execute(
            self.server.server_db, self.uid, self.server.password,
            self.ressource, name, *args)


class RPCProxy(object):

    def __init__(self, server):
        self.server = server

    def get(self, ressource):
        return RPCProxyOne(self.server, ressource)

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

    # Method to check connection
    def check_connection(self):
        # Check connection by calling RPXProxy class
        pool1 = RPCProxy(self)
        # Define Model name from which want to get data
        module = pool1.get('ir.module.module')
        # Call search_count or search method to get data
        if module.search_count([("name", "ilike", "base_synchro"),
                                ('state', '=', 'installed')]) < 1:
            raise Warning(_('If your Synchronization direction is \
                                 download and/or upload, please install \
                                 "API Odoo XMLRPC - Sync data" module in targeted \
                                 server!'))
        else:
            raise Warning(_("Connection test successed!"))


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
    cron_id = fields.Many2one('ir.cron', "Scheduled Action")

    report = []
    report_total = 0
    report_create = 0
    report_write = 0

    @api.model
    def get_id(self, object_id, id, action):
        synch_line_obj = self.env['api.odoo.synchro.obj.line']
        field_src = (action == 'u') and 'local_id' or 'remote_id'
        field_dest = (action == 'd') and 'local_id' or 'remote_id'
        synch_line_rec = synch_line_obj.search_read(
            [('obj_id', '=', object_id), (field_src, '=', id)], [field_dest])
        return synch_line_rec and synch_line_rec[0][field_dest] or False

    @api.model
    def relation_transform(self, pool_src, pool_dest, obj_model, res_id,
                           action, destination_inverted):
        if not res_id:
            return False
        _logger.debug("Relation transform")
        self._cr.execute('''select o.id from api_odoo_synchro_obj o left join
                            ir_model m on (o.model_id =m.id) where
                            m.model=%s and o.active''', (obj_model,))
        obj = self._cr.fetchone()
        result = False
        if obj:
            result = self.get_id(obj[0], res_id, action)
            _logger.debug(
                "Relation object already synchronized. Getting id %s",
                result)
        else:
            _logger.debug('Relation object not synchronized. Searching \
                 by name_get and name_search')
            if not destination_inverted:
                names = pool_src.get(obj_model).name_get([res_id])[0][1]
                res = pool_dest.env[obj_model].name_search(
                    names, [], 'like', 1)
                res = res and res[0][0] or False
            else:
                pool = pool_src.env[obj_model]
                names = pool.browse([res_id]).name_get()[0][1]
                try:
                    rec_name = pool_src.env[obj_model]._rec_name
                    res = pool_dest.get(obj_model).search(
                        [(rec_name, '=', names)], 1)
                    res = res and res[0] or False
                except Exception as e:
                    raise Warning(_(e))

            _logger.debug("name_get in src: %s", names)
            _logger.debug("name_search in dest: %s", res)
            if res:
                result = res
            else:
                _logger.warning(
                    "Record '%s' on relation %s not found, set to null.",
                    names, obj_model)
                _logger.warning(
                    "You should consider synchronize this model '%s'",
                    obj_model)
                self.report.append(
                    'WARNING: Record "%s" on relation %s not found, set to\
                     null.' % (names, obj_model))
        return result

    @api.model
    def data_transform(self, pool_src, pool_dest, obj, data, action=None,
                       destination_inverted=False, avoid_fields=[]):
        if action is None:
            action = {}
        if not destination_inverted:
            fields = pool_src.get('ir.model.fields').search_read(
                [('model_id.model', '=', obj),
                 ('name', 'not in', avoid_fields)],
                ['name', 'ttype', 'relation'])
        else:
            fields = pool_src.env['ir.model.fields'].search_read(
                [('model_id.model', '=', obj),
                 ('name', 'not in', avoid_fields)],
                ['name', 'ttype', 'relation'])
        _logger.debug("Transforming data")
        for field in fields:
            ftype = field.get('ttype')
            fname = field.get('name')
            if fname in avoid_fields:
                del data[fname]
            if ftype in ('function', 'one2many', 'one2one'):
                _logger.debug("Field %s of type %s, discarded.", fname, ftype)
                del data[fname]
            elif ftype == 'many2one':
                _logger.debug("Field %s is many2one", fname)
                if (isinstance(data[fname], list)) and data[fname]:
                    fdata = data[fname][0]
                else:
                    fdata = data[fname]
                df = self.relation_transform(pool_src, pool_dest,
                                             field.get('relation'), fdata,
                                             action, destination_inverted)
                data[fname] = df
                if not data[fname]:
                    del data[fname]
            elif ftype == 'many2many':
                data[fname] = [(6, 0, [
                    rec for rec in
                    map(lambda res: self.relation_transform(
                        pool_src, pool_dest, field.get(
                            'relation'),
                        res, action, destination_inverted),
                        data[fname]) if rec])]
        del data['id']
        return data

    def synchronize(self, server, object):
        sync_ids = []
        pool1 = RPCProxy(server)
        pool2 = self
        dt = object.synchronize_date
        module = pool1.get('ir.module.module')
        model_obj = object.model_id.model
        avoid_field_list = [a.name for a in object.avoid_ids]
        if module.search_count([("name", "ilike", "base_synchro"),
                                ('state', '=', 'installed')]) < 1:
            raise Warning(_('If your Synchronization direction is \
                          download and/or upload, please install \
                          "API Odoo XMLRPC - Sync data" module in targeted \
                          server!'))
        if object.action in ('d', 'b'):
            sync_ids = pool1.get('api.odoo.synchro.obj').get_ids(
                model_obj, dt, eval(object.domain), {'action': 'd'})
        if object.action in ('u', 'b'):
            _logger.debug("Getting ids to synchronize [%s] (%s)",
                          object.synchronize_date, object.domain)

            sync_ids += pool2.env['api.odoo.synchro.obj'].get_ids(
                model_obj, dt, eval(object.domain), {'action': 'u'})
        for dt, sync_id, action in sync_ids:
            destination_inverted = False
            if action == 'd':
                pool_src = pool1
                pool_dest = pool2
            else:
                pool_src = pool2
                pool_dest = pool1
                destination_inverted = True
            if not destination_inverted:
                value = pool_src.get(object.model_id.model).search_read(
                    [('id', '=', sync_id)])[0]
            else:
                pool = pool_src.env[object.model_id.model]
                value = pool.search_read([('id', '=', sync_id)])[0]
            avoid_field_list += ['create_date', 'write_date']

            field_vals = dict([(key, val[0] if isinstance(val, tuple)
                                else val) for key, val in filter(
                lambda i: i[0] not in avoid_field_list, value.items())])

            value = self.data_transform(
                pool_src, pool_dest, object.model_id.model, field_vals, action,
                destination_inverted, avoid_field_list)
            id2 = self.get_id(object.id, sync_id, action)
            if id2:
                _logger.debug("Updating model %s [%d]", object.model_id.name,
                              id2)
                if not destination_inverted:
                    pool = pool_dest.env[object.model_id.model]
                    pool.browse([id2]).update(value)
                else:
                    pool_dest.get(object.model_id.model).write(id2, value)
                self.report_total += 1
                self.report_write += 1
            else:
                _logger.debug("Creating model %s", object.model_id.name)
                try:
                    if not destination_inverted:
                        new_id = pool_dest.env[object.model_id.model
                                               ].create(value).id
                    else:
                        new_id = pool_dest.get(
                            object.model_id.model).create(value)
                except Exception as e:
                    raise Warning(_(e))
                self.env['api.odoo.synchro.obj.line'].create({
                    'obj_id': object.id,
                    'local_id': (action == 'u') and sync_id or new_id,
                    'remote_id': (action == 'd') and sync_id or new_id
                })
                self.report_total += 1
                self.report_create += 1
        return True

    @api.multi
    def upload_download(self, object_id):
        object = self.env['api.odoo.synchro.obj'].browse(object_id)
        self.report = []
        start_date = fields.Datetime.now()
        server = object.server_id
        # for obj_rec in server.obj_ids:
        _logger.debug("Start synchro of %s", object.name)
        self.synchronize(server, object)
        if object.action == 'b':
            time.sleep(1)
        object.write({'synchronize_date': fields.Datetime.now()})
        end_date = fields.Datetime.now()

        # Creating res.request for summary results
        request = self.env['res.request']
        if not self.report:
            self.report.append('No exception.')
        summary = '''Here is the synchronization report:
    
    Synchronization started: %s
    Synchronization finished: %s
    
    Synchronized records: %d
    Records updated: %d
    Records created: %d
    
    Exceptions:
            ''' % (start_date, end_date, self.report_total, self.report_write,
                   self.report_create)
        summary += '\n'.join(self.report)
        request.create({
            'name': "Synchronization report",
            'date': fields.Datetime.now(),
            'body': summary,
        })
        return {}

    def sync_data(self, object_id):
        threaded_synchronization = threading.Thread(
            target=self.upload_download(object_id))
        threaded_synchronization.run()

    @api.model
    def create(self, vals):
        res = super(OdooAPISynchroObj, self).create(vals)
        if res:
            model_id = self.env['ir.model'].search([('model', '=', 'api.odoo.synchro.obj')])
            cron_val = {
                'name': 'Sync Object ' + res.name,
                'model_id': model_id.id,
                'state': 'code',
                'code': 'model.sync_data(%s)' % res.id
            }
            cron = self.env['ir.cron'].create(cron_val)
            res.cron_id = cron.id
        return res

    @api.multi
    def write(self, vals):
        res = super(OdooAPISynchroObj, self).write(vals)
        if vals.get('name'):
            for object in self:
                if object.cron_id:
                    name = vals.get('name') or object.name
                    object.cron_id.name = 'Sync Object ' + name
        return res

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
    name = fields.Char('Field Name', required=True, related='field_id.name')
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
