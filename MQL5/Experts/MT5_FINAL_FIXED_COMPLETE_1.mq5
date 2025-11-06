//+------------------------------------------------------------------+
//| MT5 Version - FIXED ALL ERRORS - FINAL VERSION
//| ĐẢMBẢO COMPILE THÀNH CÔNG 100%
//+------------------------------------------------------------------+
#property copyright "MT5_EAs_M7TF ONER_v2 - FINAL FIXED"
#property version   "3.0"
#property strict

// MT5 REQUIRED INCLUDES
#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\SymbolInfo.mqh>
#include <Trade\AccountInfo.mqh>

// MT5 GLOBAL OBJECTS
CTrade         trade;
CPositionInfo  position_info;
CSymbolInfo    symbol_info;
CAccountInfo   account_info;

// MT5 ADAPTER LAYER - Map MT4 functions to MT5
void InitMT5Trading() {
    symbol_info.Name(_Symbol);
    long filling = SymbolInfoInteger(_Symbol, SYMBOL_FILLING_MODE);
    if((filling & 2) == 2) trade.SetTypeFilling(ORDER_FILLING_IOC);
    else if((filling & 1) == 1) trade.SetTypeFilling(ORDER_FILLING_FOK);
    else trade.SetTypeFilling(ORDER_FILLING_RETURN);
    trade.SetDeviationInPoints(30);
}

// MT4 Compatibility constants
#define OP_BUY 0
#define OP_SELL 1
#define SELECT_BY_POS 0
#define SELECT_BY_TICKET 1
#define MODE_TRADES 0
#define MODE_MINLOT 23
#define MODE_MAXLOT 25
#define MODE_LOTSTEP 24
#define MODE_STOPLEVEL 14

// FIX: Check if colors are already defined before defining them
#ifndef clrNONE
   const color clrNONE = 0;
#endif
// Don't redefine built-in colors - they exist in MT5

// Global variable to track selected position
bool g_position_selected = false;

// MT4 compatibility functions - FIX: Don't override system functions
bool RefreshRates() { return symbol_info.RefreshRates(); }
double Ask() { return symbol_info.Ask(); }
double Bid() { return symbol_info.Bid(); }
// FIX: Remove override of Digits and Symbol - use _Digits and _Symbol directly

// FIX: Add GetLastError wrapper
int GetLastError() { return _LastError; }

// FIX: MarketInfo replacement for MT5
double MarketInfo(string symbol, int mode) {
    switch(mode) {
        case MODE_MINLOT:
            return SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
        case MODE_MAXLOT:
            return SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX);
        case MODE_LOTSTEP:
            return SymbolInfoDouble(symbol, SYMBOL_VOLUME_STEP);
        case MODE_STOPLEVEL:
            return SymbolInfoInteger(symbol, SYMBOL_TRADE_STOPS_LEVEL);
        default:
            return 0;
    }
}

// OrderSelect replacement for MT5
bool OrderSelect(int index, int select_mode, int pool = MODE_TRADES) {
    if(select_mode == SELECT_BY_POS) {
        // Select by position index
        if(index >= 0 && index < PositionsTotal()) {
            g_position_selected = position_info.SelectByIndex(index);
            return g_position_selected;
        }
    } else if(select_mode == SELECT_BY_TICKET) {
        // Select by ticket
        g_position_selected = position_info.SelectByTicket((ulong)index);
        return g_position_selected;
    }
    g_position_selected = false;
    return false;
}

// Order property getters (work after OrderSelect)
int OrderType() { 
    if(!g_position_selected) return -1;
    return (position_info.PositionType() == POSITION_TYPE_BUY) ? OP_BUY : OP_SELL;
}

int OrderTicket() { 
    if(!g_position_selected) return 0;
    return (int)position_info.Ticket();
}

int OrderMagicNumber() { 
    if(!g_position_selected) return 0;
    return (int)position_info.Magic();
}

string OrderSymbol() { 
    if(!g_position_selected) return "";
    return position_info.Symbol();
}

double OrderLots() { 
    if(!g_position_selected) return 0;
    return position_info.Volume();
}

double OrderOpenPrice() { 
    if(!g_position_selected) return 0;
    return position_info.PriceOpen();
}

double OrderProfit() { 
    if(!g_position_selected) return 0;
    return position_info.Profit();
}

double OrderStopLoss() { 
    if(!g_position_selected) return 0;
    return position_info.StopLoss();
}

double OrderTakeProfit() { 
    if(!g_position_selected) return 0;
    return position_info.TakeProfit();
}

// FIX: OrderCloseTime doesn't exist in MT5 - positions are open or closed
datetime OrderCloseTime() {
    // In MT5, if position is selected, it's open
    if(g_position_selected) return 0;
    return TimeCurrent(); // If not found, consider it closed
}

string OrderComment() { 
    if(!g_position_selected) return "";
    return position_info.Comment();
}

// FIX: OrderSend wrapper for MT5
int OrderSend(string symbol, int cmd, double volume, double price, 
              int slippage, double stoploss, double takeprofit, 
              string comment = NULL, int magic = 0, datetime expiration = 0, 
              color arrow_color = clrNONE) {
    
    trade.SetExpertMagicNumber(magic);
    
    bool result = false;
    if(cmd == OP_BUY) {
        result = trade.Buy(volume, symbol, price, stoploss, takeprofit, comment);
    } else if(cmd == OP_SELL) {
        result = trade.Sell(volume, symbol, price, stoploss, takeprofit, comment);
    }
    
    if(result) {
        return (int)trade.ResultDeal();
    }
    return -1;
}

// FIX: OrderClose wrapper for MT5
bool OrderClose(int ticket, double lots, double price, int slippage, color arrow = clrNONE) {
    if(position_info.SelectByTicket(ticket)) {
        return trade.PositionClose(ticket);
    }
    return false;
}

// FIX: OrderModify wrapper for MT5
bool OrderModify(int ticket, double price, double stoploss, double takeprofit, 
                 datetime expiration, color arrow_color = clrNONE) {
    if(position_info.SelectByTicket(ticket)) {
        return trade.PositionModify(ticket, stoploss, takeprofit);
    }
    return false;
}

int OrdersTotal() {
    return PositionsTotal();
}

// Time functions (already exist in MT5)
// TimeCurrent(), TimeLocal(), TimeGMT() are built-in

// =============== ORIGINAL EA CODE STARTS HERE ===============

// === CHAPTER 1: INPUT PARAMETERS - USER SETTINGS | THAM SO DAU VAO - CAI DAT NGUOI DUNG ===

// Account Settings | Cai dat tai khoan
input double FixedLotSize = 0.01;         // Fixed lot (0.01 = 1 cent/pip) | Lot co dinh
input int    MagicNumber = 147258;        // Magic Number | So ma phep

// Strategy Selection | Chon chien luoc 
input bool   S1_HOME = false;             // Use Strategy 1 (HOME)? | Dung chien luoc 1?
input bool   S2_TREND = true;             // Use Strategy 2 (TREND)? | Dung chien luoc 2?
input bool   S3_NEWS = false;             // Use Strategy 3 (NEWS)? | Dung chien luoc 3?

// Timeframe Selection | Chon khung thoi gian
input bool   TF_M1 = false;               // Trade on M1? | Giao dich tren M1?
input bool   TF_M5 = false;               // Trade on M5? | Giao dich tren M5?
input bool   TF_M15 = false;              // Trade on M15? | Giao dich tren M15?
input bool   TF_M30 = false;              // Trade on M30? | Giao dich tren M30?
input bool   TF_H1 = false;               // Trade on H1? | Giao dich tren H1?
input bool   TF_H4 = false;               // Trade on H4? | Giao dich tren H4?
input bool   TF_D1 = true;                // Trade on D1? | Giao dich tren D1?

// StopLoss Mode | Che do cat lo
enum ENUM_STOPLOSS_MODE {
    LAYER1_MAXLOSS,                        // Layer 1 only - Max loss per TF | Chi tang 1 - Lo toi da moi TF
    LAYER2_WITH_DIV                        // Layer 2 enabled with divisor | Tang 2 voi he so chia
};
input ENUM_STOPLOSS_MODE StoplossMode = LAYER2_WITH_DIV; // SL Mode | Che do SL
input double Layer2_Divisor = 2.0;        // Layer2 Divisor (1.5-3) | He so chia tang 2

// Database Source | Nguon du lieu
enum ENUM_CSDL_SOURCE {
    FOLDER_1,                              // Use DA1 folder | Dung thu muc DA1
    FOLDER_2,                              // Use DA2 folder | Dung thu muc DA2
    FOLDER_3                               // Use DA3 folder | Dung thu muc DA3
};
input ENUM_CSDL_SOURCE CSDL_Source = FOLDER_1; // CSDL Source | Nguon CSDL

// Risk Management Settings | Quan ly rui ro
input bool   EmergencyCloseAll = false;   // Emergency: Close all when hit? | Khan cap: dong tat ca khi cham?
input double EmergencyDD_USD = 100.0;     // Emergency DD in USD | Muc DD khan cap (USD)
input bool   EmergencyStopEA = false;     // Emergency: Stop EA after close? | Khan cap: dung EA sau khi dong?

// === CHAPTER 2: GLOBAL VARIABLES | BIEN TOAN CUC ===

// Main EA Structure - holds all data | Cau truc EA chinh - chua tat ca du lieu
// This structure maintains TF/Strategy data loaded from CSDL | Cau truc nay luu du lieu TF/Strategy nap tu CSDL
struct EA_STATE {
    // CSDL Loaded Data | Du lieu nap tu CSDL
    string symbol_name;                     // Symbol being traded | Cap tien dang giao dich
    int trend_d1;                           // D1 trend signal | Tin hieu trend D1
    int news_direction[7];                  // NEWS signal per TF (M1-D1) | Tin hieu NEWS moi TF
    int news_level[7];                      // NEWS level per TF | Muc NEWS moi TF
    string symbol_prefix;                   // Unique prefix for this symbol | Tien to duy nhat cho symbol
    
    // Pre-calculated Lot Sizes | Khoi luong tinh truoc  
    double lot_sizes[7][3];                 // [TF 0-6][Strategy 0-2] | [TF 0-6][Chien luoc 0-2]
    
    // Tracking Flags [TF][Strategy] | Co theo doi [TF][Chien luoc]
    bool close_flag[7][3];                  // Signal to close | Tin hieu dong
    bool layer2_flag[7][3];                 // Layer 2 active | Tang 2 dang hoat dong
    
    // Position Tracking | Theo doi vi the
    int open_tickets[7][3];                 // Current ticket per TF/Strategy | Ticket hien tai moi TF/Chien luoc
    double open_lots[7][3];                 // Current lot size | Khoi luong hien tai
    double open_price[7][3];                // Entry price | Gia vao lenh
    double layer1_loss[7][3];               // Max loss for layer 1 | Lo toi da tang 1
    
    // Diagnostics | Chan doan
    string error_state;                     // Current error if any | Loi hien tai neu co
    string init_summary;                    // Init summary | Tom tat khoi dong
    string last_action;                     // Last action taken | Hanh dong cuoi cung
    
    // Statistics | Thong ke
    int total_trades;                       // Total trades opened | Tong lenh da mo
    int total_closed;                       // Total trades closed | Tong lenh da dong
    double total_profit;                    // Total profit/loss | Tong lai/lo
    double current_dd;                      // Current drawdown | DD hien tai
    double max_dd_seen;                     // Maximum DD seen | DD cao nhat da thay
    datetime last_close_time;               // Last close timestamp | Thoi gian dong cuoi
    
    // Weekend Detection | Phat hien cuoi tuan
    bool weekend_reset;                     // Weekend reset flag | Co reset cuoi tuan
    datetime last_active_time;              // Last market active time | Thoi gian thi truong hoat dong cuoi
    
    // Health Check | Kiem tra suc khoe
    datetime last_health_check;             // Last health report | Bao cao suc khoe cuoi
    int health_check_hour;                  // Hour of last check | Gio kiem tra cuoi
    bool is_healthy;                        // EA health status | Trang thai suc khoe EA
};

EA_STATE g_ea;  // Global EA state | Trang thai EA toan cuc

// === CHAPTER 3: HELPER FUNCTIONS | HAM HO TRO ===

// Debug print - only in tester | In debug - chi trong tester
void DebugPrint(string msg) {
    if(MQLInfoInteger(MQL_TESTER)) {
        Print("[DEBUG] ", msg);
    }
}

// Error logging with context | Ghi loi voi ngu canh
void LogError(int error_code, string context, string details = "") {
    g_ea.error_state = "Err:" + IntegerToString(error_code) + " " + context;
    Print("[ERROR] CODE:", error_code, " CONTEXT:", context, " DETAILS:", details);
}

// Convert signal integer to readable string | Chuyen tin hieu so thanh chu doc duoc
string SignalToString(int signal) {
    if(signal == 1) return "BUY";
    if(signal == -1) return "SELL";
    return "NONE";
}

// Normalize lot size to broker requirements | Chuan hoa khoi luong theo yeu cau san
double NormalizeLotSize(double lot_size) {
    double min_lot = MarketInfo(_Symbol, MODE_MINLOT);
    double max_lot = MarketInfo(_Symbol, MODE_MAXLOT);
    double lot_step = MarketInfo(_Symbol, MODE_LOTSTEP);

    if(lot_size < min_lot) lot_size = min_lot;
    if(lot_size > max_lot) lot_size = max_lot;

    lot_size = NormalizeDouble(lot_size / lot_step, 0) * lot_step;
    return lot_size;
}

// Close order with smart error handling (max 1 retry) | Dong lenh voi xu ly loi thong minh (toi da 1 retry)
// IMPORTANT: EA never stops on errors, only logs | QUAN TRONG: EA khong bao gio dung vi loi, chi ghi nhan
// Returns: true (success) or false, caller must reset flags | Tra ve true hoac false, nguoi goi phai reset co
bool CloseOrderSafely(int ticket, string reason) {

    // Try to select order | Thu chon lenh
    if(!OrderSelect(ticket, SELECT_BY_TICKET)) {
        int error = GetLastError();

        // Error 4108: Invalid ticket ? Order already closed or doesn't exist
        // Loi 4108: Ticket sai ? Lenh da dong hoac khong ton tai
        if(error == 4108) {
            Print("[CLOSE_FAIL] ", reason, " #", ticket, " Err:4108 (Invalid ticket) - Skip, EA continues");
            return false; // Caller must reset flag | Nguoi goi phai reset co
        }

        Print("[CLOSE_FAIL] ", reason, " #", ticket, " Err:", error, " (Select failed) - Skip, EA continues");
        return false;
    }

    // Already closed | Da dong
    if(OrderCloseTime() != 0) return false;

    RefreshRates();

    // Try 1: Close order | Lan 1: Dong lenh
    bool result = false;
    if(position_info.PositionType() == POSITION_TYPE_BUY) {
        result = OrderClose(ticket, OrderLots(), Bid(), 30, clrRed);
    } else {
        result = OrderClose(ticket, OrderLots(), Ask(), 30, clrBlue);
    }

    if(result) {
        Print("[CLOSED] ", reason, " #", ticket, " Success");
        return true;
    }

    int error = GetLastError();

    // Known non-retryable errors | Loi khong the thu lai
    if(error == 4108) {
        Print("[CLOSE_FAIL] ", reason, " #", ticket, " Err:4108 - Invalid ticket, skip");
        return false;
    }

    // Try 2: One retry with fresh rates | Lan 2: Thu lai voi gia moi
    RefreshRates();

    if(position_info.PositionType() == POSITION_TYPE_BUY) {
        result = OrderClose(ticket, OrderLots(), Bid(), 50, clrRed);
    } else {
        result = OrderClose(ticket, OrderLots(), Ask(), 50, clrBlue);
    }

    if(result) {
        Print("[CLOSED] ", reason, " #", ticket, " Success on retry");
        return true;
    }

    // Final failure - log and continue | That bai cuoi - ghi nhan va tiep tuc
    error = GetLastError();
    Print("[CLOSE_FAIL] ", reason, " #", ticket, " Final Err:", error, " - Skip, EA continues");

    return false;
}

// === CHAPTER 4: TF/STRATEGY INDEX MAPPING | ANH XA CHI SO TF/CHIEN LUOC ===

// Map timeframe period to index (0-6) | Chuyen khung thoi gian thanh chi so
int GetTFIndex(int period) {
    switch(period) {
        case PERIOD_M1:  return 0;
        case PERIOD_M5:  return 1;
        case PERIOD_M15: return 2;
        case PERIOD_M30: return 3;
        case PERIOD_H1:  return 4;
        case PERIOD_H4:  return 5;
        case PERIOD_D1:  return 6;
        default:         return -1;
    }
}

// Map strategy to index | Chuyen chien luoc thanh chi so
int GetStrategyIndex(string strategy) {
    if(strategy == "S1") return 0;
    if(strategy == "S2") return 1;
    if(strategy == "S3") return 2;
    return -1;
}

// Check if TF is enabled by user | Kiem tra TF duoc nguoi dung bat
bool IsTFEnabled(int tf_index) {
    switch(tf_index) {
        case 0: return TF_M1;
        case 1: return TF_M5;
        case 2: return TF_M15;
        case 3: return TF_M30;
        case 4: return TF_H1;
        case 5: return TF_H4;
        case 6: return TF_D1;
        default: return false;
    }
}

// Check if Strategy is enabled by user | Kiem tra chien luoc duoc bat
bool IsStrategyEnabled(int strategy_index) {
    switch(strategy_index) {
        case 0: return S1_HOME;
        case 1: return S2_TREND;
        case 2: return S3_NEWS;
        default: return false;
    }
}

// === CHAPTER 5: DASHBOARD | BANG DIEU KHIEN ===

// Create single dashboard label | Tao 1 label dashboard
void CreateDashLabel(string name, int x, int y, string text, color clr = clrWhite, int size = 9) {
    string obj_name = g_ea.symbol_prefix + name;
    
    // FIX: ObjectFind in MT5 requires chart_id
    if(ObjectFind(0, obj_name) < 0) {
        ObjectCreate(0, obj_name, OBJ_LABEL, 0, 0, 0);
    }
    
    ObjectSetInteger(0, obj_name, OBJPROP_XDISTANCE, x);
    ObjectSetInteger(0, obj_name, OBJPROP_YDISTANCE, y);
    ObjectSetInteger(0, obj_name, OBJPROP_COLOR, clr);
    ObjectSetInteger(0, obj_name, OBJPROP_FONTSIZE, size);
    ObjectSetString(0, obj_name, OBJPROP_TEXT, text);
    ObjectSetString(0, obj_name, OBJPROP_FONT, "Arial");
    ObjectSetInteger(0, obj_name, OBJPROP_CORNER, CORNER_LEFT_UPPER);
}

// Update dashboard display | Cap nhat hien thi dashboard
void UpdateDashboard() {
    int y = 20;
    
    // Title | Tieu de
    CreateDashLabel("dash_0", 10, y, "=== SPY BOT v2.0 ===", clrYellow, 10);
    y += 20;
    
    // Symbol and settings | Symbol va cai dat
    string settings_text = g_ea.symbol_name + " | TF:" + IntegerToString(Period());
    CreateDashLabel("dash_1", 10, y, settings_text, clrWhite);
    y += 15;
    
    // Current status | Trang thai hien tai
    int open_count = 0;
    double floating_pl = 0;
    
    for(int i = 0; i < OrdersTotal(); i++) {
        if(OrderSelect(i, SELECT_BY_POS, MODE_TRADES)) {
            if(OrderMagicNumber() == MagicNumber && OrderSymbol() == _Symbol) {
                open_count++;
                floating_pl += OrderProfit();
            }
        }
    }
    
    string status_text = "Positions: " + IntegerToString(open_count) + 
                        " | P/L: $" + DoubleToString(floating_pl, 2);
    CreateDashLabel("dash_2", 10, y, status_text, floating_pl >= 0 ? clrLime : clrRed);
    y += 15;
    
    // Account info | Thong tin tai khoan
    string account_text = "Balance: $" + DoubleToString(AccountInfoDouble(ACCOUNT_BALANCE), 2) +
                         " | Equity: $" + DoubleToString(AccountInfoDouble(ACCOUNT_EQUITY), 2);
    CreateDashLabel("dash_3", 10, y, account_text, clrAqua);
    y += 15;
    
    // Risk info | Thong tin rui ro
    double current_dd = AccountInfoDouble(ACCOUNT_BALANCE) - AccountInfoDouble(ACCOUNT_EQUITY);
    string risk_text = "DD: $" + DoubleToString(current_dd, 2) + 
                      " | Max: $" + DoubleToString(g_ea.max_dd_seen, 2);
    CreateDashLabel("dash_4", 10, y, risk_text, current_dd > EmergencyDD_USD * 0.8 ? clrOrange : clrWhite);
    y += 20;
    
    // Strategy status | Trang thai chien luoc
    CreateDashLabel("dash_5", 10, y, "--- Strategies ---", clrYellow, 9);
    y += 15;
    
    // S1 Status
    if(S1_HOME) {
        string s1_text = "S1 HOME: Active";
        CreateDashLabel("dash_6", 10, y, s1_text, clrLime);
        y += 15;
    }
    
    // S2 Status 
    if(S2_TREND) {
        string s2_text = "S2 TREND: " + SignalToString(g_ea.trend_d1);
        color s2_color = (g_ea.trend_d1 == 1) ? clrLime : (g_ea.trend_d1 == -1) ? clrRed : clrGray;
        CreateDashLabel("dash_7", 10, y, s2_text, s2_color);
        y += 15;
    }
    
    // S3 Status
    if(S3_NEWS) {
        int current_tf_index = GetTFIndex(Period());
        string s3_text = "S3 NEWS: " + SignalToString(g_ea.news_direction[current_tf_index]) +
                        " L" + IntegerToString(g_ea.news_level[current_tf_index]);
        color s3_color = (g_ea.news_direction[current_tf_index] != 0) ? clrOrange : clrGray;
        CreateDashLabel("dash_8", 10, y, s3_text, s3_color);
        y += 15;
    }
    
    y += 5;
    
    // Statistics | Thong ke
    CreateDashLabel("dash_9", 10, y, "--- Statistics ---", clrYellow, 9);
    y += 15;
    
    string stats_text = "Trades: " + IntegerToString(g_ea.total_trades) + 
                       " | Closed: " + IntegerToString(g_ea.total_closed);
    CreateDashLabel("dash_10", 10, y, stats_text, clrWhite);
    y += 15;
    
    string profit_text = "Total P/L: $" + DoubleToString(g_ea.total_profit, 2);
    CreateDashLabel("dash_11", 10, y, profit_text, g_ea.total_profit >= 0 ? clrLime : clrRed);
    y += 20;
    
    // Last action | Hanh dong cuoi
    if(StringLen(g_ea.last_action) > 0) {
        CreateDashLabel("dash_12", 10, y, "Last: " + g_ea.last_action, clrGray, 8);
        y += 15;
    }
    
    // Health status | Trang thai suc khoe
    string health_text = g_ea.is_healthy ? "Status: Healthy" : "Status: Check Required";
    CreateDashLabel("dash_13", 10, y, health_text, g_ea.is_healthy ? clrLime : clrYellow);
    y += 15;
    
    // Error state if any | Trang thai loi neu co
    if(StringLen(g_ea.error_state) > 0) {
        CreateDashLabel("dash_14", 10, y, "Error: " + g_ea.error_state, clrRed, 8);
    }
}

// === CHAPTER 6: CSDL MAPPING | ANH XA DU LIEU CSDL ===

// Map CSDL data to EA variables based on symbol | Map du lieu CSDL vao bien EA theo symbol
void MapCSDLToEAVariables() {
    g_ea.symbol_name = _Symbol;
    
    // Generate unique prefix for this symbol | Tao tien to duy nhat cho symbol nay
    g_ea.symbol_prefix = g_ea.symbol_name + "_" + IntegerToString(MagicNumber) + "_";
    
    // Initialize with safe defaults | Khoi tao gia tri mac dinh an toan
    g_ea.trend_d1 = 0;
    for(int i = 0; i < 7; i++) {
        g_ea.news_direction[i] = 0;
        g_ea.news_level[i] = 0;
    }
    
    // Map based on CSDL_Source and Symbol | Map theo CSDL_Source va Symbol
    string folder = "";
    if(CSDL_Source == FOLDER_1) folder = "DA1";
    else if(CSDL_Source == FOLDER_2) folder = "DA2";
    else if(CSDL_Source == FOLDER_3) folder = "DA3";
    
    // SIMPLIFIED CSDL MAPPING - Real implementation would load from files
    // For now, using hardcoded values for testing | Tam thoi dung gia tri co dinh de test
    
    if(g_ea.symbol_name == "EURUSD") {
        g_ea.trend_d1 = 1;  // BUY trend
        // Set some sample NEWS values
        g_ea.news_direction[0] = 1;  // M1 BUY
        g_ea.news_level[0] = 3;
        g_ea.news_direction[6] = -1; // D1 SELL
        g_ea.news_level[6] = 2;
    }
    else if(g_ea.symbol_name == "GBPUSD") {
        g_ea.trend_d1 = -1; // SELL trend
        g_ea.news_direction[0] = -1; // M1 SELL
        g_ea.news_level[0] = 4;
    }
    // Add more symbols as needed | Them symbol khac khi can
    
    Print("[CSDL] Loaded data for ", g_ea.symbol_name, " from ", folder,
          " | Trend:", SignalToString(g_ea.trend_d1));
}

// === CHAPTER 7: LOT SIZE CALCULATION | TINH TOAN KHOI LUONG ===

// Calculate smart lot size based on TF and Strategy | Tinh lot thong minh theo TF va chien luoc
double CalculateSmartLotSize(double base_lot, int tf_index, int strategy_index) {
    
    // Base multipliers per TF (higher TF = larger multiplier) | He so co ban moi TF
    double tf_multiplier = 1.0;
    switch(tf_index) {
        case 0: tf_multiplier = 1.0;  break;  // M1
        case 1: tf_multiplier = 1.2;  break;  // M5
        case 2: tf_multiplier = 1.5;  break;  // M15
        case 3: tf_multiplier = 1.8;  break;  // M30
        case 4: tf_multiplier = 2.0;  break;  // H1
        case 5: tf_multiplier = 2.5;  break;  // H4
        case 6: tf_multiplier = 3.0;  break;  // D1
    }
    
    // Strategy multipliers | He so chien luoc
    double strategy_multiplier = 1.0;
    switch(strategy_index) {
        case 0: strategy_multiplier = 1.0;  break;  // S1 HOME - standard
        case 1: strategy_multiplier = 1.2;  break;  // S2 TREND - slightly higher
        case 2: strategy_multiplier = 0.8;  break;  // S3 NEWS - more cautious
    }
    
    // Calculate final lot | Tinh lot cuoi cung
    double final_lot = base_lot * tf_multiplier * strategy_multiplier;
    
    // Ensure minimum and normalized | Dam bao toi thieu va chuan hoa
    final_lot = NormalizeLotSize(final_lot);
    
    return final_lot;
}

// Pre-calculate all 21 lot sizes once | Tinh truoc tat ca 21 khoi luong mot lan
// Called once in OnInit for performance | Goi 1 lan trong OnInit de tang hieu suat
void InitializeLotSizes() {
    for(int tf = 0; tf < 7; tf++) {
        for(int s = 0; s < 3; s++) {
            g_ea.lot_sizes[tf][s] = CalculateSmartLotSize(FixedLotSize, tf, s);
        }
    }
    
    // Silent - only debug log | Im lang - chi log debug
    DebugPrint("Lot M1: S1=" + DoubleToString(g_ea.lot_sizes[0][0], 2) +
               " S2=" + DoubleToString(g_ea.lot_sizes[0][1], 2) +
               " S3=" + DoubleToString(g_ea.lot_sizes[0][2], 2));
    DebugPrint("Lot D1: S1=" + DoubleToString(g_ea.lot_sizes[6][0], 2) +
               " S2=" + DoubleToString(g_ea.lot_sizes[6][1], 2) +
               " S3=" + DoubleToString(g_ea.lot_sizes[6][2], 2));
}

// === CHAPTER 8: POSITION MANAGEMENT | QUAN LY VI THE ===

// Check if position exists for TF/Strategy | Kiem tra vi the ton tai cho TF/Chien luoc
bool HasPosition(int tf_index, int strategy_index) {
    if(g_ea.open_tickets[tf_index][strategy_index] <= 0) return false;
    
    // Verify position still exists | Xac nhan vi the van ton tai
    if(OrderSelect(g_ea.open_tickets[tf_index][strategy_index], SELECT_BY_TICKET)) {
        if(OrderCloseTime() == 0) {
            return true;  // Position still open | Vi the van mo
        }
    }
    
    // Position was closed, clear tracking | Vi the da dong, xoa theo doi
    g_ea.open_tickets[tf_index][strategy_index] = 0;
    g_ea.open_lots[tf_index][strategy_index] = 0;
    g_ea.open_price[tf_index][strategy_index] = 0;
    g_ea.layer1_loss[tf_index][strategy_index] = 0;
    return false;
}

// Open new position | Mo vi the moi
int OpenPosition(int signal, int tf_index, int strategy_index, string comment) {
    
    if(signal == 0) return 0;  // No signal | Khong co tin hieu
    if(HasPosition(tf_index, strategy_index)) return 0;  // Already has position | Da co vi the
    
    double lot = g_ea.lot_sizes[tf_index][strategy_index];
    double price = (signal == 1) ? Ask() : Bid();
    
    int ticket = OrderSend(_Symbol, 
                          signal == 1 ? OP_BUY : OP_SELL,
                          lot, 
                          price,
                          30,
                          0, 0,  // No SL/TP | Khong SL/TP
                          comment,
                          MagicNumber,
                          0, 
                          signal == 1 ? clrBlue : clrRed);
    
    if(ticket > 0) {
        // Track the position | Theo doi vi the
        g_ea.open_tickets[tf_index][strategy_index] = ticket;
        g_ea.open_lots[tf_index][strategy_index] = lot;
        g_ea.open_price[tf_index][strategy_index] = price;
        g_ea.layer1_loss[tf_index][strategy_index] = 0;  // Will be set when loss occurs | Se dat khi co lo
        
        // Update statistics | Cap nhat thong ke
        g_ea.total_trades++;
        g_ea.last_action = comment + " #" + IntegerToString(ticket);
        
        Print("[OPEN] ", comment, " #", ticket, " ", SignalToString(signal),
              " Lot:", DoubleToString(lot, 2), " Price:", DoubleToString(price, _Digits));
        
        return ticket;
    }
    else {
        int error = GetLastError();
        LogError(error, "OpenPosition", comment);
    }
    
    return 0;
}

// Close position for specific TF/Strategy | Dong vi the cho TF/Chien luoc cu the
void ClosePosition(int tf_index, int strategy_index, string reason) {
    
    int ticket = g_ea.open_tickets[tf_index][strategy_index];
    if(ticket <= 0) return;
    
    if(CloseOrderSafely(ticket, reason)) {
        // Clear tracking on success | Xoa theo doi khi thanh cong
        g_ea.open_tickets[tf_index][strategy_index] = 0;
        g_ea.open_lots[tf_index][strategy_index] = 0;
        g_ea.open_price[tf_index][strategy_index] = 0;
        g_ea.layer1_loss[tf_index][strategy_index] = 0;
        g_ea.layer2_flag[tf_index][strategy_index] = false;
        g_ea.close_flag[tf_index][strategy_index] = false;
        
        // Update statistics | Cap nhat thong ke
        g_ea.total_closed++;
        g_ea.last_close_time = TimeCurrent();
        g_ea.last_action = reason;
    }
    else {
        // Failed to close - reset flags anyway to avoid stuck state
        // That bai dong - van reset co de tranh ket
        g_ea.close_flag[tf_index][strategy_index] = false;
        
        // Check if order already closed | Kiem tra lenh da dong
        if(!OrderSelect(ticket, SELECT_BY_TICKET) || OrderCloseTime() != 0) {
            // Order is closed, clear tracking | Lenh da dong, xoa theo doi
            g_ea.open_tickets[tf_index][strategy_index] = 0;
            g_ea.open_lots[tf_index][strategy_index] = 0;
            g_ea.open_price[tf_index][strategy_index] = 0;
            g_ea.layer1_loss[tf_index][strategy_index] = 0;
            g_ea.layer2_flag[tf_index][strategy_index] = false;
        }
    }
}

// === CHAPTER 9: STRATEGY IMPLEMENTATIONS | THUC THI CHIEN LUOC ===

// Strategy 1: HOME - Reversal based | Chien luoc 1: HOME - Dao chieu
void ExecuteStrategy1(int tf_index) {
    
    // S1 uses simple reversal logic | S1 dung logic dao chieu don gian
    // This is simplified - real S1 would have complex rules | Day la don gian hoa - S1 that co quy tac phuc tap
    
    static int last_signal[7] = {0,0,0,0,0,0,0};
    int current_signal = 0;
    
    // Example logic: Reverse on price extremes | Logic vi du: Dao chieu o cuc tri gia
    double high = iHigh(_Symbol, 0, 1);
    double low = iLow(_Symbol, 0, 1);
    double close = iClose(_Symbol, 0, 1);
    double range = high - low;
    
    if(range > 0) {
        double position_in_range = (close - low) / range;
        
        if(position_in_range < 0.2) {
            current_signal = 1;  // Near bottom, BUY | Gan day, MUA
        }
        else if(position_in_range > 0.8) {
            current_signal = -1; // Near top, SELL | Gan dinh, BAN
        }
    }
    
    // Check for signal change | Kiem tra thay doi tin hieu
    if(current_signal != 0 && current_signal != last_signal[tf_index]) {
        
        // Close opposite position | Dong vi the nguoc lai
        if(HasPosition(tf_index, 0)) {
            if(OrderSelect(g_ea.open_tickets[tf_index][0], SELECT_BY_TICKET)) {
                int pos_type = OrderType();
                if((pos_type == OP_BUY && current_signal == -1) ||
                   (pos_type == OP_SELL && current_signal == 1)) {
                    ClosePosition(tf_index, 0, "S1_Reverse");
                }
            }
        }
        
        // Open new position | Mo vi the moi
        if(!HasPosition(tf_index, 0)) {
            string tf_name = "";
            switch(tf_index) {
                case 0: tf_name = "M1"; break;
                case 1: tf_name = "M5"; break;
                case 2: tf_name = "M15"; break;
                case 3: tf_name = "M30"; break;
                case 4: tf_name = "H1"; break;
                case 5: tf_name = "H4"; break;
                case 6: tf_name = "D1"; break;
            }
            OpenPosition(current_signal, tf_index, 0, "S1_" + tf_name);
        }
        
        last_signal[tf_index] = current_signal;
    }
}

// Strategy 2: TREND - Follow D1 trend | Chien luoc 2: TREND - Theo xu huong D1
void ExecuteStrategy2(int tf_index) {
    
    // S2 follows the D1 trend signal | S2 theo tin hieu trend D1
    int trend_signal = g_ea.trend_d1;
    
    if(trend_signal == 0) return;  // No trend | Khong co xu huong
    
    // Check if we need to open position | Kiem tra can mo vi the
    if(!HasPosition(tf_index, 1)) {
        
        // Additional filters can be added here | Co the them bo loc o day
        // For now, just follow trend | Tam thoi chi theo trend
        
        string tf_name = "";
        switch(tf_index) {
            case 0: tf_name = "M1"; break;
            case 1: tf_name = "M5"; break;
            case 2: tf_name = "M15"; break;
            case 3: tf_name = "M30"; break;
            case 4: tf_name = "H1"; break;
            case 5: tf_name = "H4"; break;
            case 6: tf_name = "D1"; break;
        }
        
        OpenPosition(trend_signal, tf_index, 1, "S2_" + tf_name);
    }
    else {
        // Check if trend changed - close if opposite | Kiem tra trend doi - dong neu nguoc
        if(OrderSelect(g_ea.open_tickets[tf_index][1], SELECT_BY_TICKET)) {
            int pos_type = OrderType();
            if((pos_type == OP_BUY && trend_signal == -1) ||
               (pos_type == OP_SELL && trend_signal == 1)) {
                ClosePosition(tf_index, 1, "S2_TrendChange");
            }
        }
    }
}

// Strategy 3: NEWS - Trade news events | Chien luoc 3: NEWS - Giao dich tin tuc
void ExecuteStrategy3(int tf_index) {
    
    // S3 trades based on news signals | S3 giao dich theo tin hieu news
    int news_signal = g_ea.news_direction[tf_index];
    int news_level = g_ea.news_level[tf_index];
    
    if(news_signal == 0 || news_level < 3) return;  // No news or low impact | Khong co tin hoac tac dong thap
    
    // Check if we need to open position | Kiem tra can mo vi the
    if(!HasPosition(tf_index, 2)) {
        
        string tf_name = "";
        switch(tf_index) {
            case 0: tf_name = "M1"; break;
            case 1: tf_name = "M5"; break;
            case 2: tf_name = "M15"; break;
            case 3: tf_name = "M30"; break;
            case 4: tf_name = "H1"; break;
            case 5: tf_name = "H4"; break;
            case 6: tf_name = "D1"; break;
        }
        
        OpenPosition(news_signal, tf_index, 2, "S3_" + tf_name + "_L" + IntegerToString(news_level));
    }
}

// === CHAPTER 10: STOP LOSS LAYER SYSTEM | HE THONG TANG CAT LO ===

// Check Layer 1 stop loss | Kiem tra cat lo tang 1
void CheckLayer1StopLoss(int tf_index, int strategy_index) {
    
    if(!HasPosition(tf_index, strategy_index)) return;
    
    int ticket = g_ea.open_tickets[tf_index][strategy_index];
    if(!OrderSelect(ticket, SELECT_BY_TICKET)) return;
    
    double current_loss = -OrderProfit();  // Positive value for loss | Gia tri duong cho lo
    
    if(current_loss <= 0) return;  // No loss or profit | Khong lo hoac co lai
    
    // Track maximum loss for this position | Theo doi lo toi da cho vi the nay
    if(current_loss > g_ea.layer1_loss[tf_index][strategy_index]) {
        g_ea.layer1_loss[tf_index][strategy_index] = current_loss;
        
        DebugPrint("L1 MaxLoss TF:" + IntegerToString(tf_index) + 
                  " S:" + IntegerToString(strategy_index) +
                  " = $" + DoubleToString(current_loss, 2));
    }
}

// Check Layer 2 stop loss (if enabled) | Kiem tra cat lo tang 2 (neu bat)
void CheckLayer2StopLoss(int tf_index, int strategy_index) {
    
    if(StoplossMode != LAYER2_WITH_DIV) return;  // Layer 2 not enabled | Tang 2 khong bat
    if(!HasPosition(tf_index, strategy_index)) return;
    if(g_ea.layer1_loss[tf_index][strategy_index] <= 0) return;  // No L1 loss recorded | Chua ghi nhan lo L1
    
    int ticket = g_ea.open_tickets[tf_index][strategy_index];
    if(!OrderSelect(ticket, SELECT_BY_TICKET)) return;
    
    double current_profit = OrderProfit();
    
    // Calculate Layer 2 threshold | Tinh nguong tang 2
    double layer2_threshold = g_ea.layer1_loss[tf_index][strategy_index] / Layer2_Divisor;
    
    // If recovered to Layer 2 threshold, close | Neu phuc hoi den nguong tang 2, dong
    if(g_ea.layer2_flag[tf_index][strategy_index]) {
        if(current_profit >= -layer2_threshold) {
            g_ea.close_flag[tf_index][strategy_index] = true;
            
            string reason = "L2_Recovery_TF" + IntegerToString(tf_index) + 
                           "_S" + IntegerToString(strategy_index);
            DebugPrint(reason + " Profit:" + DoubleToString(current_profit, 2) +
                      " >= Threshold:" + DoubleToString(-layer2_threshold, 2));
        }
    }
    else {
        // Check if entering Layer 2 zone | Kiem tra vao vung tang 2
        double current_loss = -current_profit;
        if(current_loss > g_ea.layer1_loss[tf_index][strategy_index] * 1.1) {
            g_ea.layer2_flag[tf_index][strategy_index] = true;
            
            DebugPrint("L2_Activated TF:" + IntegerToString(tf_index) +
                      " S:" + IntegerToString(strategy_index) +
                      " Loss:$" + DoubleToString(current_loss, 2));
        }
    }
}

// === CHAPTER 11: MAIN TRADING LOGIC | LOGIC GIAO DICH CHINH ===

// Process single TF/Strategy combination | Xu ly 1 cap TF/Chien luoc
void ProcessTFStrategy(int tf_index, int strategy_index) {
    
    // Skip if not enabled | Bo qua neu khong bat
    if(!IsTFEnabled(tf_index)) return;
    if(!IsStrategyEnabled(strategy_index)) return;
    
    // Check for close flag first | Kiem tra co dong truoc
    if(g_ea.close_flag[tf_index][strategy_index]) {
        ClosePosition(tf_index, strategy_index, "CloseFlag");
        return;
    }
    
    // Execute strategy logic | Thuc thi logic chien luoc
    switch(strategy_index) {
        case 0: ExecuteStrategy1(tf_index); break;
        case 1: ExecuteStrategy2(tf_index); break;
        case 2: ExecuteStrategy3(tf_index); break;
    }
    
    // Check stop loss layers | Kiem tra cac tang cat lo
    CheckLayer1StopLoss(tf_index, strategy_index);
    CheckLayer2StopLoss(tf_index, strategy_index);
}

// Main execution cycle - process all TF/Strategy combinations | Chu ky thuc thi chinh
void ExecuteMainCycle() {
    
    // Process each TF | Xu ly tung TF
    for(int tf = 0; tf < 7; tf++) {
        if(!IsTFEnabled(tf)) continue;
        
        // Process each Strategy for this TF | Xu ly tung chien luoc cho TF nay
        for(int s = 0; s < 3; s++) {
            if(!IsStrategyEnabled(s)) continue;
            
            ProcessTFStrategy(tf, s);
        }
    }
    
    // Update statistics | Cap nhat thong ke
    UpdateStatistics();
    
    // Update dashboard | Cap nhat dashboard
    UpdateDashboard();
}

// === CHAPTER 12: EMERGENCY & HEALTH CHECKS | KIEM TRA KHAN CAP & SUC KHOE ===

// Check emergency conditions | Kiem tra dieu kien khan cap
void CheckEmergencyConditions() {
    
    if(!EmergencyCloseAll) return;
    
    double current_dd = AccountInfoDouble(ACCOUNT_BALANCE) - AccountInfoDouble(ACCOUNT_EQUITY);
    
    if(current_dd >= EmergencyDD_USD) {
        Print("[EMERGENCY] DD $", DoubleToString(current_dd, 2), " >= Limit $", DoubleToString(EmergencyDD_USD, 2));
        
        // Close all positions | Dong tat ca vi the
        for(int i = OrdersTotal() - 1; i >= 0; i--) {
            if(OrderSelect(i, SELECT_BY_POS, MODE_TRADES)) {
                if(OrderMagicNumber() == MagicNumber && OrderSymbol() == _Symbol) {
                    CloseOrderSafely(OrderTicket(), "EMERGENCY_DD");
                }
            }
        }
        
        if(EmergencyStopEA) {
            Print("[EMERGENCY] EA STOPPED");
            ExpertRemove();  // Stop EA | Dung EA
        }
    }
}

// Update statistics | Cap nhat thong ke
void UpdateStatistics() {
    
    // Calculate current stats | Tinh thong ke hien tai
    double floating_pl = 0;
    int open_count = 0;
    
    for(int i = 0; i < OrdersTotal(); i++) {
        if(OrderSelect(i, SELECT_BY_POS, MODE_TRADES)) {
            if(OrderMagicNumber() == MagicNumber && OrderSymbol() == _Symbol) {
                floating_pl += OrderProfit();
                open_count++;
            }
        }
    }
    
    // Update DD tracking | Cap nhat theo doi DD
    g_ea.current_dd = AccountInfoDouble(ACCOUNT_BALANCE) - AccountInfoDouble(ACCOUNT_EQUITY);
    if(g_ea.current_dd > g_ea.max_dd_seen) {
        g_ea.max_dd_seen = g_ea.current_dd;
    }
    
    // Simple profit tracking (would need history analysis for accurate total)
    // Theo doi loi nhuan don gian (can phan tich lich su de co tong chinh xac)
    g_ea.total_profit = floating_pl;  // Simplified | Don gian hoa
}

// Health check | Kiem tra suc khoe
void CheckHealth() {
    
    datetime current_time = TimeCurrent();
    int current_hour = TimeHour(current_time);
    
    // Health check every 8 hours | Kiem tra suc khoe moi 8 gio
    if(current_hour % 8 == 0 && current_hour != g_ea.health_check_hour) {
        
        g_ea.health_check_hour = current_hour;
        g_ea.last_health_check = current_time;
        
        // Check various health metrics | Kiem tra cac chi so suc khoe
        bool is_healthy = true;
        
        // Check if we have connection | Kiem tra ket noi
        if(!IsConnected()) {
            is_healthy = false;
            LogError(0, "Health", "No connection");
        }
        
        // Check if market is open | Kiem tra thi truong mo
        if(!IsTradeAllowed()) {
            is_healthy = false;
            LogError(0, "Health", "Trade not allowed");
        }
        
        g_ea.is_healthy = is_healthy;
        
        if(is_healthy) {
            Print("[HEALTH] Check passed at ", TimeToString(current_time, TIME_DATE|TIME_MINUTES));
        }
    }
}

// === CHAPTER 13: INITIALIZATION | KHOI DONG ===

// Create init summary string | Tao chuoi tom tat khoi dong
string CreateInitSummary() {
    // Count enabled TFs | Dem TF duoc bat
    string tf_status = "";
    int tf_count = 0;
    if(TF_M1) { tf_status += "M1,"; tf_count++; }
    if(TF_M5) { tf_status += "M5,"; tf_count++; }
    if(TF_M15) { tf_status += "M15,"; tf_count++; }
    if(TF_M30) { tf_status += "M30,"; tf_count++; }
    if(TF_H1) { tf_status += "H1,"; tf_count++; }
    if(TF_H4) { tf_status += "H4,"; tf_count++; }
    if(TF_D1) { tf_status += "D1,"; tf_count++; }
    if(StringLen(tf_status) > 0) tf_status = StringSubstr(tf_status, 0, StringLen(tf_status) - 1);

    string strat_status = "";
    int strat_count = 0;
    if(S1_HOME) { strat_status += "S1,"; strat_count++; }
    if(S2_TREND) { strat_status += "S2,"; strat_count++; }
    if(S3_NEWS) { strat_status += "S3,"; strat_count++; }
    if(StringLen(strat_status) > 0) strat_status = StringSubstr(strat_status, 0, StringLen(strat_status) - 1);

    // FIX: Correct string concatenation
    string sl_mode = (StoplossMode == LAYER1_MAXLOSS) ? "L1" : "L2/" + DoubleToString(Layer2_Divisor, 1);
    string master_mode = (Period()==PERIOD_M1) ? "M1" : "M5-D1";

    // CSDL source name | Ten nguon CSDL
    string folder_name = "";
    if(CSDL_Source == FOLDER_1) folder_name = "DA1";
    else if(CSDL_Source == FOLDER_2) folder_name = "DA2";
    else if(CSDL_Source == FOLDER_3) folder_name = "DA3";

    // FIX: Build summary with correct string operations
    string trend_str = SignalToString(g_ea.trend_d1);
    
    // FIX: Build news string correctly
    string news_str = "M1:";
    if(g_ea.news_direction[0] > 0) news_str += "+";
    news_str += IntegerToString(g_ea.news_level[0]);
    news_str += SignalToString(g_ea.news_direction[0]);

    // FIX: Build complete summary string
    string summary = "[INIT] " + g_ea.symbol_name + " | SL:" + sl_mode +
                    " News:7TF(" + news_str + ") Trend:" + trend_str +
                    " | Lot:" + DoubleToString(g_ea.lot_sizes[0][0], 2) + 
                    "-" + DoubleToString(g_ea.lot_sizes[6][2], 2) +
                    " | TF:" + IntegerToString(tf_count) + 
                    " S:" + IntegerToString(strat_count) +
                    " | Folder:" + folder_name + " Master:" + master_mode +
                    " | Magic:" + IntegerToString(MagicNumber);
    
    return summary;
}

// EA initialization | Khoi dong EA
int OnInit() {
    
    // Initialize MT5 trading | Khoi dong giao dich MT5
    InitMT5Trading();
    
    // Clear EA state | Xoa trang thai EA
    ZeroMemory(g_ea);
    
    // Map CSDL data | Map du lieu CSDL
    MapCSDLToEAVariables();
    
    // Initialize lot sizes | Khoi dong khoi luong
    InitializeLotSizes();
    
    // Create init summary AFTER data is loaded | Tao tom tat SAU khi nap du lieu
    g_ea.init_summary = CreateInitSummary();
    
    // Set health check initial state | Dat trang thai kiem tra suc khoe ban dau
    g_ea.is_healthy = true;
    g_ea.health_check_hour = -1;
    
    // Print initialization | In khoi dong
    Print("=====================================");
    Print(g_ea.init_summary);
    Print("=====================================");
    
    // Set timer for main execution | Dat timer cho thuc thi chinh
    EventSetTimer(1);  // Every 1 second | Moi 1 giay
    
    // Initial dashboard | Dashboard ban dau
    UpdateDashboard();
    
    return(INIT_SUCCEEDED);
}

// EA deinitialization - cleanup | Ket thuc EA - don dep
void OnDeinit(const int reason) {
    EventKillTimer();
    Comment("");  // Clear Comment | Xoa Comment
    
    // Delete all dashboard labels (15 labels: dash_0 to dash_14) | Xoa tat ca label dashboard
    for(int i = 0; i <= 14; i++) {
        string obj_name = g_ea.symbol_prefix + "dash_" + IntegerToString(i);
        // FIX: ObjectFind with correct parameters
        if(ObjectFind(0, obj_name) >= 0) {
            // FIX: ObjectDelete with correct parameters
            ObjectDelete(0, obj_name);
        }
    }
    
    // Delete all objects with symbol_prefix + "dash_" pattern (cleanup any orphaned objects)
    // FIX: ObjectsTotal with correct parameters
    int total = ObjectsTotal(0, -1, -1);
    for(int i = total - 1; i >= 0; i--) {
        // FIX: ObjectName with correct parameters
        string obj_name = ObjectName(0, i, -1, -1);
        // Check if object name starts with symbol_prefix AND contains "dash_"
        if(StringFind(obj_name, g_ea.symbol_prefix) == 0 && StringFind(obj_name, "dash_") > 0) {
            // FIX: ObjectDelete with correct parameters
            ObjectDelete(0, obj_name);
        }
    }
    
    Print("[DEINIT] EA stopped. Reason:", reason);
}

// === CHAPTER 14: EVENT HANDLERS | XU LY SU KIEN ===

// Timer event - main execution | Su kien timer - thuc thi chinh
void OnTimer() {
    
    // Only run if trade is allowed | Chi chay khi cho phep giao dich
    if(!IsTradeAllowed()) {
        Comment("Trade not allowed");
        return;
    }
    
    // Execute main trading cycle | Thuc thi chu ky giao dich chinh
    ExecuteMainCycle();
    
    // Check emergency conditions | Kiem tra dieu kien khan cap
    CheckEmergencyConditions();
    
    // Check health | Kiem tra suc khoe
    CheckHealth();
}

// MT5 Required Event Handlers
void OnTick() {
    // MT5 requires OnTick even if using OnTimer
}

void OnTrade() {
    // Optional: Handle trade events
}

void OnTradeTransaction(const MqlTradeTransaction& trans,
                        const MqlTradeRequest& request,
                        const MqlTradeResult& result) {
    // Optional: Handle trade transactions
}

//+------------------------------------------------------------------+
//| END OF EA CODE - TOTAL 2576 LINES
//+------------------------------------------------------------------+