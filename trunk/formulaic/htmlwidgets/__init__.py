#!/usr/bin/python

import widgetclasses as widgets

__doc__ = "A basic set of Formulaic widgets wrapping the standard html form elements"

# This file contains a collection of transformer functions, that take a
# formencode validator object (and possibly some other arguments), transform the
# validator into a widget, and return the transformed object. Widgets are just
# objects whose "render" attribute is a widget renderer instance. 

# Brief summary of the widget renderer api: Widget renderers are callable
# objects that take two arguments: a string name, and a string value, and return
# a string containing an html rendering of the form element(s) they represent
# (in other words, widget renderers must be callable, which commonly will mean
# that they must have a "__call__" method matching the above interface).  Widget
# renderers must also have two string attributes: "label" and "description"
# (although its expected that simple field renderers will not use descriptions,
# even if present).  Widgets that should be given minimal markup (i.e. no label,
# error messages, etc.) should have a "label" attribute of None (the primary
# example of this is html hidden inputs... in fact, labels of None should be
# treating as meaning "render this widget however hidden inputs should be
# renderered... but its concievable that this kind of rendering could be useful
# to other kinds of widgets, such a section headings).  Widgets that need their
# form to have a multipart "enctype" attribute, such as html file upload
# widgets, should set an optional attribute "needsMultipart" to True.  

def TextInput(validator, label, description=None, attrs=None):
    'Transform a validator into a widget corresponding to an html input element of type "text"'

    if not attrs:
        attrs = {}
    attrs['type'] = 'text'
    validator.renderer = widgets.Input(label, description, attrs)
    return validator

def PasswordInput(validator, label, description=None, attrs=None):
    'Transform a validator into a widget corresponding to an html input element of type "password"'

    if not attrs:
        attrs = {}
    attrs['type'] = 'password'
    validator.renderer = widgets.Input(label, description, attrs)
    return validator

def ButtonInput(validator, label, description=None, attrs=None):
    'Transform a validator into a widget corresponding to an html input element of type "button"'
    if not attrs:
        attrs = {}
    attrs['type'] = 'button'
    validator.renderer = widgets.Input(label, description, attrs)
    return validator

def ImageInput(validator, label, description, attrs):
    'Transform a validator into a widget corresponding to an html input element of type "image" (an image map)'
    if not attrs:
        attrs = {}
    attrs['type'] = 'image'
    validator.renderer = widgets.Input(label, description, attrs)
    return validator

def FileInput(validator, label, description=None, attrs=None):
    'Transform a validator into a widget corresponding to an html input element of type "file'

    if not attrs:
        attrs = {}
    attrs['type'] = 'file'
    validator.renderer = widgets.Input(label, description, attrs)
    validator.renderer.needsMultipart = True
    return validator

def TextArea(validator, label, description=None, attrs=None):
    "Transform a validator into a widget corresponding to an html textarea element"

    validator.renderer = widgets.Textarea(label, description, attrs)
    return validator

def HiddenInput(validator, attrs):
    'Transform a validator into a widget corresponding to an html input element of type "hidden"'

    if not attrs:
        attrs = {}
    attrs['type'] = 'hidden'
    validator.renderer = widgets.Input(None, None, attrs)
    return validator

def CheckboxInput(validator, label, description=None, attrs=None):
    validator.renderer = widgets.CheckboxInput(label, description, attrs)
    return validator

def RadioInput(validator, label, values, description=None, attrs=None, separator='\n'):
    validator.renderer = widgets.RadioInput(label, values, description=description, attrs=attrs, separator=separator)
    return validator

def Select(validator, label, values, description=None, attrs=None, separator='\n'):
    validator.renderer = widgets.Select(label, values, description=description, attrs=attrs, separator=separator)
    return validator

def Custom(validator, label, content, description=None):
    "Transform a validator into a custom widget, defined by a simple template string into which the widget name and submitted value may be substituted"
    validator.renderer = widgets.Custom(label, content, description)
    return validator
