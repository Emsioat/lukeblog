from django import forms

from .models import Comment


class CommentForm(forms.ModelForm):
    # 注：这里只要提供需要用户填写的部分。target这种由系统指定的字段，在html添加隐藏input，然后View中处理POST来的数据，保存至表单数据库内。
    nickname = forms.CharField(
        label='昵称',
        max_length=50,
        widget=forms.widgets.Input(
            attrs={'class': 'form-control', 'style': "width: 60%;"}
        )
    )
    email = forms.CharField(
        label='E-mail',
        max_length=50,
        widget=forms.widgets.EmailInput(
            attrs={'class': 'form-control', 'style': "width: 60%;"}
        )
    )
    website = forms.CharField(
        label='网站',
        max_length=100,
        widget=forms.widgets.URLInput(
            attrs={'class': 'form-control', 'style': "width:60%;"}
        )
    )
    content = forms.CharField(
        label='内容',
        max_length=500,
        widget=forms.widgets.Textarea(
            attrs={'rows': 6, 'cols': 60, 'class': 'form-control'}
        )
    )

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content) < 5:
            raise forms.ValidationError('长度过短哦！')
        return content

    class Meta:
        model = Comment
        fields = ['nickname', 'email', 'website', 'content']
