# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 Gábor Dukai
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
{
    "name" : "中文会计科目表",
    "version" : "1.0",
    "category": "Localisation/Account Charts",
    "author" : "openerp-china.org",
    "maintainer":"openerp-china.org",
    "contributors":[
           "Digitalsatori",
           "Oldrev",
           "Xiao Xiang fu",
           "Jeff",
           "Joshua",
           "Jack",
           "Mrshelly",
    ],
    "website":"http://openerp-china.org",
    "url":"http://code.google.com/p/openerp-china/source/browse/#svn/trunk/l10n_cn",
    "description": """
此模块包含如下功能：
    1.  为 OpenERP 的 RML/PDF 报表提供中文字体支持。作者：Oldrev
        原始 base_report_unicode 模块作者：Gábor Dukai
    2.  为 OpenERP 添加中国省份数据。作者：Digitalsatori
    3.  relatorio_report模块使OpenERP可以支持Calc格式的财务报表 作者:Oldrev
    4.  科目类型\会计科目表模板\增值税\辅助核算类别\管理会计凭证簿\财务会计凭证簿 作者:Wjfonhand
    5.  会计凭证界面本地化\凭证按月编号\凭证金额允许负数 作者:Wjfonhand
    6.  科目显示全称\账簿打印\报表打印 作者:Joshua
    """,
    "depends" : ["base","account"],
    'init_xml': [
        'data/base_data.xml',
    ],
    "demo_xml" : [],
    "update_xml" : [
        'account_cn/account_view.xml',
        'account_cn/account_wizard.xml',
        'account_cn/account_report.xml',
        'account_cn/board_account_fi_view.xml',
        'chart_cn/account_chart.xml',
        'chart_cn/l10n_cn_wizard.xml',
    ],
    "license": "GPL-3",
    "certificate":"",
    "active": False, 
    "installable": True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

