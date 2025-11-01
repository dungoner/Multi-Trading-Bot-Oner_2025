//+------------------------------------------------------------------+
//| Eas_Smf_Oner_V2
//| Multi Timeframe Expert Advisor | EA nhieu khung thoi gian
//| 7 TF × 3 Strategies = 21 orders | 7 khung x 3 chien luoc = 21 lenh
//+------------------------------------------------------------------+
#property copyright "Eas_Smf_Oner_V2"
#property strict

//=============================================================================
//  PART 1: USER INPUTS (30 inputs + 4 separators) | CAU HINH NGUOI DUNG
//=============================================================================

input string _________Menu_A___ = "___A. CORE SETTINGS _________";  //

//--- A.1 Timeframe toggles (7) | Bat/tat khung thoi gian
input bool TF_M1 = true;   // M1 (Signal Sym_M1 Time)
input bool TF_M5 = true;   // M5 (Buy/Sell Symbol_M5)
input bool TF_M15 = true;  // M15 (Signal Symbol_15)
input bool TF_M30 = true;  // M30 (Buy/Sell Symbol_M30)
input bool TF_H1 = true;   // H1 (Signal Symbol_H1 )
input bool TF_H4 = true;   // H4 (Buy/Sell Symbol_H4 )
input bool TF_D1 = true;   // D1 (Signal Symbol_D1)

//--- A.2 Strategy toggles (3) | Bat/tat chien luoc
input bool S1_HOME = true;   // S1: Binary (Home signal)
input bool S2_TREND = true;  // S2: Trend (Follow D1)
input bool S3_NEWS = true;   // S3: News (High impact)

//--- A.3 Risk management (2) | Quan ly rui ro
input double FixedLotSize = 0.1;           // Lot size (0.01-1.0 recommended)
input double MaxLoss_Fallback = -1000.0;   // Max loss fallback ($USD if CSDL fails)

//--- A.4 Data source (1) | Nguon du lieu
enum CSDL_SOURCE_ENUM {
    FOLDER_1 = 0,  // DataAutoOner
    FOLDER_2 = 1,  // DataAutoOner2 (Default)
    FOLDER_3 = 2,  // DataAutoOner3
};
input CSDL_SOURCE_ENUM CSDL_Source = FOLDER_2;  // CSDL folder (signal source)

input string _________Sep_B___ = "___B. STRATEGY CONFIG _________";  //

//--- B.1 S1 NEWS Filter (3) | Loc tin tuc cho S1
input bool S1_UseNewsFilter = true;            // S1: Use NEWS filter (TRUE=strict, FALSE=basic)
input int MinNewsLevelS1 = 20;                 // S1: Min NEWS level (20-70, higher=stricter)
input bool S1_RequireNewsDirection = true;     // S1: Match NEWS direction (signal==news!)

//--- B.2 S2 TREND Mode (1) | Che do xu huong
enum S2_TREND_MODE {
    S2_FOLLOW_D1 = 0,    // Follow D1 (Auto)
    S2_FORCE_BUY = 1,    // Force BUY (manual override)
    S2_FORCE_SELL = -1   // Force SELL (manual override)
};
input S2_TREND_MODE S2_TrendMode = S2_FOLLOW_D1;  // S2: Trend (D1 auto/manual)

//--- B.3 S3 NEWS Configuration (4) | Cau hinh tin tuc
input int MinNewsLevelS3 = 20;         // S3: Min NEWS level (20-70)
input bool EnableBonusNews = true;     // S3: Enable Bonus (extra on high NEWS)
input int BonusOrderCount = 2;         // S3: Bonus count (1-5 orders)
input int MinNewsLevelBonus = 20;      // S3: Min NEWS for Bonus (threshold)

input string _________Sep_C___ = "___C. RISK PROTECTION _________";  //

//--- C.1 Stoploss mode (3) | Che do cat lo
enum STOPLOSS_MODE {
    NONE = 0,            // No stoploss (close by signal only)
    LAYER1_MAXLOSS = 1,  // Layer1: max_loss × lot (from CSDL)
    LAYER2_MARGIN = 2    // Layer2: margin/divisor (emergency)
};
input STOPLOSS_MODE StoplossMode = LAYER1_MAXLOSS;  // Stoploss mode (0=OFF, 1=CSDL, 2=Margin)
input double Layer2_Divisor = 5.0;  // Layer2 divisor (margin/-5 = threshold)

//--- C.2 Take profit (2) | Chot loi
input bool   UseTakeProfit = false;  // Enable take profit (FALSE=OFF, TRUE=ON)
input double TakeProfit_Multiplier = 3;  // TP multiplier (0.5=5%, 1.0=10%, 5.0=50%)

input string _________Sep_D___ = "___D. AUXILIARY SETTINGS _________";  //

//--- D.1 Performance (1) | Hieu suat
input bool UseEvenOddMode = false;  // Even/odd split mode (load balancing)

//--- D.2 Health check & reset (2) | Kiem tra suc khoe
input bool EnableWeekendReset = true;   // Weekend reset (auto close Friday 23:50)
input bool EnableHealthCheck = true;    // Health check (8h/16h SPY bot status)

//--- D.3 Display (2) | Hien thi
input bool ShowDashboard = true;  // Show dashboard (on-chart info)
input bool DebugMode = false;      // Debug mode (verbose logging)

//=============================================================================
//  PART 2: DATA STRUCTURES (1 struct) | CAU TRUC DU LIEU
//=============================================================================

struct CSDLLoveRow {
    double max_loss;   // Col 1: Max loss per 1 LOT | Lo toi da tren 1 lot
    long timestamp;    // Col 2: Timestamp | Thoi gian
    int signal;        // Col 3: Signal (1=BUY,-1=SELL,0=NONE) | Tin hieu
    double pricediff;  // Col 4: Price diff USD (unused) | Chenh lech gia (khong dung)
    int timediff;      // Col 5: Time diff minutes (unused) | Chenh lech thoi gian (khong dung)
    int news;          // Col 6: News CASCADE (±11-16) | Tin tuc CASCADE
};

//=============================================================================
//  PART 3: EA DATA STRUCTURE (116 vars in struct) | CAU TRUC DU LIEU EA
//=============================================================================
// Contains ALL EA data for current symbol (learned from SPY Bot) | Chua tat ca du lieu EA cho symbol hien tai (hoc tu SPY Bot)
// Each EA instance on different chart has its OWN struct | Moi EA instance tren chart khac co struct RIENG
// This prevents conflicts when running multiple symbols simultaneously | Tranh xung dot khi chay nhieu symbol dong thoi
//=============================================================================

struct EASymbolData {
    // Symbol & File info (4 vars) | Thong tin symbol va file
    string symbol_name;          // Symbol name (BTCUSD, LTCUSD...) | Ten symbol
    string symbol_prefix;        // Symbol prefix with underscore | Tien to symbol co gach duoi
    string csdl_folder;          // CSDL folder path | Duong dan thu muc CSDL
    string csdl_filename;        // Full CSDL filename | Ten file CSDL day du

    // CSDL rows (7 rows) | Hang CSDL
    CSDLLoveRow csdl_rows[7];    // 7 rows for 7 TF (M1-D1) | 7 hang cho 7 khung

    // Core signals (14 vars = 2×7 TF) | Tin hieu goc
    int signal_old[7];           // Old signal for comparison | Tin hieu cu de so sanh
    datetime timestamp_old[7];   // Old timestamp for comparison | Thoi gian cu de so sanh
    // NOTE: signal_new, timestamp_new removed - use csdl_rows[tf].signal/timestamp directly
    // CHU THICH: Da loai bo signal_new, timestamp_new - dung truc tiep csdl_rows[tf].signal/timestamp

    // Magic numbers (21 vars) | So hieu lenh
    int magic_numbers[7][3];     // [TF][Strategy]: [0]=S1, [1]=S2, [2]=S3

    // Lot sizes (21 vars - pre-calculated) | Khoi luong tinh truoc
    double lot_sizes[7][3];      // [TF][Strategy]: [0]=S1, [1]=S2, [2]=S3

    // Strategy conditions (3 vars) | Dieu kien chien luoc
    int trend_d1;                // S2: D1 trend (1=BUY,-1=SELL,0=NONE) | Xu huong D1
    int news_level;              // S3: News level (abs value) | Muc do tin tuc
    int news_direction;          // S3: News direction (-1/0/1) | Huong tin tuc

    // Stoploss thresholds (21 vars) | Nguong cat lo
    double layer1_thresholds[7][3];  // [TF][Strategy]: [0]=S1, [1]=S2, [2]=S3

    // Position flags (21 vars) | Co trang thai lenh
    int position_flags[7][3];    // [TF][Strategy]: [0]=S1, [1]=S2, [2]=S3

    // Global state vars (5 vars) - Prevent multi-symbol conflicts | Bien trang thai - Tranh xung dot da symbol
    bool first_run_completed;      // Replaced g_first_run_completed | Thay the g_first_run_completed
    int weekend_last_day;           // Replaced static last_day | Thay the last_day tinh
    int health_last_check_hour;     // Replaced static last_check_hour | Thay the last_check_hour tinh
    datetime timer_last_run_time;   // Replaced static last_run_time | Thay the last_run_time tinh
    string init_summary;            // Init summary for final print in RESTORE | Tom tat khoi dong de in cuoi cung trong RESTORE
};

// Single global instance for current chart | Instance toan cuc duy nhat cho chart hien tai
EASymbolData g_ea;

//=============================================================================
//  PART 4: GLOBAL STATE (0 var) | TRANG THAI TOAN CUC
//=============================================================================
// All global state vars moved to g_ea struct (lines 118-122) | Tat ca bien toan cuc da chuyen vao struct g_ea

//=============================================================================
//  PART 5: UTILITY FUNCTIONS (11 functions) | HAM TRO GIUP
//=============================================================================

// Check if TF is enabled by user | Kiem tra TF co duoc bat boi user
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

// Print debug message if DebugMode enabled | In thong bao debug neu bat che do debug
void DebugPrint(string message) {
    if(!DebugMode) return;
    Print("[DEBUG] ", message);
}

// Log error with code, context and details | Ghi nhan loi voi ma, ngu canh va chi tiet
void LogError(int error_code, string context, string details) {
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
    double min_lot = MarketInfo(Symbol(), MODE_MINLOT);
    double max_lot = MarketInfo(Symbol(), MODE_MAXLOT);
    double lot_step = MarketInfo(Symbol(), MODE_LOTSTEP);

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
    if(OrderType() == OP_BUY) {
        result = OrderClose(ticket, OrderLots(), Bid, 3, clrRed);
    } else if(OrderType() == OP_SELL) {
        result = OrderClose(ticket, OrderLots(), Ask, 3, clrRed);
    }

    if(result) {
        // Success - detailed log printed by caller | Thanh cong - log chi tiet se in boi ham goi
        return true;
    }

    // FAILED - Check error | That bai - Kiem tra loi
    int error = GetLastError();

    // Case 1: Context busy OR Requote ? Retry 1 time
    // TH 1: MT4 ban HOAC Gia thay doi ? Thu lai 1 lan
    if(error == 146 || error == 138) {
        Print("[CLOSE_FAIL] ", reason, " #", ticket, " Err:", error, " (Retry 1x)");
        Sleep(100);
        RefreshRates();

        if(!OrderSelect(ticket, SELECT_BY_TICKET)) {
            Print("[CLOSE_FAIL] ", reason, " #", ticket, " Retry select failed - Skip, EA continues");
            return false;
        }

        if(OrderType() == OP_BUY) {
            result = OrderClose(ticket, OrderLots(), Bid, 3, clrRed);
        } else if(OrderType() == OP_SELL) {
            result = OrderClose(ticket, OrderLots(), Ask, 3, clrRed);
        }

        if(result) {
            // Retry success - detailed log printed by caller | Thanh cong sau retry - log chi tiet se in boi ham goi
            return true;
        }

        error = GetLastError();
        Print("[CLOSE_FAIL] ", reason, " #", ticket, " Retry Err:", error, " - Skip, EA continues");
        return false;
    }

    // Case 2: Other errors ? Log and continue
    // TH 2: Loi khac ? Ghi nhan va tiep tuc
    Print("[CLOSE_FAIL] ", reason, " #", ticket, " Err:", error, " - Skip, EA continues");
    return false;
}

// Draw arrow on chart - simple version | Ve mui ten tren do thi - phien ban don gian

// Open order with smart error handling (max 1 retry) | Mo lenh voi xu ly loi thong minh (toi da 1 retry)
// IMPORTANT: EA never stops on errors, only logs | QUAN TRONG: EA khong bao gio dung vi loi, chi ghi nhan
// Returns: ticket (>0) or -1, caller must check and handle flag | Tra ve ticket hoac -1, nguoi goi phai kiem tra va xu ly co
int OrderSendSafe(int tf, string symbol, int cmd, double lot_smart,
                  double price, int slippage,
                  string comment, int magic, color arrow_color) {

    RefreshRates();

    // Update price | Cap nhat gia
    if(cmd == OP_BUY) price = Ask;
    else if(cmd == OP_SELL) price = Bid;

    // Try 1: Smart lot | Lan 1: Lot thong minh
    int ticket = OrderSend(symbol, cmd, lot_smart, price, slippage, 0, 0, comment, magic, 0, clrNONE);

    if(ticket > 0) {
        // Success - detailed log printed by strategy caller | Thanh cong - log chi tiet se in boi ham chien luoc
        return ticket;
    }

    // FAILED - Check error | That bai - Kiem tra loi
    int error = GetLastError();

    // Case 1: Not enough money OR Invalid volume ? Retry with 0.01 lot
    // TH 1: Het von HOAC Lot sai ? Thu lai voi 0.01 lot
    if(error == 134 || error == 131) {
        Print("[ORDER_FAIL] ", comment, " Err:", error, " (Retry 0.01 lot)");

        ticket = OrderSend(symbol, cmd, 0.01, price, slippage, 0, 0, comment + "_Min", magic, 0, clrNONE);

        if(ticket > 0) {
            // Fallback success - detailed log printed by strategy caller | Thanh cong du phong - log chi tiet se in boi ham chien luoc
            return ticket;
        }

        error = GetLastError();
        Print("[ORDER_FAIL] ", comment, "_Min Err:", error, " - Skip, EA continues");
        return -1;
    }

    // Case 2: Context busy OR Requote ? Retry 1 time
    // TH 2: MT4 ban HOAC Gia thay doi ? Thu lai 1 lan
    if(error == 146 || error == 138) {
        Print("[ORDER_FAIL] ", comment, " Err:", error, " (Retry 1x)");
        Sleep(100);
        RefreshRates();

        if(cmd == OP_BUY) price = Ask;
        else if(cmd == OP_SELL) price = Bid;

        ticket = OrderSend(symbol, cmd, lot_smart, price, slippage, 0, 0, comment, magic, 0, clrNONE);

        if(ticket > 0) {
            // Retry success - detailed log printed by strategy caller | Thanh cong sau retry - log chi tiet se in boi ham chien luoc
            return ticket;
        }

        error = GetLastError();
        Print("[ORDER_FAIL] ", comment, " Retry Err:", error, " - Skip, EA continues");
        return -1;
    }

    // Case 3: Other errors ? Log and continue
    // TH 3: Loi khac ? Ghi nhan va tiep tuc
    Print("[ORDER_FAIL] ", comment, " Err:", error, " - Skip, EA continues");
    return -1;
}

//=============================================================================
//  PART 6: SYMBOL & FILE MANAGEMENT (6 functions) | QUAN LY KY HIEU VA FILE
//=============================================================================

// Trim whitespace from string | Loai bo khoang trang tu chuoi
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

// Discover symbol name from chart | Nhan dien ten ky hieu tu do thi
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

// Initialize symbol recognition from chart | Khoi tao nhan dien ky hieu tu do thi
bool InitializeSymbolRecognition() {
    g_ea.symbol_name = DiscoverSymbolFromChart();

    if(StringLen(g_ea.symbol_name) == 0) {
        LogError(4201, "InitializeSymbolRecognition", "Cannot detect symbol");
        return false;
    }

    DebugPrint("Symbol detected: " + g_ea.symbol_name);
    return true;
}

// Initialize symbol prefix with underscore | Khoi tao tien to ky hieu voi gach duoi
void InitializeSymbolPrefix() {
    g_ea.symbol_prefix = g_ea.symbol_name + "_";
}

// Build full CSDL filename path | Xay dung duong dan day du file CSDL
void BuildCSDLFilename() {
    g_ea.csdl_filename = g_ea.csdl_folder + g_ea.symbol_name + "_LIVE.json";
    DebugPrint("CSDL file: " + g_ea.csdl_filename);
}

//=============================================================================
//  PART 7: CSDL PARSING (3 functions) | PHAN TICH DU LIEU CSDL
//=============================================================================
// ParseLoveRow() - Parse single row | Phan tich 1 dong
// ParseCSDLLoveJSON() - Parse entire JSON | Phan tich toan bo JSON
// TryReadFile() - Try read local file | Thu doc file local
// ReadCSDLFile() - Local file reading only | Chi doc file local

// Parse one row of CSDL data (6 columns) | Phan tich 1 hang du lieu CSDL (6 cot)
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

// Parse CSDL LOVE JSON array (7 rows) | Phan tich mang JSON CSDL LOVE (7 hang)
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

// Helper: Try to read and parse file | Ham phu: Thu doc va phan tich file
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

    return true;  // SUCCESS | Thanh cong
}

// Read CSDL from local file only | Chi doc CSDL tu file local
// Supports 3 sources: FOLDER_1, FOLDER_2, FOLDER_3 | Ho tro 3 nguon: 3 folder local
void ReadCSDLFile() {
    bool success = false;

    // ========== LOCAL FILE (FOLDER_1 / FOLDER_2 / FOLDER_3) ==========
    // TRY 1: Read main local file | Lan 1: Doc file local chinh
    success = TryReadFile(g_ea.csdl_filename);

    if(!success) {
        // TRY 2: Wait 100ms and retry | Lan 2: Cho 100ms va doc lai
        Sleep(100);
        success = TryReadFile(g_ea.csdl_filename);
    }

    if(!success) {
        // TRY 3: Read backup file in DataAutoOner (FOLDER_1) | Lan 3: Doc file du phong trong DataAutoOner
        string backup_file = "DataAutoOner\\" + g_ea.symbol_name + "_LIVE.json";
        success = TryReadFile(backup_file);

        if(success) {
            Print("[BACKUP] Using DataAutoOner (FOLDER_1) file");
        }
    }

    // ========== FINAL CHECK ==========
    if(!success) {
        // ALL FAILED: Keep old data, continue | Tat ca that bai: Giu du lieu cu, tiep tuc
        Print("[WARNING] All read attempts failed. Using old data.");
    }
}

//=============================================================================
//  PART 8: MAGIC NUMBER GENERATION (3 functions) | TAO SO HIEU LENH
//=============================================================================

// Generate symbol hash from ALL characters using DJB2 algorithm | Tao ma hash tu TAT CA ky tu dung thuat toan DJB2
// This ensures unique hash for each symbol, preventing magic number collisions | Dam bao hash duy nhat cho moi symbol, tranh trung magic number
int GenerateSymbolHash(string symbol) {
    int hash = 5381;  // DJB2 hash initial value | Gia tri khoi dau DJB2

    // Process ALL characters in symbol name | Xu ly TAT CA ky tu trong ten symbol
    for(int i = 0; i < StringLen(symbol); i++) {
        int c = StringGetCharacter(symbol, i);
        hash = ((hash << 5) + hash) + c;  // hash * 33 + c (DJB2 formula)
    }

    // Make positive and limit to reasonable range (100-9999) | Dam bao duong va gioi han pham vi
    hash = MathAbs(hash % 10000);  // Modulo 10000 = range 0-9999

    if(hash < 100) hash += 100;  // Minimum 100 to avoid small numbers | Toi thieu 100 tranh so nho

    return hash;
}

// Generate smart magic: hash + tf*1000 + strat*100 | Tao so hieu thong minh theo cong thuc
int GenerateSmartMagicNumber(string symbol, int tf_index, int strategy_index) {
    int symbol_hash = GenerateSymbolHash(symbol);
    int tf_code = tf_index * 1000;      // M1=0, M5=1000, M15=2000, ...
    int strategy_code = strategy_index * 100;  // S1=0, S2=100, S3=200

    return symbol_hash + tf_code + strategy_code;
}

// Generate all 21 magic numbers (7 TF × 3 S) | Tao tat ca 21 so hieu (7 khung x 3 chien luoc)
bool GenerateMagicNumbers() {
    string symbol = g_ea.symbol_name;

    for(int tf = 0; tf < 7; tf++) {
        for(int s = 0; s < 3; s++) {
            g_ea.magic_numbers[tf][s] = GenerateSmartMagicNumber(symbol, tf, s);
        }
    }

    // Silent - only debug log | Im lang - chi log debug
    DebugPrint("Magic M1: S1=" + IntegerToString(g_ea.magic_numbers[0][0]) +
               ", S2=" + IntegerToString(g_ea.magic_numbers[0][1]) +
               ", S3=" + IntegerToString(g_ea.magic_numbers[0][2]));

    return true;
}

//=============================================================================
//  PART 9: LOT SIZE CALCULATION (2 functions) | TINH TOAN KHOI LUONG
//=============================================================================

// Calculate lot with progressive formula | Tinh lot theo cong thuc luy tien
// Formula: (base × strategy_multiplier) + tf_increment | Cong thuc: (goc × he so chien luoc) + tang TF
// Result format: X.YZ where Y=strategy(1-3), Z=TF(1-7) | Dinh dang: X.YZ voi Y=chien luoc, Z=khung
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

// Pre-calculate all 21 lot sizes once | Tinh truoc tat ca 21 khoi luong mot lan
// Called once in OnInit for performance | Goi 1 lan trong OnInit de tang hieu suat
void InitializeLotSizes() {
    for(int tf = 0; tf < 7; tf++) {
        for(int s = 0; s < 3; s++) {
            g_ea.lot_sizes[tf][s] = CalculateSmartLotSize(FixedLotSize, tf, s);
        }
    }

    // Silent - only debug log | Im lang - chi log debug
    DebugPrint("Lot M1: S1=" + DoubleToStr(g_ea.lot_sizes[0][0], 2) +
               " S2=" + DoubleToStr(g_ea.lot_sizes[0][1], 2) +
               " S3=" + DoubleToStr(g_ea.lot_sizes[0][2], 2));
}

//=============================================================================
//  PART 10: LAYER1 STOPLOSS INIT (1 function) | KHOI TAO CAT LO TANG 1
//=============================================================================

// Initialize all 21 Layer1 thresholds (7 TF × 3 S) | Khoi tao 21 nguong cat lo tang 1
// OPTIMIZED: Uses pre-calculated lot sizes | TOI UU: Dung khoi luong da tinh truoc
void InitializeLayer1Thresholds() {
    for(int tf = 0; tf < 7; tf++) {
        double max_loss_per_lot = g_ea.csdl_rows[tf].max_loss;

        if(MathAbs(max_loss_per_lot) < 1.0) {
            max_loss_per_lot = MaxLoss_Fallback;
        }

        // Use pre-calculated lots instead of calculating again | Dung lot da tinh thay vi tinh lai
        for(int s = 0; s < 3; s++) {
            g_ea.layer1_thresholds[tf][s] = max_loss_per_lot * g_ea.lot_sizes[tf][s];
        }
    }

    // Silent - only debug log | Im lang - chi log debug
    DebugPrint("Layer1 M1: S1=$" + DoubleToStr(g_ea.layer1_thresholds[0][0], 2) +
               " S2=$" + DoubleToStr(g_ea.layer1_thresholds[0][1], 2) +
               " S3=$" + DoubleToStr(g_ea.layer1_thresholds[0][2], 2));
}

//=============================================================================
//  PART 11: MAP CSDL TO EA (1 function) | ANH XA CSDL SANG EA
//=============================================================================

// Map CSDL data to EA variables for all 7 TF | Anh xa du lieu CSDL sang bien EA cho 7 khung
// OPTIMIZED: Single TREND variable + Smart NEWS mode selection | TOI UU: Bien TREND don + Che do NEWS thong minh
// NOTE: signal_new/timestamp_new removed - use csdl_rows[tf] directly | Loai bo signal_new/timestamp_new - dung truc tiep csdl_rows[tf]
void MapCSDLToEAVariables() {
    // S2: TREND - Always use D1 (row 6) for all TF | Luon dung D1 cho tat ca TF
    g_ea.trend_d1 = g_ea.csdl_rows[6].signal;

    // S3: NEWS - Use STRONGEST NEWS from all 7 TF | Dung TIN TUC MANH NHAT tu 7 khung
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
//  PART 12: POSITION MANAGEMENT (2 functions) | QUAN LY LENH
//=============================================================================
// RestoreOrCleanupPositions() - Restore/cleanup on EA startup | Khoi phuc/don dep khi EA khoi dong
// CloseAllStrategiesByMagicForTF() - Close all strategies for specific TF | Dong tat ca chien luoc cho 1 TF cu the

// Restore or cleanup positions on EA startup | Khoi phuc hoac don dep lenh khi EA khoi dong
// PHASE 2: Signal-based validation with consolidated AND logic | Xac thuc dua tren tin hieu voi logic AND gop
// LOGIC: Scan 7×3 combinations, if ANY condition fails ? CLOSE, if ALL pass ? KEEP
bool RestoreOrCleanupPositions() {
    // Step 1: Reset all flags first | Buoc 1: Reset tat ca co truoc
    for(int tf = 0; tf < 7; tf++) {
        for(int s = 0; s < 3; s++) {
            g_ea.position_flags[tf][s] = 0;
        }
    }

    int kept_count = 0;
    int closed_count = 0;

    // Step 2: Scan all open orders | Buoc 2: Quet tat ca lenh mo
    for(int i = OrdersTotal() - 1; i >= 0; i--) {
        if(!OrderSelect(i, SELECT_BY_POS, MODE_TRADES)) continue;

        // Get order info | Lay thong tin lenh
        int magic = OrderMagicNumber();
        int ticket = OrderTicket();
        int order_type = OrderType();
        string order_symbol = OrderSymbol();

        // Filter: Only this symbol | Loc: Chi lenh cua symbol nay
        if(order_symbol != Symbol()) continue;

        // Get order signal from MT4 | Lay tin hieu tu lenh MT4
        int order_signal = 0;
        if(order_type == OP_BUY) order_signal = 1;
        else if(order_type == OP_SELL) order_signal = -1;
        else continue;  // Skip pending orders | Bo qua lenh pending

        // Step 3: Scan 7×3 combinations to find valid match | Buoc 3: Quet 7x3 de tim khop hop le
        bool found = false;
        int found_tf = -1;
        int found_s = -1;

        for(int tf = 0; tf < 7; tf++) {
            // Skip if TF disabled | Bo qua neu TF tat
            if(!IsTFEnabled(tf)) continue;

            for(int s = 0; s < 3; s++) {
                // CONDITION 1: Magic match | Dieu kien 1: Magic khop
                bool cond1_magic = (magic == g_ea.magic_numbers[tf][s]);

                // CONDITION 2: Signal pair match (4 variables) | Dieu kien 2: Cap tin hieu khop (4 bien)
                // Order signal == OLD == CSDL (triple match) AND timestamp OLD == CSDL (locked)
                // Tin hieu lenh == CU == CSDL (khop 3) VA timestamp CU == CSDL (khoa)
                bool cond2_signal_pair = (order_signal == g_ea.signal_old[tf] &&
                                          order_signal == g_ea.csdl_rows[tf].signal &&
                                          g_ea.timestamp_old[tf] == (datetime)g_ea.csdl_rows[tf].timestamp);

                // CONDITION 3: Strategy enabled | Dieu kien 3: Chien luoc bat
                bool cond3_strategy = false;
                if(s == 0) cond3_strategy = S1_HOME;
                else if(s == 1) cond3_strategy = S2_TREND;
                else if(s == 2) cond3_strategy = S3_NEWS;

                // CONDITION 4: Not duplicate (flag must be 0) | Dieu kien 4: Khong trung lap
                bool cond4_unique = (g_ea.position_flags[tf][s] == 0);

                // CONSOLIDATED CHECK: ALL with AND | KIEM TRA GOP: Tat ca voi AND
                if(cond1_magic && cond2_signal_pair && cond3_strategy && cond4_unique) {
                    found = true;
                    found_tf = tf;
                    found_s = s;
                    break;  // Exit strategy loop | Thoat vong chien luoc
                }
            }

            if(found) break;  // Exit TF loop | Thoat vong TF
        }

        // Step 4: Decide KEEP or CLOSE | Buoc 4: Quyet dinh GIU hoac DONG
        if(found) {
            // ? KEEP: All conditions passed ? Restore flag | GIU: Tat ca dieu kien qua ? Khoi phuc co
            g_ea.position_flags[found_tf][found_s] = 1;
            kept_count++;

            DebugPrint("[RESTORE_KEEP] #" + IntegerToString(ticket) +
                      " TF:" + IntegerToString(found_tf) + " S:" + IntegerToString(found_s + 1) +
                      " Signal:" + IntegerToString(order_signal) + " | Flag=1");

        } else {
            // ? CLOSE: ANY condition failed ? Close order | DONG: Bat ky dieu kien sai ? Dong lenh
            CloseOrderSafely(ticket, "RESTORE_INVALID");
            closed_count++;

            // CRITICAL: Reset flag if this was a known magic | QUAN TRONG: Reset co neu la magic da biet
            // Prevents stoploss function from miscalculating | Tranh ham stoploss tinh sai
            for(int tf_check = 0; tf_check < 7; tf_check++) {
                for(int s_check = 0; s_check < 3; s_check++) {
                    if(magic == g_ea.magic_numbers[tf_check][s_check]) {
                        g_ea.position_flags[tf_check][s_check] = 0;  // Ensure flag = 0 | Dam bao co = 0
                        break;
                    }
                }
            }

            DebugPrint("[RESTORE_CLOSE] #" + IntegerToString(ticket) +
                      " Magic:" + IntegerToString(magic) +
                      " Signal:" + IntegerToString(order_signal) + " | INVALID");
        }
    }

    // Step 5: Final summary report (1 line) | Buoc 5: Bao cao tom tat cuoi cung (1 dong)
    Print(g_ea.init_summary, " | RESTORE: KEPT=", kept_count, " CLOSED=", closed_count);

    // Debug: Print restored flags (optional) | In co da khoi phuc (tuy chon)
    if(DebugMode && kept_count > 0) {
        string tf_names[7] = {"M1", "M5", "M15", "M30", "H1", "H4", "D1"};
        for(int tf = 0; tf < 7; tf++) {
            bool has_flag = false;
            for(int s = 0; s < 3; s++) {
                if(g_ea.position_flags[tf][s] == 1) {
                    has_flag = true;
                    break;
                }
            }
            if(has_flag) {
                Print("[RESTORE_FLAGS] ", tf_names[tf], ": S1=", g_ea.position_flags[tf][0],
                      " S2=", g_ea.position_flags[tf][1], " S3=", g_ea.position_flags[tf][2]);
            }
        }
    }

    return true;
}

// Close all strategies for specific TF only | Dong tat ca chien luoc cho 1 khung cu the
void CloseAllStrategiesByMagicForTF(int tf) {
    string tf_names[7] = {"M1", "M5", "M15", "M30", "H1", "H4", "D1"};
    string strategy_names[3] = {"S1", "S2", "S3"};
    int signal_old = g_ea.signal_old[tf];
    int signal_new = g_ea.csdl_rows[tf].signal;

    for(int i = OrdersTotal() - 1; i >= 0; i--) {
        if(!OrderSelect(i, SELECT_BY_POS, MODE_TRADES)) continue;
        if(OrderSymbol() != Symbol()) continue;

        int magic = OrderMagicNumber();
        int ticket = OrderTicket();
        int order_type = OrderType();
        double order_lot = OrderLots();
        double order_profit = OrderProfit() + OrderSwap() + OrderCommission();

        // Check if magic belongs to any of 3 strategies in this TF | Kiem tra magic thuoc 1 trong 3 chien luoc cua TF nay
        int strategy_index = -1;
        for(int s = 0; s < 3; s++) {
            if(magic == g_ea.magic_numbers[tf][s]) {
                strategy_index = s;
                break;
            }
        }

        if(strategy_index >= 0) {
            string order_type_str = (order_type == OP_BUY) ? "BUY" : "SELL";
            Print(">> [CLOSE] SIGNAL_CHG TF=", tf_names[tf], " S=", (strategy_index+1),
                  " | #", ticket, " ", order_type_str, " ", DoubleToStr(order_lot, 2),
                  " | Profit=$", DoubleToStr(order_profit, 2),
                  " | Old:", signal_old, " New:", signal_new, " <<");

            CloseOrderSafely(ticket, "SIGNAL_CHANGE");
        }
    }

    // Reset all 3 flags for this TF | Dat lai 3 co cua TF nay
    for(int s = 0; s < 3; s++) {
        g_ea.position_flags[tf][s] = 0;
    }
}

//=============================================================================
//  PART 13: BASE CONDITION CHECK (1 function) | KIEM TRA DIEU KIEN GOC
//=============================================================================

// Check if signal changed and new signal valid | Kiem tra tin hieu co thay doi va tin hieu moi hop le
// OPTIMIZED: Read signal/timestamp directly from csdl_rows | TOI UU: Doc tin hieu/thoi gian truc tiep tu csdl_rows
bool HasValidS2BaseCondition(int tf) {
    int signal_old = g_ea.signal_old[tf];
    int signal_new = g_ea.csdl_rows[tf].signal;
    datetime timestamp_old = g_ea.timestamp_old[tf];
    datetime timestamp_new = (datetime)g_ea.csdl_rows[tf].timestamp;

    return (signal_old != signal_new && signal_new != 0 && timestamp_old < timestamp_new);
}

//=============================================================================
//  PART 14: STRATEGY PROCESSING (3 functions) | XU LY CHIEN LUOC
//=============================================================================

// S1 Basic: Open order when signal comes (no NEWS filter) | S1 Co ban: Mo lenh khi tin hieu ve (khong loc NEWS)
// Used when S1_UseNewsFilter = FALSE | Dung khi S1_UseNewsFilter = FALSE
void ProcessS1BasicStrategy(int tf) {
    string tf_names[7] = {"M1", "M5", "M15", "M30", "H1", "H4", "D1"};
    int current_signal = g_ea.csdl_rows[tf].signal;

    RefreshRates();

    if(current_signal == 1) {
        int ticket = OrderSendSafe(tf, Symbol(), OP_BUY, g_ea.lot_sizes[tf][0],
                                   Ask, 3,
                                   "S1_" + tf_names[tf], g_ea.magic_numbers[tf][0], clrBlue);
        if(ticket > 0) {
            g_ea.position_flags[tf][0] = 1;
            Print(">>> [OPEN] S1_BASIC TF=", tf_names[tf], " | #", ticket, " BUY ",
                  DoubleToStr(g_ea.lot_sizes[tf][0], 2), " @", DoubleToStr(Ask, Digits),
                  " | Sig=+1 <<<");
        } else {
            g_ea.position_flags[tf][0] = 0;
            Print("[S1_BASIC_", tf_names[tf], "] Failed: ", GetLastError());
        }
    }
    else if(current_signal == -1) {
        int ticket = OrderSendSafe(tf, Symbol(), OP_SELL, g_ea.lot_sizes[tf][0],
                                   Bid, 3,
                                   "S1_" + tf_names[tf], g_ea.magic_numbers[tf][0], clrRed);
        if(ticket > 0) {
            g_ea.position_flags[tf][0] = 1;
            Print(">>> [OPEN] S1_BASIC TF=", tf_names[tf], " | #", ticket, " SELL ",
                  DoubleToStr(g_ea.lot_sizes[tf][0], 2), " @", DoubleToStr(Bid, Digits),
                  " | Sig=-1 <<<");
        } else {
            g_ea.position_flags[tf][0] = 0;
            Print("[S1_BASIC_", tf_names[tf], "] Failed: ", GetLastError());
        }
    }
}

// S1 NEWS Filter: Check NEWS before opening order | S1 Loc NEWS: Kiem tra NEWS truoc khi mo lenh
// Used when S1_UseNewsFilter = TRUE | Dung khi S1_UseNewsFilter = TRUE
// Conditions: 1) news_abs >= MinNewsLevelS1, 2) signal == news_direction (if required)
void ProcessS1NewsFilterStrategy(int tf) {
    string tf_names[7] = {"M1", "M5", "M15", "M30", "H1", "H4", "D1"};
    int current_signal = g_ea.csdl_rows[tf].signal;
    int tf_news = g_ea.csdl_rows[tf].news;
    int news_abs = MathAbs(tf_news);

    // Condition 1: Check NEWS level >= MinNewsLevelS1 | Dieu kien 1: Kiem tra muc NEWS
    if(news_abs < MinNewsLevelS1) {
        DebugPrint("S1_NEWS: " + tf_names[tf] + " NEWS=" + IntegerToString(news_abs) +
                   " < Min=" + IntegerToString(MinNewsLevelS1) + ", SKIP");
        return;
    }

    // Condition 2: Check NEWS direction matches signal (if required) | Dieu kien 2: Kiem tra huong NEWS khop signal
    if(S1_RequireNewsDirection) {
        int news_direction = (tf_news > 0) ? 1 : -1;

        if(current_signal != news_direction) {
            DebugPrint("S1_NEWS: " + tf_names[tf] + " Signal=" + IntegerToString(current_signal) +
                       " != NewsDir=" + IntegerToString(news_direction) + ", SKIP");
            return;
        }
    }

    // PASS all conditions → Open order | PASS tat ca dieu kien → Mo lenh
    RefreshRates();

    if(current_signal == 1) {
        int ticket = OrderSendSafe(tf, Symbol(), OP_BUY, g_ea.lot_sizes[tf][0],
                                   Ask, 3,
                                   "S1_" + tf_names[tf], g_ea.magic_numbers[tf][0], clrBlue);
        if(ticket > 0) {
            g_ea.position_flags[tf][0] = 1;
            string filter_str = S1_UseNewsFilter ? "ON" : "OFF";
            string dir_str = S1_RequireNewsDirection ? "REQ" : "ANY";
            Print(">>> [OPEN] S1_NEWS TF=", tf_names[tf], " | #", ticket, " BUY ",
                  DoubleToStr(g_ea.lot_sizes[tf][0], 2), " @", DoubleToStr(Ask, Digits),
                  " | Sig=+1 News=", tf_news > 0 ? "+" : "", tf_news,
                  " Filter:", filter_str, " Dir:", dir_str, " <<<");
        } else {
            g_ea.position_flags[tf][0] = 0;
            Print("[S1_NEWS_", tf_names[tf], "] Failed: ", GetLastError());
        }
    }
    else if(current_signal == -1) {
        int ticket = OrderSendSafe(tf, Symbol(), OP_SELL, g_ea.lot_sizes[tf][0],
                                   Bid, 3,
                                   "S1_" + tf_names[tf], g_ea.magic_numbers[tf][0], clrRed);
        if(ticket > 0) {
            g_ea.position_flags[tf][0] = 1;
            string filter_str = S1_UseNewsFilter ? "ON" : "OFF";
            string dir_str = S1_RequireNewsDirection ? "REQ" : "ANY";
            Print(">>> [OPEN] S1_NEWS TF=", tf_names[tf], " | #", ticket, " SELL ",
                  DoubleToStr(g_ea.lot_sizes[tf][0], 2), " @", DoubleToStr(Bid, Digits),
                  " | Sig=-1 News=", tf_news > 0 ? "+" : "", tf_news,
                  " Filter:", filter_str, " Dir:", dir_str, " <<<");
        } else {
            g_ea.position_flags[tf][0] = 0;
            Print("[S1_NEWS_", tf_names[tf], "] Failed: ", GetLastError());
        }
    }
}

// S1 Strategy Router: Call appropriate function based on filter setting | Bo dinh tuyen S1: Goi ham tuong ung theo cai dat
void ProcessS1Strategy(int tf) {
    if(S1_UseNewsFilter) {
        ProcessS1NewsFilterStrategy(tf);
    } else {
        ProcessS1BasicStrategy(tf);
    }
}

// Process S2 (Trend Following) strategy for TF | Xu ly chien luoc S2 (Theo xu huong)
// OPTIMIZED: Uses single g_trend_d1 + pre-calculated lot + reads signal from CSDL | TOI UU: Dung g_trend_d1 don + lot da tinh + doc tin hieu tu CSDL
// ENHANCED: Support 3 modes (auto D1 / force BUY / force SELL) | CAI TIEN: Ho tro 3 che do (tu dong D1 / chi BUY / chi SELL)
void ProcessS2Strategy(int tf) {
    int current_signal = g_ea.csdl_rows[tf].signal;

    // NEW: Determine trend based on mode | Xac dinh xu huong theo che do
    int trend_to_follow = 0;

    if(S2_TrendMode == S2_FOLLOW_D1) {
        trend_to_follow = g_ea.trend_d1;  // Follow D1 trend (auto) | Theo xu huong D1 (tu dong)
    }
    else if(S2_TrendMode == S2_FORCE_BUY) {
        trend_to_follow = 1;  // Force BUY only | Chi danh BUY
    }
    else if(S2_TrendMode == S2_FORCE_SELL) {
        trend_to_follow = -1;  // Force SELL only | Chi danh SELL
    }

    // Check signal matches trend | Kiem tra tin hieu khop voi xu huong
    if(current_signal != trend_to_follow) {
        DebugPrint("S2_TREND: Signal=" + IntegerToString(current_signal) +
                   " != Trend=" + IntegerToString(trend_to_follow) + ", skip");
        return;
    }

    RefreshRates();

    string tf_names[7] = {"M1", "M5", "M15", "M30", "H1", "H4", "D1"};

    if(current_signal == 1) {
        int ticket = OrderSendSafe(tf, Symbol(), OP_BUY, g_ea.lot_sizes[tf][1],
                                   Ask, 3,
                                   "S2_" + tf_names[tf], g_ea.magic_numbers[tf][1], clrBlue);
        if(ticket > 0) {
            g_ea.position_flags[tf][1] = 1;
            string trend_str = trend_to_follow == 1 ? "UP" : "DOWN";
            string mode_str = (S2_TrendMode == 0) ? "AUTO" : (S2_TrendMode == 1) ? "FBUY" : "FSELL";
            Print(">>> [OPEN] S2_TREND TF=", tf_names[tf], " | #", ticket, " BUY ",
                  DoubleToStr(g_ea.lot_sizes[tf][1], 2), " @", DoubleToStr(Ask, Digits),
                  " | Sig=+1 Trend:", trend_str, " Mode:", mode_str, " <<<");
        } else {
            g_ea.position_flags[tf][1] = 0;
            Print("[S2_", tf_names[tf], "] Failed: ", GetLastError());
        }
    }
    else if(current_signal == -1) {
        int ticket = OrderSendSafe(tf, Symbol(), OP_SELL, g_ea.lot_sizes[tf][1],
                                   Bid, 3,
                                   "S2_" + tf_names[tf], g_ea.magic_numbers[tf][1], clrRed);
        if(ticket > 0) {
            g_ea.position_flags[tf][1] = 1;
            string trend_str = trend_to_follow == -1 ? "DOWN" : "UP";
            string mode_str = (S2_TrendMode == 0) ? "AUTO" : (S2_TrendMode == 1) ? "FBUY" : "FSELL";
            Print(">>> [OPEN] S2_TREND TF=", tf_names[tf], " | #", ticket, " SELL ",
                  DoubleToStr(g_ea.lot_sizes[tf][1], 2), " @", DoubleToStr(Bid, Digits),
                  " | Sig=-1 Trend:", trend_str, " Mode:", mode_str, " <<<");
        } else {
            g_ea.position_flags[tf][1] = 0;
            Print("[S2_", tf_names[tf], "] Failed: ", GetLastError());
        }
    }
}

// Process S3 (News Alignment) strategy for TF | Xu ly chien luoc S3 (Theo tin tuc)
// OPTIMIZED: Uses per-TF NEWS + pre-calculated lot + reads signal from CSDL | TOI UU: Dung NEWS theo TF + lot da tinh + doc tin hieu tu CSDL
void ProcessS3Strategy(int tf) {
    // Read NEWS for this TF | Doc NEWS cua TF nay
    int tf_news = g_ea.csdl_rows[tf].news;
    int news_abs = MathAbs(tf_news);

    // Check NEWS level >= MinNewsLevelS3 | Kiem tra muc NEWS >= nguong
    if(news_abs < MinNewsLevelS3) {
        DebugPrint("S3_NEWS: TF" + IntegerToString(tf) + " NEWS=" + IntegerToString(news_abs) + " < " + IntegerToString(MinNewsLevelS3) + ", skip");
        return;
    }

    // Check NEWS direction matches signal | Kiem tra huong NEWS khop signal
    int news_direction = (tf_news > 0) ? 1 : -1;
    int current_signal = g_ea.csdl_rows[tf].signal;

    if(current_signal != news_direction) {
        DebugPrint("S3_NEWS: Signal=" + IntegerToString(current_signal) + " != NewsDir=" + IntegerToString(news_direction) + ", skip");
        return;
    }

    RefreshRates();

    string tf_names[7] = {"M1", "M5", "M15", "M30", "H1", "H4", "D1"};

    if(current_signal == 1) {
        int ticket = OrderSendSafe(tf, Symbol(), OP_BUY, g_ea.lot_sizes[tf][2],
                                   Ask, 3,
                                   "S3_" + tf_names[tf], g_ea.magic_numbers[tf][2], clrBlue);
        if(ticket > 0) {
            g_ea.position_flags[tf][2] = 1;
            string arrow = (tf_news > 0) ? "↑" : "↓";
            Print(">>> [OPEN] S3_NEWS TF=", tf_names[tf], " | #", ticket, " BUY ",
                  DoubleToStr(g_ea.lot_sizes[tf][2], 2), " @", DoubleToStr(Ask, Digits),
                  " | Sig=+1 News=", tf_news > 0 ? "+" : "", tf_news, arrow, " <<<");
        } else {
            g_ea.position_flags[tf][2] = 0;
            Print("[S3_", tf_names[tf], "] Failed: ", GetLastError());
        }
    }
    else if(current_signal == -1) {
        int ticket = OrderSendSafe(tf, Symbol(), OP_SELL, g_ea.lot_sizes[tf][2],
                                   Bid, 3,
                                   "S3_" + tf_names[tf], g_ea.magic_numbers[tf][2], clrRed);
        if(ticket > 0) {
            g_ea.position_flags[tf][2] = 1;
            string arrow = (tf_news > 0) ? "↑" : "↓";
            Print(">>> [OPEN] S3_NEWS TF=", tf_names[tf], " | #", ticket, " SELL ",
                  DoubleToStr(g_ea.lot_sizes[tf][2], 2), " @", DoubleToStr(Bid, Digits),
                  " | Sig=-1 News=", tf_news > 0 ? "+" : "", tf_news, arrow, " <<<");
        } else {
            g_ea.position_flags[tf][2] = 0;
            Print("[S3_", tf_names[tf], "] Failed: ", GetLastError());
        }
    }
}

// Process Bonus NEWS - Scan all 7 TF and open multiple orders if NEWS detected
// Xu ly tin tuc Bonus - Quet 7 TF va mo nhieu lenh neu phat hien tin tuc
void ProcessBonusNews() {
    if(!EnableBonusNews) return;

    string tf_names[7] = {"M1", "M5", "M15", "M30", "H1", "H4", "D1"};

    // Scan all 7 TF | Quet tat ca 7 TF
    for(int tf = 0; tf < 7; tf++) {
        // BUGFIX: Skip if TF disabled | Bo qua neu TF bi tat
        if(!IsTFEnabled(tf)) continue;

        int tf_news = g_ea.csdl_rows[tf].news;
        int news_abs = MathAbs(tf_news);

        // Skip if NEWS below threshold | Bo qua neu NEWS duoi nguong
        if(news_abs < MinNewsLevelBonus) continue;

        // Determine direction | Xac dinh huong
        int news_direction = (tf_news > 0) ? 1 : -1;

        RefreshRates();

        // Open BonusOrderCount orders | Mo so luong lenh Bonus
        int opened_count = 0;
        string ticket_list = "";
        double entry_price = 0;

        for(int count = 0; count < BonusOrderCount; count++) {
            if(news_direction == 1) {
                int ticket = OrderSendSafe(tf, Symbol(), OP_BUY, g_ea.lot_sizes[tf][2],
                                           Ask, 3,
                                           "BONUS_" + tf_names[tf], g_ea.magic_numbers[tf][2], clrGold);
                if(ticket > 0) {
                    opened_count++;
                    if(ticket_list != "") ticket_list = ticket_list + ",";
                    ticket_list = ticket_list + IntegerToString(ticket);
                    if(entry_price == 0) entry_price = Ask;
                }
            } else {
                int ticket = OrderSendSafe(tf, Symbol(), OP_SELL, g_ea.lot_sizes[tf][2],
                                           Bid, 3,
                                           "BONUS_" + tf_names[tf], g_ea.magic_numbers[tf][2], clrOrange);
                if(ticket > 0) {
                    opened_count++;
                    if(ticket_list != "") ticket_list = ticket_list + ",";
                    ticket_list = ticket_list + IntegerToString(ticket);
                    if(entry_price == 0) entry_price = Bid;
                }
            }
        }

        // Consolidated log after loop | Log tong ket sau vong lap
        if(opened_count > 0) {
            string arrow = (tf_news > 0) ? "↑" : "↓";
            double total_lot = opened_count * g_ea.lot_sizes[tf][2];
            Print(">>> [OPEN] BONUS TF=", tf_names[tf], " | ", opened_count, "×",
                  news_direction == 1 ? "BUY" : "SELL", " Total:",
                  DoubleToStr(total_lot, 2), " @", DoubleToStr(entry_price, Digits),
                  " | News=", tf_news > 0 ? "+" : "", tf_news, arrow,
                  " Tickets:", ticket_list, " <<<");
        }
    }
}

// Close all Bonus NEWS orders when M1 signal arrives
// Dong tat ca lenh Bonus khi tin hieu M1 den
void CloseAllBonusOrders() {
    string tf_names[7] = {"M1", "M5", "M15", "M30", "H1", "H4", "D1"};

    // Scan all 7 TF magic numbers | Quet tat ca 7 magic cua TF
    for(int tf = 0; tf < 7; tf++) {
        // BUGFIX: Skip if TF disabled | Bo qua neu TF bi tat
        if(!IsTFEnabled(tf)) continue;

        int target_magic = g_ea.magic_numbers[tf][2];
        int closed_count = 0;
        int total_count = 0;
        double total_profit = 0;
        double total_lot = 0;

        // Scan all orders on MT4 | Quet tat ca lenh tren MT4
        for(int i = OrdersTotal() - 1; i >= 0; i--) {
            if(!OrderSelect(i, SELECT_BY_POS, MODE_TRADES)) continue;
            if(OrderSymbol() != Symbol()) continue;

            // If magic matches, close it | Neu magic khop, dong lenh
            if(OrderMagicNumber() == target_magic) {
                total_count++;
                double order_profit = OrderProfit() + OrderSwap() + OrderCommission();
                double order_lot = OrderLots();

                if(CloseOrderSafely(OrderTicket(), "BONUS_M1_CLOSE")) {
                    closed_count++;
                    total_profit += order_profit;
                    total_lot += order_lot;
                }
            }
        }

        // Consolidated log after closing | Log tong ket sau khi dong
        if(total_count > 0) {
            Print(">> [CLOSE] BONUS_M1 TF=", tf_names[tf],
                  " | ", total_count, " orders Total:", DoubleToStr(total_lot, 2),
                  " | Profit=$", DoubleToStr(total_profit, 2),
                  " | Closed:", closed_count, "/", total_count, " <<");
        }

        // Reset flag | Dat lai co
        g_ea.position_flags[tf][2] = 0;
    }
}

//=============================================================================
//  PART 15: STOPLOSS CHECKS (2 functions) | KIEM TRA CAT LO
//=============================================================================

// Check stoploss & take profit for all 21 orders | Kiem tra cat lo & chot loi cho 21 lenh
// Stoploss: 2 layers (LAYER1, LAYER2) | Cat lo: 2 tang
// Take profit: 1 layer (based on max_loss × multiplier) | Chot loi: 1 tang (dua tren max_loss × he so)
void CheckStoplossAndTakeProfit() {
    if(OrdersTotal() == 0) return;

    // Scan all orders once | Quet tat ca lenh 1 lan duy nhat
    for(int i = OrdersTotal() - 1; i >= 0; i--) {
        if(!OrderSelect(i, SELECT_BY_POS, MODE_TRADES)) continue;
        if(OrderSymbol() != Symbol()) continue;

        int magic = OrderMagicNumber();
        int ticket = OrderTicket();
        double profit = OrderProfit() + OrderSwap() + OrderCommission();

        // Find TF + Strategy from magic | Tim TF + Chien luoc tu magic
        bool found = false;
        for(int tf = 0; tf < 7; tf++) {
            for(int s = 0; s < 3; s++) {
                if(magic == g_ea.magic_numbers[tf][s] &&
                   g_ea.position_flags[tf][s] == 1) {

                    string strategy_names[3] = {"S1", "S2", "S3"};
                    string tf_names[7] = {"M1", "M5", "M15", "M30", "H1", "H4", "D1"};
                    bool order_closed = false;

                    // ===== SECTION 1: STOPLOSS (2 layers) =====
                    if(StoplossMode != NONE) {
                        double sl_threshold = 0.0;
                        string mode_name = "";

                        if(StoplossMode == LAYER1_MAXLOSS) {
                            // Layer1: Use pre-calculated threshold (max_loss × lot) | Dung nguong da tinh (max_loss × lot)
                            sl_threshold = g_ea.layer1_thresholds[tf][s];
                            mode_name = "LAYER1_SL";
                        }
                        else if(StoplossMode == LAYER2_MARGIN) {
                            // Layer2: Calculate from margin (emergency) | Tinh tu margin (khan cap)
                            double margin_usd = OrderLots() * MarketInfo(Symbol(), MODE_MARGINREQUIRED);
                            sl_threshold = -(margin_usd / Layer2_Divisor);
                            mode_name = "LAYER2_SL";
                        }

                        // Check and close if loss exceeds threshold | Kiem tra va dong neu lo vuot nguong
                        if(profit <= sl_threshold) {
                            string short_mode = (mode_name == "LAYER1_SL") ? "L1_SL" : "L2_SL";
                            string order_type_str = (OrderType() == OP_BUY) ? "BUY" : "SELL";
                            string margin_info = "";
                            if(mode_name == "LAYER2_SL") {
                                double margin_usd = OrderLots() * MarketInfo(Symbol(), MODE_MARGINREQUIRED);
                                margin_info = " Margin=$" + DoubleToStr(margin_usd, 2);
                            }
                            Print(">> [CLOSE] ", short_mode, " TF=", tf_names[tf], " S=", (s+1),
                                  " | #", ticket, " ", order_type_str, " ", DoubleToStr(OrderLots(), 2),
                                  " | Loss=$", DoubleToStr(profit, 2),
                                  " | Threshold=$", DoubleToStr(sl_threshold, 2), margin_info, " <<");

                            if(CloseOrderSafely(ticket, mode_name)) {
                                g_ea.position_flags[tf][s] = 0;
                                order_closed = true;
                            }
                        }
                    }

                    // ===== SECTION 2: TAKE PROFIT (1 layer) =====
                    // Only check if order wasn't closed by stoploss | Chi kiem tra neu chua bi dong boi stoploss
                    if(!order_closed && UseTakeProfit) {
                        // Calculate TP threshold from max_loss | Tinh nguong TP tu max_loss
                        double max_loss_per_lot = MathAbs(g_ea.csdl_rows[tf].max_loss);
                        if(max_loss_per_lot < 1.0) {
                            max_loss_per_lot = MathAbs(MaxLoss_Fallback);  // 1000
                        }

                        double tp_threshold = (max_loss_per_lot * g_ea.lot_sizes[tf][s]) * TakeProfit_Multiplier;

                        // Check and close if profit exceeds threshold | Kiem tra va dong neu loi vuot nguong
                        if(profit >= tp_threshold) {
                            string order_type_str = (OrderType() == OP_BUY) ? "BUY" : "SELL";
                            Print(">> [CLOSE] TP TF=", tf_names[tf], " S=", (s+1),
                                  " | #", ticket, " ", order_type_str, " ", DoubleToStr(OrderLots(), 2),
                                  " | Profit=$", DoubleToStr(profit, 2),
                                  " | Threshold=$", DoubleToStr(tp_threshold, 2),
                                  " Mult=", DoubleToStr(TakeProfit_Multiplier, 2), " <<");

                            if(CloseOrderSafely(ticket, "TAKE_PROFIT")) {
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
//  PART 16: EMERGENCY (1 function) | KIEM TRA KHAN CAP
//=============================================================================

// Check emergency conditions (drawdown) - log only | Kiem tra dieu kien khan cap - chi ghi nhan
void CheckAllEmergencyConditions() {
    double equity = AccountEquity();
    double balance = AccountBalance();

    if(balance > 0) {
        double drawdown_percent = ((balance - equity) / balance) * 100;

        if(drawdown_percent > 25.0) {
            Print("[WARNING] Drawdown: ", DoubleToStr(drawdown_percent, 2), "%");
        }
    }
}

//=============================================================================
//  PART 17: HEALTH CHECK & RESET (4 functions) | KIEM TRA SUC KHOE VA RESET
//=============================================================================

// Smart TF reset for all charts of current symbol (learned from SPY Bot) | Reset thong minh cho tat ca chart cung symbol (hoc tu SPY Bot)
// Resets OTHER charts first, then CURRENT chart last (important for D1 SPY Bot recognition) | Reset cac chart KHAC truoc, chart HIEN TAI cuoi (quan trong cho SPY Bot nhan dien)
void SmartTFReset() {
    Print("=======================================================");
    Print("[SMART_TF_RESET] Resetting all charts of ", g_ea.symbol_name, "...");
    Print("=======================================================");

    string current_symbol = Symbol();
    int current_period = Period();
    long current_chart_id = ChartID();

    // Step 1: Find all OTHER charts of SAME symbol (not including current chart) | Tim tat ca chart KHAC cung symbol (khong bao gom chart hien tai)
    int total_charts = 0;
    long chart_ids[10];
    ArrayInitialize(chart_ids, 0);

    long temp_chart = ChartFirst();
    while(temp_chart >= 0) {
        // ONLY reset charts with SAME symbol (important for multi-symbol setup!) | CHI reset chart CUNG symbol (quan trong cho nhieu symbol!)
        if(ChartSymbol(temp_chart) == current_symbol && temp_chart != current_chart_id) {
            chart_ids[total_charts] = temp_chart;
            total_charts++;
        }
        temp_chart = ChartNext(temp_chart);
    }

    // Step 2: Reset OTHER charts FIRST (6 charts: M1/M5/M15/M30/H1/H4 or M5/M15/M30/H1/H4/D1) | Reset cac chart KHAC TRUOC
    for(int i = 0; i < total_charts; i++) {
        int other_period = ChartPeriod(chart_ids[i]);
        Print("[RESET] Step ", (i+1), "/", total_charts, ": Chart TF ", other_period, " (via W1)...");

        ChartSetSymbolPeriod(chart_ids[i], current_symbol, PERIOD_W1);
        Sleep(1000);
        ChartSetSymbolPeriod(chart_ids[i], current_symbol, other_period);
        Sleep(1000);
    }

    // Step 3: Reset CURRENT chart LAST (important: D1 chart with SPY Bot must be last!) | Reset chart HIEN TAI CUOI CUNG (quan trong: D1 co SPY Bot phai cuoi!)
    Print("[RESET] Step ", (total_charts+1), "/", (total_charts+1), ": Current chart TF ", current_period, " (LAST - via W1)...");
    ChartSetSymbolPeriod(current_chart_id, current_symbol, PERIOD_W1);
    Sleep(1000);
    ChartSetSymbolPeriod(current_chart_id, current_symbol, current_period);
    Sleep(1000);

    Print("[SMART_TF_RESET] ? Completed! ", (total_charts + 1), " charts reset");
    Print("=======================================================");
}

// Weekend reset (Saturday 00:03) - Trigger SmartTFReset | Reset cuoi tuan - Goi SmartTFReset
// ONLY M1 chart has permission to reset (master chart) | CHI chart M1 co quyen reset (chart master)
// Time: 00:03 to AVOID conflict with SPY Bot reset at 00:00 | Gio: 00:03 de TRANH xung dot voi SPY Bot reset luc 00:00
void CheckWeekendReset() {
    // Check if feature is enabled by user | Kiem tra tinh nang co duoc bat boi user
    if(!EnableWeekendReset) return;

    // ONLY M1 chart can trigger reset (to avoid conflict) | CHI chart M1 moi duoc trigger reset (tranh xung dot)
    if(Period() != PERIOD_M1) return;

    datetime current_time = TimeCurrent();
    int day_of_week = TimeDayOfWeek(current_time);
    int hour = TimeHour(current_time);
    int minute = TimeMinute(current_time);

    // Only on Saturday (6) at 0h:01 (minute 01 exactly) | Chi vao Thu 7 luc 0h:01 (phut 01 chinh xac)
    // IMPORTANT: NOT 0h:00 to avoid conflict with SPY Bot! | QUAN TRONG: KHONG 0h:00 de tranh xung dot voi SPY Bot!
    if(day_of_week != 6 || hour != 0 || minute != 3) return;

    // Prevent duplicate reset (once per day) | Tranh reset trung lap (1 lan moi ngay)
    int current_day = TimeDay(current_time);
    if(current_day == g_ea.weekend_last_day) return;  // Already reset today | Da reset hom nay roi

    Print("[WEEKEND_RESET] Saturday 00:03 - M1 chart triggering weekly reset...");
    Print("[WEEKEND_RESET] (Delayed 3 minute to avoid SPY Bot conflict at 00:00)");

    SmartTFReset();  // Call smart reset for all charts | Goi reset thong minh cho tat ca charts

    g_ea.weekend_last_day = current_day;
    Print("[WEEKEND_RESET] ? Weekly reset completed!");
}

// Health check SPY Bot (8h/16h only, NOT 24h) | Kiem tra suc khoe SPY Bot (chi 8h va 16h, KHONG 24h)
// ONLY M1 chart has permission to check and reset (master chart) | CHI chart M1 co quyen kiem tra va reset (chart master)
void CheckSPYBotHealth() {
    // Check if feature is enabled by user | Kiem tra tinh nang co duoc bat boi user
    if(!EnableHealthCheck) return;

    // ONLY M1 chart can check health (to avoid conflict) | CHI chart M1 moi duoc kiem tra (tranh xung dot)
    if(Period() != PERIOD_M1) return;

    datetime current_time = TimeCurrent();
    int hour = TimeHour(current_time);

    // Only check at 8h & 16h (NOT 24h - conflicts with weekend reset) | Chi kiem tra 8h va 16h (KHONG 24h - trung voi weekend reset)
    if(hour != 8 && hour != 16) return;

    // Prevent duplicate check (once per hour) | Tranh kiem tra trung lap (1 lan moi gio)
    if(hour == g_ea.health_last_check_hour) return;
    g_ea.health_last_check_hour = hour;

    // Get M1 timestamp from CSDL (already available) | Lay timestamp M1 tu CSDL (da co san)
    datetime m1_timestamp = g_ea.timestamp_old[0];

    // Calculate time difference | Tinh chenh lech thoi gian
    int diff_seconds = (int)(current_time - m1_timestamp);
    int diff_hours = diff_seconds / 3600;
    int diff_minutes = (diff_seconds % 3600) / 60;

    Print("[HEALTH_CHECK] Time: ", hour, "h00 | CSDL last update: ", diff_hours, "h", diff_minutes, "m ago");

    // If diff > 8 hours (28800 seconds) ? SPY Bot frozen! | Neu chenh lech > 8 gio ? SPY Bot treo!
    if(diff_seconds > 28800) {
        Print("[HEALTH_CHECK] ? SPY Bot FROZEN!");
        Print("[HEALTH_CHECK] Server time: ", TimeToStr(current_time, TIME_DATE|TIME_SECONDS));
        Print("[HEALTH_CHECK] Last CSDL update: ", TimeToStr(m1_timestamp, TIME_DATE|TIME_SECONDS));
        Print("[HEALTH_CHECK] M1 chart triggering Smart TF Reset...");

        Alert("?? SPY Bot frozen! Auto-reset all ", g_ea.symbol_name, " charts!");

        SmartTFReset();  // Call smart reset for all charts | Goi reset thong minh cho tat ca charts

        Print("[HEALTH_CHECK] ? Reset completed");

    } else {
        Print("[HEALTH_CHECK] ? SPY Bot OK - Recent activity detected");
    }
}

//=============================================================================
//  PART 18: MAIN EA FUNCTIONS (3 functions) | HAM CHINH CUA EA
//=============================================================================

// EA initialization - setup all components | Khoi tao EA - cai dat tat ca thanh phan
// OPTIMIZED V3.4: Struct-based data isolation for multi-symbol support | TOI UU: Cach ly du lieu theo struct cho da ky hieu
int OnInit() {
    // PART 1: Symbol recognition | Nhan dien ky hieu
    if(!InitializeSymbolRecognition()) return(INIT_FAILED);
    InitializeSymbolPrefix();

    // PART 2: Folder selection (only for local file mode) | Chon thu muc (chi cho che do file local)
    if(CSDL_Source == FOLDER_1) g_ea.csdl_folder = "DataAutoOner\\";
    else if(CSDL_Source == FOLDER_2) g_ea.csdl_folder = "DataAutoOner2\\";
    else if(CSDL_Source == FOLDER_3) g_ea.csdl_folder = "DataAutoOner3\\";
    else g_ea.csdl_folder = "DataAutoOner2\\";  // Fallback to FOLDER_2

    // PART 3: Build filename & Read file | Xay dung ten file va doc file
    BuildCSDLFilename();
    ReadCSDLFile();

    // PART 4: Generate magic numbers | Tao so hieu lenh
    if(!GenerateMagicNumbers()) return(INIT_FAILED);

    // PART 5: Pre-calculate all 21 lot sizes ONCE | Tinh truoc 21 khoi luong MOT LAN
    InitializeLotSizes();

    // PART 6: Initialize Layer1 thresholds (uses pre-calculated lots) | Khoi tao nguong cat lo (dung lot da tinh)
    InitializeLayer1Thresholds();

    // PART 7: Map CSDL variables (includes TREND/NEWS optimization) | Anh xa bien CSDL (bao gom toi uu TREND/NEWS)
    MapCSDLToEAVariables();

    // PART 7B: ?? CRITICAL FIX - Reset ALL auxiliary flags to prevent ZOMBIE variables | Dat lai TAT CA co phu tranh bien zombie
    // MQL4 does NOT auto-reset global variables on EA restart | MQL4 KHONG tu dong reset bien toan cuc khi EA khoi dong lai
    // If EA was killed (crash/user stop), old flag values may persist | Neu EA bi tat ngang, gia tri co cu co the con ton tai
    // This causes ZOMBIE orders: flag=1 but order doesn't exist, or TF disabled but flag still set | Gay lenh zombie: co=1 nhung lenh khong ton tai, hoac TF tat nhung co van = 1
    for(int tf = 0; tf < 7; tf++) {
        for(int s = 0; s < 3; s++) {
            g_ea.position_flags[tf][s] = 0;
        }
    }

    // Initialize global state vars (prevent multi-symbol conflicts) | Khoi tao bien trang thai (tranh xung dot da symbol)
    g_ea.first_run_completed = false;
    g_ea.weekend_last_day = -1;
    g_ea.health_last_check_hour = -1;
    g_ea.timer_last_run_time = 0;

    DebugPrint("[RESET] All position flags (21) & state vars reset to 0");

    // PART 8: Set BASELINE (only old) - FOR ALL 7 TF | Dat moc ban dau cho 7 khung
    for(int tf = 0; tf < 7; tf++) {
        g_ea.signal_old[tf] = g_ea.csdl_rows[tf].signal;
        g_ea.timestamp_old[tf] = (datetime)g_ea.csdl_rows[tf].timestamp;
    }

    // PART 8B: Build compact startup summary BEFORE RESTORE | Tao tom tat khoi dong TRUOC KHI RESTORE
    // This must be done BEFORE RestoreOrCleanupPositions() so it can print final summary | Phai lam TRUOC RestoreOrCleanupPositions() de in tom tat cuoi cung
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

    string sl_mode = (StoplossMode == LAYER1_MAXLOSS) ? "L1" : ("L2/" + DoubleToStr(Layer2_Divisor, 0));
    string master_mode = (Period()==PERIOD_M1) ? "M1" : "M5-D1";

    // CSDL source name | Ten nguon CSDL
    string folder_name = "";
    if(CSDL_Source == FOLDER_1) folder_name = "DA1";
    else if(CSDL_Source == FOLDER_2) folder_name = "DA2";
    else if(CSDL_Source == FOLDER_3) folder_name = "DA3";

    // Build init_summary with CSDL data (after MapCSDLToEAVariables) | Tao init_summary voi du lieu CSDL
    string trend_str = SignalToString(g_ea.trend_d1);
    string news_str = "Lv" + IntegerToString(g_ea.news_level) + "_" + SignalToString(g_ea.news_direction);

    g_ea.init_summary = "[INIT] " + g_ea.symbol_name + " | SL:" + sl_mode +
                        " News:STRONGEST(" + news_str + ") Trend:" + trend_str +
                        " | Lot:" + DoubleToStr(g_ea.lot_sizes[0][0], 2) + "-" + DoubleToStr(g_ea.lot_sizes[6][2], 2) +
                        " | TF:" + IntegerToString(tf_count) + " S:" + IntegerToString(strat_count) +
                        " | Folder:" + folder_name + " Master:" + master_mode +
                        " Magic:" + IntegerToString(g_ea.magic_numbers[0][0]) + "-" + IntegerToString(g_ea.magic_numbers[6][2]);

    // PART 9: Restore positions (will print init_summary) | Khoi phuc lenh (se in init_summary)
    RestoreOrCleanupPositions();

    // PART 10: Start timer | Bat timer
    if(!EventSetTimer(1)) return(INIT_FAILED);

    g_ea.first_run_completed = true;

    return(INIT_SUCCEEDED);
}

// EA deinitialization - cleanup | Ket thuc EA - don dep
void OnDeinit(const int reason) {
    EventKillTimer();
    Comment("");  // Clear Comment | Xoa Comment

    // Delete all dashboard labels (16 labels: dash_0 to dash_15) | Xoa tat ca label dashboard
    for(int i = 0; i <= 15; i++) {
        ObjectDelete("dash_" + IntegerToString(i));
    }

    Print("[EA] Shutdown. Reason: ", reason);
}

//=============================================================================
//  PART 19: DASHBOARD - OBJ_LABEL (4 functions) | BANG DIEU KHIEN OBJ_LABEL
//=============================================================================
// Leverages existing EA resources: g_ea struct, flags, lot sizes | Tan dung tai nguyen EA co san
// Uses OBJ_LABEL with fixed-width spaces + alternating colors (Blue/White) | Dung OBJ_LABEL voi khoang cach co dinh + 2 mau xen ke

// Scan all orders once for dashboard (reuse stoploss logic) | Quet lenh 1 lan cho dashboard (tai su dung logic stoploss)
// NEW: Builds 2 separate summaries - S1 only (row 1), S2+S3 (row 2) | Xay dung 2 tom tat rieng - Chi S1 (hang 1), S2+S3 (hang 2)
void ScanAllOrdersForDashboard(int &total_orders, double &total_profit, double &total_loss,
                                string &s1_summary, string &s2s3_summary) {
    total_orders = 0;
    total_profit = 0;
    total_loss = 0;
    s1_summary = "";
    s2s3_summary = "";

    string tf_names[7] = {"M1", "M5", "M15", "M30", "H1", "H4", "D1"};
    int s1_count = 0;
    int s2s3_count = 0;

    for(int i = 0; i < OrdersTotal(); i++) {
        if(!OrderSelect(i, SELECT_BY_POS, MODE_TRADES)) continue;
        if(OrderSymbol() != Symbol()) continue;

        int magic = OrderMagicNumber();
        double profit = OrderProfit() + OrderSwap() + OrderCommission();
        double margin_usd = OrderLots() * MarketInfo(Symbol(), MODE_MARGINREQUIRED);

        // Check which strategy this order belongs to | Kiem tra lenh thuoc chien luoc nao
        for(int tf = 0; tf < 7; tf++) {
            // S1 orders (row 1) | Lenh S1 (hang 1)
            if(magic == g_ea.magic_numbers[tf][0]) {
                total_orders++;
                if(profit > 0) total_profit += profit;
                else total_loss += profit;

                s1_count++;
                if(s1_count <= 7) {  // Max 7 (all TF) | Toi da 7 (tat ca TF)
                    if(s1_count > 1) s1_summary += ", ";
                    s1_summary += "S1_" + tf_names[tf] + "[$" + DoubleToStr(margin_usd, 0) + "]";
                }
                break;
            }
            // S2 + S3 orders (row 2) | Lenh S2 + S3 (hang 2)
            else if(magic == g_ea.magic_numbers[tf][1] || magic == g_ea.magic_numbers[tf][2]) {
                total_orders++;
                if(profit > 0) total_profit += profit;
                else total_loss += profit;

                s2s3_count++;
                if(s2s3_count <= 7) {  // Show first 7 | Chi hien 7 dau
                    string strategy = (magic == g_ea.magic_numbers[tf][1]) ? "S2" : "S3";
                    if(s2s3_count > 1) s2s3_summary += ", ";
                    s2s3_summary += strategy + "_" + tf_names[tf] + "[$" + DoubleToStr(margin_usd, 0) + "]";
                }
                break;
            }
        }
    }

    // Add "more" indicators | Them chi bao neu con nhieu
    if(s1_count > 7) s1_summary += " +" + IntegerToString(s1_count - 7) + " more";
    if(s2s3_count > 7) s2s3_summary += " +" + IntegerToString(s2s3_count - 7) + " more";
}

// Format age (time since signal) | Dinh dang tuoi (thoi gian tu tin hieu)
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

// Pad string to fixed width (right-pad with spaces) | Them khoang trang den do rong co dinh
string PadRight(string text, int width) {
    while(StringLen(text) < width) text += " ";
    if(StringLen(text) > width) text = StringSubstr(text, 0, width);
    return text;
}

// Main dashboard update with OBJ_LABEL (position ~200px from top) | Cap nhat dashboard voi OBJ_LABEL (vi tri 200px tu tren)
void UpdateDashboard() {
    // Check if dashboard is enabled | Kiem tra dashboard co bat khong
    if(!ShowDashboard) {
        // Hide all labels if disabled | An tat ca label neu tat
        for(int i = 0; i <= 15; i++) {
            ObjectDelete("dash_" + IntegerToString(i));
        }
        return;
    }

    string tf_names[7] = {"M1", "M5", "M15", "M30", "H1", "H4", "D1"};
    int y_start = 150;  // Start 150px from top | Bat dau tu 150px tu tren
    int line_height = 14;  // Line spacing | Khoang cach dong
    int y_pos = y_start;

    // ===== LEVERAGE: Account info | Tai su dung: Thong tin tai khoan
    double equity = AccountEquity();
    double balance = AccountBalance();
    double dd = (balance > 0) ? ((balance - equity) / balance) * 100 : 0;

    // ===== LEVERAGE: Scan orders ONCE (with 2 USD summaries) | Quet lenh MOT LAN (co 2 tom tat USD)
    int total_orders = 0;
    double total_profit = 0, total_loss = 0;
    string s1_summary = "", s2s3_summary = "";
    ScanAllOrdersForDashboard(total_orders, total_profit, total_loss, s1_summary, s2s3_summary);

    // ===== LEVERAGE: g_ea variables | Tai su dung: Bien g_ea
    string folder = "";
    if(CSDL_Source == FOLDER_1) folder = "DA1";
    else if(CSDL_Source == FOLDER_2) folder = "DA2";
    else if(CSDL_Source == FOLDER_3) folder = "DA3";
    string trend = (g_ea.trend_d1 == 1) ? "[^]" : (g_ea.trend_d1 == -1 ? "" : ">");
    string news_dir = (g_ea.news_direction == 1) ? "[^]" : (g_ea.news_direction == -1 ? "" : ">");

    // ===== LINE 0: HEADER (White) | TIEU DE (Trang)
    string header = "[" + g_ea.symbol_name + "] " + folder + " | 7TFx3S=21 | Trend:D1" + trend +
                    " News:Lv" + IntegerToString(g_ea.news_level) + news_dir +
                    " | Eq:$" + DoubleToStr(equity, 0) + " DD:" + DoubleToStr(dd, 1) + "%";
    CreateOrUpdateLabel("dash_0", header, 10, y_pos, clrWhite, 9);
    y_pos += line_height;

    // ===== LINE 1: SEPARATOR (White) | DUONG GACH (Trang)
    CreateOrUpdateLabel("dash_1", "-------------------------------------------------------------", 10, y_pos, clrWhite, 9);
    y_pos += line_height;

    // ===== LINE 2: COLUMN HEADERS (White) | TEN COT (Trang)
    string col_header = PadRight("TF", 4) + PadRight("Signal", 7) + PadRight("S1", 8) +
                        PadRight("S2", 8) + PadRight("S3", 8) + PadRight("Age", 6) +
                        PadRight("DPrice", 8) + "News";
    CreateOrUpdateLabel("dash_2", col_header, 10, y_pos, clrWhite, 9);
    y_pos += line_height;

    // ===== LINE 3: SEPARATOR (White) | DUONG GACH (Trang)
    CreateOrUpdateLabel("dash_3", "-------------------------------------------------------------", 10, y_pos, clrWhite, 9);
    y_pos += line_height;

    // ===== 7 ROWS - ALTERNATING COLORS + ASCII ARROWS | 7 HANG - 2 MAU + MUI TEN ASCII
    for(int tf = 0; tf < 7; tf++) {
        // Signal with ASCII arrows ([^] up, v down, - none) | Tin hieu voi mui ten ASCII
        int current_signal = g_ea.csdl_rows[tf].signal;
        string sig = "";
        if(current_signal == 1) sig = "[^]";      // UP arrow | Mui ten len
        else if(current_signal == -1) sig = " v "; // DOWN arrow | Mui ten xuong
        else sig = "-";                            // NONE | Khong co

        // S1/S2/S3
        string s1 = (g_ea.position_flags[tf][0] == 1) ? "*" + DoubleToStr(g_ea.lot_sizes[tf][0], 2) : "o";
        string s2 = (g_ea.position_flags[tf][1] == 1) ? "*" + DoubleToStr(g_ea.lot_sizes[tf][1], 2) : "o";
        string s3 = (g_ea.position_flags[tf][2] == 1) ? "*" + DoubleToStr(g_ea.lot_sizes[tf][2], 2) : "o";

        // Age
        string age = FormatAge((datetime)g_ea.csdl_rows[tf].timestamp);

        // DPrice
        string dp = DoubleToStr(g_ea.csdl_rows[tf].pricediff, 1);
        if(g_ea.csdl_rows[tf].pricediff > 0) dp = "+" + dp;

        // News
        string nw = IntegerToString(g_ea.csdl_rows[tf].news);
        if(g_ea.csdl_rows[tf].news > 0) nw = "+" + nw;

        // Build row with fixed-width columns | Xay dung dong voi cot co dinh
        string row = PadRight(tf_names[tf], 4) + PadRight(sig, 7) + PadRight(s1, 8) +
                     PadRight(s2, 8) + PadRight(s3, 8) + PadRight(age, 6) +
                     PadRight(dp, 8) + nw;

        // Alternating colors: Blue (even rows), White (odd rows) | Mau xen ke: Xanh (dong chan), Trang (dong le)
        color row_color = (tf % 2 == 0) ? clrDodgerBlue : clrWhite;
        CreateOrUpdateLabel("dash_" + IntegerToString(4 + tf), row, 10, y_pos, row_color, 9);
        y_pos += line_height;
    }

    // ===== LINE 11: SEPARATOR (White) | DUONG GACH (Trang)
    CreateOrUpdateLabel("dash_11", "-------------------------------------------------------------", 10, y_pos, clrWhite, 9);
    y_pos += line_height;

    // ===== LINE 12: P&L SUMMARY (White) | TOM TAT LAI LO (Trang)
    double net = total_profit + total_loss;
    string footer = "Orders:" + IntegerToString(total_orders) + "/21 | Net:$" + DoubleToStr(net, 2) +
                    " | Profit:+$" + DoubleToStr(total_profit, 2) +
                    " Loss:$" + DoubleToStr(total_loss, 2) + " | 2s";
    CreateOrUpdateLabel("dash_12", footer, 10, y_pos, clrWhite, 9);
    y_pos += line_height;

    // ===== LINE 13: S1 ORDERS USD (Yellow) | LENH S1 USD (Vang)
    string s1_line = "S1 Orders: ";
    if(s1_summary == "") s1_line += "None";
    else s1_line += s1_summary;
    CreateOrUpdateLabel("dash_13", s1_line, 10, y_pos, clrYellow, 9);
    y_pos += line_height;

    // ===== LINE 14: S2+S3 ORDERS USD (Yellow) | LENH S2+S3 USD (Vang)
    string s2s3_line = "S2+S3 Orders: ";
    if(s2s3_summary == "") s2s3_line += "None";
    else s2s3_line += s2s3_summary;
    CreateOrUpdateLabel("dash_14", s2s3_line, 10, y_pos, clrYellow, 9);
    y_pos += line_height;

    // ===== LINE 15: BROKER + SERVER + LEVERAGE (Yellow) | THONG TIN SAN + MAY CHU + DON BAY (Vang)
    string broker = AccountCompany();
    string server = AccountServer();
    int leverage = AccountLeverage();
    string broker_info = broker + " | Server:" + server + " | Leverage:1:" + IntegerToString(leverage);
    CreateOrUpdateLabel("dash_15", broker_info, 10, y_pos, clrYellow, 8);
}

// Create or update OBJ_LABEL | Tao hoac cap nhat OBJ_LABEL
void CreateOrUpdateLabel(string name, string text, int x, int y, color clr, int font_size) {
    if(ObjectFind(name) < 0) {
        ObjectCreate(name, OBJ_LABEL, 0, 0, 0);
        ObjectSet(name, OBJPROP_CORNER, CORNER_LEFT_UPPER);
        ObjectSet(name, OBJPROP_XDISTANCE, x);
        ObjectSet(name, OBJPROP_YDISTANCE, y);
    }
    ObjectSetText(name, text, font_size, "Courier New", clr);
}

// Timer event - main trading loop (1 second) | Su kien timer - vong lap giao dich chinh (1 giay)
// OPTIMIZED V4.0: Split into 2 groups (EVEN/ODD) for better performance | TOI UU: Chia 2 nhom (CHAN/LE) de tang hieu suat
// GROUP 1 (EVEN): Trading core - Read CSDL + Process signals | Nhom 1 (CHAN): Giao dich chinh - Doc CSDL + Xu ly tin hieu
// GROUP 2 (ODD): Auxiliary - Stoploss + Dashboard + Health checks | Nhom 2 (LE): Phu tro - Cat lo + Bang dieu khien + Kiem tra suc khoe
void OnTimer() {
    datetime current_time = TimeCurrent();
    int current_second = TimeSeconds(current_time);

    // Prevent duplicate execution in same second | Tranh chay trung trong cung 1 giay
    if(current_time == g_ea.timer_last_run_time) return;
    g_ea.timer_last_run_time = current_time;

    //=============================================================================
    // GROUP 1: EVEN SECONDS (0,2,4,6...) - TRADING CORE (HIGH PRIORITY)
    // NHOM 1: GIAY CHAN - GIAO DICH CHINH (UU TIEN CAO)
    //=============================================================================
    // WHY EVEN: SPY Bot writes CSDL on ODD seconds ? EA reads on EVEN ? No file lock conflict
    // TAI SAO CHAN: SPY Bot ghi CSDL giay LE ? EA doc giay CHAN ? Khong xung dot file
    if(!UseEvenOddMode || (current_second % 2 == 0)) {

        // STEP 1: Read CSDL file | Doc file CSDL
        ReadCSDLFile();

        // STEP 2: Map data for all 7 TF | Anh xa du lieu cho 7 khung
        MapCSDLToEAVariables();

        // STEP 2.5: Close Bonus orders if M1 signal changed | Dong lenh Bonus neu M1 doi tin hieu
        if(EnableBonusNews && HasValidS2BaseCondition(0)) {
            CloseAllBonusOrders();
        }

        // STEP 3: Strategy processing loop for 7 TF | Vong lap xu ly chien luoc cho 7 khung
        // IMPORTANT: CLOSE function runs on ALL 7 TF (no TF filter) | QUAN TRONG: Ham dong chay TAT CA 7 TF (khong loc TF)
        // OPEN function respects TF/Strategy toggles | Ham mo tuan theo bat/tat TF/Chien luoc
        for(int tf = 0; tf < 7; tf++) {
            if(HasValidS2BaseCondition(tf)) {

                // Close old orders for this TF (ALL 3 strategies) | Dong lenh cu cua TF (TAT CA 3 chien luoc)
                CloseAllStrategiesByMagicForTF(tf);

                // Open new orders (ONLY if TF enabled) | Mo lenh moi (CHI neu TF bat)
                if(IsTFEnabled(tf)) {
                    if(S1_HOME) ProcessS1Strategy(tf);
                    if(S2_TREND) ProcessS2Strategy(tf);
                    if(S3_NEWS) ProcessS3Strategy(tf);
                }

                // Update baseline from CSDL | Cap nhat moc tu CSDL
                g_ea.signal_old[tf] = g_ea.csdl_rows[tf].signal;
                g_ea.timestamp_old[tf] = (datetime)g_ea.csdl_rows[tf].timestamp;
            }
        }

        // STEP 4: Process Bonus NEWS (scan all 7 TF) | Xu ly Bonus tin tuc (quet 7 TF)
        ProcessBonusNews();
    }

    //=============================================================================
    // GROUP 2: ODD SECONDS (1,3,5,7...) - AUXILIARY (SUPPORT)
    // NHOM 2: GIAY LE - PHU TRO (HO TRO)
    //=============================================================================
    // WHY ODD: These functions don't need fresh CSDL data ? Run independently ? Reduce load on EVEN seconds
    // TAI SAO LE: Cac ham nay khong can CSDL moi ? Chay doc lap ? Giam tai cho giay CHAN
    // NOTE: Always runs on ODD seconds, independent of UseEvenOddMode | Luon chay giay LE, doc lap voi UseEvenOddMode
    if(current_second % 2 != 0) {

        // STEP 1: Check stoploss & take profit | Kiem tra cat lo & chot loi
        CheckStoplossAndTakeProfit();

        // STEP 2: Update dashboard | Cap nhat bang dieu khien
        UpdateDashboard();

        // STEP 3: Emergency check | Kiem tra khan cap
        CheckAllEmergencyConditions();

        // STEP 4: Weekend reset check (M1 only) | Kiem tra reset cuoi tuan (chi M1)
        CheckWeekendReset();

        // STEP 5: Health check at 8h/16h (M1 only) | Kiem tra suc khoe luc 8h/16h (chi M1)
        CheckSPYBotHealth();
    }
}
