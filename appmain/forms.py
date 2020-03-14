# \myclub_root\events\forms.py
from django import forms
from django.forms import ModelForm, inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Team, Pick, PickGame, Profile


class ProfileForm(ModelForm):
    required_css_class = 'required'

    class Meta:
        model = Profile
        fields = ('user','favorite_team','phone_number','intro_sound','show_graphics','show_video')
        widgets = {'user': forms.HiddenInput}

    favorite_team = forms.ModelChoiceField(queryset=Team.objects.all(), required=False,
                                           widget=forms.Select(attrs={'style': 'width:250px'}), help_text='Optional.')
    phone_number =  forms.CharField(max_length=30, required=False,
                    widget=forms.TextInput(attrs={'style': 'width:250px'}), help_text='Optional. Format: (xxx)xxx-xxxx')


class SignUpForm(UserCreationForm):
    #    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    #    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')
    phone_number = forms.DateField(help_text='Optional. Format: (xxx)xxx-xxxx')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2', 'email',)


class PickForm(ModelForm):
    required_css_class = 'required'

    class Meta:
        model = Pick
        widgets = {'user': forms.HiddenInput, 'wk': forms.HiddenInput, 'entered_by': forms.HiddenInput,
                   'updated_by': forms.HiddenInput}
        fields = '__all__'

    # def clean(self):


class PickGameForm(ModelForm):
    required_css_class = 'required'

    class Meta:
        model = PickGame
        # widgets = {'user': forms.HiddenInput, 'wk': forms.HiddenInput, 'entered_by': forms.HiddenInput,
        # 'updated_by': forms.HiddenInput}
        fields = '__all__'


class GamePick(ModelForm):
    class Meta:
        model = PickGame
        exclude = ()


GamePickFormSet = inlineformset_factory(Pick, PickGame, form=GamePick, extra=1)
