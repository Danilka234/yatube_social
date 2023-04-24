from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    """Создаем собственный фильтр для шаблонов
    с использованием CSS
    """
    return field.as_widget(attrs={'class': css})
