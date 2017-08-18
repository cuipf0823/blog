# !/usr/bin/python
# coding=utf-8

from datetime import datetime
from .. import rd
from .. import util

'''
1. 文章详细信息; 使用redis中的散列类型保存; key是'post:id'; 字段包括: title author time content category;
2. 文章总数; 保存于posts:count中; 只增不减;
3. 文章ID列表; 使用列表类型posts:list记录文章列表;
    a. 新文章发布使用LPUSH将文章加入到列表中;
    b. 删除文章 LREM
    c. 文章分页显示 LRANGE
4. 用户文章列表; 保存一个用户的所有文章; 用户名对应一个POST ID列表; posts:author
4. 删除文章列表; 使用列表类型保存 posts:del:list
'''

# 文章列表
POSTS_LIST = 'posts:list'
# 文章总数
POSTS_COUNT = 'posts:count'
# 文章删除列表
POSTS_DEL_LIST = 'posts:del_list'
# 每个作者文章列表
POST_AUTHOR_LIST = 'posts:author:'
# maximum number articles per page
POST_NUM_PAGE = 10


def publish_post(title, author_id, content, category):
    """
     publish post , temporarily unlocking
    """
    post_id = rd.incr(POSTS_COUNT)
    rd.hmset('post:{}'.format(post_id), {'title': title, 'author_id': author_id, 'content': content,
                                         'category': category, 'time': datetime.utcnow()})
    rd.lpush(POSTS_LIST, post_id)
    rd.lpush(POST_AUTHOR_LIST + '{}'.format(author_id), post_id)


def delete_post(post_id):
    """
    delete post, temporarily unlocking
    """
    rd.lrem(POSTS_LIST, post_id, 0)
    rd.lpush(POSTS_DEL_LIST, post_id)


def posts_by_page(page_id):
    """
    paging display
    page_id: start from 1
    post ID list key is str type
    """
    pages = int(rd.llen(POSTS_LIST) / POST_NUM_PAGE + 1)
    if 0 < page_id <= pages:
        return util.convert(rd.lrange(POSTS_LIST, (page_id - 1) * POST_NUM_PAGE, page_id * POST_NUM_PAGE - 1))
    print('invaild param page id[{0}, {1}]'.format(1, pages))


def get_post(post_id):
    """
    get post infomation
    return dict
    """
    return util.convert(rd.hgetall('post:{}'.format(post_id)))


def posts_by_author(author_id, page_id):
    """
    paging display
    get posts list by author
    """
    pages = int(rd.llen(POST_AUTHOR_LIST + '{}'.format(author_id)) / POST_NUM_PAGE + 1)
    if 0 < page_id <= pages:
        return util.convert(rd.lrange(POST_AUTHOR_LIST + '{}'.format(author_id), (page_id - 1) * POST_NUM_PAGE,
                                      page_id * POST_NUM_PAGE - 1))
    print('posts_by_author invaild param author {0} page id[{1}, {2}]: {3}'.format(author, 1, pages, page_id))
