// モバイルデバイス検出とレスポンシブ対応
(function() {
    'use strict';
    
    // デバイス情報を取得
    function getDeviceInfo() {
        const userAgent = navigator.userAgent;
        const screenWidth = window.screen.width;
        const screenHeight = window.screen.height;
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        
        // モバイルデバイス判定
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent) || 
                       viewportWidth <= 768;
        
        // タブレット判定
        const isTablet = viewportWidth > 768 && viewportWidth <= 1024;
        
        // デスクトップ判定
        const isDesktop = viewportWidth > 1024;
        
        return {
            isMobile: isMobile,
            isTablet: isTablet,
            isDesktop: isDesktop,
            width: viewportWidth,
            height: viewportHeight,
            screenWidth: screenWidth,
            screenHeight: screenHeight,
            userAgent: userAgent,
            orientation: screenWidth > screenHeight ? 'landscape' : 'portrait'
        };
    }
    
    // Streamlitセッション状態にデバイス情報を保存
    function saveDeviceInfo() {
        const deviceInfo = getDeviceInfo();
        
        // Streamlitのセッション状態に保存
        if (window.parent && window.parent.streamlit) {
            window.parent.streamlit.setComponentValue({
                type: 'device_info',
                data: deviceInfo
            });
        }
        
        // ローカルストレージにも保存
        localStorage.setItem('device_info', JSON.stringify(deviceInfo));
        
        // CSSクラスを追加
        document.body.classList.add(deviceInfo.isMobile ? 'mobile' : 
                                  deviceInfo.isTablet ? 'tablet' : 'desktop');
        
        return deviceInfo;
    }
    
    // リサイズイベントハンドラー
    function handleResize() {
        const deviceInfo = saveDeviceInfo();
        
        // モバイルメニューの制御
        if (deviceInfo.isMobile) {
            // サイドバーを非表示
            const sidebar = document.querySelector('.css-1d391kg');
            if (sidebar) {
                sidebar.style.transform = 'translateX(-100%)';
            }
        }
    }
    
    // タッチイベントの処理
    function handleTouchEvents() {
        let startY = 0;
        let startX = 0;
        
        document.addEventListener('touchstart', function(e) {
            startY = e.touches[0].clientY;
            startX = e.touches[0].clientX;
        });
        
        document.addEventListener('touchmove', function(e) {
            const currentY = e.touches[0].clientY;
            const currentX = e.touches[0].clientX;
            const diffY = startY - currentY;
            const diffX = startX - currentX;
            
            // プルツリフレッシュ
            if (diffY > 50 && Math.abs(diffX) < 50) {
                const indicator = document.querySelector('.pull-to-refresh-indicator');
                if (indicator) {
                    indicator.classList.add('active');
                }
            }
        });
        
        document.addEventListener('touchend', function(e) {
            const indicator = document.querySelector('.pull-to-refresh-indicator');
            if (indicator && indicator.classList.contains('active')) {
                indicator.classList.remove('active');
                // ページリロード
                setTimeout(() => {
                    window.location.reload();
                }, 500);
            }
        });
    }
    
    // ハンバーガーメニューの制御
    function initMobileMenu() {
        const menuButton = document.querySelector('.mobile-menu-button');
        const sidebar = document.querySelector('.css-1d391kg');
        
        if (menuButton && sidebar) {
            menuButton.addEventListener('click', function() {
                sidebar.classList.toggle('show');
            });
            
            // メニュー外をクリックで閉じる
            document.addEventListener('click', function(e) {
                if (!menuButton.contains(e.target) && !sidebar.contains(e.target)) {
                    sidebar.classList.remove('show');
                }
            });
        }
    }
    
    // スワイプジェスチャーの処理
    function initSwipeGestures() {
        let startX = 0;
        let startY = 0;
        
        document.addEventListener('touchstart', function(e) {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        });
        
        document.addEventListener('touchend', function(e) {
            const endX = e.changedTouches[0].clientX;
            const endY = e.changedTouches[0].clientY;
            const diffX = startX - endX;
            const diffY = startY - endY;
            
            // 水平スワイプ（左右）
            if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
                if (diffX > 0) {
                    // 左スワイプ
                    console.log('左スワイプ');
                } else {
                    // 右スワイプ
                    console.log('右スワイプ');
                }
            }
            
            // 垂直スワイプ（上下）
            if (Math.abs(diffY) > Math.abs(diffX) && Math.abs(diffY) > 50) {
                if (diffY > 0) {
                    // 上スワイプ
                    console.log('上スワイプ');
                } else {
                    // 下スワイプ
                    console.log('下スワイプ');
                }
            }
        });
    }
    
    // レスポンシブ画像の処理
    function initResponsiveImages() {
        const images = document.querySelectorAll('img');
        
        images.forEach(img => {
            img.style.maxWidth = '100%';
            img.style.height = 'auto';
        });
    }
    
    // フォントサイズの調整
    function adjustFontSizes() {
        const deviceInfo = getDeviceInfo();
        
        if (deviceInfo.isMobile) {
            document.body.style.fontSize = '14px';
        } else if (deviceInfo.isTablet) {
            document.body.style.fontSize = '16px';
        } else {
            document.body.style.fontSize = '18px';
        }
    }
    
    // 初期化
    function init() {
        // デバイス情報を保存
        saveDeviceInfo();
        
        // イベントリスナーを設定
        window.addEventListener('resize', handleResize);
        window.addEventListener('orientationchange', handleResize);
        
        // モバイル機能を初期化
        if (getDeviceInfo().isMobile) {
            handleTouchEvents();
            initMobileMenu();
            initSwipeGestures();
        }
        
        // レスポンシブ機能を初期化
        initResponsiveImages();
        adjustFontSizes();
        
        // DOMContentLoadedイベントで再初期化
        document.addEventListener('DOMContentLoaded', function() {
            initMobileMenu();
            initResponsiveImages();
        });
    }
    
    // ページ読み込み時に初期化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // グローバル関数として公開
    window.mobileUtils = {
        getDeviceInfo: getDeviceInfo,
        saveDeviceInfo: saveDeviceInfo,
        isMobile: function() { return getDeviceInfo().isMobile; },
        isTablet: function() { return getDeviceInfo().isTablet; },
        isDesktop: function() { return getDeviceInfo().isDesktop; }
    };
    
})();