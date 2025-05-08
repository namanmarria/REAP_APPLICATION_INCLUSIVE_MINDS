from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
import logging
from django.utils import timezone
import pytz
from django.db import connection
from django.utils.timezone import localtime

logger = logging.getLogger(__name__)
User = get_user_model()

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
        
        # Get Google ID and user data from social account
        google_id = sociallogin.account.uid
        extra_data = sociallogin.account.extra_data
        
        # Check if user already exists
        try:
            user = User.objects.get(email=email)
            logger.info(f"Existing user found: {email}")
            
            # Set MySQL timezone to IST
            with connection.cursor() as cursor:
                cursor.execute("SET time_zone = '+05:30'")
            
            # Convert current time to IST before saving
            ist = pytz.timezone('Asia/Kolkata')
            current_time = timezone.now().astimezone(ist)
            print(f"Current time: {current_time}")
            user.last_login = current_time
            user.save(update_fields=['last_login'])
            
            # Verify the saved time
            with connection.cursor() as cursor:
                cursor.execute("SELECT last_login FROM users WHERE email = %s", [email])
                saved_time = cursor.fetchone()[0]
                logger.info(f"Time saved in MySQL: {saved_time}")
            
            logger.info(f"Updated last_login for user: {email} at {localtime(user.last_login, ist).strftime('%Y-%m-%d %H:%M:%S %Z')}")
            sociallogin.connect(request, user)
        except User.DoesNotExist:
            logger.info(f"Creating new user: {email}")
            # Set data for new user
            sociallogin.user.first_name = extra_data.get('given_name', '')
            sociallogin.user.last_name = extra_data.get('family_name', '')
            sociallogin.user.google_id = google_id
            
        return super().pre_social_login(request, sociallogin)

    def populate_user(self, request, sociallogin, data):
        """
        Called when creating a new user account. Ensures name data is properly set.
        """
        user = super().populate_user(request, sociallogin, data)
        extra_data = sociallogin.account.extra_data
        user.first_name = extra_data.get('given_name', '')
        user.last_name = extra_data.get('family_name', '')
        logger.info(f"Populated new user data for: {user.email}")
        return user 