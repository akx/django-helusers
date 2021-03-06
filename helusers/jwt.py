from django.utils.translation import ugettext as _
from django.contrib.auth import get_user_model
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework import exceptions
import random

User = get_user_model()


class JWTAuthentication(JSONWebTokenAuthentication):

    def populate_user(self, user, data):
        exclude_fields = ['is_staff', 'password', 'is_superuser', 'id']
        user_fields = [f.name for f in user._meta.fields if f not in exclude_fields]
        changed = False
        for field in user_fields:
            if field in data:
                val = data[field]
                if getattr(user, field) != val:
                    setattr(user, field, val)
                    changed = True

        # Make sure there are no duplicate usernames
        tries = 0
        while User.objects.filter(username=user.username).exclude(uuid=user.uuid).exists():
            user.username = "%s-%d" % (user.username, tries + 1)
            changed = True

        return changed

    def authenticate_credentials(self, payload):
        user_id = payload.get('sub')
        if not user_id:
            msg = _('Invalid payload.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = User.objects.get(uuid=user_id)
        except User.DoesNotExist:
            user = User(uuid=user_id)
            user.set_unusable_password()

        changed = self.populate_user(user, payload)
        if changed:
            user.save()

        return super(JWTAuthentication, self).authenticate_credentials(payload)


def get_user_id_from_payload_handler(payload):
    return payload.get('sub')
