from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), default='user')  # user, admin
    avatar = db.Column(db.Text)  # base64 encoded avatar
    bio = db.Column(db.Text)  # user biography
    created_at = db.Column(db.DateTime, default=db.func.now())

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    code = db.Column(db.Text)
    image = db.Column(db.Text)  # base64
    category = db.Column(db.String(50), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_anonymous = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    is_top = db.Column(db.Boolean, default=False)
    views = db.Column(db.Integer, default=0)  # view count
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    author = db.relationship('User', backref=db.backref('posts', lazy=True))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'))  # for replies
    created_at = db.Column(db.DateTime, default=db.func.now())
    author = db.relationship('User', backref=db.backref('comments', lazy=True))
    post = db.relationship('Post', backref=db.backref('comments', lazy=True))
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy=True)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

# New models for AI Agent forum features

class Topic(db.Model):
    """话题模型 - 用于话题页面"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # 话题分类
    tags = db.Column(db.String(500))  # 逗号分隔的标签
    icon = db.Column(db.String(50), default='📋')  # 话题图标
    post_count = db.Column(db.Integer, default=0)  # 关联帖子数量
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

class Agent(db.Model):
    """Agent分享模型 - 用于Agent分享页面"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # 工具Agent, 对话Agent, 自动化Agent, 创意Agent
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    github_url = db.Column(db.String(500))
    demo_url = db.Column(db.String(500))
    documentation_url = db.Column(db.String(500))
    tags = db.Column(db.String(500))  # 逗号分隔的标签
    features = db.Column(db.Text)  # 功能特点，JSON格式存储
    status = db.Column(db.String(20), default='active')  # active, inactive
    likes = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    author = db.relationship('User', backref=db.backref('agents', lazy=True))

class AgentLike(db.Model):
    """Agent点赞模型"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

class Question(db.Model):
    """问答问题模型 - 用于问答社区"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tags = db.Column(db.String(500))  # 逗号分隔的标签
    status = db.Column(db.String(20), default='unanswered')  # unanswered, answered, solved
    answers_count = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)
    votes = db.Column(db.Integer, default=0)  # 问题投票数
    is_accepted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    author = db.relationship('User', backref=db.backref('questions', lazy=True))

class Answer(db.Model):
    """问答答案模型"""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_accepted = db.Column(db.Boolean, default=False)  # 是否被采纳为最佳答案
    votes = db.Column(db.Integer, default=0)  # 答案投票数
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    author = db.relationship('User', backref=db.backref('answers', lazy=True))
    question = db.relationship('Question', backref=db.backref('answers', lazy=True))

class QuestionVote(db.Model):
    """问题投票模型"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    vote_type = db.Column(db.String(10), nullable=False)  # up, down
    created_at = db.Column(db.DateTime, default=db.func.now())

class AnswerVote(db.Model):
    """答案投票模型"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    answer_id = db.Column(db.Integer, db.ForeignKey('answer.id'), nullable=False)
    vote_type = db.Column(db.String(10), nullable=False)  # up, down
    created_at = db.Column(db.DateTime, default=db.func.now())

class Tool(db.Model):
    """工具推荐模型 - 用于工具推荐页面"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # 框架, 平台, API, 其他
    icon = db.Column(db.String(50), default='🛠️')  # 工具图标
    website = db.Column(db.String(500), nullable=False)
    docs = db.Column(db.String(500))
    github = db.Column(db.String(500))
    features = db.Column(db.Text)  # 功能特点，JSON格式存储
    rating = db.Column(db.Float, default=0.0)  # 评分 0-5
    rating_count = db.Column(db.Integer, default=0)
    is_recommended = db.Column(db.Boolean, default=False)  # 是否推荐
    status = db.Column(db.String(20), default='active')  # active, inactive
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

class ToolRating(db.Model):
    """工具评分模型"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tool_id = db.Column(db.Integer, db.ForeignKey('tool.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    created_at = db.Column(db.DateTime, default=db.func.now())

class Notification(db.Model):
    """通知模型 - 用于用户通知系统"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # like, comment, answer, mention, etc.
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    related_id = db.Column(db.Integer)  # 相关对象的ID (post_id, comment_id, etc.)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    user = db.relationship('User', backref=db.backref('notifications', lazy=True))