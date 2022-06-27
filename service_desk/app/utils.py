from django.conf import settings
from django.db.models import Q
from django.apps import apps
from datetime import timezone
from django.contrib import messages
from .models import Tenant, TenantSession, Type, Ticket, Comment, CommentAssociation, User, TicketAssociation, Status, Board, BoardColumn, BoardColumnAssociation, TransitionAssociation, AuditLog, Attachment, AttachmentAssociation
from collections import namedtuple
import json
import logging
from django.core.files.base import ContentFile
import collections

logger = logging.getLogger(__name__)


class InstanceAuditLog:
    __slots__ = ['user', 'new_value', 'datetime', 'message']

    def __init__(self, user, new_value, datetime, message):
        self.user = user
        self.new_value = new_value
        self.datetime = datetime
        self.message = message


def get_utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


def get_client_ip_address(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    else:
        return request.META.get('REMOTE_ADDR')


def add_audit_log(request, obj, content_obj, operation, attr, attr_value):
    audit_log = AuditLog(
        user=request.user,
        object=obj._meta.model.__name__,
        object_value=obj.id,
        operation=operation,
        session=request.session.session_key,
        ip_address=get_client_ip_address(request),
        url=request.path)
    if content_obj:
        audit_log.content = content_obj._meta.model.__name__
        audit_log.content_value = content_obj.id
        audit_log.message = f'{obj._meta.model.__name__} {obj.id} {operation} {content_obj._meta.model.__name__} {content_obj.id}'
    elif attr is not None:
        audit_log.content = attr
        audit_log.content_value = attr_value
        audit_log.message = f'{obj._meta.model.__name__} {obj.id} {operation} {attr}'
    else:
        audit_log.message = f'{audit_log.message} '
    audit_log.save()
    return audit_log.message


def get_type_options(user):
    if user_is_operator(user) or user.is_superuser:
        return Type.objects.all()
    elif user_is_customer(user):
        return Type.objects.filter(env_type=settings.SD_ENV_TYPE)
    elif user_is_developer(user):
        return Type.objects.filter(env_type=settings.SOFT_ENV_TYPE)


def get_user_field_options_by_active_tenant(user):
    active_tenant_session = get_active_tenant_session(user)
    tenant = active_tenant_session.tenant
    allowed_users = User.objects.filter(groups__name__in=[tenant.customers_group, tenant.operators_group, tenant.developers_group])
    return allowed_users


def get_user_field_options_by_ticket(ticket):
    tenant = ticket.tenant
    allowed_users = User.objects.filter(groups__name__in=[tenant.customers_group, tenant.operators_group, tenant.developers_group])
    return allowed_users


def get_available_statuses(user):
    active_tenant_tickets = get_active_tenant_tickets(user, False)
    available_statuses = []
    for status in active_tenant_tickets.order_by('status__name').distinct('status__name').values_list('status'):
        available_statuses.append(str(status[0]))
    return Status.objects.filter(id__in=available_statuses)


def get_initial_type(user):
    if user_is_customer(user):
        return 2  # Service Request
    elif user_is_operator(user) or user_is_developer(user):
        return 1  # Task


def get_initial_status(env_type):
    if env_type == settings.SD_ENV_TYPE:
        return Status.objects.get(id=settings.SD_INITIAL_STATUS)
    elif env_type == settings.SOFT_ENV_TYPE:
        return Status.objects.get(id=settings.SOFT_INITIAL_STATUS)
    else:
        return Status.objects.get(id=settings.SD_INITIAL_STATUS)


def get_board_columns(user):
    active_tenant_session = get_active_tenant_session(user)
    if user_is_customer(user):
        board = Board.objects.get(id=active_tenant_session.tenant.customers_board.id)
    elif user_is_operator(user):
        board = Board.objects.get(id=active_tenant_session.tenant.operators_board.id)
    elif user_is_developer(user):
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


def change_active_tenant(tenant_id, user):
    active_tenant_session = get_active_tenant_session(user)
    active_tenant_session.active = False
    active_tenant_session.save()
    curr_tenant_session = TenantSession.objects.get(tenant=tenant_id, user=user.id)
    curr_tenant_session.active = True
    curr_tenant_session.save()


def tenant_session(user):  # checks if any tenant session exists for specific user
    try:
        TenantSession.objects.filter(user=user)
        return True
    except TenantSession.DoesNotExist:
        return False


def is_active_tenant_session(user):  # checks if any active tenant session exists for specific user
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


def set_active_tenant(tenant, request):  # change tenant state to active based on data in cookies or choose default if no data in cookies
    def _set_active_tenant(tenant, request):
        tenant_session = TenantSession.objects.get(tenant=tenant, user=request.user)
        tenant_session.active = True
        tenant_session.save()

    tenant_cookie = get_tenant_cookie_name(request.user)
    if request.COOKIES.get(tenant_cookie) is None and not TenantSession.objects.filter(active=True, user=request.user):
        _set_active_tenant(tenant, request)
    elif request.COOKIES.get(tenant_cookie) == str(tenant.id):
        _set_active_tenant(tenant, request)


def get_active_tenant(user):
    return Tenant.objects.get(id=get_active_tenant_session(user).tenant.id)


def get_active_tenant_session(user):
    return TenantSession.objects.get(active=True, user=user)


def get_all_user_tenant_sessions(user):
    return TenantSession.objects.filter(user=user.id)


def get_tenant_cookie_name(user):
    return f'active_tenant_id_{str(user.id)}'


def get_active_tenant_tickets(user, only_open):  # filtered by correct user_type
    active_tenant_session = get_active_tenant_session(user)
    if only_open:  # return tickets where resolution is null
        tickets = Ticket.objects.filter(tenant=active_tenant_session.tenant, resolution__isnull=True)
    else:
        tickets = Ticket.objects.filter(tenant=active_tenant_session.tenant)
    user_type = active_tenant_session.user_type
    if user_type == settings.CUST_TYPE and not user.is_superuser:
        return filter_tickets(tickets, {'type__env_type': settings.SD_ENV_TYPE})
    elif user_type == settings.DEV_TYPE:
        return filter_tickets(tickets, {'type__env_type': settings.SOFT_ENV_TYPE})
    return tickets


def get_allow_tickets_to_relate(user, instance):  # exclude already related tickets from select list
    related_tickets = get_related_tickets(instance)
    active_tickets = get_active_tenant_tickets(user, True).exclude(id=instance.id)
    return active_tickets.exclude(id__in=related_tickets)


def get_related_tickets(instance):
    related_tickets = []
    for ticket_id in TicketAssociation.objects.filter(src_ticket=instance).values_list('dest_ticket'):  # instance -> other ticket
        related_tickets.append(int(ticket_id[0]))
    for ticket_id in TicketAssociation.objects.filter(dest_ticket=instance).values_list('src_ticket'):  # instance <- other ticket
        related_tickets.append(int(ticket_id[0]))
    return related_tickets


def filter_tickets(tickets, filters):
    for filter in filters:
        filter_value = filters[filter]
        if filter_value == 'None':
            tickets = tickets.filter(**{filter + '__isnull': True})
        elif filter_value and not isinstance(filter_value, list):
            tickets = tickets.filter(**{filter: filter_value})
        elif isinstance(filter_value, list):
            try:
                tickets = tickets.filter(**{filter + '__in': filter_value})
            except ValueError:
                if len(filter_value) == 1:
                    tickets = tickets.filter(**{filter + '__isnull': True})
                else:
                    filter_values_not_null = []
                    for filtering_value in filter_value:
                        if filtering_value != 'None':
                            filter_values_not_null.append(filtering_value)
                    tickets = tickets.filter(Q(**{filter + '__in': filter_values_not_null}) | Q(**{filter + '__isnull': True}))
    return tickets


def order_tickets(tickets, ordering):
    tickets = tickets.order_by(ordering)
    return tickets


def get_transition_options(ticket, user):
    if user_is_customer(user) and ticket.is_service_desk_type and not user.is_superuser:
        return None
    elif user_is_operator(user) and ticket.is_software_type and not user.is_superuser:
        return None
    else:
        return TransitionAssociation.objects.filter((Q(transition__src_status=ticket.status) | Q(transition__src_status__isnull=True)) & Q(type=ticket.type))


def create_ticket(form, request):
    tenant = get_active_tenant(request.user)
    files = request.FILES.getlist('attachments')
    new_ticket = form.save(commit=False)  # create instance, but do not save
    new_ticket.key = f'{tenant.key}-{tenant.count + 1}'
    new_ticket.tenant = tenant
    new_ticket.status = get_initial_status(new_ticket.type.env_type)
    new_ticket.save()  # create ticket
    if files:
        for file in files:
            add_attachment(file, new_ticket, request)
    logger.info(add_audit_log(request, new_ticket, None, 'create', new_ticket._meta.model.__name__, new_ticket.id))
    tenant.count += 1
    tenant.save()
    form.save_m2m()


def update_ticket(form, request):
    instance_updated = None
    fields = form.initial  # data provided in form
    instance = form.instance  # ticket data
    for attr in fields:
        attr_value = fields[attr]
        form_attr_value = form.data.get(attr)
        if multiple_choice_field(form, attr):  # check if multiple choice field
            form_attr_value_list = form.data.getlist(attr)
            if not multiple_choice_field_equal([str(value.id) for value in attr_value], form_attr_value_list):
                instance_updated = update_ticket_field(instance, instance_updated, attr, form_attr_value, form, request)
        else:
            if str(attr_value) != str(form_attr_value):
                instance_updated = update_ticket_field(instance, instance_updated, attr, form_attr_value, form, request)
    return instance_updated


def update_ticket_field(ticket, ticket_updated, attr, form_attr_value, form, request):
    if ticket_updated is None:
        ticket_updated = ticket
    try:  # if common field
        setattr(ticket, attr, form_attr_value)
    except ValueError:  # if ForeignKey field
        form_attr_value = form.fields.get(attr)._queryset.get(id=form_attr_value)
        setattr(ticket, attr, form_attr_value)
        form_attr_value = form_attr_value.id
    except TypeError:  # if ManyToMany field
        form_attr_value = form.data.getlist(attr)
        ticket.getattr(attr).set(form_attr_value)
        attr = ticket.getattr(attr).model._meta.object_name
        form_attr_value = ','.join(form_attr_value)
    finally:
        logger.info(add_audit_log(request, ticket_updated, None, 'update', attr, form_attr_value))
        ticket_updated.save()
        return ticket_updated


def add_attachment(attachment, ticket, request):
    new_attachment = Attachment(directory=ticket.slug)
    new_attachment.file.save(attachment.name, ContentFile(attachment.read()))
    ticket.attachments.add(new_attachment.id)
    logger.info(add_audit_log(request, ticket, new_attachment, 'add', None, None))
    return new_attachment


def delete_attachment(ticket, attachment, request):
    attachment_association = AttachmentAssociation.objects.filter(attachment=attachment.id, ticket=ticket.id)
    if attachment.user.id != request.user.id and not request.user.is_superuser:
        return f'Attachment not uploaded by you cannot be deleted'
    elif not attachment_association:
        return f'Attachment not exists in <strong>{ticket.key}</strong>'
    else:
        attachment_association.delete()
        Attachment.objects.get(id=attachment.id).delete()
        logger.info(add_audit_log(request, ticket, attachment, 'delete', None, None))
        return True


def add_relation(ticket, ticket_to_relate, request):
    tickets_allowed_to_relate = []
    for allow_ticket_to_relate in get_allow_tickets_to_relate(request.user, ticket).values_list('id'):
        tickets_allowed_to_relate.append(str(allow_ticket_to_relate[0]))
    if str(ticket.id) == ticket_to_relate:
        return f'Ticket cannot have relation with itself'
    elif ticket_to_relate not in tickets_allowed_to_relate:
        return f'Ticket <strong>{ticket}</strong> cannot be related with selected ticket'
    try:
        related_ticket = Ticket.objects.get(id=ticket_to_relate)
    except Ticket.DoesNotExist:
        return f'Ticket with id <strong>{ticket_to_relate}<strong> does not exist'
    new_relation = TicketAssociation(src_ticket=ticket, dest_ticket=related_ticket)
    new_relation.save()
    logger.info(add_audit_log(request, ticket, related_ticket, 'add', None, None))
    return related_ticket


def delete_relation(ticket, related_ticket, request):
    try:
        relation = TicketAssociation.objects.get(src_ticket=ticket, dest_ticket=related_ticket)
    except TicketAssociation.DoesNotExist:
        relation = TicketAssociation.objects.get(src_ticket=related_ticket, dest_ticket=ticket)
    if not relation:
        return f'Relation not exist in <strong>{ticket.key}</strong>'
    else:
        logger.info(add_audit_log(request, ticket, related_ticket, 'delete', None, None))
        relation.delete()
        return True


def add_comment(ticket, comment, request):
    new_comment = Comment(content=comment)
    new_comment.save()
    ticket.comments.add(new_comment)
    logger.info(add_audit_log(request, ticket, new_comment, 'add', None, None))
    return new_comment


def delete_comment(ticket, comment, request):
    comment_association = CommentAssociation.objects.filter(comment=comment.id, ticket=ticket.id)
    if comment.author.id != request.user.id and not request.user.is_superuser:
        return f'Comment not added by you cannot be deleted'
    elif not comment_association:
        return f'Comment not exists in <strong>{ticket.key}</strong>'
    else:
        comment_association.delete()
        Comment.objects.get(id=comment.id).delete()
        logger.info(add_audit_log(request, ticket, comment, 'delete', None, None))
        return True


def edit_comment(ticket, comment, content, request):
    comment_association = CommentAssociation.objects.filter(comment=comment.id, ticket=ticket.id)
    if comment.author.id != request.user.id and not request.user.is_superuser:
        return f'Comment not added by you cannot be updated'
    elif not comment_association:
        return f'Comment not exists in <strong>{ticket.key}</strong>'
    else:
        comment_updated = Comment.objects.get(id=comment.id)
        comment_updated.content = content
        comment_updated.save()
        logger.info(add_audit_log(request, ticket, comment, 'update', None, None))
        return comment_updated


def get_audit_logs(instance):
    audit_logs = AuditLog.objects.filter(object=instance._meta.model.__name__, object_value=instance.id)
    audit_log_records = []
    for audit_log in audit_logs:
        try:
            content_obj = apps.get_model('app', audit_log.content)
            content_obj_value = content_obj.objects.get(id=audit_log.content_value)
        except ValueError:
            content_obj_value = content_obj.objects.filter(id__in=audit_log.content_value.split(',')).values_list('name', flat=True)
            content_obj_value = (', '.join(content_obj_value.values_list('name', flat=True)))
        except LookupError:
            content_obj_value = audit_log.content_value
        except content_obj.DoesNotExist:
            continue
        if audit_log.operation == 'create':
            message = f'created {audit_log.content.lower()}'
        elif audit_log.operation == 'delete':
            message = f'deleted related {audit_log.content.lower()}'
        elif audit_log.operation == 'update':
            message = f'updated {audit_log.content.lower()} to'
        elif audit_log.operation == 'add':
            message = f'added {audit_log.content.lower()}'
        else:
            message = f'changed {audit_log.content.lower()}'
        audit_log_records.append(InstanceAuditLog(audit_log.user, content_obj_value, audit_log.created, message))
    return audit_log_records


def set_ticket_status(transition_association, context_transition_associations, ticket, request):
    if ticket.suspended:
        return f'You cannot change status, because <strong>{ticket}</strong> is suspended'
    for context_transition_association in context_transition_associations:
        if context_transition_association.id == transition_association.id and ticket.type == transition_association.type:
            ticket.status = transition_association.transition.dest_status
            ticket.resolution = transition_association.transition.dest_status.resolution
            ticket.save()
            logger.info(add_audit_log(request, ticket, ticket.status, 'update', None, None))
            return ticket.status
    return f'Transition is not available in <strong>{ticket}</strong>'


def set_ticket_assignee(user, ticket, request):
    if user not in get_user_field_options_by_ticket(ticket) and user is not None:
        return f'Selected user cannot be assigned to <strong>{ticket}</strong>'
    else:
        ticket.assignee = user
        ticket.save()
        logger.info(add_audit_log(request, ticket, None, 'update', 'assignee', ticket.assignee))
        if ticket.assignee is None:
            return f'Ticket <strong>{ticket}</strong> has been unassigned'
        else:
            return ticket.assignee


def set_ticket_suspend(ticket, request):
    if ticket.suspended:
        ticket.suspended = False
    else:
        ticket.suspended = True
    logger.info(add_audit_log(request, ticket, None, 'update', 'suspended', ticket.suspended))
    ticket.save()
    return ticket


def convert_query_dict_to_dict(query_dict):
    new_dict = dict()
    for key, value in dict(query_dict).items():  # QueryDict -> common python dict
        new_dict[key] = value
    return new_dict


def user_is_customer(user):
    active_tenant_session = get_active_tenant_session(user)
    if active_tenant_session.user_type == settings.CUST_TYPE:
        return True
    else:
        return False


def user_is_operator(user):
    active_tenant_session = get_active_tenant_session(user)
    if active_tenant_session.user_type == settings.OPER_TYPE:
        return True
    else:
        return False


def user_is_developer(user):
    active_tenant_session = get_active_tenant_session(user)
    if active_tenant_session.user_type == settings.DEV_TYPE:
        return True
    else:
        return False


def permission_to_suspend(ticket, user):
    if user_is_operator(user) and ticket.is_service_desk_type or user_is_developer(user) and ticket.is_software_type or user.is_superuser:
        return True
    else:
        return False


def permission_to_assign(ticket, user):
    if user_is_operator(user) or user_is_developer(user) and ticket.is_software_type or user.is_superuser:
        return True
    else:
        return False


def permission_to_clone(ticket, user):
    if user_is_operator(user) or user.is_superuser:
        return True
    else:
        return False


def has_access_to_ticket(user, ticket):  # to correct
    if ticket in get_active_tenant_tickets(user, False) or user.is_superuser:
        return True
    else:
        return False


def multiple_choice_field(form, attr): return form.fields.get(attr).widget.attrs.get('multiple')
def multiple_choice_field_equal(list1, list2): return collections.Counter(list1) == collections.Counter(list2)
def get_env_type(type_id): return Type.objects.get(id=type_id).env_type
def json_to_obj(data): return json.loads(data, object_hook=_object_hook)
def _object_hook(converted_dict): return namedtuple('X', converted_dict.keys())(*converted_dict.values())
