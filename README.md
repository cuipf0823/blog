# blog
使用flask和redis实现blog

# 数据结构
## 用户数据

* **name.to.id** 散列表, 根据用户名字查找用户ID或者判断用户名字是否注册过; 
* **email.to.id** 散列表, 根据注册的邮件查找用户ID或者判断邮件是否已经注册过;
* **users:count** 字符串类型, 记录注册的总人数;
* **user:id** 散列表, 记录用户详细信息;
    * name 用户名;
    * password 密码;
    * email 邮件;
    * role_id 角色ID;
    * member_since 注册时间;
    * confirmed 是否邮件确认过;
    * about_me 个人简介;
    * location 地理位置;
    * last_seen 最后一次登录; 

## 博客文章

* **posts:count** 字符串类型, 文章总数, 只增不减;
* **posts:author** 列表, 记录每个用户的文章ID;
* **posts:list** 列表, 所有文章列表, 文章删除时, 移除;
* **posts:del_list** 列表, 记录删除文章ID;
* **post:id** 列表 文章详细信息;
    * title 文章标题;
    * author 文章作者;
    * time 文章发表时间;
    * content 文章内容;
    * category 文章分类;
    * post_id 文章的ID;

# 计划
* 实现关注和被关注的原子性 -- 事务;
* 实现访问频率限制;
