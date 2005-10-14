#!/usr/bin/python

import widgetclasses as widgets

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
    return validator

def CheckboxInput(validator, label, default=None, attrs=None):
    validator.renderer = widgets.CheckboxInput(label, default=default, attrs=attrs)
    return validator

def RadioInput(validator, label, values, default=None, attrs=None, separator='\n'):
    validator.renderer = widgets.RadioInput(label, values, default=default, attrs=attrs, separator=separator)
    return validator

def Select(validator, label, values, default=None, attrs=None, separator='\n'):
    validator.renderer = widgets.Select(label, values, default=default, attrs=attrs, separator=separator)
    return validator

def Custom(validator, label, content, default=None):
    "Transform a validator into a custom widget, defined by a simple template string into which the widget name and submitted value may be substituted"
    validator.renderer = widgets.Custom(label, content, default=default)
    return validator
