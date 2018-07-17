from django import template
from django.db.models import Count,Avg
from blogapp.models import *

register = template.Library()


@register.inclusion_tag("left_html.html")
def cat_tag_time(username):
    user = UserInfo.objects.filter(username=username).first()

    blog = user.blog
    blog_id = Blog.objects.filter(site_name=user).values('nid').first()
    blog = blog_id.get('nid')
    category_list = Category.objects.filter(blog_id=blog).annotate(c=Count('article__title')).values_list("title", "c")

    Tag_list = Tag.objects.filter(blog_id=blog).annotate(c=Count('article__title')).values_list("title", "c")

    time = Article.objects.filter(user=user).extra(select={'y_m_time': 'strftime("%%Y-%%m",create_time)'}).values(
        'y_m_time').annotate(c=Count('title')).values_list('y_m_time', 'c')
    return {'category_list':category_list,'Tag_list':Tag_list,'time':time,'username':username}