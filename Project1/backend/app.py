from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from models import db
from routes import *
from config import *

app = Flask(__name__)
app.config.from_object('config')

db.init_app(app)
CORS(app)  # 允许跨域

api = Api(app)

# 用户模块
api.add_resource(UserRegister, '/api/user/register')
api.add_resource(UserLogin, '/api/user/login')
api.add_resource(UserInfo, '/api/user/info')
api.add_resource(UserEdit, '/api/user/edit')

# 帖子模块
api.add_resource(PostAdd, '/api/post/add')
api.add_resource(PostEdit, '/api/post/edit')
api.add_resource(PostDelete, '/api/post/delete')
api.add_resource(PostList, '/api/post/list')
api.add_resource(PostDetail, '/api/post/detail/<int:post_id>')
api.add_resource(PostAudit, '/api/post/audit')
api.add_resource(PostTop, '/api/post/top')

# 互动模块
api.add_resource(CommentAdd, '/api/comment/add')
api.add_resource(ReplyAdd, '/api/reply/add')
api.add_resource(LikeToggle, '/api/like')
api.add_resource(FavoriteToggle, '/api/favorite')
api.add_resource(FavoriteList, '/api/favorite/list')

# 管理员模块
api.add_resource(AdminPostWaitAudit, '/api/admin/post/wait_audit')
api.add_resource(AdminBan, '/api/admin/ban')
api.add_resource(AdminDeleteContent, '/api/admin/delete/content')

# 新增功能模块
# 话题模块
api.add_resource(TopicList, '/api/topic/list')
api.add_resource(TopicDetail, '/api/topic/detail/<int:topic_id>')

# Agent分享模块
api.add_resource(AgentList, '/api/agent/list')
api.add_resource(AgentAdd, '/api/agent/add')
api.add_resource(AgentDetail, '/api/agent/detail/<int:agent_id>')
api.add_resource(AgentLikeToggle, '/api/agent/like')

# 问答社区模块
api.add_resource(QuestionList, '/api/question/list')
api.add_resource(QuestionAdd, '/api/question/add')
api.add_resource(QuestionDetail, '/api/question/detail/<int:question_id>')
api.add_resource(AnswerAdd, '/api/answer/add')
api.add_resource(AnswerAccept, '/api/answer/accept')

# 工具推荐模块
api.add_resource(ToolList, '/api/tool/list')
api.add_resource(ToolRate, '/api/tool/rate')

# 通知模块
api.add_resource(NotificationList, '/api/notification/list')
api.add_resource(NotificationMarkRead, '/api/notification/mark_read')

# 统计和活跃用户模块
api.add_resource(Stats, '/api/stats')
api.add_resource(ActiveUsers, '/api/active_users')

# 导入时自动初始化数据库表和示例数据，避免无表错误
with app.app_context():
    db.create_all()
    try:
        from init_data import init_data
        init_data()
    except Exception as e:
        print('数据库初始化跳过:', e)

if __name__ == '__main__':
    app.run(debug=True)
