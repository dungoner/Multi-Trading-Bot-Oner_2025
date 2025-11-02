//+------------------------------------------------------------------+
//| EAs_MTF_ONER_V2_MT5
//| Multi Timeframe Expert Advisor for MT5
//| 7 TF × 3 Strategies × Multi-Symbol = Unlimited positions
//| Version: 2.0 (MT5)
//+------------------------------------------------------------------+
#property copyright "EAs_MTF_ONER_V2_MT5"
#property version "2.00"
#property strict

#include <Trade\Trade.mqh>

// Global trade object for MT5 position management
CTrade trade;

// MT4 compatibility constants for order types
#define OP_BUY ORDER_TYPE_BUY
#define OP_SELL ORDER_TYPE_SELL

//=============================================================================
//  PART 1: USER INPUTS (30 inputs + 4 separators)
//=============================================================================

input string _________Menu_A___ = "___A. CORE SETTINGS _________";  //

//--- A.1 Timeframe toggles (7)
input bool TF_M1 = true;   // M1 (Signal Sym_M1 Time)
input bool TF_M5 = true;   // M5 (Buy/Sell Symbol_M5)
input bool TF_M15 = true;  // M15 (Signal Symbol_15)
input bool TF_M30 = true;  // M30 (Buy/Sell Symbol_M30)
input bool TF_H1 = true;   // H1 (Signal Symbol_H1 )
input bool TF_H4 = true;   // H4 (Buy/Sell Symbol_H4 )
input bool TF_D1 = true;   // D1 (Signal Symbol_D1)

//--- A.2 Strategy toggles (3)
input bool S1_HOME = true;   // S1: Binary (Home signal)
input bool S2_TREND = true;  // S2: Trend (Follow D1)
input bool S3_NEWS = true;   // S3: News (High impact)

//--- A.3 Risk management (2)
input double FixedLotSize = 0.1;           // Lot size (0.01-1.0 recommended)
input double MaxLoss_Fallback = -1000.0;   // Max loss fallback ($USD if CSDL fails)

//--- A.4 Data source (1)
enum CSDL_SOURCE_ENUM {
    FOLDER_1 = 0,  // DataAutoOner
    FOLDER_2 = 1,  // DataAutoOner2 (Default)
    FOLDER_3 = 2,  // DataAutoOner3
};
input CSDL_SOURCE_ENUM CSDL_Source = FOLDER_2;  // CSDL folder (signal source)

input string _________Sep_B___ = "___B. STRATEGY CONFIG _________";  //

//--- B.1 S1 NEWS Filter (3)
input bool S1_UseNewsFilter = true;            // S1: Use NEWS filter (TRUE=strict, FALSE=basic)
input int MinNewsLevelS1 = 20;                 // S1: Min NEWS level (20-70, higher=stricter)
input bool S1_RequireNewsDirection = true;     // S1: Match NEWS direction (signal==news!)

//--- B.2 S2 TREND Mode (1)
enum S2_TREND_MODE {
    S2_FOLLOW_D1 = 0,    // Follow D1 (Auto)
    S2_FORCE_BUY = 1,    // Force BUY (manual override)
    S2_FORCE_SELL = -1   // Force SELL (manual override)
};
input S2_TREND_MODE S2_TrendMode = S2_FOLLOW_D1;  // S2: Trend (D1 auto/manual)

//--- B.3 S3 NEWS Configuration (4)
input int MinNewsLevelS3 = 20;         // S3: Min NEWS level (20-70)
input bool EnableBonusNews = true;     // S3: Enable Bonus (extra on high NEWS)
input int BonusOrderCount = 2;         // S3: Bonus count (1-5 orders)
input int MinNewsLevelBonus = 20;      // S3: Min NEWS for Bonus (threshold)
input double BonusLotMultiplier = 1.0; // S3: Bonus lot multiplier (1.0-10.0)

input string _________Sep_C___ = "___C. MULTI-SYMBOL (MT5) _________";  //

// Multi-symbol support (MT5 only)
input bool EnableMultiSymbol = false;                          // Enable multi-symbol mode
input string Symbols = "XAUUSD,EURUSD,GBPUSD";                 // Symbols (comma-separated)
input int MaxSymbols = 10;                                     // Max symbols (1-10)

input string _________Sep_D___ = "___D. RISK PROTECTION _________";  //

//--- C.1 Stoploss mode (3)
enum STOPLOSS_MODE {
    NONE = 0,            // No stoploss (close by signal only)
    LAYER1_MAXLOSS = 1,  // Layer1: max_loss × lot (from CSDL)
    LAYER2_MARGIN = 2    // Layer2: margin/divisor (emergency)
};
input STOPLOSS_MODE StoplossMode = LAYER1_MAXLOSS;  // Stoploss mode (0=OFF, 1=CSDL, 2=Margin)
input double Layer2_Divisor = 5.0;  // Layer2 divisor (margin/-5 = threshold)

//--- C.2 Take profit (2)
input bool   UseTakeProfit = false;  // Enable take profit (FALSE=OFF, TRUE=ON)
input double TakeProfit_Multiplier = 3;  // TP multiplier (0.5=5%, 1.0=10%, 5.0=50%)

input string _________Sep_E___ = "___E. AUXILIARY SETTINGS _________";  //

//--- D.1 Performance (1)
input bool UseEvenOddMode = false;  // Even/odd split mode (load balancing)

//--- D.2 Health check & reset (2)
input bool EnableWeekendReset = true;   // Weekend reset (auto close Friday 23:50)
input bool EnableHealthCheck = true;    // Health check (8h/16h SPY bot status)

//--- D.3 Display (2)
input bool ShowDashboard = true;  // Show dashboard (on-chart info)
input bool DebugMode = false;      // Debug mode (verbose logging)

//=============================================================================
//  PART 2: DATA STRUCTURES (1 struct)
//=============================================================================

struct CSDLLoveRow {
    double max_loss;   // Col 1: Max loss per 1 LOT
    long timestamp;    // Col 2: Timestamp
    int signal;        // Col 3: Signal (1=BUY,-1=SELL,0=NONE)
    double pricediff;  // Col 4: Price diff USD (unused)
    int timediff;      // Col 5: Time diff minutes (unused)
    int news;          // Col 6: News CASCADE (±11-16)
};

//=============================================================================
//  PART 3: EA DATA STRUCTURE (116 vars in struct)
//=============================================================================
// Contains ALL EA data for current symbol (learned from SPY Bot)
// Each EA instance on different chart has its OWN struct
// This prevents conflicts when running multiple symbols simultaneously
//=============================================================================

struct EASymbolData {
    // Symbol & File info (4 vars)
    string symbol_name;          // Symbol name (BTCUSD, LTCUSD...)
    string symbol_prefix;        // Symbol prefix with underscore
    string csdl_folder;          // CSDL folder path
    string csdl_filename;        // Full CSDL filename

    // CSDL rows (7 rows)
    CSDLLoveRow csdl_rows[7];    // 7 rows for 7 TF (M1-D1)

    // Core signals (14 vars = 2×7 TF)
    int signal_old[7];           // Old signal for comparison
    datetime timestamp_old[7];   // Old timestamp for comparison
    // NOTE: signal_new, timestamp_new removed - use csdl_rows[tf].signal/timestamp directly
    // CHU THICH: Da loai bo signal_new, timestamp_new - dung truc tiep csdl_rows[tf].signal/timestamp

    // Magic numbers (21 vars)
    int magic_numbers[7][3];     // [TF][Strategy]: [0]=S1, [1]=S2, [2]=S3

    // Lot sizes (21 vars - pre-calculated)
    double lot_sizes[7][3];      // [TF][Strategy]: [0]=S1, [1]=S2, [2]=S3

    // Strategy conditions (3 vars)
    int trend_d1;                // S2: D1 trend (1=BUY,-1=SELL,0=NONE)
    int news_level;              // S3: News level (abs value)
    int news_direction;          // S3: News direction (-1/0/1)

    // Stoploss thresholds (21 vars)
    double layer1_thresholds[7][3];  // [TF][Strategy]: [0]=S1, [1]=S2, [2]=S3

    // Position flags (21 vars)
    int position_flags[7][3];    // [TF][Strategy]: [0]=S1, [1]=S2, [2]=S3

    // Global state vars (5 vars) - Prevent multi-symbol conflicts
    bool first_run_completed;      // Replaced g_first_run_completed
    int weekend_last_day;           // Replaced static last_day
    int health_last_check_hour;     // Replaced static last_check_hour
    datetime timer_last_run_time;   // Replaced static last_run_time
    string init_summary;            // Init summary for final print in RESTORE
};

// Single global instance for current chart (single-symbol mode)
EASymbolData g_ea;

// Multi-symbol support (MT5)
EASymbolData g_ea_array[10];  // Max 10 symbols
int g_ea_count = 0;           // Number of active symbols

//=============================================================================
//  PART 4: GLOBAL STATE (0 var)
//=============================================================================
// All global state vars moved to g_ea struct (lines 118-122)

//=============================================================================
//  PART 4A: GLOBAL CONSTANTS (2 arrays)
//=============================================================================
// Shared by all functions to avoid duplication
// NOTE: These are CONST - safe for multi-symbol usage
// 7 TF and 3 Strategies are FIXED by CSDL design
//=============================================================================

const string G_TF_NAMES[7] = {"M1", "M5", "M15", "M30", "H1", "H4", "D1"};
const string G_STRATEGY_NAMES[3] = {"S1", "S2", "S3"};

//=============================================================================
//  PART 5: UTILITY FUNCTIONS (11 functions)
//=============================================================================

// Check if TF is enabled by user
bool IsTFEnabled(int tf_index) {
    if(tf_index == 0) return TF_M1;
    if(tf_index == 1) return TF_M5;
    if(tf_index == 2) return TF_M15;
    if(tf_index == 3) return TF_M30;
    if(tf_index == 4) return TF_H1;
    if(tf_index == 5) return TF_H4;
    if(tf_index == 6) return TF_D1;
    return false;
}

// Print debug message if DebugMode enabled
void DebugPrint(string message) {
    if(!DebugMode) return;
    Print("[DEBUG] ", message);
}

// Log error with code, context and details
void LogError(int error_code, string context, string details) {
    Print("[ERROR] CODE:", error_code, " CONTEXT:", context, " DETAILS:", details);
}

// Convert signal integer to readable string
string SignalToString(int signal) {
    if(signal == 1) return "BUY";
    if(signal == -1) return "SELL";
    return "NONE";
}

// Normalize lot size to broker requirements
double NormalizeLotSize(double lot_size) {
    double min_lot = SymbolInfoDouble(Symbol(), SYMBOL_VOLUME_MIN);
    double max_lot = SymbolInfoDouble(Symbol(), SYMBOL_VOLUME_MAX);
    double lot_step = SymbolInfoDouble(Symbol(), SYMBOL_VOLUME_STEP);

    if(lot_size < min_lot) lot_size = min_lot;
    if(lot_size > max_lot) lot_size = max_lot;

    lot_size = NormalizeDouble(lot_size / lot_step, 0) * lot_step;
    return lot_size;
}

// Close order with smart error handling (max 1 retry)
// IMPORTANT: EA never stops on errors, only logs
// Returns: true (success) or false, caller must reset flags
bool CloseOrderSafely(int ticket, string reason) {

    // Try to select position
    if(!PositionSelectByTicket(ticket)) {
        int error = GetLastError();

        // Error 4108: Invalid ticket ? Position already closed or doesn't exist
        // Loi 4108: Ticket sai ? Vi the da dong hoac khong ton tai
        if(error == 4108) {
            Print("[CLOSE_FAIL] ", reason, " #", IntegerToString(ticket), " Err:4108 (Invalid ticket) - Skip, EA continues");
            return false; // Caller must reset flag
        }

        Print("[CLOSE_FAIL] ", reason, " #", IntegerToString(ticket), " Err:", IntegerToString(error), " (Select failed) - Skip, EA continues");
        return false;
    }

    // MT5: If position selected successfully, it's open (no need to check close time)
    // MT5: Neu chon vi the thanh cong, no dang mo (khong can kiem tra thoi gian dong)

    // Try 1: Close position
    bool result = trade.PositionClose(ticket, 3);

    if(result) {
        // Success - detailed log printed by caller
        return true;
    }

    // FAILED - Check error
    int error = GetLastError();

    // Case 1: Context busy OR Requote ? Retry 1 time
    // TH 1: MT5 ban HOAC Gia thay doi ? Thu lai 1 lan
    if(error == 10018 || error == 10021) {  // MT5: ERR_TRADE_TIMEOUT, ERR_TRADE_MARKET_CLOSED
        Print("[CLOSE_FAIL] ", reason, " #", IntegerToString(ticket), " Err:", IntegerToString(error), " (Retry 1x)");
        Sleep(100);

        if(!PositionSelectByTicket(ticket)) {
            Print("[CLOSE_FAIL] ", reason, " #", IntegerToString(ticket), " Retry select failed - Skip, EA continues");
            return false;
        }

        result = trade.PositionClose(ticket, 3);

        if(result) {
            // Retry success - detailed log printed by caller
            return true;
        }

        error = GetLastError();
        Print("[CLOSE_FAIL] ", reason, " #", IntegerToString(ticket), " Retry Err:", IntegerToString(error), " - Skip, EA continues");
        return false;
    }

    // Case 2: Other errors ? Log and continue
    // TH 2: Loi khac ? Ghi nhan va tiep tuc
    Print("[CLOSE_FAIL] ", reason, " #", IntegerToString(ticket), " Err:", IntegerToString(error), " - Skip, EA continues");
    return false;
}

// Draw arrow on chart - simple version

// Open order with smart error handling (max 1 retry)
// IMPORTANT: EA never stops on errors, only logs
// Returns: ticket (>0) or -1, caller must check and handle flag
int OrderSendSafe(int tf, string symbol, int cmd, double lot_smart,
                  double price, int slippage,
                  string comment, int magic, color arrow_color) {

    // Set magic number for this trade
    trade.SetExpertMagicNumber(magic);
    trade.SetDeviationInPoints(slippage);

    // Update price (MT5 uses SymbolInfoDouble)
    if(cmd == OP_BUY) price = SymbolInfoDouble(symbol, SYMBOL_ASK);
    else if(cmd == OP_SELL) price = SymbolInfoDouble(symbol, SYMBOL_BID);

    // Try 1: Smart lot
    bool result = false;
    if(cmd == OP_BUY) {
        result = trade.Buy(lot_smart, symbol, price, 0, 0, comment);
    } else if(cmd == OP_SELL) {
        result = trade.Sell(lot_smart, symbol, price, 0, 0, comment);
    }

    if(result) {
        // Success - detailed log printed by strategy caller
        return (int)trade.ResultOrder();
    }

    // FAILED - Check error
    int error = GetLastError();

    // Case 1: Not enough money OR Invalid volume ? Retry with 0.01 lot
    // TH 1: Het von HOAC Lot sai ? Thu lai voi 0.01 lot
    if(error == 10019 || error == 10014) {  // MT5: ERR_TRADE_NOT_ENOUGH_MONEY, ERR_TRADE_VOLUME_LIMIT
        Print("[ORDER_FAIL] ", comment, " Err:", IntegerToString(error), " (Retry 0.01 lot)");

        if(cmd == OP_BUY) {
            result = trade.Buy(0.01, symbol, price, 0, 0, comment + "_Min");
        } else if(cmd == OP_SELL) {
            result = trade.Sell(0.01, symbol, price, 0, 0, comment + "_Min");
        }

        if(result) {
            // Fallback success - detailed log printed by strategy caller
            return (int)trade.ResultOrder();
        }

        error = GetLastError();
        Print("[ORDER_FAIL] ", comment, "_Min Err:", IntegerToString(error), " - Skip, EA continues");
        return -1;
    }

    // Case 2: Context busy OR Requote ? Retry 1 time
    // TH 2: MT5 ban HOAC Gia thay doi ? Thu lai 1 lan
    if(error == 10018 || error == 10004) {  // MT5: ERR_TRADE_TIMEOUT, ERR_TRADE_REQUOTE
        Print("[ORDER_FAIL] ", comment, " Err:", IntegerToString(error), " (Retry 1x)");
        Sleep(100);

        if(cmd == OP_BUY) price = SymbolInfoDouble(symbol, SYMBOL_ASK);
        else if(cmd == OP_SELL) price = SymbolInfoDouble(symbol, SYMBOL_BID);

        if(cmd == OP_BUY) {
            result = trade.Buy(lot_smart, symbol, price, 0, 0, comment);
        } else if(cmd == OP_SELL) {
            result = trade.Sell(lot_smart, symbol, price, 0, 0, comment);
        }

        if(result) {
            // Retry success - detailed log printed by strategy caller
            return (int)trade.ResultOrder();
        }

        error = GetLastError();
        Print("[ORDER_FAIL] ", comment, " Retry Err:", IntegerToString(error), " - Skip, EA continues");
        return -1;
    }

    // Case 3: Other errors ? Log and continue
    // TH 3: Loi khac ? Ghi nhan va tiep tuc
    Print("[ORDER_FAIL] ", comment, " Err:", IntegerToString(error), " - Skip, EA continues");
    return -1;
}

//=============================================================================
//  PART 6: SYMBOL & FILE MANAGEMENT (6 functions)
//=============================================================================

// Trim whitespace from string
string StringTrim(string input_string) {
    int start = 0;
    int end = StringLen(input_string) - 1;

    while(start <= end && StringGetCharacter(input_string, start) == 32) {
        start++;
    }

    while(end >= start && StringGetCharacter(input_string, end) == 32) {
        end--;
    }

    if(start > end) return "";
    return StringSubstr(input_string, start, end - start + 1);
}

// Discover symbol name from chart
string DiscoverSymbolFromChart() {
    string chart_symbol = Symbol();

    string normalized = chart_symbol;
    StringReplace(normalized, ".raw", "");
    StringReplace(normalized, ".a", "");
    StringReplace(normalized, ".b", "");
    StringReplace(normalized, ".c", "");
    StringReplace(normalized, "_", "");

    return normalized;
}

// Initialize symbol recognition from chart
bool InitializeSymbolRecognition() {
    g_ea.symbol_name = DiscoverSymbolFromChart();

    if(StringLen(g_ea.symbol_name) == 0) {
        LogError(4201, "InitializeSymbolRecognition", "Cannot detect symbol");
        return false;
    }

    DebugPrint("Symbol detected: " + g_ea.symbol_name);
    return true;
}

// Initialize symbol prefix with underscore
void InitializeSymbolPrefix() {
    g_ea.symbol_prefix = g_ea.symbol_name + "_";
}

// Build full CSDL filename path
void BuildCSDLFilename() {
    g_ea.csdl_filename = g_ea.csdl_folder + g_ea.symbol_name + "_LIVE.json";
    DebugPrint("CSDL file: " + g_ea.csdl_filename);
}

//=============================================================================
//  PART 7: CSDL PARSING (3 functions)
//=============================================================================
// ParseLoveRow() - Parse single row
// ParseCSDLLoveJSON() - Parse entire JSON
// TryReadFile() - Try read local file
// ReadCSDLFile() - Local file reading only

// Parse one row of CSDL data (6 columns)
bool ParseLoveRow(string row_data, int row_index) {
    // Column 1: max_loss
    int maxloss_pos = StringFind(row_data, "\"max_loss\":");
    if(maxloss_pos >= 0) {
        string temp = StringSubstr(row_data, maxloss_pos + 11);
        int comma = StringFind(temp, ",");
        if(comma > 0) {
            g_ea.csdl_rows[row_index].max_loss = StringToDouble(StringTrim(StringSubstr(temp, 0, comma)));
        }
    }

    // Column 2: timestamp
    int ts_pos = StringFind(row_data, "\"timestamp\":");
    if(ts_pos >= 0) {
        string temp = StringSubstr(row_data, ts_pos + 12);
        int comma = StringFind(temp, ",");
        if(comma > 0) {
            g_ea.csdl_rows[row_index].timestamp = (long)StringToInteger(StringTrim(StringSubstr(temp, 0, comma)));
        }
    }

    // Column 3: signal
    int signal_pos = StringFind(row_data, "\"signal\":");
    if(signal_pos >= 0) {
        string temp = StringSubstr(row_data, signal_pos + 9);
        int comma = StringFind(temp, ",");
        if(comma > 0) {
            g_ea.csdl_rows[row_index].signal = (int)StringToInteger(StringTrim(StringSubstr(temp, 0, comma)));
        }
    }

    // Column 4: pricediff (EA không dùng - nh?ng v?n parse)
    int pricediff_pos = StringFind(row_data, "\"pricediff\":");
    if(pricediff_pos >= 0) {
        string temp = StringSubstr(row_data, pricediff_pos + 12);
        int comma = StringFind(temp, ",");
        if(comma > 0) {
            g_ea.csdl_rows[row_index].pricediff = StringToDouble(StringTrim(StringSubstr(temp, 0, comma)));
        }
    }

    // Column 5: timediff (EA không dùng - nh?ng v?n parse)
    int timediff_pos = StringFind(row_data, "\"timediff\":");
    if(timediff_pos >= 0) {
        string temp = StringSubstr(row_data, timediff_pos + 11);
        int comma = StringFind(temp, ",");
        if(comma > 0) {
            g_ea.csdl_rows[row_index].timediff = (int)StringToInteger(StringTrim(StringSubstr(temp, 0, comma)));
        }
    }

    // Column 6: news (??i tên t? s1_news)
    int news_pos = StringFind(row_data, "\"news\":");
    if(news_pos >= 0) {
        string temp = StringSubstr(row_data, news_pos + 7);
        int comma = StringFind(temp, ",");
        int bracket = StringFind(temp, "}");
        int end_pos = (comma > 0 && comma < bracket) ? comma : bracket;
        if(end_pos > 0) {
            g_ea.csdl_rows[row_index].news = (int)StringToInteger(StringTrim(StringSubstr(temp, 0, end_pos)));
        }
    }

    return true;
}

// Parse CSDL LOVE JSON array (7 rows)
bool ParseCSDLLoveJSON(string json_content) {
    StringReplace(json_content, "[", "");
    StringReplace(json_content, "]", "");
    StringReplace(json_content, "\n", "");
    StringReplace(json_content, "\r", "");

    string rows[];
    int row_count = StringSplit(json_content, '}', rows);

    DebugPrint("LOVE JSON: Found " + IntegerToString(row_count) + " rows");

    int parsed_count = 0;
    for(int i = 0; i < 7 && i < row_count; i++) {
        string row_data = rows[i];
        StringReplace(row_data, ",{", "");
        StringReplace(row_data, "{", "");

        if(StringLen(row_data) < 10) continue;

        if(ParseLoveRow(row_data, i)) {
            parsed_count++;
        }
    }

    return (parsed_count >= 1);
}

// Helper: Try to read and parse file
bool TryReadFile(string filename) {
    int handle = FileOpen(filename, FILE_READ | FILE_TXT | FILE_SHARE_READ | FILE_SHARE_WRITE);
    if(handle == INVALID_HANDLE) return false;

    string json_content = "";
    while(!FileIsEnding(handle)) {
        json_content += FileReadString(handle);
    }
    FileClose(handle);

    if(StringLen(json_content) < 20) return false;
    if(!ParseCSDLLoveJSON(json_content)) return false;

    return true;  // SUCCESS
}

// Read CSDL from local file only
// Supports 3 sources: FOLDER_1, FOLDER_2, FOLDER_3
void ReadCSDLFile() {
    bool success = false;

    // ========== LOCAL FILE (FOLDER_1 / FOLDER_2 / FOLDER_3) ==========
    // TRY 1: Read main local file
    success = TryReadFile(g_ea.csdl_filename);

    if(!success) {
        // TRY 2: Wait 100ms and retry
        Sleep(100);
        success = TryReadFile(g_ea.csdl_filename);
    }

    if(!success) {
        // TRY 3: Read backup file in DataAutoOner (FOLDER_1)
        string backup_file = "DataAutoOner\\" + g_ea.symbol_name + "_LIVE.json";
        success = TryReadFile(backup_file);

        if(success) {
            Print("[BACKUP] Using DataAutoOner (FOLDER_1) file");
        }
    }

    // ========== FINAL CHECK ==========
    if(!success) {
        // ALL FAILED: Keep old data, continue (no spam warning - only debug)
        DebugPrint("[WARNING] All read attempts failed. Using old data.");
    }
}

//=============================================================================
//  PART 8: MAGIC NUMBER GENERATION (3 functions)
//=============================================================================

// Generate symbol hash from ALL characters using DJB2 algorithm
// This ensures unique hash for each symbol, preventing magic number collisions
int GenerateSymbolHash(string symbol) {
    int hash = 5381;  // DJB2 hash initial value

    // Process ALL characters in symbol name
    for(int i = 0; i < StringLen(symbol); i++) {
        int c = StringGetCharacter(symbol, i);
        hash = ((hash << 5) + hash) + c;  // hash * 33 + c (DJB2 formula)
    }

    // Make positive and limit to reasonable range (100-9999)
    hash = MathAbs(hash % 10000);  // Modulo 10000 = range 0-9999

    if(hash < 100) hash += 100;  // Minimum 100 to avoid small numbers

    return hash;
}

// Generate smart magic: hash + tf*1000 + strat*100
int GenerateSmartMagicNumber(string symbol, int tf_index, int strategy_index) {
    int symbol_hash = GenerateSymbolHash(symbol);
    int tf_code = tf_index * 1000;      // M1=0, M5=1000, M15=2000, ...
    int strategy_code = strategy_index * 100;  // S1=0, S2=100, S3=200

    return symbol_hash + tf_code + strategy_code;
}

// Generate all 21 magic numbers (7 TF × 3 S)
bool GenerateMagicNumbers() {
    string symbol = g_ea.symbol_name;

    for(int tf = 0; tf < 7; tf++) {
        for(int s = 0; s < 3; s++) {
            g_ea.magic_numbers[tf][s] = GenerateSmartMagicNumber(symbol, tf, s);
        }
    }

    // Silent - only debug log
    DebugPrint("Magic M1: S1=" + IntegerToString(g_ea.magic_numbers[0][0]) +
               ", S2=" + IntegerToString(g_ea.magic_numbers[0][1]) +
               ", S3=" + IntegerToString(g_ea.magic_numbers[0][2]));

    return true;
}

//=============================================================================
//  PART 9: LOT SIZE CALCULATION (2 functions)
//=============================================================================

// Calculate lot with progressive formula
// Formula: (base × strategy_multiplier) + tf_increment
// Result format: X.YZ where Y=strategy(1-3), Z=TF(1-7)
double CalculateSmartLotSize(double base_lot, int tf_index, int strategy_index) {
    // NEW FORMULA: (base × strategy_multiplier) + tf_increment
    // LOT FORMAT: X.YZ where X=strategy base, Y=same as X, Z=TF identifier (1-7)
    //
    // Strategy multipliers: S2=×1 (standard), S1=×2 (strong), S3=×3 (strongest)
    // TF increments: M1=+0.01, M5=+0.02, M15=+0.03, M30=+0.04, H1=+0.05, H4=+0.06, D1=+0.07
    //
    // EXAMPLES (base_lot = 0.10):
    //   M1_S2 = (0.10×1) + 0.01 = 0.11
    //   M1_S1 = (0.10×2) + 0.01 = 0.21
    //   M1_S3 = (0.10×3) + 0.01 = 0.31
    //   M5_S2 = (0.10×1) + 0.02 = 0.12
    //   D1_S3 = (0.10×3) + 0.07 = 0.37

    // Strategy multipliers: index 0=S1(×2), 1=S2(×1), 2=S3(×3)
    double strategy_multipliers[3] = {2.0, 1.0, 3.0};

    // TF increments: index 0=M1(+0.01), 1=M5(+0.02), ..., 6=D1(+0.07)
    double tf_increments[7] = {0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07};

    // Calculate final lot
    double lot = (base_lot * strategy_multipliers[strategy_index]) + tf_increments[tf_index];

    return NormalizeLotSize(lot);
}

// Pre-calculate all 21 lot sizes once
// Called once in OnInit for performance
void InitializeLotSizes() {
    for(int tf = 0; tf < 7; tf++) {
        for(int s = 0; s < 3; s++) {
            g_ea.lot_sizes[tf][s] = CalculateSmartLotSize(FixedLotSize, tf, s);
        }
    }

    // Silent - only debug log
    DebugPrint("Lot M1: S1=" + DoubleToString(g_ea.lot_sizes[0][0], 2) +
               " S2=" + DoubleToString(g_ea.lot_sizes[0][1], 2) +
               " S3=" + DoubleToString(g_ea.lot_sizes[0][2], 2));
}

//=============================================================================
//  PART 10: LAYER1 STOPLOSS INIT (1 function)
//=============================================================================

// Initialize all 21 Layer1 thresholds (7 TF × 3 S)
// OPTIMIZED: Uses pre-calculated lot sizes
void InitializeLayer1Thresholds() {
    for(int tf = 0; tf < 7; tf++) {
        double max_loss_per_lot = g_ea.csdl_rows[tf].max_loss;

        if(MathAbs(max_loss_per_lot) < 1.0) {
            max_loss_per_lot = MaxLoss_Fallback;
        }

        // Use pre-calculated lots instead of calculating again
        for(int s = 0; s < 3; s++) {
            g_ea.layer1_thresholds[tf][s] = max_loss_per_lot * g_ea.lot_sizes[tf][s];
        }
    }

    // Silent - only debug log
    DebugPrint("Layer1 M1: S1=$" + DoubleToString(g_ea.layer1_thresholds[0][0], 2) +
               " S2=$" + DoubleToString(g_ea.layer1_thresholds[0][1], 2) +
               " S3=$" + DoubleToString(g_ea.layer1_thresholds[0][2], 2));
}

//=============================================================================
//  PART 11: MAP CSDL TO EA (1 function)
//=============================================================================

// Map CSDL data to EA variables for all 7 TF
// OPTIMIZED: Single TREND variable + Smart NEWS mode selection
// NOTE: signal_new/timestamp_new removed - use csdl_rows[tf] directly
void MapCSDLToEAVariables() {
    // S2: TREND - Always use D1 (row 6) for all TF
    g_ea.trend_d1 = g_ea.csdl_rows[6].signal;

    // S3: NEWS - Use STRONGEST NEWS from all 7 TF
    // Find strongest NEWS across all 7 TF as single decision point
    // Tim tin tuc manh nhat trong 7 khung lam diem quyet dinh duy nhat
    int strongest_news = g_ea.csdl_rows[0].news;
    for(int tf = 1; tf < 7; tf++) {
        if(MathAbs(g_ea.csdl_rows[tf].news) > MathAbs(strongest_news)) {
            strongest_news = g_ea.csdl_rows[tf].news;
        }
    }
    g_ea.news_level = MathAbs(strongest_news);
    g_ea.news_direction = (strongest_news > 0) ? 1 :
                       (strongest_news < 0) ? -1 : 0;

    DebugPrint("Mapped 7 TF | signal[0]=" + IntegerToString(g_ea.csdl_rows[0].signal) +
               " trend_d1=" + IntegerToString(g_ea.trend_d1) +
               " news_lv=" + IntegerToString(g_ea.news_level) + " (STRONGEST)");
}

//=============================================================================
//  PART 12: POSITION MANAGEMENT (2 functions)
//=============================================================================
// RestoreOrCleanupPositions() - Restore/cleanup on EA startup
// CloseAllStrategiesByMagicForTF() - Close all strategies for specific TF

// Restore or cleanup positions on EA startup
// PHASE 2: Signal-based validation with consolidated AND logic
// LOGIC: Scan 7×3 combinations, if ANY condition fails ? CLOSE, if ALL pass ? KEEP
bool RestoreOrCleanupPositions() {
    // Step 1: Reset all flags first
    for(int tf = 0; tf < 7; tf++) {
        for(int s = 0; s < 3; s++) {
            g_ea.position_flags[tf][s] = 0;
        }
    }

    int kept_count = 0;
    int closed_count = 0;

    // Step 2: Scan all open positions
    for(int i = PositionsTotal() - 1; i >= 0; i--) {
        ulong ticket = PositionGetTicket(i);
        if(ticket == 0) continue;

        // Get position info
        long magic = PositionGetInteger(POSITION_MAGIC);
        long order_type = PositionGetInteger(POSITION_TYPE);
        string order_symbol = PositionGetString(POSITION_SYMBOL);

        // Filter: Only this symbol
        if(order_symbol != Symbol()) continue;

        // Get position signal from MT5
        int order_signal = 0;
        if(order_type == POSITION_TYPE_BUY) order_signal = 1;
        else if(order_type == POSITION_TYPE_SELL) order_signal = -1;
        else continue;  // Skip other types

        // Step 3: Scan 7×3 combinations to find valid match
        bool found = false;
        int found_tf = -1;
        int found_s = -1;

        for(int tf = 0; tf < 7; tf++) {
            // Skip if TF disabled
            if(!IsTFEnabled(tf)) continue;

            for(int s = 0; s < 3; s++) {
                // CONDITION 1: Magic match
                bool cond1_magic = (magic == g_ea.magic_numbers[tf][s]);

                // CONDITION 2: Signal pair match (4 variables)
                // Order signal == OLD == CSDL (triple match) AND timestamp OLD == CSDL (locked)
                // Tin hieu lenh == CU == CSDL (khop 3) VA timestamp CU == CSDL (khoa)
                bool cond2_signal_pair = (order_signal == g_ea.signal_old[tf] &&
                                          order_signal == g_ea.csdl_rows[tf].signal &&
                                          g_ea.timestamp_old[tf] == (datetime)g_ea.csdl_rows[tf].timestamp);

                // CONDITION 3: Strategy enabled
                bool cond3_strategy = false;
                if(s == 0) cond3_strategy = S1_HOME;
                else if(s == 1) cond3_strategy = S2_TREND;
                else if(s == 2) cond3_strategy = S3_NEWS;

                // CONDITION 4: Not duplicate (flag must be 0)
                bool cond4_unique = (g_ea.position_flags[tf][s] == 0);

                // CONSOLIDATED CHECK: ALL with AND
                if(cond1_magic && cond2_signal_pair && cond3_strategy && cond4_unique) {
                    found = true;
                    found_tf = tf;
                    found_s = s;
                    break;  // Exit strategy loop
                }
            }

            if(found) break;  // Exit TF loop
        }

        // Step 4: Decide KEEP or CLOSE
        if(found) {
            // ? KEEP: All conditions passed ? Restore flag
            g_ea.position_flags[found_tf][found_s] = 1;
            kept_count++;

            DebugPrint("[RESTORE_KEEP] #" + IntegerToString(ticket) +
                      " TF:" + IntegerToString(found_tf) + " S:" + IntegerToString(found_s + 1) +
                      " Signal:" + IntegerToString(order_signal) + " | Flag=1");

        } else {
            // ? CLOSE: ANY condition failed ? Close order
            CloseOrderSafely((int)ticket, "RESTORE_INVALID");
            closed_count++;

            // CRITICAL: Reset flag if this was a known magic
            // Prevents stoploss function from miscalculating
            for(int tf_check = 0; tf_check < 7; tf_check++) {
                for(int s_check = 0; s_check < 3; s_check++) {
                    if(magic == g_ea.magic_numbers[tf_check][s_check]) {
                        g_ea.position_flags[tf_check][s_check] = 0;  // Ensure flag = 0
                        break;
                    }
                }
            }

            DebugPrint("[RESTORE_CLOSE] #" + IntegerToString(ticket) +
                      " Magic:" + IntegerToString(magic) +
                      " Signal:" + IntegerToString(order_signal) + " | INVALID");
        }
    }

    // Step 5: Final summary report (1 line)
    Print(g_ea.init_summary, " | RESTORE: KEPT=", kept_count, " CLOSED=", closed_count);

    // Debug: Print restored flags (optional)
    if(DebugMode && kept_count > 0) {
        for(int tf = 0; tf < 7; tf++) {
            bool has_flag = false;
            for(int s = 0; s < 3; s++) {
                if(g_ea.position_flags[tf][s] == 1) {
                    has_flag = true;
                    break;
                }
            }
            if(has_flag) {
                Print("[RESTORE_FLAGS] ", G_TF_NAMES[tf], ": S1=", g_ea.position_flags[tf][0],
                      " S2=", g_ea.position_flags[tf][1], " S3=", g_ea.position_flags[tf][2]);
            }
        }
    }

    return true;
}

// Close all strategies for specific TF only
void CloseAllStrategiesByMagicForTF(int tf) {
    int signal_old = g_ea.signal_old[tf];
    int signal_new = g_ea.csdl_rows[tf].signal;
    datetime timestamp_new = (datetime)g_ea.csdl_rows[tf].timestamp;

    for(int i = PositionsTotal() - 1; i >= 0; i--) {
        ulong ticket = PositionGetTicket(i);
        if(ticket == 0) continue;
        if(PositionGetString(POSITION_SYMBOL) != Symbol()) continue;

        long magic = PositionGetInteger(POSITION_MAGIC);
        long position_type = PositionGetInteger(POSITION_TYPE);
        double order_lot = PositionGetDouble(POSITION_VOLUME);
        double order_profit = PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);

        // Check if magic belongs to any of 3 strategies in this TF
        int strategy_index = -1;
        for(int s = 0; s < 3; s++) {
            if(magic == g_ea.magic_numbers[tf][s]) {
                strategy_index = s;
                break;
            }
        }

        if(strategy_index >= 0) {
            string order_type_str = (position_type == POSITION_TYPE_BUY) ? "BUY" : "SELL";
            Print(">> [CLOSE] SIGNAL_CHG TF=", G_TF_NAMES[tf], " S=", IntegerToString(strategy_index+1),
                  " | #", IntegerToString(ticket), " ", order_type_str, " ", DoubleToString(order_lot, 2),
                  " | Profit=$", DoubleToString(order_profit, 2),
                  " | Old:", IntegerToString(signal_old), " New:", IntegerToString(signal_new),
                  " | Timestamp:", IntegerToString(timestamp_new), " <<");

            CloseOrderSafely((int)ticket, "SIGNAL_CHANGE");
        }
    }

    // Reset all 3 flags for this TF
    for(int s = 0; s < 3; s++) {
        g_ea.position_flags[tf][s] = 0;
    }
}

// Close ALL BONUS orders across ALL 7 TF when M1 signal changes
// TRIGGER: M1 signal change (HasValidS2BaseCondition(0))
// ACTION: Close magic[tf][2] for ALL 7 TF
void CloseAllBonusOrders() {
    // Scan all 7 TF magic numbers
    for(int tf = 0; tf < 7; tf++) {
        if(!IsTFEnabled(tf)) continue;

        int target_magic = g_ea.magic_numbers[tf][2];  // S3_BONUS magic
        int closed_count = 0;
        int total_count = 0;
        double total_profit = 0;
        double total_lot = 0;

        // Scan all positions on MT5
        for(int i = PositionsTotal() - 1; i >= 0; i--) {
            ulong ticket = PositionGetTicket(i);
            if(ticket == 0) continue;
            if(PositionGetString(POSITION_SYMBOL) != Symbol()) continue;

            // If magic matches, close it
            if(PositionGetInteger(POSITION_MAGIC) == target_magic) {
                total_count++;
                double order_profit = PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);
                double order_lot = PositionGetDouble(POSITION_VOLUME);

                if(CloseOrderSafely((int)ticket, "BONUS_M1_CLOSE")) {
                    closed_count++;
                    total_profit += order_profit;
                    total_lot += order_lot;
                }
            }
        }

        // Consolidated log
        if(total_count > 0) {
            Print(">> [CLOSE] BONUS_M1 TF=", G_TF_NAMES[tf],
                  " | ", IntegerToString(total_count), " orders Total:", DoubleToString(total_lot, 2),
                  " | Profit=$", DoubleToString(total_profit, 2),
                  " | Closed:", IntegerToString(closed_count), "/", IntegerToString(total_count), " <<");
        }

        g_ea.position_flags[tf][2] = 0;  // Reset BONUS flag
    }
}

//=============================================================================
//  PART 13: BASE CONDITION CHECK (1 function)
//=============================================================================

// Check if signal changed and new signal valid
// OPTIMIZED: Read signal/timestamp directly from csdl_rows
bool HasValidS2BaseCondition(int tf) {
    int signal_old = g_ea.signal_old[tf];
    int signal_new = g_ea.csdl_rows[tf].signal;
    datetime timestamp_old = g_ea.timestamp_old[tf];
    datetime timestamp_new = (datetime)g_ea.csdl_rows[tf].timestamp;

    return (signal_old != signal_new && signal_new != 0 && timestamp_old < timestamp_new);
}

//=============================================================================
//  PART 14: STRATEGY PROCESSING (4 functions)
//=============================================================================

// S1 Core: Open order (DRY - shared logic for BASIC and NEWS strategies)
void OpenS1Order(int tf, int signal, string mode) {
    datetime timestamp = (datetime)g_ea.csdl_rows[tf].timestamp;
    int tf_news = g_ea.csdl_rows[tf].news;

    // MT5: Price update handled automatically

    int cmd = (signal == 1) ? OP_BUY : OP_SELL;
    double price = (signal == 1) ? SymbolInfoDouble(Symbol(), SYMBOL_ASK) : SymbolInfoDouble(Symbol(), SYMBOL_BID);
    color clr = (signal == 1) ? clrBlue : clrRed;
    string type_str = (signal == 1) ? "BUY" : "SELL";

    int ticket = OrderSendSafe(tf, Symbol(), cmd, g_ea.lot_sizes[tf][0],
                               price, 3,
                               "S1_" + G_TF_NAMES[tf], g_ea.magic_numbers[tf][0], clr);

    if(ticket > 0) {
        g_ea.position_flags[tf][0] = 1;

        string log_msg = ">>> [OPEN] S1_" + mode + " TF=" + G_TF_NAMES[tf] +
                         " | #" + IntegerToString(ticket) + " " + type_str + " " +
                         DoubleToString(g_ea.lot_sizes[tf][0], 2) + " @" + DoubleToString(price, _Digits) +
                         " | Sig=" + IntegerToString(signal);

        if(mode == "NEWS") {
            string arrow = (tf_news > 0) ? "↑" : "↓";
            log_msg += " News=" + (tf_news > 0 ? "+" : "") + IntegerToString(tf_news) + arrow;
            log_msg += " Filter:" + (S1_UseNewsFilter ? "ON" : "OFF");
            log_msg += " Dir:" + (S1_RequireNewsDirection ? "REQ" : "ANY");
        }

        log_msg += " | Timestamp:" + IntegerToString(timestamp) + " <<<";
        Print(log_msg);
    } else {
        g_ea.position_flags[tf][0] = 0;
        Print("[S1_", mode, "_", G_TF_NAMES[tf], "] Failed: ", GetLastError());
    }
}

// S1 BASIC: No NEWS check
void ProcessS1BasicStrategy(int tf) {
    int current_signal = g_ea.csdl_rows[tf].signal;
    if(current_signal == 1 || current_signal == -1) {
        OpenS1Order(tf, current_signal, "BASIC");
    }
}

// S1 NEWS Filter: Check NEWS before opening order
void ProcessS1NewsFilterStrategy(int tf) {
    int current_signal = g_ea.csdl_rows[tf].signal;
    int tf_news = g_ea.csdl_rows[tf].news;
    int news_abs = MathAbs(tf_news);

    // Condition 1: Check NEWS level >= MinNewsLevelS1
    if(news_abs < MinNewsLevelS1) {
        DebugPrint("S1_NEWS: " + G_TF_NAMES[tf] + " NEWS=" + IntegerToString(news_abs) +
                   " < Min=" + IntegerToString(MinNewsLevelS1) + ", SKIP");
        return;
    }

    // Condition 2: Check NEWS direction matches signal (if required)
    if(S1_RequireNewsDirection) {
        int news_direction = (tf_news > 0) ? 1 : -1;
        if(current_signal != news_direction) {
            DebugPrint("S1_NEWS: " + G_TF_NAMES[tf] + " Signal=" + IntegerToString(current_signal) +
                       " != NewsDir=" + IntegerToString(news_direction) + ", SKIP");
            return;
        }
    }

    // PASS all conditions → Open order
    if(current_signal == 1 || current_signal == -1) {
        OpenS1Order(tf, current_signal, "NEWS");
    }
}

// S1 Strategy Router: Call appropriate function based on filter setting
void ProcessS1Strategy(int tf) {
    if(S1_UseNewsFilter) {
        ProcessS1NewsFilterStrategy(tf);
    } else {
        ProcessS1BasicStrategy(tf);
    }
}

// Process S2 (Trend Following) strategy for TF
// OPTIMIZED: Uses single g_trend_d1 + pre-calculated lot + reads signal from CSDL
// ENHANCED: Support 3 modes (auto D1 / force BUY / force SELL)
void ProcessS2Strategy(int tf) {
    int current_signal = g_ea.csdl_rows[tf].signal;
    datetime timestamp = (datetime)g_ea.csdl_rows[tf].timestamp;

    // NEW: Determine trend based on mode
    int trend_to_follow = 0;

    if(S2_TrendMode == S2_FOLLOW_D1) {
        trend_to_follow = g_ea.trend_d1;  // Follow D1 trend (auto)
    }
    else if(S2_TrendMode == S2_FORCE_BUY) {
        trend_to_follow = 1;  // Force BUY only
    }
    else if(S2_TrendMode == S2_FORCE_SELL) {
        trend_to_follow = -1;  // Force SELL only
    }

    // Check signal matches trend
    if(current_signal != trend_to_follow) {
        DebugPrint("S2_TREND: Signal=" + IntegerToString(current_signal) +
                   " != Trend=" + IntegerToString(trend_to_follow) + ", skip");
        return;
    }

    // MT5: Price update handled automatically

    

    if(current_signal == 1) {
        int ticket = OrderSendSafe(tf, Symbol(), OP_BUY, g_ea.lot_sizes[tf][1],
                                   SymbolInfoDouble(Symbol(), SYMBOL_ASK), 3,
                                   "S2_" + G_TF_NAMES[tf], g_ea.magic_numbers[tf][1], clrBlue);
        if(ticket > 0) {
            g_ea.position_flags[tf][1] = 1;
            string trend_str = trend_to_follow == 1 ? "UP" : "DOWN";
            string mode_str = (S2_TrendMode == 0) ? "AUTO" : (S2_TrendMode == 1) ? "FBUY" : "FSELL";
            Print(">>> [OPEN] S2_TREND TF=", G_TF_NAMES[tf], " | #", IntegerToString(ticket), " BUY ",
                  DoubleToString(g_ea.lot_sizes[tf][1], 2), " @", DoubleToString(SymbolInfoDouble(Symbol(), SYMBOL_ASK), _Digits),
                  " | Sig=+1 Trend:", trend_str, " Mode:", mode_str, " | Timestamp:", IntegerToString(timestamp), " <<<");
        } else {
            g_ea.position_flags[tf][1] = 0;
            Print("[S2_", G_TF_NAMES[tf], "] Failed: ", IntegerToString(GetLastError()));
        }
    }
    else if(current_signal == -1) {
        int ticket = OrderSendSafe(tf, Symbol(), OP_SELL, g_ea.lot_sizes[tf][1],
                                   SymbolInfoDouble(Symbol(), SYMBOL_BID), 3,
                                   "S2_" + G_TF_NAMES[tf], g_ea.magic_numbers[tf][1], clrRed);
        if(ticket > 0) {
            g_ea.position_flags[tf][1] = 1;
            string trend_str = trend_to_follow == -1 ? "DOWN" : "UP";
            string mode_str = (S2_TrendMode == 0) ? "AUTO" : (S2_TrendMode == 1) ? "FBUY" : "FSELL";
            Print(">>> [OPEN] S2_TREND TF=", G_TF_NAMES[tf], " | #", IntegerToString(ticket), " SELL ",
                  DoubleToString(g_ea.lot_sizes[tf][1], 2), " @", DoubleToString(SymbolInfoDouble(Symbol(), SYMBOL_BID), _Digits),
                  " | Sig=-1 Trend:", trend_str, " Mode:", mode_str, " | Timestamp:", IntegerToString(timestamp), " <<<");
        } else {
            g_ea.position_flags[tf][1] = 0;
            Print("[S2_", G_TF_NAMES[tf], "] Failed: ", IntegerToString(GetLastError()));
        }
    }
}

// Process S3 (News Alignment) strategy for TF
// OPTIMIZED: Uses per-TF NEWS + pre-calculated lot + reads signal from CSDL
void ProcessS3Strategy(int tf) {
    // Read NEWS for this TF
    int tf_news = g_ea.csdl_rows[tf].news;
    int news_abs = MathAbs(tf_news);
    datetime timestamp = (datetime)g_ea.csdl_rows[tf].timestamp;

    // Check NEWS level >= MinNewsLevelS3
    if(news_abs < MinNewsLevelS3) {
        DebugPrint("S3_NEWS: TF" + IntegerToString(tf) + " NEWS=" + IntegerToString(news_abs) + " < " + IntegerToString(MinNewsLevelS3) + ", skip");
        return;
    }

    // Check NEWS direction matches signal
    int news_direction = (tf_news > 0) ? 1 : -1;
    int current_signal = g_ea.csdl_rows[tf].signal;

    if(current_signal != news_direction) {
        DebugPrint("S3_NEWS: Signal=" + IntegerToString(current_signal) + " != NewsDir=" + IntegerToString(news_direction) + ", skip");
        return;
    }

    // MT5: Price update handled automatically

    

    if(current_signal == 1) {
        int ticket = OrderSendSafe(tf, Symbol(), OP_BUY, g_ea.lot_sizes[tf][2],
                                   SymbolInfoDouble(Symbol(), SYMBOL_ASK), 3,
                                   "S3_" + G_TF_NAMES[tf], g_ea.magic_numbers[tf][2], clrBlue);
        if(ticket > 0) {
            g_ea.position_flags[tf][2] = 1;
            string arrow = (tf_news > 0) ? "↑" : "↓";
            Print(">>> [OPEN] S3_NEWS TF=", G_TF_NAMES[tf], " | #", IntegerToString(ticket), " BUY ",
                  DoubleToString(g_ea.lot_sizes[tf][2], 2), " @", DoubleToString(SymbolInfoDouble(Symbol(), SYMBOL_ASK), _Digits),
                  " | Sig=+1 News=", tf_news > 0 ? "+" : "", IntegerToString(tf_news), arrow, " | Timestamp:", IntegerToString(timestamp), " <<<");
        } else {
            g_ea.position_flags[tf][2] = 0;
            Print("[S3_", G_TF_NAMES[tf], "] Failed: ", IntegerToString(GetLastError()));
        }
    }
    else if(current_signal == -1) {
        int ticket = OrderSendSafe(tf, Symbol(), OP_SELL, g_ea.lot_sizes[tf][2],
                                   SymbolInfoDouble(Symbol(), SYMBOL_BID), 3,
                                   "S3_" + G_TF_NAMES[tf], g_ea.magic_numbers[tf][2], clrRed);
        if(ticket > 0) {
            g_ea.position_flags[tf][2] = 1;
            string arrow = (tf_news > 0) ? "↑" : "↓";
            Print(">>> [OPEN] S3_NEWS TF=", G_TF_NAMES[tf], " | #", IntegerToString(ticket), " SELL ",
                  DoubleToString(g_ea.lot_sizes[tf][2], 2), " @", DoubleToString(SymbolInfoDouble(Symbol(), SYMBOL_BID), _Digits),
                  " | Sig=-1 News=", tf_news > 0 ? "+" : "", IntegerToString(tf_news), arrow, " | Timestamp:", IntegerToString(timestamp), " <<<");
        } else {
            g_ea.position_flags[tf][2] = 0;
            Print("[S3_", G_TF_NAMES[tf], "] Failed: ", IntegerToString(GetLastError()));
        }
    }
}

// Process Bonus NEWS - Scan all 7 TF and open multiple orders if NEWS detected
// Xu ly tin tuc Bonus - Quet 7 TF va mo nhieu lenh neu phat hien tin tuc
void ProcessBonusNews() {
    if(!EnableBonusNews) return;

    

    // Scan all 7 TF
    for(int tf = 0; tf < 7; tf++) {
        // BUGFIX: Skip if TF disabled
        if(!IsTFEnabled(tf)) continue;

        int tf_news = g_ea.csdl_rows[tf].news;
        int news_abs = MathAbs(tf_news);

        // Skip if NEWS below threshold
        if(news_abs < MinNewsLevelBonus) continue;

        // Determine direction
        int news_direction = (tf_news > 0) ? 1 : -1;

        // Calculate BONUS lot (S3 lot × multiplier)
        double bonus_lot = g_ea.lot_sizes[tf][2] * BonusLotMultiplier;

        // MT5: Price update handled automatically

        // Open BonusOrderCount orders
        int opened_count = 0;
        string ticket_list = "";
        double entry_price = 0;

        for(int count = 0; count < BonusOrderCount; count++) {
            if(news_direction == 1) {
                int ticket = OrderSendSafe(tf, Symbol(), OP_BUY, bonus_lot,
                                           SymbolInfoDouble(Symbol(), SYMBOL_ASK), 3,
                                           "BONUS_" + G_TF_NAMES[tf], g_ea.magic_numbers[tf][2], clrGold);
                if(ticket > 0) {
                    opened_count++;
                    if(ticket_list != "") ticket_list = ticket_list + ",";
                    ticket_list = ticket_list + IntegerToString(ticket);
                    if(entry_price == 0) entry_price = SymbolInfoDouble(Symbol(), SYMBOL_ASK);
                }
            } else {
                int ticket = OrderSendSafe(tf, Symbol(), OP_SELL, bonus_lot,
                                           SymbolInfoDouble(Symbol(), SYMBOL_BID), 3,
                                           "BONUS_" + G_TF_NAMES[tf], g_ea.magic_numbers[tf][2], clrOrange);
                if(ticket > 0) {
                    opened_count++;
                    if(ticket_list != "") ticket_list = ticket_list + ",";
                    ticket_list = ticket_list + IntegerToString(ticket);
                    if(entry_price == 0) entry_price = SymbolInfoDouble(Symbol(), SYMBOL_BID);
                }
            }
        }

        // Consolidated log after loop
        if(opened_count > 0) {
            string arrow = (tf_news > 0) ? "↑" : "↓";
            double total_lot = opened_count * bonus_lot;
            Print(">>> [OPEN] BONUS TF=", G_TF_NAMES[tf], " | ", IntegerToString(opened_count), "×",
                  news_direction == 1 ? "BUY" : "SELL", " @", DoubleToString(bonus_lot, 2),
                  " Total:", DoubleToString(total_lot, 2), " @", DoubleToString(entry_price, _Digits),
                  " | News=", tf_news > 0 ? "+" : "", IntegerToString(tf_news), arrow,
                  " | Multiplier:", DoubleToString(BonusLotMultiplier, 1), "x",
                  " Tickets:", ticket_list, " <<<");
        }
    }
}

//=============================================================================
//  PART 15: STOPLOSS CHECKS (2 functions)
//=============================================================================

// Check stoploss & take profit for all 21 orders
// Stoploss: 2 layers (LAYER1, LAYER2)
// Take profit: 1 layer (based on max_loss × multiplier)
void CheckStoplossAndTakeProfit() {
    if(PositionsTotal() == 0) return;

    // Scan all positions once
    for(int i = PositionsTotal() - 1; i >= 0; i--) {
        ulong ticket = PositionGetTicket(i);
        if(ticket == 0) continue;
        if(PositionGetString(POSITION_SYMBOL) != Symbol()) continue;

        long magic = PositionGetInteger(POSITION_MAGIC);
        double profit = PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);
        double position_volume = PositionGetDouble(POSITION_VOLUME);
        long position_type = PositionGetInteger(POSITION_TYPE);

        // Find TF + Strategy from magic
        bool found = false;
        for(int tf = 0; tf < 7; tf++) {
            for(int s = 0; s < 3; s++) {
                if(magic == g_ea.magic_numbers[tf][s] &&
                   g_ea.position_flags[tf][s] == 1) {



                    bool order_closed = false;

                    // ===== SECTION 1: STOPLOSS (2 layers) =====
                    if(StoplossMode != NONE) {
                        double sl_threshold = 0.0;
                        string mode_name = "";

                        if(StoplossMode == LAYER1_MAXLOSS) {
                            // Layer1: Use pre-calculated threshold (max_loss × lot)
                            sl_threshold = g_ea.layer1_thresholds[tf][s];
                            mode_name = "LAYER1_SL";
                        }
                        else if(StoplossMode == LAYER2_MARGIN) {
                            // Layer2: Calculate from margin (emergency)
                            double margin_usd = position_volume * SymbolInfoDouble(Symbol(), SYMBOL_MARGIN_INITIAL);
                            sl_threshold = -(margin_usd / Layer2_Divisor);
                            mode_name = "LAYER2_SL";
                        }

                        // Check and close if loss exceeds threshold
                        if(profit <= sl_threshold) {
                            string short_mode = (mode_name == "LAYER1_SL") ? "L1_SL" : "L2_SL";
                            string order_type_str = (position_type == POSITION_TYPE_BUY) ? "BUY" : "SELL";
                            string margin_info = "";
                            if(mode_name == "LAYER2_SL") {
                                double margin_usd = position_volume * SymbolInfoDouble(Symbol(), SYMBOL_MARGIN_INITIAL);
                                margin_info = " Margin=$" + DoubleToString(margin_usd, 2);
                            }
                            Print(">> [CLOSE] ", short_mode, " TF=", G_TF_NAMES[tf], " S=", IntegerToString(s+1),
                                  " | #", IntegerToString(ticket), " ", order_type_str, " ", DoubleToString(position_volume, 2),
                                  " | Loss=$", DoubleToString(profit, 2),
                                  " | Threshold=$", DoubleToString(sl_threshold, 2), margin_info, " <<");

                            if(CloseOrderSafely((int)ticket, mode_name)) {
                                g_ea.position_flags[tf][s] = 0;
                                order_closed = true;
                            }
                        }
                    }

                    // ===== SECTION 2: TAKE PROFIT (1 layer) =====
                    // Only check if order wasn't closed by stoploss
                    if(!order_closed && UseTakeProfit) {
                        // Calculate TP threshold from max_loss
                        double max_loss_per_lot = MathAbs(g_ea.csdl_rows[tf].max_loss);
                        if(max_loss_per_lot < 1.0) {
                            max_loss_per_lot = MathAbs(MaxLoss_Fallback);  // 1000
                        }

                        double tp_threshold = (max_loss_per_lot * g_ea.lot_sizes[tf][s]) * TakeProfit_Multiplier;

                        // Check and close if profit exceeds threshold
                        if(profit >= tp_threshold) {
                            string order_type_str = (position_type == POSITION_TYPE_BUY) ? "BUY" : "SELL";
                            Print(">> [CLOSE] TP TF=", G_TF_NAMES[tf], " S=", IntegerToString(s+1),
                                  " | #", IntegerToString(ticket), " ", order_type_str, " ", DoubleToString(position_volume, 2),
                                  " | Profit=$", DoubleToString(profit, 2),
                                  " | Threshold=$", DoubleToString(tp_threshold, 2),
                                  " Mult=", DoubleToString(TakeProfit_Multiplier, 2), " <<");

                            if(CloseOrderSafely((int)ticket, "TAKE_PROFIT")) {
                                g_ea.position_flags[tf][s] = 0;
                            }
                        }
                    }

                    found = true;
                    break;
                }
            }
            if(found) break;
        }
    }
}

//=============================================================================
//  PART 16: EMERGENCY (1 function)
//=============================================================================

// Check emergency conditions (drawdown) - log only
void CheckAllEmergencyConditions() {
    double equity = AccountInfoDouble(ACCOUNT_EQUITY);
    double balance = AccountInfoDouble(ACCOUNT_BALANCE);

    if(balance > 0) {
        double drawdown_percent = ((balance - equity) / balance) * 100;

        if(drawdown_percent > 25.0) {
            Print("[WARNING] Drawdown: ", DoubleToString(drawdown_percent, 2), "%");
        }
    }
}

//=============================================================================
//  PART 17: HEALTH CHECK & RESET (4 functions)
//=============================================================================

// Smart TF reset for all charts of current symbol (learned from SPY Bot)
// Resets OTHER charts first, then CURRENT chart last (important for D1 SPY Bot recognition)
void SmartTFReset() {
    Print("=======================================================");
    Print("[SMART_TF_RESET] Resetting all charts of ", g_ea.symbol_name, "...");
    Print("=======================================================");

    string current_symbol = Symbol();
    int current_period = Period();
    long current_chart_id = ChartID();

    // Step 1: Find all OTHER charts of SAME symbol (not including current chart)
    int total_charts = 0;
    long chart_ids[10];
    ArrayInitialize(chart_ids, 0);

    long temp_chart = ChartFirst();
    while(temp_chart >= 0) {
        // ONLY reset charts with SAME symbol (important for multi-symbol setup!)
        if(ChartSymbol(temp_chart) == current_symbol && temp_chart != current_chart_id) {
            chart_ids[total_charts] = temp_chart;
            total_charts++;
        }
        temp_chart = ChartNext(temp_chart);
    }

    // Step 2: Reset OTHER charts FIRST (6 charts: M1/M5/M15/M30/H1/H4 or M5/M15/M30/H1/H4/D1)
    for(int i = 0; i < total_charts; i++) {
        ENUM_TIMEFRAMES other_period = (ENUM_TIMEFRAMES)ChartPeriod(chart_ids[i]);
        Print("[RESET] Step ", (i+1), "/", total_charts, ": Chart TF ", other_period, " (via W1)...");

        ChartSetSymbolPeriod(chart_ids[i], current_symbol, PERIOD_W1);
        Sleep(1000);
        ChartSetSymbolPeriod(chart_ids[i], current_symbol, other_period);
        Sleep(1000);
    }

    // Step 3: Reset CURRENT chart LAST (important: D1 chart with SPY Bot must be last!)
    Print("[RESET] Step ", (total_charts+1), "/", (total_charts+1), ": Current chart TF ", current_period, " (LAST - via W1)...");
    ChartSetSymbolPeriod(current_chart_id, current_symbol, PERIOD_W1);
    Sleep(1000);
    ChartSetSymbolPeriod(current_chart_id, current_symbol, (ENUM_TIMEFRAMES)current_period);
    Sleep(1000);

    Print("[SMART_TF_RESET] ? Completed! ", (total_charts + 1), " charts reset");
    Print("=======================================================");
}

// Weekend reset (Saturday 00:03) - Trigger SmartTFReset
// ONLY M1 chart has permission to reset (master chart)
// Time: 00:03 to AVOID conflict with SPY Bot reset at 00:00
void CheckWeekendReset() {
    // Check if feature is enabled by user
    if(!EnableWeekendReset) return;

    // ONLY M1 chart can trigger reset (to avoid conflict)
    if(Period() != PERIOD_M1) return;

    datetime current_time = TimeCurrent();
    MqlDateTime dt;
    TimeToStruct(current_time, dt);
    int day_of_week = dt.day_of_week;
    int hour = dt.hour;
    int minute = dt.min;

    // Only on Saturday (6) at 0h:01 (minute 01 exactly)
    // IMPORTANT: NOT 0h:00 to avoid conflict with SPY Bot!
    if(day_of_week != 6 || hour != 0 || minute != 3) return;

    // Prevent duplicate reset (once per day)
    int current_day = dt.day;
    if(current_day == g_ea.weekend_last_day) return;  // Already reset today

    Print("[WEEKEND_RESET] Saturday 00:03 - M1 chart triggering weekly reset...");
    Print("[WEEKEND_RESET] (Delayed 3 minute to avoid SPY Bot conflict at 00:00)");

    SmartTFReset();  // Call smart reset for all charts

    g_ea.weekend_last_day = current_day;
    Print("[WEEKEND_RESET] ? Weekly reset completed!");
}

// Health check SPY Bot (8h/16h only, NOT 24h)
// ONLY M1 chart has permission to check and reset (master chart)
void CheckSPYBotHealth() {
    // Check if feature is enabled by user
    if(!EnableHealthCheck) return;

    // ONLY M1 chart can check health (to avoid conflict)
    if(Period() != PERIOD_M1) return;

    datetime current_time = TimeCurrent();
    MqlDateTime dt;
    TimeToStruct(current_time, dt);
    int hour = dt.hour;

    // Only check at 8h & 16h (NOT 24h - conflicts with weekend reset)
    if(hour != 8 && hour != 16) return;

    // Prevent duplicate check (once per hour)
    if(hour == g_ea.health_last_check_hour) return;
    g_ea.health_last_check_hour = hour;

    // Get M1 timestamp from CSDL (already available)
    datetime m1_timestamp = g_ea.timestamp_old[0];

    // Calculate time difference
    int diff_seconds = (int)(current_time - m1_timestamp);
    int diff_hours = diff_seconds / 3600;
    int diff_minutes = (diff_seconds % 3600) / 60;

    Print("[HEALTH_CHECK] Time: ", hour, "h00 | CSDL last update: ", diff_hours, "h", diff_minutes, "m ago");

    // If diff > 8 hours (28800 seconds) ? SPY Bot frozen!
    if(diff_seconds > 28800) {
        Print("[HEALTH_CHECK] ? SPY Bot FROZEN!");
        Print("[HEALTH_CHECK] Server time: ", TimeToString(current_time, TIME_DATE|TIME_SECONDS));
        Print("[HEALTH_CHECK] Last CSDL update: ", TimeToString(m1_timestamp, TIME_DATE|TIME_SECONDS));
        Print("[HEALTH_CHECK] M1 chart triggering Smart TF Reset...");

        Alert("?? SPY Bot frozen! Auto-reset all ", g_ea.symbol_name, " charts!");

        SmartTFReset();  // Call smart reset for all charts

        Print("[HEALTH_CHECK] ? Reset completed");

    } else {
        Print("[HEALTH_CHECK] ? SPY Bot OK - Recent activity detected");
    }
}

//=============================================================================
//  PART 18: MAIN EA FUNCTIONS (3 functions)
//=============================================================================

// EA initialization - setup all components
// OPTIMIZED V3.4: Struct-based data isolation for multi-symbol support
int OnInit() {
    // PART 1: Symbol recognition
    if(!InitializeSymbolRecognition()) return(INIT_FAILED);
    InitializeSymbolPrefix();

    // PART 2: Folder selection (only for local file mode)
    if(CSDL_Source == FOLDER_1) g_ea.csdl_folder = "DataAutoOner\\";
    else if(CSDL_Source == FOLDER_2) g_ea.csdl_folder = "DataAutoOner2\\";
    else if(CSDL_Source == FOLDER_3) g_ea.csdl_folder = "DataAutoOner3\\";
    else g_ea.csdl_folder = "DataAutoOner2\\";  // Fallback to FOLDER_2

    // PART 3: Build filename & Read file
    BuildCSDLFilename();
    ReadCSDLFile();

    // PART 4: Generate magic numbers
    if(!GenerateMagicNumbers()) return(INIT_FAILED);

    // PART 5: Pre-calculate all 21 lot sizes ONCE
    InitializeLotSizes();

    // PART 6: Initialize Layer1 thresholds (uses pre-calculated lots)
    InitializeLayer1Thresholds();

    // PART 7: Map CSDL variables (includes TREND/NEWS optimization)
    MapCSDLToEAVariables();

    // PART 7B: ?? CRITICAL FIX - Reset ALL auxiliary flags to prevent ZOMBIE variables
    // MQL4 does NOT auto-reset global variables on EA restart
    // If EA was killed (crash/user stop), old flag values may persist
    // This causes ZOMBIE orders: flag=1 but order doesn't exist, or TF disabled but flag still set
    for(int tf = 0; tf < 7; tf++) {
        for(int s = 0; s < 3; s++) {
            g_ea.position_flags[tf][s] = 0;
        }
    }

    // Initialize global state vars (prevent multi-symbol conflicts)
    g_ea.first_run_completed = false;
    g_ea.weekend_last_day = -1;
    g_ea.health_last_check_hour = -1;
    g_ea.timer_last_run_time = 0;

    DebugPrint("[RESET] All position flags (21) & state vars reset to 0");

    // PART 8: Set BASELINE (only old) - FOR ALL 7 TF
    for(int tf = 0; tf < 7; tf++) {
        g_ea.signal_old[tf] = g_ea.csdl_rows[tf].signal;
        g_ea.timestamp_old[tf] = (datetime)g_ea.csdl_rows[tf].timestamp;
    }

    // PART 8B: Build compact startup summary BEFORE RESTORE
    // This must be done BEFORE RestoreOrCleanupPositions() so it can print final summary
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

    string sl_mode = (StoplossMode == LAYER1_MAXLOSS) ? "L1" : ("L2/" + DoubleToString(Layer2_Divisor, 0));
    string master_mode = (Period()==PERIOD_M1) ? "M1" : "M5-D1";

    // CSDL source name
    string folder_name = "";
    if(CSDL_Source == FOLDER_1) folder_name = "DA1";
    else if(CSDL_Source == FOLDER_2) folder_name = "DA2";
    else if(CSDL_Source == FOLDER_3) folder_name = "DA3";

    // Build init_summary with CSDL data (after MapCSDLToEAVariables)
    string trend_str = SignalToString(g_ea.trend_d1);
    string news_str = "Lv" + IntegerToString(g_ea.news_level) + "_" + SignalToString(g_ea.news_direction);

    g_ea.init_summary = "[INIT] " + g_ea.symbol_name + " | SL:" + sl_mode +
                        " News:STRONGEST(" + news_str + ") Trend:" + trend_str +
                        " | Lot:" + DoubleToString(g_ea.lot_sizes[0][0], 2) + "-" + DoubleToString(g_ea.lot_sizes[6][2], 2) +
                        " | TF:" + IntegerToString(tf_count) + " S:" + IntegerToString(strat_count) +
                        " | Folder:" + folder_name + " Master:" + master_mode +
                        " Magic:" + IntegerToString(g_ea.magic_numbers[0][0]) + "-" + IntegerToString(g_ea.magic_numbers[6][2]);

    // PART 9: Restore positions (will print init_summary)
    RestoreOrCleanupPositions();

    // PART 10: Start timer
    if(!EventSetTimer(1)) return(INIT_FAILED);

    g_ea.first_run_completed = true;

    return(INIT_SUCCEEDED);
}

// EA deinitialization - cleanup
void OnDeinit(const int reason) {
    EventKillTimer();
    Comment("");  // Clear Comment

    // Delete all dashboard labels (16 labels: dash_0 to dash_15)
    for(int i = 0; i <= 15; i++) {
        ObjectDelete(0, "dash_" + IntegerToString(i));
    }

    Print("[EA] Shutdown. Reason: ", reason);
}

//=============================================================================
//  PART 19: DASHBOARD - OBJ_LABEL (4 functions)
//=============================================================================
// Leverages existing EA resources: g_ea struct, flags, lot sizes
// Uses OBJ_LABEL with fixed-width spaces + alternating colors (Blue/White)

// Scan all orders once for dashboard (reuse stoploss logic)
// NEW: Builds 2 separate summaries - S1 only (row 1), S2+S3 (row 2)
void ScanAllOrdersForDashboard(int &total_orders, double &total_profit, double &total_loss,
                                string &s1_summary, string &s2s3_summary) {
    total_orders = 0;
    total_profit = 0;
    total_loss = 0;
    s1_summary = "";
    s2s3_summary = "";


    int s1_count = 0;
    int s2s3_count = 0;

    for(int i = 0; i < PositionsTotal(); i++) {
        ulong ticket = PositionGetTicket(i);
        if(ticket == 0) continue;
        if(PositionGetString(POSITION_SYMBOL) != Symbol()) continue;

        long magic = PositionGetInteger(POSITION_MAGIC);
        double profit = PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);
        double position_volume = PositionGetDouble(POSITION_VOLUME);
        double margin_usd = position_volume * SymbolInfoDouble(Symbol(), SYMBOL_MARGIN_INITIAL);

        // Check which strategy this order belongs to
        for(int tf = 0; tf < 7; tf++) {
            // S1 orders (row 1)
            if(magic == g_ea.magic_numbers[tf][0]) {
                total_orders++;
                if(profit > 0) total_profit += profit;
                else total_loss += profit;

                s1_count++;
                if(s1_count <= 7) {  // Max 7 (all TF)
                    if(s1_count > 1) s1_summary += ", ";
                    s1_summary += "S1_" + G_TF_NAMES[tf] + "[$" + DoubleToString(margin_usd, 0) + "]";
                }
                break;
            }
            // S2 + S3 orders (row 2)
            else if(magic == g_ea.magic_numbers[tf][1] || magic == g_ea.magic_numbers[tf][2]) {
                total_orders++;
                if(profit > 0) total_profit += profit;
                else total_loss += profit;

                s2s3_count++;
                if(s2s3_count <= 7) {  // Show first 7
                    string strategy = (magic == g_ea.magic_numbers[tf][1]) ? "S2" : "S3";
                    if(s2s3_count > 1) s2s3_summary += ", ";
                    s2s3_summary += strategy + "_" + G_TF_NAMES[tf] + "[$" + DoubleToString(margin_usd, 0) + "]";
                }
                break;
            }
        }
    }

    // Add "more" indicators
    if(s1_count > 7) s1_summary += " +" + IntegerToString(s1_count - 7) + " more";
    if(s2s3_count > 7) s2s3_summary += " +" + IntegerToString(s2s3_count - 7) + " more";
}

// Format age (time since signal)
string FormatAge(datetime timestamp) {
    int diff = (int)(TimeCurrent() - timestamp);
    if(diff < 60) return IntegerToString(diff) + "s";
    if(diff < 3600) return IntegerToString(diff / 60) + "m";
    if(diff < 86400) {
        int h = diff / 3600;
        int m = (diff % 3600) / 60;
        return IntegerToString(h) + "h" + IntegerToString(m) + "m";
    }
    return IntegerToString(diff / 86400) + "d";
}

// Pad string to fixed width (right-pad with spaces)
string PadRight(string text, int width) {
    while(StringLen(text) < width) text += " ";
    if(StringLen(text) > width) text = StringSubstr(text, 0, width);
    return text;
}

// Calculate total P&L for specific TF (all strategies)
double CalculateTFPnL(int tf) {
    double total_pnl = 0;

    // Loop through all 3 strategies for this TF
    for(int s = 0; s < 3; s++) {
        // Skip if no position open
        if(g_ea.position_flags[tf][s] != 1) continue;

        int target_magic = g_ea.magic_numbers[tf][s];

        // Scan all positions to find matching magic
        for(int i = 0; i < PositionsTotal(); i++) {
            ulong ticket = PositionGetTicket(i);
            if(ticket == 0) continue;
            if(PositionGetString(POSITION_SYMBOL) != Symbol()) continue;
            if(PositionGetInteger(POSITION_MAGIC) == target_magic) {
                total_pnl += PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);
            }
        }
    }

    return total_pnl;
}

// Check if TF has BONUS orders
bool HasBonusOrders(int tf) {
    int target_magic = g_ea.magic_numbers[tf][2]; // S3 magic for this TF

    for(int i = 0; i < PositionsTotal(); i++) {
        ulong ticket = PositionGetTicket(i);
        if(ticket == 0) continue;
        if(PositionGetString(POSITION_SYMBOL) != Symbol()) continue;
        if(PositionGetInteger(POSITION_MAGIC) == target_magic) {
            // Check if comment contains "BONUS"
            string comment = PositionGetString(POSITION_COMMENT);
            if(StringFind(comment, "BONUS") >= 0) {
                return true;
            }
        }
    }

    return false;
}

// Format BONUS status line for dashboard
string FormatBonusStatus() {
    // Check if BONUS is enabled
    if(!EnableBonusNews) return "BONUS: Disabled";

    string bonus_list = "";
    string status = "IDLE";
    int bonus_tf_count = 0;

    // First check: Are there any BONUS orders currently open?
    for(int tf = 0; tf < 7; tf++) {
        if(!IsTFEnabled(tf)) continue;

        if(HasBonusOrders(tf)) {
            status = "OPEN";
            bonus_tf_count++;

            int news = g_ea.csdl_rows[tf].news;
            string arrow = (news > 0) ? "^" : "v";

            if(bonus_list != "") bonus_list += " ";
            bonus_list += G_TF_NAMES[tf] + "(" + IntegerToString(BonusOrderCount) + "x " +
                         (news > 0 ? "+" : "") + IntegerToString(news) + arrow + ")";
        }
    }

    // Second check: If no orders open, which TFs qualify for BONUS?
    if(status == "IDLE") {
        for(int tf = 0; tf < 7; tf++) {
            if(!IsTFEnabled(tf)) continue;

            int news_abs = MathAbs(g_ea.csdl_rows[tf].news);
            if(news_abs >= MinNewsLevelBonus) {
                status = "WAIT";
                bonus_tf_count++;

                int news = g_ea.csdl_rows[tf].news;
                string arrow = (news > 0) ? "^" : "v";

                if(bonus_list != "") bonus_list += " ";
                bonus_list += G_TF_NAMES[tf] + "(" + IntegerToString(BonusOrderCount) + "x " +
                             (news > 0 ? "+" : "") + IntegerToString(news) + arrow + ")";
            }
        }
    }

    // If no qualifying TFs, show "None"
    if(bonus_list == "") bonus_list = "None";

    // Format timestamp (last BONUS open time)
    string last_time = TimeToString(TimeCurrent(), TIME_SECONDS);

    // Build final status line
    string result = "BONUS: " + bonus_list + " | " + status + " | Last:" + last_time;

    return result;
}

// Main dashboard update with OBJ_LABEL (12 lines, optimized)
void UpdateDashboard() {
    // Check if dashboard is enabled
    if(!ShowDashboard) {
        // Hide all labels if disabled
        for(int i = 0; i <= 15; i++) {
            ObjectDelete(0, "dash_" + IntegerToString(i));
        }
        return;
    }


    int y_start = 150;  // Start 150px from top
    int line_height = 14;  // Line spacing
    int y_pos = y_start;

    // ===== LEVERAGE: Account info
    double equity = AccountInfoDouble(ACCOUNT_EQUITY);
    double balance = AccountInfoDouble(ACCOUNT_BALANCE);
    double dd = (balance > 0) ? ((balance - equity) / balance) * 100 : 0;

    // ===== LEVERAGE: Scan orders ONCE and count by strategy
    int total_orders = 0;
    double total_profit = 0, total_loss = 0;
    string s1_summary = "", s2s3_summary = "";
    ScanAllOrdersForDashboard(total_orders, total_profit, total_loss, s1_summary, s2s3_summary);

    // Count positions by strategy type for compact summary
    int s1_count = 0, s2_count = 0, s3_count = 0;
    double s1_pnl = 0, s2_pnl = 0, s3_pnl = 0;
    for(int i = 0; i < PositionsTotal(); i++) {
        ulong ticket = PositionGetTicket(i);
        if(ticket == 0) continue;
        if(PositionGetString(POSITION_SYMBOL) != Symbol()) continue;

        double order_pnl = PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);
        long magic = PositionGetInteger(POSITION_MAGIC);

        // Check which strategy this position belongs to
        bool found = false;
        for(int tf = 0; tf < 7; tf++) {
            if(magic == g_ea.magic_numbers[tf][0]) { s1_count++; s1_pnl += order_pnl; found = true; break; }
            if(magic == g_ea.magic_numbers[tf][1]) { s2_count++; s2_pnl += order_pnl; found = true; break; }
            if(magic == g_ea.magic_numbers[tf][2]) { s3_count++; s3_pnl += order_pnl; found = true; break; }
        }
    }

    // ===== LEVERAGE: g_ea variables
    string folder = "";
    if(CSDL_Source == FOLDER_1) folder = "DA1";
    else if(CSDL_Source == FOLDER_2) folder = "DA2";
    else if(CSDL_Source == FOLDER_3) folder = "DA3";
    string trend = (g_ea.trend_d1 == 1) ? "^" : (g_ea.trend_d1 == -1 ? "v" : "-");
    string news_dir = (g_ea.news_direction == 1) ? "^" : (g_ea.news_direction == -1 ? "v" : "-");

    // ===== LINE 0: HEADER (YELLOW)
    string header = "[" + g_ea.symbol_name + "] " + folder + " | 7TFx3S | D1:" + trend +
                    " | $" + DoubleToString(equity, 0) + " DD:" + DoubleToString(dd, 1) + "% | " +
                    IntegerToString(total_orders) + "/21";
    CreateOrUpdateLabel("dash_0", header, 10, y_pos, clrYellow, 9);
    y_pos += line_height;

    // ===== LINE 1: SEPARATOR (White)
    CreateOrUpdateLabel("dash_1", "---------------------------------------------", 10, y_pos, clrWhite, 9);
    y_pos += line_height;

    // ===== LINE 2: COLUMN HEADERS (White)
    string col_header = PadRight("TF", 5) + PadRight("Sig", 5) + PadRight("S1", 7) +
                        PadRight("S2", 7) + PadRight("S3", 7) + PadRight("P&L", 9) + "News";
    CreateOrUpdateLabel("dash_2", col_header, 10, y_pos, clrWhite, 9);
    y_pos += line_height;

    // ===== LINE 3: SEPARATOR (White)
    CreateOrUpdateLabel("dash_3", "---------------------------------------------", 10, y_pos, clrWhite, 9);
    y_pos += line_height;

    // ===== LINES 4-10: 7 TF ROWS - ALTERNATING COLORS + P&L
    for(int tf = 0; tf < 7; tf++) {
        // Signal with ASCII arrows (^ up, v down, - none)
        int current_signal = g_ea.csdl_rows[tf].signal;
        string sig = "";
        if(current_signal == 1) sig = "^";         // UP arrow
        else if(current_signal == -1) sig = "v";   // DOWN arrow
        else sig = "-";                             // NONE

        // S1/S2/S3 positions
        string s1 = (g_ea.position_flags[tf][0] == 1) ? "*" + DoubleToString(g_ea.lot_sizes[tf][0], 2) : "o";
        string s2 = (g_ea.position_flags[tf][1] == 1) ? "*" + DoubleToString(g_ea.lot_sizes[tf][1], 2) : "o";
        string s3 = (g_ea.position_flags[tf][2] == 1) ? "*" + DoubleToString(g_ea.lot_sizes[tf][2], 2) : "o";

        // P&L for this TF (all strategies)
        double tf_pnl = CalculateTFPnL(tf);
        string pnl_str = "";
        if(tf_pnl > 0) pnl_str = "+" + DoubleToString(tf_pnl, 2);
        else if(tf_pnl < 0) pnl_str = DoubleToString(tf_pnl, 2);
        else pnl_str = "+0.00";

        // News with sign
        string nw = IntegerToString(g_ea.csdl_rows[tf].news);
        if(g_ea.csdl_rows[tf].news > 0) nw = "+" + nw;

        // Build row with fixed-width columns
        string row = PadRight(G_TF_NAMES[tf], 5) + PadRight(sig, 5) + PadRight(s1, 7) +
                     PadRight(s2, 7) + PadRight(s3, 7) + PadRight(pnl_str, 9) + nw;

        // Alternating colors: Blue (even rows), White (odd rows)
        color row_color = (tf % 2 == 0) ? clrDodgerBlue : clrWhite;
        CreateOrUpdateLabel("dash_" + IntegerToString(4 + tf), row, 10, y_pos, row_color, 9);
        y_pos += line_height;
    }

    // ===== LINE 11: SEPARATOR (White)
    CreateOrUpdateLabel("dash_11", "---------------------------------------------", 10, y_pos, clrWhite, 9);
    y_pos += line_height;

    // ===== LINE 12: BONUS STATUS (White)
    string bonus_status = FormatBonusStatus();
    CreateOrUpdateLabel("dash_12", bonus_status, 10, y_pos, clrWhite, 9);
    y_pos += line_height;

    // ===== LINE 13: NET SUMMARY (Yellow)
    double net = total_profit + total_loss;
    string net_summary = "NET:$" + DoubleToString(net, 2);

    // Add strategy breakdown if there are orders
    if(s1_count > 0) net_summary += " | S1:" + IntegerToString(s1_count) + "x$" + DoubleToString(s1_pnl, 0);
    if(s2_count > 0) net_summary += " | S2:" + IntegerToString(s2_count) + "x$" + DoubleToString(s2_pnl, 0);
    if(s3_count > 0) net_summary += " | S3:" + IntegerToString(s3_count) + "x$" + DoubleToString(s3_pnl, 1);

    net_summary += " | " + IntegerToString(total_orders) + "/21";

    CreateOrUpdateLabel("dash_13", net_summary, 10, y_pos, clrYellow, 9);
    y_pos += line_height;

    // ===== LINE 14: BROKER INFO (Yellow)
    string broker = AccountInfoString(ACCOUNT_COMPANY);
    int leverage = (int)AccountInfoInteger(ACCOUNT_LEVERAGE);
    string broker_info = broker + " | Lev:1:" + IntegerToString(leverage) + " | 2s";
    CreateOrUpdateLabel("dash_14", broker_info, 10, y_pos, clrYellow, 8);

    // Clean up old unused label (line 15 from old layout)
    ObjectDelete(0, "dash_15");
}

// Create or update OBJ_LABEL
void CreateOrUpdateLabel(string name, string text, int x, int y, color clr, int font_size) {
    if(ObjectFind(0, name) < 0) {
        ObjectCreate(0, name, OBJ_LABEL, 0, 0, 0);
        ObjectSetInteger(0, name, OBJPROP_CORNER, CORNER_LEFT_UPPER);
        ObjectSetInteger(0, name, OBJPROP_XDISTANCE, x);
        ObjectSetInteger(0, name, OBJPROP_YDISTANCE, y);
    }
    ObjectSetString(0, name, OBJPROP_TEXT, text);
    ObjectSetInteger(0, name, OBJPROP_FONTSIZE, font_size);
    ObjectSetString(0, name, OBJPROP_FONT, "Courier New");
    ObjectSetInteger(0, name, OBJPROP_COLOR, clr);
}

// Timer event - main trading loop (1 second)
// OPTIMIZED V4.0: Split into 2 groups (EVEN/ODD) for better performance
// GROUP 1 (EVEN): Trading core - Read CSDL + Process signals
// GROUP 2 (ODD): Auxiliary - Stoploss + Dashboard + Health checks
void OnTimer() {
    datetime current_time = TimeCurrent();
    MqlDateTime dt;
    TimeToStruct(current_time, dt);
    int current_second = dt.sec;

    // Prevent duplicate execution in same second
    if(current_time == g_ea.timer_last_run_time) return;
    g_ea.timer_last_run_time = current_time;

    //=============================================================================
    // GROUP 1: EVEN SECONDS (0,2,4,6...) - TRADING CORE (HIGH PRIORITY)
    // NHOM 1: GIAY CHAN - GIAO DICH CHINH (UU TIEN CAO)
    //=============================================================================
    // WHY EVEN: SPY Bot writes CSDL on ODD seconds ? EA reads on EVEN ? No file lock conflict
    // TAI SAO CHAN: SPY Bot ghi CSDL giay LE ? EA doc giay CHAN ? Khong xung dot file
    if(!UseEvenOddMode || (current_second % 2 == 0)) {

        // STEP 1: Read CSDL file
        ReadCSDLFile();

        // STEP 2: Map data for all 7 TF
        MapCSDLToEAVariables();

        // STEP 3: Strategy processing loop for 7 TF
        // IMPORTANT: CLOSE function runs on ALL 7 TF (no TF filter)
        // OPEN function respects TF/Strategy toggles
        for(int tf = 0; tf < 7; tf++) {
            if(HasValidS2BaseCondition(tf)) {

                // STEP 3.1: Close ALL BONUS orders when M1 signal changes
                // LOGIC: Check if current TF is M1 (tf==0), if yes close ALL 7 TF bonus orders
                // LOGIC: Kiem tra neu TF hien tai la M1, neu dung dong TAT CA 7 khung lenh bonus
                if(tf == 0 && EnableBonusNews) {
                    CloseAllBonusOrders();  // Close magic[tf][2] for ALL 7 TF
                }

                // STEP 3.2: Close old orders for this TF (ALL 3 strategies)
                CloseAllStrategiesByMagicForTF(tf);

                // STEP 3.3: Open new orders (ONLY if TF enabled)
                if(IsTFEnabled(tf)) {
                    if(S1_HOME) ProcessS1Strategy(tf);
                    if(S2_TREND) ProcessS2Strategy(tf);
                    if(S3_NEWS) ProcessS3Strategy(tf);
                }

                // STEP 3.4: Process Bonus NEWS (scans ALL 7 TF, opens if NEWS >= threshold, must be before old=new)
                if(EnableBonusNews) {
                    ProcessBonusNews();
                }

                // STEP 3.5: Update baseline from CSDL
                g_ea.signal_old[tf] = g_ea.csdl_rows[tf].signal;
                g_ea.timestamp_old[tf] = (datetime)g_ea.csdl_rows[tf].timestamp;
            }
        }
    }

    //=============================================================================
    // GROUP 2: ODD SECONDS (1,3,5,7...) - AUXILIARY (SUPPORT)
    // NHOM 2: GIAY LE - PHU TRO (HO TRO)
    //=============================================================================
    // WHY ODD: These functions don't need fresh CSDL data ? Run independently ? Reduce load on EVEN seconds
    // TAI SAO LE: Cac ham nay khong can CSDL moi ? Chay doc lap ? Giam tai cho giay CHAN
    // NOTE: Respects UseEvenOddMode - if disabled, runs every second
    if(!UseEvenOddMode || (current_second % 2 != 0)) {

        // STEP 1: Check stoploss & take profit
        CheckStoplossAndTakeProfit();

        // STEP 2: Update dashboard
        UpdateDashboard();

        // STEP 3: Emergency check
        CheckAllEmergencyConditions();

        // STEP 4: Weekend reset check (M1 only)
        CheckWeekendReset();

        // STEP 5: Health check at 8h/16h (M1 only)
        CheckSPYBotHealth();
    }
}
