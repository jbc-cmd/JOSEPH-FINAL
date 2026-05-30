from unittest.mock import patch

from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.test import TestCase, TransactionTestCase
from django.urls import reverse

from .models import DeliveryAddress, UserProfile


class RegisterPhoneValidationTests(TestCase):
    def build_payload(self, phone_number):
        return {
            'first_name': 'Juan',
            'last_name': 'Dela Cruz',
            'username': f'user_{phone_number.replace("+", "").replace(" ", "")}',
            'email': f'{phone_number.replace("+", "").replace(" ", "")}@example.com',
            'phone_number': phone_number,
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'agree': 'on',
        }

    def test_register_accepts_eleven_digit_philippine_mobile_number(self):
        response = self.client.post(
            reverse('accounts:register'),
            self.build_payload('09171234567'),
        )

        self.assertRedirects(response, reverse('products:home'))
        user = User.objects.get(username='user_09171234567')
        self.assertEqual(user.profile.phone_number, '09171234567')

    def test_register_rejects_non_philippine_mobile_number_formats(self):
        invalid_numbers = ['9171234567', '0917123456', '091712345678', '+639171234567', '08171234567']

        for index, phone_number in enumerate(invalid_numbers):
            payload = self.build_payload(phone_number)
            payload['username'] = f'invalid_phone_{index}'
            payload['email'] = f'invalid_phone_{index}@example.com'

            response = self.client.post(reverse('accounts:register'), payload)

            self.assertContains(
                response,
                'Enter a valid Philippine mobile number with 11 digits.',
                status_code=200,
            )
            self.assertFalse(User.objects.filter(username=payload['username']).exists())


class DeliveryAddressSignalTests(TestCase):
    def test_deleting_delivery_address_syncs_profile_to_remaining_address(self):
        user = User.objects.create_user(username='address-user', password='pass')
        home = DeliveryAddress.objects.create(
            user=user,
            label='Home',
            recipient_name='Test User',
            phone_number='09171234567',
            address='123 Sampaguita Street',
            city='Manila',
            is_default=True,
        )
        DeliveryAddress.objects.create(
            user=user,
            label='Office',
            recipient_name='Test User',
            phone_number='09171234567',
            address='456 Orchid Avenue',
            city='Makati',
        )

        home.delete()

        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.default_delivery_address, '456 Orchid Avenue, Makati')
        self.assertEqual(profile.address, '456 Orchid Avenue, Makati')


class UserCascadeDeleteTests(TransactionTestCase):
    def test_deleting_user_with_delivery_address_does_not_leave_profile_reference(self):
        user = User.objects.create_user(username='deleted-user', password='pass')
        UserProfile.objects.get_or_create(user=user)
        DeliveryAddress.objects.create(
            user=user,
            label='Home',
            recipient_name='Deleted User',
            phone_number='09171234567',
            address='789 Rose Road',
            city='Quezon City',
            is_default=True,
        )
        user_id = user.pk

        user.delete()
        connection.check_constraints()

        self.assertFalse(User.objects.filter(pk=user_id).exists())
        self.assertFalse(UserProfile.objects.filter(user_id=user_id).exists())
        self.assertFalse(DeliveryAddress.objects.filter(user_id=user_id).exists())


class ProfileInformationTests(TestCase):
    def test_partial_profile_update_keeps_existing_phone_number(self):
        user = User.objects.create_user(
            username='profile-user',
            password='StrongPass123!',
            first_name='Profile',
            last_name='User',
            email='profile@example.com',
        )
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.phone_number = '09171234567'
        profile.save()

        self.client.force_login(user)
        response = self.client.post(
            reverse('accounts:profile_information'),
            {
                'first_name': 'Profile',
                'last_name': 'Updated',
                'email': 'profile.updated@example.com',
            },
        )

        self.assertRedirects(response, reverse('accounts:profile_information'))
        profile.refresh_from_db()
        user.refresh_from_db()
        self.assertEqual(profile.phone_number, '09171234567')
        self.assertEqual(user.last_name, 'Updated')

    def test_profile_update_saves_normalized_phone_number(self):
        user = User.objects.create_user(
            username='phone-user',
            password='StrongPass123!',
            first_name='Phone',
            last_name='User',
            email='phone@example.com',
        )
        UserProfile.objects.get_or_create(user=user)

        self.client.force_login(user)
        response = self.client.post(
            reverse('accounts:profile_information'),
            {
                'first_name': 'Phone',
                'last_name': 'User',
                'email': 'phone@example.com',
                'phone_number': '0917 123 4567',
            },
        )

        self.assertRedirects(response, reverse('accounts:profile_information'))
        self.assertEqual(UserProfile.objects.get(user=user).phone_number, '09171234567')

    def test_profile_picture_storage_failure_returns_message(self):
        user = User.objects.create_user(
            username='photo-user',
            password='StrongPass123!',
            first_name='Photo',
            last_name='User',
            email='photo@example.com',
        )
        UserProfile.objects.get_or_create(user=user)
        upload = SimpleUploadedFile(
            'avatar.png',
            (
                b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
                b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde'
                b'\x00\x00\x00\x0cIDATx\x9cc\xf8\xff\xff?\x00\x05'
                b'\xfe\x02\xfeA\xdc\xcc\xb8\x00\x00\x00\x00IEND\xaeB`\x82'
            ),
            content_type='image/png',
        )
        storage = UserProfile._meta.get_field('profile_picture').storage

        self.client.force_login(user)
        with patch.object(storage, 'save', side_effect=OSError('media storage unavailable')):
            response = self.client.post(
                reverse('accounts:profile_information'),
                {
                    'first_name': 'Photo',
                    'last_name': 'User',
                    'email': 'photo@example.com',
                    'phone_number': '09171234567',
                    'profile_picture': upload,
                },
            )

        self.assertRedirects(response, reverse('accounts:profile_information'))
        messages = [message.message for message in get_messages(response.wsgi_request)]
        self.assertIn('Profile could not be updated right now. Please try again later.', messages)
