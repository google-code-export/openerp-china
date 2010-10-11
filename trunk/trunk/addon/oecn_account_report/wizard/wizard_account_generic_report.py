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

#期间表单
_PERIOD_FORM = u'''<?xml version="1.0"?>
<form string="选择日期">
    <field name="company_id" />
    <field name="date"/>
</form>'''



_PERIOD_FIELDS = {
# 表单的字段定义
    'company_id': {'string': u'公司', 'type': 'many2one', 'relation': 'res.company', 'required': True},
    'date': {'string': u'日期', 'type': 'date', 'required':True, 'default': lambda *a: time.strftime('%Y-%m-%d')},
}

def _next(self, cr, uid, data, context):
    return 'date_selection'

class WizardReport(wizard.interface):

    def _get_defaults(self, cr, uid, data, context={}):
    #从user获取company_id
        user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, uid, context=context)
        if user.company_id:
            company_id = user.company_id.id
        else:
            company_id = pooler.get_pool(cr.dbname).get('res.company').search(cr, uid, [('parent_id', '=', False)])[0]
        data['form']['company_id'] = company_id
        data['form']['context'] = context
        return data['form']

    states = {
        'init': {
            'actions': [],
            'result': {'type':'choice','next_state':_next}
        },
        'date_selection': {
            'actions': [_get_defaults],
            'result': {'type':'form', 'arch':_PERIOD_FORM,'fields':_PERIOD_FIELDS, 
                'state':[('end',u'取消','gtk-cancel'),('report_balance_sheet',u'打印','gtk-print')]}
        },
        
        'report_balance_sheet': {
        #资产负债表
            'actions': [],
            'result': {'type':'print', 'report':'account.balance_sheet', 'state':'end'}
        },
    }

WizardReport('account.generice_report')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: