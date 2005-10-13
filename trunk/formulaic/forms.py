#!/usr/bin/python

from formencode import schema
from odict import OrderedDict
from xml.sax.saxutils import quoteattr, escape

def renderAttributes(attrs, **kwargs):
    output = []
    for name, value in attrs.items() + kwargs.items():
        output.append('%s=%s' % (name, quoteattr(str(value))))
    return ' '.join(output)

class SimpleForm(OrderedDict):
    "A basic formencode-enabled html form"

    fieldSeparator = '\n\n'
    formTpl = '<form %(formAtts)s>\n%(fields)s\n<input type="submit" value="%(submitlabel)s">\n</form>'

    def __init__(self, method='POST', action='', fieldRenderer=None, attrs=None):
        "Initialize a new, empty form"
        OrderedDict.__init__(self)
        self.schema = schema.Schema()
        self.schema.fields = self 

        self.attrs = {'method':method, 'action':action}
        if attrs:
            self.attrs.update(attrs)

        if fieldRenderer:
            self.fieldRenderer = fieldRenderer
        elif not hasattr(self, 'fieldRenderer'):
            self.fieldRenderer = SimpleFieldRenderer()
        assert callable(self.fieldRenderer)

    def render(self, values, errors):
        data = {}

        renderedFields = []
        for name, field in self.schema.fields.items():
            r = self.fieldRenderer(field, name, values.get(name, None), errors.get(name, None))
            renderedFields.append(r)
        data['fields'] = self.fieldSeparator.join(renderedFields)

        data['formAtts'] = renderAttributes(self.attrs)
        data['submitlabel'] = 'Submit'
        return self.formTpl % data

class TableForm(SimpleForm):

    formTpl = '<form %(formAttrs)s>\n<table %(tableAttrs)s>\n%(fields)s\n%(footer)s\n</table>\n</form>'
    normalFieldTpl = '<tr><td class="label">%(label)s</td><td>%(widget)s</td><td class="error">%(error)s</td></tr>'
    reducedFieldTpl = '<tr><td>%(widget)s</td></tr>'
    fieldSeparator = '\n'
    def __init__(self, method='POST', action='', formAttrs=None, tableAttrs=None):
        self.tableAttrs = {'border':'0', 'cellpadding':'0', 'cellspacing':'0', 'class':'formtable'}
        self.tableAttrs.update(tableAttrs or {})
        SimpleForm.__init__(self, method, action, attrs=formAttrs)

    def render(self, values, errors):
        data = {}
        renderedFields = []
        for name, field in self.schema.fields.items():
            r = self.fieldRenderer(field, name, values.get(name, None), errors.get(name, None))
            renderedFields.append(r)
        data['fields'] = self.fieldSeparator.join(renderedFields)
        data['formAttrs'] = renderAttributes(self.attrs)
        data['tableAttrs'] = renderAttributes(self.tableAttrs)
        data['footer'] = self.normalFieldTpl % {'label':'', 'widget':'<input type="submit" value="Submit"/>', 'error':''}
        return self.formTpl % data

    def fieldRenderer(self, field, name, value, error):
        fieldStr = field.renderer(name, value)
        label = field.renderer.label
        if label is not None:
            tpl = self.normalFieldTpl
        else:
            tpl = self.reducedFieldTpl
        error = error or ''
        return tpl % {'label':label, 'widget':fieldStr, 'error':error}

        

class SimpleFieldRenderer:
    "A callable that renders fields into html"

    labelTpl = '<label>%s</label>'
    errorTpl = '<span class="error">%s</span>'
    fieldTpl = '%(label)s\n%(field)s\n%(error)s'

    def __call__(self, field, name, value, error):
        fieldStr = field.renderer(name, value)
        label = field.renderer.label
        labelStr = (label is not None and self.labelTpl % label) or ''
#       formencode invalid exceptions render into strings intelligently
#       so error can be either an invalid exception or a plain string
        errorStr = (error and self.errorTpl % error) or ''

        return self.fieldTpl % {'label':labelStr, 'field':fieldStr, 'error':errorStr}
