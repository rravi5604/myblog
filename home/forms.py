from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from froala_editor.widgets import FroalaEditor
from .models import BlogModel
from django.contrib import messages

class BlogForm(forms.ModelForm):
    class Meta:
        model = BlogModel
        fields = ['title', 'content']
        widgets = {
            'content': FroalaEditor(),
        }
        labels = {
            'title': 'Blog Title',
            'content': 'Blog Content',
        }
        help_texts = {
            'title': 'Enter the title of your blog post.',
            'content': 'Write the content of your blog post here.',
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if BlogModel.objects.filter(title=title).exists():
            raise forms.ValidationError("A blog with this title already exists. Please choose a different title.")
        return title

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken. Please choose a different one.")
        return username
