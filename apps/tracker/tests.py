from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from apps.tracker.models import Category, BudgetRecord, CategoryLimit
from apps.account.models import UserProfile
from datetime import date
import json

class EndpointTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.profile, _ = UserProfile.objects.get_or_create(user=self.user)
        self.category = Category.objects.create(name='Food', classification=Category.Classification.WANT)
        self.record = BudgetRecord.objects.create(
            user=self.user,
            amount=100,
            spending_type=BudgetRecord.Type.EXPENSE,
            category=self.category,
            date=date.today()
        )

    def login_user(self):
        self.client.login(username='testuser', password='password123')

    def test_login_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/login.html')

    def test_register_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/register.html')

    def test_profile_view_protected(self):
        url = reverse('profile_view', kwargs={'pk': self.user.pk})
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_profile_view_authenticated(self):
        self.login_user()
        response = self.client.get(reverse('profile_view', kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/profile.html')

    def test_dashboard_view(self):
        self.login_user()
        response = self.client.get(reverse('dashboard_view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tracker/dashboard.html')
        # Check if charts data is in context
        self.assertIn('cat_labels_json', response.context)
        self.assertIn('cat_data_json', response.context)
        self.assertIn('nws_labels_json', response.context)
        self.assertIn('nws_data_json', response.context)

    def test_record_list(self):
        self.login_user()
        response = self.client.get(reverse('record_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tracker/record_list.html')

    def test_record_list_htmx(self):
        self.login_user()
        response = self.client.get(reverse('record_list'), HTTP_HX_REQUEST='true')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tracker/partials/record_list_table.html')

    def test_add_record_get_htmx(self):
        self.login_user()
        response = self.client.get(reverse('add_record'), HTTP_HX_REQUEST='true')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tracker/partials/add_record_form.html')

    def test_add_record_post(self):
        self.login_user()
        data = {
            'type': BudgetRecord.Type.EXPENSE,
            'category': self.category.id,
            'amount': '50.00',
            'note': 'Snack',
            'date': date.today().isoformat()
        }
        response = self.client.post(reverse('add_record'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"")
        self.assertEqual(response.headers['HX-Trigger'], 'recordAdded')
        self.assertTrue(BudgetRecord.objects.filter(note='Snack').exists())

    def test_edit_record_get_htmx(self):
        self.login_user()
        response = self.client.get(reverse('edit_record', kwargs={'record_id': self.record.id}), HTTP_HX_REQUEST='true')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tracker/partials/edit_record_form.html')

    def test_edit_record_post(self):
        self.login_user()
        data = {
            'type': BudgetRecord.Type.EXPENSE,
            'category': self.category.id,
            'amount': '150.00',
            'note': 'Updated Food',
            'date': date.today().isoformat()
        }
        response = self.client.post(reverse('edit_record', kwargs={'record_id': self.record.id}), data)
        self.assertEqual(response.status_code, 200)
        self.record.refresh_from_db()
        self.assertEqual(self.record.amount, 150.00)

    def test_delete_record_post(self):
        self.login_user()
        response = self.client.post(reverse('delete_record', kwargs={'record_id': self.record.id}))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(BudgetRecord.objects.filter(id=self.record.id).exists())

    def test_update_limit_post(self):
        self.login_user()
        limit_obj = CategoryLimit.objects.create(
            user=self.user,
            category=self.category,
            limit_amount=500,
            month=date.today().replace(day=1)
        )
        data = {'limit_amount': '600'}
        response = self.client.post(reverse('update_limit', kwargs={'limit_id': limit_obj.id}), data, HTTP_HX_REQUEST='true')
        self.assertEqual(response.status_code, 200)
        limit_obj.refresh_from_db()
        self.assertEqual(limit_obj.limit_amount, 600)

    def test_category_limits_htmx(self):
        self.login_user()
        response = self.client.get(reverse('category_limits'), HTTP_HX_REQUEST='true')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tracker/partials/category_limits.html')

    def test_manage_budgets(self):
        self.login_user()
        response = self.client.get(reverse('manage_budgets'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tracker/manage_budgets.html')

    def test_chatbot_view(self):
        self.login_user()
        response = self.client.get(reverse('chatbot_view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'AI/chatbot_partial.html')

    def test_send_message_post(self):
        self.login_user()
        # Mocking the AI service might be needed if it makes external calls, 
        # but let's see if it works as is (maybe it uses a mock or local logic).
        # Assuming get_coach_response works in tests.
        data = {'message': 'Hello AI'}
        response = self.client.post(reverse('send_message'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'AI/chat_messages_partial.html')

    def test_clear_chat_post(self):
        self.login_user()
        response = self.client.post(reverse('clear_chat'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['HX-Trigger'], 'chatCleared')

    def test_legacy_dashboard(self):
        self.login_user()
        response = self.client.get(reverse('legacy_dashboard'))
        self.assertEqual(response.status_code, 200)
        # Note: legacy_dashboard uses HomePageView.as_view(), need to check its template
