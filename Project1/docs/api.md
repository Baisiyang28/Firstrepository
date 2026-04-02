# 接口文档

## 用户模块

### POST /api/user/register
用户注册

**请求参数：**
- username: string (用户名)
- password: string (密码)
- email: string (邮箱)

**返回值：**
- 201: { "message": "User registered successfully" }
- 400: { "message": "User already exists" }

### POST /api/user/login
用户登录

**请求参数：**
- username: string
- password: string

**返回值：**
- 200: { "token": "jwt_token", "user": { "id": int, "username": string, "role": string } }
- 401: { "message": "Invalid credentials" }

### GET /api/user/info
获取用户信息

**请求头：**
- Authorization: jwt_token

**返回值：**
- 200: { "id": int, "username": string, "email": string, "role": string }
- 401: { "message": "Invalid token" }

### POST /api/user/edit
编辑用户信息

**请求头：**
- Authorization: jwt_token

**请求参数：**
- email: string (可选)
- password: string (可选)

**返回值：**
- 200: { "message": "User updated successfully" }
- 401: { "message": "Invalid token" }

## 帖子模块

### POST /api/post/add
发布帖子

**请求头：**
- Authorization: jwt_token

**请求参数：**
- title: string
- content: string
- code: string (可选)
- image: string (base64, 可选)
- category: string
- is_anonymous: boolean (可选)

**返回值：**
- 201: { "message": "Post added successfully", "post_id": int }
- 401: { "message": "Invalid token" }

### POST /api/post/edit
编辑帖子

**请求头：**
- Authorization: jwt_token

**请求参数：**
- post_id: int
- title: string (可选)
- content: string (可选)
- code: string (可选)
- image: string (可选)
- category: string (可选)

**返回值：**
- 200: { "message": "Post updated successfully" }
- 401: { "message": "Invalid token" }
- 403: { "message": "Unauthorized" }

### POST /api/post/delete
删除帖子

**请求头：**
- Authorization: jwt_token

**请求参数：**
- post_id: int

**返回值：**
- 200: { "message": "Post deleted successfully" }
- 401: { "message": "Invalid token" }
- 403: { "message": "Unauthorized" }

### GET /api/post/list
获取帖子列表

**查询参数：**
- page: int (默认1)
- per_page: int (默认10)
- category: string (可选)
- search: string (可选)

**返回值：**
- 200: { "posts": [ { "id": int, "title": string, "content": string, "category": string, "author": string, "is_top": boolean, "created_at": string, "likes": int, "comments": int } ], "total": int, "pages": int }

### GET /api/post/detail/{post_id}
获取帖子详情

**返回值：**
- 200: { "id": int, "title": string, "content": string, "code": string, "image": string, "category": string, "author": string, "is_top": boolean, "created_at": string, "likes": int, "comments": [ { "id": int, "content": string, "author": string, "created_at": string, "replies": [...] } ] }
- 404: { "message": "Post not found" }

### POST /api/post/audit
管理员审核帖子

**请求头：**
- Authorization: jwt_token (admin only)

**请求参数：**
- post_id: int
- status: string ("approved" or "rejected")

**返回值：**
- 200: { "message": "Post audited successfully" }
- 403: { "message": "Unauthorized" }

### POST /api/post/top
设置精华置顶

**请求头：**
- Authorization: jwt_token (admin only)

**请求参数：**
- post_id: int
- is_top: boolean

**返回值：**
- 200: { "message": "Post top status updated successfully" }
- 403: { "message": "Unauthorized" }

## 互动模块

### POST /api/comment/add
发布评论

**请求头：**
- Authorization: jwt_token

**请求参数：**
- content: string
- post_id: int

**返回值：**
- 201: { "message": "Comment added successfully", "comment_id": int }
- 401: { "message": "Invalid token" }

### POST /api/reply/add
发布回复

**请求头：**
- Authorization: jwt_token

**请求参数：**
- content: string
- post_id: int
- parent_id: int

**返回值：**
- 201: { "message": "Comment added successfully", "comment_id": int }
- 401: { "message": "Invalid token" }

### POST /api/like
点赞/取消点赞

**请求头：**
- Authorization: jwt_token

**请求参数：**
- post_id: int

**返回值：**
- 200: { "message": "Like added" or "Like removed" }
- 401: { "message": "Invalid token" }

### POST /api/favorite
收藏/取消收藏

**请求头：**
- Authorization: jwt_token

**请求参数：**
- post_id: int

**返回值：**
- 200: { "message": "Favorite added" or "Favorite removed" }
- 401: { "message": "Invalid token" }

### GET /api/favorite/list
获取我的收藏

**请求头：**
- Authorization: jwt_token

**返回值：**
- 200: { "favorites": [ { "id": int, "title": string, "content": string, "category": string, "author": string, "created_at": string } ] }
- 401: { "message": "Invalid token" }

## 管理员模块

### GET /api/admin/post/wait_audit
待审核帖子列表

**请求头：**
- Authorization: jwt_token (admin only)

**返回值：**
- 200: { "posts": [ { "id": int, "title": string, "content": string, "category": string, "author": string, "created_at": string } ] }
- 403: { "message": "Unauthorized" }

### POST /api/admin/ban
禁用违规用户

**请求头：**
- Authorization: jwt_token (admin only)

**请求参数：**
- user_id: int

**返回值：**
- 200: { "message": "User banned successfully" }
- 403: { "message": "Unauthorized" }

### POST /api/admin/delete/content
删除违规内容

**请求头：**
- Authorization: jwt_token (admin only)

**请求参数：**
- post_id: int (可选)
- comment_id: int (可选)

**返回值：**
- 200: { "message": "Content deleted successfully" }
- 403: { "message": "Unauthorized" }