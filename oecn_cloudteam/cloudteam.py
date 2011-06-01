# -*- encoding: utf-8 -*-
##############################################################################
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
#    Created on 2011-04-28
#    author:Joshua  
##############################################################################

from osv import fields,osv

class cloudtaem_case(osv.osv):
    '''
    云团队成员贡献类型
    '''
    _name =  "cloudteam.case"
    _description = '云团队事务'
    _columns = {
        'name': fields.char('事务名', required=True, size=64, translate=True),
        'active' : fields.boolean('Active', help="用于隐藏需要删除的类型"),
    }

    _defaults = {
        'active' : lambda *a: 1,
    }
    
cloudtaem_case()

class cloudteam_menber(osv.osv):
    '''
    云团队成员
    '''
    _name =  "cloudteam.menber"
    _description = '云团队成员'
    _columns = {
        'user':fields.many2one('res.users','用户名'),
        'case':fields.many2one('cloudteam.case','用户类型'),
        'text':fields.text('具体描述'),
        'link':fields.char('链接',size=128),
        'quantity':fields.float('数量'),
    }
cloudteam_menber()