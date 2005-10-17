#!/usr/bin/python

from formencode import schema
from odict import OrderedDict
from xml.sax.saxutils import quoteattr, escape
from string import Template

class BaseForm(OrderedDict):
    "A basic formencode-enabled html form, designed to be easily customizable through subclassing"

#   Settings for rendering the entire form
    fieldSeparator = '\n\n' 
    formTpl = '''\
<form $formAttributes>

$fields

</form>''' 
    footer = Template('<input type="submit" value="$submitLabel"/>')

#   Settings for rendering each field
    labelTpl = '<label>$label</label>'
    errorTpl = '<span class="error">$errorMsg</span>'
    normalFieldTpl = '''\
$label
$widget
$error'''
    bareFieldTpl = '$widget'

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
        needsMultipart = False

#       Render each user field
        for name, field in self.schema.fields.items():
            value, error = values.get(name, None), errors.get(name, None)
            renderedFields.append(self.renderField(name, value, error))
            if getattr(field.renderer, 'needsMultipart', False):
                needsMultipart = True

#       Render the submit button
        renderedFields.append(self.renderFooter())

        # if any widgets require the form to use multipart encoding
        if needsMultipart: 
            self.attrs['enctype'] = 'multipart/form-data'

        fields = self.fieldSeparator.join(renderedFields)
        formAttributes = self.renderAttributes(self.attrs)
        return Template(self.formTpl).substitute(fields=fields, formAttributes=formAttributes)

    def renderField(self, name, value, error=None):
        "Render the complelete html of a field"
        field = self[name]
        widgetStr = field.renderer(name, value)

        label = field.renderer.label
        if label is not None:
            template = self.normalFieldTpl
        else:
            template = self.bareFieldTpl
        
        if error:
            errorStr = Template(self.errorTpl).substitute(errorMsg=error)
        else:
            errorStr = ''

        labelStr = Template(self.labelTpl).substitute(label=label)
        return Template(template).substitute(label=labelStr, widget=widgetStr, error=errorStr).strip()

    def renderFooter(self):
        "Render the footer (submit button) for the form"
        submitLabel = escape(self.submitLabel).replace('"', '&quot;')
        widgetStr = Template(self.footer).substitute(submitLabel=submitLabel)
        return Template(self.normalFieldTpl).substitute(label='', widget=widgetStr, error='')

class TableForm(BaseForm):
    "A form that is rendered in a simple 3-column html table (label, widget, error)"

    formTpl = '''\
<form $formAttributes>
<table $tableAttributes>

$fields

</table>
</form>'''

    normalFieldTpl = '<tr><td>$label</td><td>$widget</td><td>$error</td></tr>'
    bareFieldTpl = '<tr><td>$widget</td></tr>'
    
    tableAttrs = {'border':'0', 'cellpadding':'0', 'cellspacing':'0'}

    def __init__(self, method='POST', action='', formAttrs=None, tableAttrs=None, submitLabel='Submit'):
        BaseForm.__init__(self, method, action, attrs=formAttrs, submitLabel=submitLabel)
        self.tableAttrs.update(tableAttrs or {})
        self.formTpl = Template(self.formTpl).safe_substitute(tableAttributes=self.renderAttributes(self.tableAttrs)))

class RequirementsForm(BaseForm):
    "A form that autodetects whether fields are required, and renders their labels differently if so"

    reqLabelTpl = '<label class="required">$label</label>'

    def renderField(self, name, value, error=None):
        field = self[name]
        widgetStr = field.renderer(name, value)

        label = field.renderer.label
        if label is not None:
            template = self.normalFieldTpl
        else:
            template = self.bareFieldTpl
        
        if error:
            errorStr = Template(self.errorTpl).substitute(errorMsg=error)
        else:
            errorStr = ''

#       Test to determine whether this is a required field
        try:
            field.to_python(None)
            req = False
        except:
            req = True

        if not req:
            labelStr = Template(self.labelTpl).substitute(label=label)
        else:
            labelTpl = Template(self.reqLabelTpl).substitute(label=label)

        return Template(template.substitute(label=labelStr, widget=widgetStr, error=errorStr).strip()

