# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
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

import wizard
import pooler
import locale
import time
from tools.translate import _
#向导一：现则科目
_ACCOUNT_FORM = u'''<?xml version="1.0"?>
<form string="选择科目">
    <field name="Account_list" colspan="4" mode="tree" />
    <newline/>
</form>'''

_ACCOUNT_FIELDS = {
#科目的字段
    'Account_list': {'string':u'会计科目', 'type':'many2one', 'relation':'account.account', 'required':True},
   
}


#期间表单
_PERIOD_FORM = u'''<?xml version="1.0"?>
<form string="选择期间">
    <field name="company_id" />
    <newline/>
    <field name="period_form"/>
    <newline/>
    <field name="period_to"/>
    <newline/>
    <field name="product" />
    <newline/>
    <field name="partner" />
    <newline/>

</form>'''


_PERIOD_FIELDS = {
#表单的字段定义
    'company_id': {'string': u'公司', 'type': 'many2one', 'relation': 'res.company', 'required': True},
    'period_form':  {'string': u'开始期间', 'type': 'many2one', 'relation': 'account.period', 'required': True},
    'period_to':  {'string': u'结束期间', 'type': 'many2one', 'relation': 'account.period', 'required': True},
    'product': {'string':u'产品','type':'many2one','relation':'product.product'},
    'partner': {'string':u'业务伙伴','type':'many2one','relation':'res.partner'},
}


def _check_path(self, cr, uid, data, context):
#检查model是否account.account
    if data['model'] == 'account.account':
        return 'checktype'
    else:
        return 'account_selection'

def _check(self, cr, uid, data, context):
    """
检查科目类型：
1.科目1002、1001结尾的且外币字段不为空打印“外币日记账”,外币字段为空就打印“现金日记账”
2.科目不是1002、1001结尾的，且有选择产品的打印“数量单位日记账”
3.其他“打印三栏式日记账”
    """
    new_ids = None
    if (data['model'] == 'account.account'):
        new_ids = data['ids'][0]
    else:
        new_ids = data['form']['Account_list']
    account = pooler.get_pool(cr.dbname).get('account.account').browse(cr, uid, new_ids, context=context)
    if(account.code[0:4] == '1002' or account.code[0:4] == '1001'):
        if(account.currency_id):
            return 'foreign_currency_cash_ledger'
        else:
            return 'report_cash_ledger'
    elif data['form'].get('product',''):
        return 'report_product_ledger'
    else:
        return 'report_threecolumns_ledger'


class WizardReport(wizard.interface):

    def _get_defaults(self, cr, uid, data, context={}):
        user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, uid, context=context)
        if user.company_id:
            company_id = user.company_id.id
        else:
            company_id = pooler.get_pool(cr.dbname).get('res.company').search(cr, uid, [('parent_id', '=', False)])[0]
        data['form']['company_id'] = company_id
        data['form']['report_type'] = 'report_threecolumns_ledger'
        #获取期间的开始结束时间
        ids = pooler.get_pool(cr.dbname).get('account.period').find(cr, uid, context=context)
        fiscalyear_id = pooler.get_pool(cr.dbname).get('account.period').browse(cr, uid, ids[0]).fiscalyear_id
        cr.execute(("SELECT date_start ,fiscalyear_id,id "\
                    "FROM account_period "\
                    "WHERE fiscalyear_id='%s' "\
                    "ORDER BY date_start asc ")% (int(fiscalyear_id)))
        res = cr.dictfetchall()
        data['form']['period_to'] = ids[0]
        data['form']['period_form'] = res[0]['id']
        data['form']['context'] = context
        return data['form']

    states = {
        'init': {
            'actions': [],
            'result': {'type':'choice','next_state':_check_path}
        },
        'account_selection': {
            'actions': [],
            'result': {'type':'form', 'arch':_ACCOUNT_FORM,'fields':_ACCOUNT_FIELDS, 
                'state':[('end',u'取消','gtk-cancel'),('checktype',u'下一步 >','gtk-go-forward')]}
        },
        'checktype': {
            'actions': [_get_defaults],
            'result': {'type':'form', 'arch':_PERIOD_FORM, 'fields':_PERIOD_FIELDS, 
                'state':[('end',u'取消','gtk-cancel'),('checkreport',u'打印','gtk-print')]}
        },
        'checkreport': {
            'actions': [],
            'result': {'type':'choice','next_state':_check}
        },

        'report_cash_ledger': {
        #现金日记账
            'actions': [],
            'result': {'type':'print', 'report':'account.cash_ledger', 'state':'end'}
        },

        'foreign_currency_cash_ledger': {
        #外币日记账
            'actions': [],
            'result': {'type':'print', 'report':'account.foreign_currency_cash_ledger', 'state':'end'}
        },

        'report_threecolumns_ledger': {
        #三栏式明细账
            'actions': [],
            'result': {'type':'print', 'report':'account.threecolumns_ledger', 'state':'end'}
        },
        'report_product_ledger': {
        #数量金额明细账
            'actions': [],
            'result': {'type':'print', 'report':'account.product_ledger', 'state':'end'}
        },
    }

WizardReport('account.ledger.report')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
