// Service Worker for RetirementAdvisorPro Admin
// Provides offline capabilities and caching

const CACHE_NAME = 'rap-admin-v1.0.0';
const STATIC_CACHE_NAME = 'rap-static-v1.0.0';
const DYNAMIC_CACHE_NAME = 'rap-dynamic-v1.0.0';

// Resources to cache immediately
const STATIC_ASSETS = [
  '/',
  '/admin/dashboard',
  '/assets/css/theme.min.css',
  '/assets/js/theme.min.js',
  '/assets/icons/icon-192x192.png',
  '/assets/icons/icon-512x512.png',
  '/manifest.json'
];

// API endpoints that can be cached
const CACHEABLE_API_PATTERNS = [
  /\/api\/admin\/analytics\/summary/,
  /\/api\/admin\/users\?/,
  /\/api\/admin\/monitoring\?/,
  /\/api\/tax\//,
  /\/api\/clients\?/
];

// Network-first patterns (always try network first)
const NETWORK_FIRST_PATTERNS = [
  /\/api\/admin\/support\//,
  /\/api\/admin\/communication\//,
  /\/api\/auth\//,
  /\/api\/admin\/performance\//
];

// Install event - cache static assets
self.addEventListener('install', event => {
  console.log('Service Worker: Installing...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE_NAME)
      .then(cache => {
        console.log('Service Worker: Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => {
        console.log('Service Worker: Static assets cached');
        return self.skipWaiting();
      })
      .catch(error => {
        console.error('Service Worker: Failed to cache static assets', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('Service Worker: Activating...');
  
  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            // Delete old caches that don't match current version
            if (cacheName !== STATIC_CACHE_NAME && 
                cacheName !== DYNAMIC_CACHE_NAME && 
                cacheName !== CACHE_NAME) {
              console.log('Service Worker: Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('Service Worker: Activated');
        return self.clients.claim();
      })
  );
});

// Fetch event - handle requests with caching strategies
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Handle different types of requests
  if (isStaticAsset(request.url)) {
    event.respondWith(cacheFirst(request, STATIC_CACHE_NAME));
  } else if (isApiRequest(url)) {
    event.respondWith(handleApiRequest(request));
  } else {
    event.respondWith(networkFirst(request, DYNAMIC_CACHE_NAME));
  }
});

// Message event - handle messages from the main thread
self.addEventListener('message', event => {
  const { type, payload } = event.data;
  
  switch (type) {
    case 'SKIP_WAITING':
      self.skipWaiting();
      break;
      
    case 'CACHE_URLS':
      cacheUrls(payload.urls);
      break;
      
    case 'CLEAR_CACHE':
      clearCache(payload.cacheName);
      break;
      
    case 'GET_CACHE_STATS':
      getCacheStats().then(stats => {
        event.ports[0].postMessage({ type: 'CACHE_STATS', payload: stats });
      });
      break;
  }
});

// Background sync for failed requests
self.addEventListener('sync', event => {
  if (event.tag === 'background-sync') {
    console.log('Service Worker: Background sync triggered');
    event.waitUntil(handleBackgroundSync());
  }
});

// Push notification handling
self.addEventListener('push', event => {
  const options = {
    body: event.data ? event.data.text() : 'New admin notification',
    icon: '/assets/icons/icon-192x192.png',
    badge: '/assets/icons/badge-72x72.png',
    data: {
      timestamp: Date.now()
    },
    actions: [
      {
        action: 'open',
        title: 'Open Admin',
        icon: '/assets/icons/open-action.png'
      },
      {
        action: 'dismiss',
        title: 'Dismiss',
        icon: '/assets/icons/dismiss-action.png'
      }
    ],
    tag: 'admin-notification',
    renotify: true
  };
  
  event.waitUntil(
    self.registration.showNotification('RetirementAdvisorPro Admin', options)
  );
});

// Notification click handling
self.addEventListener('notificationclick', event => {
  event.notification.close();
  
  if (event.action === 'open' || !event.action) {
    event.waitUntil(
      clients.openWindow('/admin/dashboard')
    );
  }
});

// Helper functions

function isStaticAsset(url) {
  return url.includes('/assets/') || 
         url.includes('/manifest.json') || 
         url.includes('/favicon.ico');
}

function isApiRequest(url) {
  return url.pathname.startsWith('/api/');
}

function isNetworkFirst(url) {
  return NETWORK_FIRST_PATTERNS.some(pattern => pattern.test(url));
}

function isCacheableApi(url) {
  return CACHEABLE_API_PATTERNS.some(pattern => pattern.test(url));
}

// Cache-first strategy
async function cacheFirst(request, cacheName) {
  try {
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      // Update cache in background
      updateCacheInBackground(request, cache);
      return cachedResponse;
    }
    
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.error('Cache-first strategy failed:', error);
    return new Response('Offline - Resource not available', {
      status: 503,
      statusText: 'Service Unavailable'
    });
  }
}

// Network-first strategy
async function networkFirst(request, cacheName) {
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('Network failed, trying cache:', error);
    
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline page for navigation requests
    if (request.destination === 'document') {
      return caches.match('/offline.html');
    }
    
    return new Response('Offline - Resource not available', {
      status: 503,
      statusText: 'Service Unavailable'
    });
  }
}

// Handle API requests with intelligent caching
async function handleApiRequest(request) {
  const url = new URL(request.url);
  
  // Network-first for critical endpoints
  if (isNetworkFirst(url)) {
    return networkFirst(request, DYNAMIC_CACHE_NAME);
  }
  
  // Cache-first for cacheable APIs with TTL
  if (isCacheableApi(url)) {
    return cacheWithTTL(request, DYNAMIC_CACHE_NAME, 5 * 60 * 1000); // 5 minutes
  }
  
  // Default: network-only for other API requests
  try {
    const response = await fetch(request);
    
    // Queue failed requests for background sync
    if (!response.ok && response.status >= 500) {
      queueFailedRequest(request);
    }
    
    return response;
  } catch (error) {
    queueFailedRequest(request);
    
    return new Response(JSON.stringify({
      error: 'Network unavailable',
      offline: true,
      timestamp: Date.now()
    }), {
      status: 503,
      statusText: 'Service Unavailable',
      headers: {
        'Content-Type': 'application/json'
      }
    });
  }
}

// Cache with TTL (Time To Live)
async function cacheWithTTL(request, cacheName, ttl) {
  try {
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      const cachedTime = new Date(cachedResponse.headers.get('sw-cached-time'));
      const now = new Date();
      
      // Return cached response if within TTL
      if (now.getTime() - cachedTime.getTime() < ttl) {
        return cachedResponse;
      }
    }
    
    // Fetch from network
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      // Clone response and add timestamp header
      const responseClone = networkResponse.clone();
      const headers = new Headers(responseClone.headers);
      headers.set('sw-cached-time', new Date().toISOString());
      
      const cachedResponse = new Response(responseClone.body, {
        status: responseClone.status,
        statusText: responseClone.statusText,
        headers: headers
      });
      
      cache.put(request, cachedResponse);
    }
    
    return networkResponse;
  } catch (error) {
    // Return cached response even if expired
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    throw error;
  }
}

// Update cache in background
async function updateCacheInBackground(request, cache) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      cache.put(request, response);
    }
  } catch (error) {
    console.log('Background cache update failed:', error);
  }
}

// Queue failed requests for background sync
function queueFailedRequest(request) {
  // In a real implementation, you'd store this in IndexedDB
  console.log('Queueing failed request for background sync:', request.url);
}

// Handle background sync
async function handleBackgroundSync() {
  // In a real implementation, you'd retrieve queued requests from IndexedDB
  // and retry them
  console.log('Processing background sync...');
}

// Cache specific URLs
async function cacheUrls(urls) {
  const cache = await caches.open(DYNAMIC_CACHE_NAME);
  
  for (const url of urls) {
    try {
      const response = await fetch(url);
      if (response.ok) {
        cache.put(url, response);
      }
    } catch (error) {
      console.error(`Failed to cache ${url}:`, error);
    }
  }
}

// Clear specific cache
async function clearCache(cacheName) {
  try {
    await caches.delete(cacheName);
    console.log(`Cache ${cacheName} cleared`);
  } catch (error) {
    console.error(`Failed to clear cache ${cacheName}:`, error);
  }
}

// Get cache statistics
async function getCacheStats() {
  const cacheNames = await caches.keys();
  const stats = {};
  
  for (const cacheName of cacheNames) {
    const cache = await caches.open(cacheName);
    const keys = await cache.keys();
    stats[cacheName] = {
      name: cacheName,
      size: keys.length,
      urls: keys.map(key => key.url)
    };
  }
  
  return stats;
}