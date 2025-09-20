/**
 * Enhanced Accessibility Features for Stock Analysis Tool
 * WCAG 2.1 AA Compliance
 */

class AccessibilityManager {
    constructor() {
        this.isInitialized = false;
        this.currentTheme = 'dark';
        this.fontSize = 16;
        this.highContrast = false;
        this.keyboardNavigation = false;
        this.screenReaderMode = false;
        
        this.init();
    }
    
    init() {
        if (this.isInitialized) return;
        
        this.setupKeyboardNavigation();
        this.setupScreenReaderSupport();
        this.setupThemeToggle();
        this.setupFontSizeControl();
        this.setupHighContrastMode();
        this.setupFocusManagement();
        this.setupARIALabels();
        this.setupSkipLinks();
        
        this.isInitialized = true;
        console.log('Accessibility Manager initialized');
    }
    
    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            // Tab navigation enhancement
            if (e.key === 'Tab') {
                this.keyboardNavigation = true;
                document.body.classList.add('keyboard-navigation');
            }
            
            // Escape key handling
            if (e.key === 'Escape') {
                this.closeAllModals();
                this.clearFocus();
            }
            
            // Arrow key navigation for custom components
            if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                this.handleArrowNavigation(e);
            }
            
            // Enter key handling
            if (e.key === 'Enter' && e.target.classList.contains('netflix-nav-item')) {
                this.activateNavigationItem(e.target);
            }
        });
        
        document.addEventListener('mousedown', () => {
            this.keyboardNavigation = false;
            document.body.classList.remove('keyboard-navigation');
        });
    }
    
    setupScreenReaderSupport() {
        // Add screen reader announcements
        this.announceToScreenReader = (message, priority = 'polite') => {
            const announcement = document.createElement('div');
            announcement.setAttribute('aria-live', priority);
            announcement.setAttribute('aria-atomic', 'true');
            announcement.className = 'sr-only';
            announcement.textContent = message;
            
            document.body.appendChild(announcement);
            
            setTimeout(() => {
                document.body.removeChild(announcement);
            }, 1000);
        };
        
        // Monitor dynamic content changes
        this.observeContentChanges();
    }
    
    setupThemeToggle() {
        // Create theme toggle button
        const themeToggle = document.createElement('button');
        themeToggle.id = 'theme-toggle';
        themeToggle.className = 'accessibility-control';
        themeToggle.setAttribute('aria-label', 'テーマを切り替え');
        themeToggle.innerHTML = '🌙';
        
        themeToggle.addEventListener('click', () => {
            this.toggleTheme();
        });
        
        // Add to page
        this.addAccessibilityControls([themeToggle]);
    }
    
    setupFontSizeControl() {
        // Create font size controls
        const fontSizeContainer = document.createElement('div');
        fontSizeContainer.className = 'font-size-controls';
        fontSizeContainer.innerHTML = `
            <button id="font-decrease" aria-label="フォントサイズを小さく">A-</button>
            <span id="font-size-display">${this.fontSize}px</span>
            <button id="font-increase" aria-label="フォントサイズを大きく">A+</button>
        `;
        
        const decreaseBtn = fontSizeContainer.querySelector('#font-decrease');
        const increaseBtn = fontSizeContainer.querySelector('#font-increase');
        const display = fontSizeContainer.querySelector('#font-size-display');
        
        decreaseBtn.addEventListener('click', () => {
            this.fontSize = Math.max(12, this.fontSize - 2);
            this.updateFontSize();
            display.textContent = `${this.fontSize}px`;
        });
        
        increaseBtn.addEventListener('click', () => {
            this.fontSize = Math.min(24, this.fontSize + 2);
            this.updateFontSize();
            display.textContent = `${this.fontSize}px`;
        });
        
        this.addAccessibilityControls([fontSizeContainer]);
    }
    
    setupHighContrastMode() {
        // Create high contrast toggle
        const contrastToggle = document.createElement('button');
        contrastToggle.id = 'contrast-toggle';
        contrastToggle.className = 'accessibility-control';
        contrastToggle.setAttribute('aria-label', '高コントラストモードを切り替え');
        contrastToggle.innerHTML = '🔍';
        
        contrastToggle.addEventListener('click', () => {
            this.toggleHighContrast();
        });
        
        this.addAccessibilityControls([contrastToggle]);
    }
    
    setupFocusManagement() {
        // Enhanced focus indicators
        const style = document.createElement('style');
        style.textContent = `
            .keyboard-navigation *:focus {
                outline: 3px solid #667eea !important;
                outline-offset: 2px !important;
                box-shadow: 0 0 0 5px rgba(102, 126, 234, 0.3) !important;
            }
            
            .netflix-nav-item:focus {
                background: rgba(102, 126, 234, 0.2) !important;
                border-color: #667eea !important;
            }
            
            .metric-card:focus {
                transform: translateY(-4px) !important;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2) !important;
            }
        `;
        document.head.appendChild(style);
        
        // Focus trap for modals
        this.setupFocusTrap();
    }
    
    setupARIALabels() {
        // Add ARIA labels to interactive elements
        const interactiveElements = document.querySelectorAll(
            '.netflix-nav-item, .metric-card, .stButton button, .stTextInput input, .stSelectbox select'
        );
        
        interactiveElements.forEach((element, index) => {
            if (!element.getAttribute('aria-label') && !element.getAttribute('aria-labelledby')) {
                const label = this.generateARIALabel(element);
                element.setAttribute('aria-label', label);
            }
        });
        
        // Add role attributes
        document.querySelectorAll('.netflix-nav-menu').forEach(menu => {
            menu.setAttribute('role', 'navigation');
            menu.setAttribute('aria-label', 'メインナビゲーション');
        });
        
        document.querySelectorAll('.metric-card').forEach(card => {
            card.setAttribute('role', 'region');
            card.setAttribute('aria-label', 'メトリックカード');
        });
    }
    
    setupSkipLinks() {
        // Create skip links
        const skipLinks = document.createElement('div');
        skipLinks.className = 'skip-links';
        skipLinks.innerHTML = `
            <a href="#main-content" class="skip-link">メインコンテンツにスキップ</a>
            <a href="#navigation" class="skip-link">ナビゲーションにスキップ</a>
            <a href="#sidebar" class="skip-link">サイドバーにスキップ</a>
        `;
        
        const style = document.createElement('style');
        style.textContent = `
            .skip-links {
                position: absolute;
                top: -100px;
                left: 0;
                z-index: 1000;
            }
            
            .skip-link {
                position: absolute;
                top: 0;
                left: 0;
                background: #667eea;
                color: white;
                padding: 8px 16px;
                text-decoration: none;
                border-radius: 4px;
                font-weight: bold;
                transform: translateY(-100px);
                transition: transform 0.3s;
            }
            
            .skip-link:focus {
                transform: translateY(0);
            }
        `;
        document.head.appendChild(style);
        document.body.insertBefore(skipLinks, document.body.firstChild);
    }
    
    addAccessibilityControls(controls) {
        let controlsContainer = document.getElementById('accessibility-controls');
        if (!controlsContainer) {
            controlsContainer = document.createElement('div');
            controlsContainer.id = 'accessibility-controls';
            controlsContainer.className = 'accessibility-controls';
            controlsContainer.setAttribute('role', 'toolbar');
            controlsContainer.setAttribute('aria-label', 'アクセシビリティコントロール');
            
            const style = document.createElement('style');
            style.textContent = `
                .accessibility-controls {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 1000;
                    display: flex;
                    gap: 10px;
                    background: rgba(0, 0, 0, 0.8);
                    padding: 10px;
                    border-radius: 8px;
                    backdrop-filter: blur(10px);
                }
                
                .accessibility-control {
                    background: #667eea;
                    color: white;
                    border: none;
                    padding: 8px 12px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 14px;
                    transition: all 0.3s;
                }
                
                .accessibility-control:hover {
                    background: #5a6fd8;
                    transform: scale(1.05);
                }
                
                .accessibility-control:focus {
                    outline: 3px solid #f093fb;
                    outline-offset: 2px;
                }
                
                .font-size-controls {
                    display: flex;
                    align-items: center;
                    gap: 5px;
                    background: rgba(255, 255, 255, 0.1);
                    padding: 5px;
                    border-radius: 4px;
                }
                
                .font-size-controls button {
                    background: #667eea;
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 3px;
                    cursor: pointer;
                    font-size: 12px;
                }
                
                .font-size-controls span {
                    color: white;
                    font-size: 12px;
                    min-width: 40px;
                    text-align: center;
                }
                
                .sr-only {
                    position: absolute;
                    width: 1px;
                    height: 1px;
                    padding: 0;
                    margin: -1px;
                    overflow: hidden;
                    clip: rect(0, 0, 0, 0);
                    white-space: nowrap;
                    border: 0;
                }
            `;
            document.head.appendChild(style);
            document.body.appendChild(controlsContainer);
        }
        
        controls.forEach(control => {
            controlsContainer.appendChild(control);
        });
    }
    
    toggleTheme() {
        this.currentTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', this.currentTheme);
        
        const toggleBtn = document.getElementById('theme-toggle');
        toggleBtn.innerHTML = this.currentTheme === 'dark' ? '🌙' : '☀️';
        
        this.announceToScreenReader(`テーマを${this.currentTheme === 'dark' ? 'ダーク' : 'ライト'}モードに変更しました`);
        
        // Save preference
        localStorage.setItem('theme', this.currentTheme);
    }
    
    updateFontSize() {
        document.documentElement.style.fontSize = `${this.fontSize}px`;
        
        // Update CSS custom property
        document.documentElement.style.setProperty('--font-size-base', `${this.fontSize}px`);
        
        this.announceToScreenReader(`フォントサイズを${this.fontSize}ピクセルに変更しました`);
        
        // Save preference
        localStorage.setItem('fontSize', this.fontSize);
    }
    
    toggleHighContrast() {
        this.highContrast = !this.highContrast;
        document.body.classList.toggle('high-contrast', this.highContrast);
        
        const contrastBtn = document.getElementById('contrast-toggle');
        contrastBtn.innerHTML = this.highContrast ? '🔍' : '👁️';
        
        this.announceToScreenReader(`高コントラストモードを${this.highContrast ? '有効' : '無効'}にしました`);
        
        // Save preference
        localStorage.setItem('highContrast', this.highContrast);
    }
    
    handleArrowNavigation(e) {
        const currentElement = e.target;
        const parent = currentElement.closest('.netflix-nav-menu');
        
        if (parent) {
            const items = Array.from(parent.querySelectorAll('.netflix-nav-item'));
            const currentIndex = items.indexOf(currentElement);
            
            let nextIndex;
            if (e.key === 'ArrowDown') {
                nextIndex = (currentIndex + 1) % items.length;
            } else {
                nextIndex = (currentIndex - 1 + items.length) % items.length;
            }
            
            items[nextIndex].focus();
            e.preventDefault();
        }
    }
    
    activateNavigationItem(element) {
        const text = element.querySelector('.netflix-nav-text').textContent;
        this.announceToScreenReader(`${text}ページに移動します`);
        
        // Trigger click event
        element.click();
    }
    
    observeContentChanges() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            this.setupARIALabels();
                        }
                    });
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    generateARIALabel(element) {
        const text = element.textContent?.trim();
        const placeholder = element.getAttribute('placeholder');
        const title = element.getAttribute('title');
        
        return text || placeholder || title || 'インタラクティブ要素';
    }
    
    setupFocusTrap() {
        this.trapFocus = (container) => {
            const focusableElements = container.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            
            const firstElement = focusableElements[0];
            const lastElement = focusableElements[focusableElements.length - 1];
            
            container.addEventListener('keydown', (e) => {
                if (e.key === 'Tab') {
                    if (e.shiftKey) {
                        if (document.activeElement === firstElement) {
                            lastElement.focus();
                            e.preventDefault();
                        }
                    } else {
                        if (document.activeElement === lastElement) {
                            firstElement.focus();
                            e.preventDefault();
                        }
                    }
                }
            });
        };
    }
    
    closeAllModals() {
        // Close any open modals or dropdowns
        const modals = document.querySelectorAll('.modal, .dropdown, .popup');
        modals.forEach(modal => {
            modal.style.display = 'none';
        });
    }
    
    clearFocus() {
        document.activeElement?.blur();
    }
    
    // Load saved preferences
    loadPreferences() {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            this.currentTheme = savedTheme;
            document.documentElement.setAttribute('data-theme', savedTheme);
        }
        
        const savedFontSize = localStorage.getItem('fontSize');
        if (savedFontSize) {
            this.fontSize = parseInt(savedFontSize);
            this.updateFontSize();
        }
        
        const savedHighContrast = localStorage.getItem('highContrast');
        if (savedHighContrast === 'true') {
            this.highContrast = true;
            document.body.classList.add('high-contrast');
        }
    }
}

// Initialize accessibility manager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const accessibilityManager = new AccessibilityManager();
    accessibilityManager.loadPreferences();
    
    // Make it globally available
    window.accessibilityManager = accessibilityManager;
});

// Enhanced Netflix navigation functionality
function selectPage(page) {
    const pageMap = {
        'dashboard': '🏠 ダッシュボード',
        'realtime': '⚡ リアルタイム',
        'screening': '🔍 スクリーニング',
        'ai': '🤖 AI分析',
        'portfolio': '📊 ポートフォリオ',
        'settings': '⚙️ 設定'
    };
    
    // Update Streamlit selectbox
    const selectbox = document.querySelector('[data-testid="stSelectbox"] select');
    if (selectbox) {
        const options = Array.from(selectbox.options);
        const targetOption = options.find(option => 
            option.textContent.includes(pageMap[page])
        );
        if (targetOption) {
            selectbox.value = targetOption.value;
            selectbox.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }
    
    // Update active navigation item
    document.querySelectorAll('.netflix-nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    const activeItem = document.querySelector(`[onclick="selectPage('${page}')"]`);
    if (activeItem) {
        activeItem.classList.add('active');
    }
    
    // Announce to screen readers
    if (window.accessibilityManager) {
        window.accessibilityManager.announceToScreenReader(`${pageMap[page]}ページに移動しました`);
    }
}

// Enhanced animation and interaction functions
function addEnhancedAnimations() {
    // Smooth scroll behavior
    document.documentElement.style.scrollBehavior = 'smooth';
    
    // Intersection Observer for animations
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, { threshold: 0.1 });
    
    // Observe elements for animation
    document.querySelectorAll('.metric-card, .netflix-nav-item').forEach(el => {
        observer.observe(el);
    });
}

// Initialize enhanced animations
document.addEventListener('DOMContentLoaded', addEnhancedAnimations);