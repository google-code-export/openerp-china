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

class general_ledger_parser(report_sxw.rml_parse):
    """
    总账
    """
    def __init__(self, cr, uid, name, context):
        super(general_ledger_parser, self).__init__(cr, uid, name, context=context)
        self.query = ""
        self.preiod = {}
        self.localcontext.update({
            'time': time,
            'generla_ledger_line':self._generla_ledger_line,
            'beginning_balance_accounts':self._beginning_balance_accounts,
            'period_date':self.get_dete,
        })

    def set_context(self, objects, data, ids, report_type = None):
        """
        设置 OE context
        """
        self.all_dete = self.get_dete(data['form'])

        new_ids = []
        if (data['model'] == 'account.account'):
            new_ids = ids
        else:
            new_ids.append(data['form']['Account_list'])
            objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)

        super(general_ledger_parser, self).set_context(objects, data, new_ids, report_type)

    def get_dete(self, form):
        """
        根据wizard获取日期：期间开始日期，期间结束日期，会计年开始日期
        """
        period_form_id = form['period_form']
        period_to_id = form['period_to']
        period_obj = self.pool.get('account.period')
        period_start_obj = period_obj.read(self.cr, self.uid, period_form_id, ['date_start','fiscalyear_id'])
        period_end_obj = period_obj.read(self.cr, self.uid, period_to_id, ['date_stop'])
        fiscalyear_obj = self.pool.get('account.fiscalyear').read(self.cr, self.uid, period_start_obj['fiscalyear_id'], ['date_start'])
        self.all_dete = {
            'period_start_date_start':period_start_obj['date_start'],
            'period_end_date_stop':period_end_obj['date_stop'],
            'fiscalyear_obj_date_start':fiscalyear_obj[0]['date_start'],
        }
        return self.all_dete

    def _get_periods(self, form):
        """
        根据日期段获取里面的期间
        """
        self.cr.execute(("select date_start,date_stop,name as period_name "\
                    "from account_period where "\
                    " date_start>='%s' and date_stop<='%s' "\
                    " order by date_start")% (self.all_dete['period_start_date_start'], self.all_dete['period_end_date_stop']))
        periods = self.cr.dictfetchall()
        return periods

    def _beginning_balance_accounts(self, account, form):
        """
        计算年初，借、贷、余额
        """
        periods = self._get_periods(form)
        account_ids = account.id
        result={
            'beginning_balance_debit':0,
            'beginning_balance_credit':0,
            'beginning_balance_balance':0,
            'beginning_balance_debit_or_credit':u'平',
            'month':self.all_dete['fiscalyear_obj_date_start'][5:7],
            'day':self.all_dete['fiscalyear_obj_date_start'][8:10],
        }
        if account_ids:
            self.cr.execute(("SELECT l.account_id as id, " \
                        "a.code as code," \
                        "a.name as name," \
                        "COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as beginning_balance_balance , " \
                        "COALESCE(SUM(l.debit), 0) as beginning_balance_debit, " \
                        "COALESCE(SUM(l.credit), 0) as beginning_balance_credit " \
                        "FROM " \
                            "account_move_line l " \
                        "JOIN " \
                            "account_account a on (l.account_id=a.id)"
                        "WHERE " \
                            "l.account_id IN (%s) " \
                            "and l.date< '%s' " \
                        " GROUP BY l.account_id,a.code,a.name " \
                        " ORDER BY a.code") % (account_ids,self.all_dete['fiscalyear_obj_date_start']))
            res = self.cr.dictfetchall()
            if(res):
                if (int(res[0]['beginning_balance_balance']) == 0):
                    result['beginning_balance_debit_or_credit'] = u'平'
                elif (int(res[0]['beginning_balance_balance']) > 0):
                    result['beginning_balance_debit_or_credit'] = u'借'
                else :
                    result['beginning_balance_debit_or_credit'] = u'贷'
                result['beginning_balance_debit']=res[0]['beginning_balance_debit']
                result['beginning_balance_credit']=res[0]['beginning_balance_credit']
                result['beginning_balance_balance']=res[0]['beginning_balance_balance']

        return result

    def _generla_ledger_line(self, account, form):
        """
        生成总账
        """
        result=[]
        month_debit_or_credit = u'平'
        year_debit_or_credit = u'平'
        i = 0
        month_amount_balance = 0
        periods = self._get_periods(form)
        account_ids = account.id
        month_amount_accounts={}
        beginning_balance_accounts={}
        year_amount_accounts={}
        for period in periods:
            if account_ids:
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
                        " ORDER BY a.code") % (account_ids,period['date_stop'], period['date_start']))
                month_amount_accounts = self.cr.dictfetchall()

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
                        " ORDER BY a.code") % (account_ids,period['date_stop'], self.all_dete['fiscalyear_obj_date_start']))
                year_amount_accounts = self.cr.dictfetchall()

            if (month_amount_accounts):
                if (int(month_amount_accounts[0]['month_amount_balance']) == 0):
                    month_debit_or_credit = u'平'
                elif (int(month_amount_accounts[0]['month_amount_balance']) > 0):
                    month_debit_or_credit = u'借'
                else:
                    month_debit_or_credit = u'贷'
                if (int(year_amount_accounts[0]['year_amount_balance']) == 0):
                    year_debit_or_credit = u'平'
                elif (int(year_amount_accounts[0]['year_amount_balance']) > 0):
                    year_debit_or_credit = u'借'
                else:
                    year_debit_or_credit = u'贷'

                month_amount_balance = month_amount_balance + month_amount_accounts[0]['month_amount_balance']
                sums = {
                    'period_month':period['date_stop'][5:7],
                    'period_day': period['date_stop'][8:10],
                    'code': month_amount_accounts[0]['code'],
                    'name': month_amount_accounts[0]['name'],
                    'month_amount_debit': month_amount_accounts[0]['month_amount_debit'],
                    'month_amount_credit': month_amount_accounts[0]['month_amount_credit'],
                    'month_amount_balance': month_amount_balance,
                    'month_debit_or_credit':month_debit_or_credit,
                    'year_amount_debit': year_amount_accounts[0]['year_amount_debit'],
                    'year_amount_credit': year_amount_accounts[0]['year_amount_credit'],
                    'year_amount_balance':year_amount_accounts[0]['year_amount_balance'],
                    'year_debit_or_credit':year_debit_or_credit,
                }
                result.append(sums)
        return result

report_sxw.report_sxw('report.account.general_ledger', 'account.account', 'addons/oecn_account_report/report/general_ledger.odt', parser=general_ledger_parser, header=False)
