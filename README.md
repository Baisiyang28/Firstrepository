# 项目运行教程

## 环境要求
- Python 3.8+
- 现代浏览器（支持ES6）

## 后端启动步骤
1. 进入backend目录：
   ```
   cd backend
   ```

2. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

3. 运行后端服务器：
   ```
   python app.py
   ```
   服务器将在 http://localhost:5000 启动。

## 前端启动步骤
1. 直接在浏览器中打开 `frontend/index.html` 文件。
   - 由于使用CDN加载Vue和Axios，无需额外安装。
   - 确保后端已启动，否则API调用会失败。

## 一键运行指南
- 后端：运行 `python backend/app.py`
- 前端：双击 `frontend/index.html` 打开浏览器

## 注意事项
- 首次运行后端时，会自动创建SQLite数据库文件 `forum.db`。
- 默认管理员用户：用户名 `admin`，密码 `admin123`，用于审核帖子。
- 截图上传使用base64编码，存储在数据库中。
- 跨域已通过Flask-CORS解决。

## 测试
- 注册用户，登录。
- 发布帖子（可能需要管理员审核）。
- 评论、点赞、收藏。
- 管理员审核帖子。
