import os

import sys
from locale import getlocale

libdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib')
if os.path.exists(libdir) and libdir not in sys.path:
    sys.path.insert(0, libdir)

del sys
del libdir

from relatorio.templates.opendocument import Template

import report
from report.report_sxw import *
from osv import osv,fields
import tools

def create_single_odt(self, cr, uid, ids, data, report_xml, context=None):
    if not context:
        context={}
    context = context.copy()
    report_type = report_xml.report_type
    context['parents'] = sxw_parents
    sxw_path = os.path.join(tools.config['addons_path'], report_xml.report_sxw)
    odt_template = Template(source=None, filepath=sxw_path)
    objs = self.getObjects(cr, uid, ids, context)
    odt_parser = self.parser(cr, uid, self.name2, context)
    odt_parser.set_context(objs, data, ids, report_xml.report_type)
    odt_generated = odt_template.generate(**odt_parser.localcontext).render()
    final_op = odt_generated.getvalue() 
    return (final_op, "odt")

report_sxw.create_single_odt = create_single_odt
