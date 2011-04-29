# -*- encoding: utf-8 -*-
##############################################################################
#
#    Tony Gu (digisatori@gmail.com)
#    http://www.shine-it.net
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
##############################################################################
import report.render.rml2pdf.customfonts as cfonts
from addons import get_module_resource
from reportlab.lib.styles import ParagraphStyle

this_module = 'l10n_cn'

simsun = get_module_resource(this_module,'pdf_report_zh', 'fonts', 'SimSun.ttf')
simhei = get_module_resource(this_module,'pdf_report_zh', 'fonts', 'SimHei.ttc')
if not (simsun and simhei):
    raise OSError("SimSun.ttf and/or SimHei.ttf not in %s resources", this_module)

CustomTTFonts = [
        ('Helvetica',"SimSun", simsun, 'normal'),
        ('Helvetica',"SimHei", simhei, 'bold'),
        ('Helvetica',"SimSun", simsun, 'italic'),
        ('Helvetica',"SimHei", simhei, 'bolditalic'),
        ('Times',"SimSun", simsun, 'normal'),
        ('Times',"SimHei", simhei, 'bold'),
        ('Times',"SimSun", simsun, 'italic'),
        ('Times',"SimHei", simhei, 'bolditalic'),
        ('Times-Roman',"SimSun", simsun, 'normal'),
        ('Times-Roman',"SimHei", simhei, 'bold'),
        ('Times-Roman',"SimSun", simsun, 'italic'),
        ('Times-Roman',"SimHei", simhei, 'bolditalic'),
        ('Courier',"SimSun", simsun, 'normal'),
        ('Courier',"SimHei", simhei, 'bold'),
        ('Courier',"SimSun", simsun, 'italic'),
        ('Courier',"SimHei", simhei, 'bolditalic'),
        ]
cfonts.CustomTTFonts=CustomTTFonts
ParagraphStyle.defaults['wordWrap'] = "CJK"
