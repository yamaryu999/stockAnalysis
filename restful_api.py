"""
RESTful API for Stock Analysis Tool
株価分析ツール用RESTful API - FastAPI、認証、レート制限、OpenAPI仕様
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
import uvicorn
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from pydantic import BaseModel, Field, validator
import json
import time
from contextlib import asynccontextmanager
import os
import sys

# プロジェクトのモジュールをインポート
try:
    from enhanced_data_sources import multi_data_source_manager
    from advanced_ml_pipeline import advanced_ml_pipeline
    from enhanced_realtime_engine import enhanced_realtime_engine
    from intelligent_performance_optimizer import intelligent_performance_optimizer
    from security_manager import security_manager
    from advanced_visualization import advanced_visualization
    from database_manager import DatabaseManager
    from cache_manager import cache_manager
except ImportError as e:
    logging.error(f"モジュールインポートエラー: {e}")
    # ダミーのモジュールを作成
    class DummyModule:
        def __getattr__(self, name):
            return lambda *args, **kwargs: {}
    
    multi_data_source_manager = DummyModule()
    advanced_ml_pipeline = DummyModule()
    enhanced_realtime_engine = DummyModule()
    intelligent_performance_optimizer = DummyModule()
    security_manager = DummyModule()
    advanced_visualization = DummyModule()
    DatabaseManager = DummyModule
    cache_manager = DummyModule()

# Pydanticモデル
class StockDataRequest(BaseModel):
    symbol: str = Field(..., description="株式シンボル")
    period: str = Field(default="1y", description="期間")
    interval: str = Field(default="1d", description="間隔")

class FinancialMetricsRequest(BaseModel):
    symbol: str = Field(..., description="株式シンボル")

class NewsRequest(BaseModel):
    symbol: str = Field(..., description="株式シンボル")
    days_back: int = Field(default=7, description="過去何日分のニュースを取得するか")

class MLPredictionRequest(BaseModel):
    symbol: str = Field(..., description="株式シンボル")
    model_type: str = Field(default="ensemble", description="使用するモデルタイプ")
    days_ahead: int = Field(default=5, description="何日先を予測するか")

class RealtimeAnalysisRequest(BaseModel):
    symbols: List[str] = Field(..., description="分析対象のシンボルリスト")

class UserRegistrationRequest(BaseModel):
    user_id: str = Field(..., description="ユーザーID")
    password: str = Field(..., description="パスワード")
    role: str = Field(default="user", description="ユーザーロール")

class UserLoginRequest(BaseModel):
    user_id: str = Field(..., description="ユーザーID")
    password: str = Field(..., description="パスワード")

class AlertRuleRequest(BaseModel):
    rule_id: str = Field(..., description="ルールID")
    symbol: str = Field(..., description="対象シンボル")
    condition: Dict[str, Any] = Field(..., description="アラート条件")
    severity: str = Field(default="medium", description="重要度")

class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: Optional[str] = None

# レート制限管理
class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    def is_allowed(self, client_ip: str) -> bool:
        current_time = time.time()
        window_start = current_time - self.window_seconds
        
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # 古いリクエストを削除
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > window_start
        ]
        
        # リクエスト数をチェック
        if len(self.requests[client_ip]) >= self.max_requests:
            return False
        
        # 新しいリクエストを追加
        self.requests[client_ip].append(current_time)
        return True

# グローバル変数
rate_limiter = RateLimiter()
security = HTTPBearer()

# アプリケーションのライフサイクル管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 起動時の処理
    logging.info("APIサーバー起動中...")
    
    # データベースの初期化
    try:
        db_manager = DatabaseManager()
        logging.info("データベース初期化完了")
    except Exception as e:
        logging.error(f"データベース初期化エラー: {e}")
    
    # パフォーマンス最適化の開始
    try:
        intelligent_performance_optimizer.start_auto_optimization()
        logging.info("パフォーマンス最適化開始")
    except Exception as e:
        logging.error(f"パフォーマンス最適化開始エラー: {e}")
    
    yield
    
    # シャットダウン時の処理
    logging.info("APIサーバーシャットダウン中...")
    
    try:
        intelligent_performance_optimizer.stop_auto_optimization()
        logging.info("パフォーマンス最適化停止")
    except Exception as e:
        logging.error(f"パフォーマンス最適化停止エラー: {e}")
    
    try:
        enhanced_realtime_engine.stop_analysis()
        logging.info("リアルタイム分析停止")
    except Exception as e:
        logging.error(f"リアルタイム分析停止エラー: {e}")

# FastAPIアプリケーションの作成
app = FastAPI(
    title="Stock Analysis API",
    description="高度な株価分析ツール用RESTful API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# ミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に制限
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # 本番環境では適切に制限
)

# 依存関係
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """現在のユーザーを取得"""
    try:
        # セッションIDからユーザーを検証
        session = security_manager.access_control.session_manager.validate_session(credentials.credentials)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session"
            )
        return session.user_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

async def check_rate_limit(request: Request):
    """レート制限をチェック"""
    client_ip = request.client.host
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )

async def log_request(request: Request, call_next):
    """リクエストをログ"""
    start_time = time.time()
    
    # リクエスト情報をログ
    logging.info(f"Request: {request.method} {request.url}")
    
    response = await call_next(request)
    
    # レスポンス時間をログ
    process_time = time.time() - start_time
    logging.info(f"Response: {response.status_code} - {process_time:.3f}s")
    
    return response

app.middleware("http")(log_request)

# ルートエンドポイント
@app.get("/", response_class=HTMLResponse)
async def root():
    """ルートエンドポイント"""
    return """
    <html>
        <head>
            <title>Stock Analysis API</title>
        </head>
        <body>
            <h1>Stock Analysis API</h1>
            <p>高度な株価分析ツール用RESTful API</p>
            <ul>
                <li><a href="/docs">API Documentation (Swagger)</a></li>
                <li><a href="/redoc">API Documentation (ReDoc)</a></li>
                <li><a href="/health">Health Check</a></li>
                <li><a href="/metrics">Performance Metrics</a></li>
            </ul>
        </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0"
    }

@app.get("/metrics")
async def get_metrics():
    """パフォーマンスメトリクスを取得"""
    try:
        metrics = intelligent_performance_optimizer.get_performance_report()
        return APIResponse(
            success=True,
            message="Metrics retrieved successfully",
            data=metrics
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve metrics: {str(e)}"
        )

# 認証エンドポイント
@app.post("/auth/register", response_model=APIResponse)
async def register_user(request: UserRegistrationRequest):
    """ユーザー登録"""
    try:
        success = security_manager.create_user(
            request.user_id,
            request.password,
            request.role
        )
        
        if success:
            return APIResponse(
                success=True,
                message="User registered successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User registration failed"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration error: {str(e)}"
        )

@app.post("/auth/login", response_model=APIResponse)
async def login_user(request: UserLoginRequest, http_request: Request):
    """ユーザーログイン"""
    try:
        client_ip = http_request.client.host
        user_agent = http_request.headers.get("user-agent", "")
        
        success, session_id = security_manager.authenticate_user(
            request.user_id,
            request.password,
            client_ip,
            user_agent
        )
        
        if success:
            return APIResponse(
                success=True,
                message="Login successful",
                data={"session_id": session_id}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login error: {str(e)}"
        )

@app.post("/auth/logout", response_model=APIResponse)
async def logout_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """ユーザーログアウト"""
    try:
        security_manager.access_control.session_manager.invalidate_session(credentials.credentials)
        return APIResponse(
            success=True,
            message="Logout successful"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout error: {str(e)}"
        )

# データ取得エンドポイント
@app.get("/api/v1/stock/{symbol}", response_model=APIResponse)
async def get_stock_data(
    symbol: str,
    period: str = "1y",
    interval: str = "1d",
    _: str = Depends(get_current_user)
):
    """株価データを取得"""
    try:
        data = multi_data_source_manager.get_stock_data(symbol, period)
        
        if data:
            return APIResponse(
                success=True,
                message="Stock data retrieved successfully",
                data={
                    "symbol": data.symbol,
                    "data": data.data.to_dict(),
                    "source": data.source,
                    "confidence": data.confidence,
                    "metadata": data.metadata
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stock data not found"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve stock data: {str(e)}"
        )

@app.get("/api/v1/stock/{symbol}/metrics", response_model=APIResponse)
async def get_financial_metrics(
    symbol: str,
    _: str = Depends(get_current_user)
):
    """財務指標を取得"""
    try:
        metrics = multi_data_source_manager.get_financial_metrics(symbol)
        
        if metrics:
            return APIResponse(
                success=True,
                message="Financial metrics retrieved successfully",
                data=metrics
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Financial metrics not found"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve financial metrics: {str(e)}"
        )

@app.get("/api/v1/stock/{symbol}/news", response_model=APIResponse)
async def get_news_data(
    symbol: str,
    days_back: int = 7,
    _: str = Depends(get_current_user)
):
    """ニュースデータを取得"""
    try:
        news = multi_data_source_manager.get_news_data(symbol, days_back)
        
        return APIResponse(
            success=True,
            message="News data retrieved successfully",
            data=news
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve news data: {str(e)}"
        )

# 機械学習エンドポイント
@app.post("/api/v1/ml/predict", response_model=APIResponse)
async def predict_stock_price(
    request: MLPredictionRequest,
    _: str = Depends(get_current_user)
):
    """株価予測を実行"""
    try:
        # 株価データを取得
        stock_data = multi_data_source_manager.get_stock_data(request.symbol, "1y")
        if not stock_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stock data not found"
            )
        
        # 財務指標を取得
        financial_metrics = multi_data_source_manager.get_financial_metrics(request.symbol)
        
        # 特徴量を準備
        features, target = advanced_ml_pipeline.prepare_features(
            stock_data.data, financial_metrics
        )
        
        if features.empty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient data for prediction"
            )
        
        # モデルを訓練（必要に応じて）
        if not advanced_ml_pipeline.load_models(request.symbol):
            advanced_ml_pipeline.train_models(features, target, request.symbol)
        
        # 予測を実行
        prediction = advanced_ml_pipeline.predict(
            request.symbol, features.tail(1), request.model_type
        )
        
        return APIResponse(
            success=True,
            message="Prediction completed successfully",
            data=asdict(prediction)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )

@app.get("/api/v1/ml/models/{symbol}", response_model=APIResponse)
async def get_model_insights(
    symbol: str,
    _: str = Depends(get_current_user)
):
    """モデルインサイトを取得"""
    try:
        insights = advanced_ml_pipeline.get_model_insights(symbol)
        
        return APIResponse(
            success=True,
            message="Model insights retrieved successfully",
            data=insights
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve model insights: {str(e)}"
        )

# リアルタイム分析エンドポイント
@app.post("/api/v1/realtime/start", response_model=APIResponse)
async def start_realtime_analysis(
    request: RealtimeAnalysisRequest,
    _: str = Depends(get_current_user)
):
    """リアルタイム分析を開始"""
    try:
        enhanced_realtime_engine.start_analysis(request.symbols)
        
        return APIResponse(
            success=True,
            message="Realtime analysis started successfully",
            data={"symbols": request.symbols}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start realtime analysis: {str(e)}"
        )

@app.post("/api/v1/realtime/stop", response_model=APIResponse)
async def stop_realtime_analysis(_: str = Depends(get_current_user)):
    """リアルタイム分析を停止"""
    try:
        enhanced_realtime_engine.stop_analysis()
        
        return APIResponse(
            success=True,
            message="Realtime analysis stopped successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop realtime analysis: {str(e)}"
        )

@app.get("/api/v1/realtime/results", response_model=APIResponse)
async def get_realtime_results(_: str = Depends(get_current_user)):
    """リアルタイム分析結果を取得"""
    try:
        results = enhanced_realtime_engine.get_all_results()
        
        return APIResponse(
            success=True,
            message="Realtime results retrieved successfully",
            data=results
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve realtime results: {str(e)}"
        )

@app.get("/api/v1/realtime/alerts", response_model=APIResponse)
async def get_realtime_alerts(
    severity: Optional[str] = None,
    _: str = Depends(get_current_user)
):
    """リアルタイムアラートを取得"""
    try:
        alerts = enhanced_realtime_engine.get_active_alerts(severity)
        
        return APIResponse(
            success=True,
            message="Realtime alerts retrieved successfully",
            data=[asdict(alert) for alert in alerts]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve realtime alerts: {str(e)}"
        )

# アラート管理エンドポイント
@app.post("/api/v1/alerts/rules", response_model=APIResponse)
async def create_alert_rule(
    request: AlertRuleRequest,
    _: str = Depends(get_current_user)
):
    """アラートルールを作成"""
    try:
        rule = {
            'symbol': request.symbol,
            'condition': request.condition,
            'severity': request.severity,
            'message': f"Custom alert rule for {request.symbol}"
        }
        
        enhanced_realtime_engine.add_custom_alert_rule(request.rule_id, rule)
        
        return APIResponse(
            success=True,
            message="Alert rule created successfully",
            data={"rule_id": request.rule_id}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create alert rule: {str(e)}"
        )

# 可視化エンドポイント
@app.get("/api/v1/visualization/chart/{chart_type}", response_model=APIResponse)
async def get_chart_data(
    chart_type: str,
    symbol: str,
    period: str = "1y",
    _: str = Depends(get_current_user)
):
    """チャートデータを取得"""
    try:
        # 株価データを取得
        stock_data = multi_data_source_manager.get_stock_data(symbol, period)
        if not stock_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stock data not found"
            )
        
        # チャートタイプに応じてデータを生成
        if chart_type == "candlestick":
            chart = advanced_visualization['chart_generator'].create_candlestick_chart(
                stock_data.data
            )
        elif chart_type == "volume":
            chart = advanced_visualization['chart_generator'].create_volume_chart(
                stock_data.data
            )
        elif chart_type == "technical":
            chart = advanced_visualization['chart_generator'].create_technical_indicators_chart(
                stock_data.data
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid chart type"
            )
        
        return APIResponse(
            success=True,
            message="Chart data retrieved successfully",
            data=chart.to_json()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate chart: {str(e)}"
        )

# セキュリティエンドポイント
@app.get("/api/v1/security/report", response_model=APIResponse)
async def get_security_report(
    days: int = 7,
    _: str = Depends(get_current_user)
):
    """セキュリティレポートを取得"""
    try:
        report = security_manager.get_security_report(days)
        
        return APIResponse(
            success=True,
            message="Security report retrieved successfully",
            data=report
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve security report: {str(e)}"
        )

# パフォーマンス最適化エンドポイント
@app.post("/api/v1/performance/optimize", response_model=APIResponse)
async def manual_optimize(
    optimization_type: str,
    _: str = Depends(get_current_user)
):
    """手動最適化を実行"""
    try:
        result = intelligent_performance_optimizer.manual_optimize(optimization_type)
        
        return APIResponse(
            success=True,
            message="Optimization completed successfully",
            data=result
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Optimization failed: {str(e)}"
        )

# エラーハンドラー
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP例外ハンドラー"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "timestamp": datetime.now(),
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """一般例外ハンドラー"""
    logging.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal server error",
            "timestamp": datetime.now(),
            "path": str(request.url)
        }
    )

# OpenAPI仕様のカスタマイズ
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Stock Analysis API",
        version="1.0.0",
        description="高度な株価分析ツール用RESTful API",
        routes=app.routes,
    )
    
    # セキュリティスキームを追加
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    
    # セキュリティ要件を追加
    openapi_schema["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# サーバー起動関数
def start_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """APIサーバーを起動"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    uvicorn.run(
        "restful_api:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    start_server()
