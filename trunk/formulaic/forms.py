#!/usr/bin/python
"""
forms - Basic form renderers for the formulaic form generation toolkit
Copyright (C) 2005 Greg Steffensen, greg.steffensen@gmail.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

from formencode import schema
from odict import OrderedDict
from xml.sax.saxutils import quoteattr, escape
from string import Template

__doc__  = '''Simple form class that can be used and customized directly, or
subclassed.'''

class BaseForm(OrderedDict):
    '''A basic formencode-enabled html form, designed to be easily customizable
    through subclassing.

    BaseForm is an B{ordered dictionary}.  That means that it implements the
    regular python dict interface, but (unlike standard python dicts), remembers
    the order in which items were added.  The dict elements are the various
    fields of the form, so this means that to display the form's fields in a
    particular order, you should add those fields to the form in the order they
    should be displayed.  You can set the order manually by setting the
    "sequence" element too.  

    The creation of a BaseForm instance also causes a formencode schema instance
    to be created, which is accessible via the "schema" attribute.  The BaseForm
    instance and schema instance are linked, so that any fields that are added
    to the form are also added to the schema (and vice versa).
    
    BaseForm is intended to be a minimalistic implementation of a formulaic form
    that more sophisticated forms can subclass.  But its still quite
    customizable as-is, and is quite suitable for real usage.

    Much of the output markup can be customized via various class variables
    containing template strings.  Like typical python class variables, these can
    be accessed both at the class and instance level.  So, to customize
    all forms (at least, all forms derived from BaseForm),
    set the class variables (i.e. "BaseForm.labelTpl"), and to customize one
    form instance, set the instance variables (i.e. "form.labelTpl").  These
    templates are strings used to initialize python 2.4 string Templates, with
    the default "$" delimiter for Template parameters.  Again, to be clear,
    these template class variables are the strings used to create Template
    instances, I{not} Template instances themselves.

    Fields are rendered by the I{renderField} method, and fields are rendered in
    one of two modes; "bare" mode is used if the field object has a "renderBare"
    attribute with a true value, and "normal" mode is used otherwise.  In "bare"
    mode, the field is rendered without a label or error message.  "bare" mode
    should primarily be interpreted to mean "render this however hidden fields
    should be rendered", as that is the special case it was created to address,
    but it can be used with any field that requires extra control over layout.

    @cvar formTpl: The template for the entire form.  Accepts three template
    parameters: I{$fields} (the final, joined rendering of all the fields of the
    form), I{$formAttributes} (a single, joined string rendering of all the html
    attributes to be applied to the form element, such as "action"), and
    I{$footer}, the rendering of the form footer, which is often just a submit
    button.

    @cvar labelTpl: the template for field labels.  Takes one parameter,
    I{$label}: the string label of the field.  Note that labels are not used when
    field request to be rendered in "bare" mode, and that when a field has a
    label value of None, the empty string will be used instead of the output of
    this template.

    @cvar errorTpl: the template for field error messages.  Takes one parameter,
    I{$error}.  Note that error messages are not used when a field requests to
    be rendered in "bare" mode, and that when no error is provided for a field,
    the empty string will be used instead of the output of this template.

    @cvar normalFieldTpl: the template for rendering fields in "normal" mode (as
    opposed to "bare" mode).  Takes three parameters: I{$label}, I{$widget} and
    I{$error}.

    @cvar bareFieldTpl: the template for rendering fields in "bare" mode.  Takes
    one parameter: I{$widget}.

    @cvar fieldSeparator: the string that will be used to join all fields,
    normal or bare or whatever (because it takes no parameters, it is just a
    string, not a template).

    @ivar attrs: html attributes for the I{<form/>} element
    '''

#   Settings for rendering the entire form
    fieldSeparator = '\n\n' 
    formTpl = '''\
<form $formAttributes>

$fields

$footer

</form>''' 
    footer = '<input type="submit" value="$submitLabel"/>'

#   Settings for rendering each field
    labelTpl = '<label>$label</label>'
    errorTpl = '<span class="error">$error</span>'
    normalFieldTpl = '''\
$label
$widget
$error'''
    bareFieldTpl = '$widget'

    def __init__(self, method='POST', action='', submitLabel='Submit', attrs=None):
        '''Initialize a new, empty form instance.

        @param method: the form method attribute (i.e. "GET" or "POST")
        @type method: str
        @param action: the form action attribute.  This will often be the empty
        @type action: str
        string ("self-submission"), for simplified validation and error message display.
        @param submitLabel: the text of the final submit button.
        @type submitLabel: str
        @param attrs: a dictionary of attribute names and values for the form
        element (i.e. the "class" or "id" attributes).  The I{method} and
        I{action} attributes can be set here, or through their parameters (which
        are provided simply as a convenience; if set on both, the values here
        take precedence.
        @type attrs: dict
        '''
        OrderedDict.__init__(self)
        self.schema = schema.Schema()
        self.schema.fields = self 

        self.attrs = {'method':method, 'action':action}
        if attrs:
            self.attrs.update(attrs)

        self.submitLabel = submitLabel

    @staticmethod
    def renderAttributes(attrs=None, **kwargs):
        '''Render a dictionary of an element's attribute names and values into a
        string, with proper escaping of special characters.  Examples:

        >>> forms.BaseForm.renderAttributes({'class':'myclass', 'id':'myelement'})
        'class="myclass" id="myelement"'
        >>> forms.BaseForm.renderAttributes({'id':'ben&jerrys'})
        'id="ben&amp;jerrys"'
        >>> forms.BaseForm.renderAttributes({'first':'a'}, second='b')
        'first="a" second="b"'

        @param attrs: a mapping of attribute names (i.e. "class") to values
        (i.e. "myclass").  Both keys and values should be strings.
        @type attrs: dict
        @param **kwargs: additional attribute names and values.
        @return: an attribute string that is ready to be placed inside an
        element tag
        @rtype: str
        '''
        if attrs is None:
            attrs = {}

        output = []
        for name, value in attrs.items() + kwargs.items():
            output.append('%s=%s' % (name, quoteattr(str(value))))
        return ' '.join(output)

    def smartRender(self, values, errors):
        """Like render, but doesn't display any errors if the form is being
        viewed for the first time.

        This method assumes that if formencode's conventions for using field
        names to structure data are being used, that such processsing has
        already been done to the values dict, and that all widgets implement
        those conventions correctly.  Otherwise, the detection of whether the
        form is being viewed for the first time may generate false positives.

        @param values: a dict of values submitted by the user.  If formencode's
        conventions for organizing inputs into lists and dicts are being used,
        this processing should be done on the dict before this method is called,
        since the method does not do such transformation itself.  @type values:
        dict 
        
        @param errors: a dict of error messages generated during
        validation.  Keys should match the current keys of this BaseForm
        instance, and values should be objects that can be rendered into usable
        error messages by the python str() function.  Typically, you will want
        to pass the value of the I{error_dict} attribute of a formencode Invalid
        exception raised by validating this form (when formencode schema objects
        are unable to validate, the Invalid exception that is raised contains a
        dict mapping the field name to other Invalid objects.  
        
        @return: the string rendering of the form

        @rtype: str
        """

        submissionKeys = set(values.keys())
        formKeys = set(self.keys())

        if not submissionKeys.intersection(formKeys):
            errors = {}

        return self.render(values, errors)

    def render(self, values, errors):
        '''Render the entire form.  Typically, this will be called after
        validation of the submitted values has been attempted and has failed (if
        it had succeeded, there would typically be no need to display the form
        again).

        @param values: a dict of values submitted by the user.  If formencode's
        conventions for organizing inputs into lists and dicts are being used,
        this processing should be done on the dict before this method is called,
        since the method does not do such transformation itself.  @type values:
        dict 
        
        @param errors: a dict of error messages generated during
        validation.  Keys should match the current keys of this BaseForm
        instance, and values should be objects that can be rendered into usable
        error messages by the python str() function.  Typically, you will want
        to pass the value of the I{error_dict} attribute of a formencode Invalid
        exception raised by validating this form (when formencode schema objects
        are unable to validate, the Invalid exception that is raised contains a
        dict mapping the field name to other Invalid objects.  
        
        @return: the string rendering of the form

        @rtype: str'''

        renderedFields = []
        needsMultipart = False

#       Render each user field
        for name, field in self.schema.fields.items():
            value, error = values.get(name, None), errors.get(name, None)
            renderedFields.append(self.renderField(name, value, error))
            if getattr(field.renderer, 'needsMultipart', False):
                needsMultipart = True

#       Render the submit button
        footer = self.renderFooter()

        # if any widgets require the form to use multipart encoding
        if needsMultipart: 
            self.attrs['enctype'] = 'multipart/form-data'

        fields = self.fieldSeparator.join(renderedFields)
        formAttributes = self.renderAttributes(self.attrs)
        return Template(self.formTpl).substitute(fields=fields, footer=footer, formAttributes=formAttributes)

    def renderField(self, name, value, error=None):
        '''Render the complete html of one of this form's fields

        @param name: the name of the field to be rendered (i.e. its key within
        this form object)
        @type name: str
        @param value: the value that the field should contain when rendered
        (i.e. the value that was submitted by the user).  None represents the
        field's default value.  If not None, this parameter is typically a
        string, though it doesn't have to be.
        @param error: the error message that the field should be rendered with.
        None indicates that it should be rendered without an error.
        @return: the string of the rendered html of the field.
        @rtype: str
        '''
        field = self[name]
        widgetStr = field.renderer(name, value)

        if getattr(field.renderer, 'renderBare', False):
            template = self.bareFieldTpl  # if this field should be rendered in bare mode
        else: 
            template = self.normalFieldTpl # if this field should be rendered in normal mode
        
        if error:
            errorStr = Template(self.errorTpl).substitute(error=error)
        else:
            errorStr = '' # if there is no error message, nothing is inserted, not even an empty error message

        label = field.renderer.label
        if label is not None:
            labelStr = Template(self.labelTpl).substitute(label=field.renderer.label)
        else:
            labelStr = ''

        return Template(template).substitute(label=labelStr, widget=widgetStr, error=errorStr).strip()

#   The footer isn't just included as part of the form template because this
#   this makes it easier to make it look like other fields if BaseForm is customized
#   or subclassed...
    def renderFooter(self):
        '''Render the footer (submit button) for the form

        @return: the string of the rendered html of the form footer. Typically, this
        will be a submit button, rendered similarly to a normal field.
        @rtype: str
        '''
        submitLabel = escape(self.submitLabel).replace('"', '&quot;')
        widgetStr = Template(self.footer).substitute(submitLabel=submitLabel)
        label = ''
        return Template(self.normalFieldTpl).substitute(label=label, widget=widgetStr, error='').strip()

class TableForm(BaseForm):
    '''A form that is rendered in a simple 3-column html table (label, widget, error)

    @tableAttrs: html attributes for the I{<table/>} element

    '''

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
        self.formTpl = Template(self.formTpl).safe_substitute(tableAttributes=self.renderAttributes(self.tableAttrs))

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
            errorStr = Template(self.errorTpl).substitute(error=error)
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

        return template.substitute(label=labelStr, widget=widgetStr, error=errorStr).strip()
