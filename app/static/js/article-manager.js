/**
 * Article Manager
 * Handles article listing, filtering, selection, and actions
 */

const ArticleManager = {
    articles: [],
    filteredArticles: [],
    selectedIds: new Set(),
    currentView: 'grid',
    sortBy: 'rank',

    // DOM elements
    container: null,
    selectionBar: null,

    /**
     * Initialize the article manager
     */
    init(containerId = 'articles-container') {
        this.container = document.getElementById(containerId);
        this.createSelectionBar();

        // Initialize filter toolbar callback
        if (window.FilterToolbar) {
            FilterToolbar.init((filters, view) => {
                this.currentView = view;
                this.applyFilters(filters);
            });
        }

        return this;
    },

    /**
     * Load articles from API
     */
    async load(params = {}) {
        try {
            LoadingSpinner.show('Loading articles...');

            const response = await API.articles.list(params);
            this.articles = response.data || response.articles || [];
            this.filteredArticles = [...this.articles];

            this.render();
            this.updateStats();

            LoadingSpinner.hide();
        } catch (error) {
            LoadingSpinner.hide();
            Toast.error('Error', 'Failed to load articles: ' + error.message);
        }
    },

    /**
     * Apply filters to articles
     */
    applyFilters(filters) {
        this.filteredArticles = this.articles.filter(article => {
            // Search filter
            if (filters.search) {
                const search = filters.search.toLowerCase();
                const matchesSearch =
                    article.title?.toLowerCase().includes(search) ||
                    article.content?.toLowerCase().includes(search) ||
                    article.source?.name?.toLowerCase().includes(search);
                if (!matchesSearch) return false;
            }

            // Category filter
            if (filters.category && article.category !== filters.category) {
                return false;
            }

            // Source filter
            if (filters.source && article.source?.name !== filters.source) {
                return false;
            }

            // Date filter
            if (filters.date) {
                const articleDate = new Date(article.scraped_at);
                const now = new Date();
                const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

                switch (filters.date) {
                    case 'today':
                        if (articleDate < today) return false;
                        break;
                    case 'yesterday':
                        const yesterday = new Date(today - 86400000);
                        if (articleDate < yesterday || articleDate >= today) return false;
                        break;
                    case 'week':
                        const weekAgo = new Date(today - 7 * 86400000);
                        if (articleDate < weekAgo) return false;
                        break;
                    case 'month':
                        const monthAgo = new Date(today - 30 * 86400000);
                        if (articleDate < monthAgo) return false;
                        break;
                }
            }

            return true;
        });

        // Apply sorting
        this.sortArticles(filters.sort || this.sortBy);
        this.render();
    },

    /**
     * Sort articles
     */
    sortArticles(sortBy) {
        this.sortBy = sortBy;

        this.filteredArticles.sort((a, b) => {
            switch (sortBy) {
                case 'rank':
                    return (b.rank_score || 0) - (a.rank_score || 0);
                case 'newest':
                    return new Date(b.scraped_at) - new Date(a.scraped_at);
                case 'oldest':
                    return new Date(a.scraped_at) - new Date(b.scraped_at);
                case 'title':
                    return a.title.localeCompare(b.title);
                default:
                    return 0;
            }
        });
    },

    /**
     * Render articles
     */
    render() {
        if (!this.container) return;

        if (this.filteredArticles.length === 0) {
            this.container.innerHTML = `
                <div class="no-articles">
                    <i class="bi bi-newspaper"></i>
                    <h4>No articles found</h4>
                    <p>Try adjusting your filters or scrape new articles.</p>
                </div>
            `;
            return;
        }

        const isGrid = this.currentView === 'grid';
        this.container.className = isGrid ? 'articles-grid' : 'articles-list';

        this.container.innerHTML = this.filteredArticles.map(article =>
            this.renderArticleCard(article, isGrid)
        ).join('');

        // Update selection states
        this.updateSelectionUI();
    },

    /**
     * Render single article card
     */
    renderArticleCard(article, isGrid = true) {
        const isSelected = this.selectedIds.has(article.id);
        const image = article.generated_image_url || article.image_url;
        const timeAgo = this.formatTimeAgo(article.scraped_at);

        if (isGrid) {
            return `
                <div class="article-card ${isSelected ? 'selected' : ''}"
                     data-article-id="${article.id}">
                    <div class="article-card-select">
                        <input type="checkbox"
                               ${isSelected ? 'checked' : ''}
                               onchange="ArticleManager.toggleSelect('${article.id}')">
                    </div>
                    ${image ? `
                        <div class="article-card-image">
                            <img src="${image}" alt="${article.title}" loading="lazy">
                        </div>
                    ` : ''}
                    <div class="article-card-content">
                        <div class="article-card-meta">
                            ${article.category ? `<span class="badge">${article.category}</span>` : ''}
                            <span>${article.source?.name || 'Unknown'}</span>
                            <span>${timeAgo}</span>
                        </div>
                        <h3 class="article-card-title">${article.title}</h3>
                        <div class="article-card-actions">
                            <button class="btn btn-sm btn-outline-primary"
                                    onclick="ArticleManager.preview('${article.id}')">
                                <i class="bi bi-eye"></i> Preview
                            </button>
                            <button class="btn btn-sm btn-outline-success"
                                    onclick="ArticleManager.toggleSelect('${article.id}')">
                                <i class="bi bi-${isSelected ? 'check-square' : 'square'}"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `;
        } else {
            return `
                <div class="article-list-item ${isSelected ? 'selected' : ''}"
                     data-article-id="${article.id}">
                    <input type="checkbox"
                           ${isSelected ? 'checked' : ''}
                           onchange="ArticleManager.toggleSelect('${article.id}')">
                    ${image ? `<img src="${image}" alt="" class="article-list-thumb">` : ''}
                    <div class="article-list-content">
                        <h4>${article.title}</h4>
                        <div class="article-list-meta">
                            ${article.category ? `<span class="badge">${article.category}</span>` : ''}
                            <span>${article.source?.name}</span>
                            <span>${timeAgo}</span>
                            ${article.rank_score ? `<span class="score">${Math.round(article.rank_score * 100)}%</span>` : ''}
                        </div>
                    </div>
                    <div class="article-list-actions">
                        <button class="btn btn-sm btn-outline-primary" onclick="ArticleManager.preview('${article.id}')">
                            <i class="bi bi-eye"></i>
                        </button>
                    </div>
                </div>
            `;
        }
    },

    /**
     * Toggle article selection
     */
    toggleSelect(id) {
        if (this.selectedIds.has(id)) {
            this.selectedIds.delete(id);
        } else {
            this.selectedIds.add(id);
        }
        this.updateSelectionUI();
    },

    /**
     * Select all visible articles
     */
    selectAll() {
        this.filteredArticles.forEach(a => this.selectedIds.add(a.id));
        this.updateSelectionUI();
        this.render();
    },

    /**
     * Clear selection
     */
    clearSelection() {
        this.selectedIds.clear();
        this.updateSelectionUI();
        this.render();
    },

    /**
     * Update selection UI
     */
    updateSelectionUI() {
        const count = this.selectedIds.size;

        if (this.selectionBar) {
            this.selectionBar.style.display = count > 0 ? 'flex' : 'none';
            this.selectionBar.querySelector('.selection-count').textContent =
                `${count} article${count !== 1 ? 's' : ''} selected`;
        }

        // Update card states
        document.querySelectorAll('.article-card, .article-list-item').forEach(el => {
            const id = el.dataset.articleId;
            el.classList.toggle('selected', this.selectedIds.has(id));
        });
    },

    /**
     * Create selection action bar
     */
    createSelectionBar() {
        this.selectionBar = document.createElement('div');
        this.selectionBar.className = 'selection-bar';
        this.selectionBar.style.display = 'none';
        this.selectionBar.innerHTML = `
            <span class="selection-count">0 articles selected</span>
            <div class="selection-actions">
                <button class="btn btn-primary btn-sm" onclick="ArticleManager.publishSelected()">
                    <i class="bi bi-send"></i> Publish Selected
                </button>
                <button class="btn btn-outline-primary btn-sm" onclick="ArticleManager.enhanceSelected()">
                    <i class="bi bi-magic"></i> Enhance with AI
                </button>
                <button class="btn btn-outline-danger btn-sm" onclick="ArticleManager.deleteSelected()">
                    <i class="bi bi-trash"></i> Delete
                </button>
                <button class="btn btn-link btn-sm" onclick="ArticleManager.clearSelection()">
                    Clear Selection
                </button>
            </div>
        `;
        document.body.appendChild(this.selectionBar);
    },

    /**
     * Preview article
     */
    preview(id) {
        const article = this.articles.find(a => a.id === id);
        if (article && window.Modal) {
            Modal.articlePreview(article);
        }
    },

    /**
     * Publish selected articles
     */
    async publishSelected() {
        if (this.selectedIds.size === 0) {
            Toast.warning('No Selection', 'Please select articles to publish.');
            return;
        }

        Modal.confirm(
            'Publish Articles',
            `Are you sure you want to publish ${this.selectedIds.size} article(s)?`,
            async () => {
                LoadingSpinner.show('Publishing articles...', true);

                let published = 0;
                const total = this.selectedIds.size;

                for (const id of this.selectedIds) {
                    try {
                        await API.wordpress.publish(id);
                        published++;
                        LoadingSpinner.setProgress((published / total) * 100);
                    } catch (error) {
                        console.error(`Failed to publish ${id}:`, error);
                    }
                }

                LoadingSpinner.hide();
                Toast.success('Published', `Successfully published ${published} of ${total} articles.`);
                this.clearSelection();
                this.load();
            }
        );
    },

    /**
     * Delete selected articles
     */
    async deleteSelected() {
        if (this.selectedIds.size === 0) return;

        Modal.danger(
            'Delete Articles',
            `Are you sure you want to delete ${this.selectedIds.size} article(s)? This cannot be undone.`,
            async () => {
                LoadingSpinner.show('Deleting articles...');

                for (const id of this.selectedIds) {
                    try {
                        await API.articles.delete(id);
                    } catch (error) {
                        console.error(`Failed to delete ${id}:`, error);
                    }
                }

                LoadingSpinner.hide();
                Toast.success('Deleted', 'Articles have been deleted.');
                this.clearSelection();
                this.load();
            }
        );
    },

    /**
     * Format time ago
     */
    formatTimeAgo(dateStr) {
        if (!dateStr) return 'Unknown';

        const date = new Date(dateStr);
        const now = new Date();
        const diff = (now - date) / 1000;

        if (diff < 60) return 'Just now';
        if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
        if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
        if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`;
        return date.toLocaleDateString();
    },

    /**
     * Update dashboard stats
     */
    updateStats() {
        const stats = {
            total: this.articles.length,
            filtered: this.filteredArticles.length,
            selected: this.selectedIds.size
        };

        // Update any stats displays
        const statsEl = document.getElementById('articles-stats');
        if (statsEl) {
            statsEl.textContent = `Showing ${stats.filtered} of ${stats.total} articles`;
        }
    }
};

// Make globally available
window.ArticleManager = ArticleManager;
