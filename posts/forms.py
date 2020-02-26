#!/usr/bin/env python3

from django import forms

from pagedown.widgets import PagedownWidget
from .models import Post


class PostForm(forms.ModelForm):
    context = forms.CharField(widget=PagedownWidget())
    publish = forms.DateField(widget=forms.SelectDateWidget)

    class Meta:
        model = Post
        fields = ["title", "context", "image", "draft", "publish"]
