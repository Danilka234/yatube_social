from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ("text", "group", "image")
        help_text = {
            "text": "Введите текст",
            "group": "Выберите группу",
            "image": "Вставьте картинку"
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ("text",)
