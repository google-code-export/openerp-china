# -*- encoding: utf-8 -*-
##############################################################################
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields

class account_account(osv.osv):
    _inherit = 'account.account'
    """
    替换account对象的name_get方法，显示科目名称的时候也显示父级的科目名称
    例如 “100902 其他货币资金/银行本票”
    """ 
    def name_get(self, cr, uid, ids, context={}):
        if not len(ids):
            return []
        reads = self.read(cr, uid, ids, ['name', 'code','parent_id'], context)
        res = []
        for record in reads:
            name = record['name']
            if record['code']:
                #添加父节点[Joshua]
                if record['parent_id']:
                    account_parent_id = record['parent_id'][0]
                    while account_parent_id:
                            parent_obj = self.read(cr, uid, account_parent_id, ['name', 'parent_id'], context)
                            name = parent_obj['name'] + '/'+name
                            if  parent_obj['parent_id']:
                                account_parent_id = parent_obj['parent_id'][0]
                            else:
                                account_parent_id = False
                #添加父节点[Joshua]
            name = record['code'] + ' '+name
            res.append((record['id'], name))
        return res

account_account()

class account_move(osv.osv):
    _inherit = 'account.move'
    """
    替换account.move对象的post方法
    凭证审核后生成的凭证号按相同期间连续编号
    """
    def post(self, cr, uid, ids, context=None):
        if self.validate(cr, uid, ids, context) and len(ids):
            for move in self.browse(cr, uid, ids):
            #凭证按月编号[wjfonhand]
                new_name = ''
                posted_moves = self.search(cr, uid, [('period_id', '=', move.period_id.id),
                                                     ('journal_id.sequence_id', '=', move.journal_id.sequence_id.id),
                                                     ('state', '=', 'posted')])
                prefix = move.journal_id.sequence_id.prefix and move.journal_id.sequence_id.prefix or ''
                suffix = move.journal_id.sequence_id.suffix and move.journal_id.sequence_id.suffix or ''
                new_name = prefix + '%%0%sd' % move.journal_id.sequence_id.padding % (len(posted_moves)+1) + suffix
                self.write(cr, uid, [move.id], {'name':new_name})
            #凭证按月编号[wjfonhand]
            cr.execute('update account_move set state=%s where id in ('+','.join(map(str,ids))+')', ('posted',))
        else:
            raise osv.except_osv(_('Integrity Error !'), _('You can not validate a non-balanced entry !'))
        return True
    """
    添加制单、审核、附件数三个字段
    """
    _columns = {
        'write_uid':fields.many2one('res.users', '审核', readonly=True),
        'create_uid':fields.many2one('res.users', '制单', readonly=True, select=True),      
        'attachment_count':fields.integer('附件数', required=True, help='该记账凭证对应的原始凭证数量'),
    }
    """
    附件数默认为1张
    凭证业务类型默认为总帐     
    """
    _defaults = {
        'attachment_count': lambda *args: 1,
        'journal_id': lambda self, cr, uid, context:self.pool.get('account.journal').search(cr, uid, [('type', '=', 'general')], limit=1)[0]
    }

account_move()

class config_allow_negative(osv.osv_memory):
    _name = 'oecn_account.config.allow_negative'
    _columns = {
        'name': fields.char('Name', size=64),
        'allow': fields.selection([
            ('yes', '用'),
            ('no', '不用')
        ], '贵公司是否使用负数金额的凭证', required=True,
           help="OpenERP默认不支持负数凭证，这里可以设置为支持，以满足中国用户需要")
    }
    _defaults = {
        'allow': lambda *a: 'yes'
    }

    def allow_negative(self, cr, uid, ids, context=None):
        for o in self.browse(cr, uid, ids, context=context):
            if o.allow == 'yes':
                cr.execute("ALTER TABLE account_move_line DROP CONSTRAINT account_move_line_credit_debit2")
                cr.commit()
        return {
                'view_type': 'form',
                "view_mode": 'form',
                'res_model': 'ir.actions.configuration.wizard',
                'type': 'ir.actions.act_window',
                'target': 'new',
         }

    def action_cancel(self, cr, uid, ids, context=None):
        return {
                'view_type': 'form',
                "view_mode": 'form',
                'res_model': 'ir.actions.configuration.wizard',
                'type': 'ir.actions.act_window',
                'target': 'new',
         }

config_allow_negative()