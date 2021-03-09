from django import forms
from rango.models import Page, Category, UserProfile, Chat
from django.contrib.auth.models import User


class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=128, help_text="Please enter the category name.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)

    # using inital=0 and hide the field allows to set the field easily to 0

    # inline class to provide additional information on the form
    class Meta:
        # Provide association between ModelForm and a model
        model = Category
        fields = ('name',)


class PageForm(forms.ModelForm):
    title = forms.CharField(max_length=128,
                            help_text="Please enter the title of the page.")
    url = forms.URLField(max_length=200,
                         help_text="Please enter the URL of the page")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    class Meta:
        # Provide association between ModelForm and model
        model = Page

        # either name all fields to include or only name those to exclude
        exclude = ('category',)

    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')

        # If URL doesn't start with http:// then add it
        if url and not url.startswith('http://'):
            url = f'http://{url}'
            cleaned_data['url'] = url

        return cleaned_data


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password',)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('website', 'picture',)


class ChatForm(forms.ModelForm):
    name = forms.CharField(max_length=128, help_text="Please enter the name of the Chat.")

    class Meta:
        model = Chat
        fields = ('name',)
