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
    'name': 'China Account',
    'version': '1.0',
    'description': """
    按中国会计制度对原会计模块进行增强：
    凭证界面按中国会计习惯调整                
    凭证按月按编号范围编号            
    """,
    'author': 'OpenERP中国顾问社区',
    'website': 'http://openerp-china.org/',
    'depends': ['account',
    ],
    'init_xml': [],
    'update_xml': ['oecn_account_view.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'certificate': ''
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
