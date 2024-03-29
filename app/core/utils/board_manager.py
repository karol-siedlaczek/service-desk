from ..models import BoardColumnAssociation, BoardColumn


def get_board_columns(user):
    return BoardColumn.get_board_columns(user)


def get_board_columns_associations(board_columns):
    board_columns_associations = []
    for board_column in board_columns:
        board_columns_associations.append(BoardColumnAssociation.objects.filter(column=board_column))
    return board_columns_associations
