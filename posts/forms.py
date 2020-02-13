#!/usr/bin/env python3

from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "context", "image", "draft", "publish"]
