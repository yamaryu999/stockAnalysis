/**
 * 🚀 日本株価分析ツール - アクセシビリティ改善
 * キーボードナビゲーション、スクリーンリーダー対応、フォーカス管理
 */

class AccessibilityManager {
    constructor() {
        this.init();
    }

    init() {
        this.setupKeyboardNavigation();
        this.setupScreenReaderSupport();
        this.setupFocusManagement();
        this.setupAriaLabels();
        this.setupSkipLinks();
    }

    /**
     * キーボードナビゲーションの設定
     */
    setupKeyboardNavigation() {
        // Tabキーでのナビゲーション改善
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                this.handleTabNavigation(e);
            }
            
            // Enterキーでボタンクリック
            if (e.key === 'Enter' && e.target.classList.contains('stButton')) {
                e.target.click();
            }
            
            // Escapeキーでモーダル閉じる
            if (e.key === 'Escape') {
                this.closeModals();
            }
            
            // 矢印キーでタブ切り替え
            if (['ArrowLeft', 'ArrowRight'].includes(e.key)) {
                this.handleTabSwitching(e);
            }
        });
    }

    /**
     * Tabナビゲーションの処理
     */
    handleTabNavigation(e) {
        const focusableElements = this.getFocusableElements();
        const currentIndex = focusableElements.indexOf(document.activeElement);
        
        if (e.shiftKey) {
            // Shift+Tab: 前の要素へ
            if (currentIndex > 0) {
                focusableElements[currentIndex - 1].focus();
            } else {
                focusableElements[focusableElements.length - 1].focus();
            }
        } else {
            // Tab: 次の要素へ
            if (currentIndex < focusableElements.length - 1) {
                focusableElements[currentIndex + 1].focus();
            } else {
                focusableElements[0].focus();
            }
        }
        
        e.preventDefault();
    }

    /**
     * フォーカス可能な要素を取得
     */
    getFocusableElements() {
        const selectors = [
            'button:not([disabled])',
            'input:not([disabled])',
            'select:not([disabled])',
            'textarea:not([disabled])',
            'a[href]',
            '[tabindex]:not([tabindex="-1"])',
            '.stButton button',
            '.stTabs [data-baseweb="tab"]',
            '.metric-card[tabindex]'
        ];
        
        return Array.from(document.querySelectorAll(selectors.join(', ')));
    }

    /**
     * タブ切り替えの処理
     */
    handleTabSwitching(e) {
        const tabs = document.querySelectorAll('.stTabs [data-baseweb="tab"]');
        const activeTab = document.querySelector('.stTabs [aria-selected="true"]');
        
        if (!activeTab) return;
        
        const currentIndex = Array.from(tabs).indexOf(activeTab);
        let newIndex;
        
        if (e.key === 'ArrowLeft') {
            newIndex = currentIndex > 0 ? currentIndex - 1 : tabs.length - 1;
        } else if (e.key === 'ArrowRight') {
            newIndex = currentIndex < tabs.length - 1 ? currentIndex + 1 : 0;
        }
        
        if (newIndex !== undefined) {
            tabs[newIndex].click();
            tabs[newIndex].focus();
        }
    }

    /**
     * スクリーンリーダー対応の設定
     */
    setupScreenReaderSupport() {
        // 動的コンテンツの変更をアナウンス
        this.setupLiveRegion();
        
        // 画像のalt属性を改善
        this.improveImageAltText();
        
        // フォームラベルの改善
        this.improveFormLabels();
    }

    /**
     * ライブリージョンの設定
     */
    setupLiveRegion() {
        // ライブリージョン要素を作成
        const liveRegion = document.createElement('div');
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.className = 'sr-only';
        liveRegion.style.cssText = `
            position: absolute;
            left: -10000px;
            width: 1px;
            height: 1px;
            overflow: hidden;
        `;
        document.body.appendChild(liveRegion);
        
        // 分析結果の更新をアナウンス
        this.observeAnalysisResults(liveRegion);
    }

    /**
     * 分析結果の変更を監視
     */
    observeAnalysisResults(liveRegion) {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    const addedNodes = Array.from(mutation.addedNodes);
                    addedNodes.forEach((node) => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            if (node.classList.contains('metric-card')) {
                                liveRegion.textContent = '分析結果が更新されました';
                            }
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

    /**
     * 画像のalt属性を改善
     */
    improveImageAltText() {
        const images = document.querySelectorAll('img');
        images.forEach((img) => {
            if (!img.alt) {
                img.alt = 'チャートまたはグラフ';
            }
        });
    }

    /**
     * フォームラベルの改善
     */
    improveFormLabels() {
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach((input) => {
            if (!input.getAttribute('aria-label') && !input.getAttribute('aria-labelledby')) {
                const label = input.previousElementSibling;
                if (label && label.tagName === 'LABEL') {
                    input.setAttribute('aria-labelledby', label.id || this.generateId(label));
                }
            }
        });
    }

    /**
     * フォーカス管理の設定
     */
    setupFocusManagement() {
        // フォーカス可視性の改善
        this.improveFocusVisibility();
        
        // フォーカストラップの設定
        this.setupFocusTrap();
        
        // フォーカス復元の設定
        this.setupFocusRestore();
    }

    /**
     * フォーカス可視性の改善
     */
    improveFocusVisibility() {
        const style = document.createElement('style');
        style.textContent = `
            *:focus {
                outline: 3px solid #667eea !important;
                outline-offset: 2px !important;
            }
            
            .stButton button:focus {
                outline: 3px solid #667eea !important;
                outline-offset: 2px !important;
            }
            
            .stTabs [data-baseweb="tab"]:focus {
                outline: 2px solid #667eea !important;
                outline-offset: 1px !important;
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * フォーカストラップの設定
     */
    setupFocusTrap() {
        // モーダルが開いた時のフォーカストラップ
        const modals = document.querySelectorAll('[role="dialog"]');
        modals.forEach((modal) => {
            modal.addEventListener('keydown', (e) => {
                if (e.key === 'Tab') {
                    this.trapFocus(e, modal);
                }
            });
        });
    }

    /**
     * フォーカスをトラップ
     */
    trapFocus(e, container) {
        const focusableElements = container.querySelectorAll(
            'button, input, select, textarea, a[href], [tabindex]:not([tabindex="-1"])'
        );
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        
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

    /**
     * フォーカス復元の設定
     */
    setupFocusRestore() {
        let lastFocusedElement = null;
        
        document.addEventListener('focusin', (e) => {
            lastFocusedElement = e.target;
        });
        
        // ページロード時にフォーカスを復元
        window.addEventListener('load', () => {
            if (lastFocusedElement) {
                lastFocusedElement.focus();
            }
        });
    }

    /**
     * ARIAラベルの設定
     */
    setupAriaLabels() {
        // ボタンにARIAラベルを追加
        this.addAriaLabelsToButtons();
        
        // カードにARIAラベルを追加
        this.addAriaLabelsToCards();
        
        // タブにARIAラベルを追加
        this.addAriaLabelsToTabs();
    }

    /**
     * ボタンにARIAラベルを追加
     */
    addAriaLabelsToButtons() {
        const buttons = document.querySelectorAll('.stButton button');
        buttons.forEach((button) => {
            if (!button.getAttribute('aria-label')) {
                button.setAttribute('aria-label', button.textContent.trim());
            }
        });
    }

    /**
     * カードにARIAラベルを追加
     */
    addAriaLabelsToCards() {
        const cards = document.querySelectorAll('.metric-card');
        cards.forEach((card, index) => {
            card.setAttribute('role', 'region');
            card.setAttribute('aria-label', `メトリックカード ${index + 1}`);
            card.setAttribute('tabindex', '0');
        });
    }

    /**
     * タブにARIAラベルを追加
     */
    addAriaLabelsToTabs() {
        const tabs = document.querySelectorAll('.stTabs [data-baseweb="tab"]');
        tabs.forEach((tab, index) => {
            tab.setAttribute('aria-label', `タブ ${index + 1}: ${tab.textContent.trim()}`);
        });
    }

    /**
     * スキップリンクの設定
     */
    setupSkipLinks() {
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.textContent = 'メインコンテンツにスキップ';
        skipLink.className = 'skip-link';
        skipLink.style.cssText = `
            position: absolute;
            top: -40px;
            left: 6px;
            background: #667eea;
            color: white;
            padding: 8px;
            text-decoration: none;
            border-radius: 4px;
            z-index: 1000;
            transition: top 0.3s;
        `;
        
        skipLink.addEventListener('focus', () => {
            skipLink.style.top = '6px';
        });
        
        skipLink.addEventListener('blur', () => {
            skipLink.style.top = '-40px';
        });
        
        document.body.insertBefore(skipLink, document.body.firstChild);
        
        // メインコンテンツにIDを追加
        const mainContent = document.querySelector('.main');
        if (mainContent) {
            mainContent.id = 'main-content';
        }
    }

    /**
     * モーダルを閉じる
     */
    closeModals() {
        const modals = document.querySelectorAll('[role="dialog"]');
        modals.forEach((modal) => {
            const closeButton = modal.querySelector('[aria-label*="閉じる"], [aria-label*="close"]');
            if (closeButton) {
                closeButton.click();
            }
        });
    }

    /**
     * IDを生成
     */
    generateId(element) {
        const id = 'label-' + Math.random().toString(36).substr(2, 9);
        element.id = id;
        return id;
    }

    /**
     * アクセシビリティチェック
     */
    checkAccessibility() {
        const issues = [];
        
        // 画像のalt属性チェック
        const images = document.querySelectorAll('img');
        images.forEach((img) => {
            if (!img.alt) {
                issues.push(`画像にalt属性がありません: ${img.src}`);
            }
        });
        
        // フォームのラベルチェック
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach((input) => {
            if (!input.getAttribute('aria-label') && 
                !input.getAttribute('aria-labelledby') && 
                !input.closest('label')) {
                issues.push(`フォーム要素にラベルがありません: ${input.type || input.tagName}`);
            }
        });
        
        // ボタンのテキストチェック
        const buttons = document.querySelectorAll('button');
        buttons.forEach((button) => {
            if (!button.textContent.trim() && !button.getAttribute('aria-label')) {
                issues.push(`ボタンにテキストまたはaria-labelがありません`);
            }
        });
        
        return issues;
    }
}

// アクセシビリティマネージャーを初期化
document.addEventListener('DOMContentLoaded', () => {
    new AccessibilityManager();
});

// Streamlitの動的コンテンツ更新に対応
if (window.streamlit) {
    window.streamlit.addEventListener('onload', () => {
        new AccessibilityManager();
    });
}