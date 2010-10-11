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

import time
from report import report_sxw
from osv import osv
import pooler

class generic_report(report_sxw.rml_parse):
    """
    余额表，资产负债表
    """

    def __init__(self, cr, uid, name, context):
        super(generic_report, self).__init__(cr, uid, name, context=context)
        self.query = ""
        self.localcontext.update({
            'time': time,
            'balance_line':self._balance_line,
            'report_imformation':self._get_report_imformation,
        })

    def set_context(self, objects, data, ids, report_type = None):
        """
        设置 OE context
        """
        new_ids = []
        if (data['model'] == 'account.account'):
            new_ids = ids
        else:
            new_ids = self.pool.get('account.account').search(self.cr, self.uid, [('id','!=','0')], context={})
            objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)

        super(generic_report, self).set_context(objects, data, new_ids, report_type)

    def _get_report_imformation(self, form):
        """
        获取打印日期，wizard选择的公司名称
        """
        res={
            'date':'',
            'company':'',
        }
        res['date']=form['date']
        companyObj = self.pool.get('res.company').read(self.cr,self.uid,form['company_id'],['name'])
        res['company'] = companyObj['name']
        return res

    def _get_children_and_consol(self, cr, uid, ids, context={}):
        """
        this function search for all the children and all consolidated children (recursively) of the given account ids
        """
        ids2 = self.pool.get('account.account').search(cr, uid, [('parent_id', 'child_of', ids)], context=context)
        ids3 = []
        for rec in self.pool.get('account.account').browse(cr, uid, ids2, context=context):
            for child in rec.child_consol_ids:
                ids3.append(child.id)
        if ids3:
            ids3 = self._get_children_and_consol(cr, uid, ids3, context)
        return ids2 + ids3

    def _balance_line(self,form):
        """
        生成余额表
        """
        result={}
        i=0
        beginning_field_names = ['beginning_balance','beginning_debit','beginning_credit']
        year_amount_field_names = ['year_amount_balance','year_amount_debit','year_amount_credit']
        month_amount_field_names = ['month_amount_balance','month_amount_debit','month_amount_credit']
        ending_field_names = ['ending_balance','ending_debit','ending_credit']
        pool = pooler.get_pool(self.cr.dbname)

        end_dete =form['date']
        year_begin_date = end_dete[0:4]+'-01-01'
        month_begin_date = end_dete[0:7]+'-01'

        account_ids = pool.get('account.account').search(self.cr, self.uid, [('id','!=','0')], context={})
        ids2 = self._get_children_and_consol(self.cr, self.uid, account_ids, context={})
        acc_set = ",".join(map(str, ids2))
        #compute for each account the balance/debit/credit from the move lines for Ending Blance
        beginning_accounts = {}
        year_amount_accounts = {}
        month_amount_accounts = {}
        ending_accounts = {}

        #期初
        if ids2:
            
            self.cr.execute(("SELECT l.account_id as id, " \
                    "a.code as code," \
                    "a.name as name," \
                    "COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as beginning_balance , " \
                    "COALESCE(SUM(l.debit), 0) as beginning_debit, " \
                    "COALESCE(SUM(l.credit), 0) as beginning_credit " \
                    "FROM " \
                        "account_move_line l " \
                    "JOIN " \
                        "account_account a on (l.account_id=a.id)"
                    "WHERE " \
                        "l.account_id IN (%s) " \
                        "and l.date<= '%s'"
                    " GROUP BY l.account_id,a.code,a.name " \
                    " ORDER BY a.code") % (acc_set, year_begin_date))

            for res in self.cr.dictfetchall():
                beginning_accounts[res['id']] = res

        #本年发生额
        if ids2:
            self.cr.execute(("SELECT l.account_id as id, " \
                    "a.code as code," \
                    "a.name as name," \
                    "COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as year_amount_balance , " \
                    "COALESCE(SUM(l.debit), 0) as year_amount_debit, " \
                    "COALESCE(SUM(l.credit), 0) as year_amount_credit " \
                    "FROM " \
                        "account_move_line l " \
                    "JOIN " \
                        "account_account a on (l.account_id=a.id)"
                    "WHERE " \
                        "l.account_id IN (%s) " \
                        "and l.date<= '%s' " \
                        "and l.date>= '%s' "
                    " GROUP BY l.account_id,a.code,a.name " \
                    " ORDER BY a.code") % (acc_set, end_dete,year_begin_date))

            for res in self.cr.dictfetchall():
                year_amount_accounts[res['id']] = res

        #本月发生额
        if ids2:
            self.cr.execute(("SELECT l.account_id as id, " \
                    "a.code as code," \
                    "a.name as name," \
                    "COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as month_amount_balance , " \
                    "COALESCE(SUM(l.debit), 0) as month_amount_debit, " \
                    "COALESCE(SUM(l.credit), 0) as month_amount_credit " \
                    "FROM " \
                        "account_move_line l " \
                    "JOIN " \
                        "account_account a on (l.account_id=a.id)"
                    "WHERE " \
                        "l.account_id IN (%s) " \
                        "and l.date<= '%s' " \
                        "and l.date>= '%s' "
                    " GROUP BY l.account_id,a.code,a.name " \
                    " ORDER BY a.code") % (acc_set, end_dete,month_begin_date))

            for res in self.cr.dictfetchall():
                month_amount_accounts[res['id']] = res

        #期末
        if ids2:
            self.cr.execute(("SELECT l.account_id as id, " \
                    "a.code as code," \
                    "a.name as name," \
                    "COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as ending_balance , " \
                    "COALESCE(SUM(l.debit), 0) as ending_debit, " \
                    "COALESCE(SUM(l.credit), 0) as ending_credit " \
                    "FROM " \
                        "account_move_line l " \
                    "JOIN " \
                        "account_account a on (l.account_id=a.id)"
                    "WHERE " \
                        "l.account_id IN (%s) " \
                        "and l.date<= '%s'"
                    " GROUP BY l.account_id,a.code,a.name " \
                    " ORDER BY a.code") % (acc_set, end_dete))

            for res in self.cr.dictfetchall():
                ending_accounts[res['id']] = res
        # consolidate accounts with direct children
        brs = list(self.pool.get('account.account').browse(self.cr, self.uid, ids2, context={}))
        sums = {}
        while brs:
            current = brs[0]
            can_compute = True
            for child in current.child_id:
                if child.id not in sums:
                    can_compute = False
                    try:
                        brs.insert(0, brs.pop(brs.index(child)))
                    except ValueError:
                        brs.insert(0, child)
            if can_compute:
                brs.pop(0)
                sums.setdefault(current.id, {})['code'] = current.code
                sums.setdefault(current.id, {})['name'] = current.name
                for fn in beginning_field_names:
                    sums.setdefault(current.id, {})[fn] = beginning_accounts.get(current.id, {}).get(fn, 0.0)
                    if current.child_id:
                        sums[current.id][fn] += sum(sums[child.id][fn] for child in current.child_id)
                        
                for fn in year_amount_field_names:
                    sums.setdefault(current.id, {})[fn] = year_amount_accounts.get(current.id, {}).get(fn, 0.0)
                    if current.child_id:
                        sums[current.id][fn] += sum(sums[child.id][fn] for child in current.child_id)
                        
                for fn in month_amount_field_names:
                    sums.setdefault(current.id, {})[fn] = month_amount_accounts.get(current.id, {}).get(fn, 0.0)
                    if current.child_id:
                        sums[current.id][fn] += sum(sums[child.id][fn] for child in current.child_id)
                        
                for fn in ending_field_names:
                    sums.setdefault(current.id, {})[fn] = ending_accounts.get(current.id, {}).get(fn, 0.0)
                    if current.child_id:
                        sums[current.id][fn] += sum(sums[child.id][fn] for child in current.child_id)

        res = []
        for s in sums:
             res.append(sums.get(s,{}))
        return res

report_sxw.report_sxw('report.account.balance_sheet','account.account','addons/oecn_account_report/report/balance_sheet.odt',parser=generic_report)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
