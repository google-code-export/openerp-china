# -*- encoding: utf-8 -*-
##############################################################################
#
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
    'name': '中国会计报表模块',
    'version': '1.0',
    'description': """
    按中国会计制度对原会计模块进行增强：
    总账账簿输出             
    明细账簿输出             
    会计报表输出             
    """,
    'author': 'hornerp',
    'website': 'http://openerp-china.org/',
    'depends': ['board',
                'account',
                'relatorio_report',
                'oecn_account',
     ],
    'init_xml': [],
    'update_xml': ['account_wizard.xml',
                   'account_report.xml',
                   'board_account_fi_view.xml'
    ],
    'demo_xml': [],
    'installable': True,
    'certificate': ''
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
