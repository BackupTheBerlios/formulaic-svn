#!/usr/bin/python

from formencode import schema
from odict import OrderedDict
from xml.sax.saxutils import quoteattr, escape
from string import Template

class SimpleForm(OrderedDict):
    "A basic formencode-enabled html form"

#   Settings for rendering the entire form
    fieldSeparator = '\n\n' 
    formTpl = Template('''\
<form $formAttributes>

$fields

</form>''') 
    footer = Template('<input type="submit" value="$submitLabel"/>')

#   Settings for rendering each field
    labelTpl = Template('<label>$label</label>')
    errorTpl = Template('<span class="error">$errorMsg</span>')
    normalFieldTpl = Template('''\
$label
$widget
$error''')
    reducedFieldTpl = Template('$widget')

    def __init__(self, method='POST', action='', submitLabel='Submit', attrs=None):
        "Initialize a new, empty form"
        OrderedDict.__init__(self)
        self.schema = schema.Schema()
        self.schema.fields = self 

        self.attrs = {'method':method, 'action':action}
        if attrs:
            self.attrs.update(attrs)

        self.submitLabel = submitLabel

    @staticmethod
    def renderAttributes(attrs, **kwargs):
        output = []
        for name, value in attrs.items() + kwargs.items():
            output.append('%s=%s' % (name, quoteattr(str(value))))
        return ' '.join(output)

    def render(self, values, errors):
        "Render the entire form"

        renderedFields = []

#       Render each user field
        for name, field in self.schema.fields.items():
            value, error = values.get(name, None), errors.get(name, None)
            label = field.renderer.label
            widgetStr = field.renderer(name, value)
            renderedFields.append(self.renderField(label, widgetStr, error))

#       Render the submit button
        renderedFields.append(self.renderFooter())

        fields = self.fieldSeparator.join(renderedFields)
        formAttributes = self.renderAttributes(self.attrs)
        return self.formTpl.substitute(fields=fields, formAttributes=formAttributes)

    def renderFooter(self):
        "Render the footer (submit button) for the form"
        sl = escape(self.submitLabel).replace('"', '&quot;')
        return self.renderField('', self.footer.substitute(submitLabel=sl), None)

    def renderField(self, label, widget, error=None):
        "Render the complete html of a field"

        if label is not None:
            template = self.normalFieldTpl
        else:
            template = self.reducedFieldTpl

        if error:
            errorStr = self.errorTpl.substitute(errorMsg=error)
        else:
            errorStr = ''

        labelStr = self.labelTpl.substitute(label=label)
        return template.substitute(label=labelStr, widget=widget, error=errorStr).strip()

class TableForm(SimpleForm):

    formTpl = Template('''\
<form $formAttributes>
<table $tableAttributes>

$fields

</table>
</form>''')
    fieldSeparator = '\n\n'

    labelTpl = Template('$label')
    errorTpl = Template('$errorMsg')
    normalFieldTpl = Template('<tr><td class="label">$label</td><td>$widget</td><td class="error">$error</td></tr>')
    reducedFieldTpl = Template('<tr><td>$widget</td></tr>')
    
    tableAttrs = {'border':'0', 'cellpadding':'0', 'cellspacing':'0'}

    def __init__(self, method='POST', action='', formAttrs=None, tableAttrs=None, submitLabel='Submit'):
        SimpleForm.__init__(self, method, action, attrs=formAttrs, submitLabel=submitLabel)
        self.tableAttrs.update(tableAttrs or {})
        self.formTpl = Template(self.formTpl.safe_substitute(tableAttributes=self.renderAttributes(self.tableAttrs)))
