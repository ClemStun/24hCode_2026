const csrfToken = getCookie('csrftoken');
//const csrfToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJjb2RpbmdnYW1lIiwic3ViIjoiMDAyNjQyYzItYmJiMS00OTdkLWFiZTItMDU5ZTA2MGJhNzExIiwicm9sZXMiOlsiVVNFUiJdfQ.bTbRXfHkvrBHYexewru3uX7x3j8L-GfMnXzymkxbU2k';

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';').map(cookie => cookie.trim());
        for (const cookie of cookies) {
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

class Api {
    _requests = { get: {}, post: {}, put: {}, delete: {} };
    _pendingRequests = {};
    get pendingRequests() {
        return { ...this._pendingRequests };
    }

    constructor(baseUrl) {
        this._baseUrl = baseUrl || window.location.origin;
    }

    async get(endpoint, options = {}) {
        if (this._shutdown) {
            return;
        }

        const url = new URL(endpoint, this._baseUrl);
        Object.entries(options.data ?? {}).forEach(([key, value]) => url.searchParams.append(key, value));
        delete options.data;

        const headers = {
            'X-CSRFToken': csrfToken
        };
        if (options.headers) {
            delete options.headers['X-CSRFToken'];
            Object.assign(headers, options.headers);
            delete options.headers;
        }

        this._requests.get[endpoint]?.abort();
        this._requests.get[endpoint] = new AbortController();
        const request = fetch(url, {
            ...options,
            method: 'GET',
            headers: headers,
            signal: this._requests.get[endpoint].signal,
        });

        this._pendingRequests[endpoint] = request;
        const response = await request;
        if (!response.ok) {
            throw new Error(`GET ${endpoint} failed with status ${response.status}`);
        }

        console.log(response.json());
        return await response.json();
    }

    async post(endpoint, options = {}) {
        if (this._shutdown) {
            return;
        }

        const data = options.data ?? {};
        delete options.data;
        const headers = {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        };

        if (options.headers) {
            delete options.headers['Content-Type'];
            delete options.headers['X-CSRFToken'];
            Object.assign(headers, options.headers);
            delete options.headers;
        }

        if (data instanceof FormData) {
            delete headers['Content-Type'];
        }

        this._requests.post[endpoint]?.abort();
        this._requests.post[endpoint] = new AbortController();
        const url = new URL(endpoint, this._baseUrl);
        const request = fetch(url, {
            ...options,
            method: 'POST',
            headers: headers,
            body: data instanceof FormData ? data : JSON.stringify(data),
            signal: this._requests.post[endpoint].signal,
        });

        this._pendingRequests[endpoint] = request;
        const response = await request;
        if (!response.ok) {
            throw new Error(`POST ${endpoint} failed with status ${response.status}`);
        }

        try {
            return await response.json();
        } catch {
            return undefined;
        }
    }

    async put(endpoint, options = {}) {
        if (this._shutdown) {
            return;
        }

        const data = options.data ?? {};
        delete options.data;
        const headers = {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        };

        if (options.headers) {
            delete options.headers['Content-Type'];
            delete options.headers['X-CSRFToken'];
            Object.assign(headers, options.headers);
            delete options.headers;
        }

        if (data instanceof FormData) {
            delete headers['Content-Type'];
        }

        this._requests.put[endpoint]?.abort();
        this._requests.put[endpoint] = new AbortController();
        const url = new URL(endpoint, this._baseUrl);
        const request = fetch(url, {
            ...options,
            method: 'PUT',
            headers: headers,
            body: data instanceof FormData ? data : JSON.stringify(data),
            signal: this._requests.put[endpoint].signal,
        });

        this._pendingRequests[endpoint] = request;
        const response = await request;
        if (!response.ok) {
            throw new Error(`PUT ${endpoint} failed with status ${response.status}`);
        }

        try {
            return await response.json();
        } catch {
            return undefined;
        }
    }

    async delete(endpoint, options = {}) {
        if (this._shutdown) {
            return;
        }

        const headers = {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        };
        if (options.headers) {
            delete options.headers['Content-Type'];
            delete options.headers['X-CSRFToken'];
            Object.assign(headers, options.headers);
            delete options.headers;
        }

        this._requests.delete[endpoint]?.abort();
        this._requests.delete[endpoint] = new AbortController();
        const url = new URL(endpoint, this._baseUrl);
        const request = fetch(url, {
            ...options,
            method: 'DELETE',
            headers: headers,
            signal: this._requests.delete[endpoint].signal
        });

        this._pendingRequests[endpoint] = request;
        const response = await request;
        if (!response.ok) {
            throw new Error(`DELETE ${endpoint} failed with status ${response.status}`);
        }

        try {
            return await response.json();
        } catch {
            return undefined;
        }
    }

    async onShutdown() {
        this._shutdown = true;
        await Promise.all(Object.values(this._pendingRequests));
    }
}

const api = new Api(window.location.origin);
export { api, Api };