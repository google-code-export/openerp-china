# -*- encoding: utf-8 -*-
##############################################################################
#
#    Base Localization Module for OpenERP
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
##############################################################################

from tools.config import config
import report
import os
import sys

from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFont
import reportlab.lib.styles

if sys.platform == "win32" or sys.platform == "win64":
    fonts_dir = os.path.join(os.getenv("WINDIR"), "Fonts")    
    registerFont(TTFont("SimSun", os.path.join(fonts_dir, "simsun.ttc")))
else:
    fonts = ('SimSun')
    adp = os.path.abspath(config['addons_path'])
    for font in fonts:
        fntp = os.path.normcase(os.path.join(adp, 'l10n_cn', 'fonts', font+'.ttf'))
        registerFont(TTFont(font, fntp))

reportlab.lib.styles.ParagraphStyle.defaults['wordWrap'] = "CJK"

def wrap_trml2pdf(method):
    """We have to wrap the original parseString() to modify the rml data
    before it generates the pdf."""
    def convert2TrueType(*args, **argv):
        """This function replaces the type1 font names with their truetype
        substitutes and puts a font registration section at the beginning
        of the rml file. The rml file is acually a string (data)."""
        data = args[0]
        fontmap = {
            'Times-Roman':                   'SimSun',
            'Times-BoldItalic':              'SimSun',
            'Times-Bold':                    'SimSun',
            'Times-Italic':                  'SimSun',

            'Helvetica':                     'SimSun',
            'Helvetica-BoldItalic':          'SimSun',
            'Helvetica-Bold':                'SimSun',
            'Helvetica-BoldOblique':         'SimSun',
            'Helvetica-Oblique':             'SimSun',
            'Helvetica-Italic':              'SimSun',

            'Courier':                       'SimSun',
            'Courier-Bold':                  'SimSun',
            'Courier-BoldItalic':            'SimSun',
            'Courier-BoldOblique':           'SimSun',
            'Courier-Oblique':               'SimSun',
            'Courier-Italic':                'SimSun',

            'Helvetica-ExtraLight':          'SimSun',

            'TimesCondensed-Roman':          'SimSun',
            'TimesCondensed-BoldItalic':     'SimSun',
            'TimesCondensed-Bold':           'SimSun',
            'TimesCondensed-Italic':         'SimSun',

            'HelveticaCondensed':            'SimSun',
            'HelveticaCondensed-BoldItalic': 'SimSun',
            'HelveticaCondensed-Bold':       'SimSun',
            'HelveticaCondensed-Italic':     'SimSun',
        }
        while len(fontmap)>0:
            ck=max(fontmap)
            data = data.replace(ck,fontmap.pop(ck))
        return method(data, args[1:] if len(args) > 2 else args[1], **argv)
    return convert2TrueType

report.render.rml2pdf.parseString = wrap_trml2pdf(report.render.rml2pdf.parseString)

report.render.rml2pdf.parseNode = wrap_trml2pdf(report.render.rml2pdf.parseNode)
