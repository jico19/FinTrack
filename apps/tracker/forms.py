from django import forms
from . import models






class BudgetRecordForms(forms.ModelForm):
    class Meta:
        model = models.BudgetRecord
        fields = "__all__"
