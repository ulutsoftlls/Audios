from django import forms
from django.contrib.admin.widgets import AutocompleteSelect
from django.contrib import admin
from .models import Audios, Univers
from django.core.exceptions import ValidationError
from django_recaptcha.fields import ReCaptchaField

class User_nameForm(forms.Form):
    captcha = ReCaptchaField(label='')
    user_name = forms.CharField(max_length=20,
                                widget=forms.TextInput(
                                    attrs={'class': 'form-control',
                                        'placeholder':'Атыңыз',
                                           "style": "width:200px"}))

    user_name.widget.attrs.update(size="40")



    # Использование ChoiceField с виджетом RadioSelect
    univers = Univers.objects.values_list('univer_name', flat=True)
    univer_name = forms.ChoiceField(choices=[(name, name) for name in univers],
        #widget=forms.RadioSelect(),
        label='Выберите один вариант:'
    )
class MyModel(forms.ModelForm):
    class Meta:
        fields = ('text',)
        widgets = {
            'text': AutocompleteSelect(
                Audios.audio_file.field.remote_field,
                admin.site,
                attrs={'style':'width: 100px'}
            ),
        }



class TextForm(forms.ModelForm):
    #captcha2 = ReCaptchaField(label='', )
    #text = forms.CharField(label='Enter Text', widget=forms.Textarea(attrs={'class': 'form-control'}), required=False)
    class Meta:
        model = Audios
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={ "style": "height:150px; width:80%", 'max_length':'400', 'class': 'form-control', 'placeholder':"Бул жерге жазыңыз...", 'required':'required'})

        }
    def clean_text(self):
        text = str(self.cleaned_data['text'])
        if len(text) > 250:
            raise ValidationError('Кайра жазыңыз')
        return text
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['text'].widget.attrs.update({'class': 'form-control'})

    # def clean(self):
    #     cleaned_data = super().clean()
    #     if not cleaned_data.get('text'):
    #         raise forms.ValidationError('Please enter text ')


