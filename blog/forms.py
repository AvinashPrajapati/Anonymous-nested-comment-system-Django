from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    token = forms.CharField(max_length=20)

    class Meta:
        model = Comment
        fields = ("name", "token", "body")

    # overriding default form setting and adding bootstrap class
    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields["name"].widget.attrs = {
            "placeholder": "Enter name",
            "class": "form-control",
            "type": "text",
            "required": "required",
        }
        self.fields["token"].widget.attrs = {
            "placeholder": "Enter The Code Sent to the Mail",
            "class": "form-control",
            "required": "required",
            "type": "text",
        }
        self.fields["body"].widget.attrs = {
            "placeholder": "Comment here...",
            "class": "form-control",
            "required": "required",
            "rows": "5",
        }
