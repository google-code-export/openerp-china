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
    "name" : "OpenERP 基础中文化模块",
    "version" : "1.1",
    "category": "Localisation/Account Charts",
    "author" : "openerp-china.org",
    "description": """
===============================================================================
    此模块用于为 OpenERP 的基础系统提供汉化，仅依赖内置的 base 模块。
    
    此模块包含如下功能：
    1.  为 OpenERP 的 RML/PDF 报表提供中文字体支持
    2.  为 OpenERP 添加中文省份数据
    3.  本地化国家数据。
    4.  本地化货币数据，并设置人民币为本币而不是默认的欧元。

    中文说明：
    使用文泉驿正黑体和 AR PL SungtiL GB 宋体（二者均为开源字体）替换系统原来不支持 Unicode 的英文字体，安装此模块可以使内置的报表自动支持中文字体。 
    注意: 直接解压复制到 addons 目录. 然后更新模块列表并安装，此模块不能用导入功能安装。如果您使用的是 Windows 系统的话推荐使用 Windows 的 SimHei.ttf 和 SimSun.ttf 替换 fonts 目录中的相应字体文件。

    原始 base_report_unicode 模块作者：Gábor Dukai

    A relatorio reporting module to replace OpenERP's internal ODT reporting subsystem.
        
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
    "active": False, 
    "installable": True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

