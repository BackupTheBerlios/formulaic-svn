#!/usr/bin/python

import copy
from xml.sax.saxutils import quoteattr, escape

def renderAttributes(attrs, **kwargs):
    output = []
    for name, value in attrs.items() + kwargs.items():
        output.append('%s=%s' % (name, quoteattr(str(value))))
    return ' '.join(output)


class Input:
    "A callable that renders html input elements"

    defaultAttrs = {}

    def __init__(self, label, description=None, attrs=None):
        self.label = label
        self.description = description
        self.attrs = copy.copy(self.defaultAttrs)
        self.attrs.update(attrs)

    def __call__(self, name, value):
        "Render this field into an html string"
        return '<input %s/>' % renderAttributes(self.attrs, name=name, value=value)

class Custom:
    "A callable that returns a custom html string, intended for the creation of simple custom widgets"

    def __init__(self, label, content, description=None):
        self.label = label
        self.description = description
        self.content = content
    def __call__(self, name, value):
        return self.content % {'name':quoteattr(name), 'value':escape(value)}

class CheckboxInput(Input):
    "A callable that renders html checkbox input elements"

    defaultAttrs = {}

    def __call__(self, name, value):
        if value:
            attrString = renderAttributes(self.attrs, name=name, checked='checked')
        else:
            attrString = renderAttributes(self.attrs, name=name)
        return '<input %s/>' % attrString 


class Textarea(Input):
    "A callable that renders html textarea elements"
    defaultAttrs = {'rows':'10', 'cols':'20'}

    def __call__(self, name, value):
        attrString = common.renderAttributes(self.attrs, name=name)
        return '<textarea %s>%s</textarea>' % (attrString, escape(str(value)))

class RadioInput(Input):
    "A callable that renders html radio input elements... note that unlike most other widgets, one instance of this class renders multiple html elements.  However, as with all widgets, all of those elements are rendered as a single form field (i.e. all the radio elements are grouped under one label)."

    defaultAttrs = {'type':'radio'}

    def __init__(self, label, values, description=None, attrs=None, separator='\n'):
        self.values = values
        self.separator = separator
        Input.__init__(self, label, description=description, attrs=attrs)

    def __call__(self, name, value):
        output = []
        for choice in self.values:
            if value != choice:
                output.append('<input %s>%s</input>' %
                (common.renderAttributes(self.attrs, name=name, value=choice),
                escape(choice)))
            else:
                output.append('<input %s>%s</input>' %
                (common.renderAttributes(self.attrs, checked="checked", name=name, value=choice), escape(value)))
        return self.separator.join(output)

class Select(Input):
    "A callable that renders an html select element, including its options."

    def __init__(self, label, values, description=None, attrs=None, separator='\n'):

#       Values can be a dict or a list (or any iterable)... dicts are preferrred
        self.values = values
        self.separator = separator
        Input.__init__(self, label, description=description, attrs=attrs)

    def __isSelected(item, selection):
        "Determine whether a given item is selected... works for both single selection and multiple selection fields"
        if isinstance(selection, basestring):
            return item == selection
        else:
            return item in selection

    def __call__(self, name, value):
        options = []
        if hasattr(self.values, 'keys'): # if values was a dict
            for label, item_value in sorted(self.values.items()):
                if self.__isSelected(item_value, value):
                    options.append('<option selected="selected" value=%s>%s</option>' % (quoteattr(label), escape(item_value)))
                else:
                    options.append('<option value=%s>%s</option>' % (quoteattr(label), escape(item_value)))
        else: # if values was a list
            for item_value in sorted(self.values):
                if self.__isSelected(item_value, value):
                    options.append('<option selected="selected" value=%s>%s</option>' % (quoteattr(item_value), escape(item_value)))
                else:
                    options.append('<option value=%s>%s</option>' % (quoteattr(item_value), escape(item_value)))
        options = self.separator.join(options)
        attrString = renderAttributes(self.attrs, name=name)
        return '<select %s>\n%s\n</select>' % (attrString, options)
