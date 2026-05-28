import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from apps.tracker.models import Category, BudgetRecord, CategoryLimit
from apps.account.models import UserProfile
from datetime import date

@pytest.fixture
def test_user(db):
    user = User.objects.create_user(username='testuser', password='password')
    UserProfile.objects.get_or_create(user=user)
    return user

@pytest.fixture
def auth_client(client, test_user):
    client.login(username='testuser', password='password')
    return client

@pytest.fixture
def sample_category(db):
    return Category.objects.create(name="Food", classification='WANT')

@pytest.mark.django_db
class TestEndpoints:
    def test_login_page(self, client):
        url = reverse('login')
        response = client.get(url)
        assert response.status_code == 200

    def test_register_page(self, client):
        url = reverse('register')
        response = client.get(url)
        assert response.status_code == 200

    def test_dashboard_access_denied_anonymous(self, client):
        url = reverse('dashboard_view')
        response = client.get(url)
        assert response.status_code == 302  # Redirects to login

    def test_dashboard_access_allowed_authenticated(self, auth_client):
        url = reverse('dashboard_view')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_record_list(self, auth_client):
        url = reverse('record_list')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_add_record_get(self, auth_client):
        url = reverse('add_record')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_add_record_post(self, auth_client, sample_category):
        url = reverse('add_record')
        data = {
            'type': 'EXPENSE',
            'category': sample_category.id,
            'amount': '50.00',
            'note': 'Lunch',
            'date': date.today().isoformat()
        }
        response = auth_client.post(url, data)
        assert response.status_code == 200
        assert BudgetRecord.objects.filter(note='Lunch').exists()

    def test_manage_budgets(self, auth_client):
        url = reverse('manage_budgets')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_category_limits_partial(self, auth_client):
        url = reverse('category_limits')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_ai_coach(self, auth_client):
        url = reverse('chatbot_view')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_profile_view(self, auth_client, test_user):
        url = reverse('profile_view', kwargs={'pk': test_user.pk})
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_edit_profile(self, auth_client):
        url = reverse('edit-profile')
        response = auth_client.get(url)
        assert response.status_code == 200
