from django import forms
from django.utils.translation import gettext_lazy as _
# Import model BookComment từ file models.py cùng thư mục
from .models import BookComment

class BookCommentForm(forms.ModelForm):
    class Meta:
        model = BookComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full rounded-xl border border-slate-300 p-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': _('Viết suy nghĩ của bạn về cuốn sách này...')
            })
        }
        labels = {
            'content': _('Nội dung bình luận')
        }
