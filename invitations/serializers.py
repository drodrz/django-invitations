from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

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

        # if serializer.is_valid():
            # invite = Invitation.create(self.validated_data['email'],
            #                            self.validated_data['name'],
            #                            self.validated_data['event'],)
            # invite.send_invitation(request=None)
            # serializer.save(key=invite.key)

    # def create(self, validated_data):
    #     print('Hello from create', validated_data)
    #     invite = Invitation.objects.create(**validated_data)
    #     invite.send_invitation(request=None)
    #     return invite

    # def save(self):
    #     invite = Invitation.create(self.validated_data['email'],
    #                                        self.validated_data['name'],
    #                                        self.validated_data['event'],)
    #     invite.send_invitation(request=None)

