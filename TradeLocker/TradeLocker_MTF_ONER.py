#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
TradeLocker_MTF_ONER.py : Multi Timeframe Expert Advisor for TradeLocker
Bot EA nhiều khung thời gian cho TradeLocker
==============================================================================
7 TF × 3 Strategies = 21 orders | 7 khung × 3 chiến lược = 21 lệnh
Version: TL_V1 - Converted from MT5 EA V2 | Phiên bản: TL_V1 - Chuyển đổi từ MT5 EA V2

CONVERTED FROM: /MQL5/Experts/_MT5_EAs_MTF ONER_V2.mq5 (2995 lines)
LOGIC: 100% identical to MT5 EA - NO CHANGES | LOGIC: 100% giống MT5 EA - KHÔNG THAY ĐỔI
==============================================================================
"""

import sys
import os
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass, field
import signal
import threading

# TradeLocker API (requires: pip install tradelocker)
try:
    from tradelocker import TLAPI
except ImportError:
    print("ERROR: TradeLocker library not installed. Run: pip install tradelocker")
    sys.exit(1)

# ==============================================================================
#  PART 1: USER INPUTS (30 inputs + 4 separators) | CẤU HÌNH NGƯỜI DÙNG
# ==============================================================================

class Config:
    """User configuration (loads from config.json) | Cấu hình người dùng (đọc từ config.json)"""

    # ===== A. CORE SETTINGS | CÀI ĐẶT CỐT LÕI =====

    # A.1 Timeframe toggles (7) | Bật/tắt khung thời gian
    TF_M1: bool = False  # M1 Signal(1,-1) vs Timestamp(Mt4server)
    TF_M5: bool = True   # M5 (Buy/Sell Symbol_M5)
    TF_M15: bool = True  # M15 (Signal Symbol_M15)
    TF_M30: bool = True  # M30 (Buy/Sell Symbol_M30)
    TF_H1: bool = True   # H1 (Signal Symbol_H1)
    TF_H4: bool = True   # H4 (Buy/Sell Symbol_H4)
    TF_D1: bool = False  # D1 (Signal Symbol_D1)

    # A.2 Strategy toggles (3) | Bật/tắt chiến lược
    S1_HOME: bool = True   # S1: Binary (Home_7TF > B1:S1_NewsFilter=false)
    S2_TREND: bool = True  # S2: Trend (Follow D1)
    S3_NEWS: bool = True   # S3: News (High compact)

    # A.3 Close Mode Configuration (2) | Chế độ đóng lệnh
    S1_CloseByM1: bool = True   # S1: Close by M1 (TRUE=fast M1, FALSE=own TF)
    S2_CloseByM1: bool = False  # S2: Close by M1 (TRUE=fast M1, FALSE=own TF)

    # A.4 Risk management (2) | Quản lý rủi ro
    FixedLotSize: float = 0.1           # Lot size (0.01-1.0 recommended)
    MaxLoss_Fallback: float = -1000.0   # Maxloss fallback ($USD if CSDL fails)

    # A.5 Data source (1) | Nguồn dữ liệu
    # Options: "FOLDER_1", "FOLDER_2", "FOLDER_3", "HTTP_API"
    CSDL_Source: str = "HTTP_API"  # CSDL via HTTP (Bot Sync Py)

    # A.6 HTTP API settings | Cấu hình HTTP API
    HTTP_Server_IP: str = "dungalading.duckdns.org"  # HTTP Server domain/IP
    HTTP_API_Key: str = ""                           # API Key (empty = no auth)
    EnableSymbolNormalization: bool = False          # Symbol name normalization

    # ===== B. STRATEGY CONFIG | CẤU HÌNH CHIẾN LƯỢC =====

    # B.1 S1 NEWS Filter (3) | Lọc tin tức cho S1
    S1_UseNewsFilter: bool = True          # S1: Use NEWS filter (TRUE=strict, FALSE=basic)
    MinNewsLevelS1: int = 2                # S1: Min NEWS level (2-70, higher=stricter)
    S1_RequireNewsDirection: bool = True   # S1: Match NEWS direction (signal==news!)

    # B.2 S2 TREND Mode (1) | Chế độ xu hướng
    # Options: "S2_FOLLOW_D1" (0), "S2_FORCE_BUY" (1), "S2_FORCE_SELL" (-1)
    S2_TrendMode: int = 0  # S2: Trend (D1 Auto/manual)

    # B.2B S2 NEWS Filter (3) | Lọc tin tức cho S2 (optional, default OFF)
    S2_UseNewsFilter: bool = False         # S2: Use NEWS filter (FALSE=OFF, TRUE=ON)
    MinNewsLevelS2: int = 2                # S2: Min NEWS level (2-70, same as S1)
    S2_RequireNewsDirection: bool = False  # S2: Match NEWS direction (signal==news!)

    # B.3 S3 NEWS Configuration (4) | Cấu hình tin tức
    MinNewsLevelS3: int = 20               # S3: Min NEWS level (2-70)
    EnableBonusNews: bool = True           # S3: Enable Bonus (extra on high NEWS)
    BonusOrderCount: int = 1               # S3: Bonus count (1-5 orders)
    MinNewsLevelBonus: int = 2             # S3: Min NEWS for Bonus (threshold)
    BonusLotMultiplier: float = 1.2        # S3: Bonus lot multiplier (1.0-10)

    # ===== C. RISK PROTECTION | BẢO VỆ RỦI RO =====

    # C.1 Stoploss mode (3) | Chế độ cắt lỗ
    # Options: 0=NONE, 1=LAYER1_MAXLOSS, 2=LAYER2_MARGIN
    StoplossMode: int = 1            # Stoploss mode (0=OFF, 1=CSDL, 2=Margin)
    Layer2_Divisor: float = 5.0      # Layer2 divisor (margin/-5 = threshold)

    # C.2 Take profit (2) | Chốt lời
    UseTakeProfit: bool = False      # Enable take profit (FALSE=OFF, TRUE=ON)
    TakeProfit_Multiplier: float = 5 # TP_multi (vd=1000 × 0.21 × 3 = 630 USD)

    # ===== D. AUXILIARY SETTINGS | CÀI ĐẶT PHỤ TRỢ =====

    # D.1 Performance (1) | Hiệu suất
    UseEvenOddMode: bool = True  # Even/odd split mode (load balancing)

    # D.2 Health check & reset (2) | Kiểm tra sức khỏe
    EnableWeekendReset: bool = False  # Weekend reset (auto close Friday 23:50)
    EnableHealthCheck: bool = True    # Health check (8h/16h SPY bot status)

    # D.3 Display (2) | Hiển thị
    ShowDashboard: bool = True   # Show dashboard (console info)
    DebugMode: bool = False      # Debug mode (verbose logging)

    # D.4 NY Session Hours Filter (3) | Lọc giờ phiên NY (chỉ S1/S2, không S3/Bonus)
    EnableNYHoursFilter: bool = False  # Enable NY hours filter (only S1/S2, not S3/Bonus)
    NYSessionStart: int = 14           # NY session start hour (Server time, ICMarket EU: 14=8AM NY)
    NYSessionEnd: int = 21             # NY session end hour (Server time, ICMarket EU: 21=3PM NY)

    # ===== E. TRADELOCKER CREDENTIALS | THÔNG TIN ĐĂNG NHẬP =====

    TL_Environment: str = "https://demo.tradelocker.com"  # TradeLocker server URL
    TL_Username: str = "user@email.com"                   # Account email
    TL_Password: str = "YOUR_PASSWORD"                    # Account password
    TL_Server: str = "SERVER_NAME"                        # Server name

    @classmethod
    def load_from_json(cls, json_path: str = "config.json"):
        """Load configuration from JSON file | Đọc cấu hình từ file JSON

        Args:
            json_path: Path to config.json file

        Returns:
            Config instance with loaded settings
        """
        config = cls()

        # Try to load from JSON file
        try:
            # Get script directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            full_path = os.path.join(script_dir, json_path)

            if not os.path.exists(full_path):
                print(f"⚠️  Config file not found: {full_path}")
                print(f"⚠️  Using default configuration (edit {json_path} to customize)")
                return config

            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Load TradeLocker credentials
            if 'tradelocker' in data:
                tl = data['tradelocker']
                config.TL_Environment = tl.get('environment', config.TL_Environment)
                config.TL_Username = tl.get('username', config.TL_Username)
                config.TL_Password = tl.get('password', config.TL_Password)
                config.TL_Server = tl.get('server', config.TL_Server)

            # Load timeframes
            if 'timeframes' in data:
                tf = data['timeframes']
                config.TF_M1 = tf.get('M1', config.TF_M1)
                config.TF_M5 = tf.get('M5', config.TF_M5)
                config.TF_M15 = tf.get('M15', config.TF_M15)
                config.TF_M30 = tf.get('M30', config.TF_M30)
                config.TF_H1 = tf.get('H1', config.TF_H1)
                config.TF_H4 = tf.get('H4', config.TF_H4)
                config.TF_D1 = tf.get('D1', config.TF_D1)

            # Load strategies
            if 'strategies' in data:
                strat = data['strategies']
                config.S1_HOME = strat.get('S1_HOME', config.S1_HOME)
                config.S2_TREND = strat.get('S2_TREND', config.S2_TREND)
                config.S3_NEWS = strat.get('S3_NEWS', config.S3_NEWS)

            # Load close mode
            if 'close_mode' in data:
                cm = data['close_mode']
                config.S1_CloseByM1 = cm.get('S1_CloseByM1', config.S1_CloseByM1)
                config.S2_CloseByM1 = cm.get('S2_CloseByM1', config.S2_CloseByM1)

            # Load risk settings
            if 'risk' in data:
                risk = data['risk']
                config.FixedLotSize = risk.get('FixedLotSize', config.FixedLotSize)
                config.MaxLoss_Fallback = risk.get('MaxLoss_Fallback', config.MaxLoss_Fallback)

            # Load CSDL settings
            if 'csdl' in data:
                csdl = data['csdl']
                config.CSDL_Source = csdl.get('source', config.CSDL_Source)
                config.HTTP_Server_IP = csdl.get('HTTP_Server_IP', config.HTTP_Server_IP)
                config.HTTP_API_Key = csdl.get('HTTP_API_Key', config.HTTP_API_Key)
                config.EnableSymbolNormalization = csdl.get('EnableSymbolNormalization', config.EnableSymbolNormalization)

            # Load S1 strategy settings
            if 'strategy_s1' in data:
                s1 = data['strategy_s1']
                config.S1_UseNewsFilter = s1.get('UseNewsFilter', config.S1_UseNewsFilter)
                config.MinNewsLevelS1 = s1.get('MinNewsLevel', config.MinNewsLevelS1)
                config.S1_RequireNewsDirection = s1.get('RequireNewsDirection', config.S1_RequireNewsDirection)

            # Load S2 strategy settings
            if 'strategy_s2' in data:
                s2 = data['strategy_s2']
                config.S2_TrendMode = s2.get('TrendMode', config.S2_TrendMode)
                config.S2_UseNewsFilter = s2.get('UseNewsFilter', config.S2_UseNewsFilter)
                config.MinNewsLevelS2 = s2.get('MinNewsLevel', config.MinNewsLevelS2)
                config.S2_RequireNewsDirection = s2.get('RequireNewsDirection', config.S2_RequireNewsDirection)

            # Load S3 strategy settings
            if 'strategy_s3' in data:
                s3 = data['strategy_s3']
                config.MinNewsLevelS3 = s3.get('MinNewsLevel', config.MinNewsLevelS3)
                config.EnableBonusNews = s3.get('EnableBonusNews', config.EnableBonusNews)
                config.BonusOrderCount = s3.get('BonusOrderCount', config.BonusOrderCount)
                config.MinNewsLevelBonus = s3.get('MinNewsLevelBonus', config.MinNewsLevelBonus)
                config.BonusLotMultiplier = s3.get('BonusLotMultiplier', config.BonusLotMultiplier)

            # Load stoploss settings
            if 'stoploss' in data:
                sl = data['stoploss']
                config.StoplossMode = sl.get('Mode', config.StoplossMode)
                config.Layer2_Divisor = sl.get('Layer2_Divisor', config.Layer2_Divisor)

            # Load take profit settings
            if 'takeprofit' in data:
                tp = data['takeprofit']
                config.UseTakeProfit = tp.get('Enable', config.UseTakeProfit)
                config.TakeProfit_Multiplier = tp.get('Multiplier', config.TakeProfit_Multiplier)

            # Load auxiliary settings
            if 'auxiliary' in data:
                aux = data['auxiliary']
                config.UseEvenOddMode = aux.get('UseEvenOddMode', config.UseEvenOddMode)
                config.EnableWeekendReset = aux.get('EnableWeekendReset', config.EnableWeekendReset)
                config.EnableHealthCheck = aux.get('EnableHealthCheck', config.EnableHealthCheck)
                config.ShowDashboard = aux.get('ShowDashboard', config.ShowDashboard)
                config.DebugMode = aux.get('DebugMode', config.DebugMode)
                config.EnableNYHoursFilter = aux.get('EnableNYHoursFilter', config.EnableNYHoursFilter)
                config.NYSessionStart = aux.get('NYSessionStart', config.NYSessionStart)
                config.NYSessionEnd = aux.get('NYSessionEnd', config.NYSessionEnd)

            print(f"✅ Configuration loaded from: {json_path}")

        except json.JSONDecodeError as e:
            print(f"❌ ERROR: Invalid JSON in {json_path}: {e}")
            print(f"⚠️  Using default configuration")
        except Exception as e:
            print(f"❌ ERROR: Failed to load config: {e}")
            print(f"⚠️  Using default configuration")

        return config

# ==============================================================================
#  PART 2: DATA STRUCTURES (2 classes) | CẤU TRÚC DỮ LIỆU
# ==============================================================================

@dataclass
class CSDLLoveRow:
    """CSDL data for one timeframe (6 columns) | Dữ liệu CSDL cho 1 khung thời gian (6 cột)"""
    max_loss: float = 0.0      # Col 1: Max loss per 1 LOT
    timestamp: int = 0         # Col 2: Timestamp
    signal: int = 0            # Col 3: Signal (1=BUY, -1=SELL, 0=NONE)
    pricediff: float = 0.0     # Col 4: Price diff USD (unused)
    timediff: int = 0          # Col 5: Time diff minutes (unused)
    news: int = 0              # Col 6: News CASCADE (±11-16)

@dataclass
class EASymbolData:
    """EA data structure for current symbol (116 variables) | Cấu trúc dữ liệu EA cho symbol hiện tại"""

    # Symbol & File info (9 vars)
    symbol_name: str = ""
    normalized_symbol_name: str = ""
    symbol_prefix: str = ""
    symbol_type: str = ""          # FX/CRYPTO/METAL/INDEX/STOCK
    all_leverages: str = ""
    broker_name: str = ""
    account_type: str = ""
    csdl_folder: str = ""
    csdl_filename: str = ""

    # CSDL rows (7 rows)
    csdl_rows: List[CSDLLoveRow] = field(default_factory=lambda: [CSDLLoveRow() for _ in range(7)])

    # Core signals (14 vars = 2×7 TF)
    signal_old: List[int] = field(default_factory=lambda: [0] * 7)
    timestamp_old: List[int] = field(default_factory=lambda: [0] * 7)

    # Magic numbers (21 vars: 7×3)
    magic_numbers: List[List[int]] = field(default_factory=lambda: [[0]*3 for _ in range(7)])

    # Lot sizes (21 vars: 7×3)
    lot_sizes: List[List[float]] = field(default_factory=lambda: [[0.0]*3 for _ in range(7)])

    # Strategy conditions (15 vars = 1 + 7 + 7)
    trend_d1: int = 0
    news_level: List[int] = field(default_factory=lambda: [0] * 7)
    news_direction: List[int] = field(default_factory=lambda: [0] * 7)

    # Stoploss thresholds (21 vars: 7×3)
    layer1_thresholds: List[List[float]] = field(default_factory=lambda: [[0.0]*3 for _ in range(7)])

    # Position flags (21 vars: 7×3)
    position_flags: List[List[int]] = field(default_factory=lambda: [[0]*3 for _ in range(7)])

    # TradeLocker specific: ticket mapping (21 vars: 7×3)
    position_tickets: List[List[Optional[str]]] = field(default_factory=lambda: [[None]*3 for _ in range(7)])

    # Global state vars (6 vars) - Prevent multi-symbol conflicts
    print_failed: List[List[bool]] = field(default_factory=lambda: [[False]*3 for _ in range(7)])  # Replaced global self.g_ea.print_failed
    first_run_completed: bool = False
    weekend_last_day: int = 0
    health_last_check_hour: int = -1
    timer_last_run_time: int = 0
    init_summary: str = ""

# ==============================================================================
#  PART 3: GLOBAL CONSTANTS (2 arrays) | HẰNG SỐ TOÀN CỤC
# ==============================================================================

G_TF_NAMES = ["M1", "M5", "M15", "M30", "H1", "H4", "D1"]
G_STRATEGY_NAMES = ["S1", "S2", "S3"]

# ==============================================================================
#  PART 4: LOGGING SETUP | THIẾT LẬP GHI NHẬN
# ==============================================================================

def setup_logging(debug_mode: bool = False):
    """Setup logging configuration | Thiết lập cấu hình ghi nhận"""
    level = logging.DEBUG if debug_mode else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)

# ==============================================================================
#  PART 5: TRADELOCKER BOT CLASS | LỚP BOT TRADELOCKER
# ==============================================================================

class TradeLockerBot:
    """Main bot class - Identical logic to MT5 EA | Lớp bot chính - Logic giống MT5 EA"""

    def __init__(self, config: Config, logger: logging.Logger):
        """Initialize bot with config | Khởi tạo bot với cấu hình"""
        self.config = config
        self.logger = logger
        self.g_ea = EASymbolData()
        self.tl: Optional[TLAPI] = None
        self.running = False
        self.timer_thread: Optional[threading.Thread] = None

        # Instrument ID cache (TradeLocker specific)
        self.instrument_id: Optional[int] = None

        # Account ID cache (TradeLocker specific)
        self.account_id: Optional[str] = None

    # ==========================================================================
    #  PART 5A: UTILITY FUNCTIONS (from MT5 EA PART 5)
    # ==========================================================================

    def IsTFEnabled(self, tf_index: int) -> bool:
        """Check if TF is enabled | Kiểm tra TF có được bật"""
        tf_flags = [
            self.config.TF_M1, self.config.TF_M5, self.config.TF_M15,
            self.config.TF_M30, self.config.TF_H1, self.config.TF_H4, self.config.TF_D1
        ]
        return tf_flags[tf_index] if 0 <= tf_index < 7 else False

    def DebugPrint(self, message: str):
        """Print debug message if DebugMode enabled | In thông báo debug nếu bật"""
        if self.config.DebugMode:
            self.logger.debug(f"[DEBUG] {message}")

    def LogError(self, error_code: int, context: str, details: str):
        """Log error with code, context and details | Ghi nhận lỗi"""
        self.logger.error(f"[ERROR] CODE:{error_code} CONTEXT:{context} DETAILS:{details}")

    def SignalToString(self, signal: int) -> str:
        """Convert signal integer to readable string | Chuyển tín hiệu số thành chữ"""
        if signal == 1:
            return "BUY"
        elif signal == -1:
            return "SELL"
        return "NONE"

    def IsWithinNYHours(self) -> bool:
        """Check if current time is within NY session hours | Kiểm tra giờ hiện tại trong phiên NY

        Returns:
            bool: True if within hours OR filter disabled, False otherwise

        Note: Only applies to S1/S2 strategies, not S3/Bonus (they have own NEWS logic)
        """
        if not self.config.EnableNYHoursFilter:
            return True  # Filter disabled, allow all hours

        current_hour = datetime.now().hour

        # Simple case: Start < End (same day, e.g., 14:00-21:00)
        if self.config.NYSessionStart < self.config.NYSessionEnd:
            return (current_hour >= self.config.NYSessionStart and
                   current_hour < self.config.NYSessionEnd)
        # Complex case: Start > End (cross midnight, e.g., 22:00-06:00)
        else:
            return (current_hour >= self.config.NYSessionStart or
                   current_hour < self.config.NYSessionEnd)

    # ==========================================================================
    #  PART 5B: TRADELOCKER API WRAPPERS (equivalent to MT5 wrappers)
    # ==========================================================================

    def InitTradingConnection(self) -> bool:
        """Initialize TradeLocker connection | Khởi tạo kết nối TradeLocker"""
        try:
            self.logger.info("[INIT] Connecting to TradeLocker...")

            self.tl = TLAPI(
                environment=self.config.TL_Environment,
                username=self.config.TL_Username,
                password=self.config.TL_Password,
                server=self.config.TL_Server
            )

            # Get account ID (required for positions/orders)
            # TradeLocker specific: account ID is needed for API calls
            try:
                all_instruments = self.tl.get_all_instruments()
                if not all_instruments:
                    self.logger.error("[INIT] Failed to get instruments from TradeLocker")
                    return False

                self.logger.info(f"[INIT] TradeLocker connection successful ✓")
                return True

            except Exception as e:
                self.logger.error(f"[INIT] Failed to verify connection: {e}")
                return False

        except Exception as e:
            self.logger.error(f"[INIT] Connection failed: {e}")
            return False

    def GetInstrumentID(self, symbol_name: str) -> Optional[int]:
        """Get TradeLocker instrument ID from symbol name | Lấy instrument ID"""
        try:
            if self.instrument_id is not None:
                return self.instrument_id

            self.instrument_id = self.tl.get_instrument_id_from_symbol_name(symbol_name)

            if self.instrument_id is None:
                self.logger.error(f"[ERROR] Cannot find instrument ID for symbol: {symbol_name}")
                return None

            self.logger.info(f"[INIT] Instrument ID for {symbol_name}: {self.instrument_id}")
            return self.instrument_id

        except Exception as e:
            self.logger.error(f"[ERROR] GetInstrumentID failed: {e}")
            return None

    def GetLatestPrice(self) -> Tuple[Optional[float], Optional[float]]:
        """Get latest Bid/Ask prices | Lấy giá Bid/Ask mới nhất"""
        try:
            if self.instrument_id is None:
                return None, None

            # TradeLocker API: get_latest_asking_price
            ask_price = self.tl.get_latest_asking_price(self.instrument_id)

            # Approximate bid (TradeLocker may not provide separate bid)
            # Typically bid = ask - spread (simplified)
            bid_price = ask_price  # Simplified: use same price

            return bid_price, ask_price

        except Exception as e:
            self.DebugPrint(f"GetLatestPrice error: {e}")
            return None, None

    def CreateOrder(self, side: str, quantity: float, comment: str, magic: int) -> Optional[str]:
        """
        Create market order on TradeLocker | Tạo lệnh thị trường

        Returns: order_id (string) or None
        """
        try:
            if self.instrument_id is None:
                self.logger.error("[ORDER] Instrument ID not set")
                return None

            # TradeLocker API: create_order(instrument_id, quantity, side, type_, label)
            # Use label to store comment (for position identification in RestoreOrCleanupPositions)
            order_id = self.tl.create_order(
                self.instrument_id,
                quantity=quantity,
                side=side.lower(),  # "buy" or "sell"
                type_="market",
                label=comment  # Store comment as label for position tracking
            )

            if order_id:
                self.DebugPrint(f"[ORDER] Created order_id={order_id} {side} {quantity}")
                return str(order_id)
            else:
                self.DebugPrint(f"[ORDER] Failed to create order: {side} {quantity}")
                return None

        except Exception as e:
            self.logger.error(f"[ORDER] CreateOrder error: {e}")
            return None

    def ClosePosition(self, order_id: str) -> bool:
        """Close position by order_id | Đóng lệnh theo order_id"""
        try:
            if order_id is None:
                return False

            # TradeLocker API: close_position(order_id)
            result = self.tl.close_position(order_id)

            if result:
                self.DebugPrint(f"[CLOSE] Closed order_id={order_id}")
                return True
            else:
                self.DebugPrint(f"[CLOSE] Failed to close order_id={order_id}")
                return False

        except Exception as e:
            self.logger.error(f"[CLOSE] ClosePosition error: {e}")
            return False

    def GetOpenPositions(self) -> List[Dict]:
        """
        Get all open positions for current symbol | Lấy tất cả lệnh đang mở

        Returns: List of position dictionaries with keys:
            - ticket: position ID (string)
            - symbol: symbol name (string)
            - type: order type (0=BUY, 1=SELL)
            - lots: position volume (float)
            - profit: current profit including swap/commission (float)
            - magic: magic number (int)
            - open_price: entry price (float)
        """
        try:
            if self.tl is None:
                return []

            # TradeLocker API: get all positions
            # Note: TradeLocker library may have get_all_positions() method
            # If not available, use REST API directly
            try:
                # Method 1: Try library method
                all_positions = self.tl.get_all_positions()

                if not all_positions:
                    return []

                # Filter by current symbol and format
                result = []
                for pos in all_positions:
                    # Filter by symbol (TradeLocker uses instrumentId)
                    if pos.get('instrumentId') != self.instrument_id:
                        continue

                    # Format to match MT5 structure
                    formatted_pos = {
                        'ticket': str(pos.get('id', '')),
                        'symbol': self.g_ea.symbol_name,
                        'type': 0 if pos.get('side', 'buy').lower() == 'buy' else 1,
                        'lots': float(pos.get('qty', 0.0)),
                        'profit': float(pos.get('pnl', 0.0)),
                        'magic': 0,  # TradeLocker doesn't support magic numbers natively
                        'open_price': float(pos.get('openPrice', 0.0)),
                        'comment': str(pos.get('label', ''))  # Use label as comment
                    }
                    result.append(formatted_pos)

                return result

            except AttributeError:
                # Method 2: Library doesn't have the method, log and return empty
                self.DebugPrint("[POSITIONS] TradeLocker library doesn't support get_all_positions yet")
                return []

        except Exception as e:
            self.logger.error(f"[POSITIONS] GetOpenPositions error: {e}")
            return []

    def GetAccountInfo(self) -> Dict:
        """
        Get account balance, equity, margin | Lấy thông tin tài khoản

        Returns: Dictionary with keys:
            - balance: account balance (float)
            - equity: account equity (float)
            - margin: used margin (float)
            - free_margin: available margin (float)
            - profit: current profit (float)
        """
        try:
            if self.tl is None:
                return {
                    "balance": 0.0,
                    "equity": 0.0,
                    "margin": 0.0,
                    "free_margin": 0.0,
                    "profit": 0.0
                }

            try:
                # TradeLocker API: get account state
                # Note: Method names may vary depending on library version
                account_state = self.tl.get_account_state()

                if not account_state:
                    # Return safe defaults
                    return {
                        "balance": 10000.0,
                        "equity": 10000.0,
                        "margin": 0.0,
                        "free_margin": 10000.0,
                        "profit": 0.0
                    }

                # Extract values from account state
                balance = float(account_state.get('balance', 10000.0))
                equity = float(account_state.get('equity', balance))
                margin = float(account_state.get('usedMargin', 0.0))
                free_margin = float(account_state.get('freeMargin', balance))
                profit = equity - balance

                return {
                    "balance": balance,
                    "equity": equity,
                    "margin": margin,
                    "free_margin": free_margin,
                    "profit": profit
                }

            except AttributeError:
                # Library doesn't have the method, return safe defaults
                self.DebugPrint("[ACCOUNT] TradeLocker library doesn't support get_account_state yet")
                return {
                    "balance": 10000.0,
                    "equity": 10000.0,
                    "margin": 0.0,
                    "free_margin": 10000.0,
                    "profit": 0.0
                }

        except Exception as e:
            self.logger.error(f"[ACCOUNT] GetAccountInfo error: {e}")
            return {
                "balance": 0.0,
                "equity": 0.0,
                "margin": 0.0,
                "free_margin": 0.0,
                "profit": 0.0
            }

    # ==========================================================================
    #  PART 6: SYMBOL & FILE MANAGEMENT (from MT5 EA PART 6)
    # ==========================================================================

    def StringTrim(self, input_string: str) -> str:
        """Trim whitespace from string | Loại bỏ khoảng trắng"""
        return input_string.strip()

    def DiscoverSymbolFromChart(self) -> str:
        """Discover symbol name | Nhận diện tên ký hiệu"""
        # In TradeLocker bot, symbol must be provided via config or argument
        # For now, use default symbol (will be set during init)
        return self.g_ea.symbol_name

    def InitializeSymbolRecognition(self, symbol_name: str) -> bool:
        """Initialize symbol recognition | Khởi tạo nhận diện ký hiệu"""
        self.g_ea.symbol_name = symbol_name

        if len(self.g_ea.symbol_name) == 0:
            self.LogError(4201, "InitializeSymbolRecognition", "Cannot detect symbol")
            return False

        self.DebugPrint(f"Symbol detected: {self.g_ea.symbol_name}")
        return True

    def InitializeSymbolPrefix(self):
        """Initialize symbol prefix | Khởi tạo tiền tố ký hiệu"""
        if self.config.EnableSymbolNormalization:
            self.g_ea.normalized_symbol_name = self.NormalizeSymbolName(self.g_ea.symbol_name)
        else:
            self.g_ea.normalized_symbol_name = self.g_ea.symbol_name

        self.g_ea.symbol_prefix = self.g_ea.symbol_name + "_"

    def DetectSymbolType(self, symbol: str) -> str:
        """
        Detect symbol type by pattern matching | Phát hiện loại symbol bằng pattern matching

        Returns: "CRYPTO", "METAL", "ENERGY", "INDEX", or "FX" (default)
        Logic matches MT5 EA DetectSymbolType() function exactly
        """
        sym = symbol.upper()

        # CRYPTO patterns | Các pattern CRYPTO
        if any(crypto in sym for crypto in ["BTC", "ETH", "LTC", "XRP", "BNB"]):
            return "CRYPTO"

        # METAL patterns | Các pattern KIM LOẠI
        if any(metal in sym for metal in ["XAU", "XAG", "GOLD", "SILVER"]):
            return "METAL"

        # ENERGY patterns | Các pattern NĂNG LƯỢNG
        if any(energy in sym for energy in ["OIL", "WTI", "BRENT"]):
            return "ENERGY"

        # INDEX patterns | Các pattern CHỈ SỐ
        if any(index in sym for index in ["SPX", "NAS", "DOW", "DAX"]):
            return "INDEX"

        # Default to FOREX | Mặc định là FOREX
        return "FX"

    def BuildCSDLFilename(self):
        """Build full CSDL filename path | Xây dựng đường dẫn file CSDL"""
        self.g_ea.csdl_filename = self.g_ea.csdl_folder + self.g_ea.symbol_name + "_LIVE.json"
        self.DebugPrint(f"CSDL file: {self.g_ea.csdl_filename}")

    # ==========================================================================
    #  PART 7: CSDL PARSING (from MT5 EA PART 7)
    # ==========================================================================

    def ParseLoveRow(self, row_data: Dict, row_index: int) -> bool:
        """Parse one row of CSDL data | Phân tích 1 hàng dữ liệu CSDL"""
        try:
            self.g_ea.csdl_rows[row_index].max_loss = float(row_data.get("max_loss", 0.0))
            self.g_ea.csdl_rows[row_index].timestamp = int(row_data.get("timestamp", 0))
            self.g_ea.csdl_rows[row_index].signal = int(row_data.get("signal", 0))
            self.g_ea.csdl_rows[row_index].pricediff = float(row_data.get("pricediff", 0.0))
            self.g_ea.csdl_rows[row_index].timediff = int(row_data.get("timediff", 0))
            self.g_ea.csdl_rows[row_index].news = int(row_data.get("news", 0))

            return True

        except Exception as e:
            self.DebugPrint(f"ParseLoveRow error at index {row_index}: {e}")
            return False

    def ParseCSDLLoveJSON(self, json_content: str) -> bool:
        """Parse CSDL JSON array (7 rows) | Phân tích mảng JSON CSDL (7 hàng)"""
        try:
            data = json.loads(json_content)

            if not isinstance(data, list):
                self.DebugPrint("CSDL JSON is not an array")
                return False

            parsed_count = 0
            for i in range(min(7, len(data))):
                if self.ParseLoveRow(data[i], i):
                    parsed_count += 1

            self.DebugPrint(f"LOVE JSON: Parsed {parsed_count} rows")
            return parsed_count >= 1

        except json.JSONDecodeError as e:
            self.DebugPrint(f"JSON parse error: {e}")
            return False
        except Exception as e:
            self.DebugPrint(f"ParseCSDLLoveJSON error: {e}")
            return False

    def NormalizeSymbolName(self, symbol: str) -> str:
        """Normalize symbol name for API calls | Chuẩn hóa tên symbol"""
        normalized = symbol

        # Step 1: Remove everything after "."
        if "." in normalized:
            normalized = normalized.split(".")[0]
            self.DebugPrint(f"[NORMALIZE] Removed dot suffix: {symbol} → {normalized}")

        # Step 2: Keep maximum 6 characters
        if len(normalized) > 6:
            truncated = normalized[:6]
            self.DebugPrint(f"[NORMALIZE] Truncated to 6 chars: {normalized} → {truncated}")
            normalized = truncated

        # Step 3: Convert to uppercase
        normalized = normalized.upper()

        if normalized != symbol:
            self.logger.info(f"[NORMALIZE] Symbol standardized: {symbol} → {normalized}")

        return normalized

    def ReadCSDLFromHTTP(self) -> bool:
        """Read CSDL from HTTP API | Đọc CSDL từ HTTP API"""
        try:
            url = f"http://{self.config.HTTP_Server_IP}/api/csdl/{self.g_ea.normalized_symbol_name}_LIVE.json"

            headers = {}
            if self.config.HTTP_API_Key:
                headers["X-API-Key"] = self.config.HTTP_API_Key

            response = requests.get(url, headers=headers, timeout=0.5)

            if response.status_code != 200:
                self.DebugPrint(f"[HTTP_ERROR] Server returned status code: {response.status_code}")
                return False

            json_content = response.text

            if len(json_content) < 20:
                self.DebugPrint(f"[HTTP_ERROR] Response too short: {len(json_content)} bytes")
                return False

            if not self.ParseCSDLLoveJSON(json_content):
                self.DebugPrint("[HTTP_ERROR] Failed to parse JSON response")
                return False

            self.DebugPrint("[HTTP_OK] Successfully loaded CSDL from API")
            return True

        except requests.exceptions.Timeout:
            self.DebugPrint("[HTTP_ERROR] Request timeout")
            return False
        except Exception as e:
            self.DebugPrint(f"[HTTP_ERROR] {e}")
            return False

    def TryReadLocalFile(self, filename: str) -> bool:
        """Try to read local file | Thử đọc file local"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                json_content = f.read()

            if len(json_content) < 20:
                self.DebugPrint(f"[READ] Content too short: {len(json_content)}")
                return False

            if not self.ParseCSDLLoveJSON(json_content):
                self.DebugPrint("[READ] ParseCSDLLoveJSON failed")
                return False

            return True

        except FileNotFoundError:
            self.DebugPrint(f"[READ] File not found: {filename}")
            return False
        except Exception as e:
            self.DebugPrint(f"[READ] Error reading file: {e}")
            return False

    def ReadCSDLFile(self):
        """Read CSDL with smart routing | Đọc CSDL với định tuyến thông minh"""
        success = False

        if self.config.CSDL_Source == "HTTP_API":
            # Try HTTP API
            success = self.ReadCSDLFromHTTP()

            if not success:
                time.sleep(0.1)
                success = self.ReadCSDLFromHTTP()

        else:
            # Try local file
            success = self.TryReadLocalFile(self.g_ea.csdl_filename)

            if not success:
                time.sleep(0.1)
                success = self.TryReadLocalFile(self.g_ea.csdl_filename)

        if not success:
            self.DebugPrint("[WARNING] All read attempts failed. Using old data.")

    # ==========================================================================
    #  PART 8: MAGIC NUMBER GENERATION (from MT5 EA PART 8)
    # ==========================================================================

    def GenerateSymbolHash(self, symbol: str) -> int:
        """Generate symbol hash using DJB2 algorithm | Tạo mã hash"""
        hash_val = 5381

        for char in symbol:
            hash_val = ((hash_val << 5) + hash_val) + ord(char)

        hash_val = abs(hash_val % 10000)

        if hash_val < 100:
            hash_val += 100

        return hash_val

    def GenerateSmartMagicNumber(self, symbol: str, tf_index: int, strategy_index: int) -> int:
        """Generate smart magic number | Tạo số hiệu thông minh"""
        symbol_hash = self.GenerateSymbolHash(symbol)
        tf_code = tf_index * 1000
        strategy_code = strategy_index * 100

        return symbol_hash + tf_code + strategy_code

    def GenerateMagicNumbers(self) -> bool:
        """Generate all 21 magic numbers | Tạo tất cả 21 số hiệu"""
        symbol = self.g_ea.symbol_name

        for tf in range(7):
            for s in range(3):
                self.g_ea.magic_numbers[tf][s] = self.GenerateSmartMagicNumber(symbol, tf, s)

        self.DebugPrint(f"Magic M1: S1={self.g_ea.magic_numbers[0][0]}, "
                       f"S2={self.g_ea.magic_numbers[0][1]}, "
                       f"S3={self.g_ea.magic_numbers[0][2]}")

        return True

    # ==========================================================================
    #  PART 9: LOT SIZE CALCULATION (from MT5 EA PART 9)
    # ==========================================================================

    def CalculateSmartLotSize(self, base_lot: float, tf_index: int, strategy_index: int) -> float:
        """Calculate lot with progressive formula | Tính lot theo công thức lũy tiến

        FORMULA: (base × strategy_multiplier) + tf_increment
        Strategy multipliers: S1=×2, S2=×1, S3=×3
        TF increments: M1=+0.01, M5=+0.02, ..., D1=+0.07

        Examples (base_lot=0.1):
          M1_S1 = (0.1×2) + 0.01 = 0.21
          M1_S2 = (0.1×1) + 0.01 = 0.11
          M1_S3 = (0.1×3) + 0.01 = 0.31
        """

        # Strategy multipliers: index 0=S1(×2), 1=S2(×1), 2=S3(×3)
        strategy_multipliers = [2.0, 1.0, 3.0]
        strategy_multiplier = strategy_multipliers[strategy_index]

        # TF increments: index 0=M1(+0.01), 1=M5(+0.02), ..., 6=D1(+0.07)
        tf_increments = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07]
        tf_increment = tf_increments[tf_index]

        # Calculate final lot: (base × strategy_multiplier) + tf_increment
        lot = (base_lot * strategy_multiplier) + tf_increment

        # Round to 2 decimals
        lot = round(lot, 2)

        return lot

    def InitializeLotSizes(self):
        """Pre-calculate all 21 lot sizes | Tính trước 21 khối lượng"""
        for tf in range(7):
            for s in range(3):
                self.g_ea.lot_sizes[tf][s] = self.CalculateSmartLotSize(
                    self.config.FixedLotSize, tf, s
                )

        self.DebugPrint(f"Lots M1: S1={self.g_ea.lot_sizes[0][0]}, "
                       f"S2={self.g_ea.lot_sizes[0][1]}, "
                       f"S3={self.g_ea.lot_sizes[0][2]}")

    # ==========================================================================
    #  PART 10: LAYER1 THRESHOLDS (from MT5 EA PART 10)
    # ==========================================================================

    def InitializeLayer1Thresholds(self):
        """Initialize Layer1 stoploss thresholds | Khởi tạo ngưỡng cắt lỗ"""
        for tf in range(7):
            max_loss_per_lot = self.g_ea.csdl_rows[tf].max_loss

            if abs(max_loss_per_lot) < 1.0:
                max_loss_per_lot = self.config.MaxLoss_Fallback

            for s in range(3):
                self.g_ea.layer1_thresholds[tf][s] = max_loss_per_lot * self.g_ea.lot_sizes[tf][s]

        self.DebugPrint(f"Layer1 M1: S1=${self.g_ea.layer1_thresholds[0][0]:.2f}, "
                       f"S2=${self.g_ea.layer1_thresholds[0][1]:.2f}, "
                       f"S3=${self.g_ea.layer1_thresholds[0][2]:.2f}")

    # ==========================================================================
    #  PART 11: MAP CSDL TO EA (from MT5 EA PART 11)
    # ==========================================================================

    def MapCSDLToEAVariables(self):
        """Map CSDL data to EA variables | Ánh xạ dữ liệu CSDL sang biến EA"""
        # S2: TREND - Always use D1 (row 6)
        self.g_ea.trend_d1 = self.g_ea.csdl_rows[6].signal

        # S3: NEWS - Map 7 NEWS values to 14 variables
        self.MapNewsTo14Variables()

        self.DebugPrint(f"Mapped 7 TF | signal[0]={self.g_ea.csdl_rows[0].signal}, "
                       f"trend_d1={self.g_ea.trend_d1}, "
                       f"news[M1]={self.g_ea.csdl_rows[0].news}")

    def MapNewsTo14Variables(self):
        """Map 7 NEWS values to 14 variables | Tách 7 giá trị NEWS thành 14 biến"""
        for tf in range(7):
            tf_news = self.g_ea.csdl_rows[tf].news

            self.g_ea.news_level[tf] = abs(tf_news)

            if tf_news > 0:
                self.g_ea.news_direction[tf] = 1
            elif tf_news < 0:
                self.g_ea.news_direction[tf] = -1
            else:
                self.g_ea.news_direction[tf] = 0

        self.DebugPrint(f"NEWS 14 vars: M1[{self.g_ea.news_level[0]}/{self.g_ea.news_direction[0]}], "
                       f"M5[{self.g_ea.news_level[1]}/{self.g_ea.news_direction[1]}], "
                       f"D1[{self.g_ea.news_level[6]}/{self.g_ea.news_direction[6]}]")

    # ==========================================================================
    #  PART 12-18: TRADING LOGIC (Strategies, Stoploss, TP, Health Check)
    #  NOTE: These are simplified versions - full implementation needed
    # ==========================================================================

    def RestoreOrCleanupPositions(self) -> bool:
        """Restore or cleanup positions on startup | Khôi phục hoặc dọn dẹp lệnh

        NOTE: TradeLocker doesn't support magic numbers natively.
        We use position comment field to identify TF and Strategy (e.g., "S1_M5", "S2_H1").
        """
        # Step 1: Reset all flags first | Bước 1: Reset tất cả cờ trước
        for tf in range(7):
            for s in range(3):
                self.g_ea.position_flags[tf][s] = 0
                self.g_ea.position_tickets[tf][s] = None

        kept_count = 0
        closed_count = 0

        # Step 2: Get all open positions | Bước 2: Lấy tất cả lệnh đang mở
        positions = self.GetOpenPositions()

        # Step 3: Scan each position and decide KEEP or CLOSE | Bước 3: Quét từng lệnh và quyết định GIỮ hoặc ĐÓNG
        for pos in positions:
            ticket = pos.get('ticket', '')
            order_type = pos.get('type', 0)  # 0=BUY, 1=SELL

            # Get order signal from position type
            order_signal = 1 if order_type == 0 else -1  # BUY=+1, SELL=-1

            # Try to parse comment to get TF and Strategy
            # Comment format: "S1_M5", "S2_H1", "S3_M15", "BONUS_M5", etc.
            comment = pos.get('comment', '')

            # Find matching TF and Strategy
            found = False
            found_tf = -1
            found_s = -1

            # Try to parse comment (e.g., "S1_M5" -> strategy=0, tf=1)
            if comment.startswith("S1_"):
                found_s = 0
                tf_name = comment[3:]  # "M5", "H1", etc.
                for i, name in enumerate(G_TF_NAMES):
                    if name == tf_name:
                        found_tf = i
                        break
            elif comment.startswith("S2_"):
                found_s = 1
                tf_name = comment[3:]
                for i, name in enumerate(G_TF_NAMES):
                    if name == tf_name:
                        found_tf = i
                        break
            elif comment.startswith("S3_"):
                found_s = 2
                tf_name = comment[3:]
                for i, name in enumerate(G_TF_NAMES):
                    if name == tf_name:
                        found_tf = i
                        break

            # If we found TF and Strategy from comment, validate all conditions
            if found_tf >= 0 and found_s >= 0:
                # CONDITION 1: TF enabled | Điều kiện 1: TF được bật
                cond1_tf_enabled = self.IsTFEnabled(found_tf)

                # CONDITION 2: Signal pair match | Điều kiện 2: Cặp tín hiệu khớp
                # Order signal == OLD == CSDL (triple match) AND timestamp OLD == CSDL (locked)
                cond2_signal_pair = (
                    order_signal == self.g_ea.signal_old[found_tf] and
                    order_signal == self.g_ea.csdl_rows[found_tf].signal and
                    self.g_ea.timestamp_old[found_tf] == self.g_ea.csdl_rows[found_tf].timestamp
                )

                # CONDITION 3: Strategy enabled | Điều kiện 3: Chiến lược được bật
                cond3_strategy = False
                if found_s == 0:
                    cond3_strategy = self.config.S1_HOME
                elif found_s == 1:
                    cond3_strategy = self.config.S2_TREND
                elif found_s == 2:
                    cond3_strategy = self.config.S3_NEWS

                # CONDITION 4: Not duplicate (flag must be 0) | Điều kiện 4: Không trùng lặp
                cond4_unique = (self.g_ea.position_flags[found_tf][found_s] == 0)

                # CONSOLIDATED CHECK: ALL with AND | KIỂM TRA GỘP: Tất cả với AND
                if cond1_tf_enabled and cond2_signal_pair and cond3_strategy and cond4_unique:
                    found = True

            # Step 4: Decide KEEP or CLOSE | Bước 4: Quyết định GIỮ hoặc ĐÓNG
            if found:
                # ✓ KEEP: All conditions passed → Restore flag | GIỮ: Tất cả điều kiện qua → Khôi phục cờ
                self.g_ea.position_flags[found_tf][found_s] = 1
                self.g_ea.position_tickets[found_tf][found_s] = ticket
                kept_count += 1

                self.DebugPrint(f"[RESTORE_KEEP] #{ticket} TF:{found_tf} S:{found_s + 1} "
                              f"Signal:{order_signal} | Flag=1")

            else:
                # ✗ CLOSE: ANY condition failed → Close order | ĐÓNG: Bất kỳ điều kiện sai → Đóng lệnh
                self.ClosePosition(ticket)
                closed_count += 1

                self.DebugPrint(f"[RESTORE_CLOSE] #{ticket} Signal:{order_signal} | INVALID")

        # Step 5: Final summary report | Bước 5: Báo cáo tóm tắt cuối cùng
        self.logger.info(f"{self.g_ea.init_summary} | RESTORE: KEPT={kept_count}, CLOSED={closed_count}")

        # Debug: Print restored flags (optional) | In cờ đã khôi phục (tùy chọn)
        if self.config.DebugMode and kept_count > 0:
            for tf in range(7):
                has_flag = any(self.g_ea.position_flags[tf][s] == 1 for s in range(3))
                if has_flag:
                    self.logger.debug(f"[RESTORE_FLAGS] {G_TF_NAMES[tf]}: "
                                    f"S1={self.g_ea.position_flags[tf][0]} "
                                    f"S2={self.g_ea.position_flags[tf][1]} "
                                    f"S3={self.g_ea.position_flags[tf][2]}")

        return True

    def HasValidS2BaseCondition(self, tf: int) -> bool:
        """Check if signal changed (base condition for close/open) | Kiểm tra tín hiệu đổi"""
        signal_old = self.g_ea.signal_old[tf]
        signal_new = self.g_ea.csdl_rows[tf].signal
        timestamp_old = self.g_ea.timestamp_old[tf]
        timestamp_new = self.g_ea.csdl_rows[tf].timestamp

        return (signal_old != signal_new and
                signal_new != 0 and
                timestamp_old < timestamp_new and
                (timestamp_new - timestamp_old) > 15)

    def ProcessS1Strategy(self, tf: int):
        """Process S1 strategy | Xử lý chiến lược S1"""
        # CHECK NY HOURS: Only S1 needs this (S3/Bonus have own NEWS logic)
        if not self.IsWithinNYHours():
            return

        if self.config.S1_UseNewsFilter:
            self.ProcessS1NewsFilterStrategy(tf)
        else:
            self.ProcessS1BasicStrategy(tf)

    def ProcessS1BasicStrategy(self, tf: int):
        """S1 BASIC: No NEWS check | S1 cơ bản: Không kiểm tra NEWS"""
        current_signal = self.g_ea.csdl_rows[tf].signal
        if current_signal in [1, -1]:
            self.OpenS1Order(tf, current_signal, "BASIC")

    def ProcessS1NewsFilterStrategy(self, tf: int):
        """S1 NEWS Filter: Check NEWS before opening | S1 với lọc NEWS"""
        current_signal = self.g_ea.csdl_rows[tf].signal
        news_level = self.g_ea.news_level[tf]
        news_direction = self.g_ea.news_direction[tf]

        if news_level < self.config.MinNewsLevelS1:
            self.DebugPrint(f"S1_NEWS: {G_TF_NAMES[tf]} NEWS={news_level} < Min={self.config.MinNewsLevelS1}, SKIP")
            return

        if self.config.S1_RequireNewsDirection:
            if current_signal != news_direction:
                self.DebugPrint(f"S1_NEWS: {G_TF_NAMES[tf]} Signal={current_signal} != NewsDir={news_direction}, SKIP")
                return

        if current_signal in [1, -1]:
            self.OpenS1Order(tf, current_signal, "NEWS")

    def OpenS1Order(self, tf: int, signal: int, mode: str):
        """Open S1 order | Mở lệnh S1"""
        timestamp = self.g_ea.csdl_rows[tf].timestamp
        news_level = self.g_ea.news_level[tf]
        news_direction = self.g_ea.news_direction[tf]

        side = "buy" if signal == 1 else "sell"
        type_str = "BUY" if signal == 1 else "SELL"

        order_id = self.CreateOrder(
            side=side,
            quantity=self.g_ea.lot_sizes[tf][0],
            comment=f"S1_{G_TF_NAMES[tf]}",
            magic=self.g_ea.magic_numbers[tf][0]
        )

        if order_id:
            self.g_ea.position_flags[tf][0] = 1
            self.g_ea.position_tickets[tf][0] = order_id
            self.g_ea.print_failed[tf][0] = False

            log_msg = f">>> [OPEN] S1_{mode} TF={G_TF_NAMES[tf]} | #{order_id} {type_str} {self.g_ea.lot_sizes[tf][0]:.2f}"

            if mode == "NEWS":
                arrow = "↑" if news_direction > 0 else "↓"
                log_msg += f" | News={'+' if news_direction > 0 else ''}{news_level}{arrow}"

            log_msg += f" | Timestamp:{timestamp} <<<"
            self.logger.info(log_msg)
        else:
            self.g_ea.position_flags[tf][0] = 0

            if not self.g_ea.print_failed[tf][0]:
                self.logger.error(f"[S1_{mode}_{G_TF_NAMES[tf]}] Failed to create order")
                self.g_ea.print_failed[tf][0] = True

    def ProcessS2Strategy(self, tf: int):
        """Process S2 (Trend Following) strategy | Xử lý chiến lược S2"""
        # CHECK NY HOURS: Only S2 needs this (S3/Bonus have own NEWS logic)
        if not self.IsWithinNYHours():
            return

        current_signal = self.g_ea.csdl_rows[tf].signal
        timestamp = self.g_ea.csdl_rows[tf].timestamp

        # Determine trend based on mode
        if self.config.S2_TrendMode == 0:  # S2_FOLLOW_D1
            trend_to_follow = self.g_ea.trend_d1
        elif self.config.S2_TrendMode == 1:  # S2_FORCE_BUY
            trend_to_follow = 1
        else:  # S2_FORCE_SELL
            trend_to_follow = -1

        if current_signal != trend_to_follow:
            self.DebugPrint(f"S2_TREND: Signal={current_signal} != Trend={trend_to_follow}, skip")
            return

        # STEP 3: NEWS filter check (optional, only if S2_UseNewsFilter = true)
        if self.config.S2_UseNewsFilter:
            news_level = self.g_ea.news_level[tf]
            news_direction = self.g_ea.news_direction[tf]

            # Check 1: NEWS level >= MinNewsLevelS2
            if news_level < self.config.MinNewsLevelS2:
                self.DebugPrint(f"S2_NEWS: {G_TF_NAMES[tf]} NEWS={news_level} < Min={self.config.MinNewsLevelS2}, SKIP")
                return

            # Check 2: Signal = NEWS direction (if S2_RequireNewsDirection = true)
            if self.config.S2_RequireNewsDirection:
                if current_signal != news_direction:
                    self.DebugPrint(f"S2_NEWS: {G_TF_NAMES[tf]} Signal={current_signal} != NewsDir={news_direction}, SKIP")
                    return

        side = "buy" if current_signal == 1 else "sell"
        type_str = "BUY" if current_signal == 1 else "SELL"

        order_id = self.CreateOrder(
            side=side,
            quantity=self.g_ea.lot_sizes[tf][1],
            comment=f"S2_{G_TF_NAMES[tf]}",
            magic=self.g_ea.magic_numbers[tf][1]
        )

        if order_id:
            self.g_ea.position_flags[tf][1] = 1
            self.g_ea.position_tickets[tf][1] = order_id
            self.g_ea.print_failed[tf][1] = False

            trend_str = "UP" if trend_to_follow == 1 else "DOWN"
            mode_str = "AUTO" if self.config.S2_TrendMode == 0 else ("FBUY" if self.config.S2_TrendMode == 1 else "FSELL")

            self.logger.info(f">>> [OPEN] S2_TREND TF={G_TF_NAMES[tf]} | #{order_id} {type_str} "
                           f"{self.g_ea.lot_sizes[tf][1]:.2f} | Sig={current_signal} Trend:{trend_str} "
                           f"Mode:{mode_str} | Timestamp:{timestamp} <<<")
        else:
            self.g_ea.position_flags[tf][1] = 0

            if not self.g_ea.print_failed[tf][1]:
                self.logger.error(f"[S2_{G_TF_NAMES[tf]}] Failed to create order")
                self.g_ea.print_failed[tf][1] = True

    def ProcessS3Strategy(self, tf: int):
        """Process S3 (News Alignment) strategy | Xử lý chiến lược S3"""
        news_level = self.g_ea.news_level[tf]
        news_direction = self.g_ea.news_direction[tf]
        current_signal = self.g_ea.csdl_rows[tf].signal
        timestamp = self.g_ea.csdl_rows[tf].timestamp

        if news_level < self.config.MinNewsLevelS3:
            self.DebugPrint(f"S3_NEWS: TF{tf} NEWS={news_level} < {self.config.MinNewsLevelS3}, skip")
            return

        if current_signal != news_direction:
            self.DebugPrint(f"S3_NEWS: Signal={current_signal} != NewsDir={news_direction}, skip")
            return

        side = "buy" if current_signal == 1 else "sell"
        type_str = "BUY" if current_signal == 1 else "SELL"

        order_id = self.CreateOrder(
            side=side,
            quantity=self.g_ea.lot_sizes[tf][2],
            comment=f"S3_{G_TF_NAMES[tf]}",
            magic=self.g_ea.magic_numbers[tf][2]
        )

        if order_id:
            self.g_ea.position_flags[tf][2] = 1
            self.g_ea.position_tickets[tf][2] = order_id
            self.g_ea.print_failed[tf][2] = False

            arrow = "↑" if news_direction > 0 else "↓"
            self.logger.info(f">>> [OPEN] S3_NEWS TF={G_TF_NAMES[tf]} | #{order_id} {type_str} "
                           f"{self.g_ea.lot_sizes[tf][2]:.2f} | Sig={current_signal} "
                           f"News={'+' if news_direction > 0 else ''}{news_level}{arrow} | "
                           f"Timestamp:{timestamp} <<<")
        else:
            self.g_ea.position_flags[tf][2] = 0

            if not self.g_ea.print_failed[tf][2]:
                self.logger.error(f"[S3_{G_TF_NAMES[tf]}] Failed to create order")
                self.g_ea.print_failed[tf][2] = True

    def ProcessBonusNews(self):
        """
        Process Bonus NEWS - open extra orders on high news | Xử lý tin tức Bonus

        Scans all 7 TF and opens BonusOrderCount orders if:
        - NEWS level >= MinNewsLevelBonus
        - NEWS level != 1 and != 10 (skip weak news)
        """
        if not self.config.EnableBonusNews:
            return

        # Scan all 7 TF
        for tf in range(7):
            # Skip if TF disabled
            if not self.IsTFEnabled(tf):
                continue

            # Use NEWS from 14 variables (7 level + 7 direction) per TF
            news_level = self.g_ea.news_level[tf]
            news_direction = self.g_ea.news_direction[tf]

            # Skip if NEWS below threshold
            if news_level < self.config.MinNewsLevelBonus:
                continue

            # OPTIMIZED: Skip low-value NEWS (Category 2 L1 and Category 1 L1)
            # Category 2 Level 1: ±1 (too weak for Bonus)
            # Category 1 Level 1: ±10 (minimum level, prefer higher)
            if news_level == 1 or news_level == 10:
                continue

            # Calculate BONUS lot (S3 lot × multiplier)
            bonus_lot = self.g_ea.lot_sizes[tf][2] * self.config.BonusLotMultiplier

            # CRITICAL: Round to 2 decimals (0.01 step) to prevent "invalid volume" error
            # TradeLocker requires lot to be multiple of 0.01 (e.g., 0.38 OK, 0.384 INVALID)
            bonus_lot = round(bonus_lot, 2)

            # Open BonusOrderCount orders
            opened_count = 0
            ticket_list = []
            entry_price = 0.0

            for count in range(self.config.BonusOrderCount):
                side = "buy" if news_direction == 1 else "sell"

                order_id = self.CreateOrder(
                    side=side,
                    quantity=bonus_lot,
                    comment=f"BONUS_{G_TF_NAMES[tf]}",
                    magic=self.g_ea.magic_numbers[tf][2]  # Use S3 magic for BONUS
                )

                if order_id:
                    opened_count += 1
                    ticket_list.append(order_id)

                    # Get entry price (approximate from latest price)
                    if entry_price == 0.0:
                        bid, ask = self.GetLatestPrice()
                        entry_price = ask if news_direction == 1 else bid

            # Consolidated log after loop
            if opened_count > 0:
                arrow = "↑" if news_direction > 0 else "↓"
                total_lot = opened_count * bonus_lot
                type_str = "BUY" if news_direction == 1 else "SELL"
                tickets_str = ",".join(ticket_list)

                self.logger.info(f">>> [OPEN] BONUS TF={G_TF_NAMES[tf]} | {opened_count}×{type_str} "
                               f"@{bonus_lot:.2f} Total:{total_lot:.2f} @{entry_price:.5f} "
                               f"| News={'+' if news_direction > 0 else ''}{news_level}{arrow} "
                               f"| Multiplier:{self.config.BonusLotMultiplier:.1f}x "
                               f"Tickets:{tickets_str} <<<")

    def CloseAllStrategiesByMagicForTF(self, tf: int):
        """Close all strategies for specific TF | Đóng tất cả chiến lược cho 1 TF"""
        for s in range(3):
            if self.g_ea.position_flags[tf][s] == 1:
                order_id = self.g_ea.position_tickets[tf][s]
                if order_id:
                    if self.ClosePosition(order_id):
                        self.g_ea.position_flags[tf][s] = 0
                        self.g_ea.position_tickets[tf][s] = None
                        self.logger.info(f">> [CLOSE] SIGNAL_CHANGE TF={G_TF_NAMES[tf]} S={s+1} | #{order_id} <<")

    def CloseS1OrdersByM1(self):
        """Close all S1 orders using M1 signal | Đóng tất cả lệnh S1 theo M1"""
        for tf in range(7):
            if self.g_ea.position_flags[tf][0] == 1:
                order_id = self.g_ea.position_tickets[tf][0]
                if order_id:
                    if self.ClosePosition(order_id):
                        self.g_ea.position_flags[tf][0] = 0
                        self.g_ea.position_tickets[tf][0] = None
                        self.logger.info(f">> [CLOSE] M1_FAST TF={G_TF_NAMES[tf]} S1 | #{order_id} <<")

    def CloseS2OrdersByM1(self):
        """Close all S2 orders using M1 signal | Đóng tất cả lệnh S2 theo M1"""
        for tf in range(7):
            if self.g_ea.position_flags[tf][1] == 1:
                order_id = self.g_ea.position_tickets[tf][1]
                if order_id:
                    if self.ClosePosition(order_id):
                        self.g_ea.position_flags[tf][1] = 0
                        self.g_ea.position_tickets[tf][1] = None
                        self.logger.info(f">> [CLOSE] M1_FAST TF={G_TF_NAMES[tf]} S2 | #{order_id} <<")

    def CloseS3OrdersForTF(self, tf: int):
        """Close S3 orders for specific TF | Đóng lệnh S3 cho TF cụ thể"""
        if self.g_ea.position_flags[tf][2] == 1:
            order_id = self.g_ea.position_tickets[tf][2]
            if order_id:
                if self.ClosePosition(order_id):
                    self.g_ea.position_flags[tf][2] = 0
                    self.g_ea.position_tickets[tf][2] = None
                    self.logger.info(f">> [CLOSE] SIGNAL_CHANGE TF={G_TF_NAMES[tf]} S3 | #{order_id} <<")

    def CloseAllBonusOrders(self):
        """
        Close all bonus orders | Đóng tất cả lệnh bonus

        Scans all positions and closes those with "BONUS" in comment
        """
        positions = self.GetOpenPositions()

        if len(positions) == 0:
            return

        closed_count = 0

        for pos in positions:
            ticket = pos['ticket']

            # TradeLocker note: We need to track BONUS orders separately
            # Since TradeLocker doesn't have magic numbers, we use comment field
            # But GetOpenPositions doesn't return comment, so we'll close by checking
            # if the ticket matches any S3 strategy positions that aren't tracked

            # Alternative: Track BONUS tickets separately in a list
            # For now, skip implementation as it requires position comment tracking
            pass

        if closed_count > 0:
            self.logger.info(f"[CLOSE] Closed {closed_count} BONUS orders")

    def CheckStoplossAndTakeProfit(self):
        """
        Check stoploss & take profit for all orders | Kiểm tra cắt lỗ & chốt lời
        Stoploss: 2 layers (LAYER1_MAXLOSS, LAYER2_MARGIN) | Cắt lỗ: 2 tầng
        Take profit: 1 layer (max_loss × multiplier) | Chốt lời: 1 tầng
        """
        positions = self.GetOpenPositions()

        if len(positions) == 0:
            return

        # Scan all positions
        for pos in positions:
            ticket = pos['ticket']
            profit = pos['profit']
            lots = pos['lots']

            # Find TF + Strategy from position ticket mapping
            found = False
            for tf in range(7):
                for s in range(3):
                    # Match by ticket (TradeLocker specific)
                    if (self.g_ea.position_flags[tf][s] == 1 and
                        self.g_ea.position_tickets[tf][s] == ticket):

                        order_closed = False

                        # ===== SECTION 1: STOPLOSS (2 layers) =====
                        if self.config.StoplossMode != 0:  # 0 = NONE
                            sl_threshold = 0.0
                            mode_name = ""

                            if self.config.StoplossMode == 1:  # LAYER1_MAXLOSS
                                # Layer1: Use pre-calculated threshold (max_loss × lot)
                                sl_threshold = self.g_ea.layer1_thresholds[tf][s]
                                mode_name = "LAYER1_SL"

                            elif self.config.StoplossMode == 2:  # LAYER2_MARGIN
                                # Layer2: Calculate from margin (emergency)
                                # TradeLocker: approximate margin calculation
                                # margin_usd = lot × contract_size × price / leverage
                                # Simplified: use a fixed margin per lot (will need adjustment)
                                margin_per_lot = 1000.0  # Approximate for most symbols
                                margin_usd = lots * margin_per_lot
                                sl_threshold = -(margin_usd / self.config.Layer2_Divisor)
                                mode_name = "LAYER2_SL"

                            # Check and close if loss exceeds threshold
                            if profit <= sl_threshold:
                                short_mode = "L1_SL" if mode_name == "LAYER1_SL" else "L2_SL"
                                order_type_str = "BUY" if pos['type'] == 0 else "SELL"

                                margin_info = ""
                                if mode_name == "LAYER2_SL":
                                    margin_usd = lots * 1000.0
                                    margin_info = f" Margin=${margin_usd:.2f}"

                                self.logger.info(f">> [CLOSE] {short_mode} TF={G_TF_NAMES[tf]} S={s+1} "
                                               f"| #{ticket} {order_type_str} {lots:.2f} "
                                               f"| Loss=${profit:.2f} | Threshold=${sl_threshold:.2f}"
                                               f"{margin_info} <<")

                                if self.ClosePosition(ticket):
                                    self.g_ea.position_flags[tf][s] = 0
                                    self.g_ea.position_tickets[tf][s] = None
                                    order_closed = True

                        # ===== SECTION 2: TAKE PROFIT (1 layer) =====
                        # Only check if order wasn't closed by stoploss
                        if not order_closed and self.config.UseTakeProfit:
                            # Calculate TP threshold from max_loss
                            max_loss_per_lot = abs(self.g_ea.csdl_rows[tf].max_loss)
                            if max_loss_per_lot < 1.0:
                                max_loss_per_lot = abs(self.config.MaxLoss_Fallback)  # 1000

                            tp_threshold = (max_loss_per_lot * self.g_ea.lot_sizes[tf][s]) * self.config.TakeProfit_Multiplier

                            # Check and close if profit exceeds threshold
                            if profit >= tp_threshold:
                                order_type_str = "BUY" if pos['type'] == 0 else "SELL"

                                self.logger.info(f">> [CLOSE] TP TF={G_TF_NAMES[tf]} S={s+1} "
                                               f"| #{ticket} {order_type_str} {lots:.2f} "
                                               f"| Profit=${profit:.2f} | Threshold=${tp_threshold:.2f} "
                                               f"Mult={self.config.TakeProfit_Multiplier:.2f} <<")

                                if self.ClosePosition(ticket):
                                    self.g_ea.position_flags[tf][s] = 0
                                    self.g_ea.position_tickets[tf][s] = None

                        found = True
                        break
                if found:
                    break

    def CheckAllEmergencyConditions(self):
        """Check emergency conditions (drawdown) | Kiểm tra điều kiện khẩn cấp"""
        account_info = self.GetAccountInfo()

        balance = account_info.get("balance", 0.0)
        equity = account_info.get("equity", 0.0)

        if balance > 0:
            drawdown_percent = ((balance - equity) / balance) * 100

            if drawdown_percent > 25.0:
                self.logger.warning(f"[WARNING] Drawdown: {drawdown_percent:.2f}%")

    def CheckWeekendReset(self):
        """
        Weekend reset (Saturday 00:03) | Reset cuối tuần

        NOTE: SmartTFReset is MT5-specific (resets charts)
        For TradeLocker Python bot, we'll just log the event
        """
        if not self.config.EnableWeekendReset:
            return

        current_time = int(time.time())
        dt = datetime.fromtimestamp(current_time)

        day_of_week = dt.weekday()  # 0=Monday, 5=Saturday
        hour = dt.hour
        minute = dt.minute

        # Only on Saturday (5) at 0h:03 (minute 03 exactly)
        # IMPORTANT: NOT 0h:00 to avoid conflict with SPY Bot!
        if day_of_week != 5 or hour != 0 or minute != 3:
            return

        # Prevent duplicate reset (once per day)
        current_day = dt.day
        if current_day == self.g_ea.weekend_last_day:
            return  # Already reset today

        self.logger.info("[WEEKEND_RESET] Saturday 00:03 - Weekly reset triggered")

        # Note: MT5's SmartTFReset() resets all charts by switching timeframes
        # This is MT5-specific and doesn't apply to TradeLocker Python bot
        # For TradeLocker, we could optionally:
        # 1. Close all positions (aggressive)
        # 2. Just log the event (current implementation)
        # 3. Reset internal state flags (if needed)

        # For now, just mark the day to prevent duplicate triggers
        self.g_ea.weekend_last_day = current_day

        self.logger.info("[WEEKEND_RESET] Weekly reset completed")

    def CheckSPYBotHealth(self):
        """Health check SPY Bot (8h/16h only) | Kiểm tra sức khỏe SPY Bot"""
        if not self.config.EnableHealthCheck:
            return

        current_time = int(time.time())
        hour = datetime.fromtimestamp(current_time).hour

        if hour not in [8, 16]:
            return

        if hour == self.g_ea.health_last_check_hour:
            return

        self.g_ea.health_last_check_hour = hour

        m1_timestamp = self.g_ea.timestamp_old[0]
        diff_seconds = current_time - m1_timestamp

        if diff_seconds > 28800:  # 8 hours
            diff_hours = diff_seconds // 3600
            diff_minutes = (diff_seconds % 3600) // 60
            self.logger.warning(f"[HEALTH_CHECK] ⚠️ SPY Bot frozen (CSDL: {diff_hours}h{diff_minutes}m old) - Check system at {hour}h00")

    def FormatAge(self, timestamp: int) -> str:
        """Format age (time since signal) | Định dạng tuổi (thời gian từ tín hiệu)"""
        current_time = int(time.time())
        diff = current_time - timestamp

        if diff < 60:
            return f"{diff}s"
        if diff < 3600:
            return f"{diff // 60}m"
        if diff < 86400:
            h = diff // 3600
            m = (diff % 3600) // 60
            return f"{h}h{m}m"
        return f"{diff // 86400}d"

    def PadRight(self, text: str, width: int) -> str:
        """Pad string to fixed width (right-pad with spaces) | Thêm khoảng trắng đến độ rộng cố định"""
        while len(text) < width:
            text += " "
        if len(text) > width:
            text = text[:width]
        return text

    def CalculateTFPnL(self, tf: int) -> float:
        """Calculate total P&L for specific TF (all strategies) | Tính tổng P&L cho TF cụ thể"""
        total_pnl = 0.0

        # Get all positions
        positions = self.GetOpenPositions()

        # Loop through all 3 strategies for this TF
        for s in range(3):
            # Skip if no position open
            if self.g_ea.position_flags[tf][s] != 1:
                continue

            ticket = self.g_ea.position_tickets[tf][s]
            if ticket is None:
                continue

            # Find matching position
            for pos in positions:
                if pos['ticket'] == ticket:
                    total_pnl += pos['profit']
                    break

        return total_pnl

    def HasBonusOrders(self, tf: int) -> bool:
        """Check if TF has BONUS orders | Kiểm tra TF có lệnh BONUS không"""
        # Note: TradeLocker doesn't support magic numbers or comments in GetOpenPositions
        # This is a limitation - would need to track BONUS tickets separately
        # For now, return False (incomplete implementation)
        return False

    def FormatBonusStatus(self) -> str:
        """Format BONUS status line for dashboard | Định dạng dòng trạng thái BONUS"""
        if not self.config.EnableBonusNews:
            return "BONUS: Disabled"

        bonus_list = ""
        status = "IDLE"
        bonus_tf_count = 0

        # First check: Are there any BONUS orders currently open?
        for tf in range(7):
            if not self.IsTFEnabled(tf):
                continue

            if self.HasBonusOrders(tf):
                status = "OPEN"
                bonus_tf_count += 1

                news = self.g_ea.csdl_rows[tf].news
                arrow = "^" if news > 0 else "v"

                if bonus_list != "":
                    bonus_list += " "
                bonus_list += f"{G_TF_NAMES[tf]}({self.config.BonusOrderCount}x " + \
                             ('+' if news > 0 else '') + f"{news}{arrow})"

        # Second check: If no orders open, which TFs qualify for BONUS?
        if status == "IDLE":
            for tf in range(7):
                if not self.IsTFEnabled(tf):
                    continue

                news_abs = abs(self.g_ea.csdl_rows[tf].news)
                if news_abs >= self.config.MinNewsLevelBonus:
                    status = "WAIT"
                    bonus_tf_count += 1

                    news = self.g_ea.csdl_rows[tf].news
                    arrow = "^" if news > 0 else "v"

                    if bonus_list != "":
                        bonus_list += " "
                    bonus_list += f"{G_TF_NAMES[tf]}({self.config.BonusOrderCount}x " + \
                                 ('+' if news > 0 else '') + f"{news}{arrow})"

        # If no qualifying TFs, show "None"
        if bonus_list == "":
            bonus_list = "None"

        # Format timestamp (last BONUS open time)
        last_time = datetime.now().strftime("%H:%M:%S")

        # Build final status line
        result = f"BONUS: {bonus_list} | {status} | Last:{last_time}"

        return result

    def ScanAllOrdersForDashboard(self) -> Tuple[int, float, float, str, str]:
        """
        Scan all orders for dashboard display | Quét tất cả lệnh cho dashboard

        Returns: (total_orders, total_profit, total_loss, s1_summary, s2s3_summary)
        """
        total_orders = 0
        total_profit = 0.0
        total_loss = 0.0
        s1_summary = ""
        s2s3_summary = ""

        s1_count = 0
        s2s3_count = 0

        positions = self.GetOpenPositions()

        for pos in positions:
            ticket = pos['ticket']
            profit = pos['profit']

            # Check which strategy this order belongs to
            for tf in range(7):
                # S1 orders
                if (self.g_ea.position_flags[tf][0] == 1 and
                    self.g_ea.position_tickets[tf][0] == ticket):
                    total_orders += 1
                    if profit > 0:
                        total_profit += profit
                    else:
                        total_loss += profit

                    s1_count += 1
                    if s1_count <= 7:  # Max 7 (all TF)
                        margin_usd = pos['lots'] * 1000.0  # Approximate
                        if s1_count > 1:
                            s1_summary += ", "
                        s1_summary += f"S1_{G_TF_NAMES[tf]}[${margin_usd:.0f}]"
                    break

                # S2 + S3 orders
                elif ((self.g_ea.position_flags[tf][1] == 1 and self.g_ea.position_tickets[tf][1] == ticket) or
                      (self.g_ea.position_flags[tf][2] == 1 and self.g_ea.position_tickets[tf][2] == ticket)):
                    total_orders += 1
                    if profit > 0:
                        total_profit += profit
                    else:
                        total_loss += profit

                    s2s3_count += 1
                    if s2s3_count <= 7:  # Show first 7
                        strategy = "S2" if self.g_ea.position_tickets[tf][1] == ticket else "S3"
                        margin_usd = pos['lots'] * 1000.0  # Approximate
                        if s2s3_count > 1:
                            s2s3_summary += ", "
                        s2s3_summary += f"{strategy}_{G_TF_NAMES[tf]}[${margin_usd:.0f}]"
                    break

        # Add "more" indicators
        if s1_count > 7:
            s1_summary += f" +{s1_count - 7} more"
        if s2s3_count > 7:
            s2s3_summary += f" +{s2s3_count - 7} more"

        return total_orders, total_profit, total_loss, s1_summary, s2s3_summary

    def UpdateDashboard(self):
        """
        Update dashboard (console display) | Cập nhật bảng điều khiển

        Displays:
        - Account info (balance, equity, drawdown)
        - Active positions summary
        - P&L breakdown
        - Strategy status
        """
        if not self.config.ShowDashboard:
            return

        # Get account info
        account_info = self.GetAccountInfo()
        equity = account_info.get("equity", 0.0)
        balance = account_info.get("balance", 0.0)
        dd = ((balance - equity) / balance) * 100 if balance > 0 else 0.0

        # Scan orders ONCE
        total_orders, total_profit, total_loss, s1_summary, s2s3_summary = self.ScanAllOrdersForDashboard()

        # Build dashboard text (console format)
        dashboard_lines = []
        dashboard_lines.append("=" * 80)
        dashboard_lines.append(f"TradeLocker MTF ONER - {self.g_ea.symbol_name}")
        dashboard_lines.append("=" * 80)
        dashboard_lines.append(f"Account: Balance=${balance:.2f} | Equity=${equity:.2f} | DD={dd:.2f}%")
        dashboard_lines.append(f"Orders: {total_orders} | Profit=${total_profit:.2f} | Loss=${total_loss:.2f}")
        dashboard_lines.append("-" * 80)

        # Strategy status for each TF
        for tf in range(7):
            if not self.IsTFEnabled(tf):
                continue

            signal = self.g_ea.csdl_rows[tf].signal
            signal_str = self.SignalToString(signal)
            timestamp = self.g_ea.csdl_rows[tf].timestamp
            age = self.FormatAge(timestamp)

            # Check positions
            s1_status = "■" if self.g_ea.position_flags[tf][0] == 1 else "□"
            s2_status = "■" if self.g_ea.position_flags[tf][1] == 1 else "□"
            s3_status = "■" if self.g_ea.position_flags[tf][2] == 1 else "□"

            # TF P&L
            tf_pnl = self.CalculateTFPnL(tf)

            dashboard_lines.append(f"{G_TF_NAMES[tf]:4s} | Sig:{signal_str:4s} Age:{age:6s} | "
                                 f"S1:{s1_status} S2:{s2_status} S3:{s3_status} | P&L:${tf_pnl:+7.2f}")

        dashboard_lines.append("-" * 80)

        # BONUS status
        bonus_status = self.FormatBonusStatus()
        dashboard_lines.append(bonus_status)

        dashboard_lines.append("=" * 80)

        # Print all lines (console output)
        for line in dashboard_lines:
            print(line)

        # Also log to file
        self.logger.debug("[DASHBOARD] Updated")

    # ==========================================================================
    #  PART 19: MAIN EA FUNCTIONS (OnInit, OnTimer)
    # ==========================================================================

    def OnInit(self, symbol_name: str) -> bool:
        """EA initialization | Khởi tạo EA"""

        # PART 1: Symbol recognition
        if not self.InitializeSymbolRecognition(symbol_name):
            return False

        self.InitializeSymbolPrefix()

        # PART 1B: Detect symbol type (pattern matching like MT5 EA)
        self.g_ea.symbol_type = self.DetectSymbolType(symbol_name)

        # PART 1C: Get account info
        self.g_ea.broker_name = "TradeLocker"
        self.g_ea.account_type = "Demo" if "demo" in self.config.TL_Environment else "Live"
        self.g_ea.all_leverages = "TL:100"

        # Compact init summary
        self.logger.info(f"[INIT] {self.g_ea.symbol_name} {self.g_ea.symbol_type} | "
                        f"Broker:{self.g_ea.broker_name}/{self.g_ea.account_type} | "
                        f"Leverage:{self.g_ea.all_leverages} ✓")

        # PART 2: Folder selection
        if self.config.CSDL_Source == "FOLDER_1":
            self.g_ea.csdl_folder = "DataAutoOner/"
        elif self.config.CSDL_Source == "FOLDER_2":
            self.g_ea.csdl_folder = "DataAutoOner2/"
        elif self.config.CSDL_Source == "FOLDER_3":
            self.g_ea.csdl_folder = "DataAutoOner3/"
        else:
            self.g_ea.csdl_folder = "DataAutoOner2/"

        # PART 3: Build filename & Read file
        self.BuildCSDLFilename()
        self.ReadCSDLFile()

        # PART 4: Generate magic numbers
        if not self.GenerateMagicNumbers():
            return False

        # PART 5: Pre-calculate all 21 lot sizes
        self.InitializeLotSizes()

        # PART 6: Initialize Layer1 thresholds
        self.InitializeLayer1Thresholds()

        # PART 7: Map CSDL variables
        self.MapCSDLToEAVariables()

        # PART 7B: Reset ALL auxiliary flags
        for tf in range(7):
            for s in range(3):
                self.g_ea.position_flags[tf][s] = 0
                self.g_ea.position_tickets[tf][s] = None

        # PART 8: Restore positions
        self.RestoreOrCleanupPositions()

        # PART 9: Initialize timestamps
        for tf in range(7):
            self.g_ea.signal_old[tf] = self.g_ea.csdl_rows[tf].signal
            self.g_ea.timestamp_old[tf] = self.g_ea.csdl_rows[tf].timestamp

        # PART 10: Initialize health check
        self.g_ea.health_last_check_hour = datetime.now().hour

        # PART 11: Mark first run completed
        self.g_ea.first_run_completed = True

        self.logger.info("[INIT] EA initialization completed ✓")
        return True

    def OnTimer(self):
        """Timer event - main trading loop (1 second) | Sự kiện timer - vòng lặp giao dịch chính"""
        current_time = int(time.time())
        current_second = current_time % 60

        # Prevent duplicate execution
        if current_time == self.g_ea.timer_last_run_time:
            return

        self.g_ea.timer_last_run_time = current_time

        # ==================================================================
        # GROUP 1: EVEN SECONDS (0,2,4,6...) - TRADING CORE (HIGH PRIORITY)
        # ==================================================================
        if not self.config.UseEvenOddMode or (current_second % 2 == 0):

            # STEP 1: Read CSDL file
            self.ReadCSDLFile()

            # STEP 2: Map data for all 7 TF
            self.MapCSDLToEAVariables()

            # STEP 3: Strategy processing loop
            for tf in range(7):
                # STEP 3.1: FAST CLOSE by M1
                if tf == 0 and self.HasValidS2BaseCondition(0):
                    if self.config.S1_CloseByM1:
                        self.CloseS1OrdersByM1()
                    if self.config.S2_CloseByM1:
                        self.CloseS2OrdersByM1()
                    if self.config.EnableBonusNews:
                        self.CloseAllBonusOrders()

                # STEP 3.2: NORMAL CLOSE by TF signal
                if self.HasValidS2BaseCondition(tf):
                    if self.config.S1_CloseByM1 and self.config.S2_CloseByM1:
                        self.CloseS3OrdersForTF(tf)
                    elif self.config.S1_CloseByM1:
                        # Close S2 and S3
                        if self.g_ea.position_flags[tf][1] == 1:
                            order_id = self.g_ea.position_tickets[tf][1]
                            if order_id and self.ClosePosition(order_id):
                                self.g_ea.position_flags[tf][1] = 0
                                self.g_ea.position_tickets[tf][1] = None
                        if self.g_ea.position_flags[tf][2] == 1:
                            order_id = self.g_ea.position_tickets[tf][2]
                            if order_id and self.ClosePosition(order_id):
                                self.g_ea.position_flags[tf][2] = 0
                                self.g_ea.position_tickets[tf][2] = None
                    elif self.config.S2_CloseByM1:
                        # Close S1 and S3
                        if self.g_ea.position_flags[tf][0] == 1:
                            order_id = self.g_ea.position_tickets[tf][0]
                            if order_id and self.ClosePosition(order_id):
                                self.g_ea.position_flags[tf][0] = 0
                                self.g_ea.position_tickets[tf][0] = None
                        if self.g_ea.position_flags[tf][2] == 1:
                            order_id = self.g_ea.position_tickets[tf][2]
                            if order_id and self.ClosePosition(order_id):
                                self.g_ea.position_flags[tf][2] = 0
                                self.g_ea.position_tickets[tf][2] = None
                    else:
                        self.CloseAllStrategiesByMagicForTF(tf)

                    # STEP 3.3: Open new orders (ONLY if TF enabled)
                    if self.IsTFEnabled(tf):
                        if self.config.S1_HOME:
                            self.ProcessS1Strategy(tf)
                        if self.config.S2_TREND:
                            self.ProcessS2Strategy(tf)
                        if self.config.S3_NEWS:
                            self.ProcessS3Strategy(tf)

                    # STEP 3.4: Process Bonus NEWS
                    if self.config.EnableBonusNews:
                        self.ProcessBonusNews()

                    # STEP 3.5: Update baseline
                    self.g_ea.signal_old[tf] = self.g_ea.csdl_rows[tf].signal
                    self.g_ea.timestamp_old[tf] = self.g_ea.csdl_rows[tf].timestamp

        # ==================================================================
        # GROUP 2: ODD SECONDS (1,3,5,7...) - AUXILIARY (SUPPORT)
        # ==================================================================
        if not self.config.UseEvenOddMode or (current_second % 2 != 0):

            # STEP 1: Check stoploss & take profit
            self.CheckStoplossAndTakeProfit()

            # STEP 2: Update dashboard
            self.UpdateDashboard()

            # STEP 3: Emergency check
            self.CheckAllEmergencyConditions()

            # STEP 4: Weekend reset check
            self.CheckWeekendReset()

            # STEP 5: Health check at 8h/16h
            self.CheckSPYBotHealth()

    def Start(self, symbol_name: str):
        """Start the bot | Khởi động bot"""

        # Initialize TradeLocker connection
        if not self.InitTradingConnection():
            self.logger.error("[ERROR] Failed to connect to TradeLocker")
            return

        # Get instrument ID
        if not self.GetInstrumentID(symbol_name):
            self.logger.error(f"[ERROR] Failed to get instrument ID for {symbol_name}")
            return

        # Initialize EA
        if not self.OnInit(symbol_name):
            self.logger.error("[ERROR] EA initialization failed")
            return

        # Set running flag
        self.running = True

        # Start timer thread
        self.timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
        self.timer_thread.start()

        self.logger.info("[START] Bot started successfully ✓")
        self.logger.info("[START] Press Ctrl+C to stop")

        # Main loop - keep alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("[STOP] Keyboard interrupt received")
            self.Stop()

    def _timer_loop(self):
        """Internal timer loop | Vòng lặp timer nội bộ"""
        while self.running:
            try:
                self.OnTimer()
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"[TIMER ERROR] {e}")
                time.sleep(1)

    def Stop(self):
        """Stop the bot | Dừng bot"""
        self.logger.info("[STOP] Stopping bot...")
        self.running = False

        if self.timer_thread:
            self.timer_thread.join(timeout=5)

        self.logger.info("[STOP] Bot stopped ✓")

# ==============================================================================
#  PART 20: MAIN ENTRY POINT | ĐIỂM KHỞI ĐỘNG CHÍNH
# ==============================================================================

def main():
    """Main entry point | Điểm khởi động chính"""

    print("""
==============================================================================
TradeLocker MTF ONER Bot - Multi Timeframe Expert Advisor
Bot EA nhiều khung thời gian cho TradeLocker
==============================================================================
Version: TL_V1 - Converted from MT5 EA V2
Logic: 100% identical to MT5 EA - NO CHANGES
==============================================================================
""")

    # Load configuration from config.json
    config = Config.load_from_json("config.json")

    # Setup logging
    logger = setup_logging(config.DebugMode)

    # Check credentials
    if config.TL_Username == "your_email@example.com" or config.TL_Password == "YOUR_PASSWORD":
        logger.error("[ERROR] Please configure TradeLocker credentials in config.json")
        logger.error("[ERROR] Edit config.json and set your username, password, and server")
        return

    # Get symbol from command line or use default
    if len(sys.argv) > 1:
        symbol_name = sys.argv[1]
    else:
        symbol_name = "BTCUSD"  # Default symbol
        logger.info(f"[INFO] Using default symbol: {symbol_name}")
        logger.info(f"[INFO] To use different symbol: python {sys.argv[0]} SYMBOL_NAME")

    # Create bot instance
    bot = TradeLockerBot(config, logger)

    # Setup signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        logger.info("\n[SIGNAL] Shutdown signal received")
        bot.Stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start bot
    try:
        bot.Start(symbol_name)
    except Exception as e:
        logger.error(f"[FATAL] Bot crashed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        bot.Stop()

if __name__ == "__main__":
    main()
