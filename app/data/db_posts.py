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
4. 删除文章列表; 使用列表类型保存 posts:del:list
'''

POSTS_LIST = 'posts:list'
POSTS_COUNT = 'posts:count'
POSTS_DEL_LIST = 'posts:del_list'
# maximum number articles per page
POST_NUM_PAGE = 10


def publish_post(title, author, content, category):
    """
     publish post , temporarily unlocking
    """
    post_id = rd.incr(POSTS_COUNT)
    rd.hmset('post:{}'.format(post_id), {'title': title, 'author': author, 'content': content, 'category': category,
                                         'time': datetime.utcnow()})
    rd.lpush(POSTS_LIST, post_id)


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
    post ID list key is bytes type
    """
    pages = int(rd.llen(POSTS_LIST) / POST_NUM_PAGE + 1)
    if 0 < page_id <= pages:
        return rd.lrange(POSTS_LIST, (page_id - 1) * POST_NUM_PAGE, page_id * POST_NUM_PAGE - 1)
    print('invaild param page id[{0}, {1}]'.format(1, pages))


def get_post(post_id):
    """
    get post infomation
    return dict
    """
    return util.convert(rd.hgetall('post:{}'.format(post_id)))

