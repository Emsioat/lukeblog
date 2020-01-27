from django import template  # 模板标签注册装饰器

from comment.forms import CommentForm
from comment.models import Comment

register = template.Library()


@register.inclusion_tag('comment/block.html')  # 注册器传入评论标签所用的模板
def comment_block(target):
    return {
        # 以下是要传给block.html的上下文
        'target': target,  # 由于是自定义标签，没有request对象，需要将target值传递给模板
        'comment_form': CommentForm(),  # 评论表单
        'comment_list': Comment.get_by_target(target),  # 在Model中定义的classmethod，通过评论目标获取评论列表
    }
