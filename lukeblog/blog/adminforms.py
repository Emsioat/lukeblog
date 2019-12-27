"""自定义admin的form"""
from django import forms


class PostAdminForm(forms.ModelForm):
    # 定制desc（文章摘要）字段的展示
    desc = forms.CharField(widget=forms.Textarea, label='自定义摘要form', required=False)
