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

import rml_parse

class AccountMoveReportParser(rml_parse.rml_parse):
    """
    凭证报表解析器
    """
    def __init__(self, cr, uid, name, context):
        super(AccountMoveReportParser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'exchange_rate': self._get_exchange_rate,
            'unit_price':self._get_unit_price,
        })
    
    def _get_exchange_rate(self, line):
        """
        计算汇率 公式：借or贷/外币价值
        """
        exchange_rate = False 
        if line.amount_currency: 
             if line.debit > 0: 
                 exchange_rate = line.debit/line.amount_currency 
             if line.credit > 0: 
                 exchange_rate = line.credit/line.amount_currency 
        return exchange_rate 

    def _get_unit_price(self, line):
        """
        计算单价 公式：借or贷/数量
        """
        unit_price = False
        if line.quantity:
            if line.debit > 0:
                unit_price = line.debit/line.quantity
            if line.credit > 0:
                unit_price = line.credit/line.quantity
        return unit_price

# 注册凭证报表
report_sxw.report_sxw('report.account.move.odt', 'account.move', 'addons/oecn_account_report/report/report_move.odt', parser=AccountMoveReportParser)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

