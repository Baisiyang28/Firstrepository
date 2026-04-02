// Components definitions
const Home = {
    props: ['user', 'token', 'globalSearch', 'categoryFilter'],
    template: `
        <div>
            <div class="page-header">
                <h2>🏠 最新动态</h2>
                <p>发现最新的AI Agent讨论和分享</p>
            </div>

            <div class="filters-section">
                <div class="filter-group">
                    <select v-model="category" @change="loadPosts">
                        <option value="">所有分类</option>
                        <option value="Agent构建">Agent构建</option>
                        <option value="Prompt工程">Prompt工程</option>
                        <option value="RAG">RAG</option>
                        <option value="智能体实战">智能体实战</option>
                        <option value="AI工具">AI工具</option>
                        <option value="踩坑分享">踩坑分享</option>
                        <option value="技术讨论">技术讨论</option>
                        <option value="问答">问答</option>
                    </select>
                    <input v-model="search" placeholder="搜索帖子..." @keyup.enter="loadPosts">
                    <button @click="loadPosts" class="search-btn">🔍 搜索</button>
                    <button @click="refresh" class="refresh-btn">🔄 刷新</button>
                </div>
            </div>

            <div class="posts-container">
                <div v-for="post in posts" :key="post.id" class="post">
                    <div class="post-header">
                        <div class="post-meta">
                            <span class="category-tag">{{ post.category }}</span>
                            <span class="author">作者: {{ post.author }}</span>
                            <span class="time">{{ formatTime(post.created_at) }}</span>
                        </div>
                        <div class="post-actions">
                            <button @click="toggleLike(post)" class="action-btn">
                                {{ post.liked ? '❤️' : '🤍' }} {{ post.likes }}
                            </button>
                        </div>
                    </div>
                    <h3>{{ post.title }}</h3>
                    <p class="post-content">{{ truncateContent(post.content) }}</p>
                    <div class="post-footer">
                        <div class="post-stats">
                            <span>💬 {{ post.comments }}</span>
                            <span>👁️ {{ post.views }}</span>
                        </div>
                        <button @click="$emit('setPage', 'post-detail', post.id)" class="read-more-btn">阅读更多</button>
                    </div>
                </div>
            </div>

            <div class="load-more-section">
                <button @click="loadMore" v-if="hasMore" class="load-more-btn">加载更多</button>
                <p v-else class="no-more">没有更多内容了</p>
            </div>
        </div>
    `,
    data() {
        return {
            posts: [],
            category: this.categoryFilter || '',
            search: this.globalSearch || '',
            page: 1,
            hasMore: true
        };
    },
    watch: {
        globalSearch(newVal) {
            this.search = newVal;
            this.loadPosts();
        },
        categoryFilter(newVal) {
            if (newVal) {
                this.category = newVal;
                this.loadPosts();
            }
        }
    },
    methods: {
        loadPosts() {
            this.page = 1;
            this.posts = [];
            this.fetchPosts();
        },
        fetchPosts() {
            axios.get('http://localhost:5000/api/post/list', {
                params: { category: this.category, search: this.search, page: this.page, per_page: 10 }
            }).then(response => {
                this.posts.push(...response.data.posts);
                this.hasMore = this.page < response.data.pages;
            }).catch(error => {
                console.error('加载帖子失败:', error);
            });
        },
        loadMore() {
            this.page++;
            this.fetchPosts();
        },
        refresh() {
            this.loadPosts();
        },
        toggleLike(post) {
            if (!this.user) {
                alert('请先登录');
                return;
            }
            axios.post('http://localhost:5000/api/like', { post_id: post.id }, {
                headers: { Authorization: this.token }
            }).then(() => {
                post.liked = !post.liked;
                post.likes += post.liked ? 1 : -1;
            });
        },
        truncateContent(content) {
            return content.length > 200 ? content.substring(0, 200) + '...' : content;
        },
        formatTime(time) {
            return new Date(time).toLocaleString('zh-CN');
        }
    },
    mounted() {
        this.loadPosts();
    }
};

// Topics Component - 话题页面
const Topics = {
    props: ['setPage', 'onCategorySelected'],
    template: `
        <div>
            <div class="page-header">
                <h2>📋 热门话题</h2>
                <p>探索AI Agent领域的热门话题</p>
            </div>

            <div class="topics-grid">
                <div class="topic-card" v-for="topic in topics" :key="topic.id">
                    <div class="topic-header">
                        <h3>{{ topic.title }}</h3>
                        <span class="topic-posts">{{ topic.posts_count }} 帖子</span>
                    </div>
                    <p>{{ topic.description }}</p>
                    <div class="topic-tags">
                        <span class="tag" v-for="tag in topic.tags" :key="tag">{{ tag }}</span>
                    </div>
                    <button @click="viewTopic(topic)" class="topic-btn">查看话题</button>
                </div>
            </div>
        </div>
    `,
    data() {
        return {
            topics: []
        };
    },
    methods: {
        loadTopics() {
            axios.get('http://localhost:5000/api/topic/list')
                .then(response => {
                    this.topics = response.data.topics || [];
                }).catch(error => {
                    console.error('获取话题列表失败', error);
                });
        },
        viewTopic(topic) {
            if (topic && topic.category) {
                this.$emit('setPage', 'home');
                this.$emit('filter-category', topic.category);
            }
        }
    },
    mounted() {
        this.loadTopics();
    }
};

// AgentShare Component - Agent分享页面
const AgentShare = {
    props: ['user', 'token'],
    template: `
        <div>
            <div class="page-header">
                <h2>🤖 Agent分享</h2>
                <p>分享你构建的AI Agent项目和经验</p>
            </div>

            <div class="share-section">
                <div class="share-form">
                    <h3>分享你的Agent</h3>
                    <form @submit.prevent="shareAgent">
                        <input v-model="agentName" placeholder="Agent名称" required>
                        <textarea v-model="description" placeholder="Agent描述" required></textarea>
                        <input v-model="githubUrl" placeholder="GitHub链接（可选）">
                        <input v-model="demoUrl" placeholder="演示链接（可选）">
                        <input v-model="docsUrl" placeholder="文档链接（可选）">
                        <select v-model="category">
                            <option value="工具Agent">工具Agent</option>
                            <option value="对话Agent">对话Agent</option>
                            <option value="自动化Agent">自动化Agent</option>
                            <option value="创意Agent">创意Agent</option>
                        </select>
                        <input v-model="tags" placeholder="标签，逗号分隔（可选）">
                        <input v-model="features" placeholder="功能亮点，逗号分隔（可选）">
                        <button type="submit" class="share-btn">分享Agent</button>
                    </form>
                    <p v-if="error" class="error">{{ error }}</p>
                    <p v-if="success" class="success">{{ success }}</p>
                </div>
            </div>

            <div class="agents-list">
                <div class="agent-card" v-for="agent in agents" :key="agent.id">
                    <div class="agent-header">
                        <h4>{{ agent.name }}</h4>
                        <span class="agent-category">{{ agent.category }}</span>
                    </div>
                    <p>{{ agent.description }}</p>
                    <div class="agent-links">
                        <a v-if="agent.github_url" :href="agent.github_url" target="_blank">GitHub</a>
                        <a v-if="agent.demo_url" :href="agent.demo_url" target="_blank">演示</a>
                    </div>
                    <div class="agent-stats">
                        <span>⭐ {{ agent.likes }}</span>
                        <span>👁️ {{ agent.views }}</span>
                    </div>
                </div>
            </div>
        </div>
    `,
    data() {
        return {
            agentName: '',
            description: '',
            githubUrl: '',
            demoUrl: '',
            docsUrl: '',
            category: '工具Agent',
            tags: '',
            features: '',
            agents: [],
            error: '',
            success: ''
        };
    },
    methods: {
        loadAgents() {
            axios.get('http://localhost:5000/api/agent/list')
                .then(response => {
                    this.agents = response.data.agents || [];
                }).catch(error => {
                    console.error('加载Agent列表失败', error);
                });
        },
        shareAgent() {
            if (!this.user) {
                this.error = '请先登录后分享Agent';
                return;
            }
            axios.post('http://localhost:5000/api/agent/add', {
                name: this.agentName,
                description: this.description,
                category: this.category,
                github_url: this.githubUrl,
                demo_url: this.demoUrl,
                documentation_url: this.docsUrl,
                tags: this.tags.split(',').map(t => t.trim()).filter(t => t),
                features: this.features.split(',').map(f => f.trim()).filter(f => f)
            }, {
                headers: { Authorization: this.token }
            }).then(() => {
                this.success = 'Agent 分享成功！';
                this.error = '';
                this.agentName = '';
                this.description = '';
                this.githubUrl = '';
                this.demoUrl = '';
                this.docsUrl = '';
                this.tags = '';
                this.features = '';
                this.loadAgents();
            }).catch(error => {
                this.error = error.response?.data?.message || 'Agent 分享失败';
                this.success = '';
            });
        }
    },
    mounted() {
        this.loadAgents();
    }
};

// TechDiscuss Component - 技术讨论页面
const TechDiscuss = {
    props: ['user', 'token'],
    template: `
        <div>
            <div class="page-header">
                <h2>💻 技术讨论</h2>
                <p>深入探讨AI Agent相关技术话题</p>
            </div>

            <div class="discussion-board">
                <div class="discussion-thread" v-for="thread in threads" :key="thread.id">
                    <div class="thread-header">
                        <h3>{{ thread.title }}</h3>
                        <div class="thread-meta">
                            <span>作者: {{ thread.author }}</span>
                            <span>评论: {{ thread.comments }}</span>
                            <span>创建: {{ formatTime(thread.created_at) }}</span>
                        </div>
                    </div>
                    <p class="thread-preview">{{ thread.content }}</p>
                    <div class="thread-tags">
                        <span class="tag" v-for="tag in thread.tags" :key="tag">{{ tag }}</span>
                    </div>
                    <button @click="$emit('setPage', 'post-detail', thread.id)" class="thread-btn">参与讨论</button>
                </div>
            </div>

            <div class="start-discussion">
                <button @click="startNewDiscussion" class="new-discussion-btn" v-if="user">发起新讨论</button>
                <p v-else>请先登录后参与讨论</p>
            </div>
        </div>
    `,
    data() {
        return {
            threads: []
        };
    },
    methods: {
        loadThreads() {
            axios.get('http://localhost:5000/api/post/list', {
                params: { category: '技术讨论', page: 1, per_page: 20 }
            }).then(response => {
                this.threads = response.data.posts.map(post => ({
                    id: post.id,
                    title: post.title,
                    author: post.author,
                    comments: post.comments,
                    created_at: post.created_at,
                    content: post.content
                }));
            }).catch(error => {
                console.error('加载技术讨论失败', error);
            });
        },
        viewThread(threadId) {
            this.$emit('setPage', 'post-detail', threadId);
        },
        startNewDiscussion() {
            this.$emit('setPage', 'add_post');
        },
        formatTime(time) {
            return new Date(time).toLocaleString('zh-CN');
        }
    },
    mounted() {
        this.loadThreads();
    }
};

// QA Component - 问答页面
const QA = {
    props: ['user', 'token'],
    template: `
        <div>
            <div class="page-header">
                <h2>❓ 问答社区</h2>
                <p>在这里提问或解答AI Agent相关问题</p>
            </div>

            <div class="qa-tabs">
                <button @click="setTab('latest')" :class="{active: activeTab === 'latest'}">最新问题</button>
                <button @click="setTab('unanswered')" :class="{active: activeTab === 'unanswered'}">待回答</button>
                <button @click="setTab('solved')" :class="{active: activeTab === 'solved'}">已解决</button>
            </div>

            <div class="questions-list">
                <div class="question-card" v-for="question in questions" :key="question.id">
                    <div class="question-header">
                        <h3>{{ question.title }}</h3>
                        <div class="question-status" :class="question.status">
                            {{ question.status === 'solved' ? '✅ 已解决' : question.status === 'unanswered' ? '⏳ 待回答' : '🆕 最新' }}
                        </div>
                    </div>
                    <p class="question-content">{{ question.content }}</p>
                    <div class="question-meta">
                        <span>提问者: {{ question.author }}</span>
                        <span>创建: {{ formatTime(question.created_at) }}</span>
                        <span>回答: {{ question.answers_count }}</span>
                        <span>浏览: {{ question.views }}</span>
                        <span>投票: {{ question.votes }}</span>
                    </div>
                    <div class="question-tags">
                        <span class="tag" v-for="tag in question.tags" :key="tag">{{ tag }}</span>
                    </div>
                    <button @click="viewQuestion(question.id)" class="answer-btn">
                        查看详情
                    </button>
                </div>
            </div>

            <div class="ask-question">
                <div v-if="user" class="ask-form">
                    <h3>提出新问题</h3>
                    <input v-model="newQuestionTitle" placeholder="问题标题" required>
                    <textarea v-model="newQuestionContent" placeholder="问题内容" required></textarea>
                    <input v-model="newQuestionTags" placeholder="标签（逗号分隔）">
                    <button @click="postQuestion" class="ask-btn">发布问题</button>
                    <p v-if="error" class="error">{{ error }}</p>
                    <p v-if="success" class="success">{{ success }}</p>
                </div>
                <p v-else>请先登录后提问</p>
            </div>
        </div>
    `,
    data() {
        return {
            activeTab: 'latest',
            questions: [],
            newQuestionTitle: '',
            newQuestionContent: '',
            newQuestionTags: '',
            error: '',
            success: ''
        };
    },
    methods: {
        setTab(tab) {
            this.activeTab = tab;
            this.loadQuestions();
        },
        loadQuestions() {
            const params = {
                page: 1,
                per_page: 20
            };
            if (this.activeTab !== 'all') {
                params.status = this.activeTab;
            }
            axios.get('http://localhost:5000/api/question/list', { params })
                .then(response => {
                    this.questions = response.data.questions.map(question => ({
                        ...question,
                        tags: question.tags || []
                    }));
                }).catch(error => {
                    console.error('加载问题失败', error);
                });
        },
        viewQuestion(questionId) {
            this.$emit('setPage', 'qa', questionId);
        },
        postQuestion() {
            if (!this.newQuestionTitle || !this.newQuestionContent) {
                this.error = '标题和内容不能为空';
                return;
            }
            axios.post('http://localhost:5000/api/question/add', {
                title: this.newQuestionTitle,
                content: this.newQuestionContent,
                tags: this.newQuestionTags.split(',').map(t => t.trim()).filter(t => t)
            }, {
                headers: { Authorization: this.token }
            }).then(() => {
                this.success = '问题发布成功';
                this.error = '';
                this.newQuestionTitle = '';
                this.newQuestionContent = '';
                this.newQuestionTags = '';
                this.loadQuestions();
            }).catch(error => {
                this.error = error.response?.data?.message || '问题发布失败';
                this.success = '';
            });
        },
        formatTime(time) {
            return new Date(time).toLocaleString('zh-CN');
        }
    },
    mounted() {
        this.loadQuestions();
    }
};

// Tools Component - 工具推荐页面
const Tools = {
    props: ['token'],
    template: `
        <div>
            <div class="page-header">
                <h2>🛠️ 工具推荐</h2>
                <p>发现优秀的AI Agent开发工具和资源</p>
            </div>

            <div class="tools-categories">
                <button @click="setCategory('all')" :class="{active: activeCategory === 'all'}">全部</button>
                <button @click="setCategory('框架')" :class="{active: activeCategory === '框架'}">框架</button>
                <button @click="setCategory('平台')" :class="{active: activeCategory === '平台'}">平台</button>
                <button @click="setCategory('API')" :class="{active: activeCategory === 'API'}">API</button>
                <button @click="setCategory('其他')" :class="{active: activeCategory === '其他'}">其他</button>
            </div>

            <div class="tools-grid">
                <div class="tool-card" v-for="tool in filteredTools" :key="tool.id">
                    <div class="tool-header">
                        <div class="tool-icon">{{ tool.icon }}</div>
                        <div class="tool-info">
                            <h3>{{ tool.name }}</h3>
                            <span class="tool-category">{{ tool.category }}</span>
                        </div>
                    </div>
                    <p class="tool-description">{{ tool.description }}</p>
                    <div class="tool-features">
                        <span class="feature" v-for="feature in tool.features" :key="feature">{{ feature }}</span>
                    </div>
                    <div class="tool-links">
                        <a :href="tool.website" target="_blank" class="tool-link">官网</a>
                        <a v-if="tool.docs" :href="tool.docs" target="_blank" class="tool-link">文档</a>
                        <a v-if="tool.github" :href="tool.github" target="_blank" class="tool-link">GitHub</a>
                    </div>
                    <div class="tool-rating">
                        <div class="stars">
                            <span v-for="i in 5" :key="i" :class="{filled: i <= Math.round(tool.rating)}">⭐</span>
                        </div>
                        <span class="rating-text">{{ tool.rating.toFixed(1) }}/5</span>
                        <div class="rate-action" v-if="token">
                            <select v-model="tool.userRating">
                                <option value="">评分</option>
                                <option v-for="n in 5" :key="n" :value="n">{{ n }} 星</option>
                            </select>
                            <button @click="rateTool(tool)">提交</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,
    data() {
        return {
            activeCategory: 'all',
            tools: []
        };
    },
    computed: {
        filteredTools() {
            if (this.activeCategory === 'all') {
                return this.tools;
            }
            return this.tools.filter(tool => tool.category === this.activeCategory);
        }
    },
    methods: {
        setCategory(category) {
            this.activeCategory = category;
        },
        loadTools() {
            axios.get('http://localhost:5000/api/tool/list')
                .then(response => {
                    this.tools = response.data.tools || [];
                    this.tools.forEach(t => { t.userRating = ''; });
                }).catch(error => {
                    console.error('加载工具列表失败', error);
                });
        },
        rateTool(tool) {
            if (!tool.userRating) {
                return;
            }
            axios.post('http://localhost:5000/api/tool/rate', {
                tool_id: tool.id,
                rating: Number(tool.userRating)
            }, {
                headers: { Authorization: this.token }
            }).then(() => {
                this.loadTools();
            }).catch(error => {
                console.error('评分失败', error);
            });
        }
    },
    mounted() {
        this.loadTools();
    }
};

// Login Component - 深色主题登录页面
const Login = {
    template: `
        <div class="auth-page">
            <!-- 全屏深色背景 -->
            <div class="auth-background">
                <div class="tech-grid"></div>
                <div class="glow-effect"></div>
            </div>

            <!-- 顶部Logo区域 -->
            <div class="auth-header">
                <div class="logo-section">
                    <div class="logo-icon">🤖</div>
                    <div class="logo-text">AI AGENT FORUM</div>
                </div>
            </div>

            <!-- 核心登录卡片 -->
            <div class="auth-container">
                <div class="auth-card">
                    <!-- 登录方式切换栏 -->
                    <div class="auth-tabs">
                        <div class="tab active">账号登录</div>
                    </div>

                    <!-- 登录表单 -->
                    <form @submit.prevent="handleLogin" class="auth-form">
                        <div class="form-group">
                            <div class="input-wrapper">
                                <input
                                    v-model="username"
                                    type="text"
                                    placeholder="请输入用户名"
                                    class="auth-input"
                                    :class="{ 'error': usernameError }"
                                    @focus="clearErrors"
                                    required
                                >
                                <div class="input-line" :class="{ 'focused': usernameFocused }"></div>
                            </div>
                            <div v-if="usernameError" class="field-error">{{ usernameError }}</div>
                        </div>

                        <div class="form-group">
                            <div class="input-wrapper">
                                <input
                                    v-model="password"
                                    :type="showPassword ? 'text' : 'password'"
                                    placeholder="请输入密码"
                                    class="auth-input"
                                    :class="{ 'error': passwordError }"
                                    @focus="clearErrors"
                                    required
                                >
                                <button
                                    type="button"
                                    class="password-toggle"
                                    @click="showPassword = !showPassword"
                                >
                                    {{ showPassword ? '🙈' : '👁️' }}
                                </button>
                                <div class="input-line" :class="{ 'focused': passwordFocused }"></div>
                            </div>
                            <div v-if="passwordError" class="field-error">{{ passwordError }}</div>
                        </div>

                        <div class="form-options">
                            <label class="checkbox-label">
                                <input v-model="rememberMe" type="checkbox" class="checkbox">
                                <span class="checkmark"></span>
                                记住我
                            </label>
                            <a href="#" class="forgot-link" @click="handleForgotPassword">忘记密码？</a>
                        </div>

                        <button type="submit" class="auth-button" :disabled="loading">
                            <span v-if="loading" class="loading-spinner"></span>
                            {{ loading ? '登录中...' : '登录' }}
                        </button>
                    </form>

                    <!-- 底部信息 -->
                    <div class="auth-footer">
                        <p class="register-hint">未注册的账号在注册后将自动开通账号。</p>
                        <div class="footer-links">
                            <a href="#" @click="$emit('setPage', 'register')" class="link">立即注册</a>
                            <span class="divider">|</span>
                            <a href="#" class="link">服务条例</a>
                            <span class="divider">|</span>
                            <a href="#" class="link">隐私声明</a>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Toast提示 -->
            <div v-if="toast.show" class="toast" :class="toast.type">
                {{ toast.message }}
            </div>
        </div>
    `,
    data() {
        return {
            username: '',
            password: '',
            showPassword: false,
            rememberMe: false,
            loading: false,
            usernameError: '',
            passwordError: '',
            usernameFocused: false,
            passwordFocused: false,
            toast: {
                show: false,
                message: '',
                type: 'error'
            }
        };
    },
    methods: {
        clearErrors() {
            this.usernameError = '';
            this.passwordError = '';
        },
        validateForm() {
            this.clearErrors();
            let isValid = true;

            if (!this.username.trim()) {
                this.usernameError = '请输入用户名';
                isValid = false;
            }

            if (!this.password.trim()) {
                this.passwordError = '请输入密码';
                isValid = false;
            }

            return isValid;
        },
        handleLogin() {
            if (!this.validateForm()) {
                return;
            }

            this.loading = true;
            this.clearErrors();

            axios.post('http://localhost:5000/api/user/login', {
                username: this.username.trim(),
                password: this.password
            }).then(response => {
                this.loading = false;
                this.showToast('登录成功！', 'success');
                setTimeout(() => {
                    this.$emit('login', response.data.user, response.data.token);
                }, 1000);
            }).catch(error => {
                this.loading = false;
                const message = error.response?.data?.message || '登录失败，请重试';
                this.showToast(message, 'error');
            });
        },
        handleForgotPassword() {
            this.showToast('忘记密码功能开发中...', 'info');
        },
        showToast(message, type = 'error') {
            this.toast = { show: true, message, type };
            setTimeout(() => {
                this.toast.show = false;
            }, 3000);
        }
    }
};

// Register Component - 深色主题注册页面
const Register = {
    template: `
        <div class="auth-page">
            <!-- 全屏深色背景 -->
            <div class="auth-background">
                <div class="tech-grid"></div>
                <div class="glow-effect"></div>
            </div>

            <!-- 顶部Logo区域 -->
            <div class="auth-header">
                <div class="logo-section">
                    <div class="logo-icon">🤖</div>
                    <div class="logo-text">AI AGENT FORUM</div>
                </div>
            </div>

            <!-- 核心注册卡片 -->
            <div class="auth-container">
                <div class="auth-card">
                    <!-- 注册方式切换栏 -->
                    <div class="auth-tabs">
                        <div class="tab active">账号注册</div>
                    </div>

                    <!-- 注册表单 -->
                    <form @submit.prevent="handleRegister" class="auth-form">
                        <div class="form-group">
                            <div class="input-wrapper">
                                <input
                                    v-model="username"
                                    type="text"
                                    placeholder="请输入用户名"
                                    class="auth-input"
                                    :class="{ 'error': usernameError }"
                                    @focus="clearErrors"
                                    required
                                >
                                <div class="input-line" :class="{ 'focused': usernameFocused }"></div>
                            </div>
                            <div v-if="usernameError" class="field-error">{{ usernameError }}</div>
                        </div>

                        <div class="form-group">
                            <div class="input-wrapper">
                                <input
                                    v-model="email"
                                    type="email"
                                    placeholder="请输入邮箱"
                                    class="auth-input"
                                    :class="{ 'error': emailError }"
                                    @focus="clearErrors"
                                    required
                                >
                                <div class="input-line" :class="{ 'focused': emailFocused }"></div>
                            </div>
                            <div v-if="emailError" class="field-error">{{ emailError }}</div>
                        </div>

                        <div class="form-group">
                            <div class="input-wrapper">
                                <input
                                    v-model="password"
                                    :type="showPassword ? 'text' : 'password'"
                                    placeholder="请输入密码"
                                    class="auth-input"
                                    :class="{ 'error': passwordError }"
                                    @focus="clearErrors"
                                    required
                                >
                                <button
                                    type="button"
                                    class="password-toggle"
                                    @click="showPassword = !showPassword"
                                >
                                    {{ showPassword ? '🙈' : '👁️' }}
                                </button>
                                <div class="input-line" :class="{ 'focused': passwordFocused }"></div>
                            </div>
                            <div v-if="passwordError" class="field-error">{{ passwordError }}</div>
                        </div>

                        <div class="form-group">
                            <div class="input-wrapper">
                                <input
                                    v-model="confirmPassword"
                                    :type="showConfirmPassword ? 'text' : 'password'"
                                    placeholder="请确认密码"
                                    class="auth-input"
                                    :class="{ 'error': confirmPasswordError }"
                                    @focus="clearErrors"
                                    required
                                >
                                <button
                                    type="button"
                                    class="password-toggle"
                                    @click="showConfirmPassword = !showConfirmPassword"
                                >
                                    {{ showConfirmPassword ? '🙈' : '👁️' }}
                                </button>
                                <div class="input-line" :class="{ 'focused': confirmPasswordFocused }"></div>
                            </div>
                            <div v-if="confirmPasswordError" class="field-error">{{ confirmPasswordError }}</div>
                        </div>

                        <button type="submit" class="auth-button" :disabled="loading">
                            <span v-if="loading" class="loading-spinner"></span>
                            {{ loading ? '注册中...' : '注册' }}
                        </button>
                    </form>

                    <!-- 底部信息 -->
                    <div class="auth-footer">
                        <p class="register-hint">注册即表示您同意我们的服务条款。</p>
                        <div class="footer-links">
                            <a href="#" @click="$emit('setPage', 'login')" class="link">已有账号？立即登录</a>
                            <span class="divider">|</span>
                            <a href="#" class="link">服务条例</a>
                            <span class="divider">|</span>
                            <a href="#" class="link">隐私声明</a>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Toast提示 -->
            <div v-if="toast.show" class="toast" :class="toast.type">
                {{ toast.message }}
            </div>
        </div>
    `,
    data() {
        return {
            username: '',
            email: '',
            password: '',
            confirmPassword: '',
            showPassword: false,
            showConfirmPassword: false,
            loading: false,
            usernameError: '',
            emailError: '',
            passwordError: '',
            confirmPasswordError: '',
            usernameFocused: false,
            emailFocused: false,
            passwordFocused: false,
            confirmPasswordFocused: false,
            toast: {
                show: false,
                message: '',
                type: 'error'
            }
        };
    },
    methods: {
        clearErrors() {
            this.usernameError = '';
            this.emailError = '';
            this.passwordError = '';
            this.confirmPasswordError = '';
        },
        validateForm() {
            this.clearErrors();
            let isValid = true;

            if (!this.username.trim()) {
                this.usernameError = '请输入用户名';
                isValid = false;
            } else if (this.username.length < 3) {
                this.usernameError = '用户名至少3个字符';
                isValid = false;
            }

            if (!this.email.trim()) {
                this.emailError = '请输入邮箱';
                isValid = false;
            } else if (!this.isValidEmail(this.email)) {
                this.emailError = '请输入有效的邮箱地址';
                isValid = false;
            }

            if (!this.password.trim()) {
                this.passwordError = '请输入密码';
                isValid = false;
            } else if (this.password.length < 6) {
                this.passwordError = '密码至少6个字符';
                isValid = false;
            }

            if (!this.confirmPassword.trim()) {
                this.confirmPasswordError = '请确认密码';
                isValid = false;
            } else if (this.password !== this.confirmPassword) {
                this.confirmPasswordError = '两次输入的密码不一致';
                isValid = false;
            }

            return isValid;
        },
        isValidEmail(email) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return emailRegex.test(email);
        },
        handleRegister() {
            if (!this.validateForm()) {
                return;
            }

            this.loading = true;
            this.clearErrors();

            axios.post('http://localhost:5000/api/user/register', {
                username: this.username.trim(),
                email: this.email.trim(),
                password: this.password
            }).then(() => {
                this.loading = false;
                this.showToast('注册成功！正在跳转到登录页面...', 'success');
                setTimeout(() => {
                    this.$emit('register');
                }, 2000);
            }).catch(error => {
                this.loading = false;
                const message = error.response?.data?.message || '注册失败，请重试';
                this.showToast(message, 'error');
            });
        },
        showToast(message, type = 'error') {
            this.toast = { show: true, message, type };
            setTimeout(() => {
                this.toast.show = false;
            }, 3000);
        }
    }
};

// AddPost Component
const AddPost = {
    template: `
        <div>
            <div class="page-header">
                <h2>✏️ 发布新帖</h2>
                <p>分享你的AI Agent经验和见解</p>
            </div>

            <form @submit.prevent="addPost" class="post-form">
                <div class="form-group">
                    <label for="title">标题</label>
                    <input v-model="title" id="title" placeholder="请输入帖子标题" required>
                </div>

                <div class="form-group">
                    <label for="category">分类</label>
                    <select v-model="category" id="category" required>
                        <option value="">选择分类</option>
                        <option value="Agent构建">Agent构建</option>
                        <option value="Prompt工程">Prompt工程</option>
                        <option value="RAG">RAG</option>
                        <option value="智能体实战">智能体实战</option>
                        <option value="AI工具">AI工具</option>
                        <option value="踩坑分享">踩坑分享</option>
                        <option value="技术讨论">技术讨论</option>
                        <option value="问答">问答</option>
                        <option value="其他">其他</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="content">内容</label>
                    <textarea v-model="content" id="content" placeholder="详细描述你的内容..." required></textarea>
                </div>

                <div class="form-group">
                    <label for="code">代码（可选）</label>
                    <textarea v-model="code" id="code" placeholder="粘贴相关代码片段..."></textarea>
                </div>

                <div class="form-group">
                    <label for="image">图片（可选）</label>
                    <input type="file" id="image" @change="handleImage" accept="image/*">
                    <div v-if="imagePreview" class="image-preview">
                        <img :src="imagePreview" alt="预览">
                    </div>
                </div>

                <div class="form-group">
                    <label class="checkbox-label">
                        <input type="checkbox" v-model="isAnonymous">
                        匿名发布
                    </label>
                </div>

                <div class="form-actions">
                    <button type="submit" :disabled="loading" class="submit-btn">
                        {{ loading ? '发布中...' : '发布帖子' }}
                    </button>
                    <button type="button" @click="$emit('setPage', 'home')" class="cancel-btn">取消</button>
                </div>
            </form>

            <div v-if="error" class="error message-box">{{ error }}</div>
            <div v-if="success" class="success message-box">{{ success }}</div>
        </div>
    `,
    data() {
        return {
            title: '',
            category: '',
            content: '',
            code: '',
            image: '',
            imagePreview: '',
            isAnonymous: false,
            error: '',
            success: '',
            loading: false
        };
    },
    props: ['token'],
    methods: {
        handleImage(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = () => {
                    this.image = reader.result;
                    this.imagePreview = reader.result;
                };
                reader.readAsDataURL(file);
            }
        },
        addPost() {
            if (!this.title.trim() || !this.category || !this.content.trim()) {
                this.error = '请填写所有必填字段';
                return;
            }

            this.loading = true;
            this.error = '';
            this.success = '';

            axios.post('http://localhost:5000/api/post/add', {
                title: this.title.trim(),
                category: this.category,
                content: this.content.trim(),
                code: this.code.trim(),
                image: this.image,
                is_anonymous: this.isAnonymous
            }, {
                headers: { Authorization: this.token }
            }).then(() => {
                this.success = '发布成功！正在等待管理员审核...';
                this.clearForm();
                setTimeout(() => {
                    this.$emit('setPage', 'home');
                }, 2000);
            }).catch(error => {
                this.error = error.response?.data?.message || '发布失败，请重试';
                this.loading = false;
            });
        },
        clearForm() {
            this.title = '';
            this.category = '';
            this.content = '';
            this.code = '';
            this.image = '';
            this.imagePreview = '';
            this.isAnonymous = false;
            this.loading = false;
        }
    }
};

// PostDetail Component
const PostDetail = {
    template: `
        <div>
            <h2>{{ post.title }}</h2>
            <p>{{ post.content }}</p>
            <pre v-if="post.code">{{ post.code }}</pre>
            <img v-if="post.image" :src="post.image" alt="截图">
            <p>分类: {{ post.category }} | 作者: {{ post.author }}</p>
            <button @click="toggleLike">{{ liked ? '取消点赞' : '点赞' }} ({{ post.likes }})</button>
            <button @click="toggleFavorite">{{ favorited ? '取消收藏' : '收藏' }}</button>
            <h3>评论</h3>
            <div v-for="comment in post.comments" :key="comment.id" class="comment">
                <p>{{ comment.content }}</p>
                <p>作者: {{ comment.author }}</p>
                <button @click="showReply(comment.id)">回复</button>
                <div v-if="replyingTo === comment.id">
                    <textarea v-model="replyContent"></textarea>
                    <button @click="addReply(comment.id)">提交回复</button>
                </div>
                <div v-for="reply in comment.replies" :key="reply.id" class="comment">
                    <p>{{ reply.content }}</p>
                    <p>作者: {{ reply.author }}</p>
                </div>
            </div>
            <textarea v-model="newComment" placeholder="添加评论"></textarea>
            <button @click="addComment">提交评论</button>
        </div>
    `,
    data() {
        return {
            post: {},
            liked: false,
            favorited: false,
            newComment: '',
            replyingTo: null,
            replyContent: ''
        };
    },
    props: ['user', 'token', 'postId'],
    methods: {
        loadPost() {
            if (!this.postId) return;
            axios.get(`http://localhost:5000/api/post/detail/${this.postId}`).then(response => {
                this.post = response.data;
                this.checkLike();
                this.checkFavorite();
            });
        },
        checkLike() {
            // Assume API to check if liked
            // For simplicity, not implemented
        },
        checkFavorite() {
            // Similar
        },
        toggleLike() {
            axios.post('http://localhost:5000/api/like', { post_id: this.postId }, {
                headers: { Authorization: this.token }
            }).then(() => {
                this.liked = !this.liked;
                this.post.likes += this.liked ? 1 : -1;
            });
        },
        toggleFavorite() {
            axios.post('http://localhost:5000/api/favorite', { post_id: this.postId }, {
                headers: { Authorization: this.token }
            }).then(() => {
                this.favorited = !this.favorited;
            });
        },
        addComment() {
            axios.post('http://localhost:5000/api/comment/add', {
                content: this.newComment,
                post_id: this.postId
            }, {
                headers: { Authorization: this.token }
            }).then(() => {
                this.newComment = '';
                this.loadPost();
            });
        },
        showReply(commentId) {
            this.replyingTo = commentId;
        },
        addReply(commentId) {
            axios.post('http://localhost:5000/api/reply/add', {
                content: this.replyContent,
                post_id: this.postId,
                parent_id: commentId
            }, {
                headers: { Authorization: this.token }
            }).then(() => {
                this.replyContent = '';
                this.replyingTo = null;
                this.loadPost();
            });
        }
    },
    mounted() {
        this.loadPost();
    }
};

// Profile Component
const Profile = {
    template: `
        <div>
            <h2>个人中心</h2>
            <p>用户名: {{ user.username }}</p>
            <p>邮箱: {{ user.email }}</p>
            <h3>我的帖子</h3>
            <div v-for="post in myPosts" :key="post.id" class="post">
                <h4>{{ post.title }}</h4>
                <p>{{ post.content }}</p>
            </div>
            <h3>我的收藏</h3>
            <div v-for="fav in favorites" :key="fav.id" class="post">
                <h4>{{ fav.title }}</h4>
                <p>{{ fav.content }}</p>
            </div>
        </div>
    `,
    data() {
        return {
            myPosts: [],
            favorites: []
        };
    },
    props: ['user', 'token'],
    methods: {
        loadData() {
            // Load my posts - need API, for simplicity, skip
            axios.get('http://localhost:5000/api/favorite/list', {
                headers: { Authorization: this.token }
            }).then(response => {
                this.favorites = response.data.favorites;
            });
        }
    },
    mounted() {
        this.loadData();
    }
};

// Admin Component
const Admin = {
    template: `
        <div>
            <h2>管理员页面</h2>
            <h3>待审核帖子</h3>
            <div v-for="post in pendingPosts" :key="post.id" class="post">
                <h4>{{ post.title }}</h4>
                <p>{{ post.content }}</p>
                <button @click="auditPost(post.id, 'approved')">通过</button>
                <button @click="auditPost(post.id, 'rejected')">拒绝</button>
            </div>
        </div>
    `,
    data() {
        return {
            pendingPosts: []
        };
    },
    props: ['token'],
    methods: {
        loadPending() {
            axios.get('http://localhost:5000/api/admin/post/wait_audit', {
                headers: { Authorization: this.token }
            }).then(response => {
                this.pendingPosts = response.data.posts;
            });
        },
        auditPost(postId, status) {
            axios.post('http://localhost:5000/api/post/audit', { post_id: postId, status }, {
                headers: { Authorization: this.token }
            }).then(() => {
                this.loadPending();
            });
        }
    },
    mounted() {
        this.loadPending();
    }
};

// Register components
// Moved to app.js