from crispy_forms.layout import Submit

from django.forms import ModelForm
from crispy_forms.helper import FormHelper

from golfstats.models import Score


class EditScoreForm(ModelForm):
    class Meta:
        model = Score
        fields = ['score']

    def __init__(self, *args, **kwargs):
        super(EditScoreForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))