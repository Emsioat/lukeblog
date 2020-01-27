"""自定义admin的form"""
from django import forms
# from ckeditor.widgets import CKEditorWidget  # 无上传文件功能的富文本编辑器
from ckeditor_uploader.widgets import CKEditorUploadingWidget  # 具有上传文件功能的富文本编辑器

from .models import Post


class PostAdminForm(forms.ModelForm):
    # 定制desc（文章摘要）字段的展示
    desc = forms.CharField(widget=forms.Textarea, label='自定义摘要(Textarea)', required=False)  # 将摘要改为Textarea，required为是否必填
    content_ck = forms.CharField(widget=CKEditorUploadingWidget(), label='正文', required=False)  # 富文本编辑器
    content_md = forms.CharField(widget=forms.Textarea(), label='正文', required=False)  # 文本输入框
    content = forms.CharField(widget=forms.HiddenInput(), required=False)  # 接收最终编辑的内容（隐藏输入）

    class Meta:
        model = Post
        fields = (
            'category', 'tag', 'desc', 'title',
            'is_md', 'content', 'content_md', 'content_ck',
            'status',
        )

    def __init__(self, instance=None, initial=None, **kwargs):
        """ 重写__init__()可以修改前端表单显示的初始化数据 """
        # 说明：initial为表单中填写的前端初始化数据(是一个字典)，instance为[文章实例]
        initial = initial or {}  # 相当于if initial
        if instance:
            if instance.is_md:  # 通过判断实例中的is_md值，来自动填写表单
                initial['content_md'] = instance.content
            else:
                initial['content_ck'] = instance.content

        super().__init__(instance=instance, initial=initial, **kwargs)

    def clean(self):
        """ 对用户提交的内容进行处理， """
        is_md = self.cleaned_data.get('is_md')
        if is_md:
            content_field_name = 'content_md'
        else:
            content_field_name = 'content_ck'
        content = self.cleaned_data.get(content_field_name)  # 根据is_md字段来判断最终内容来自哪个编辑器
        if not content:
            self.add_error(content_field_name, '必填项！')
            return
        self.cleaned_data['content'] = content
        return super().clean()

    class Media:
        js = ('js/post_editor.js', )
