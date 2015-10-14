from django.views.generic import FormView, View
from django.views.generic.detail import SingleObjectMixin
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect
from django.utils.crypto import get_random_string
from django.db.models import Q

from braces.views import LoginRequiredMixin
from allauth.account.adapter import get_adapter
from rest_framework import viewsets

from events.models import Event
from .forms import InviteForm
from .models import Invitation
from . import signals
from .app_settings import app_settings
from .mixins import MultiSerializerViewSetMixin
from .serializers import InvitationSerializer, InvitationListSerializer


class SendInvite(LoginRequiredMixin, FormView):
    template_name = 'invitations/forms/_invite.html'
    form_class = InviteForm

    def form_valid(self, form):
        print(form.cleaned_data)
        email = form.cleaned_data["email"]
        name = form.cleaned_data["name"]
        event = form.cleaned_data["event"]

        invite = form.save(email, name, event)
        invite.send_invitation(self.request)

        return self.render_to_response(
            self.get_context_data(
                success_message='%s has been invited' % email))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class AcceptInvite(SingleObjectMixin, View):
    form_class = InviteForm

    def get(self, *args, **kwargs):
        if app_settings.CONFIRM_INVITE_ON_GET:
            return self.post(*args, **kwargs)
        else:
            raise Http404()

    def post(self, *args, **kwargs):
        self.object = invitation = self.get_object()
        invitation.accepted = True
        invitation.save()
        get_adapter().stash_verified_email(self.request, invitation.email)

        signals.invite_accepted.send(sender=self.__class__,
                                     request=self.request,
                                     email=invitation.email)

        get_adapter().add_message(self.request,
                                  messages.SUCCESS,
                                  'invitations/messages/invite_accepted.txt',
                                  {'email': invitation.email})

        return redirect(app_settings.SIGNUP_REDIRECT)

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        try:
            return queryset.get(key=self.kwargs["key"].lower())
        except Invitation.DoesNotExist:
            raise Http404()

    def get_queryset(self):
        return Invitation.objects.all_valid()


class InvitationViewSet(MultiSerializerViewSetMixin, viewsets.ModelViewSet):
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer
    serializer_action_classes = {
        'list': InvitationListSerializer,
        'create': InvitationListSerializer,
    }

    def get_queryset(self):
        user = self.request.user

        # Return all events where user is either the organizer or planner
        events = Event.objects.filter(Q(attendees__user=user, attendees__planner=True) | Q(organizer=user)).distinct()
        #return Invitation.objects.filter(event=events)
        return Invitation.objects.all_valid()

    def perform_create(self, serializer):
        instance = serializer.save(key=get_random_string(64))
        instance.send_invitation(request=self.request)
