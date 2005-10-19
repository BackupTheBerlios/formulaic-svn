#!/usr/bin/python

import widgetclasses as widgets

__doc__ '''Basic implementations of the most common form elements.

The functions in this namespace are B{not} class constructors.  They're
transformation functions; they take a formencode validator instance as their
first argument, and return the same validator object, transformed into a widget
of the requested type.  Note that transforming a validator into a widget just
means adding a "renderer" attribute to it that fulfills the widget renderer
api.  All validator functionality is preserved.

Widget renderers are callable objects (i.e. they can be called like functions).
All widget renderers take two arguments when invoked: the name of the widget
within the form, and the value that the widget should be rendered with (a value
of None means to render with the default value).  In addition to being callable
objects, widget renderers also all have a "label" attribute.  There are some
optional attributes as well, such as "needsMultipart" (if the widget needs its
form to submit with enctype="multipart/mime", as with file upload widgets) and 
"renderBare" (if the widget needs to be rendered in "bare" mode, as with hidden
inputs).
'''

__doc__ = "A basic set of Formulaic widgets wrapping the standard html form elements"

def TextInput(validator, label, default=None, attrs=None):
    'Transform a validator into a widget corresponding to an html input element of type "text"'

    if not attrs:
        attrs = {}
    attrs['type'] = 'text'
    validator.renderer = widgets.Input(label, default=default, attrs=attrs)
    return validator

def PasswordInput(validator, label, default=None, attrs=None):
    'Transform a validator into a widget corresponding to an html input element of type "password"'

    if not attrs:
        attrs = {}
    attrs['type'] = 'password'
    validator.renderer = widgets.Input(label, default=default, attrs=attrs)
    return validator

def ButtonInput(validator, label, default=None, attrs=None):
    'Transform a validator into a widget corresponding to an html input element of type "button"'
    if not attrs:
        attrs = {}
    attrs['type'] = 'button'
    validator.renderer = widgets.Input(label, default=default, attrs=attrs)
    return validator

def ImageInput(validator, label, default=None, attrs=None):
    'Transform a validator into a widget corresponding to an html input element of type "image" (an image map)'
    if not attrs:
        attrs = {}
    attrs['type'] = 'image'
    validator.renderer = widgets.Input(label, default=default, attrs=attrs)
    return validator

def FileInput(validator, label, default=None, attrs=None):
    'Transform a validator into a widget corresponding to an html input element of type "file'

    if not attrs:
        attrs = {}
    attrs['type'] = 'file'
    validator.renderer = widgets.Input(label, default=default, attrs=attrs)
    validator.renderer.needsMultipart = True
    return validator

def TextArea(validator, label, default=None, attrs=None):
    "Transform a validator into a widget corresponding to an html textarea element"

    validator.renderer = widgets.Textarea(label, default=default, attrs=attrs)
    return validator

def HiddenInput(validator, attrs):
    'Transform a validator into a widget corresponding to an html input element of type "hidden"'

    if not attrs:
        attrs = {}
    attrs['type'] = 'hidden'
    validator.renderer = widgets.Input(None, None, attrs)
    validator.renderer.renderBare = True
    return validator

def CheckboxInput(validator, label, default=None, attrs=None):
    '''Transform a validator into a widget corresponding to an html input element
    of type "checkbox"'''
    validator.renderer = widgets.CheckboxInput(label, default=default, attrs=attrs)
    return validator

def RadioInput(validator, label, values, default=None, attrs=None, separator='\n'):
    '''Transform a validator into a widget corresponding to a B{group} of html
    input elements of type "radio"
    
    @param values: the displayed choices for this element.  Should be either a
    dict (mapping element values to labels) or a list (in which case the option
    value and label are given the same string) 
    '''
    validator.renderer = widgets.RadioInput(label, values, default=default, attrs=attrs, separator=separator)
    return validator

def Select(validator, label, values, default=None, attrs=None, separator='\n'):
    '''Transform a validator into a widget corresponding to an html select
    element
    
    @param values: the displayed choices for this element.  Should be either a
    dict (mapping option values to labels) or a list (in which case the option
    value and label are given the same string) 
    ''' 

    validator.renderer = widgets.Select(label, values, default=default, attrs=attrs, separator=separator)
    return validator

def Custom(validator, label, content, default=None):
    "Transform a validator into a custom widget, defined by a simple template string into which the widget name and submitted value may be substituted"
    validator.renderer = widgets.Custom(label, content, default=default)
    return validator
