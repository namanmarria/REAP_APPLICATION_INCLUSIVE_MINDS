from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.core.exceptions import ValidationError

class CustomAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return False  # Disable regular signup

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        return True  # Allow social signup

    def pre_social_login(self, request, sociallogin):
        # Check if the email domain is allowed
        email = sociallogin.user.email
        if not email or not email.endswith('@themindshare.in'):
            raise ValidationError('Only @themindshare.in email addresses are allowed to sign in.')
        return super().pre_social_login(request, sociallogin) 