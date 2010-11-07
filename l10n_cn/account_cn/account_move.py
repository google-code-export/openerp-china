# -*- encoding: utf-8 -*-
from osv import osv, fields
from tools.translate import _

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
    _name = 'l10n_cn.config.allow_negative'
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
