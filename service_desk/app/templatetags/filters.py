from django import template

register = template.Library()


@register.filter(name='in_board_columns_associations')
def in_board_columns_associations(board_columns_associations, column):
    return board_columns_associations.filter(column=column)