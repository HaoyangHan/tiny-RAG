// TinyRAG Knowledge Base JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeKnowledgeBase();
});

function initializeKnowledgeBase() {
    // Initialize search functionality
    initializeSearch();
    
    // Initialize navigation
    initializeNavigation();
    
    // Initialize animations
    initializeAnimations();
    
    // Add knowledge link functionality
    initializeKnowledgeLinks();
}

// Search functionality
function initializeSearch() {
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.querySelector('.search-btn');
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce(performSearch, 300));
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
    }
    
    if (searchBtn) {
        searchBtn.addEventListener('click', performSearch);
    }
}

// Debounce function for search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Perform search across documentation
function performSearch() {
    const searchInput = document.getElementById('searchInput');
    const query = searchInput.value.toLowerCase().trim();
    
    if (!query) {
        resetSearchResults();
        return;
    }
    
    // Search in current page content
    const searchResults = searchInCurrentPage(query);
    
    // Highlight search results
    highlightSearchResults(searchResults);
    
    // Show search feedback
    showSearchFeedback(query, searchResults.length);
}

// Search in current page content
function searchInCurrentPage(query) {
    const searchableElements = document.querySelectorAll('.content-item, .nav-card');
    const results = [];
    
    searchableElements.forEach((element, index) => {
        const text = element.textContent.toLowerCase();
        if (text.includes(query)) {
            results.push({
                element: element,
                index: index,
                relevance: calculateRelevance(text, query)
            });
        }
    });
    
    return results.sort((a, b) => b.relevance - a.relevance);
}

// Calculate search relevance
function calculateRelevance(text, query) {
    const words = query.split(' ');
    let score = 0;
    
    words.forEach(word => {
        const occurrences = (text.match(new RegExp(word, 'g')) || []).length;
        score += occurrences;
    });
    
    return score;
}

// Highlight search results
function highlightSearchResults(results) {
    // Clear previous highlights
    clearHighlights();
    
    // Hide non-matching elements
    const allElements = document.querySelectorAll('.content-item, .nav-card');
    allElements.forEach(el => {
        el.style.opacity = '0.3';
        el.style.transform = 'scale(0.95)';
    });
    
    // Show and highlight matching elements
    results.forEach(result => {
        const element = result.element;
        element.style.opacity = '1';
        element.style.transform = 'scale(1)';
        element.style.border = '2px solid var(--primary-500)';
        element.style.boxShadow = '0 0 20px rgba(59, 130, 246, 0.3)';
    });
}

// Clear search highlights
function clearHighlights() {
    const allElements = document.querySelectorAll('.content-item, .nav-card');
    allElements.forEach(el => {
        el.style.opacity = '';
        el.style.transform = '';
        el.style.border = '';
        el.style.boxShadow = '';
    });
}

// Reset search results
function resetSearchResults() {
    clearHighlights();
    hideSearchFeedback();
}

// Show search feedback
function showSearchFeedback(query, count) {
    let feedbackEl = document.getElementById('searchFeedback');
    
    if (!feedbackEl) {
        feedbackEl = document.createElement('div');
        feedbackEl.id = 'searchFeedback';
        feedbackEl.className = 'search-feedback';
        document.querySelector('.hero').appendChild(feedbackEl);
    }
    
    feedbackEl.innerHTML = `
        <p>Found ${count} result${count !== 1 ? 's' : ''} for "${query}"</p>
        <button onclick="resetSearchResults()" class="clear-search">Clear</button>
    `;
    feedbackEl.style.display = 'block';
}

// Hide search feedback
function hideSearchFeedback() {
    const feedbackEl = document.getElementById('searchFeedback');
    if (feedbackEl) {
        feedbackEl.style.display = 'none';
    }
}

// Navigation functionality
function initializeNavigation() {
    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add active section highlighting
    window.addEventListener('scroll', updateActiveSection);
}

// Update active section based on scroll position
function updateActiveSection() {
    const sections = document.querySelectorAll('.content-section');
    const navLinks = document.querySelectorAll('.nav-links a[href^="#"]');
    
    let currentSection = '';
    
    sections.forEach(section => {
        const rect = section.getBoundingClientRect();
        if (rect.top <= 100 && rect.bottom >= 100) {
            currentSection = section.id;
        }
    });
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${currentSection}`) {
            link.classList.add('active');
        }
    });
}

// Initialize animations
function initializeAnimations() {
    // Intersection Observer for fade-in animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    const animatedElements = document.querySelectorAll('.nav-card, .content-item');
    animatedElements.forEach(el => observer.observe(el));
}

// Navigation functions
function navigateTo(url) {
    // Check if it's an external link or internal page
    if (url.startsWith('http')) {
        window.open(url, '_blank');
    } else {
        window.location.href = url;
    }
}

// Knowledge link functionality for UI integration
function initializeKnowledgeLinks() {
    // This would be used when integrating with the main UI
    window.TinyRAGKnowledge = {
        openModal: function(topic) {
            createKnowledgeModal(topic);
        },
        
        getTopicContent: function(topic) {
            return fetch(`guides/${topic}.html`)
                .then(response => response.text())
                .catch(() => `Content for ${topic} not found.`);
        }
    };
}

// Create knowledge modal for UI integration
function createKnowledgeModal(topic) {
    const modal = document.createElement('div');
    modal.className = 'knowledge-modal';
    modal.innerHTML = `
        <div class="modal-overlay" onclick="closeKnowledgeModal()"></div>
        <div class="modal-content">
            <div class="modal-header">
                <h3>📚 ${formatTopicTitle(topic)}</h3>
                <button onclick="closeKnowledgeModal()" class="modal-close">×</button>
            </div>
            <div class="modal-body">
                <div class="loading">Loading content...</div>
            </div>
            <div class="modal-footer">
                <a href="${topic}.html" target="_blank" class="btn-primary">
                    View Full Documentation
                </a>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Load content
    window.TinyRAGKnowledge.getTopicContent(topic).then(content => {
        const bodyEl = modal.querySelector('.modal-body');
        bodyEl.innerHTML = content;
    });
    
    // Add modal styles if not present
    addModalStyles();
}

// Close knowledge modal
function closeKnowledgeModal() {
    const modal = document.querySelector('.knowledge-modal');
    if (modal) {
        modal.remove();
    }
}

// Format topic title
function formatTopicTitle(topic) {
    return topic
        .replace(/-/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase());
}

// Add modal styles
function addModalStyles() {
    if (document.getElementById('modalStyles')) return;
    
    const styles = document.createElement('style');
    styles.id = 'modalStyles';
    styles.textContent = `
        .knowledge-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .modal-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(4px);
        }
        
        .modal-content {
            position: relative;
            background: white;
            border-radius: 12px;
            max-width: 800px;
            max-height: 80vh;
            width: 90%;
            display: flex;
            flex-direction: column;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
        }
        
        .modal-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 24px;
            border-bottom: 1px solid #e5e7eb;
        }
        
        .modal-close {
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
            color: #6b7280;
            transition: color 0.15s;
        }
        
        .modal-close:hover {
            color: #374151;
        }
        
        .modal-body {
            flex: 1;
            padding: 24px;
            overflow-y: auto;
        }
        
        .modal-footer {
            padding: 24px;
            border-top: 1px solid #e5e7eb;
            text-align: right;
        }
        
        .loading {
            text-align: center;
            color: #6b7280;
            padding: 40px;
        }
    `;
    
    document.head.appendChild(styles);
}

// Copy to clipboard functionality
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!', 'success');
    }).catch(() => {
        showNotification('Failed to copy', 'error');
    });
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--${type === 'success' ? 'success' : type === 'error' ? 'error' : 'primary-600'});
        color: white;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 500;
        box-shadow: var(--shadow-lg);
        z-index: 1000;
        animation: slideInRight 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease-in';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add notification animations
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .search-feedback {
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid var(--gray-200);
        border-radius: 8px;
        padding: 16px;
        margin-top: 20px;
        display: none;
        backdrop-filter: blur(10px);
    }
    
    .search-feedback p {
        margin: 0 0 10px 0;
        color: var(--gray-700);
    }
    
    .clear-search {
        background: var(--primary-600);
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
    }
    
    .nav-links a.active {
        color: var(--primary-600);
        font-weight: 600;
    }
    
    .animate-in {
        animation: fadeInUp 0.6s ease-out;
    }
`;

document.head.appendChild(notificationStyles); 