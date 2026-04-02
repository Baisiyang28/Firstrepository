const { createApp, ref } = Vue;

const app = createApp({
    data() {
        return {
            currentPage: 'home',
            user: null,
            token: null,
            selectedPostId: null,
            globalSearch: '',
            categoryFilter: '',
            activeUsers: []
        };
    },
    methods: {
        setPage(page, postId = null) {
            this.currentPage = page;
            this.selectedPostId = postId;
        },
        handleLogin(user, token) {
            this.user = user;
            this.token = token;
            this.setPage('home');
        },
        handleRegister() {
            this.setPage('login');
        },
        logout() {
            this.user = null;
            this.token = null;
            this.setPage('home');
        },
        checkLogin() {
            // TODO: file:// 下localStorage受限，生产环境可恢复
        },
        handleSearch(searchTerm) {
            this.globalSearch = searchTerm;
            this.setPage('home');
        },
        filterByTag(tag) {
            this.categoryFilter = tag.replace(/^#/, '');
            this.setPage('home');
        },
        setCategory(category) {
            this.categoryFilter = category;
            this.setPage('home');
        },
        searchGlobal() {
            if (this.globalSearch.trim()) {
                this.handleSearch(this.globalSearch);
            }
        },
        loadActiveUsers() {
            axios.get('http://localhost:5000/api/active_users?limit=10').then(response => {
                this.activeUsers = response.data.users || [];
            }).catch(error => {
                console.error('加载活跃用户失败', error);
            });
        }
    },
    mounted() {
        this.checkLogin();
        this.loadActiveUsers();
        const globalSearchInput = document.getElementById('globalSearchInput');
        const globalSearchBtn = document.getElementById('globalSearchBtn');
        if (globalSearchInput) {
            globalSearchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    this.handleSearch(e.target.value);
                }
            });
        }
        if (globalSearchBtn) {
            globalSearchBtn.addEventListener('click', () => {
                this.handleSearch(globalSearchInput ? globalSearchInput.value : '');
            });
        }
    }
});

// Register components after they are loaded
app.component('home', Home);
app.component('login', Login);
app.component('register', Register);
app.component('add-post', AddPost);
app.component('post-detail', PostDetail);
app.component('profile', Profile);
app.component('admin', Admin);

app.component('topics', Topics);
app.component('agent-share', AgentShare);
app.component('tech-discuss', TechDiscuss);
app.component('qa', QA);
app.component('tools', Tools);

app.mount('#app');