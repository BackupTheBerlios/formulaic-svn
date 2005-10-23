#!/usr/bin/python

"""
widgetclasses.py - Utilities for basic field renderers for the formulaic
form generation toolkit Copyright (C) 2005 Greg Steffensen,
greg.steffensen@gmail.com

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
import copy
from xml.sax.saxutils import quoteattr, escape
from string import Template

__doc__ = '''Implementation details for the htmlwidgets package.  Doesn't need to
be accessed directly when using the provided widget functions, but possibly
useful when writing your own widgets.'''

class Widget:
    "Abstract base class for widgets to inheirit from... handles labels, default values"

#   A place to put extra information about how to render this widget

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

    def __init__(self, type='text', attrs=None):
        self.attrs = copy.copy(self.defaultAttrs)
        attrs = attrs or {}
        attrs['type'] = type
        self.attrs.update(attrs)

    def _render(self, name, value):
        "Render this field into an html string"
        return '<input %s/>' % self.renderAttributes(self.attrs, name=name, value=value)

class Custom(Widget):
    "A callable that returns a custom html string, intended for the creation of simple custom widgets"

    def __init__(self, content):
        self.content = content

    def _render(self, name, value):
        return self.content.safe_substitute(name=quoteattr(name), value=escape(value))

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

    def __init__(self, options=None, attrs=None, separator='\n'):
        if not options:
            raise Exception('No options passed in creation of radio widget')
        self.options = options
        self.separator = separator
        Input.__init__(self, attrs=attrs)

    def _render(self, name, value):
        output = []
        for choice in self.options:
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

    def __init__(self, options=None, attrs=None, separator='\n'):

#       Options can be a dict or a list (or any iterable)... dicts are preferrred
        if not options:
            raise Exception('No options provided for select widget')
        self.options = options
        self.separator = separator
        Input.__init__(self, attrs=attrs)

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
        if hasattr(self.options, 'keys'): # if options was a dict
            for label, item_value in sorted(self.options.items()):
                if self.__isSelected(item_value, value):
                    options.append('<option selected="selected" value=%s>%s</option>' % (quoteattr(label), escape(item_value)))
                else:
                    options.append('<option value=%s>%s</option>' % (quoteattr(label), escape(item_value)))
        else: # if options was a list
            for item_value in self.options:
                if self.__isSelected(item_value, value):
                    options.append('<option selected="selected" value=%s>%s</option>' % (quoteattr(item_value), escape(item_value)))
                else:
                    options.append('<option value=%s>%s</option>' % (quoteattr(item_value), escape(item_value)))
        options = self.separator.join(options)
        attrString = self.renderAttributes(self.attrs, name=name)
        return '<select %s>\n%s\n</select>' % (attrString, options)
