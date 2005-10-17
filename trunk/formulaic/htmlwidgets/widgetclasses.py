#!/usr/bin/python

import copy
from xml.sax.saxutils import quoteattr, escape

class Widget:
    "Abstract base class for widgets to inheirit from... handles labels, default values"

#   A place to put extra information about how to render this widget

    def __init__(self, label, default=None):
        self.label = label
        self.default = default

    @staticmethod
    def renderAttributes(attrs, **kwargs):
        output = []
        for name, value in attrs.items() + kwargs.items():
            output.append('%s=%s' % (name, quoteattr(str(value))))
        return ' '.join(output)

    def __call__(self, name, value):
        if value is None:
            value = getattr(self, 'default', None)
        return self._render(name, value or '')

class Input(Widget):
    "A callable that can be used to render html input elements of any type"

    defaultAttrs = {}

    def __init__(self, label, default=None, attrs=None):
        Widget.__init__(self, label, default=default)
        self.attrs = copy.copy(self.defaultAttrs)
        self.attrs.update(attrs or {})

    def _render(self, name, value):
        "Render this field into an html string"
        return '<input %s/>' % self.renderAttributes(self.attrs, name=name, value=value)

class Custom(Widget):
    "A callable that returns a custom html string, intended for the creation of simple custom widgets"

    def __init__(self, label, content, default=None):
        Widget.__init__(self, label, default=default)
        self.content = content

    def _render(self, name, value):
        return self.content % {'name':quoteattr(name), 'value':escape(value)}

class CheckboxInput(Input):
    "A callable that renders html checkbox input elements"

#   This class overrides __call__ directly, instead of _render, because
#   checkbnox widgets should not have default value functionality... if the
#   default value is true, it will be impossible for the user to submit it as
#   unchecked
    def __call__(self, name, value):
        if value:
            attrString = self.renderAttributes(self.attrs, name=name, checked='checked')
        else:
            attrString = self.renderAttributes(self.attrs, name=name)
        return '<input %s/>' % attrString 


class Textarea(Input):
    "A callable that renders html textarea elements"
    defaultAttrs = {'rows':'10', 'cols':'20'}

    def _render(self, name, value):
        attrString = self.renderAttributes(self.attrs, name=name)
        return '<textarea %s>%s</textarea>' % (attrString, escape(str(value)))

class RadioInput(Input):
    "A callable that renders html radio input elements... note that unlike most other widgets, one instance of this class renders multiple html elements.  However, as with all widgets, all of those elements are rendered as a single form field (i.e. all the radio elements are grouped under one label)."

    defaultAttrs = {'type':'radio'}

    def __init__(self, label, values, default=None, attrs=None, separator='\n'):
        self.values = values
        self.separator = separator
        Input.__init__(self, label, default=default, attrs=attrs)

    def _render(self, name, value):
        output = []
        for choice in self.values:
            if value != choice: # if this input is not selected
                output.append('<input %s>%s</input>' %
                (self.renderAttributes(self.attrs, name=name, value=choice),
                escape(choice)))
            else: # if this input is selected
                output.append('<input %s>%s</input>' %
                (self.renderAttributes(self.attrs, checked="checked", name=name, value=choice), escape(value)))
        return self.separator.join(output)

class Select(Input):
    "A callable that renders an html select element, including its options."

    def __init__(self, label, values, default=None, attrs=None, separator='\n'):

#       Values can be a dict or a list (or any iterable)... dicts are preferrred
        self.values = values
        self.separator = separator
        Input.__init__(self, label, default=default, attrs=attrs)

    @staticmethod
    def __isSelected(item, selection):
        "Determine whether a given item is selected... works for both single selection and multiple selection fields"
        if selection is None:
            return False
        elif isinstance(selection, basestring):
            return item == selection
        else: # selection is a probably a list
            try:
                return item in selection
            except: # just in case it isn't a list
                return item == selection

    def _render(self, name, value):
        options = []
        if hasattr(self.values, 'keys'): # if values was a dict
            for label, item_value in sorted(self.values.items()):
                if self.__isSelected(item_value, value):
                    options.append('<option selected="selected" value=%s>%s</option>' % (quoteattr(label), escape(item_value)))
                else:
                    options.append('<option value=%s>%s</option>' % (quoteattr(label), escape(item_value)))
        else: # if values was a list
            for item_value in self.values:
                if self.__isSelected(item_value, value):
                    options.append('<option selected="selected" value=%s>%s</option>' % (quoteattr(item_value), escape(item_value)))
                else:
                    options.append('<option value=%s>%s</option>' % (quoteattr(item_value), escape(item_value)))
        options = self.separator.join(options)
        attrString = self.renderAttributes(self.attrs, name=name)
        return '<select %s>\n%s\n</select>' % (attrString, options)
