#!/usr/bin/python

import widgetclasses as widgets
from formencode.api import FancyValidator
import copy

__doc__ = '''Basic implementations of the most common form elements.

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

class InertValidator(FancyValidator):
    "A validator that simply returns the original value"
    pass

class _TransformerBase:
    "A callable class used to implement the transformer functions... not intended for direct use by you"

    def __init__(self, widgetClass, renderBare=False, needsMultipart=False, defaultArgs=None):
        self.widgetClass = widgetClass
        self._renderBare = renderBare
        self._needsMultipart = needsMultipart
        self.defaultArgs = defaultArgs or {}

    def __call__(self, validator, label, description='', default=None, *args, **kw):
        '''Given a validator, create a new formulaic widget.

        The object that this function returns will look very much like the original validator you passed in (with a "render" attribute added), but it is B{NOT} the same object!  Its a copy!  Originally, functions like this did return the original validator, but I changed to copies to enforce consistent use of these functions (i.e. I didn't want ambiguity over the functions should be used for their side effects or return value... you now always use them for their return values).

        If you don't want any validation behavior with your widget, pass None as the validator argument.  The widget will still end up looking like a formencode validator, but one that is completely inert.

        @param validator: a formencode compatible validator object (or None)
        @param label: the label for the widget
        @type label: string
        @param description: additional notes to be displayed with the widget (note that this is only useful if your form supports displaying descriptions, which the included formulaic form classes currently do not)
        @param default: the default value for the widget to display if no value is provided (note that the empty string counts as a value in this context)
        '''

#       this makes it simple for users to not do any validation if they don't want to
        if validator is None:
            widget = InertValidator()
        else:
            widget = copy.copy(validator)

        kw.update(self.defaultArgs)
        widget.renderer = self.widgetClass(*args, **kw)

#       Set required attributes
        widget.renderer.renderBare = bool(self._renderBare)
        widget.renderer.needsMultipart = bool(self._needsMultipart)
        widget.renderer.label = label
        widget.renderer.default = default
        widget.renderer.description = description
        return widget

TextInput = _TransformerBase(widgets.Input, defaultArgs={'type':'text'})
PasswordInput = _TransformerBase(widgets.Input, defaultArgs={'type':'password'})
ButtonInput = _TransformerBase(widgets.Input, defaultArgs={'type':'button'})
ImageInput = _TransformerBase(widgets.Input, defaultArgs={'type':'image'})
FileInput = _TransformerBase(widgets.Input, needsMultipart=True, defaultArgs={'type':'file'})
Textarea = _TransformerBase(widgets.Textarea)
HiddenInput = _TransformerBase(widgets.Input, renderBare=True, defaultArgs={'type':'hidden'})
CheckboxInput = _TransformerBase(widgets.CheckboxInput)
RadioInput = _TransformerBase(widgets.RadioInput)
Select = _TransformerBase(widgets.Select)
Custom = _TransformerBase(widgets.Custom)
