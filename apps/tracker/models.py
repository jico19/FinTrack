from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    """
    F-06: Store categories in the database as a Category model.
    """
    class Classification(models.TextChoices):
        NEED = "NEED", "Need"
        WANT = "WANT", "Want"
        SAVING = "SAVING", "Saving"
        INCOME = "INCOME", "Income"

    name = models.CharField(max_length=100)
    classification = models.CharField(max_length=20, choices=Classification)

    def __str__(self):
        return f"{self.name} ({self.get_classification_display()})"

class CategoryLimit(models.Model):
    """
    F-08: Monthly spending limits per category per user.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="limits")
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    limit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    month = models.DateField() # Store as first day of month (e.g. 2026-04-01)

    class Meta:
        unique_together = ('user', 'category', 'month')

    def __str__(self):
        return f"{self.user.username} - {self.category.name} Limit for {self.month.strftime('%B %Y')}"

class BudgetRecord(models.Model):
    """
    F-03: Amount, note, date, category, type.
    """
    class Type(models.TextChoices):
        INCOME = "INCOME", "Income"
        EXPENSE = "EXPENSE", "Expense"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="records")
    spending_type = models.CharField(max_length=20, choices=Type)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="records")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.TextField(null=True, blank=True)
    date = models.DateField() # Custom date as per F-03
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.spending_type} - {self.category.name}: {self.amount}"
