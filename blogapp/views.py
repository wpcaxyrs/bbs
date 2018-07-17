import json
import os
from bs4 import BeautifulSoup
from blogapp.code import check_code
from django.contrib import auth
from blogapp.models import *
from django.db.models import Count,Avg
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.http import JsonResponse
from django.db.models import F
from django.db import transaction
from blog_demo import settings
from django.shortcuts import render,HttpResponse,redirect
# Create your views here.

#主界面
def index(request):
    #所有文章的显示
    #加上分页
    Article_list = Article.objects.all()
    # 分页器，作业完成再来添加
    # paginator = Paginator(Article_list,1)


    return render(request,'index.html',{'Article_list':Article_list})

#登录界面
def login(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        user = request.POST.get('user')
        pwd = request.POST.get('pwd')
        user = auth.authenticate(username=user,password=pwd)
        if code.upper() != request.session.get('ran_code').upper():
            return render(request, 'login.html',{'msg':'验证码错误'})
        if user:
            auth.login(request,user)
            #全局变量request.user
            return redirect('/index/')

    return render(request, 'login.html',locals())

#注销
def logout(request):
    auth.logout(request)

    return redirect('/index/')

#主页面
def home_page(request,username,**kwargs):
    user = UserInfo.objects.filter(username=username).first()
    # user_list = [v['username'] for v in user_list]
    # 此方法占用内存太高，效率低下

    if not user:
        return render(request,'error.html')

    # print(user_list.pk)
    #用户加上pk显示其主键id
    if kwargs:
        condition = kwargs.get('condition')
        pagam = kwargs.get('pagam')
        if condition == 'category':
            article = Article.objects.filter(user_id=user.pk).filter(category__title=pagam)

        elif condition == 'tag':
            artihcle = Article.objects.filter(user_id=user.pk).filter(tags__title=pagam)

        elif condition == 'article':

            year, month = pagam.split('-')
            print(year, month)

            article = Article.objects.filter(user__username=username).filter(create_time__year=year,
                                                                             create_time__month=month)

    else:
        article = Article.objects.filter(user_id=user.pk)

    blog = user.blog
    category_list = Category.objects.filter(blog=blog).annotate(c=Count('article__title')).values_list("title","c")

    Tag_list = Tag.objects.filter(blog=blog).annotate(c=Count('article__title')).values_list("title","c")

    time = Article.objects.filter(user=user).extra(select={'y_m_time':'strftime("%%Y-%%m",create_time)'}).values('y_m_time').annotate(c=Count('title')).values_list('y_m_time','c')

    return render(request,'home_page.html',locals())

#个人页面
def article_home(request,username,article_id):
    article = Article.objects.filter(nid=article_id)
    blogs = Blog.objects.filter(site_name=username).first()
    comment_list = Comment.objects.filter(article_id=article_id)
    return render(request,'article_home.html',locals())

#点赞系统
def digg(request):
    is_up = json.loads(request.POST.get('is_up'))
    article_id = request.POST.get('article_id')
    user_id = request.user.pk
    start={'state':True,'msg':None}
    obj = ArticleUpDown.objects.filter(article_id=article_id,user_id=user_id).first()
    if obj:
        start['state'] = False
        start['msg'] = obj.is_up
    else:
        with transaction.atomic():
            obj_creat = ArticleUpDown.objects.create(is_up=is_up, article_id=article_id,user_id=user_id)

            if is_up:
                Article.objects.filter(pk=article_id).update(up_count=F('up_count')+1)
            else:
                Article.objects.filter(pk=article_id).update(down_count=F('down_count') +1)

    return JsonResponse(start)

#评论系统
def comment(request):
    user_id=request.POST.get('user_id')
    article_id = request.POST.get('article_id')
    content = request.POST.get('content')
    res = {'state': True,'content':None,'pid':'','user_content':None,'user':None}
    if content:
        pid = request.POST.get('pid')
        with transaction.atomic():
            comment = Comment.objects.create(user_id=user_id,article_id=article_id,content=content,parent_comment_id=pid)
            Article.objects.filter(pk=article_id).update(comment_count=F('comment_count')+1)
        res['timer']=comment.create_time.strftime('%Y-%m-%d %X')
        res['content']=comment.content
        res['pid'] = pid

        if pid:
            res['user_content'] = comment.parent_comment.content
            res["user"] = '%s'%(comment.parent_comment.user)
        return JsonResponse(res)

    else:
        res['state'] = False

        return JsonResponse(res)

#后台管理系统
def Back_manage(request):
    user = request.user
    article_list = Article.objects.filter(user=user)
    return render(request,'backend/backend.html',locals())

#添加文章
def add_article(request):
    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        #利用bs4过滤所有标签，只取文章内容
        soup = BeautifulSoup(content, 'html.parser')
        desc = soup.text[1:150]
        user_id = request.user.pk
        cate_id = request.POST.get('cate')
        tag_list_id = request.POST.getlist('tag')

        with transaction.atomic():
            new_artivle = Article.objects.create(title=title,desc=desc,content=content,user_id=user_id,category_id = cate_id)

            if tag_list_id:
                for tag2art in tag_list_id:
                    Article2Tag.objects.create(article_id=new_artivle.pk,tag_id=tag2art)

        return redirect('/backend/')
    blog = request.user.blog
    cate_list = Category.objects.filter(blog=blog)
    tags = Tag.objects.filter(blog=blog)

    return render(request,'backend/add_article.html',locals())

#文件上传
def upload(request):
    img = request.FILES.get("upload_img")
    img_name = img.name
    path = os.path.join(settings.BASE_DIR,'static','upload',img_name)
    with open(path,'wb')as f:
        for i in img:
            f.write(i)

    res= {
        'error':0,
        'url':'/static/upload/'+ img_name
    }

    return HttpResponse(json.dumps(res))

#文件删除
def delete(request):
    article_id = request.POST.get('article')
    Article.objects.filter(pk=article_id).delete()
    Article2Tag.objects.filter(article_id=article_id).delete()
    res = {'state':True}
    return JsonResponse(res)

#文章编辑
def update(request,article_id):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        soup = BeautifulSoup(content, 'html.parser')
        desc = soup.text[1:150]
        cate_id = request.POST.get('cate')
        tag_list_id = request.POST.getlist('tag')

        with transaction.atomic():
            new_article = Article.objects.filter(pk = article_id).update(title=title,desc=desc,content=content,category_id = cate_id)

            if tag_list_id:
                for tag2art in tag_list_id:
                    Article2Tag.objects.filter(article_id=article_id).update(tag_id=tag2art)

    blog = request.user.blog
    cate_list = Category.objects.filter(blog=blog)
    tags = Tag.objects.filter(blog=blog)
    article = Article.objects.filter(pk=article_id).first()
    article_cate_id = Article.objects.filter(pk=article_id).values('tags__title')
    article_cate_id = [i.get('tags__title') for i in article_cate_id]
    return render(request,'backend/update_article.html',locals())

#login验证
def code(request):
    """
    图片生成
    :return:
    """
    img,ran_code = check_code()
    request.session['ran_code'] = ran_code
    from io import BytesIO
    stream = BytesIO()
    img.save(stream,'png')
    return HttpResponse(stream.getvalue())
