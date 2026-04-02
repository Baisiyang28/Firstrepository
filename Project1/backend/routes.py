from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from models import db, User, Post, Comment, Like, Favorite, Topic, Agent, AgentLike, Question, Answer, QuestionVote, AnswerVote, Tool, ToolRating, Notification
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import json

def create_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    return jwt.encode(payload, 'your_secret_key_here', algorithm='HS256')

def decode_token(token):
    try:
        payload = jwt.decode(token, 'your_secret_key_here', algorithms=['HS256'])
        return payload['user_id']
    except:
        return None

class UserRegister(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            return {'message': 'User already exists'}, 400
        hashed_password = generate_password_hash(password)
        user = User(username=username, password=hashed_password, email=email)
        db.session.add(user)
        db.session.commit()
        return {'message': 'User registered successfully'}, 201

class UserLogin(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            return {'message': 'Invalid credentials'}, 401
        token = create_token(user.id)
        return {'token': token, 'user': {'id': user.id, 'username': user.username, 'role': user.role}}, 200

class UserInfo(Resource):
    def get(self):
        token = request.headers.get('Authorization')
        user_id = decode_token(token)
        if not user_id:
            return {'message': 'Invalid token'}, 401
        user = User.query.get(user_id)
        return {'id': user.id, 'username': user.username, 'email': user.email, 'role': user.role}, 200

class UserEdit(Resource):
    def post(self):
        token = request.headers.get('Authorization')
        user_id = decode_token(token)
        if not user_id:
            return {'message': 'Invalid token'}, 401
        data = request.get_json()
        user = User.query.get(user_id)
        user.email = data.get('email', user.email)
        if 'password' in data:
            user.password = generate_password_hash(data['password'])
        db.session.commit()
        return {'message': 'User updated successfully'}, 200

class PostAdd(Resource):
    def post(self):
        token = request.headers.get('Authorization')
        user_id = decode_token(token)
        if not user_id:
            return {'message': 'Invalid token'}, 401
        data = request.get_json()
        post = Post(
            title=data['title'],
            content=data['content'],
            code=data.get('code'),
            image=data.get('image'),
            category=data['category'],
            author_id=user_id,
            is_anonymous=data.get('is_anonymous', False)
        )
        db.session.add(post)
        db.session.commit()
        return {'message': 'Post added successfully', 'post_id': post.id}, 201

class PostEdit(Resource):
    def post(self):
        token = request.headers.get('Authorization')
        user_id = decode_token(token)
        if not user_id:
            return {'message': 'Invalid token'}, 401
        data = request.get_json()
        post = Post.query.get(data['post_id'])
        if post.author_id != user_id:
            return {'message': 'Unauthorized'}, 403
        post.title = data.get('title', post.title)
        post.content = data.get('content', post.content)
        post.code = data.get('code', post.code)
        post.image = data.get('image', post.image)
        post.category = data.get('category', post.category)
        db.session.commit()
        return {'message': 'Post updated successfully'}, 200

class PostDelete(Resource):
    def post(self):
        token = request.headers.get('Authorization')
        user_id = decode_token(token)
        if not user_id:
            return {'message': 'Invalid token'}, 401
        data = request.get_json()
        post = Post.query.get(data['post_id'])
        if post.author_id != user_id:
            return {'message': 'Unauthorized'}, 403
        db.session.delete(post)
        db.session.commit()
        return {'message': 'Post deleted successfully'}, 200

class PostList(Resource):
    def get(self):
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        category = request.args.get('category')
        search = request.args.get('search')
        query = Post.query.filter_by(status='approved')
        if category:
            query = query.filter_by(category=category)
        if search:
            query = query.filter(Post.title.contains(search) | Post.content.contains(search))
        query = query.order_by(Post.is_top.desc(), Post.created_at.desc())
        posts = query.paginate(page=page, per_page=per_page, error_out=False)
        result = []
        for post in posts.items:
            author_name = '匿名' if post.is_anonymous else post.author.username
            result.append({
                'id': post.id,
                'title': post.title,
                'content': post.content[:100] + '...' if len(post.content) > 100 else post.content,
                'category': post.category,
                'author': author_name,
                'is_top': post.is_top,
                'views': post.views,
                'created_at': post.created_at.isoformat(),
                'likes': len(post.likes),
                'comments': len(post.comments)
            })
        return {'posts': result, 'total': posts.total, 'pages': posts.pages}, 200

class PostDetail(Resource):
    def get(self, post_id):
        post = Post.query.get(post_id)
        if not post or post.status != 'approved':
            return {'message': 'Post not found'}, 404

        # 增加浏览量
        post.views += 1
        db.session.commit()

        author_name = '匿名' if post.is_anonymous else post.author.username
        comments = []
        for comment in post.comments.filter_by(parent_id=None):
            replies = [{'id': r.id, 'content': r.content, 'author': r.author.username, 'created_at': r.created_at.isoformat()} for r in comment.replies]
            comments.append({
                'id': comment.id,
                'content': comment.content,
                'author': comment.author.username,
                'created_at': comment.created_at.isoformat(),
                'replies': replies
            })
        return {
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'code': post.code,
            'image': post.image,
            'category': post.category,
            'author': author_name,
            'is_top': post.is_top,
            'views': post.views,
            'created_at': post.created_at.isoformat(),
            'likes': len(post.likes),
            'comments': comments
        }, 200

class PostAudit(Resource):
    def post(self):
        token = request.headers.get('Authorization')
        user_id = decode_token(token)
        if not user_id or User.query.get(user_id).role != 'admin':
            return {'message': 'Unauthorized'}, 403
        data = request.get_json()
        post = Post.query.get(data['post_id'])
        post.status = data['status']  # approved or rejected
        db.session.commit()
        return {'message': 'Post audited successfully'}, 200

class PostTop(Resource):
    def post(self):
        token = request.headers.get('Authorization')
        user_id = decode_token(token)
        if not user_id or User.query.get(user_id).role != 'admin':
            return {'message': 'Unauthorized'}, 403
        data = request.get_json()
        post = Post.query.get(data['post_id'])
        post.is_top = data['is_top']
        db.session.commit()
        return {'message': 'Post top status updated successfully'}, 200

class CommentAdd(Resource):
    def post(self):
        token = request.headers.get('Authorization')
        user_id = decode_token(token)
        if not user_id:
            return {'message': 'Invalid token'}, 401
        data = request.get_json()
        comment = Comment(
            content=data['content'],
            post_id=data['post_id'],
            author_id=user_id,
            parent_id=data.get('parent_id')
        )
        db.session.add(comment)
        db.session.commit()
        return {'message': 'Comment added successfully', 'comment_id': comment.id}, 201

class ReplyAdd(Resource):
    def post(self):
        # Same as CommentAdd, since reply is a comment with parent_id
        return CommentAdd().post()

class LikeToggle(Resource):
    def post(self):
        token = request.headers.get('Authorization')
        user_id = decode_token(token)
        if not user_id:
            return {'message': 'Invalid token'}, 401
        data = request.get_json()
        like = Like.query.filter_by(user_id=user_id, post_id=data['post_id']).first()
        if like:
            db.session.delete(like)
            message = 'Like removed'
        else:
            like = Like(user_id=user_id, post_id=data['post_id'])
            db.session.add(like)
            message = 'Like added'
        db.session.commit()
        return {'message': message}, 200

class FavoriteToggle(Resource):
    def post(self):
        token = request.headers.get('Authorization')
        user_id = decode_token(token)
        if not user_id:
            return {'message': 'Invalid token'}, 401
        data = request.get_json()
        favorite = Favorite.query.filter_by(user_id=user_id, post_id=data['post_id']).first()
        if favorite:
            db.session.delete(favorite)
            message = 'Favorite removed'
        else:
            favorite = Favorite(user_id=user_id, post_id=data['post_id'])
            db.session.add(favorite)
            message = 'Favorite added'
        db.session.commit()
        return {'message': message}, 200

class FavoriteList(Resource):
    def get(self):
        token = request.headers.get('Authorization')
        user_id = decode_token(token)
        if not user_id:
            return {'message': 'Invalid token'}, 401
        favorites = Favorite.query.filter_by(user_id=user_id).all()
        posts = []
        for fav in favorites:
            post = fav.post
            if post.status == 'approved':
                author_name = '匿名' if post.is_anonymous else post.author.username
                posts.append({
                    'id': post.id,
                    'title': post.title,
                    'content': post.content[:100] + '...' if len(post.content) > 100 else post.content,
                    'category': post.category,
                    'author': author_name,
                    'created_at': post.created_at.isoformat()
                })
        return {'favorites': posts}, 200

class AdminPostWaitAudit(Resource):
    def get(self):
        token = request.headers.get('Authorization')
        user_id = decode_token(token)
        if not user_id or User.query.get(user_id).role != 'admin':
            return {'message': 'Unauthorized'}, 403
        posts = Post.query.filter_by(status='pending').all()
        result = []
        for post in posts:
            result.append({
                'id': post.id,
                'title': post.title,
                'content': post.content[:100] + '...' if len(post.content) > 100 else post.content,
                'category': post.category,
                'author': post.author.username,
                'created_at': post.created_at.isoformat()
            })
        return {'posts': result}, 200

class AdminBan(Resource):
    def post(self):
        token = request.headers.get('Authorization')
        user_id = decode_token(token)
        if not user_id or User.query.get(user_id).role != 'admin':
            return {'message': 'Unauthorized'}, 403
        data = request.get_json()
        user = User.query.get(data['user_id'])
        # Simple ban: delete user or set inactive, but for simplicity, delete
        db.session.delete(user)
        db.session.commit()
        return {'message': 'User banned successfully'}, 200

class AdminDeleteContent(Resource):
    def post(self):
        token = request.headers.get('Authorization')
        user_id = decode_token(token)
        if not user_id or User.query.get(user_id).role != 'admin':
            return {'message': 'Unauthorized'}, 403
        data = request.get_json()
        if 'post_id' in data:
            post = Post.query.get(data['post_id'])
            db.session.delete(post)
        elif 'comment_id' in data:
            comment = Comment.query.get(data['comment_id'])
            db.session.delete(comment)
        db.session.commit()
        return {'message': 'Content deleted successfully'}, 200

# ===== 新增功能API =====

# 话题相关API
class TopicList(Resource):
    def get(self):
        """获取所有话题列表"""
        topics = Topic.query.filter_by(is_active=True).order_by(Topic.created_at.desc()).all()
        result = []
        for topic in topics:
            result.append({
                'id': topic.id,
                'title': topic.title,
                'description': topic.description,
                'category': topic.category,
                'tags': topic.tags.split(',') if topic.tags else [],
                'icon': topic.icon,
                'posts_count': topic.post_count
            })
        return {'topics': result}, 200

class TopicDetail(Resource):
    def get(self, topic_id):
        """获取话题详情"""
        topic = Topic.query.get(topic_id)
        if not topic or not topic.is_active:
            return {'message': 'Topic not found'}, 404

        # 获取该话题下的帖子
        posts = Post.query.filter_by(category=topic.category, status='approved').order_by(Post.created_at.desc()).limit(20).all()
        posts_data = []
        for post in posts:
            author_name = '匿名' if post.is_anonymous else post.author.username
            posts_data.append({
                'id': post.id,
                'title': post.title,
                'content': post.content[:200] + '...' if len(post.content) > 200 else post.content,
                'author': author_name,
                'created_at': post.created_at.isoformat(),
                'likes': len(post.likes),
                'comments': len(post.comments)
            })

        return {
            'topic': {
                'id': topic.id,
                'title': topic.title,
                'description': topic.description,
                'category': topic.category,
                'tags': topic.tags.split(',') if topic.tags else [],
                'icon': topic.icon,
                'posts_count': topic.post_count
            },
            'posts': posts_data
        }, 200

# Agent分享相关API
class AgentList(Resource):
    def get(self):
        """获取Agent分享列表"""
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 12))
        category = request.args.get('category')
        search = request.args.get('search')

        query = Agent.query.filter_by(status='active')
        if category:
            query = query.filter_by(category=category)
        if search:
            query = query.filter(Agent.name.contains(search) | Agent.description.contains(search))

        agents = query.order_by(Agent.likes.desc(), Agent.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

        result = []
        for agent in agents.items:
            result.append({
                'id': agent.id,
                'name': agent.name,
                'description': agent.description,
                'category': agent.category,
                'author': agent.author.username,
                'github_url': agent.github_url,
                'demo_url': agent.demo_url,
                'tags': agent.tags.split(',') if agent.tags else [],
                'likes': agent.likes,
                'views': agent.views,
                'created_at': agent.created_at.isoformat()
            })

        return {
            'agents': result,
            'total': agents.total,
            'pages': agents.pages,
            'current_page': page
        }, 200

class AgentAdd(Resource):
    def post(self):
        """添加Agent分享"""
        token = request.headers.get('Authorization')
        user_id = decode_token(token)
        if not user_id:
            return {'message': 'Invalid token'}, 401

        data = request.get_json()
        agent = Agent(
            name=data['name'],
            description=data['description'],
            category=data['category'],
            author_id=user_id,
            github_url=data.get('github_url'),
            demo_url=data.get('demo_url'),
            documentation_url=data.get('documentation_url'),
            tags=','.join(data.get('tags', [])),
            features=json.dumps(data.get('features', []))
        )
        db.session.add(agent)
        db.session.commit()
        return {'message': 'Agent shared successfully', 'agent_id': agent.id}, 201

class AgentDetail(Resource):
    def get(self, agent_id):
        """获取Agent详情"""
        agent = Agent.query.get(agent_id)
        if not agent or agent.status != 'active':
            return {'message': 'Agent not found'}, 404

        # 增加浏览量
        agent.views += 1
        db.session.commit()

        return {
            'id': agent.id,
            'name': agent.name,
            'description': agent.description,
            'category': agent.category,
            'author': agent.author.username,
            'github_url': agent.github_url,
            'demo_url': agent.demo_url,
            'documentation_url': agent.documentation_url,
            'tags': agent.tags.split(',') if agent.tags else [],
            'features': json.loads(agent.features) if agent.features else [],
            'likes': agent.likes,
            'views': agent.views,
            'created_at': agent.created_at.isoformat()
        }, 200

class AgentLikeToggle(Resource):
    def post(self):
        """Agent点赞/取消点赞"""
        token = request.headers.get('Authorization')
        user_id = decode_token(token)
        if not user_id:
            return {'message': 'Invalid token'}, 401

        data = request.get_json()
        agent_like = AgentLike.query.filter_by(user_id=user_id, agent_id=data['agent_id']).first()

        if agent_like:
            db.session.delete(agent_like)
            agent = Agent.query.get(data['agent_id'])
            agent.likes -= 1
            message = 'Like removed'
        else:
            agent_like = AgentLike(user_id=user_id, agent_id=data['agent_id'])
            db.session.add(agent_like)
            agent = Agent.query.get(data['agent_id'])
            agent.likes += 1
            message = 'Like added'

        db.session.commit()
        return {'message': message}, 200

# 问答社区相关API
class QuestionList(Resource):
    def get(self):
        """获取问题列表"""
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        status = request.args.get('status', 'all')  # all, unanswered, answered, solved
        search = request.args.get('search')
        tag = request.args.get('tag')

        query = Question.query
        if status == 'unanswered':
            query = query.filter_by(status='unanswered')
        elif status == 'answered':
            query = query.filter_by(status='answered')
        elif status == 'solved':
            query = query.filter_by(status='solved')

        if search:
            query = query.filter(Question.title.contains(search) | Question.content.contains(search))
        if tag:
            query = query.filter(Question.tags.contains(tag))

        questions = query.order_by(Question.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

        result = []
        for question in questions.items:
            result.append({
                'id': question.id,
                'title': question.title,
                'content': question.content[:200] + '...' if len(question.content) > 200 else question.content,
                'author': question.author.username,
                'tags': question.tags.split(',') if question.tags else [],
                'status': question.status,
                'answers_count': question.answers_count,
                'views': question.views,
                'votes': question.votes,
                'created_at': question.created_at.isoformat()
            })

        return {
            'questions': result,
            'total': questions.total,
            'pages': questions.pages,
            'current_page': page
        }, 200

class QuestionAdd(Resource):
    def post(self):
        """添加问题"""
        token = request.headers.get('Authorization')
        user_id = decode_token(token)
        if not user_id:
            return {'message': 'Invalid token'}, 401

        data = request.get_json()
        question = Question(
            title=data['title'],
            content=data['content'],
            author_id=user_id,
            tags=','.join(data.get('tags', []))
        )
        db.session.add(question)
        db.session.commit()
        return {'message': 'Question added successfully', 'question_id': question.id}, 201

class QuestionDetail(Resource):
    def get(self, question_id):
        """获取问题详情"""
        question = Question.query.get(question_id)
        if not question:
            return {'message': 'Question not found'}, 404

        # 增加浏览量
        question.views += 1
        db.session.commit()

        # 获取答案
        answers = Answer.query.filter_by(question_id=question_id).order_by(Answer.votes.desc(), Answer.created_at.asc()).all()
        answers_data = []
        for answer in answers:
            answers_data.append({
                'id': answer.id,
                'content': answer.content,
                'author': answer.author.username,
                'is_accepted': answer.is_accepted,
                'votes': answer.votes,
                'created_at': answer.created_at.isoformat()
            })

        return {
            'question': {
                'id': question.id,
                'title': question.title,
                'content': question.content,
                'author': question.author.username,
                'tags': question.tags.split(',') if question.tags else [],
                'status': question.status,
                'answers_count': question.answers_count,
                'views': question.views,
                'votes': question.votes,
                'created_at': question.created_at.isoformat()
            },
            'answers': answers_data
        }, 200

class AnswerAdd(Resource):
    def post(self):
        """添加答案"""
        token = request.headers.get('Authorization')
        user_id = decode_token(token)
        if not user_id:
            return {'message': 'Invalid token'}, 401

        data = request.get_json()
        answer = Answer(
            content=data['content'],
            question_id=data['question_id'],
            author_id=user_id
        )
        db.session.add(answer)

        # 更新问题答案数量
        question = Question.query.get(data['question_id'])
        question.answers_count += 1
        if question.status == 'unanswered':
            question.status = 'answered'

        db.session.commit()
        return {'message': 'Answer added successfully', 'answer_id': answer.id}, 201

class AnswerAccept(Resource):
    def post(self):
        """采纳答案"""
        token = request.headers.get('Authorization')
        user_id = decode_token(token)
        if not user_id:
            return {'message': 'Invalid token'}, 401

        data = request.get_json()
        answer = Answer.query.get(data['answer_id'])
        question = answer.question

        # 只有问题作者可以采纳答案
        if question.author_id != user_id:
            return {'message': 'Unauthorized'}, 403

        # 取消其他答案的采纳状态
        Answer.query.filter_by(question_id=question.id).update({'is_accepted': False})

        # 采纳当前答案
        answer.is_accepted = True
        question.status = 'solved'
        question.is_accepted = True

        db.session.commit()
        return {'message': 'Answer accepted successfully'}, 200

# 工具推荐相关API
class ToolList(Resource):
    def get(self):
        """获取工具列表"""
        category = request.args.get('category', 'all')
        search = request.args.get('search')

        query = Tool.query.filter_by(status='active')
        if category != 'all':
            query = query.filter_by(category=category)
        if search:
            query = query.filter(Tool.name.contains(search) | Tool.description.contains(search))

        tools = query.order_by(Tool.is_recommended.desc(), Tool.rating.desc(), Tool.created_at.desc()).all()

        result = []
        for tool in tools:
            result.append({
                'id': tool.id,
                'name': tool.name,
                'description': tool.description,
                'category': tool.category,
                'icon': tool.icon,
                'website': tool.website,
                'docs': tool.docs,
                'github': tool.github,
                'features': json.loads(tool.features) if tool.features else [],
                'rating': tool.rating,
                'rating_count': tool.rating_count,
                'is_recommended': tool.is_recommended
            })

        return {'tools': result}, 200

class ToolRate(Resource):
    def post(self):
        """为工具评分"""
        token = request.headers.get('Authorization')
        user_id = decode_token(token)
        if not user_id:
            return {'message': 'Invalid token'}, 401

        data = request.get_json()
        tool_id = data['tool_id']
        rating = data['rating']

        if not (1 <= rating <= 5):
            return {'message': 'Rating must be between 1 and 5'}, 400

        # 检查是否已经评分
        existing_rating = ToolRating.query.filter_by(user_id=user_id, tool_id=tool_id).first()
        if existing_rating:
            existing_rating.rating = rating
        else:
            tool_rating = ToolRating(user_id=user_id, tool_id=tool_id, rating=rating)
            db.session.add(tool_rating)

        # 更新工具平均评分
        tool = Tool.query.get(tool_id)
        all_ratings = ToolRating.query.filter_by(tool_id=tool_id).all()
        total_rating = sum(r.rating for r in all_ratings)
        tool.rating = total_rating / len(all_ratings)
        tool.rating_count = len(all_ratings)

        db.session.commit()
        return {'message': 'Rating submitted successfully'}, 200

# 通知相关API
class NotificationList(Resource):
    def get(self):
        """获取用户通知"""
        token = request.headers.get('Authorization')
        user_id = decode_token(token)
        if not user_id:
            return {'message': 'Invalid token'}, 401

        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))

        notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

        result = []
        for notification in notifications.items:
            result.append({
                'id': notification.id,
                'type': notification.type,
                'title': notification.title,
                'content': notification.content,
                'related_id': notification.related_id,
                'is_read': notification.is_read,
                'created_at': notification.created_at.isoformat()
            })

        return {
            'notifications': result,
            'total': notifications.total,
            'pages': notifications.pages,
            'unread_count': Notification.query.filter_by(user_id=user_id, is_read=False).count()
        }, 200

class NotificationMarkRead(Resource):
    def post(self):
        """标记通知为已读"""
        token = request.headers.get('Authorization')
        user_id = decode_token(token)
        if not user_id:
            return {'message': 'Invalid token'}, 401

        data = request.get_json()
        notification_ids = data.get('notification_ids', [])

        if notification_ids:
            Notification.query.filter(Notification.id.in_(notification_ids), Notification.user_id == user_id).update({'is_read': True})
        else:
            # 标记所有通知为已读
            Notification.query.filter_by(user_id=user_id).update({'is_read': True})

        db.session.commit()
        return {'message': 'Notifications marked as read'}, 200

# 统计信息API
class Stats(Resource):
    def get(self):
        """获取论坛统计信息"""
        stats = {
            'total_users': User.query.count(),
            'total_posts': Post.query.filter_by(status='approved').count(),
            'total_questions': Question.query.count(),
            'total_agents': Agent.query.filter_by(status='active').count(),
            'total_tools': Tool.query.filter_by(status='active').count(),
            'active_topics': Topic.query.filter_by(is_active=True).count()
        }
        return {'stats': stats}, 200

# 活跃用户API
class ActiveUsers(Resource):
    def get(self):
        """获取活跃用户列表"""
        # 简单的活跃用户逻辑：最近发帖的用户
        limit = int(request.args.get('limit', 10))

        # 获取最近30天内发帖的用户
        thirty_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=30)
        active_users = db.session.query(User).join(Post).filter(
            Post.created_at >= thirty_days_ago,
            Post.status == 'approved'
        ).group_by(User.id).order_by(db.func.count(Post.id).desc()).limit(limit).all()

        result = []
        for user in active_users:
            post_count = Post.query.filter_by(author_id=user.id, status='approved').count()
            result.append({
                'id': user.id,
                'username': user.username,
                'avatar': user.avatar or f"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><circle cx='50' cy='50' r='50' fill='%23667eea'/><text x='50' y='65' text-anchor='middle' fill='white' font-size='40'>{user.username[0].upper()}</text></svg>",
                'post_count': post_count,
                'bio': user.bio
            })

        return {'users': result}, 200