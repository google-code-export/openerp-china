# -*- encoding: utf-8 -*-
##############################################################################
# 帐簿报表解析器实现
#
# Authors: * Camptocamp
#          * oldrev <oldrev@gmail.com>
#          * add you
# 
# Copyright (C) 2010-TODAY by The HornERP Team
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import time
from mx.DateTime import *
from report import report_sxw
import xml
import rml_parse
import pooler


class LedgerParser(rml_parse.rml_parse):
    """
    通用帐簿解析器基类（即报表后台）
    """
    def __init__(self, cr, uid, name, context):
        super(LedgerParser, self).__init__(cr, uid, name, context)
        # self.date_borne = {}
        self.query = ""
        self.child_ids = ""
        self.sql_condition = " "
        self.tot_currency = 0.0
        self.period_sql = ""
        self.sold_accounts = {}
        self.localcontext.update( { # 注册报表模板里可以访问的函数
            'time': time,
            'lines': self.lines,
            'type':self._check_type,
            'period_date':self.get_dete,
            # 'sum_debit_account': self._sum_debit_account,
            # 'sum_credit_account': self._sum_credit_account,
            # 'sum_solde_account': self._sum_solde_account,
            'sum_debit': self._sum_debit,
            'sum_credit': self._sum_credit,
            'sum_solde': self._sum_solde,
            'get_children_accounts': self.get_children_accounts,
            # 'sum_currency_amount_account': self._sum_currency_amount_account,
            'get_direction':self._get_direction,
            # 'sum_quantity_account':self._sum_quantity_account,
            'account_name' :self._get_account_name,
            'get_periods':self._get_periods,
            'sum_begin_solde':self._sum_begin_solde,
            'sum_year_amount_solde':self._sum_year_amount_solde,
            'sum_year_amount_currency':self._sum_year_amount_currency,
            'sum_amount_currency':self._sum_amount_currency,
            'sum_amount_quantity':self._sum_amount_quantity,
            'sum_year_quantity':self._sum_year_quantity,
            'sum_begin_balance_amount_currency':self._sum_begin_balance_amount_currency,
            'sum_year_balance_amount_currency':self._sum_year_balance_amount_currency,
            'sum_begin_balance_quantity':self._sum_begin_balance_quantity,
            'sum_year_balance_quantity':self._sum_year_balance_quantity,
        })
        self.context = context

    def set_context(self, objects, data, ids, report_type = None):
        """
        设置 OE context
        """
        # self.borne_date = self.get_date(data['form'])
        self.all_dete = self.get_dete(data['form'])
        self.sql_condition = self.get_threecolumns_ledger_type(data['form'])

        new_ids = []
        if (data['model'] == 'account.account'):
            new_ids = ids
        else:
            new_ids.append(data['form']['Account_list'])
            objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)

        super(LedgerParser, self).set_context(objects, data, new_ids, report_type)

    def get_dete(self, form):
        """
        分析日期
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
        获取期间
        """
        self.cr.execute(("select date_start,date_stop,name as period_name "\
                    "from account_period where "\
                    " date_start>='%s' and date_stop<='%s' "\
                    " order by date_start")% (self.all_dete['period_start_date_start'], self.all_dete['period_end_date_stop']))
        periods = self.cr.dictfetchall()
        return periods

    def _check_type(self, form):
        """
        检测报表类型
        """
        res = {}
        res['product'] = ""
        res['partner'] = ""
        res['report_name'] = u'三栏式'
        if form.get('product',''):
            res['report_name'] = u'产品'
            product_sql = """SELECT t.name AS name
                    FROM product_product AS p join product_template AS t on (p.product_tmpl_id=t.id)
                        WHERE p.id='%s'"""%(form['product'])
            self.cr.execute(product_sql)
            product_res = self.cr.dictfetchall()
            res['product']=product_res[0]['name']
        if form.get('partner',''):
            res['report_name'] = u'业务伙伴'
            partner_sql = """SELECT name 
                    FROM res_partner 
                        WHERE res_partner.id='%s'"""%(form['partner'])
            self.cr.execute(partner_sql)
            partner_res = self.cr.dictfetchall()
            res['partner']=partner_res[0]['name']
        return res

    def _calc_contrepartie(self,cr,uid,ids, context={}):
        """
        计算"对方科目"，下边这是法语吧
        """
        result = {}
        #for id in ids:
        #    result.setdefault(id, False)

        for account_line in self.pool.get('account.move.line').browse(cr, uid, ids, context):
            # For avoid long text in the field we will limit it to 5 lines

            result[account_line.id] = ' '
            num_id_move = str(account_line.move_id.id)
            num_id_line = str(account_line.id)
            account_id = str(account_line.account_id.id)
            # search the basic account
            # We have the account ID we will search all account move line from now until this time
            # We are in the case of we are on the top of the account move Line
            cr.execute('SELECT distinct(ac.code) as code_rest,ac.name as name_rest from account_account AS ac, account_move_line mv\
                    where ac.id = mv.account_id and mv.move_id = ' + num_id_move +' and mv.account_id <> ' + account_id )
            res_mv = cr.dictfetchall()
            # we need a result more than 2 line to make the test so we will made the the on 1 because we have exclude the current line
            if (len(res_mv) >=1):
                concat = ''
                rup_id = 0
                for move_rest in res_mv:
                    concat = concat + move_rest['code_rest'] + u' ' + move_rest['name_rest'] + u'；'
                    result[account_line.id] = concat
                    if rup_id >5:
                        # we need to stop the computing and to escape but before we will add "..."
                        result[account_line.id] = concat + '...'
                        break
                    rup_id+=1
        return result

    def get_date(self, form):
        """
        获取 move.lines 的日期区间
        """
        period_form_id = form['period_form']
        period_to_id = form['period_to']
        period_obj = self.pool.get('account.period')
        period_start_obj = period_obj.read(self.cr, self.uid, period_form_id, ['date_start'])
        period_end_obj = period_obj.read(self.cr, self.uid, period_to_id, ['date_stop'])
        borne_min = period_start_obj['date_start']
        borne_max = period_end_obj['date_stop']

        self.date_borne = {
            'min_date': borne_min,
            'max_date': borne_max,
            }
        return self.date_borne

    def get_threecolumns_ledger_type(self, form):
        if form.get('product',''):
            self.sql_condition = " AND l.product_id ='"+str(form['product'])+"'"
        if form.get('partner',''):
            self.sql_condition = " AND l.partner_id ='"+str(form['partner'])+"'"
        return self.sql_condition


    def get_children_accounts(self, account, form, period, recursion=True):
        """
        遍历指定科目下的所有子科目
        """
        self.child_ids = self.pool.get('account.account').search(self.cr, self.uid,
            [('parent_id', 'child_of', self.ids)])

        res = []
        ctx = self.context.copy()
        ## We will make the test for period or date
        ## We will now make the test
        #
        #ctx['state'] = form['context'].get('state','all')
        #if form.has_key('fiscalyear'):
        #    ctx['fiscalyear'] = form['fiscalyear']
        #    ctx['periods'] = form['periods'][0][2]
        #else:
        #    ctx['date_from'] = form['date_from']
        #    ctx['date_to'] = form['date_to']

        self.query = self.pool.get('account.move.line')._query_get(self.cr, self.uid, context=ctx)
        if account and account.child_consol_ids: # add ids of consolidated childs also of selected account
            ctx['consolidate_childs'] = True
            ctx['account_id'] = account.id                    

        ids_acc = self.pool.get('account.account').search(
            self.cr, self.uid,[('parent_id', 'child_of', [account.id])], context=ctx)

        for child_id in ids_acc:
            child_account = self.pool.get('account.account').browse(self.cr, self.uid, child_id)
            sold_account = self._sum_solde_account(child_account,form, period)
            self.sold_accounts[child_account.id] = sold_account
            
            if child_account.type != 'view' \
            and len(self.pool.get('account.move.line').search(self.cr, self.uid,
                [('account_id','>=',child_account.id)],
                context=ctx)) <> 0 :
                res.append(child_account)

        if not len(res):
            return [account]
        for move in res:
            SOLDEINIT = "SELECT sum(l.debit) AS sum_debit, sum(l.credit) AS sum_credit, sum(l.quantity) AS sum_quantity, sum(l.amount_currency) AS sum_amount_currency FROM account_move_line l WHERE l.account_id = " + str(move.id) +  " AND l.date < '" + period['date_stop'] + "'" +  " AND l.date > '" + period['date_start'] +"'"+ self.sql_condition
            self.cr.execute(SOLDEINIT)
            resultat = self.cr.dictfetchall()
            if resultat[0] :
                if resultat[0]['sum_debit'] == None:
                    sum_debit = 0
                else:
                    sum_debit = resultat[0]['sum_debit']
                if resultat[0]['sum_credit'] == None:
                    sum_credit = 0
                else:
                    sum_credit = resultat[0]['sum_credit']
                if resultat[0]['sum_amount_currency'] == None:
                    sum_amount_currency =0
                else:
                    sum_amount_currency = resultat[0]['sum_amount_currency']
                if resultat[0]['sum_quantity'] == None:
                    sum_quantity = 0
                else:
                    sum_quantity = resultat[0]['sum_quantity']

                move.init_credit = sum_credit
                move.init_debit = sum_debit
                move.init_amount_currency = sum_amount_currency
                move.init_quantity = sum_quantity

            else:
                move.init_credit = 0
                move.init_debit = 0
                move.init_currency = 0
                move.init_quantity = 0

        return res


    def lines(self, account, form, period, day=False):
        """
        按向导指定的参数获取所有的 account.move.line
        """
        self.tot_currency = 0.0

        inv_types = {
                'out_invoice': 'CI: ',
                'in_invoice': 'SI: ',
                'out_refund': 'OR: ',
                'in_refund': 'SR: ',
                }
        sql = """
            SELECT l.id, l.date, j.code,c.code AS currency_code,l.amount_currency ,l.ref, l.name , l.debit, l.credit, l.period_id, l.quantity
                    FROM account_move_line as l
                       LEFT JOIN res_currency c on (l.currency_id=c.id)
                                JOIN account_journal j on (l.journal_id=j.id)
                                AND account_id = %%s
                                AND %s
                                    %s
                                WHERE l.date<=%%s
                                AND l.date>=%%s
                                ORDER BY l.date, l.id""" % (self.query, self.sql_condition)
        if day:
            self.cr.execute(sql, (account.id, day, day,))
            res = self.cr.dictfetchall()
        else:
            self.cr.execute(sql, (account.id, period['date_stop'], period['date_start'],))
            res = self.cr.dictfetchall()
        sum = 0.0
        account_move_line_obj = pooler.get_pool(self.cr.dbname).get('account.move.line')
        for l in res:
            line = self.pool.get('account.move.line').browse(self.cr, self.uid, l['id'])
            l['move'] = line.move_id.name
            self.cr.execute('Select id from account_invoice where move_id =%s'%(line.move_id.id))
            tmpres = self.cr.dictfetchall()
            if len(tmpres) > 0 :
                inv = self.pool.get('account.invoice').browse(self.cr, self.uid, tmpres[0]['id'])
                l['ref'] = inv_types[inv.type] + ': '+str(inv.number)
            if line.partner_id :
                l['partner'] = line.partner_id.name
            else :
                l['partner'] = ''

            # 需要修正的地方请加上 FIXME 标记，需要尚未实现完全的地方请加上 TODO
            # by mrshelly 为啥要初始化, 这里也需要处理
            if type(l['debit'])  == type(None):
                l['debit'] = 0.0
            if type(l['credit'])  == type(None):
                l['credit'] = 0.0
            # by mrshelly 为啥要初始化, 这里也需要处理

            sum = l['debit'] - l ['credit']
            l['progress'] = sum
            balance = line.balance
        
            l['balance'] = abs(balance)
            #if balance == 0:
            #    str = u'平'
            #elif balance > 0:
            #    str = u'借'
            #else:
            #    str = u'贷'
            l['direction'] = self._get_direction(l['debit'] - l ['credit'])
            l['line_corresp'] = self._calc_contrepartie(self.cr,self.uid,[l['id']])[l['id']]
            # Modification du amount Currency
            #if (l['credit'] > 0):
            #    if l['amount_currency'] != None:
            #        l['amount_currency'] = abs(l['amount_currency']) * -1

            #if l['amount_currency'] != None:
            #    l['amount_currency_balance'] = self.tot_currency + l['amount_currency']

            #单价
            if (l['quantity'] != None and l['quantity'] !=0):
                if  l['debit'] != 0.0:
                    l['price'] = l['debit']/l['quantity']
                elif  l['credit'] != 0.0:
                    l['price'] = l['credit']/l['quantity']
            #汇率
            if (l['amount_currency'] != None and l['amount_currency'] !=0):
                if  l['debit'] != 0.0:
                    l['rate'] = l['debit']/l['amount_currency']
                elif  l['credit'] != 0.0:
                    l['rate'] = l['credit']/l['amount_currency']
            l['sum_balance_amount_currency'] = (self._sum_balance_currency_quantiry(l['date'],l['id']))['sum_balance_amount_currency']
            l['sum_balance_quantity'] = (self._sum_balance_currency_quantiry(l['date'],l['id']))['sum_balance_quantity']

        return res

    def _sum_solde_account(self, account, form, period=False):
        """
        科目余额合计
        """
        if period==False:
            self.cr.execute("SELECT (sum(debit) - sum(credit)) as tot_solde "\
                "FROM account_move_line l "\
                "WHERE l.account_id = "+str(account.id)+" AND l.date<='"+self.all_dete['period_end_date_stop']+"' AND l.date>='"+self.all_dete['period_start_date_start']+"' AND "+self.query+ " "+self.sql_condition)
        else:
            self.cr.execute("SELECT (sum(debit) - sum(credit)) as tot_solde "\
                "FROM account_move_line l "\
                "WHERE l.account_id = "+str(account.id)+" AND l.date<='"+period['date_stop']+"' AND l.date>='"+period['date_start']+"' AND "+self.query+ " "+self.sql_condition)
        sum_solde = self.cr.fetchone()[0] or 0.0
        if form.get('soldeinit', False):
            sum_solde += account.init_debit - account.init_credit

        return sum_solde

    def _sum_begin_solde(self):
        """
        期初余额
        """
        result = {
            'begin_date':'',
            'direction':'',
            'debit':'',
            'credit':'',
            'sum_begin_solde':0,
        }
        if not self.ids:
            return 0.0
        self.cr.execute("SELECT sum(debit) as debit , sum(credit) as credit "\
                "FROM account_move_line l "\
                "WHERE l.account_id in ("+','.join(map(str, self.pool.get('account.account').search(self.cr, self.uid,
            [('parent_id', 'child_of', self.ids)])))+") "+ " AND l.date < '" + self.all_dete['period_start_date_start'] +"'"+self.sql_condition)
        res = self.cr.dictfetchall()
        sum_begin_solde = (res[0]['debit'] or 0.0) - (res[0]['credit'] or 0.0)
        if sum_begin_solde == 0:
            result['direction'] = u'平'
        elif sum_begin_solde > 0:
            result['direction'] = u'借'
        else:
            result['direction'] = u'贷'
        result['sum_begin_solde'] = abs(sum_begin_solde or 0.0)
        result['begin_date'] = self.all_dete['period_start_date_start']
        return result

    def _sum_year_amount_solde(self, period):
        """
        本年累计
        """
        result = {
            'end_date':'',
            'direction':'',
            'debit':'',
            'credit':'',
            'sum_year_amount_solde':0,
        }
        self.cr.execute("SELECT sum(debit) as debit , sum(credit) as credit  "\
                "FROM account_move_line l "\
                "WHERE l.account_id in ("+','.join(map(str, self.pool.get('account.account').search(self.cr, self.uid,
            [('parent_id', 'child_of', self.ids)])))+") "+ " AND l.state<>'draft' AND l.date <= '" + period['date_stop']  +"'"+ " AND l.date >= '" + self.all_dete['fiscalyear_obj_date_start']  + "'"+self.sql_condition)
        res = self.cr.dictfetchall()
        sum_year_amount_solde = (res[0]['debit'] or 0.0) - (res[0]['credit'] or 0.0)
        if sum_year_amount_solde == 0:
            result['direction'] = u'平'
        elif sum_year_amount_solde > 0:
            result['direction'] = u'借'
        else:
            result['direction'] = u'贷'
        result['sum_year_amount_solde'] = abs(sum_year_amount_solde or 0.0)
        result['end_date'] = self.all_dete['fiscalyear_obj_date_start']
        result['debit'] = res[0]['debit']
        result['credit'] = res[0]['credit']
        return result

    def _sum_amount_currency_quantiry(self, start_date = False, end_date = False):
        """
        获取外币、数量合计值
        """
        result = {
            'sum_debit_amount_currency':0.00,
            'sum_credit_amount_currency':0.00,
            'sum_debit_quantity':0.00,
            'sum_credit_quantity':0.00,
        }
        if end_date:
            end_date_sql = " AND l.date <= '" + end_date +"'"
        else:
            end_date_sql = ' '
        if start_date:
            start_date_sql = " AND l.date >= '" + start_date  + "'"
        else:
            start_date_sql = ' '

        #方向是借
        self.cr.execute("SELECT  sum(amount_currency) AS amount_currency, sum(quantity) AS quantity "\
                " FROM account_move_line l "\
                " WHERE l.account_id in ("+','.join(map(str, self.pool.get('account.account').search(self.cr, self.uid,
            [('parent_id', 'child_of', self.ids)])))+") "+ 
            " AND l.state<>'draft' AND l.debit-l.credit>0 " + end_date_sql + start_date_sql + self.sql_condition)
        debit_res = self.cr.dictfetchall()

        #方向是贷
        self.cr.execute("SELECT  sum(amount_currency) AS amount_currency, sum(quantity) AS quantity "\
                " FROM account_move_line l "\
                " WHERE l.account_id in ("+','.join(map(str, self.pool.get('account.account').search(self.cr, self.uid,
            [('parent_id', 'child_of', self.ids)])))+") "+ 
            " AND l.state<>'draft' AND l.debit-l.credit<0 " + end_date_sql + start_date_sql + self.sql_condition)
        cedit_res = self.cr.dictfetchall()
        if debit_res[0].get('amount_currency',0.00)!= None:
            result['sum_debit_amount_currency'] = debit_res[0].get('amount_currency',0.00)
        if debit_res[0].get('quantity',0.00)!=None:
            result['sum_debit_quantity'] = debit_res[0].get('quantity',0.00)
        if cedit_res[0].get('amount_currency',0.00)!=None:
            result['sum_credit_amount_currency'] = cedit_res[0].get('amount_currency',0.00)
        if cedit_res[0].get('quantity',0.00)!=None:
            result['sum_credit_quantity'] = cedit_res[0].get('quantity',0.00)
        return result

    def _sum_balance_currency_quantiry(self,date = False, id = False,):
        """
        获取外币、数量的余额
        """
        result = {
            'sum_balance_amount_currency':0.00,
            'sum_balance_quantity':0.00,
        }
        sum_debit_amount_currency = 0.00
        sum_credit_amount_currency = 0.00
        sum_debit_quantity = 0.00
        sum_credit_quantity = 0.00
        balance_condition = ' '
        if date:
            balance_condition = " AND l.date <= '" + date +"'"
        if id and date:
            balance_condition = " AND (date<'"+str(date)+"' OR (date='"+str(date)+"' AND id<='"+str(id)+"')) "

        #方向是借
        self.cr.execute("SELECT sum(amount_currency) AS amount_currency, sum(quantity) AS quantity"\
                " FROM account_move_line l "\
                " WHERE l.account_id in ("+','.join(map(str, self.pool.get('account.account').search(self.cr, self.uid,
            [('parent_id', 'child_of', self.ids)])))+") "+ 
            " AND l.state<>'draft' AND l.debit-l.credit>0 " + balance_condition + self.sql_condition)
        debit_res = self.cr.dictfetchall()

        #方向是贷
        self.cr.execute("SELECT sum(amount_currency) AS amount_currency, sum(quantity) AS quantity"\
                " FROM account_move_line l "\
                " WHERE l.account_id in ("+','.join(map(str, self.pool.get('account.account').search(self.cr, self.uid,
            [('parent_id', 'child_of', self.ids)])))+") "+ 
            " AND l.state<>'draft' AND l.debit-l.credit<0 " + balance_condition  + self.sql_condition)
        cedit_res = self.cr.dictfetchall()

        if debit_res[0].get('amount_currency',0.0)!=None:
            sum_debit_amount_currency = debit_res[0].get('amount_currency',0.0)
            
        if debit_res[0].get('quantity',0.0)!=None:
            sum_debit_quantity = debit_res[0].get('quantity',0.0)
        
        if cedit_res[0].get('amount_currency',0.0)!=None:
            sum_credit_amount_currency = cedit_res[0].get('amount_currency',0.0)
            
        if cedit_res[0].get('quantity',0.0)!=None:
            sum_credit_quantity = cedit_res[0].get('quantity',0.0)

        result['sum_balance_amount_currency'] = abs(sum_debit_amount_currency - sum_credit_amount_currency ) 
        result['sum_balance_quantity'] = abs(sum_debit_quantity - sum_credit_quantity )

        return result

    def _sum_begin_balance_amount_currency(self):
        """
        外币期初余额
        """
        result = self._sum_balance_currency_quantiry(date = self.all_dete['period_start_date_start'])
        return result

    def _sum_year_balance_amount_currency(self, period):
        """
        外币期间、本年余额
        """
        result = self._sum_balance_currency_quantiry(date = period['date_stop'])
        return result

    def _sum_year_amount_currency(self, period):
        """
        外币本年借、贷合计
        """
        result = self._sum_amount_currency_quantiry(self.all_dete['fiscalyear_obj_date_start'], period['date_stop'])
        return result

    def _sum_amount_currency(self, period):
        """
        外币期间借、贷合计
        """
        result = self._sum_amount_currency_quantiry(self.all_dete['period_start_date_start'],self.all_dete['period_end_date_stop'])
        return result

    def _sum_year_quantity(self, period):
        """
        数量本年借、贷合计
        """
        result = self._sum_amount_currency_quantiry(self.all_dete['fiscalyear_obj_date_start'], period['date_stop'])
        return result

    def _sum_amount_quantity(self, form, period=False):
        """
        数量期间借、贷合计
        """
        result = self._sum_amount_currency_quantiry( self.all_dete['period_start_date_start'], self.all_dete['period_end_date_stop'])
        return result

    def _sum_begin_balance_quantity(self):
        """
        数量期初余额
        """
        result = self._sum_balance_currency_quantiry(date = self.all_dete['period_start_date_start'])
        return result

    def _sum_year_balance_quantity(self,period):
        """
        数量期间、本年余额
        """
        result = self._sum_balance_currency_quantiry(date = period['date_stop'])
        return result

    def _sum_debit(self, form, period=False):
        """
        借方期间总计
        """
        if not self.ids:
            return 0.0
        if period==False:
            self.cr.execute("SELECT sum(debit) "\
                "FROM account_move_line l "\
                "WHERE l.account_id in ("+','.join(map(str, self.child_ids))+") AND "+self.query + " AND l.date < '" +self.all_dete['period_end_date_stop'] + "'" +  " AND l.date > '" + self.all_dete['period_start_date_start'] +"'"+self.sql_condition)
        else:
            self.cr.execute("SELECT sum(debit) "\
                "FROM account_move_line l "\
                "WHERE l.account_id in ("+','.join(map(str, self.child_ids))+") AND "+self.query + " AND l.date < '" + period['date_stop'] + "'" +  " AND l.date > '" + period['date_start'] +"'"+self.sql_condition)
        sum_debit = self.cr.fetchone()[0] or 0.0
        return sum_debit

    def _sum_credit(self, form, period=False):
        """
        贷方期间总计
        """
        if not self.ids:
            return 0.0
        if period==False:
            self.cr.execute("SELECT sum(credit) "\
                "FROM account_move_line l "\
                "WHERE l.account_id in ("+','.join(map(str, self.child_ids))+") AND "+self.query + " AND l.date < '" +self.all_dete['period_end_date_stop'] + "'" +  " AND l.date > '" + self.all_dete['period_start_date_start'] +"'"+self.sql_condition)
        else:
            self.cr.execute("SELECT sum(credit) "\
                "FROM account_move_line l "\
                "WHERE l.account_id in ("+','.join(map(str, self.child_ids))+") AND "+self.query + " AND l.date < '" + period['date_stop'] + "'" +  " AND l.date > '" + period['date_start'] +"'"+self.sql_condition)
        ## Add solde init to the result
        sum_credit = self.cr.fetchone()[0] or 0.0
        return sum_credit

    def _sum_solde(self, form, period=False):
        """
        余额期间总计
        """
        if not self.ids:
            return 0.0
        if period==False:
             self.cr.execute("SELECT (sum(debit) - sum(credit)) as tot_solde "\
                "FROM account_move_line l "\
                "WHERE l.account_id in ("+','.join(map(str, self.child_ids))+") AND "+self.query + " AND l.date < '" +self.all_dete['period_end_date_stop'] + "'" +  " AND l.date > '" + self.all_dete['period_start_date_start'] +"'"+self.sql_condition)
        else:
            self.cr.execute("SELECT (sum(debit) - sum(credit)) as tot_solde "\
                "FROM account_move_line l "\
                "WHERE l.account_id in ("+','.join(map(str, self.child_ids))+") AND "+self.query + " AND l.date < '" + period['date_stop'] + "'" +  " AND l.date > '" + period['date_start'] +"'"+self.sql_condition)
        sum_solde = abs(self.cr.fetchone()[0] or 0.0)
        return sum_solde

    #    def _sum_amount_currency(self, form, period=False):
    #        if not self.ids:
    #            return 0.0
    #        if period==False:
    #            self.cr.execute("SELECT sum(amount_currency) "\
    #                        "FROM account_move_line l "\
    #                        "WHERE l.account_id in ("+','.join(map(str, self.child_ids))+") AND "+self.query + " AND l.date < '" +self.all_dete['period_end_date_stop'] + "'" +  " AND l.date > '" + self.all_dete['period_start_date_start'] +"'"+self.sql_condition)
    #        else:
    #            self.cr.execute("SELECT sum(amount_currency) "\
    #                            "FROM account_move_line l "\
    #                            "WHERE l.account_id in ("+','.join(map(str, self.child_ids))+") AND "+self.query + " AND l.date < '" + period['date_stop'] + "'" +  " AND l.date > '" + period['date_start'] +"'"+self.sql_condition)
    #        sum_amount_currency = self.cr.fetchone()[0] or 0.0
    #        return sum_amount_currency

    def _set_get_account_currency_code(self, account_id):
        self.cr.execute("SELECT c.code as code "\
                "FROM res_currency c,account_account as ac "\
                "WHERE ac.id = %s AND ac.currency_id = c.id"%(account_id))
        result = self.cr.fetchone()
        if result:
            self.account_currency = result[0]
        else:
            self.account_currency = False

    #    def _sum_currency_amount_account(self, account, form):
    #        self._set_get_account_currency_code(account.id)
    #        self.cr.execute("SELECT sum(aml.amount_currency) FROM account_move_line as aml,res_currency as rc WHERE aml.currency_id = rc.id AND aml.account_id= %s ", (account.id,))
    #        total = self.cr.fetchone()
    #        if self.account_currency:
    #            return_field = str(total[0]) + self.account_currency
    #            return return_field
    #        else:
    #            currency_total = self.tot_currency = 0.0
    #            return currency_total

    def _get_direction(self, balance):
        #FIXME: 这里估计是错的，还待研判
        str = ''
        if balance == 0:
            str = u'平'
        elif balance > 0:
            str = u'借'
        else:
            str = u'贷'
        return str

    def _get_account_name(self,account):
        """
        获取完整的科目名称
        """
        id = str(account.id)
        account_name = self.pool.get('account.account').name_get(self.cr, self.uid, id,{})
        return account_name[0][1]


class CashLedgerParser(LedgerParser):
    """
    现金日记账报表解析器
    """
    def __init__(self, cr, uid, name, context):
        super(CashLedgerParser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'days': self.days,
        })

    def days(self, account, form, period):
        """
        从 account.move.line 里按日期分组
        也就是把所有的凭证明细的不同日分出来，方便计算单日合计
        """
        sql = """
            SELECT l.date AS date, SUM(l.debit) AS debit, SUM(l.credit) AS credit, MAX(l.id) AS last_line_id, sum(l.amount_currency) AS sum_currency
                FROM account_move_line AS l
                       LEFT JOIN res_currency c on (l.currency_id=c.id)
                          JOIN account_journal j on (l.journal_id=j.id)
                             AND account_id = %%s
                             AND %s
                               WHERE l.date<=%%s
                               AND l.date>=%%s
                               GROUP BY l.date
                               ORDER BY l.date """ % (self.query)
        max_date = period['date_stop']
        min_date = period['date_start']
        self.cr.execute(sql, (account.id, max_date, min_date))

        res = self.cr.dictfetchall()
        account_move_line_obj = pooler.get_pool(self.cr.dbname).get('account.move.line')
        for day in res:
            start_date = ''
            day['sum_balance_amount_currency'] = (self._sum_balance_currency_quantiry( date = str(day.get('date','')))).get('sum_balance_amount_currency',0.0)
            day['sum_debit_amount_currency'] = (self._sum_amount_currency_quantiry( start_date = str(day.get('date','')),end_date = str(day.get('date','')))).get('sum_debit_amount_currency',0.0)
            day['sum_credit_amount_currency'] = (self._sum_amount_currency_quantiry( start_date = str(day.get('date','')),end_date = str(day.get('date','')))).get('sum_credit_amount_currency',0.0)
            line = self.pool.get('account.move.line').browse(self.cr, self.uid, day['last_line_id'])
            day['balance'] = abs(line.balance)
            if(type(day['debit']) == type(None)):
                day['debit'] = 0.0              # by mrshelly 只是为了报表出来.这里需要处理.
            if(type(day['credit']) == type(None)):
                day['credit'] = 0.0             # by mrshelly 只是为了报表出来.这里需要处理.

        return res

#注册报表类

#总帐

#现金日记帐
report_sxw.report_sxw('report.account.cash_ledger', 'account.account', 'addons/oecn_account_report/report/cash_ledger.odt', parser=CashLedgerParser, header=False)

#外币日记帐
report_sxw.report_sxw('report.account.foreign_currency_cash_ledger', 'account.account', 'addons/oecn_account_report/report/foreign_currency_cash_ledger.odt', parser=CashLedgerParser, header=False)

#三栏明细帐
report_sxw.report_sxw('report.account.threecolumns_ledger', 'account.account', 'addons/oecn_account_report/report/threecolumns_ledger.odt', parser=LedgerParser, header=False)
        
#数量金额明细帐
report_sxw.report_sxw('report.account.product_ledger', 'account.account', 'addons/oecn_account_report/report/product_ledger.odt', parser=LedgerParser, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
