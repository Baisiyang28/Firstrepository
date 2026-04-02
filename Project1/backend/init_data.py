#!/usr/bin/env python3
"""
初始化数据脚本 - 为AI Agent论坛添加示例数据
"""

from app import app, db
from models import User, Topic, Tool
from werkzeug.security import generate_password_hash
import json

def init_data():
    """初始化示例数据"""
    with app.app_context():
        # 检查是否已有数据
        if Topic.query.count() > 0:
            print("数据已存在，跳过初始化")
            return

        print("开始初始化数据...")

        # 创建默认管理员用户（如果不存在）
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                password=generate_password_hash('admin123'),
                email='admin@aiagent.com',
                role='admin',
                bio='论坛管理员，AI Agent爱好者'
            )
            db.session.add(admin)
            db.session.commit()
            print("创建管理员用户")

        # 创建话题数据
        topics_data = [
            {
                'title': 'Agent构建基础',
                'description': '学习如何从零开始构建AI Agent，包括架构设计、组件选择等',
                'category': 'Agent构建',
                'tags': 'Agent构建,架构设计,基础教程',
                'icon': '🏗️'
            },
            {
                'title': 'Prompt工程实战',
                'description': '分享Prompt设计技巧、最佳实践和优化经验',
                'category': 'Prompt工程',
                'tags': 'Prompt工程,优化技巧,最佳实践',
                'icon': '📝'
            },
            {
                'title': 'RAG技术探讨',
                'description': '讨论检索增强生成技术的最新进展和应用案例',
                'category': 'RAG',
                'tags': 'RAG,检索增强,技术探讨',
                'icon': '🔍'
            },
            {
                'title': '智能体实战案例',
                'description': '分享实际项目中的AI Agent应用案例和经验教训',
                'category': '智能体实战',
                'tags': '智能体实战,案例分享,项目经验',
                'icon': '🚀'
            },
            {
                'title': 'AI工具推荐',
                'description': '推荐优秀的AI开发工具、框架和平台',
                'category': 'AI工具',
                'tags': 'AI工具,开发工具,框架推荐',
                'icon': '🛠️'
            },
            {
                'title': '踩坑分享',
                'description': '分享开发过程中遇到的坑和解决方案',
                'category': '踩坑分享',
                'tags': '踩坑分享,问题解决,经验分享',
                'icon': '⚠️'
            }
        ]

        for topic_data in topics_data:
            topic = Topic(**topic_data)
            db.session.add(topic)

        db.session.commit()
        print("创建话题数据")

        # 创建工具数据
        tools_data = [
            {
                'name': 'LangChain',
                'description': '用于开发由语言模型驱动的应用程序的框架',
                'category': '框架',
                'icon': '🔗',
                'website': 'https://langchain.com',
                'docs': 'https://python.langchain.com',
                'github': 'https://github.com/langchain-ai/langchain',
                'features': json.dumps(['模块化', '易扩展', '多模型支持']),
                'rating': 5.0,
                'rating_count': 1,
                'is_recommended': True
            },
            {
                'name': 'AutoGen',
                'description': '微软开发的用于构建多Agent系统的框架',
                'category': '框架',
                'icon': '🤖',
                'website': 'https://microsoft.github.io/autogen',
                'docs': 'https://microsoft.github.io/autogen/docs',
                'github': 'https://github.com/microsoft/autogen',
                'features': json.dumps(['多Agent协作', '自动代码生成', '对话管理']),
                'rating': 4.5,
                'rating_count': 1,
                'is_recommended': True
            },
            {
                'name': 'OpenAI API',
                'description': 'OpenAI提供的强大AI模型API接口',
                'category': 'API',
                'icon': '🧠',
                'website': 'https://openai.com/api',
                'docs': 'https://platform.openai.com/docs',
                'features': json.dumps(['GPT-4', 'DALL-E', 'Whisper']),
                'rating': 5.0,
                'rating_count': 1,
                'is_recommended': True
            },
            {
                'name': 'Pinecone',
                'description': '向量数据库，用于构建RAG应用',
                'category': '平台',
                'icon': '🌲',
                'website': 'https://pinecone.io',
                'docs': 'https://docs.pinecone.io',
                'features': json.dumps(['向量搜索', '高性能', '易集成']),
                'rating': 4.5,
                'rating_count': 1,
                'is_recommended': True
            },
            {
                'name': 'Streamlit',
                'description': '快速构建AI应用界面的Python框架',
                'category': '框架',
                'icon': '🌊',
                'website': 'https://streamlit.io',
                'docs': 'https://docs.streamlit.io',
                'github': 'https://github.com/streamlit/streamlit',
                'features': json.dumps(['快速原型', '交互式界面', 'Python原生']),
                'rating': 4.0,
                'rating_count': 1,
                'is_recommended': False
            },
            {
                'name': 'Hugging Face Transformers',
                'description': '开源的自然语言处理库，支持多种预训练模型',
                'category': '框架',
                'icon': '🤗',
                'website': 'https://huggingface.co/docs/transformers',
                'docs': 'https://huggingface.co/docs/transformers/index',
                'github': 'https://github.com/huggingface/transformers',
                'features': json.dumps(['预训练模型', '多语言支持', '易于微调']),
                'rating': 4.5,
                'rating_count': 1,
                'is_recommended': True
            }
        ]

        for tool_data in tools_data:
            tool = Tool(**tool_data)
            db.session.add(tool)

        db.session.commit()
        print("创建工具数据")

        print("数据初始化完成！")

if __name__ == '__main__':
    init_data()