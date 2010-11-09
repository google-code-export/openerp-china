# -*- encoding: utf-8 -*-
from osv import osv, fields
from tools.translate import _

class account(osv.osv):
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
                            parent_obj = self.read(cr, uid, account_parent_id, ['code','name', 'parent_id'], context)
                            if parent_obj['code']:     #Jeff 不显示最上层view科目的名称
                                name = parent_obj['name'] + '/'+name
                            if  parent_obj['parent_id']:
                                account_parent_id = parent_obj['parent_id'][0]
                            else:
                                account_parent_id = False
                #添加父节点[Joshua]
            name = record['code'] + ' '+name
            res.append((record['id'], name))
        return res

account()