"""
@note: In the development version of Django, RadioInpt and CheckboxSelectMultiple
will be deprecated in favor of a more generic ChoiceInput class and RadioChoiceInput
When Django 1.6 is released, this file will have to be redone.
"""

from itertools import chain
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text
from django.utils.html import conditional_escape, format_html
from django.forms.widgets import RadioInput, RadioFieldRenderer
from django.forms.widgets import CheckboxSelectMultiple, CheckboxInput

######################################################################
## Bootstrap Radio Widgets
######################################################################

class BootstrapRadioInput(RadioInput):
    """
    A custom RadioInput widget that renders HTML and CSS suitable for use
    with the Bootstrap CSS styles and javascript. To achieve this, all
    that is required is to override the C{render} method.

    @note: This object is used by a forms.widgets.RadioFieldRenderer, and
    only represents a single <input type='radio'>.
    """

    def render(self, name=None, value=None, attrs=None, choices=()):
        """
        The work of this custom class, and the main override. Simply
        replace the render method of C{forms.widgets.RadioInput) with the
        required HTML and CSS, making sure to escape where necessary.

        @param name: Used to populate the name attribute on the input.
        @param value: Used to populate the value attribute on the input.
        @param attrs: A dictionary of other attributes for the input.
        @param choices: A placeholder, not used in this method.

        @note: None of the params in this method are actually used?

        @return: A unicode string representing the HTML of this element.
        @rtype: C{unicode}
        """

        name = name or self.name
        value = value or self.value
        attrs = attrs or self.attrs

        if 'id' in self.attrs:
            label_for = ' for="%s_%s"' % (self.attrs['id'], self.index)
        else:
            label_for = ''

        if self.attrs.get('inline', False):
            css_class = "radio inline"
        else:
            css_class = "radio"

        choice_label = conditional_escape(force_text(self.choice_label))
        return mark_safe(u'<label class="%s"%s>\n%s\n<span>%s</span>\n</label>' % (css_class, label_for, self.tag(), choice_label))

class BootstrapRadioRenderer(RadioFieldRenderer):
    """
    A custom RadioFieldRenderer that will allow the rendering of custom
    BootstrapRadioInputs by overriding the __iter__ method to force the
    creation of our custom class.

    @note: C{forms.RadioSelect.renderer} ensures that we always subclass
    the correct renderer, without requiring us to specify the class.
    """

    def __iter__(self):
        """
        Iterates through the choices and creates a BootstrapRadioInput
        for each of them-- enabling Bootstrap HTML for the radio input.

        @return: a generator of BootstrapRadioInput instead of RadioInput
        @rtype: C{generator}
        """
        for i, choice in enumerate(self.choices):
            yield BootstrapRadioInput(self.name, self.value, self.attrs.copy(), choice, i)

    def render(self):
        """
        Outputs Bootstrap HTML for the entire series of RadioInputs.

        @note: The super class returns an unordered list of radio inputs.
        """
        return mark_safe(u'\n'.join([force_text(w) for w in self]))

######################################################################
## Bootstrap Checkbox Select Multiple Widget
######################################################################

class BootstrapCheckboxSelectMultiple(CheckboxSelectMultiple):
    """
    See BootstrapRadioRenderer, and replace radio with Checkbox.
    """

    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        inline = attrs and attrs.get('inline', False)
        final_attrs = self.build_attrs(attrs, name=name)
        output = [ ]

        str_values = set([force_text(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            if has_id:
                final_attrs = dict(final_attrs, id="%s_%s" % (attrs[id], i))
                label_for = format_html(' for="{0}"', final_attrs['id'])
            else:
                label_for = ''

            if inline:
                label_class = "checkbox inline"
            else:
                label_class = "checkbox"
            label_class = format_html(' class="{0}"', label_class)


            cb = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_text(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = force_text(option_label)
            output.append(format_html('<label{0}{1}>{2} {3}</label>',
                            label_for, label_class, rendered_cb, option_label))
        return mark_safe(u'\n'.join(output))
