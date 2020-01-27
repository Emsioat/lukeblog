from django.shortcuts import redirect  # 重定向模块
from django.views.generic import TemplateView

from .forms import CommentForm


class CommentView(TemplateView):
    """ 评论表单的action功能页面 """
    http_method_names = ['post']  # 此View只处理POST请求
    template_name = 'comment/result.html'  # 返回结果页的模板

    def post(self, request, *args, **kwargs):
        """ 重写POST请求逻辑 """
        comment_form = CommentForm(request.POST)  # 根据forms.py中定义的用户输入表单，取出POST提交表单中用户输入的数据
        target = request.POST.get('target')  # 取出表单中隐藏的target值

        if comment_form.is_valid():  # 如果数据有效
            instance = comment_form.save(commit=False)  # 保存表单为一个实例，但不提交到数据库，默认为True
            instance.target = target  # 添加上述表单实例属性target（值为之前取回的来自页面POST的值）
            instance.save()  # 保存表单并提交到数据库
            succeed = True
            # return redirect(target)  # 重定向到表单提交页面，如果没有这句，将往下执行，返回提交成功的提示
        else:
            succeed = False

        context = {
            'succeed': succeed,
            'form': comment_form,
            'target': target,
        }
        return self.render_to_response(context)
