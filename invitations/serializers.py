from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from events.models import Event

from .models import Invitation

User = get_user_model()


class InvitationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Invitation

        fields = ('id', 'url', 'name', 'email', 'event', 'accepted', 'created', 'key', 'sent')
        read_only_fields = ('id', 'url', 'name', 'email', 'event', 'accepted', 'created', 'key', 'sent')

        rw_fields = tuple(set(fields)-set(read_only_fields))


class InvitationListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Invitation
        fields = ('id', 'url', 'name', 'email', 'event', 'accepted', 'created', 'key', 'sent')
        read_only_fields = ('id', 'url', 'accepted', 'created', 'key', 'sent')

    def validate(self, data):
        event = data['event']
        email = data['email']

        if event.invitees.filter(email=email):
            raise serializers.ValidationError('User has already been invited to this event')

        if event.attendees.filter(user__email=email):
            raise serializers.ValidationError('User is already attending this event')

        return data
