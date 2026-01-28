/**
 * API Client for Basement Cowboy
 * Handles all communication with the backend API
 */

const API = {
    baseUrl: '',

    /**
     * Make an API request
     */
    async request(method, endpoint, data = null, options = {}) {
        const url = this.baseUrl + endpoint;

        const fetchOptions = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        };

        if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
            fetchOptions.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, fetchOptions);
            const json = await response.json();

            if (!response.ok) {
                throw new APIError(
                    json.error?.message || 'Request failed',
                    json.error?.code || 'UNKNOWN_ERROR',
                    response.status
                );
            }

            return json;
        } catch (error) {
            if (error instanceof APIError) {
                throw error;
            }
            throw new APIError(error.message, 'NETWORK_ERROR', 0);
        }
    },

    // Convenience methods
    get(endpoint, options = {}) {
        return this.request('GET', endpoint, null, options);
    },

    post(endpoint, data, options = {}) {
        return this.request('POST', endpoint, data, options);
    },

    put(endpoint, data, options = {}) {
        return this.request('PUT', endpoint, data, options);
    },

    delete(endpoint, options = {}) {
        return this.request('DELETE', endpoint, null, options);
    },

    // Article endpoints
    articles: {
        list(params = {}) {
            const query = new URLSearchParams(params).toString();
            return API.get(`/api/articles${query ? '?' + query : ''}`);
        },

        get(id) {
            return API.get(`/api/articles/${id}`);
        },

        delete(id) {
            return API.delete(`/api/articles/${id}`);
        },

        rank(articleIds = null, weights = null) {
            return API.post('/api/rank', { article_ids: articleIds, weights: weights });
        },

        enhance(id, options = {}) {
            return API.post(`/api/enhance/${id}`, options);
        }
    },

    // Scraper endpoints
    scraper: {
        start(sources = null, maxArticles = null) {
            return API.post('/api/scrape', { sources, max_articles: maxArticles });
        },

        status() {
            return API.get('/api/scrape/status');
        },

        sources() {
            return API.get('/api/sources');
        }
    },

    // WordPress endpoints
    wordpress: {
        test() {
            return API.get('/api/wordpress/test');
        },

        publish(articleId, options = {}) {
            return API.post('/api/publish', { article_id: articleId, ...options });
        },

        categories() {
            return API.get('/api/wordpress/categories');
        },

        tags() {
            return API.get('/api/wordpress/tags');
        }
    },

    // Stats endpoints
    stats: {
        dashboard() {
            return API.get('/api/stats');
        },

        costs() {
            return API.get('/api/stats/costs');
        }
    },

    // Config endpoints
    config: {
        get() {
            return API.get('/api/config');
        },

        update(config) {
            return API.post('/api/config', config);
        },

        setApiKey(key) {
            return API.post('/api/config/api-key', { api_key: key });
        }
    }
};

/**
 * Custom API Error class
 */
class APIError extends Error {
    constructor(message, code, status) {
        super(message);
        this.name = 'APIError';
        this.code = code;
        this.status = status;
    }
}

/**
 * API Request Queue for rate limiting
 */
const RequestQueue = {
    queue: [],
    processing: false,
    rateLimit: 100, // ms between requests

    add(request) {
        return new Promise((resolve, reject) => {
            this.queue.push({ request, resolve, reject });
            this.process();
        });
    },

    async process() {
        if (this.processing || this.queue.length === 0) return;

        this.processing = true;

        while (this.queue.length > 0) {
            const { request, resolve, reject } = this.queue.shift();

            try {
                const result = await request();
                resolve(result);
            } catch (error) {
                reject(error);
            }

            if (this.queue.length > 0) {
                await new Promise(r => setTimeout(r, this.rateLimit));
            }
        }

        this.processing = false;
    }
};

// Make globally available
window.API = API;
window.APIError = APIError;
window.RequestQueue = RequestQueue;
