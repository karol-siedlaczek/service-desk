from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, reverse, redirect
from .models import Tenant, TenantSession, IssueType, Issue, Status, Board, BoardColumn, BoardColumnAssociation
from collections import namedtuple
import json


def get_initial_status(env_type):
    if env_type == settings.SD_ENV_TYPE:
        return Status.objects.get(id=settings.SD_INITIAL_STATUS)
    elif env_type == settings.SOFT_ENV_TYPE:
        return Status.objects.get(id=settings.SOFT_INITIAL_STATUS)
    else:
        return Status.objects.get(id=settings.SD_INITIAL_STATUS)


def get_board_columns(user):
    active_tenant_session = get_active_tenant_session(user)
    if active_tenant_session.user_type == settings.CUST_TYPE:
        board = Board.objects.get(id=active_tenant_session.tenant.customers_board.id)
    elif active_tenant_session.user_type == settings.OPER_TYPE:
        board = Board.objects.get(id=active_tenant_session.tenant.operators_board.id)
    elif active_tenant_session.user_type == settings.DEV_TYPE:
        board = Board.objects.get(id=active_tenant_session.tenant.developers_board.id)
    return BoardColumn.objects.filter(board=board)


def get_board_columns_assocations(board_columns):
    board_columns_associations = []
    for board_column in board_columns:
        board_columns_associations.append(BoardColumnAssociation.objects.filter(column=board_column))
    return board_columns_associations


def get_tenant_by_group_type(group_type, group_id):
    try:
        if group_type == settings.CUST_TYPE:
            return Tenant.objects.get(customers_group=group_id)
        elif group_type == settings.OPER_TYPE:
            return Tenant.objects.get(operators_group=group_id)
        elif group_type == settings.DEV_TYPE:
            return Tenant.objects.get(developers_group=group_id)
    except Tenant.DoesNotExists:
        return None


def tenant_session(user):  # checks if any tenant session exists for specific user
    try:
        TenantSession.objects.filter(user=user)
        return True
    except TenantSession.DoesNotExist:
        return False


def active_tenant_session(user):  # checks if any active tenant session exists for specific user
    try:
        get_active_tenant_session(user)
        return True
    except TenantSession.DoesNotExist:
        return False


def tenant_session_exists(tenant, user):  # check if specific tenant session assigned to provided user exists in database
    if TenantSession.objects.filter(tenant=tenant, user=user):
        return True
    else:
        return False


def add_tenant_session(tenant, user, user_type):  # creates tenant session record in database for selected user
    TenantSession.objects.create(
        user_type=user_type,
        tenant=tenant,
        user=user)


def clear_tenant_session(user):  # delete all tenant session data for selected user (during log out)
    TenantSession.objects.filter(user=user).delete()


def set_active_tenant(tenant, request, user):  # change tenant state to active based on data in cookies or choose default if no data in cookies
    def _set_active_tenant(tenant, user):
        tenant_session = TenantSession.objects.get(tenant=tenant, user=user)
        tenant_session.active = True
        tenant_session.save()
    tenant_cookie = get_tenant_cookie_name(user)
    if request.COOKIES.get(tenant_cookie) is None and not TenantSession.objects.filter(active=True, user=user):
        _set_active_tenant(tenant, user)
    elif request.COOKIES.get(tenant_cookie) == str(tenant.id):
        _set_active_tenant(tenant, user)


def get_active_tenant(user):
    return Tenant.objects.get(id=get_active_tenant_session(user).tenant.id)


def get_active_tenant_session(user):
    return TenantSession.objects.get(active=True, user=user)


def get_all_user_tenant_sessions(user):
    return TenantSession.objects.filter(user=user.id)


def get_tenant_cookie_name(user):
    return f'active_tenant_id_{str(user.id)}'


def get_active_tenant_issues(user, filter_assignee, filter_reporter, ordering, ordering_type):
    active_tenant = get_active_tenant(user)
    tickets = Issue.objects.filter(tenant=active_tenant.id)
    if filter_assignee:
        tickets = tickets.filter(assignee__username=filter_assignee)
    if filter_reporter:
        tickets = tickets.filter(reporter__username=filter_reporter)
    if ordering:  # add DESC or ASC type
        if ordering_type == 'asc':
            tickets = tickets.order_by(ordering, 'status')
        else:
            tickets = tickets.order_by('-' + ordering, 'status')
    return tickets


def change_active_tenant(tenant_id, user):
    active_tenant_session = get_active_tenant_session(user)
    active_tenant_session.active = False
    active_tenant_session.save()
    curr_tenant_session = TenantSession.objects.get(tenant=tenant_id, user=user.id)
    curr_tenant_session.active = True
    curr_tenant_session.save()


def get_env_type(issue_type_id): return IssueType.objects.get(id=issue_type_id).env_type
def json_to_obj(data): return json.loads(data, object_hook=_object_hook)
def _object_hook(converted_dict): return namedtuple('X', converted_dict.keys())(*converted_dict.values())
