import os.path
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import update_session_auth_hash, login as auth_login, logout as auth_logout, views as auth_views
from django.contrib.auth.forms import PasswordResetForm, AuthenticationForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.signals import user_logged_out, user_logged_in
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView, ListView
from django.views.generic.edit import UpdateView, DeleteView, CreateView, FormView, FormMixin
from django.views.generic.base import TemplateView
from django.views.decorators.vary import vary_on_cookie
from django.views.decorators.cache import never_cache, cache_page
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.translation import gettext_lazy as _
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.urls.exceptions import NoReverseMatch
from django.core.mail import send_mail, BadHeaderError
from django.core.exceptions import ValidationError, ObjectDoesNotExist, PermissionDenied
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render, reverse, redirect, resolve_url
from django.conf import settings
from django.core.cache import cache
from django.dispatch import receiver
from django.db.models.query_utils import Q
from django.db.models.signals import post_delete, post_save, post_init
from django.template.loader import render_to_string
from .models import Ticket, TransitionAssociation, Attachment, Comment, Status, User, Tenant, TenantSession, Type, Priority
from .forms import TicketCreateForm, TicketFilterViewForm, TicketEditAssigneeForm, TicketEditForm, TicketCommentForm, TicketCloneForm, SetPasswordForm, PasswordChangeForm
from .utils import tenant_manager, board_manager, ticket_manager, util_manager
from .context_processors import context_tenant_session
from .receivers import after_login, after_logout


def validate_get_request(self, request, view_name, tenant_check=False, *args, **kwargs):
    cookie = request.COOKIES.get(Tenant.get_cookie_name(request.user))
    if not request.user.is_authenticated:
        return login_page(request.path)
    if not tenant_manager.active_session_exists(request.user):  # check if any record in tenant_session is stored with active state
        context_tenant_session(request)  # assign active tenant/s based on membership to groups
    if cookie is None or not TenantSession.cookie_valid(cookie, request.user):
        return redirect('tenant_update', tenant_check=tenant_check)
    response = super(view_name, self).get(request, *args, **kwargs)
    response.status_code = 200
    return response


def error_no_tenant(request, template_name='errors/no-tenant.html'):
    return render(request, template_name, {}, status=403)


def csrf_error(request, template_name='errors/csrf-token.html'):
    return render(request, template_name, {}, status=403)


def error_400(request, exception=None, template_name='errors/400.html'):
    return render(request, template_name, {}, status=400)


def error_401(request, exception=None, template_name='errors/401.html'):
    return render(request, template_name, {}, status=401)


def error_403(request, exception=None, template_name='errors/403.html'):
    return render(request, template_name, {}, status=403)


def error_404(request, exception=None, template_name='errors/404.html'):
    return render(request, template_name, {}, status=404)


def error_405(request, exception=None, template_name='errors/405.html'):
    return render(request, template_name, {}, status=405)


def error_500(request, exception=None, template_name='errors/500.html'):
    return render(request, template_name, {}, status=500)


def login_page(path):
    if not path == '/':
        return HttpResponseRedirect(f'{settings.LOGIN_URL}?next={path}')
    else:
        return HttpResponseRedirect(settings.LOGIN_URL)


user_logged_out.connect(after_logout)
user_logged_in.connect(after_login)

# Views


@method_decorator([cache_page(600), vary_on_cookie], name='dispatch')
class TicketCreateView(SuccessMessageMixin, CreateView):
    model = Ticket
    form_class = TicketCreateForm
    template_name = 'ticket/ticket-create.html'

    def get_initial(self):
        initial = super(TicketCreateView, self).get_initial()
        initial['reporter'] = self.request.user
        return initial

    def get_form_kwargs(self):
        kwargs = super(TicketCreateView, self).get_form_kwargs()
        kwargs.update({
            'request': self.request
        })
        return kwargs

    def get_success_url(self, **kwargs):
        return reverse_lazy('view_ticket', args=(self.object.slug,))

    def get_success_message(self, cleaned_data):
        return f'Ticket <strong>{self.object.key}</strong> has been created successfully'

    def form_valid(self, form):
        result = Ticket.create_ticket(form, self.request.user, self.request.FILES.getlist('attachments'))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_data())
        return redirect(self.request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

    def get(self, request, *args, **kwargs):
        return validate_get_request(self, request, TicketCreateView, tenant_check=True, *args, **kwargs)


@method_decorator([cache_page(600), vary_on_cookie], name='dispatch')
class TicketDetailView(FormMixin, DetailView):  # Detail view for ticket
    model = Ticket
    form_class = TicketEditAssigneeForm
    template_name = 'ticket/ticket-view.html'

    def get_form_kwargs(self):
        kwargs = super(TicketDetailView, self).get_form_kwargs()
        kwargs.update({
            'request': self.request,
            'ticket': self.object
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ticket = self.object
        user = self.request.user
        context.update({
            'transitions': ticket.get_transition_options(user),
            'available_tickets_to_relate': ticket.get_relation_options(user),
            'allow_to_suspend': ticket.permission_to_suspend(user),
            'allow_to_assign': ticket.permission_to_assign(user),
            'allow_to_clone': ticket.permission_to_clone(user),
            'audit_logs': ticket.get_audit_logs(),
            'form_update': TicketEditForm(instance=ticket),
            'form_comment': TicketCommentForm(),
            'form_clone_ticket': TicketCloneForm(),
            'form_update_assignee': self.get_form()
        })
        return context

    def get(self, request, *args, **kwargs):
        print(settings.LOG_DIR)
        ticket = self.get_object()
        if not request.user.is_authenticated:
            return login_page(request.path)
        elif not ticket.permission_to_open(request.user):  # TO DO when link on next in login page
            raise PermissionDenied()
        elif ticket.tenant != Tenant.get_active(request.user):  # TO DO when from link
            messages.info(request, 'Active tenant has been changed, returned to board view')
            return redirect('home')
        return validate_get_request(self, request, TicketDetailView, tenant_check=True, *args, **kwargs)


@method_decorator([cache_page(600), vary_on_cookie], name='dispatch')
class TicketEditView(UpdateView):
    model = Ticket
    fields = ['title', 'priority', 'description', 'labels']

    def form_invalid(self, form):
        print(form.errors.as_data())
        return HttpResponse('invalid form')

    def get(self, request, *args, **kwargs):
        return error_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        form = TicketEditForm(request.POST or None, instance=ticket)
        ticket_updated = ticket.update_ticket(form)
        if ticket_updated:
            messages.success(request, f'Ticket <strong>{ticket_updated.key}</strong> has been updated')
        elif ticket_updated is None:
            messages.info(request, f'No changes were made in <strong>{ticket.key}</strong>')
        return HttpResponseRedirect(reverse('view_ticket', args=[ticket.slug]))


class TicketEditStatusView(UpdateView):
    model = Ticket
    fields = ['status']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ticket = self.object
        context.update({
            'transitions': ticket.get_transition_options(self.request.user)
        })
        return context

    def get(self, request, *args, **kwargs):
        return error_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not ticket.permission_to_open(request.user):
            raise PermissionDenied()
        super().post(request, *args, **kwargs)
        context_transition_associations = self.get_context_data().get('transitions')
        try:
            transition_association = TransitionAssociation.objects.get(id=request.POST.get('transition'))
            result = ticket.set_status(transition_association, context_transition_associations)
            if isinstance(result, Status):
                messages.success(request, f'Status of <strong>{ticket.key}</strong> has been changed to <strong>{result}</strong>')
            else:
                messages.error(request, result)
        except ObjectDoesNotExist:
            messages.error(request, f'Transition in <strong>{ticket}</strong> not exist')
        return HttpResponseRedirect(reverse('view_ticket', args=[ticket.slug]))


class TicketEditAssigneeView(UpdateView):
    model = Ticket
    fields = ['assignee']

    def get(self, request, *args, **kwargs):
        return error_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not ticket.permission_to_open(request.user) or not ticket.permission_to_assign(request.user):
            raise PermissionDenied()
        user_id = request.POST.get('assignee')
        try:
            if user_id is None or user_id == '':
                user = None
            else:
                user = User.objects.get(id=request.POST.get('assignee'))
            result = ticket.set_assignee(user)
            if isinstance(result, User):
                messages.success(request, f'Ticket has been assigned to <strong>{result}</strong>')
            elif user is None:
                messages.success(request, result)
            else:
                messages.error(request, result)
        except ObjectDoesNotExist:
            messages.error(request, f'Selected user not exist')
        return HttpResponseRedirect(reverse('view_ticket', args=[ticket.slug]))


class TicketEditSuspendView(UpdateView):
    model = Ticket
    fields = ['suspended']

    def get(self, request, *args, **kwargs):
        return error_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not ticket.permission_to_open(request.user) or not ticket.permission_to_suspend(request.user):
            raise PermissionDenied()
        result = ticket.set_suspended()
        if isinstance(result, Ticket):
            if result.suspended:
                messages.success(request, f'Ticket <strong>{result}</strong> has been suspended')
            else:
                messages.success(request, f'Ticket <strong>{result}</strong> has been unsuspended')
        else:
            messages.error(request, result)
        return HttpResponseRedirect(reverse('view_ticket', args=[ticket.slug]))


class TicketAddAttachmentView(UpdateView):
    model = Ticket

    def get(self, request, *args, **kwargs):
        return error_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not ticket.permission_to_open(request.user):
            raise PermissionDenied()
        files = request.FILES.getlist('attachments')
        if files:
            for file in files:
                result = ticket.add_attachment(file)
                messages.success(request, f'Attachment <strong>{result}</strong> has been uploaded to <strong>{ticket}</strong>')
        else:
            messages.info(request, f'No new files uploaded to <strong>{ticket.key}</strong>')
        return HttpResponseRedirect(reverse('view_ticket', args=[ticket.slug]))


class TicketDeleteAttachmentView(DeleteView):
    model = Ticket

    def get(self, request, *args, **kwargs):
        return error_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not ticket.permission_to_open(request.user):
            raise PermissionDenied()
        attachment_id = request.POST.get('attachment')
        try:
            attachment = Attachment.objects.get(id=attachment_id)
            result = ticket.delete_attachment(attachment, request.user)
            if result is True:
                messages.success(request, f'Attachment <strong>{attachment.filename}</strong> has been deleted from <strong>{ticket.key}</strong>')
            else:
                messages.error(request, result)
        except ObjectDoesNotExist:
            messages.error(request, f'Attachment with value <strong>{attachment_id}</strong> not exist')
        return HttpResponseRedirect(reverse('view_ticket', args=[ticket.slug]))


class TicketAddRelationView(UpdateView):
    model = Ticket

    def get(self, request, *args, **kwargs):
        return error_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not ticket.permission_to_open(request.user):
            raise PermissionDenied()
        tickets_to_relate = request.POST.getlist('relations')
        if tickets_to_relate:
            for ticket_to_relate in tickets_to_relate:
                result = ticket.add_relation(ticket_to_relate, self.request.user)
                if isinstance(result, Ticket):
                    messages.success(request, f'Relation between <strong>{ticket.key}</strong> and <strong>{result}</strong> has been created')
                else:
                    messages.error(request, result)
        else:
            messages.info(request, f'No ticket has been selected to create relation with <strong>{ticket.key}</strong>')
        return HttpResponseRedirect(reverse('view_ticket', args=[ticket.slug]))


class TicketDeleteRelationView(DeleteView):
    model = Ticket

    def get(self, request, *args, **kwargs):
        return error_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not ticket.permission_to_open(request.user):
            raise PermissionDenied()
        relation_id = request.POST.get('relation')
        try:
            relation = Ticket.objects.get(id=relation_id)
            result = ticket.delete_relation(relation, request.user)
            if result is True:
                messages.success(request, f'Relation between <strong>{ticket}</strong> and <strong>{relation}</strong> has been deleted')
            else:
                messages.error(request, result)
        except ObjectDoesNotExist:
            messages.error(request, f'Relation with value <strong>{relation_id}</strong> not exist')
        return HttpResponseRedirect(reverse('view_ticket', args=[ticket.slug]))


class TicketAddCommentView(UpdateView):
    model = Ticket

    def get(self, request, *args, **kwargs):
        return error_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not ticket.permission_to_open(request.user):
            raise PermissionDenied()
        comment_content = request.POST.get('content')
        if comment_content:
            result = ticket.add_comment(comment_content)
            if isinstance(result, Comment):
                messages.success(request, f'Comment in <strong>{ticket.key}</strong> has been added')
            else:
                messages.error(request, result)
        else:
            messages.info(request, f'No content has been entered, a comment has not been added')
        return HttpResponseRedirect(reverse('view_ticket', args=[ticket.slug]))


class TicketDeleteCommentView(DeleteView):
    model = Ticket

    def get(self, request, *args, **kwargs):
        return error_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not ticket.permission_to_open(request.user):
            raise PermissionDenied()
        comment_id = request.POST.get('comment')
        try:
            comment = Comment.objects.get(id=comment_id)
            result = ticket.delete_comment(comment, request.user)
            if result is True:
                messages.success(request, f'Comment from <strong>{ticket}</strong> has been deleted')
            else:
                messages.error(request, result)
        except ObjectDoesNotExist:
            messages.error(request, f'Comment in <strong>{ticket}</strong> not exist')
        return HttpResponseRedirect(reverse('view_ticket', args=[ticket.slug]))


class TicketEditCommentView(UpdateView):
    model = Ticket

    def get(self, request, *args, **kwargs):
        return error_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not ticket.permission_to_open(request.user):
            raise PermissionDenied()
        comment_id = request.POST.get('comment')
        content = request.POST.get('content')
        try:
            comment = Comment.objects.get(id=comment_id)
            result = ticket.edit_comment(comment, content, request.user)
            if isinstance(result, Comment):
                messages.success(request, f'Comment in <strong>{ticket.key}</strong> has been updated')
            else:
                messages.error(request, result)
        except ObjectDoesNotExist:
            messages.error(request, f'Comment in <strong>{ticket}</strong> not exist')
        return HttpResponseRedirect(reverse('view_ticket', args=[ticket.slug]))


class TicketCloneView(UpdateView):
    model = Ticket

    def get(self, request, *args, **kwargs):
        return error_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not ticket.permission_to_open(request.user) or not ticket.permission_to_clone(request.user):
            raise PermissionDenied()
        type_id = request.POST.get('type')
        if type_id:
            result = ticket.clone_ticket(type_id, request.user)
            if isinstance(result, Ticket):
                messages.success(request, f'Ticket <strong>{ticket}</strong> has been cloned to <strong>{result}</strong>')
                return HttpResponseRedirect(reverse('view_ticket', args=[result.slug]))
            else:
                messages.error(request, result)
        else:
            messages.info(request, f'Selected type not exist')
        return HttpResponseRedirect(reverse('view_ticket', args=[ticket.slug]))


@method_decorator([cache_page(600), vary_on_cookie], name='dispatch')
class TicketBoardView(ListView):
    model = Ticket
    context_object_name = 'tickets'
    template_name = 'home.html'

    def get_queryset(self):
        tickets = tenant_manager.get_active_tenant_tickets(self.request.user, True)
        return tickets

    def get_context_data(self, **kwargs):
        context = super(TicketBoardView, self).get_context_data(**kwargs)
        context.update({
            'board_columns_associations': board_manager.get_board_columns_associations(board_manager.get_board_columns(self.request.user)),
            'users': User.objects.all()
        })
        return context

    def get(self, request, *args, **kwargs):
        return validate_get_request(self, request, TicketBoardView, tenant_check=True, *args, **kwargs)


@method_decorator([cache_page(600), vary_on_cookie], name='dispatch')
class TicketFilterView(FormMixin, ListView):
    model = Ticket
    context_object_name = 'tickets'
    form_class = TicketFilterViewForm
    template_name = 'ticket/ticket-filter.html'
    ordering = ['key']

    def get_form_kwargs(self):
        kwargs = super(TicketFilterView, self).get_form_kwargs()
        kwargs.update({
            'request': self.request
        })
        return kwargs

    def get_queryset(self):
        filters = {
            'assignee': self.request.GET.get('assignee', ''),
            'reporter': self.request.GET.get('reporter', ''),
            'status': self.request.GET.getlist('status', ''),
            'resolution': self.request.GET.getlist('resolution', ''),
            'labels': self.request.GET.getlist('label', ''),
            'type': self.request.GET.getlist('type', ''),
            'priority': self.request.GET.getlist('priority', '')
        }
        tickets = tenant_manager.get_active_tenant_tickets(self.request.user)
        tickets = ticket_manager.filter_tickets(tickets, filters)
        if self.request.GET.get('ordering'):  # if any ordering provided in request
            tickets = ticket_manager.order_tickets(tickets, self.get_ordering())
        return tickets

    def get_context_data(self, **kwargs):
        context = super(TicketFilterView, self).get_context_data(**kwargs)
        model = self.model
        context.update({
            'form': self.get_form(),
            'fields': model.get_ordering_fields(),
            'curr_ordering': self.request.GET.get('ordering'),
            'curr_selected': util_manager.convert_query_dict_to_dict(self.request.GET)
        })
        return context

    def get_ordering(self):
        return self.request.GET.get('ordering', 'key')

    def get(self, request, *args, **kwargs):
        return validate_get_request(self, request, TicketFilterView, tenant_check=True, *args, **kwargs)


class LoginView(auth_views.LoginView):
    template_name = 'login.html'
    authentication_form = AuthenticationForm
    redirect_authenticated_user = True

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if self.redirect_authenticated_user and self.request.user.is_authenticated:
            redirect_to = self.get_success_url()
            if redirect_to == self.request.path:
                raise ValueError('Redirection loop for authenticated user detected. Check LOGIN_REDIRECT_URL in settings')
            return HttpResponseRedirect(redirect_to)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = User.objects.get(username=form.get_user().username)
        if user.active:
            auth_login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, 'Incorrect username or password.')
        return HttpResponseRedirect(self.request.path)


INTERNAL_RESET_SESSION_TOKEN = '_password_reset_token'


class PasswordContextMixin:
    extra_context = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title,
            **(self.extra_context or {})
        })
        return context


class PasswordChangeView(auth_views.PasswordChangeView):
    template_name = 'password/password-change.html'
    success_url = reverse_lazy('password_change_success')
    form_class = PasswordChangeForm

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        update_session_auth_hash(self.request, user)  # Important!
        messages.success(self.request, 'Password has been successfully changed')
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        if form.errors.get('old_password'):
            messages.error(self.request, form.errors.get('old_password'))
        elif form.errors.get('new_password2'):
            messages.error(self.request, form.errors.get('new_password2'))
        else:
            messages.error(self.request, f'An error occurred during the operation')
        return HttpResponseRedirect(self.request.path)


class PasswordChangeSuccessView(auth_views.PasswordChangeDoneView):
    template_name = 'password/password-change-success.html'


class PasswordResetView(auth_views.PasswordResetView):
    template_name = 'password/password-reset.html'
    email_template_name = 'password/password-reset-email.html'
    subject_template_name = 'password/password-reset-subject.txt',
    success_url = reverse_lazy('password_reset_sent')
    form_class = PasswordResetForm

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        data = form.cleaned_data['email']
        users = User.objects.filter(Q(email=data))
        if users.exists():
            for user in users:
                email_data = {
                    'email': user.email,
                    'domain': '127.0.0.1:8000',
                    'site_name': settings.SITE_NAME,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'user': user,
                    'token': default_token_generator.make_token(user),
                    'protocol': 'http'}
                email = render_to_string(self.email_template_name, email_data)
                try:
                    send_mail('', email, 'admin@example.com', [user.email])
                except BadHeaderError:
                    messages.error(self.request, 'Invalid header found')
                    return HttpResponseRedirect(reverse('password_reset'))
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_data())
        return HttpResponseRedirect(reverse('password_reset'))


class PasswordResetSentView(auth_views.PasswordResetDoneView):
    template_name = 'password/password-reset-sent.html'


class PasswordResetConfirmView(FormView, PasswordContextMixin):
    form_class = SetPasswordForm
    post_reset_login = False
    post_reset_login_backend = None
    reset_url_token = 'set-password'
    success_url = reverse_lazy('password_reset_success')
    template_name = 'password/password-reset-confirm.html'
    token_generator = default_token_generator

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        assert 'uidb64' in kwargs and 'token' in kwargs
        self.validlink = False
        self.user = self.get_user(kwargs['uidb64'])
        if self.user is not None:
            token = kwargs['token']
            if token == self.reset_url_token:
                session_token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
                if self.token_generator.check_token(self.user, session_token):
                    self.validlink = True  # If the token is valid, display the password reset form.
                    return super().dispatch(*args, **kwargs)
            else:
                if self.token_generator.check_token(self.user, token): # Store the token in the session and redirect to the password reset form at a URL without the token. That avoids the possibility of leaking the token in the HTTP Referer header.
                    self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(token, self.reset_url_token)
                    return HttpResponseRedirect(redirect_url)
        messages.warning(self.request, 'Security token has expired, send email again')
        return self.render_to_response(self.get_context_data())  # display unsuccessful title

    @staticmethod
    def get_user(uidb64):
        try:  # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, ObjectDoesNotExist, ValidationError):
            user = None
        return user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def form_valid(self, form):
        user = form.save()
        del self.request.session[INTERNAL_RESET_SESSION_TOKEN]
        if self.post_reset_login:
            auth_login(self.request, user, self.post_reset_login_backend)
        messages.success(self.request, 'Password has been successfully changed')
        return super().form_valid(form)

    def form_invalid(self, form):
        if form.errors.get('new_password2'):
            messages.error(self.request, form.errors.get('new_password2'))
        return HttpResponseRedirect(self.request.path)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.validlink:
            context['validlink'] = True
        else:
            context.update({
                'form': None,
                'title': _('Password reset unsuccessful'),
                'validlink': False,
            })
        return context


class PasswordResetSuccessView(PasswordContextMixin, TemplateView):
    template_name = 'password/password-reset-success.html'
    title = _('Password reset success')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['login_url'] = resolve_url(settings.LOGIN_URL)
        return context


class RobotsView(TemplateView):
    template_name = 'robots.txt'
    content_type = 'text/plain'

    def get(self, request, *args, **kwargs):
        lines = [
            'User-Agent: *',
            'Disallow: /admin/',
            f'Sitemap: {request.build_absolute_uri("sitemap.xml")}'
        ]
        return HttpResponse('\n'.join(lines), content_type=self.content_type)


def tenant_update(request, tenant_check=False):
    if not request.user.is_authenticated:
        return login_page(request.path)
    elif request.method == 'POST':
        tenant_session = TenantSession.get_active(request.user)
        tenant_id = request.POST.get('tenant_id')
        tenant_session.change_active(tenant_id, request.user)
    else:
        if not tenant_manager.active_session_exists(request.user):
            context_tenant_session(request)
        tenant_session = TenantSession.get_active(request.user)
        if not tenant_session and tenant_check:
            return error_no_tenant(request)
        tenant_id = tenant_session.tenant.id
    try:
        response = redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
        response.set_cookie(key=Tenant.get_cookie_name(request.user), value=tenant_id)
        return response
    except NoReverseMatch:
        response = redirect('home')
        response.set_cookie(key=Tenant.get_cookie_name(request.user), value=tenant_id)
        return response


def logged_out(request, template_name='logged-out.html'):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))
    return render(request, template_name, {}, status=200)

# Receivers DELETE

'''
@receiver(post_delete, sender=Type, dispatch_uid='post_deleted')
def object_post_delete_handler(sender, **kwargs):
    cache.delete('type_objects')


@receiver(post_delete, sender=Priority, dispatch_uid='post_deleted')
def object_post_delete_handler(sender, **kwargs):
    cache.delete('priority_objects')


@receiver(post_delete, sender=User, dispatch_uid='post_deleted')
def object_post_delete_handler(sender, **kwargs):
    cache.delete('user_objects')

# Receivers UPDATE


@receiver(post_save, sender=Type, dispatch_uid='posts_updated')
def object_post_save_handler(sender, **kwargs):
    cache.delete('type_objects')


@receiver(post_save, sender=Priority, dispatch_uid='posts_updated')
def object_post_save_handler(sender, **kwargs):
    cache.delete('priority_objects')


@receiver(post_save, sender=User, dispatch_uid='posts_updated')
def object_post_save_handler(sender, **kwargs):
    cache.delete('users_objects')



@receiver(post_init, sender=Ticket, dispatch_uid='ticket_created')
def object_post_init_handler(sender, instance, **kwargs):
    print(f"init sender: {sender}, instance: {instance}")
    cache.delete('ticket_objects')


@receiver(post_delete, sender=Ticket, dispatch_uid='ticket_deleted')
def object_post_delete_handler(sender, instance, **kwargs):
    print(f"delete sender: {sender}, instance: {instance}")
    cache.delete('ticket_objects')


@receiver(post_save, sender=Ticket, dispatch_uid='tickets_updated')
def object_post_save_handler(sender, instance, **kwargs):
    print(f"save: sender: {sender}, instance: {instance}")
    cache.delete('tickets_objects')
'''

'''
class TenantUpdateView(UpdateView):
    tenant_id = None

    def get_queryset(self):
        tenant_check = {'tenant_check': self.request.GET.get('tenant_check', False)}
        return tenant_check

    def get_success_url(self):
        try:
            response = redirect(self.request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
            response.set_cookie(key=tenant_manager.get_tenant_cookie_name(self.request.user), value=self.tenant_id)
            return response
        except NoReverseMatch:
            response = redirect('home')
            response.set_cookie(key=tenant_manager.get_tenant_cookie_name(self.request.user), value=self.tenant_id)
            return response

    def get(self, request, *args, **kwargs):
        print(args)
        print(self.request.GET)
        print(self.request.GET.get('tenant_check'))
        if not tenant_manager.active_session_exists(request.user):
            context_tenant_session(request)
        tenant_session = tenant_manager.get_active_tenant_session(request.user)
        if not tenant_session and tenant_check:
            return error_no_tenant(request)
        self.tenant_id = tenant_session.tenant.id
        return self.get_success_url()

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        print(request.POST)
        tenant_session = tenant_manager.get_active_tenant_session(request.user)
        tenant_id = request.POST.get('tenant_id')
        tenant_session.change_active(tenant_id, request.user)
        return self.get_success_url()
'''
