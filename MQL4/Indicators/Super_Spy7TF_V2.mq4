//+-----------------------------------------------------------------------------------+
//  SUPER SPY BOT V2 - Multi-Timeframe Signal Monitor | BOT GIAM SAT TIN HIEU NHIEU KHUNG THOI GIAN V2
//+-----------------------------------------------------------------------------------+
#property copyright "SUPER_Spy7TF_Oner V2 - Multi-Timeframe Signal Spy with NEWS CASCADE Analysis"

#property link      "CSDL1: 8 Columns + CSDL3: 2 Strategies Only"
#property strict

#property indicator_chart_window  // Display on main chart | Hien thi tren bieu do chinh
#property indicator_buffers 0     // No indicator buffers needed | Khong can buffer chi bao

// Import WinAPI for timeframe switching | Import WinAPI de chuyen timeframe
#import "user32.dll"
   int PostMessageA(long hWnd, int Msg, int wParam, int lParam);
#import

#define WM_COMMAND 0x0111  // Windows message command constant | Hang so lenh tin nhan Windows

//==============================================================================
//  SECTION 1: USER INPUTS - ALL SWITCHES IN ONE PLACE | TAT CA CAC NUT BAT TAT O 1 CHO
//==============================================================================
input int    Timer = 1;                                      // Timer Interval in seconds (1-60) | Khoang thoi gian timer (1-60 giay)
input int    Retry = 3;                                      // Retry Attempts per round (1-10) | So lan thu lai moi vong (1-10)
input string TargetSymbol = "";                              // Target Symbol - Empty = current chart | Symbol muc tieu - Rong = chart hien tai
input bool   EnableHealthCheck = true;                       // Health check at 8h & 16h | Kiem tra suc khoe luc 8h va 16h
input bool   EnableMidnightReset = true;                     // Midnight reset at 0h daily | Reset luc 0h hang ngay
input bool   ProcessSignalOnOddSecond = true;                // Process Signal on ODD second only | Xu ly tin hieu giay le (tranh conflict)
input bool   EnableMonthlyStats = true;                      // Monthly stats on 1st day of month | Thong ke thang vao ngay 1
input string DataFolder = "DataAutoOner\\";                  // Data Storage Folder | Thu muc luu tru du lieu

//==============================================================================
//  SECTION 2: DATA STRUCTURES (3 structs) | PHAN 2: CAU TRUC DU LIEU
//==============================================================================
// Core data structures for signal tracking and history management
// Cau truc du lieu chinh de theo doi tin hieu va quan ly lich su
//==============================================================================

// History entry structure | Cau truc muc lich su
struct SignalHistoryEntry {
    string timeframe_name;           // Timeframe name (M1,M5,M15,M30,H1,H4,D1) | Ten khung thoi gian
    int signal_3col;                 // Signal value: 1=BUY, -1=SELL | Gia tri tin hieu
    double price_4col;               // Entry price | Gia vao lenh
    long cross_5col;                 // Cross reference (timestamp of previous TF) | Tham chieu cheo timestamp TF truoc
    long timestamp_6col;             // Signal timestamp | Dau thoi gian tin hieu
    double pricediff_7col;           // Price difference in USD | Chenh lech gia theo USD
    int timediff_8col;               // Time difference in minutes | Chenh lech thoi gian theo phut
    int news_result_9col;            // NEWS CASCADE result (±11-16 or 0) | Ket qua NEWS CASCADE
};

#define HISTORY_SIZE 7               // 7 signals per timeframe | 7 tin hieu moi khung thoi gian

// ============================================================================
// MAIN DATA STRUCTURE: SymbolCSDL1Data | CAU TRUC DU LIEU CHINH
// ============================================================================
// Contains ALL data for 1 symbol (current chart) | Chua tat ca du lieu cho 1 symbol
// - 7 TF × 10 columns (CSDL1 current data) | 7 khung thoi gian x 10 cot du lieu hien tai
// - 7 TF × 7 history entries | 7 khung thoi gian x 7 muc lich su
// - Counters, timestamps, etc. | Bo dem, dau thoi gian, v.v.
// ============================================================================

struct SymbolCSDL1Data {
    // Symbol identification | Nhan dien symbol
    string symbol;                    // Current chart symbol | Symbol bieu do hien tai

    // ==================================================
    // CSDL1 CURRENT DATA - 7 TF × 10 COLUMNS | DU LIEU HIEN TAI
    // ==================================================
    // Row index: 0=M1, 1=M5, 2=M15, 3=M30, 4=H1, 5=H4, 6=D1 | Chi so hang

    int signals[7];                   // Column 3: Signal (-1, 0, 1) | Cot 3: Tin hieu
    double prices[7];                 // Column 4: Price | Cot 4: Gia
    long crosses[7];                  // Column 5: Cross (timestamp of prev TF) | Cot 5: Tham chieu cheo
    long timestamps[7];               // Column 6: Timestamp | Cot 6: Dau thoi gian
    double pricediffs[7];             // Column 7: PriceDiff USD | Cot 7: Chenh lech gia USD
    int timediffs[7];                 // Column 8: TimeDiff minutes | Cot 8: Chenh lech thoi gian phut
    int news_results[7];              // Column 9: NEWS CASCADE (±11-16 or 0) | Cot 9: Ket qua NEWS CASCADE
    double max_losses[7];             // Column 10: Max Loss (negative value) | Cot 10: Lo toi da

    // ==================================================
    // LAST SIGNAL TRACKING (for PriceDiff calculation) | THEO DOI TIN HIEU TRUOC
    // ==================================================
    int signals_last[7];              // Previous signal | Tin hieu truoc
    double prices_last[7];            // Previous price | Gia truoc
    long timestamps_last[7];          // Previous timestamp | Dau thoi gian truoc
    long processed_timestamps[7];     // Last processed timestamp (avoid duplicate) | Timestamp da xu ly

    // ==================================================
    // HISTORY ARRAYS - 7 TF × 7 ENTRIES | MANG LICH SU
    // ==================================================
    SignalHistoryEntry m1_history[HISTORY_SIZE];   // M1 history buffer | Bo dem lich su M1
    SignalHistoryEntry m5_history[HISTORY_SIZE];   // M5 history buffer | Bo dem lich su M5
    SignalHistoryEntry m15_history[HISTORY_SIZE];  // M15 history buffer | Bo dem lich su M15
    SignalHistoryEntry m30_history[HISTORY_SIZE];  // M30 history buffer | Bo dem lich su M30
    SignalHistoryEntry h1_history[HISTORY_SIZE];   // H1 history buffer | Bo dem lich su H1
    SignalHistoryEntry h4_history[HISTORY_SIZE];   // H4 history buffer | Bo dem lich su H4
    SignalHistoryEntry d1_history[HISTORY_SIZE];   // D1 history buffer | Bo dem lich su D1

    // History counters | Bo dem lich su
    int m1_count;   // M1 history count | So luong lich su M1
    int m5_count;   // M5 history count | So luong lich su M5
    int m15_count;  // M15 history count | So luong lich su M15
    int m30_count;  // M30 history count | So luong lich su M30
    int h1_count;   // H1 history count | So luong lich su H1
    int h4_count;   // H4 history count | So luong lich su H4
    int d1_count;   // D1 history count | So luong lich su D1

    // ==================================================
    // METADATA | DU LIEU META
    // ==================================================
    long last_file_modified;          // File modification timestamp | Dau thoi gian sua doi file
    int files_written;                // Write counter | Bo dem ghi file
};

// ============================================================================
// GLOBAL DATA - SINGLE STRUCT FOR CURRENT CHART | DU LIEU TOAN CAU
// ============================================================================
SymbolCSDL1Data g_symbol_data;  // Data for current chart symbol only | Du lieu cho symbol hien tai

//==============================================================================
//  SECTION 3: GLOBAL STATE VARIABLES (2 variables) | PHAN 3: BIEN TRANG THAI TOAN CAU
//==============================================================================

// NEWS Strategy Global State Variables | Bien trang thai toan cau chien luoc NEWS
int g_news_active_level = 0;       // Active NEWS cascade level (0-6) | Cap do NEWS cascade dang hoat dong
int g_news_active_direction = 0;   // Active NEWS direction (1=BUY,-1=SELL) | Huong NEWS dang hoat dong

//==============================================================================
//  SECTION 4: CONSTANTS & ANALYSIS STRUCTURES | PHAN 4: HANG SO VA CAU TRUC PHAN TICH
//==============================================================================

//--- Strategy result constants | Hang so ket qua chien luoc
#define STRATEGY_BEARISH    -1  // Bearish signal | Tin hieu giam
#define STRATEGY_NEUTRAL     0  // Neutral signal | Tin hieu trung lap
#define STRATEGY_BULLISH     1  // Bullish signal | Tin hieu tang

//--- NEWS Impact Levels (0-4 scale) | Cap do tac dong NEWS
#define NEWS_NONE           0    // No significant news impact | Khong co tac dong tin tuc
#define NEWS_WEAK           1    // Minor news impact | Tac dong tin tuc nho
#define NEWS_MEDIUM         2    // Moderate news impact | Tac dong tin tuc trung binh
#define NEWS_STRONG         3    // Strong news impact | Tac dong tin tuc manh
#define NEWS_EXTREME        4    // Extremely strong news impact | Tac dong tin tuc rat manh

//--- Analysis Input Structure | Cau truc input phan tich
struct AnalysisInput {
    int signal;        // Direction: 1=BUY, -1=SELL | Huong giao dich
    double price;      // Price to analyze | Gia phan tich
    long timestamp;    // Time of analysis | Thoi gian phan tich
    double usd_diff;   // USD value difference from entry | Chenh lech gia tri USD tu entry
};

//==============================================================================
//  SECTION 5: CORE DATA FUNCTIONS (7 functions) | PHAN 5: HAM XU LY DU LIEU CHINH
//==============================================================================

// Initialize symbol data structure to default values | Khoi tao cau truc du lieu symbol ve gia tri mac dinh
void InitSymbolData(string symbol) {
    g_symbol_data.symbol = symbol;

    // =========================================================================
    // CH? RESET BI?N PH? - KHÔNG ??NG VÀO 10 C?T CSDL1!
    // 10 c?t CSDL1 (signals, prices, crosses, timestamps, pricediffs, timediffs,
    // news_results, max_losses) s? ???c LOAD t? file, KHÔNG gán =0!
    // Bot WT t?o tín hi?u TH?C 24/7 ? SPY ch? LOAD, không can thi?p!
    // =========================================================================
    for(int i = 0; i < 7; i++) {
        // Bi?n PH? ?? tính toán (signals_last, prices_last, timestamps_last)
        g_symbol_data.signals_last[i] = 0;
        g_symbol_data.prices_last[i] = 0.0;
        g_symbol_data.timestamps_last[i] = 0;
        g_symbol_data.processed_timestamps[i] = 0;
    }

    // Zero history arrays
    for(int i = 0; i < HISTORY_SIZE; i++) {
        g_symbol_data.m1_history[i].signal_3col = 0;
        g_symbol_data.m5_history[i].signal_3col = 0;
        g_symbol_data.m15_history[i].signal_3col = 0;
        g_symbol_data.m30_history[i].signal_3col = 0;
        g_symbol_data.h1_history[i].signal_3col = 0;
        g_symbol_data.h4_history[i].signal_3col = 0;
        g_symbol_data.d1_history[i].signal_3col = 0;
    }

    // Zero counters
    g_symbol_data.m1_count = 0;
    g_symbol_data.m5_count = 0;
    g_symbol_data.m15_count = 0;
    g_symbol_data.m30_count = 0;
    g_symbol_data.h1_count = 0;
    g_symbol_data.h4_count = 0;
    g_symbol_data.d1_count = 0;

    // Reset metadata
    g_symbol_data.last_file_modified = 0;
    g_symbol_data.files_written = 0;

    // Print suppressed - OnInit will print summary
}

// Load CSDL1 JSON file data into memory structure | Doc du lieu file JSON CSDL1 vao cau truc bo nho
bool LoadCSDL1FileIntoArray() {
    string symbol = g_symbol_data.symbol;
    string json_file_path = DataFolder + symbol + ".json";

    // Read file using existing function
    string rows[];
    ArrayResize(rows, MAINDB_ROWS + 1);

    if(!FileIsExist(json_file_path)) {
        // Print suppressed - OnInit will print summary
        return false;  // File doesn't exist yet
    }

    if(!ReadJsonToRows(json_file_path, rows)) {
        Print("ERROR: LoadCSDL1 - Failed to read: ", json_file_path);
        return false;
    }

    // Parse rows into struct
    for(int row = 1; row <= MAINDB_ROWS; row++) {
        int tf_idx = row - 1;  // 0=M1, 1=M5, ..., 6=D1

        if(rows[row] == "" || StringLen(rows[row]) < 5) continue;

        // Split comma-separated row
        string cols[];
        int col_count = StringSplit(rows[row], ',', cols);

        if(col_count >= 8) {
            // =========================================================================
            // LOAD 10 C?T TR?C TI?P T? FILE (GIÁ TR? TH?C T? BOT WT)
            // KHÔNG gán =0, KHÔNG can thi?p, load gì thì dùng ?ó!
            // C?p signal + timestamp LUÔN ?I ?ÔI, t? nhiên t? WT
            // =========================================================================
            g_symbol_data.signals[tf_idx] = (int)StringToInteger(cols[2]);       // Col 3
            g_symbol_data.prices[tf_idx] = StringToDouble(cols[3]);             // Col 4
            g_symbol_data.crosses[tf_idx] = (long)StringToInteger(cols[4]);      // Col 5
            g_symbol_data.timestamps[tf_idx] = (long)StringToInteger(cols[5]);   // Col 6
            g_symbol_data.pricediffs[tf_idx] = StringToDouble(cols[6]);         // Col 7
            g_symbol_data.timediffs[tf_idx] = (int)StringToInteger(cols[7]);     // Col 8

            if(col_count >= 9) {
                g_symbol_data.news_results[tf_idx] = (int)StringToInteger(cols[8]); // Col 9
            }

            if(col_count >= 10) {
                g_symbol_data.max_losses[tf_idx] = StringToDouble(cols[9]);      // Col 10
            }

            // Mark timestamp as processed (tránh x? lý l?i tín hi?u c? t? file)
            // KHÔNG gán signals_last - ?? =0 (ch?a có signal tr??c)
            if(g_symbol_data.timestamps[tf_idx] > 0) {
                g_symbol_data.processed_timestamps[tf_idx] = g_symbol_data.timestamps[tf_idx];
            }
        }
    }

    // Load history arrays (7 TF × 7 entries) from "history" section
    LoadHistoryFromCSDL1(json_file_path);

    // Print suppressed - OnInit will print summary
    return true;
}

// Load history arrays from CSDL1 JSON file | Tai lich su tu file JSON CSDL1
bool LoadHistoryFromCSDL1(string json_file_path) {
    string json_content;
    if(!ReadFileWithRetry(json_file_path, json_content)) {
        return false;
    }

    // Find history_count section
    int history_count_start = StringFind(json_content, "\"history_count\":");
    if(history_count_start >= 0) {
        g_symbol_data.m1_count = ExtractJsonInt(json_content, "m1");
        g_symbol_data.m5_count = ExtractJsonInt(json_content, "m5");
        g_symbol_data.m15_count = ExtractJsonInt(json_content, "m15");
        g_symbol_data.m30_count = ExtractJsonInt(json_content, "m30");
        g_symbol_data.h1_count = ExtractJsonInt(json_content, "h1");
        g_symbol_data.h4_count = ExtractJsonInt(json_content, "h4");
        g_symbol_data.d1_count = ExtractJsonInt(json_content, "d1");
    }

    // Find history section
    int history_start = StringFind(json_content, "\"history\":");
    if(history_start < 0) return false;

    // Load M1 history
    LoadTimeframeHistory(json_content, "m1", g_symbol_data.m1_history, g_symbol_data.m1_count);
    LoadTimeframeHistory(json_content, "m5", g_symbol_data.m5_history, g_symbol_data.m5_count);
    LoadTimeframeHistory(json_content, "m15", g_symbol_data.m15_history, g_symbol_data.m15_count);
    LoadTimeframeHistory(json_content, "m30", g_symbol_data.m30_history, g_symbol_data.m30_count);
    LoadTimeframeHistory(json_content, "h1", g_symbol_data.h1_history, g_symbol_data.h1_count);
    LoadTimeframeHistory(json_content, "h4", g_symbol_data.h4_history, g_symbol_data.h4_count);
    LoadTimeframeHistory(json_content, "d1", g_symbol_data.d1_history, g_symbol_data.d1_count);

    return true;
}

// Load history for specific timeframe | Tai lich su cho khung thoi gian cu the
void LoadTimeframeHistory(string json_content, string tf_key, SignalHistoryEntry& history[], int count) {
    if(count <= 0 || count > 7) return;  // Safety check

    // Find timeframe section: "m1": [
    string search_pattern = "\"" + tf_key + "\": [";
    int tf_start = StringFind(json_content, search_pattern);
    if(tf_start < 0) return;

    int array_start = tf_start + StringLen(search_pattern);

    // Find closing bracket for this timeframe array
    int bracket_count = 1;
    int array_end = array_start;
    for(int i = array_start; i < StringLen(json_content); i++) {
        ushort ch = StringGetCharacter(json_content, i);
        if(ch == '[') bracket_count++;
        if(ch == ']') {
            bracket_count--;
            if(bracket_count == 0) {
                array_end = i;
                break;
            }
        }
    }

    if(array_end <= array_start) return;

    string array_content = StringSubstr(json_content, array_start, array_end - array_start);

    // Split by objects (each object ends with })
    string objects[];
    int obj_count = StringSplit(array_content, '}', objects);

    // Load each history entry
    for(int i = 0; i < obj_count && i < count && i < 7; i++) {
        string obj = objects[i];
        StringReplace(obj, "{", "");
        StringReplace(obj, "\"", "");
        StringReplace(obj, "\n", "");
        StringReplace(obj, " ", "");

        // Extract 8 fields from JSON object
        history[i].timeframe_name = ExtractHistoryValue(obj, "timeframe");
        history[i].signal_3col = (int)StringToInteger(ExtractHistoryValue(obj, "signal"));
        history[i].price_4col = StringToDouble(ExtractHistoryValue(obj, "price"));
        history[i].cross_5col = (long)StringToInteger(ExtractHistoryValue(obj, "cross"));
        history[i].timestamp_6col = (long)StringToInteger(ExtractHistoryValue(obj, "timestamp"));
        history[i].pricediff_7col = StringToDouble(ExtractHistoryValue(obj, "pricediff"));
        history[i].timediff_8col = (int)StringToInteger(ExtractHistoryValue(obj, "timediff"));
        history[i].news_result_9col = (int)StringToInteger(ExtractHistoryValue(obj, "news"));
    }
}

// Extract value from history JSON object | Trich xuat gia tri tu doi tuong JSON lich su
string ExtractHistoryValue(string obj, string key) {
    int key_pos = StringFind(obj, key + ":");
    if(key_pos < 0) return "";

    int value_start = key_pos + StringLen(key) + 1;
    int value_end = StringFind(obj, ",", value_start);
    if(value_end < 0) value_end = StringLen(obj);

    string value = StringSubstr(obj, value_start, value_end - value_start);
    StringTrimLeft(value);
    StringTrimRight(value);

    return value;
}

// Write CSDL1 data from memory to JSON file | Ghi du lieu CSDL1 tu bo nho ra file JSON
bool WriteCSDL1ArrayToFile() {
    string symbol = g_symbol_data.symbol;
    string json_file_path = DataFolder + symbol + ".json";

    // Build rows array
    string rows[];
    ArrayResize(rows, MAINDB_ROWS + 1);

    int timeframe_periods[7] = {1, 5, 15, 30, 60, 240, 1440};

    for(int tf_idx = 0; tf_idx < 7; tf_idx++) {
        int row = tf_idx + 1;  // row 1-7

        // Build comma-separated row (10 columns)
        rows[row] = "0," +  // Column 0: Placeholder
                    IntegerToString(timeframe_periods[tf_idx]) + "," +  // Column 1: TF period
                    IntegerToString(g_symbol_data.signals[tf_idx]) + "," +  // Column 2: Signal
                    DoubleToString(g_symbol_data.prices[tf_idx], 5) + "," +  // Column 3: Price
                    IntegerToString(g_symbol_data.crosses[tf_idx]) + "," +  // Column 4: Cross
                    IntegerToString(g_symbol_data.timestamps[tf_idx]) + "," +  // Column 5: Timestamp
                    DoubleToString(g_symbol_data.pricediffs[tf_idx], 2) + "," +  // Column 6: PriceDiff
                    IntegerToString(g_symbol_data.timediffs[tf_idx]) + "," +  // Column 7: TimeDiff
                    IntegerToString(g_symbol_data.news_results[tf_idx]) + "," +  // Column 9: NEWS
                    DoubleToString(g_symbol_data.max_losses[tf_idx], 2);  // Column 10: MaxLoss
    }

    // =========================================================================
    // FILE A: DataAutoOner/SYMBOL.json - WRITE IMMEDIATELY
    // =========================================================================
    if(!WriteRowsToJson(json_file_path, rows)) {
        Print("ERROR: WriteCSDL1 - Failed: ", json_file_path);
        return false;
    }

    // =========================================================================
    // FILE C: DataAutoOner3/SYMBOL.json - WRITE IMMEDIATELY (NEW!)
    // =========================================================================
    string json_file_path_C = "DataAutoOner3\\" + symbol + ".json";
    if(!WriteRowsToJson(json_file_path_C, rows)) {
        Print("ERROR: WriteCSDL1 - Failed to write to C: ", json_file_path_C);
        // Don't return false - A is already written successfully
    }

    g_symbol_data.files_written++;
    // Print suppressed - ProcessSignalForTF will print summary
    return true;
}

// Calculate maximum loss per standard lot based on symbol type | Tinh lo toi da moi lot chuan dua tren loai symbol
double CalculateMaxLoss() {
    string symbol_upper = g_symbol_data.symbol;
    StringToUpper(symbol_upper);

    double balance = AccountBalance();
    double risk_percent = 1.0 / 25.0;  // M?c ??nh: 4% (1/25)

    // CRYPTO - Volatility cao -> Risk th?p h?n
    if(StringFind(symbol_upper, "BTC") >= 0) {
        risk_percent = 1.0 / 50.0;  // 2.0%
    }
    else if(StringFind(symbol_upper, "ETH") >= 0) {
        risk_percent = 1.0 / 45.0;  // 2.22%
    }
    else if(StringFind(symbol_upper, "LTC") >= 0 ||
            StringFind(symbol_upper, "BNB") >= 0 ||
            StringFind(symbol_upper, "SOL") >= 0 ||
            StringFind(symbol_upper, "ADA") >= 0 ||
            StringFind(symbol_upper, "XRP") >= 0) {
        risk_percent = 1.0 / 40.0;  // 2.5%
    }
    // GOLD - Volatility trung bình
    else if(StringFind(symbol_upper, "XAU") >= 0) {
        risk_percent = 1.0 / 25.0;  // 4%
    }
    // SILVER - Volatility cao
    else if(StringFind(symbol_upper, "XAG") >= 0) {
        risk_percent = 1.0 / 40.0;  // 2.5%
    }
    // FOREX - Volatility th?p -> Risk cao h?n
    else {
        string currencies[] = {"EUR", "GBP", "USD", "JPY", "AUD", "NZD", "CHF", "CAD"};
        for(int i = 0; i < ArraySize(currencies); i++) {
            if(StringFind(symbol_upper, currencies[i]) >= 0) {
                risk_percent = 1.0 / 30.0;  // 3.33%
                break;
            }
        }
    }

    // TÍNH MAX LOSS CHO 1 LOT (CHU?N)
    double max_loss_per_lot = balance * risk_percent;

    return -max_loss_per_lot;  // Return negative value | Tra ve gia tri am
}

// Write CSDL2 LIVE data to 3 folders (no history) | Ghi du lieu CSDL2 LIVE ra 3 thu muc (khong co lich su)
bool WriteCSDL2ArrayToFile() {
    string symbol = g_symbol_data.symbol;

    // Build JSON array content (7 TF × 6 columns)
    string json_content = "[\n";

    for(int tf_idx = 0; tf_idx < 7; tf_idx++) {
        if(tf_idx > 0) json_content += ",\n";

        json_content += "  {";
        json_content += "\"max_loss\":" + DoubleToString(g_symbol_data.max_losses[tf_idx], 2) + ",";
        json_content += "\"timestamp\":" + IntegerToString(g_symbol_data.timestamps[tf_idx]) + ",";
        json_content += "\"signal\":" + IntegerToString(g_symbol_data.signals[tf_idx]) + ",";
        json_content += "\"pricediff\":" + DoubleToString(g_symbol_data.pricediffs[tf_idx], 2) + ",";
        json_content += "\"timediff\":" + IntegerToString(g_symbol_data.timediffs[tf_idx]) + ",";
        json_content += "\"news\":" + IntegerToString(g_symbol_data.news_results[tf_idx]);
        json_content += "}";
    }

    json_content += "\n]";

    // =========================================================================
    // GHI ĐỒNG BỘ 3 FILE: A, B, C (CÙNG LÚC)
    // =========================================================================

    // FILE A: DataAutoOner/SYMBOL_LIVE.json
    string fileA = DataFolder + symbol + "_LIVE.json";
    if(!WriteFileWithRetry(fileA, json_content)) {
        Print("ERROR: WriteCSDL2 - Failed to write file A: ", fileA);
        return false;
    }

    // FILE B: DataAutoOner2/SYMBOL_LIVE.json - GHI ĐỒNG BỘ
    string fileB = "DataAutoOner2\\" + symbol + "_LIVE.json";
    if(!WriteFileWithRetry(fileB, json_content)) {
        Print("ERROR: WriteCSDL2 - Failed to write file B: ", fileB);
        // Don't return false - A is already written successfully
    }

    // FILE C: DataAutoOner3/SYMBOL_LIVE.json - GHI ĐỒNG BỘ
    string fileC = "DataAutoOner3\\" + symbol + "_LIVE.json";
    if(!WriteFileWithRetry(fileC, json_content)) {
        Print("ERROR: WriteCSDL2 - Failed to write file C: ", fileC);
        // Don't return false - A is already written successfully
    }

    return true;
}

// [REMOVED] CopyCSDL2ToBackupFolders() - File B now written synchronously in WriteCSDL2ArrayToFile()

// Write string content to file with auto folder creation | Ghi noi dung chuoi vao file va tu dong tao thu muc
bool WriteStringToFile(string file_path, string content) {
    // MQL4 FileOpen() t? ??ng t?o folder n?u ch?a có
    int handle = FileOpen(file_path, FILE_WRITE|FILE_TXT|FILE_COMMON);
    if(handle == INVALID_HANDLE) {
        // Th? l?i không dùng FILE_COMMON
        handle = FileOpen(file_path, FILE_WRITE|FILE_TXT);
        if(handle == INVALID_HANDLE) {
            return false;
        }
    }

    FileWriteString(handle, content);
    FileClose(handle);
    return true;
}

//==============================================================================
//  SECTION 6: SIGNAL PROCESSING FUNCTIONS (3 functions) | PHAN 6: HAM XU LY TIN HIEU
//==============================================================================

// Update history array for specific timeframe (shift and insert) | Cap nhat mang lich su cho khung thoi gian cu the
void UpdateHistoryForTF(int tf_idx, int signal, double price, long cross_ref,
                        long timestamp, double pricediff, int timediff, int news_result) {

    // M1 (tf_idx = 0)
    if(tf_idx == 0) {
        // Shift array
        for(int i = HISTORY_SIZE - 1; i > 0; i--) {
            g_symbol_data.m1_history[i] = g_symbol_data.m1_history[i-1];
        }
        // Insert new
        g_symbol_data.m1_history[0].timeframe_name = "M1";
        g_symbol_data.m1_history[0].signal_3col = signal;
        g_symbol_data.m1_history[0].price_4col = price;
        g_symbol_data.m1_history[0].cross_5col = cross_ref;
        g_symbol_data.m1_history[0].timestamp_6col = timestamp;
        g_symbol_data.m1_history[0].pricediff_7col = pricediff;
        g_symbol_data.m1_history[0].timediff_8col = timediff;
        g_symbol_data.m1_history[0].news_result_9col = news_result;
        if(g_symbol_data.m1_count < HISTORY_SIZE) g_symbol_data.m1_count++;
    }
    // M5 (tf_idx = 1)
    else if(tf_idx == 1) {
        for(int i = HISTORY_SIZE - 1; i > 0; i--) {
            g_symbol_data.m5_history[i] = g_symbol_data.m5_history[i-1];
        }
        g_symbol_data.m5_history[0].timeframe_name = "M5";
        g_symbol_data.m5_history[0].signal_3col = signal;
        g_symbol_data.m5_history[0].price_4col = price;
        g_symbol_data.m5_history[0].cross_5col = cross_ref;
        g_symbol_data.m5_history[0].timestamp_6col = timestamp;
        g_symbol_data.m5_history[0].pricediff_7col = pricediff;
        g_symbol_data.m5_history[0].timediff_8col = timediff;
        g_symbol_data.m5_history[0].news_result_9col = news_result;
        if(g_symbol_data.m5_count < HISTORY_SIZE) g_symbol_data.m5_count++;
    }
    // M15 (tf_idx = 2)
    else if(tf_idx == 2) {
        for(int i = HISTORY_SIZE - 1; i > 0; i--) {
            g_symbol_data.m15_history[i] = g_symbol_data.m15_history[i-1];
        }
        g_symbol_data.m15_history[0].timeframe_name = "M15";
        g_symbol_data.m15_history[0].signal_3col = signal;
        g_symbol_data.m15_history[0].price_4col = price;
        g_symbol_data.m15_history[0].cross_5col = cross_ref;
        g_symbol_data.m15_history[0].timestamp_6col = timestamp;
        g_symbol_data.m15_history[0].pricediff_7col = pricediff;
        g_symbol_data.m15_history[0].timediff_8col = timediff;
        g_symbol_data.m15_history[0].news_result_9col = news_result;
        if(g_symbol_data.m15_count < HISTORY_SIZE) g_symbol_data.m15_count++;
    }
    // M30 (tf_idx = 3)
    else if(tf_idx == 3) {
        for(int i = HISTORY_SIZE - 1; i > 0; i--) {
            g_symbol_data.m30_history[i] = g_symbol_data.m30_history[i-1];
        }
        g_symbol_data.m30_history[0].timeframe_name = "M30";
        g_symbol_data.m30_history[0].signal_3col = signal;
        g_symbol_data.m30_history[0].price_4col = price;
        g_symbol_data.m30_history[0].cross_5col = cross_ref;
        g_symbol_data.m30_history[0].timestamp_6col = timestamp;
        g_symbol_data.m30_history[0].pricediff_7col = pricediff;
        g_symbol_data.m30_history[0].timediff_8col = timediff;
        g_symbol_data.m30_history[0].news_result_9col = news_result;
        if(g_symbol_data.m30_count < HISTORY_SIZE) g_symbol_data.m30_count++;
    }
    // H1 (tf_idx = 4)
    else if(tf_idx == 4) {
        for(int i = HISTORY_SIZE - 1; i > 0; i--) {
            g_symbol_data.h1_history[i] = g_symbol_data.h1_history[i-1];
        }
        g_symbol_data.h1_history[0].timeframe_name = "H1";
        g_symbol_data.h1_history[0].signal_3col = signal;
        g_symbol_data.h1_history[0].price_4col = price;
        g_symbol_data.h1_history[0].cross_5col = cross_ref;
        g_symbol_data.h1_history[0].timestamp_6col = timestamp;
        g_symbol_data.h1_history[0].pricediff_7col = pricediff;
        g_symbol_data.h1_history[0].timediff_8col = timediff;
        g_symbol_data.h1_history[0].news_result_9col = news_result;
        if(g_symbol_data.h1_count < HISTORY_SIZE) g_symbol_data.h1_count++;
    }
    // H4 (tf_idx = 5)
    else if(tf_idx == 5) {
        for(int i = HISTORY_SIZE - 1; i > 0; i--) {
            g_symbol_data.h4_history[i] = g_symbol_data.h4_history[i-1];
        }
        g_symbol_data.h4_history[0].timeframe_name = "H4";
        g_symbol_data.h4_history[0].signal_3col = signal;
        g_symbol_data.h4_history[0].price_4col = price;
        g_symbol_data.h4_history[0].cross_5col = cross_ref;
        g_symbol_data.h4_history[0].timestamp_6col = timestamp;
        g_symbol_data.h4_history[0].pricediff_7col = pricediff;
        g_symbol_data.h4_history[0].timediff_8col = timediff;
        g_symbol_data.h4_history[0].news_result_9col = news_result;
        if(g_symbol_data.h4_count < HISTORY_SIZE) g_symbol_data.h4_count++;
    }
    // D1 (tf_idx = 6)
    else if(tf_idx == 6) {
        for(int i = HISTORY_SIZE - 1; i > 0; i--) {
            g_symbol_data.d1_history[i] = g_symbol_data.d1_history[i-1];
        }
        g_symbol_data.d1_history[0].timeframe_name = "D1";
        g_symbol_data.d1_history[0].signal_3col = signal;
        g_symbol_data.d1_history[0].price_4col = price;
        g_symbol_data.d1_history[0].cross_5col = cross_ref;
        g_symbol_data.d1_history[0].timestamp_6col = timestamp;
        g_symbol_data.d1_history[0].pricediff_7col = pricediff;
        g_symbol_data.d1_history[0].timediff_8col = timediff;
        g_symbol_data.d1_history[0].news_result_9col = news_result;
        if(g_symbol_data.d1_count < HISTORY_SIZE) g_symbol_data.d1_count++;
    }
}

// Process new signal for timeframe with full analysis and file writes | Xu ly tin hieu moi cho khung thoi gian voi phan tich day du
bool ProcessSignalForTF(int tf_idx, int signal, long signal_time) {
    // Validate
    if(tf_idx < 0 || tf_idx >= 7) return false;
    if(signal_time <= 0) return false;
    if(signal == 0) return false;

    string symbol = g_symbol_data.symbol;
    string tf_names[7] = {"M1", "M5", "M15", "M30", "H1", "H4", "D1"};

    // Check if already processed (timestamp check is sufficient)
    if(signal_time <= g_symbol_data.processed_timestamps[tf_idx]) {
        return false;  // Already processed
    }

    // Get current price
    double current_price = (signal > 0) ? Ask : Bid;

    // Calculate Column 7: PriceDiff USD
    double price_diff = 0.0;
    if(g_symbol_data.signals_last[tf_idx] != 0) {
        if(signal > 0 && g_symbol_data.signals_last[tf_idx] < 0) {
            // BUY after SELL ? evaluate SELL
            price_diff = g_symbol_data.prices_last[tf_idx] - current_price;
        }
        else if(signal < 0 && g_symbol_data.signals_last[tf_idx] > 0) {
            // SELL after BUY ? evaluate BUY
            price_diff = current_price - g_symbol_data.prices_last[tf_idx];
        }
    }

    double pricediff_usd = GetUSDValue(symbol, MathAbs(price_diff));
    if(price_diff < 0) pricediff_usd = -pricediff_usd;

    // Calculate Column 8: TimeDiff minutes
    int timediff_min = 0;
    if(g_symbol_data.timestamps_last[tf_idx] > 0) {
        timediff_min = (int)((signal_time - g_symbol_data.timestamps_last[tf_idx]) / 60);
    }

    // Calculate Column 5: Cross (timestamp of previous TF)
    long cross_ref = 0;
    if(tf_idx > 0) {
        cross_ref = g_symbol_data.timestamps[tf_idx - 1];
    }

    // Update current arrays BEFORE calculating NEWS
    g_symbol_data.signals[tf_idx] = signal;
    g_symbol_data.prices[tf_idx] = current_price;
    g_symbol_data.timestamps[tf_idx] = signal_time;
    g_symbol_data.crosses[tf_idx] = cross_ref;
    g_symbol_data.pricediffs[tf_idx] = pricediff_usd;
    g_symbol_data.timediffs[tf_idx] = timediff_min;

    // Calculate Column 9: NEWS (reads from g_symbol_data)
    int news_result = AnalyzeNEWS();
    g_symbol_data.news_results[tf_idx] = news_result;

    // Calculate Column 10: Max Loss
    double max_loss = CalculateMaxLoss();
    g_symbol_data.max_losses[tf_idx] = max_loss;

    // Update last tracking
    g_symbol_data.signals_last[tf_idx] = signal;
    g_symbol_data.prices_last[tf_idx] = current_price;
    g_symbol_data.timestamps_last[tf_idx] = signal_time;
    g_symbol_data.processed_timestamps[tf_idx] = signal_time;

    // Update history
    UpdateHistoryForTF(tf_idx, signal, current_price, cross_ref,
                       signal_time, pricediff_usd, timediff_min, news_result);

    // Write files
    WriteCSDL1ArrayToFile();   // CSDL1: SYMBOL.json (10 columns + history)
    WriteCSDL2ArrayToFile();   // CSDL2: SYMBOL_LIVE.json (6 columns, no history, 3 folders)

    // Print 2 dòng vào Expert Tab
    string signal_text = (signal > 0) ? "BUY" : "SELL";
    string price_str = DoubleToString(current_price, 5);
    string pricediff_str = (pricediff_usd >= 0) ? "+" + DoubleToString(pricediff_usd, 2) : DoubleToString(pricediff_usd, 2);
    string news_str_log = (news_result >= 0) ? "+" + IntegerToString(news_result) : IntegerToString(news_result);

    // DÒNG 2: CSDL1 - A (IN SAU CSDL2)
    Print("->A>" + tf_names[tf_idx] + "< " + signal_text + " @ (" + IntegerToString(signal_time) + ") " + TimeToString(signal_time, TIME_DATE|TIME_MINUTES) +
          " | Price: " + price_str +
          " | PriceDiff: " + pricediff_str + " USD" +
          " | TimeDiff: " + IntegerToString(timediff_min) + "m" +
          " | NEWS: " + news_str_log);

    // DÒNG 1: CSDL2 Copy s? in TR??C trong CopyCSDL2ToBackupFolders()

    // Dashboard will be updated by OnTimer() every second

    return true;
}

// Print professional dashboard with 4 lines showing all 7 timeframe data | In bang dieu khien chuyen nghiep 4 dong hien thi du lieu 7 khung thoi gian
void PrintDashboard() {
    string symbol = g_symbol_data.symbol;
    string tf_names[7] = {"M1", "M5", "M15", "M30", "H1", "H4", "D1"};

    // Dòng 1: Thông tin c? b?n + LIVE values
    double pip_value = GetPipValue(symbol);
    double point_value = MarketInfo(symbol, MODE_POINT);
    if(point_value <= 0) point_value = Point;
    double usd_test = GetUSDValue(symbol, 1.0);

    // Calculate LIVE USD diff and Time diff (real-time t? M1)
    double m1_price = g_symbol_data.prices[0];           // M1 last signal price
    datetime m1_time = (datetime)g_symbol_data.timestamps[0];  // M1 last signal time
    double current_price = (Ask + Bid) / 2.0;           // Current real-time price
    double live_diff_raw = current_price - m1_price;    // Raw price difference
    double live_usd_diff = GetUSDValue(symbol, MathAbs(live_diff_raw));  // USD conversion
    int live_time_diff = (int)((TimeCurrent() - m1_time) / 60);  // Minutes since M1 signal

    // Format LIVE values
    string live_usd_str = DoubleToString(live_usd_diff, 2);
    if(live_diff_raw >= 0) live_usd_str = "+" + live_usd_str;
    else live_usd_str = "-" + live_usd_str;

    // =========================================================================
    // DÒNG 2: M1 ? M30 (4 TF)
    // =========================================================================
    string line2 = "";
    for(int i = 0; i < 4; i++) {
        string sig = "NONE";
        if(g_symbol_data.signals[i] > 0) sig = "BUY";
        else if(g_symbol_data.signals[i] < 0) sig = "SELL";

        string pricediff = DoubleToString(g_symbol_data.pricediffs[i], 2);
        if(g_symbol_data.pricediffs[i] >= 0) pricediff = "+" + pricediff;

        line2 += "[" + tf_names[i] + "|" + sig + "|" + pricediff + "|" + IntegerToString(g_symbol_data.timediffs[i]) + "m] ";
    }

    // =========================================================================
    // DÒNG 3: H1 ? D1 (3 TF)
    // =========================================================================
    string line3 = "";
    for(int i = 4; i < 7; i++) {
        string sig = "NONE";
        if(g_symbol_data.signals[i] > 0) sig = "BUY";
        else if(g_symbol_data.signals[i] < 0) sig = "SELL";

        string pricediff = DoubleToString(g_symbol_data.pricediffs[i], 2);
        if(g_symbol_data.pricediffs[i] >= 0) pricediff = "+" + pricediff;

        line3 += "[" + tf_names[i] + "|" + sig + "|" + pricediff + "|" + IntegerToString(g_symbol_data.timediffs[i]) + "m] ";
    }

    // =========================================================================
    // DÒNG 4: TREND_D1 + NEWS + LIVE values
    // =========================================================================
    string news_str = IntegerToString(g_symbol_data.news_results[0]);  // C?t 10 M1
    if(g_symbol_data.news_results[0] >= 0) news_str = "+" + news_str;

    string trend_d1 = "NONE";
    if(g_symbol_data.signals[6] > 0) trend_d1 = "BUY";
    else if(g_symbol_data.signals[6] < 0) trend_d1 = "SELL";

    // =========================================================================
    // BUILD 4 DÒNG DASHBOARD - DÙNG OBJECTCREATE() ?? TRÁNH CONFLICT V?I WT
    // =========================================================================
    // DÒNG 1: Thông tin c? b?n
    string line1 = "[" + symbol + "] SPY | CSDL1: Active | 7TF | USD:" + DoubleToString(usd_test, 2) + " pip:" + DoubleToString(pip_value, 5);
    // DÒNG 4: TREND_D1 + NEWS + LIVE values
    string line4 = "TREND_D1: " + trend_d1 + "  |  NEWS: " + news_str + " | LIVE: " + live_usd_str + " USD | " + IntegerToString(live_time_diff) + "m";

    // =========================================================================
    // T?O 4 OBJECTS RIÊNG BI?T (KHÔNG CONFLICT V?I COMMENT() C?A WT)
    // =========================================================================
    int y_start = 120;  // V? trí b?t ??u (120 pixels t? trên, d??i WT)
    int y_spacing = 15; // Kho?ng cách gi?a các dòng

    string obj_names[4];
    obj_names[0] = "SPY_Dashboard_Line1";
    obj_names[1] = "SPY_Dashboard_Line2";
    obj_names[2] = "SPY_Dashboard_Line3";
    obj_names[3] = "SPY_Dashboard_Line4";

    string lines[4];
    lines[0] = line1;
    lines[1] = line2;
    lines[2] = line3;
    lines[3] = line4;

    // T?o 4 objects
    for(int i = 0; i < 4; i++) {
        // Xóa object c? n?u có
        if(ObjectFind(0, obj_names[i]) >= 0) {
            ObjectDelete(0, obj_names[i]);
        }

        // Mau xen ke: Trang -> Xanh -> Trang -> Xanh | Alternating colors: White -> Blue -> White -> Blue
        color line_color = (i % 2 == 0) ? clrWhite : clrDodgerBlue;

        // T?o object m?i
        ObjectCreate(0, obj_names[i], OBJ_LABEL, 0, 0, 0);
        ObjectSetInteger(0, obj_names[i], OBJPROP_CORNER, CORNER_LEFT_UPPER);
        ObjectSetInteger(0, obj_names[i], OBJPROP_XDISTANCE, 10);
        ObjectSetInteger(0, obj_names[i], OBJPROP_YDISTANCE, y_start + (i * y_spacing));
        ObjectSetInteger(0, obj_names[i], OBJPROP_COLOR, line_color);
        ObjectSetInteger(0, obj_names[i], OBJPROP_FONTSIZE, 8);
        ObjectSetString(0, obj_names[i], OBJPROP_FONT, "Courier New");
        ObjectSetString(0, obj_names[i], OBJPROP_TEXT, lines[i]);
        ObjectSetInteger(0, obj_names[i], OBJPROP_SELECTABLE, false);
        ObjectSetInteger(0, obj_names[i], OBJPROP_HIDDEN, true);
    }
}

//==============================================================================
//  SECTION 7: ADDITIONAL GLOBAL VARIABLES (10 variables) | PHAN 7: BIEN TOAN CAU BO SUNG
//==============================================================================

// Enhanced database structure constants | Hang so cau truc co so du lieu
const int MAINDB_COLUMNS = 10;  // Column 9 = NEWS result, Column 10 = MAX LOSS | 10 cot du lieu
const int MAINDB_ROWS = 7;      // Number of database rows (7 timeframes) | So hang du lieu (7 khung thoi gian)

// System global variables | Bien toan cau he thong
string g_target_symbol = "";                                 // Target symbol discovered | Symbol muc tieu da phat hien
bool g_system_initialized = false;                           // System initialization status | Trang thai khoi tao he thong
int g_files_written = 0;                                     // Files written counter | Bo dem file da ghi

// Instance management constants | Hang so quan ly instance
const int MAX_INSTANCES = 10;                                // Maximum concurrent instances | So instance toi da

// Dashboard globals | Bien toan cau bang dieu khien
string g_dashboard_info = "";                                // Dashboard information | Thong tin bang dieu khien

// Midnight reset system | He thong reset luc nua dem
datetime g_last_midnight_switch = 0;                         // Last midnight switch time | Thoi gian chuyen doi nua dem cuoi
bool g_midnight_switch_done_today = false;                   // Today's switch status | Trang thai chuyen doi hom nay
int g_chart_period_before_switch = 0;                        // Store chart TF before midnight switch | Luu khung thoi gian truoc khi chuyen doi 0h

// Health check system | He thong kiem tra suc khoe
datetime g_last_health_check = 0;                            // Last health check time | Thoi gian kiem tra suc khoe cuoi
datetime g_last_csdl1_modified = 0;                          // Last CSDL1 modification time | Thoi gian sua doi CSDL1 cuoi

// CSDL1A Cache structure for LiveSignalAnalyzer | Cau truc bo nho dem CSDL1A
struct CSDL1ACache {
    // Timeframe data arrays | Mang du lieu khung thoi gian
    int signals[7];           // M1, M5, M15, M30, H1, H4 signals | Tin hieu cac khung
    double prices[7];         // M1, M5, M15, M30, H1, H4 prices | Gia cac khung
    long crosses[7];          // M1, M5, M15, M30, H1, H4 crosses | Tham chieu cheo
    long timestamps[7];       // M1, M5, M15, M30, H1, H4 timestamps | Dau thoi gian
    double pricediffs[7];     // M1, M5, M15, M30, H1, H4 price diffs | Chenh lech gia
    int timediffs[7];         // M1, M5, M15, M30, H1, H4 time diffs | Chenh lech thoi gian

    // History data | Du lieu lich su
    double history_prices[7]; // M1 history prices for sideways detection | Gia lich su M1 de phat hien dao dong ngang
    long last_file_time;      // Last file modification time | Thoi gian sua doi file cuoi
};

//==============================================================================
//  SECTION 8: LIVE SIGNAL CLASS (1 class) | PHAN 8: LOP TIN HIEU TRUC TIEP
//==============================================================================

// Simple live signal generator using MA crossover | Bo tao tin hieu truc tiep don gian dung MA cat nhau
class SimpleLiveSignal {
private:
    int m_last_signal;
    double m_ma5_prev;
    double m_ma10_prev;

public:
    SimpleLiveSignal() {
        m_last_signal = 0;
        m_ma5_prev = 0;
        m_ma10_prev = 0;
    }

    int GenerateLive() {
        double ma5 = iMA(NULL, 0, 5, 0, MODE_SMA, PRICE_CLOSE, 0);
        double ma10 = iMA(NULL, 0, 10, 0, MODE_SMA, PRICE_CLOSE, 0);

        if(ma5 > ma10 && m_ma5_prev <= m_ma10_prev) {
            if(m_last_signal <= 0) {
                m_last_signal = 1;
                m_ma5_prev = ma5;
                m_ma10_prev = ma10;
                return 1;
            }
        }
        else if(ma5 < ma10 && m_ma5_prev >= m_ma10_prev) {
            if(m_last_signal >= 0) {
                m_last_signal = -1;
                m_ma5_prev = ma5;
                m_ma10_prev = ma10;
                return -1;
            }
        }

        m_ma5_prev = ma5;
        m_ma10_prev = ma10;
        return 0;
    }

    void Reset() {
        m_last_signal = 0;
        m_ma5_prev = 0;
        m_ma10_prev = 0;
    }
};

//==============================================================================
//  SECTION 9: HELPER FUNCTIONS (20 functions) | PHAN 9: HAM HO TRO
//==============================================================================

// Calculate pip value for symbol (varies by asset type) | Tinh gia tri pip cho symbol (thay doi theo loai tai san)
double GetPipValue(string symbol) {
    // Get market info for the symbol
    double point = MarketInfo(symbol, MODE_POINT);
    int digits = (int)MarketInfo(symbol, MODE_DIGITS);

    if(point <= 0) {
        // Fallback: use current symbol if symbol info not available
        point = Point;
        digits = Digits;
    }

    // Convert symbol name to uppercase for comparison
    string symbol_upper = symbol;
    StringToUpper(symbol_upper);

    // ============ PRECIOUS METALS ============
    // GOLD - 1 PIP = 1.00 USD (integer part)
    if(StringFind(symbol_upper, "XAU") >= 0 ||
       StringFind(symbol_upper, "GOLD") >= 0) {
        return 1.00;  // FIXED: Gold 1 pip = 1.00 USD
    }
    // SILVER - 1 PIP = 0.01 USD
    else if(StringFind(symbol_upper, "XAG") >= 0 ||
            StringFind(symbol_upper, "SILVER") >= 0) {
        return 0.01;  // Silver 1 pip = 0.01 USD
    }

    // ============ JPY PAIRS ============
    // 1 PIP = 0.01 (2nd decimal place)
    else if(StringFind(symbol_upper, "JPY") >= 0) {
        if(digits == 3) {
            return 0.01;  // Standard JPY: 145.000
        }
        else if(digits == 4) {
            return 0.001;  // ECN JPY with pipette: 145.0000
        }
        else {
            return point * 10;  // Fallback
        }
    }

    // ============ CRYPTOCURRENCY ============
    // 1 PIP = 1.00 (integer part like gold)
    else if(StringFind(symbol_upper, "BTC") >= 0 ||
            StringFind(symbol_upper, "ETH") >= 0 ||
            StringFind(symbol_upper, "LTC") >= 0 ||
            StringFind(symbol_upper, "XRP") >= 0) {
        if(digits <= 2) {
            return 1.00;  // Crypto 1 pip = 1.00 USD
        }
        else {
            return point * 10;  // Higher precision crypto
        }
    }

    // ============ FOREX STANDARD PAIRS ============
    else if(digits == 4) {
        return point;  // 4-digit broker: 1 PIP = POINT
    }
    else if(digits == 5) {
        return point * 10;  // 5-digit ECN: 1 PIP = 10 POINTS
    }

    // ============ INDICES ============
    // US30, NAS100, SPX500, etc - 1 PIP = 1.00
    else if(StringFind(symbol_upper, "US30") >= 0 ||
            StringFind(symbol_upper, "NAS100") >= 0 ||
            StringFind(symbol_upper, "SPX500") >= 0 ||
            StringFind(symbol_upper, "GER40") >= 0 ||
            digits <= 2) {
        return 1.00;  // Indices 1 pip = 1.00
    }

    // ============ OIL ============
    else if(StringFind(symbol_upper, "OIL") >= 0 ||
            StringFind(symbol_upper, "WTI") >= 0 ||
            StringFind(symbol_upper, "BRENT") >= 0) {
        if(digits == 2) return 0.01;
        else if(digits == 3) return 0.01;
        else return point;
    }

    // ============ FALLBACK ============
    else {
        if(digits >= 4) {
            return point * 10;  // Assume forex-like
        }
        else if(digits == 3) {
            return 0.01;  // Could be JPY-like or commodity
        }
        else {
            return point;  // Conservative
        }
    }
}
// Convert price change to USD value using GOLD STANDARD | Chuyen doi thay doi gia sang gia tri USD dung chuan VANG
// GOLD STANDARD: 1 pip GOLD (0.01) = $0.10 USD as reference for all symbols
// Chuan vang: 1 pip VANG (0.01) = $0.10 USD lam tham chieu cho tat ca symbol
double GetUSDValue(string symbol, double price_change) {
    string symbol_upper = symbol;
    StringToUpper(symbol_upper);

    double point = MarketInfo(symbol, MODE_POINT);
    double digits = MarketInfo(symbol, MODE_DIGITS);

    // ========== CRYPTO - Already in USD ==========
    if(StringFind(symbol_upper, "BTC") >= 0 || StringFind(symbol_upper, "ETH") >= 0 ||
       StringFind(symbol_upper, "LTC") >= 0 || StringFind(symbol_upper, "BNB") >= 0 ||
       StringFind(symbol_upper, "SOL") >= 0 || StringFind(symbol_upper, "ADA") >= 0) {
        if(StringFind(symbol_upper, "BTC") >= 0) {
            return price_change * 1.0;
        }
        else if(StringFind(symbol_upper, "ETH") >= 0) {
            return price_change * 0.5;
        }
        else if(StringFind(symbol_upper, "LTC") >= 0) {
            return (price_change / 0.01) * 0.10;
        }
        else {
            return (price_change / 0.01) * 0.10;
        }
    }

    // ========== GOLD/SILVER - Our standard ==========
    if(StringFind(symbol_upper, "XAU") >= 0) {
        return (price_change / 0.01) * 0.10;
    }

    if(StringFind(symbol_upper, "XAG") >= 0) {
        return (price_change / 0.001) * 0.05;
    }

    // ========== FOREX PAIRS ==========
    bool is_forex = false;
    string currencies[] = {"EUR", "GBP", "USD", "JPY", "AUD", "NZD", "CHF", "CAD"};
    for(int i = 0; i < ArraySize(currencies); i++) {
        if(StringFind(symbol_upper, currencies[i]) >= 0) {
            is_forex = true;
            break;
        }
    }

    if(is_forex) {
        double pip_size = 0;
        if(digits == 2 || digits == 3) {
            pip_size = 0.01;
        } else if(digits == 4 || digits == 5) {
            pip_size = 0.0001;
        }

        if(digits == 5) pip_size = 0.0001;
        if(digits == 3) pip_size = 0.01;

        double pips = price_change / pip_size;

        if(StringFind(symbol_upper, "USD") == StringLen(symbol_upper) - 3) {
            return pips * 1.0;
        }
        else if(StringFind(symbol_upper, "USD") == 0) {
            double current_price = MarketInfo(symbol, MODE_BID);
            if(current_price > 0) {
                if(StringFind(symbol_upper, "JPY") > 0) {
                    return pips * 1.0 * 100 / current_price;
                } else {
                    return pips * 1.0 / current_price;
                }
            }
        }
        else {
            double tick_value = MarketInfo(symbol, MODE_TICKVALUE);
            if(tick_value > 0) {
                return pips * tick_value * 0.01;
            }
        }
    }

    // ========== INDICES ==========
    if(StringFind(symbol_upper, "US30") >= 0 || StringFind(symbol_upper, "US100") >= 0 ||
       StringFind(symbol_upper, "NAS") >= 0 || StringFind(symbol_upper, "SP") >= 0 ||
       StringFind(symbol_upper, "DAX") >= 0 || StringFind(symbol_upper, "FTSE") >= 0) {
        return (price_change / point) * 0.10;
    }

    // ========== OIL ==========
    if(StringFind(symbol_upper, "XTI") >= 0 || StringFind(symbol_upper, "XBR") >= 0 ||
       StringFind(symbol_upper, "OIL") >= 0 || StringFind(symbol_upper, "WTI") >= 0) {
        return (price_change / 0.01) * 0.10;
    }

    // ========== DEFAULT FALLBACK ==========
    double tick_value = MarketInfo(symbol, MODE_TICKVALUE);
    double tick_size = MarketInfo(symbol, MODE_TICKSIZE);

    if(tick_size > 0 && tick_value > 0) {
        return (price_change / tick_size) * tick_value * 0.01;
    }

    return (price_change / point) * 0.10;
}

// Extract integer field from JSON object string | Trich xuat truong so nguyen tu chuoi doi tuong JSON
int ExtractIntField(string json_obj, string field_name) {
    string search_str = "\"" + field_name + "\":";
    int pos = StringFind(json_obj, search_str);
    if(pos < 0) return 0;

    pos += StringLen(search_str);

    while(pos < StringLen(json_obj) &&
          (StringGetCharacter(json_obj, pos) == ' ' ||
           StringGetCharacter(json_obj, pos) == '\t')) {
        pos++;
    }

    string num_str = "";
    while(pos < StringLen(json_obj)) {
        ushort ch = StringGetCharacter(json_obj, pos);
        if(ch == ',' || ch == ' ' || ch == '}' || ch == '\n' || ch == '\r') break;
        num_str += ShortToString(ch);
        pos++;
    }

    return (int)StringToInteger(num_str);
}

// Extract long integer field from JSON object string | Trich xuat truong so nguyen dai tu chuoi doi tuong JSON
long ExtractLongField(string json_obj, string field_name) {
    string search_str = "\"" + field_name + "\":";
    int pos = StringFind(json_obj, search_str);
    if(pos < 0) return 0;

    pos += StringLen(search_str);

    while(pos < StringLen(json_obj) &&
          (StringGetCharacter(json_obj, pos) == ' ' ||
           StringGetCharacter(json_obj, pos) == '\t')) {
        pos++;
    }

    string num_str = "";
    while(pos < StringLen(json_obj)) {
        ushort ch = StringGetCharacter(json_obj, pos);
        if(ch == ',' || ch == ' ' || ch == '}' || ch == '\n' || ch == '\r') break;
        num_str += ShortToString(ch);
        pos++;
    }

    return (long)StringToInteger(num_str);
}

// Extract double field from JSON object string | Trich xuat truong so thuc tu chuoi doi tuong JSON
double ExtractDoubleField(string json_obj, string field_name) {
    string search_str = "\"" + field_name + "\":";
    int pos = StringFind(json_obj, search_str);
    if(pos < 0) return 0.0;

    pos += StringLen(search_str);

    while(pos < StringLen(json_obj) &&
          (StringGetCharacter(json_obj, pos) == ' ' ||
           StringGetCharacter(json_obj, pos) == '\t')) {
        pos++;
    }

    string num_str = "";
    while(pos < StringLen(json_obj)) {
        ushort ch = StringGetCharacter(json_obj, pos);
        if(ch == ',' || ch == ' ' || ch == '}' || ch == '\n' || ch == '\r') break;
        num_str += ShortToString(ch);
        pos++;
    }

    return StringToDouble(num_str);
}

// Convert signal integer to string representation | Chuyen doi so nguyen tin hieu sang chuoi dai dien
string SignalToString(int signal) {
    if(signal > 0) return "BUY";   // Buy signal | Tin hieu mua
    if(signal < 0) return "SELL";  // Sell signal | Tin hieu ban
    return "NONE";                 // No signal | Khong co tin hieu
}

// Calculate hash value for symbol string | Tinh gia tri hash cho chuoi symbol
int GetSymbolHash(string symbol) {
    int hash = 0;
    for(int i = 0; i < StringLen(symbol); i++) {
        hash = hash * 31 + StringGetCharacter(symbol, i);
    }
    return MathAbs(hash);
}

// Convert timeframe minutes to array index (1-7) | Chuyen doi phut khung thoi gian sang chi so mang
int GetTFIndex(int minutes) {
    switch(minutes) {
        case 1: return 1;
        case 5: return 2;
        case 15: return 3;
        case 30: return 4;
        case 60: return 5;
        case 240: return 6;
        case 1440: return 7;  // D1
    }
    return 0;
}

//...........................................................

string ExtractJsonValue(string json_obj, string key) {
    int key_pos = StringFind(json_obj, "\"" + key + "\":");
    if(key_pos < 0) return "0";

    int value_start = StringFind(json_obj, ":", key_pos) + 1;

    // Skip whitespace
    while(value_start < StringLen(json_obj) &&
          (StringGetChar(json_obj, value_start) == ' ' ||
           StringGetChar(json_obj, value_start) == '\t')) {
        value_start++;
    }

    // Find end (comma or })
    int value_end = value_start;
    while(value_end < StringLen(json_obj) &&
          StringGetChar(json_obj, value_end) != ',' &&
          StringGetChar(json_obj, value_end) != '}') {
        value_end++;
    }

    string value = StringSubstr(json_obj, value_start, value_end - value_start);
    StringTrimLeft(value);
    StringTrimRight(value);

    return value;
}

//==============================================================================
//  SECTION 10: FILE I/O FUNCTIONS (10 functions) | PHAN 10: HAM XUONG NHAP FILE
//==============================================================================

// Convert pips to points for the current symbol | Chuyen doi pip sang diem cho symbol hien tai
double PipsToPoints(double pips) {
    double pip_value = GetPipValue(g_target_symbol);
    if(pip_value <= 0) return 0.0;
    return pips * pip_value;
}

// Convert points to pips for display | Chuyen doi diem sang pip de hien thi
double PointsToPips(double points) {
    double pip_value = GetPipValue(g_target_symbol);
    if(pip_value <= 0) return 0.0;
    return points / pip_value;
}

// Convert timeframe period number to string name | Chuyen doi so chu ky khung thoi gian sang ten chuoi
string TimeframeToString(int tf_period) {
    switch(tf_period) {
        case 1: return "M1";
        case 5: return "M5";
        case 15: return "M15";
        case 30: return "M30";
        case 60: return "H1";
        case 240: return "H4";
        case 1440: return "D1";
        case 10080: return "W1";
        case 43200: return "MN1";
        default: return "M" + IntegerToString(tf_period);
    }
}

// Read file with 2-round retry mechanism (3 attempts per round) | Doc file voi co che thu lai 2 vong (3 lan thu moi vong)
bool ReadFileWithRetry(string filename, string& content) {
    // ROUND 1: First 3 attempts
    for(int retry = 0; retry < Retry; retry++) {
        int handle = FileOpen(filename, FILE_READ|FILE_TXT|FILE_ANSI);
        if(handle != INVALID_HANDLE) {
            content = "";
            while(!FileIsEnding(handle)) {
                content = content + FileReadString(handle) + "\n";
            }
            FileClose(handle);
            return true;
        }
        Sleep(250);
    }
    
    // ROUND 1 FAILED ? Auto unlock file
    int handle_unlock = FileOpen(filename, FILE_READ|FILE_SHARE_READ|FILE_SHARE_WRITE);
    if(handle_unlock != INVALID_HANDLE) {
        FileClose(handle_unlock);
    }
    Sleep(250);
    
    // ROUND 2: Second 3 attempts (after unlock)
    for(int retry = 0; retry < Retry; retry++) {
        int handle = FileOpen(filename, FILE_READ|FILE_TXT|FILE_ANSI);
        if(handle != INVALID_HANDLE) {
            content = "";
            while(!FileIsEnding(handle)) {
                content = content + FileReadString(handle) + "\n";
            }
            FileClose(handle);
            return true;
        }
        Sleep(250);
    }
    
    // ROUND 2 FAILED ? Simple warning (NO STOP BOT)
    Print("? File read failed after 2 rounds (", Retry*2, " attempts): ", filename, " - Bot continues");
    return false;
}

// Write file with 2-round retry mechanism (3 attempts per round) | Ghi file voi co che thu lai 2 vong (3 lan thu moi vong)
bool WriteFileWithRetry(string filename, string content) {
    // ROUND 1: First 3 attempts
    for(int retry = 0; retry < Retry; retry++) {
        int handle = FileOpen(filename, FILE_WRITE|FILE_TXT);
        if(handle != INVALID_HANDLE) {
            FileWrite(handle, content);
            FileClose(handle);
            return true;
        }
        Sleep(250);
    }
    
    // ROUND 1 FAILED ? Auto unlock file
    int handle_unlock = FileOpen(filename, FILE_READ|FILE_SHARE_READ|FILE_SHARE_WRITE);
    if(handle_unlock != INVALID_HANDLE) {
        FileClose(handle_unlock);
    }
    Sleep(250);
    
    // ROUND 2: Second 3 attempts (after unlock)
    for(int retry = 0; retry < Retry; retry++) {
        int handle = FileOpen(filename, FILE_WRITE|FILE_TXT);
        if(handle != INVALID_HANDLE) {
            FileWrite(handle, content);
            FileClose(handle);
            return true;
        }
        Sleep(250);
    }
    
    // ROUND 2 FAILED ? Simple warning (NO STOP BOT)
    Print("? File write failed after 2 rounds (", Retry*2, " attempts): ", filename, " - Bot continues");
    return false;
}

// Discover symbol from current chart or input parameter | Phat hien symbol tu bieu do hien tai hoac tham so dau vao
string DiscoverSymbolFromChart() {
    // First try: Use TargetSymbol if provided
    if(StringLen(TargetSymbol) > 0) {
        return TargetSymbol;
    }

    // Second try: Use current chart symbol
    string chart_symbol = Symbol();
    if(StringLen(chart_symbol) > 0) {
        return chart_symbol;
    }

    // Fallback
    return "EURUSD";
}

// Create all 3 data folder structures if not exist | Tao tat ca 3 cau truc thu muc du lieu neu chua ton tai
void CreateFolderStructure() {
    // T?O 3 TH? M?C N?U CH?A CÓ
    // MQL4 không có FolderCreate() - dùng FileOpen() trick
    // T?o dummy file ?? force t?o folder, sau ?ó xóa

    // Folder 1: DataAutoOner (cho CSDL1 + CSDL2 A)
    string test1 = "DataAutoOner\\.test";
    if(!FileIsExist(test1)) {
        string dummy1 = "DataAutoOner\\.dummy";
        int handle1 = FileOpen(dummy1, FILE_WRITE|FILE_TXT);
        if(handle1 != INVALID_HANDLE) {
            FileClose(handle1);
            FileDelete(dummy1);
        }
    }

    // Folder 2: DataAutoOner2 (cho CSDL2 B)
    string test2 = "DataAutoOner2\\.test";
    if(!FileIsExist(test2)) {
        string dummy2 = "DataAutoOner2\\.dummy";
        int handle2 = FileOpen(dummy2, FILE_WRITE|FILE_TXT);
        if(handle2 != INVALID_HANDLE) {
            FileClose(handle2);
            FileDelete(dummy2);
        }
    }

    // Folder 3: DataAutoOner3 (cho CSDL2 C)
    string test3 = "DataAutoOner3\\.test";
    if(!FileIsExist(test3)) {
        string dummy3 = "DataAutoOner3\\.dummy";
        int handle3 = FileOpen(dummy3, FILE_WRITE|FILE_TXT);
        if(handle3 != INVALID_HANDLE) {
            FileClose(handle3);
            FileDelete(dummy3);
        }
    }

    // Folder 4: DataAutoOner\HISTORY (cho thong ke thang)
    string test4 = "DataAutoOner\\HISTORY\\.test";
    if(!FileIsExist(test4)) {
        string dummy4 = "DataAutoOner\\HISTORY\\.dummy";
        int handle4 = FileOpen(dummy4, FILE_WRITE|FILE_TXT);
        if(handle4 != INVALID_HANDLE) {
            FileClose(handle4);
            FileDelete(dummy4);
        }
    }
}

// Create empty CSDL1 file if not exist (called from OnInit) | Tao file CSDL1 rong neu chua ton tai (goi tu OnInit)
void CreateEmptyCSDL1File() {
    string file_path = DataFolder + g_symbol_data.symbol + ".json";

    // Neu file da co thi khong lam gi | If file exists, do nothing
    if(FileIsExist(file_path)) return;

    // Tao file moi voi cau truc day du: metadata + data + history_count + history
    // Create new file with full structure: metadata + data + history_count + history
    string symbol = g_symbol_data.symbol;
    long current_time = TimeCurrent();

    string json = "{\n";
    json += "    \"symbol\": \"" + symbol + "\",\n";
    json += "    \"type\": \"main\",\n";
    json += "    \"timestamp\": " + IntegerToString(current_time) + ",\n";
    json += "    \"rows\": 7,\n";
    json += "    \"columns\": 10,\n";
    json += "    \"data\": [\n";

    // 7 TF × 10 columns (all zeros) | 7 khung thoi gian × 10 cot (tat ca = 0)
    string tf_names[7] = {"M1", "M5", "M15", "M30", "H1", "H4", "D1"};
    int tf_periods[7] = {1, 5, 15, 30, 60, 240, 1440};

    for(int i = 0; i < 7; i++) {
        if(i > 0) json += ",\n";
        json += "        {\"timeframe_name\": \"" + tf_names[i] + "\", ";
        json += "\"timeframe\": " + IntegerToString(tf_periods[i]) + ", ";
        json += "\"signal\": 0, ";
        json += "\"price\": 0.00000, ";
        json += "\"cross\": 0, ";
        json += "\"timestamp\": 0, ";
        json += "\"pricediff\": 0.00, ";
        json += "\"timediff\": 0, ";
        json += "\"news\": 0, ";
        json += "\"max_loss\": 0.00}";
    }

    json += "\n    ],\n";

    // history_count: all zeros | Dem lich su: tat ca = 0
    json += "    \"history_count\": {\"m1\": 0, \"m5\": 0, \"m15\": 0, \"m30\": 0, \"h1\": 0, \"h4\": 0, \"d1\": 0},\n";

    // history: empty arrays | Lich su: mang rong
    json += "\"history\": {\n";
    json += "    \"m1\": [\n";
    json += "    ],\n";
    json += "    \"m5\": [\n";
    json += "    ],\n";
    json += "    \"m15\": [\n";
    json += "    ],\n";
    json += "    \"m30\": [],\n";
    json += "    \"h1\": [],\n";
    json += "    \"h4\": [],\n";
    json += "    \"d1\": [\n";
    json += "    ]\n";
    json += "}\n";
    json += "}\n";

    // Write to file | Ghi vao file
    int handle = FileOpen(file_path, FILE_WRITE|FILE_TXT);
    if(handle != INVALID_HANDLE) {
        FileWriteString(handle, json);
        FileClose(handle);
        Print("[CSDL1_CREATE] Empty file created with full structure: ", file_path);
    } else {
        Print("[CSDL1_CREATE_ERROR] Failed to create file: ", file_path, " Error: ", GetLastError());
    }
}

// Copy CSDL1 File C from A if not exist (called from OnInit once) | Sao chep CSDL1 File C tu A neu chua ton tai (goi 1 lan tu OnInit)
void CreateEmptyCSDL1FileC() {
    string symbol = g_symbol_data.symbol;
    string fileA = DataFolder + symbol + ".json";
    string fileC = "DataAutoOner3\\" + symbol + ".json";

    // Nếu File C đã tồn tại → Không làm gì
    if(FileIsExist(fileC)) return;

    // Nếu File A không tồn tại → Không làm gì (sẽ tạo sau khi có signal)
    if(!FileIsExist(fileA)) return;

    // Copy File A → File C (1 lần duy nhất khi khởi động)
    int handleA = FileOpen(fileA, FILE_READ|FILE_TXT);
    if(handleA == INVALID_HANDLE) return;

    string content = "";
    while(!FileIsEnding(handleA)) {
        content += FileReadString(handleA);
    }
    FileClose(handleA);

    if(StringLen(content) > 10) {
        int handleC = FileOpen(fileC, FILE_WRITE|FILE_TXT);
        if(handleC != INVALID_HANDLE) {
            FileWrite(handleC, content);
            FileClose(handleC);
            Print("OK: CSDL1 C copied from A (OnInit)");
        }
    }
}

// Create empty CSDL2 files A,B,C if not exist (called from OnInit) | Tao file CSDL2 rong A,B,C neu chua ton tai (goi tu OnInit)
void CreateEmptyCSDL2Files() {
    string symbol = g_symbol_data.symbol;
    string fileA = DataFolder + symbol + "_LIVE.json";
    string fileB = "DataAutoOner2\\" + symbol + "_LIVE.json";
    string fileC = "DataAutoOner3\\" + symbol + "_LIVE.json";

    // 1. T?O FILE A R?NG N?U CH?A CÓ
    if(!FileIsExist(fileA)) {
        string empty_json = "[\n";
        empty_json += "  {\"max_loss\":0.00,\"timestamp\":0,\"signal\":0,\"pricediff\":0.00,\"timediff\":0,\"news\":0},\n";  // M1
        empty_json += "  {\"max_loss\":0.00,\"timestamp\":0,\"signal\":0,\"pricediff\":0.00,\"timediff\":0,\"news\":0},\n";  // M5
        empty_json += "  {\"max_loss\":0.00,\"timestamp\":0,\"signal\":0,\"pricediff\":0.00,\"timediff\":0,\"news\":0},\n";  // M15
        empty_json += "  {\"max_loss\":0.00,\"timestamp\":0,\"signal\":0,\"pricediff\":0.00,\"timediff\":0,\"news\":0},\n";  // M30
        empty_json += "  {\"max_loss\":0.00,\"timestamp\":0,\"signal\":0,\"pricediff\":0.00,\"timediff\":0,\"news\":0},\n";  // H1
        empty_json += "  {\"max_loss\":0.00,\"timestamp\":0,\"signal\":0,\"pricediff\":0.00,\"timediff\":0,\"news\":0},\n";  // H4
        empty_json += "  {\"max_loss\":0.00,\"timestamp\":0,\"signal\":0,\"pricediff\":0.00,\"timediff\":0,\"news\":0}\n";   // D1
        empty_json += "]\n";

        int handleA = FileOpen(fileA, FILE_WRITE|FILE_TXT);
        if(handleA != INVALID_HANDLE) {
            FileWrite(handleA, empty_json);
            FileClose(handleA);
            Print("? CSDL2 A empty file created");
        }
    }

    // 2. COPY FILE B T? A N?U CH?A CÓ (KHÔNG T?O R?NG!)
    if(!FileIsExist(fileB) && FileIsExist(fileA)) {
        int handleA = FileOpen(fileA, FILE_READ|FILE_TXT);
        if(handleA != INVALID_HANDLE) {
            string content = "";
            while(!FileIsEnding(handleA)) {
                content += FileReadString(handleA);
            }
            FileClose(handleA);

            if(StringLen(content) > 10) {
                int handleB = FileOpen(fileB, FILE_WRITE|FILE_TXT);
                if(handleB != INVALID_HANDLE) {
                    FileWrite(handleB, content);
                    FileClose(handleB);
                    Print("? CSDL2 B copied from A");
                }
            }
        }
    }

    // 3. COPY FILE C T? A N?U CH?A CÓ (KHÔNG T?O R?NG!)
    if(!FileIsExist(fileC) && FileIsExist(fileA)) {
        int handleA = FileOpen(fileA, FILE_READ|FILE_TXT);
        if(handleA != INVALID_HANDLE) {
            string content = "";
            while(!FileIsEnding(handleA)) {
                content += FileReadString(handleA);
            }
            FileClose(handleA);

            if(StringLen(content) > 10) {
                int handleC = FileOpen(fileC, FILE_WRITE|FILE_TXT);
                if(handleC != INVALID_HANDLE) {
                    FileWrite(handleC, content);
                    FileClose(handleC);
                    Print("? CSDL2 C copied from A");
                }
            }
        }
    }
}

//==============================================================================
//  SECTION 11: NEWS CASCADE STRATEGY (5 functions) | PHAN 11: CHIEN LUOC NEWS CASCADE
//==============================================================================
// 6-level cascade detection system for multi-timeframe signal alignment
// He thong phat hien cascade 6 cap do de sap xep tin hieu nhieu khung thoi gian

// Detect NEWS CASCADE across 6 levels of timeframe alignment | Phat hien NEWS CASCADE qua 6 cap do sap xep khung thoi gian
int DetectCASCADE_New() {
    // Get 7 TF signals (M1=0, M5=1, ..., D1=6) from g_symbol_data
    int m1_signal = g_symbol_data.signals[0];
    int m5_signal = g_symbol_data.signals[1];
    int m15_signal = g_symbol_data.signals[2];
    int m30_signal = g_symbol_data.signals[3];
    int h1_signal = g_symbol_data.signals[4];
    int h4_signal = g_symbol_data.signals[5];
    int d1_signal = g_symbol_data.signals[6];

    // Get timestamps & crosses
    datetime m1_time = (datetime)g_symbol_data.timestamps[0];
    datetime m5_time = (datetime)g_symbol_data.timestamps[1];
    datetime m15_time = (datetime)g_symbol_data.timestamps[2];
    datetime m30_time = (datetime)g_symbol_data.timestamps[3];
    datetime h1_time = (datetime)g_symbol_data.timestamps[4];
    datetime h4_time = (datetime)g_symbol_data.timestamps[5];
    datetime d1_time = (datetime)g_symbol_data.timestamps[6];

    datetime m1_cross = (datetime)g_symbol_data.crosses[0];
    datetime m5_cross = (datetime)g_symbol_data.crosses[1];
    datetime m15_cross = (datetime)g_symbol_data.crosses[2];
    datetime m30_cross = (datetime)g_symbol_data.crosses[3];
    datetime h1_cross = (datetime)g_symbol_data.crosses[4];
    datetime h4_cross = (datetime)g_symbol_data.crosses[5];
    datetime d1_cross = (datetime)g_symbol_data.crosses[6];

    // Calculate LIVE USD diff from current price (real-time)
    double m1_price = g_symbol_data.prices[0];          // M1 last signal price
    double current_price = (Ask + Bid) / 2.0;                // Current real-time price
    double live_diff_raw = current_price - m1_price;         // Raw price difference
    double live_usd_diff = GetUSDValue(g_target_symbol, MathAbs(live_diff_raw));  // USD conversion
    int live_time_diff = (int)(TimeCurrent() - m1_time);     // Time since M1 signal
    int highest_result = 0;

    // ============================================================
    // L1: M5?M1 (Basic +1 / Advanced +16)
    // ============================================================
    if(m5_signal != 0 && m1_signal != 0 && m1_signal == m5_signal) {
        if(m5_cross == m1_time) {  // M5.cross = M1.timestamp
            int result = 1;  // Basic
            if(live_usd_diff >= 4.0 && live_time_diff <= 300) {  // 5 min
                result = 16;  // Advanced
            }
            highest_result = m5_signal * result;
        }
    }

    // ============================================================
    // L2: M15?M5?M1 (Basic +12 / Advanced +17)
    // BONUS: M15?M5 (cross reference exists, USD > 0) = +2
    // ============================================================
    if(m15_signal != 0 && m5_signal != 0 && m5_signal == m15_signal) {
        if(m15_cross == m5_time) {  // M15.cross = M5.timestamp
            int result = 0;

            // Check if M5?M1 cascade exists
                // Full cascade: M15?M5?M1
            if(m1_signal == m15_signal && m5_cross == m1_time) {
                result = 12;  // Basic
                if(live_usd_diff >= 6.0 && live_time_diff <= 900) {  // 15 min
                    result = 17;  // Advanced
                }
            } else if(m15_cross == m5_time && live_usd_diff > 0) {
                // BONUS: M15?M5 cross exists + USD > 0
                result = 2;
            }

            if(result > MathAbs(highest_result)) {
                highest_result = m15_signal * result;
            }
        }
    }

    // BONUS standalone check if not in full cascade
    // MUST check same direction: m5_signal == m15_signal
    if(m15_signal != 0 && m5_signal != 0 && m5_signal == m15_signal && m15_cross == m5_time && live_usd_diff > 0) {
        if(MathAbs(highest_result) < 2) {
            highest_result = m15_signal * 2;
        }
    }

    // ============================================================
    // L3: M30?M15?M5 (Basic +13 / Advanced +18)
    // BONUS: M30?M15 (cross exists, USD > 0) = +3
    // ============================================================
    if(m30_signal != 0 && m15_signal != 0 && m15_signal == m30_signal) {
        if(m30_cross == m15_time) {  // M30.cross = M15.timestamp
            int result = 0;

            // Check M15?M5 cascade
            if(m5_signal == m30_signal && m15_cross == m5_time) {
                // Full: M30?M15?M5
                result = 13;
                if(live_usd_diff >= 8.0 && live_time_diff <= 1800) {  // 30 min
                    result = 18;
                }
            } else if(m30_cross == m15_time && live_usd_diff > 0) {
                // BONUS: M30?M15 cross exists + USD > 0
                result = 3;
            }

            if(result > MathAbs(highest_result)) {
                highest_result = m30_signal * result;
            }
        }
    }

    // BONUS standalone
    // MUST check same direction: m15_signal == m30_signal
    if(m30_signal != 0 && m15_signal != 0 && m15_signal == m30_signal && m30_cross == m15_time && live_usd_diff > 0) {
        if(MathAbs(highest_result) < 3) {
            highest_result = m30_signal * 3;
        }
    }

    // ============================================================
    // L4: H1?M30?M15 (Basic +14 / Advanced +19)
    // BONUS: H1?M30 (cross exists, USD > 0) = +4
    // ============================================================
    if(h1_signal != 0 && m30_signal != 0 && m30_signal == h1_signal) {
        if(h1_cross == m30_time) {  // H1.cross = M30.timestamp
            int result = 0;

            // Check M30?M15 cascade
            if(m15_signal == h1_signal && m30_cross == m15_time) {
                // Full: H1?M30?M15
                result = 14;
                if(live_usd_diff >= 10.0 && live_time_diff <= 3600) {  // 1 hour
                    result = 19;
                }
            } else if(h1_cross == m30_time && live_usd_diff > 0) {
                // BONUS: H1?M30 cross exists + USD > 0
                result = 4;
            }

            if(result > MathAbs(highest_result)) {
                highest_result = h1_signal * result;
            }
        }
    }

    // BONUS standalone
    // MUST check same direction: m30_signal == h1_signal
    if(h1_signal != 0 && m30_signal != 0 && m30_signal == h1_signal && h1_cross == m30_time && live_usd_diff > 0) {
        if(MathAbs(highest_result) < 4) {
            highest_result = h1_signal * 4;
        }
    }

    // ============================================================
    // L5: H4?H1?M30 (Basic +15 / Advanced +20)
    // BONUS: H4?H1 (cross exists, USD > 0) = +5
    // ============================================================
    if(h4_signal != 0 && h1_signal != 0 && h1_signal == h4_signal) {
        if(h4_cross == h1_time) {  // H4.cross = H1.timestamp
            int result = 0;

            // Check H1?M30 cascade
            if(m30_signal == h4_signal && h1_cross == m30_time) {
                // Full: H4?H1?M30
                result = 15;
                if(live_usd_diff >= 12.0 && live_time_diff <= 14400) {  // 4 hours
                    result = 20;
                }
            } else if(h4_cross == h1_time && live_usd_diff > 0) {
                // BONUS: H4?H1 cross exists + USD > 0
                result = 5;
            }

            if(result > MathAbs(highest_result)) {
                highest_result = h4_signal * result;
            }
        }
    }

    // BONUS standalone
    // MUST check same direction: h1_signal == h4_signal
    if(h4_signal != 0 && h1_signal != 0 && h1_signal == h4_signal && h4_cross == h1_time && live_usd_diff > 0) {
        if(MathAbs(highest_result) < 5) {
            highest_result = h4_signal * 5;
        }
    }

    // ============================================================
    // L6: D1?H4?H1 (Basic +16 / Advanced +30) - NEW
    // BONUS: D1?H4 (cross exists, USD > 0) = +6
    // ============================================================
    if(d1_signal != 0 && h4_signal != 0 && h4_signal == d1_signal) {
        if(d1_cross == h4_time) {  // D1.cross = H4.timestamp
            int result = 0;

            // Check H4?H1 cascade
            if(h1_signal == d1_signal && h4_cross == h1_time) {
                // Full: D1?H4?H1
                result = 16;
                if(live_usd_diff >= 14.0 && live_time_diff <= 14400) {  // 4 hours
                    result = 30;
                }
            } else if(d1_cross == h4_time && live_usd_diff > 0) {
                // BONUS: D1?H4 cross exists + USD > 0
                result = 6;
            }

            if(result > MathAbs(highest_result)) {
                highest_result = d1_signal * result;
            }
        }
    }

    // BONUS standalone
    // MUST check same direction: h4_signal == d1_signal
    if(d1_signal != 0 && h4_signal != 0 && h4_signal == d1_signal && d1_cross == h4_time && live_usd_diff > 0) {
        if(MathAbs(highest_result) < 6) {
            highest_result = d1_signal * 6;
        }
    }

    return highest_result;
}

// Check if active NEWS direction has reversed based on timeframe | Kiem tra huong NEWS dang hoat dong co dao nguoc khong
bool DirectionReversed() {
    if(g_news_active_level == 0) return false;  // No active state

    // L1: No reversal check - will reset naturally when CASCADE expires
    if(g_news_active_level == 1) return false;

    // Map level to timeframe index for reset check
    int check_index = -1;

    switch(g_news_active_level) {
        case 2: check_index = 1; break;  // L2 (M15?M5?M1) - reset when M5 reverses
        case 3: check_index = 2; break;  // L3 (M30?M15?M5) - reset when M15 reverses
        case 4: check_index = 6; break;  // L4 (H1?M30?M15) - reset when D1 reverses
        case 5: check_index = 6; break;  // L5 (H4?H1?M30) - reset when D1 reverses
        case 6: check_index = 6; break;  // L6 (D1?H4?H1) - reset when D1 reverses
    }

    if(check_index < 0) return false;

    // Get signal from g_symbol_data
    int tf_signal = g_symbol_data.signals[check_index];

    // Check reversal
    if(tf_signal != 0 && tf_signal != g_news_active_direction) {
        return true;
    }

    return false;
}

// Activate NEWS state with level and direction | Kich hoat trang thai NEWS voi cap do va huong
void ActivateNewsState(int level, int direction) {
    if(level < 1 || level > 6) return;  // ??i 5?6 ?? support L6
    
    // CH? update n?u level cao h?n
    if(level > g_news_active_level) {
        g_news_active_level = level;
        g_news_active_direction = direction;
        
    }
}

// Reset NEWS state to inactive | Dat lai trang thai NEWS ve khong hoat dong
void ResetNewsState() {
    g_news_active_level = 0;       // Clear level | Xoa cap do
    g_news_active_direction = 0;   // Clear direction | Xoa huong
}

// Main NEWS analysis function with cascade detection and state management | Ham phan tich NEWS chinh voi phat hien cascade va quan ly trang thai
int AnalyzeNEWS() {
    // Get M1 signal from g_symbol_data
    int m1_signal = g_symbol_data.signals[0];
    double m1_price = g_symbol_data.prices[0];
    long m1_timestamp = g_symbol_data.timestamps[0];

    if(m1_signal == 0) return 0;

    // Step 0: CHECK DIRECTION REVERSAL - RESET STATE - 2025-10-15
    // L1: Natural reset when CASCADE expires (không check reversal)
    // L2: Reset when M5 reverses
    // L3: Reset when M15 reverses
    // L4, L5, L6: Reset when D1 reverses
    if(g_news_active_level > 0) {
        if(DirectionReversed()) {
            ResetNewsState();
        }
    }


    // Step 3: CASCADE detection (NEW ENCODING)
    int cascade_result = DetectCASCADE_New();

    // Step 4: State management (NEW LOGIC)
    if(cascade_result != 0) {
        int level = MathAbs(cascade_result);
        int direction = cascade_result > 0 ? 1 : -1;

        // Priority: activate if higher level or direction changed
        if(level > g_news_active_level ||
           (level == g_news_active_level && direction != g_news_active_direction)) {
            ActivateNewsState(level, direction);

        }
    }
    else {
        // No CASCADE detected
        // L1: Natural reset when CASCADE expires (live h?t thì t? reset)
        if(g_news_active_level == 1) {
            ResetNewsState();
        }
    }

    // Step 5: Return active state OR CASCADE result
    // If state active, return state (keep level until reset conditions met)
    if(g_news_active_level > 0) {
        int active_result = g_news_active_direction * g_news_active_level;
        return active_result;
    }

    // If no active state, return cascade result
    if(cascade_result != 0) {
        return cascade_result;  // Return encoded value: +1 to +30 or -1 to -30
    }

    return 0;
}

//==============================================================================
//  SECTION 12: JSON & DATABASE FUNCTIONS (8 functions) | PHAN 12: HAM JSON VA CO SO DU LIEU
//==============================================================================

// Read JSON file and parse to rows array | Doc file JSON va phan tich thanh mang hang
bool ReadJsonToRows(string file_path, string& rows[]) {
    string json_content;
    if(!ReadFileWithRetry(file_path, json_content)) {
        return false;
    }

    return ParseJsonToRows(json_content, rows);
}

// Parse JSON content string to rows array | Phan tich chuoi noi dung JSON thanh mang hang
bool ParseJsonToRows(string json_content, string& rows[]) {
    // Find data array
    int data_start = StringFind(json_content, "\"data\": [");
    if(data_start < 0) return false;

    int array_start = StringFind(json_content, "[", data_start) + 1;
    int array_end = StringFind(json_content, "]", array_start);
    if(array_end < 0) return false;

    string data_content = StringSubstr(json_content, array_start, array_end - array_start);

    // Split by objects
    string objects[];
    int obj_count = StringSplit(data_content, '}', objects);

    for(int i = 0; i < obj_count && i < MAINDB_ROWS; i++) {
        string obj = objects[i];
        StringReplace(obj, "{", "");
        StringReplace(obj, "\"", "");

        // Extract timeframe value directly
        int row_num = 0;
        string tf_value = ExtractValue(obj, "timeframe");

        if(tf_value == "1") row_num = 1;      // M1
        else if(tf_value == "5") row_num = 2;  // M5
        else if(tf_value == "15") row_num = 3; // M15
        else if(tf_value == "30") row_num = 4; // M30
        else if(tf_value == "60") row_num = 5; // H1
        else if(tf_value == "240") row_num = 6; // H4
        else if(tf_value == "1440") row_num = 7; // D1

        // Skip if row number not found or invalid
        if(row_num < 1 || row_num > MAINDB_ROWS) continue;

        rows[row_num] = ParseObjectToRowString(obj);

    }

    return true;
}

// Parse JSON object to CSV row string | Phan tich doi tuong JSON thanh chuoi hang CSV
string ParseObjectToRowString(string obj) {
    // Extract values in order
    string values[10];  // 10 columns (with news_result and max_loss)

    // Internal array needs placeholder at [0] and timeframe value at [1] for compatibility
    values[0] = "0";  // placeholder (internal use)

    // Extract timeframe as number
    string tf_str = ExtractValue(obj, "timeframe");
    if(tf_str == "") {
        // Try to parse from timeframe_name
        string tf_name = ExtractValue(obj, "timeframe_name");
        if(tf_name == "M1") values[1] = "1";
        else if(tf_name == "M5") values[1] = "5";
        else if(tf_name == "M15") values[1] = "15";
        else if(tf_name == "M30") values[1] = "30";
        else if(tf_name == "H1") values[1] = "60";
        else if(tf_name == "H4") values[1] = "240";
        else if(tf_name == "D1") values[1] = "1440";
        else values[1] = "0";
    } else {
        values[1] = tf_str;
    }

    // Map 10 JSON columns to internal array
    values[2] = ExtractValue(obj, "signal");        // Column 3 in JSON
    values[3] = ExtractValue(obj, "price");         // Column 4 in JSON
    values[4] = ExtractValue(obj, "cross");         // Column 5 in JSON
    values[5] = ExtractValue(obj, "timestamp");     // Column 6 in JSON
    values[6] = ExtractValue(obj, "pricediff");     // Column 7 in JSON
    values[7] = ExtractValue(obj, "timediff");      // Column 8 in JSON
    values[8] = ExtractValue(obj, "news");          // Column 9 in JSON
    values[9] = ExtractValue(obj, "max_loss");      // Column 10 in JSON

    // Build row string
    string row = "";
    for(int i = 0; i < MAINDB_COLUMNS; i++) {
        if(i > 0) row = row + ",";
        if(values[i] == "") values[i] = "0";  // Default to 0 if missing
        row = row + values[i];
    }

    return row;
}

// Extract value for key from JSON object string | Trich xuat gia tri cho khoa tu chuoi doi tuong JSON
string ExtractValue(string obj, string key) {
    int key_pos = StringFind(obj, key + ": ");
    if(key_pos < 0) return "";

    int value_start = key_pos + StringLen(key) + 2;
    int value_end = StringFind(obj, ",", value_start);
    if(value_end < 0) value_end = StringLen(obj);

    string value = StringSubstr(obj, value_start, value_end - value_start);
    StringTrimLeft(value);
    StringTrimRight(value);

    return value;
}

// Write rows array to JSON file with retry mechanism | Ghi mang hang ra file JSON voi co che thu lai
bool WriteRowsToJson(string file_path, string& rows[]) {
    string json_content = BuildEnhancedJsonContent(rows);

    // Use retry mechanism for main file write
    if(!WriteFileWithRetry(file_path, json_content)) {
        return false;
    }

    g_files_written++;  // Increment write counter


    return true;
}

// Build enhanced JSON content with metadata and history | Xay dung noi dung JSON nang cao voi du lieu meta va lich su
string BuildEnhancedJsonContent(string& rows[]) {
    string json_content = "{\n";
    json_content = json_content + "    \"symbol\": \"" + g_target_symbol + "\",\n";
    json_content = json_content + "    \"type\": \"main\",\n";
    json_content = json_content + "    \"timestamp\": " + IntegerToString(TimeCurrent()) + ",\n";
    json_content = json_content + "    \"rows\": " + IntegerToString(MAINDB_ROWS) + ",\n";
    json_content = json_content + "    \"columns\": " + IntegerToString(MAINDB_COLUMNS) + ",\n";     // 10 columns
    json_content = json_content + "    \"data\": [\n";

    // Build data for each row
    for(int i = 1; i <= MAINDB_ROWS; i++) {
        if(i > 1) json_content = json_content + ",\n";
        json_content = json_content + "        " + RowToJsonObject(rows[i], i);
    }

    json_content = json_content + "\n    ],\n";

    // Add history_count metadata for each timeframe
    json_content = json_content + "    \"history_count\": {";
    json_content = json_content + "\"m1\": " + IntegerToString(g_symbol_data.m1_count);
    json_content = json_content + ", \"m5\": " + IntegerToString(g_symbol_data.m5_count);
    json_content = json_content + ", \"m15\": " + IntegerToString(g_symbol_data.m15_count);
    json_content = json_content + ", \"m30\": " + IntegerToString(g_symbol_data.m30_count);
    json_content = json_content + ", \"h1\": " + IntegerToString(g_symbol_data.h1_count);
    json_content = json_content + ", \"h4\": " + IntegerToString(g_symbol_data.h4_count);
    json_content = json_content + ", \"d1\": " + IntegerToString(g_symbol_data.d1_count);
    json_content = json_content + "},\n";

    // Add enhanced history section
    json_content = json_content + BuildEnhancedHistoryJson();

    json_content = json_content + "\n}";
    return json_content;
}


//==============================================================================
//    SECTION: CSDL2 FILE MANAGEMENT
//==============================================================================


int ExtractJsonInt(string json, string key) {
    int key_pos = StringFind(json, "\"" + key + "\":");
    if(key_pos < 0) return 0;

    int value_start = key_pos + StringLen("\"" + key + "\":");

    string value_str = "";
    for(int i = value_start; i < StringLen(json); i++) {
        ushort ch = StringGetCharacter(json, i);
        if(ch == '"' || ch == ',') break;
        if((ch >= '0' && ch <= '9') || ch == '-') {
            value_str = value_str + CharToString((uchar)ch);
        }
    }

    return (int)StringToInteger(value_str);
}

long ExtractJsonLong(string json, string key) {
    return (long)ExtractJsonInt(json, key);
}

double ExtractJsonDouble(string json, string key) {
    int key_pos = StringFind(json, "\"" + key + "\":");
    if(key_pos < 0) return 0.0;

    int value_start = key_pos + StringLen("\"" + key + "\":");

    string value_str = "";
    for(int i = value_start; i < StringLen(json); i++) {
        ushort ch = StringGetCharacter(json, i);
        if(ch == '"' || ch == ',') break;
        if((ch >= '0' && ch <= '9') || ch == '.' || ch == '-') {
            value_str = value_str + CharToString((uchar)ch);
        }
    }

    return StringToDouble(value_str);
}

// REMOVED: WriteCSDL2ToFile() and BuildCSDL2JsonContent() - CSDL2 not used


// Convert row string to JSON object
string RowToJsonObject(string row, int row_num) {
    string parts[];
    int part_count = StringSplit(row, ',', parts);

    // Ensure we have enough parts
    if(part_count < MAINDB_COLUMNS) {
        ArrayResize(parts, MAINDB_COLUMNS);
        for(int i = part_count; i < MAINDB_COLUMNS; i++) {
            parts[i] = "0";
        }
    }

    string timeframe_names[7] = {"M1", "M5", "M15", "M30", "H1", "H4", "D1"};
    int timeframe_periods[7] = {1, 5, 15, 30, 60, 240, 1440};

    // Output exactly 10 columns (with news_result and max_loss)
    string obj = "{";
    obj = obj + "\"timeframe_name\": \"" + timeframe_names[row_num-1] + "\", ";  // Column 1
    obj = obj + "\"timeframe\": " + IntegerToString(timeframe_periods[row_num-1]) + ", ";  // Column 2
    obj = obj + "\"signal\": " + parts[2] + ", ";                      // Column 3
    obj = obj + "\"price\": " + parts[3] + ", ";                       // Column 4
    obj = obj + "\"cross\": " + parts[4] + ", ";                       // Column 5
    obj = obj + "\"timestamp\": " + parts[5] + ", ";                   // Column 6
    obj = obj + "\"pricediff\": " + parts[6] + ", ";                   // Column 7
    obj = obj + "\"timediff\": " + parts[7] + ", ";                    // Column 8
    obj = obj + "\"news\": " + parts[8] + ", ";                        // Column 9
    obj = obj + "\"max_loss\": " + parts[9];                           // Column 10

    obj = obj + "}";
    return obj;
}

// Build enhanced history JSON (simplified)
string BuildEnhancedHistoryJson() {
    string history_json = "\"history\": {";

    // M1 history (7 signals) - WITH NEWLINES
    history_json = history_json + "\n    \"m1\": [";
    for(int i = 0; i < g_symbol_data.m1_count; i++) {
        if(i > 0) history_json = history_json + ",";
        history_json = history_json + "\n        {";
        history_json = history_json + "\"timeframe\": \"" + g_symbol_data.m1_history[i].timeframe_name + "\"";
        history_json = history_json + ", \"signal\": " + IntegerToString(g_symbol_data.m1_history[i].signal_3col);
        history_json = history_json + ", \"price\": " + DoubleToString(g_symbol_data.m1_history[i].price_4col, 5);
        history_json = history_json + ", \"cross\": " + IntegerToString(g_symbol_data.m1_history[i].cross_5col);
        history_json = history_json + ", \"timestamp\": " + IntegerToString(g_symbol_data.m1_history[i].timestamp_6col);
        history_json = history_json + ", \"pricediff\": " + DoubleToString(g_symbol_data.m1_history[i].pricediff_7col, 2);
        history_json = history_json + ", \"timediff\": " + IntegerToString(g_symbol_data.m1_history[i].timediff_8col);
        history_json = history_json + ", \"news\": " + IntegerToString(g_symbol_data.m1_history[i].news_result_9col);
        history_json = history_json + "\n        }";
    }
    history_json = history_json + "]";

    // M5 history
    history_json = history_json + ",\n    \"m5\": [";
    for(int i = 0; i < g_symbol_data.m5_count; i++) {
        if(i > 0) history_json = history_json + ",";
        history_json = history_json + "\n        {";
        history_json = history_json + "\"timeframe\": \"" + g_symbol_data.m5_history[i].timeframe_name + "\"";
        history_json = history_json + ", \"signal\": " + IntegerToString(g_symbol_data.m5_history[i].signal_3col);
        history_json = history_json + ", \"price\": " + DoubleToString(g_symbol_data.m5_history[i].price_4col, 5);
        history_json = history_json + ", \"cross\": " + IntegerToString(g_symbol_data.m5_history[i].cross_5col);
        history_json = history_json + ", \"timestamp\": " + IntegerToString(g_symbol_data.m5_history[i].timestamp_6col);
        history_json = history_json + ", \"pricediff\": " + DoubleToString(g_symbol_data.m5_history[i].pricediff_7col, 2);
        history_json = history_json + ", \"timediff\": " + IntegerToString(g_symbol_data.m5_history[i].timediff_8col);
        history_json = history_json + ", \"news\": " + IntegerToString(g_symbol_data.m5_history[i].news_result_9col);
        history_json = history_json + "\n        }";
    }
    history_json = history_json + "]";

    // M15 history
    history_json = history_json + ",\n    \"m15\": [";
    for(int i = 0; i < g_symbol_data.m15_count; i++) {
        if(i > 0) history_json = history_json + ",";
        history_json = history_json + "\n        {";
        history_json = history_json + "\"timeframe\": \"" + g_symbol_data.m15_history[i].timeframe_name + "\"";
        history_json = history_json + ", \"signal\": " + IntegerToString(g_symbol_data.m15_history[i].signal_3col);
        history_json = history_json + ", \"price\": " + DoubleToString(g_symbol_data.m15_history[i].price_4col, 5);
        history_json = history_json + ", \"cross\": " + IntegerToString(g_symbol_data.m15_history[i].cross_5col);
        history_json = history_json + ", \"timestamp\": " + IntegerToString(g_symbol_data.m15_history[i].timestamp_6col);
        history_json = history_json + ", \"pricediff\": " + DoubleToString(g_symbol_data.m15_history[i].pricediff_7col, 2);
        history_json = history_json + ", \"timediff\": " + IntegerToString(g_symbol_data.m15_history[i].timediff_8col);
        history_json = history_json + ", \"news\": " + IntegerToString(g_symbol_data.m15_history[i].news_result_9col);
        history_json = history_json + "\n        }";
    }
    history_json = history_json + "]";

    // M30 history
    history_json = history_json + ",\n    \"m30\": [";
    for(int i = 0; i < g_symbol_data.m30_count; i++) {
        if(i > 0) history_json = history_json + ",";
        history_json = history_json + "\n        {";
        history_json = history_json + "\"timeframe\": \"" + g_symbol_data.m30_history[i].timeframe_name + "\"";
        history_json = history_json + ", \"signal\": " + IntegerToString(g_symbol_data.m30_history[i].signal_3col);
        history_json = history_json + ", \"price\": " + DoubleToString(g_symbol_data.m30_history[i].price_4col, 5);
        history_json = history_json + ", \"cross\": " + IntegerToString(g_symbol_data.m30_history[i].cross_5col);
        history_json = history_json + ", \"timestamp\": " + IntegerToString(g_symbol_data.m30_history[i].timestamp_6col);
        history_json = history_json + ", \"pricediff\": " + DoubleToString(g_symbol_data.m30_history[i].pricediff_7col, 2);
        history_json = history_json + ", \"timediff\": " + IntegerToString(g_symbol_data.m30_history[i].timediff_8col);
        history_json = history_json + ", \"news\": " + IntegerToString(g_symbol_data.m30_history[i].news_result_9col);
        history_json = history_json + "\n        }";
    }
    history_json = history_json + "]";

    // H1 history
    history_json = history_json + ",\n    \"h1\": [";
    for(int i = 0; i < g_symbol_data.h1_count; i++) {
        if(i > 0) history_json = history_json + ",";
        history_json = history_json + "\n        {";
        history_json = history_json + "\"timeframe\": \"" + g_symbol_data.h1_history[i].timeframe_name + "\"";
        history_json = history_json + ", \"signal\": " + IntegerToString(g_symbol_data.h1_history[i].signal_3col);
        history_json = history_json + ", \"price\": " + DoubleToString(g_symbol_data.h1_history[i].price_4col, 5);
        history_json = history_json + ", \"cross\": " + IntegerToString(g_symbol_data.h1_history[i].cross_5col);
        history_json = history_json + ", \"timestamp\": " + IntegerToString(g_symbol_data.h1_history[i].timestamp_6col);
        history_json = history_json + ", \"pricediff\": " + DoubleToString(g_symbol_data.h1_history[i].pricediff_7col, 2);
        history_json = history_json + ", \"timediff\": " + IntegerToString(g_symbol_data.h1_history[i].timediff_8col);
        history_json = history_json + ", \"news\": " + IntegerToString(g_symbol_data.h1_history[i].news_result_9col);
        history_json = history_json + "\n        }";
    }
    history_json = history_json + "]";

    // H4 history
    history_json = history_json + ",\n    \"h4\": [";
    for(int i = 0; i < g_symbol_data.h4_count; i++) {
        if(i > 0) history_json = history_json + ",";
        history_json = history_json + "\n        {";
        history_json = history_json + "\"timeframe\": \"" + g_symbol_data.h4_history[i].timeframe_name + "\"";
        history_json = history_json + ", \"signal\": " + IntegerToString(g_symbol_data.h4_history[i].signal_3col);
        history_json = history_json + ", \"price\": " + DoubleToString(g_symbol_data.h4_history[i].price_4col, 5);
        history_json = history_json + ", \"cross\": " + IntegerToString(g_symbol_data.h4_history[i].cross_5col);
        history_json = history_json + ", \"timestamp\": " + IntegerToString(g_symbol_data.h4_history[i].timestamp_6col);
        history_json = history_json + ", \"pricediff\": " + DoubleToString(g_symbol_data.h4_history[i].pricediff_7col, 2);
        history_json = history_json + ", \"timediff\": " + IntegerToString(g_symbol_data.h4_history[i].timediff_8col);
        history_json = history_json + ", \"news\": " + IntegerToString(g_symbol_data.h4_history[i].news_result_9col);
        history_json = history_json + "\n        }";
    }
    history_json = history_json + "]";

    // D1 history - HÀNG 7 M?I THÊM
    history_json = history_json + ",\n    \"d1\": [";
    for(int i = 0; i < g_symbol_data.d1_count; i++) {
        if(i > 0) history_json = history_json + ",";
        history_json = history_json + "\n        {";
        history_json = history_json + "\"timeframe\": \"" + g_symbol_data.d1_history[i].timeframe_name + "\"";
        history_json = history_json + ", \"signal\": " + IntegerToString(g_symbol_data.d1_history[i].signal_3col);
        history_json = history_json + ", \"price\": " + DoubleToString(g_symbol_data.d1_history[i].price_4col, 5);
        history_json = history_json + ", \"cross\": " + IntegerToString(g_symbol_data.d1_history[i].cross_5col);
        history_json = history_json + ", \"timestamp\": " + IntegerToString(g_symbol_data.d1_history[i].timestamp_6col);
        history_json = history_json + ", \"pricediff\": " + DoubleToString(g_symbol_data.d1_history[i].pricediff_7col, 2);
        history_json = history_json + ", \"timediff\": " + IntegerToString(g_symbol_data.d1_history[i].timediff_8col);
        history_json = history_json + ", \"news\": " + IntegerToString(g_symbol_data.d1_history[i].news_result_9col);
        history_json = history_json + "\n        }";
    }
    history_json = history_json + "\n    ]";

    history_json = history_json + "\n}";
    return history_json;
}

//==============================================================================
//  SECTION 12.5: MONTHLY STATISTICS | PHAN 12.5: THONG KE THANG
//==============================================================================

// Monthly statistics structure | Cau truc thong ke thang
struct MonthlyStats {
    string symbol;           // Symbol name | Ten symbol
    int year;                // Year | Nam
    int month;               // Month (1-12) | Thang
    int total_trades;        // Total trades | Tong so lenh
    int winning_trades;      // Winning trades | Lenh thang
    int losing_trades;       // Losing trades | Lenh thua
    double total_profit;     // Total profit USD | Tong loi USD
    double total_loss;       // Total loss USD | Tong lo USD
    double net_profit;       // Net profit USD | Lai rong USD
    double win_rate;         // Win rate % | Ti le thang %
    double avg_win;          // Average win USD | Trung binh thang USD
    double avg_loss;         // Average loss USD | Trung binh thua USD
    double largest_win;      // Largest win USD | Thang lon nhat USD
    double largest_loss;     // Largest loss USD | Thua lon nhat USD
    double total_lots;       // Total lots traded | Tong khoi luong
};

// Calculate monthly statistics for previous month | Tinh thong ke thang truoc
MonthlyStats CalculateMonthlyStats(string target_symbol, int year, int month) {
    MonthlyStats stats;

    // Initialize
    stats.symbol = target_symbol;
    stats.year = year;
    stats.month = month;
    stats.total_trades = 0;
    stats.winning_trades = 0;
    stats.losing_trades = 0;
    stats.total_profit = 0.0;
    stats.total_loss = 0.0;
    stats.largest_win = 0.0;
    stats.largest_loss = 0.0;
    stats.total_lots = 0.0;

    // Calculate time range for target month
    datetime month_start = StrToTime(IntegerToString(year) + "." +
                                      StringFormat("%02d", month) + ".01 00:00:00");
    datetime month_end;

    if(month == 12) {
        month_end = StrToTime(IntegerToString(year + 1) + ".01.01 00:00:00");
    } else {
        month_end = StrToTime(IntegerToString(year) + "." +
                               StringFormat("%02d", month + 1) + ".01 00:00:00");
    }

    // Scan all history orders
    int total_history = OrdersHistoryTotal();

    for(int i = 0; i < total_history; i++) {
        if(!OrderSelect(i, SELECT_BY_POS, MODE_HISTORY)) continue;

        // Filter by symbol
        if(OrderSymbol() != target_symbol) continue;

        // Filter by close time (must be in target month)
        datetime close_time = OrderCloseTime();
        if(close_time < month_start || close_time >= month_end) continue;

        // Calculate net profit (profit + swap + commission)
        double net = OrderProfit() + OrderSwap() + OrderCommission();

        stats.total_trades++;
        stats.total_lots += OrderLots();

        if(net > 0) {
            stats.winning_trades++;
            stats.total_profit += net;
            if(net > stats.largest_win) stats.largest_win = net;
        } else {
            stats.losing_trades++;
            stats.total_loss += net;  // Negative value
            if(net < stats.largest_loss) stats.largest_loss = net;
        }
    }

    // Calculate derived statistics
    stats.net_profit = stats.total_profit + stats.total_loss;

    if(stats.total_trades > 0) {
        stats.win_rate = (double)stats.winning_trades / stats.total_trades * 100.0;
    }

    if(stats.winning_trades > 0) {
        stats.avg_win = stats.total_profit / stats.winning_trades;
    }

    if(stats.losing_trades > 0) {
        stats.avg_loss = stats.total_loss / stats.losing_trades;
    }

    return stats;
}

// Write monthly stats to JSON file | Ghi thong ke thang vao file JSON
bool WriteMonthlyStatsToFile(MonthlyStats& stats) {
    // Create HISTORY folder if not exists
    string history_folder = DataFolder + "HISTORY\\";

    // Build filename: SYMBOL_YYYY_MM.json
    string filename = history_folder + stats.symbol + "_" +
                      IntegerToString(stats.year) + "_" +
                      StringFormat("%02d", stats.month) + ".json";

    // Build JSON content - Summary section
    string json = "{\n";
    json += "  \"symbol\": \"" + stats.symbol + "\",\n";
    json += "  \"year\": " + IntegerToString(stats.year) + ",\n";
    json += "  \"month\": " + IntegerToString(stats.month) + ",\n";
    json += "  \"generated_time\": " + IntegerToString(TimeCurrent()) + ",\n";
    json += "  \"total_trades\": " + IntegerToString(stats.total_trades) + ",\n";
    json += "  \"winning_trades\": " + IntegerToString(stats.winning_trades) + ",\n";
    json += "  \"losing_trades\": " + IntegerToString(stats.losing_trades) + ",\n";
    json += "  \"total_profit\": " + DoubleToString(stats.total_profit, 2) + ",\n";
    json += "  \"total_loss\": " + DoubleToString(stats.total_loss, 2) + ",\n";
    json += "  \"net_profit\": " + DoubleToString(stats.net_profit, 2) + ",\n";
    json += "  \"win_rate\": " + DoubleToString(stats.win_rate, 2) + ",\n";
    json += "  \"avg_win\": " + DoubleToString(stats.avg_win, 2) + ",\n";
    json += "  \"avg_loss\": " + DoubleToString(stats.avg_loss, 2) + ",\n";
    json += "  \"largest_win\": " + DoubleToString(stats.largest_win, 2) + ",\n";
    json += "  \"largest_loss\": " + DoubleToString(stats.largest_loss, 2) + ",\n";
    json += "  \"total_lots\": " + DoubleToString(stats.total_lots, 2) + ",\n";

    // Build trades array
    json += "  \"trades\": [\n";

    // Calculate time range for target month
    datetime month_start = StrToTime(IntegerToString(stats.year) + "." +
                                      StringFormat("%02d", stats.month) + ".01 00:00:00");
    datetime month_end;
    if(stats.month == 12) {
        month_end = StrToTime(IntegerToString(stats.year + 1) + ".01.01 00:00:00");
    } else {
        month_end = StrToTime(IntegerToString(stats.year) + "." +
                               StringFormat("%02d", stats.month + 1) + ".01 00:00:00");
    }

    // Collect all trades for this month
    int total_history = OrdersHistoryTotal();
    int trade_count = 0;

    for(int i = 0; i < total_history; i++) {
        if(!OrderSelect(i, SELECT_BY_POS, MODE_HISTORY)) continue;

        // Filter by symbol
        if(OrderSymbol() != stats.symbol) continue;

        // Filter by close time (must be in target month)
        datetime close_time = OrderCloseTime();
        if(close_time < month_start || close_time >= month_end) continue;

        // Calculate net profit
        double net = OrderProfit() + OrderSwap() + OrderCommission();

        // Calculate duration
        datetime open_time = OrderOpenTime();
        int duration_seconds = (int)(close_time - open_time);
        int hours = duration_seconds / 3600;
        int minutes = (duration_seconds % 3600) / 60;
        string duration_str = IntegerToString(hours) + "h " + IntegerToString(minutes) + "m";

        // Order type
        string type_str = (OrderType() == OP_BUY) ? "BUY" : "SELL";

        // Add comma before each trade except first
        if(trade_count > 0) json += ",\n";

        // Build trade JSON object
        json += "    {\n";
        json += "      \"ticket\": " + IntegerToString(OrderTicket()) + ",\n";
        json += "      \"open_time\": \"" + TimeToString(open_time, TIME_DATE|TIME_MINUTES) + "\",\n";
        json += "      \"close_time\": \"" + TimeToString(close_time, TIME_DATE|TIME_MINUTES) + "\",\n";
        json += "      \"type\": \"" + type_str + "\",\n";
        json += "      \"lots\": " + DoubleToString(OrderLots(), 2) + ",\n";
        json += "      \"open_price\": " + DoubleToString(OrderOpenPrice(), 5) + ",\n";
        json += "      \"close_price\": " + DoubleToString(OrderClosePrice(), 5) + ",\n";
        json += "      \"profit\": " + DoubleToString(net, 2) + ",\n";
        json += "      \"duration\": \"" + duration_str + "\"\n";
        json += "    }";

        trade_count++;
    }

    json += "\n  ]\n";
    json += "}";

    // Write to file
    int handle = FileOpen(filename, FILE_WRITE|FILE_TXT);
    if(handle == INVALID_HANDLE) {
        Print("ERROR: Failed to create monthly stats file: ", filename);
        return false;
    }

    FileWriteString(handle, json);
    FileClose(handle);

    Print("Monthly stats saved: ", filename, " (", trade_count, " trades)");
    return true;
}

// Run monthly statistics on startup (if 1st day of month) | Chay thong ke thang khi khoi dong
void RunMonthlyStatsOnStartup() {
    if(!EnableMonthlyStats) return;

    datetime now = TimeCurrent();
    int current_day = TimeDay(now);

    // Only run on 1st day of month
    if(current_day != 1) return;

    // Calculate previous month
    int current_year = TimeYear(now);
    int current_month = TimeMonth(now);

    int target_year = current_year;
    int target_month = current_month - 1;

    if(target_month < 1) {
        target_month = 12;
        target_year = current_year - 1;
    }

    // Check if stats file already exists for this month
    string history_folder = DataFolder + "HISTORY\\";
    string filename = history_folder + g_target_symbol + "_" +
                      IntegerToString(target_year) + "_" +
                      StringFormat("%02d", target_month) + ".json";

    if(FileIsExist(filename)) {
        Print("Monthly stats already exists for ", target_year, "-",
              StringFormat("%02d", target_month), ": ", filename);
        return;
    }

    Print("-------------------------------------------------------");
    Print("   MONTHLY STATS - Calculating ", g_target_symbol, " ",
          target_year, "-", StringFormat("%02d", target_month));
    Print("-------------------------------------------------------");

    // Calculate statistics
    MonthlyStats stats = CalculateMonthlyStats(g_target_symbol, target_year, target_month);

    // Write to file
    WriteMonthlyStatsToFile(stats);

    // Print summary
    Print("Total Trades: ", stats.total_trades,
          " | Win: ", stats.winning_trades,
          " | Loss: ", stats.losing_trades);
    Print("Net Profit: $", DoubleToString(stats.net_profit, 2),
          " | Win Rate: ", DoubleToString(stats.win_rate, 2), "%");
    Print("-------------------------------------------------------");
}

//==============================================================================
//  SECTION 13: MAIN SYSTEM FUNCTIONS (7 functions) | PHAN 13: HAM HE THONG CHINH
//==============================================================================

// System initialization function | Ham khoi tao he thong
int OnInit() {
    // ============================================================
    // REFACTORED OnInit() - T?O FILE R?NG TR??C KHI CÓ TÍN HI?U
    // ============================================================

    // Step 1: Discover symbol from chart
    g_target_symbol = DiscoverSymbolFromChart();

    // Step 2: Initialize symbol data
    InitSymbolData(g_target_symbol);

    // Step 3: T?O 3 TH? M?C (n?u ch?a có)
    CreateFolderStructure();

    // Step 4: TẠO FILE CSDL1 A RỖNG (nếu chưa có) - TRƯỚC KHI CÓ TÍN HIỆU
    CreateEmptyCSDL1File();

    // Step 5: COPY FILE CSDL1 C từ A (nếu chưa có) - 1 LẦN DUY NHẤT
    CreateEmptyCSDL1FileC();

    // Step 6: TẠO FILE CSDL2 A, B, C RỖNG (nếu chưa có) - TRƯỚC KHI CÓ TÍN HIỆU
    CreateEmptyCSDL2Files();

    // Step 7: Load CSDL1 vào memory (file đã tồn tại rồi, có thể rỗng hoặc có data)
    LoadCSDL1FileIntoArray();

    // Step 7.1: Print history counts after loading
    Print("History Loaded: M1=", g_symbol_data.m1_count, " M5=", g_symbol_data.m5_count,
          " M15=", g_symbol_data.m15_count, " M30=", g_symbol_data.m30_count,
          " H1=", g_symbol_data.h1_count, " H4=", g_symbol_data.h4_count,
          " D1=", g_symbol_data.d1_count);

    // Step 7.2: Run monthly statistics (if 1st day of month)
    RunMonthlyStatsOnStartup();

    // Step 8: Set timer
    EventSetTimer(Timer);

    // Calculate pip and point values for display
    double pip_value = GetPipValue(g_target_symbol);
    double point_value = MarketInfo(g_target_symbol, MODE_POINT);
    if(point_value <= 0) point_value = Point;
    double usd_test = GetUSDValue(g_target_symbol, 1.0);

    // Single line professional initialization message
    Print("? [", g_target_symbol, "] SPY Init | CSDL1: OK | CSDL2: OK | 3 Folders: OK | USD:", DoubleToString(usd_test, 2), " pip:", DoubleToString(pip_value, 5), " pt:", DoubleToString(point_value, 5));

    // Dashboard will be shown by OnTimer() every second (không c?n g?i ? OnInit)

    // Mark system as initialized
    g_system_initialized = true;

    return INIT_SUCCEEDED;
}

// Timer event handler for periodic signal processing | Ham xu ly su kien timer cho xu ly tin hieu dinh ky
// ============================================================
// SECONDARY FUNCTIONS | CAC HAM PHU
// ============================================================

// Startup Reset: 1 minute after bot starts (1 TIME ONLY)
void RunStartupReset() {
    static string reset_executed;  // Kệ nó, không gán gì cả
    static datetime init_time;

    if(init_time == 0) {
        init_time = TimeCurrent();
    }

    // Điều kiện duy nhất: != "HAHA" thì làm reset, gán = "HAHA" để không bao giờ chạy lại
    if(reset_executed != "HAHA" && (TimeCurrent() - init_time >= 60)) {
        Print("-------------------------------------------------------");
        Print("   STARTUP RESET - 1 Minute After ", g_target_symbol, " Bot Started");
        Print("-------------------------------------------------------");
        SmartTFReset();
        reset_executed = "HAHA";  // Gán = "HAHA", bot khác không thể trùng
    }
}

// Midnight Reset & Health Check
void RunMidnightAndHealthCheck() {
    int current_hour = TimeHour(TimeCurrent());
    static int last_check_hour = -2;  // Init != -1 to allow first check

    // Midnight Reset: Only at 0h daily
    if(EnableMidnightReset && current_hour == 0 && current_hour != last_check_hour) {
        MidnightReset();
        last_check_hour = current_hour;
    }

    // Health Check: Only at 8h and 16h
    if(EnableHealthCheck &&
       (current_hour == 8 || current_hour == 16) &&
       current_hour != last_check_hour) {
        HealthCheck();
        last_check_hour = current_hour;
    }
}

// Dashboard Update
void RunDashboardUpdate() {
    static int dashboard_cycle = 0;
    dashboard_cycle++;

    if(dashboard_cycle % 5 == 0) {  // Moi 5 lan = 10 giay
        PrintDashboard();
    }
}

// Process All Signals (7 TF)
void ProcessAllSignals() {
    int timeframes[7] = {1, 5, 15, 30, 60, 240, 1440};
    string tf_names[7] = {"M1", "M5", "M15", "M30", "H1", "H4", "D1"};

    for(int i = 0; i < 7; i++) {
        // Check GlobalVariable from WallStreet
        string signal_var = g_target_symbol + "_" + tf_names[i] + "_SignalType1";
        string time_var = g_target_symbol + "_" + tf_names[i] + "_LastSignalTime";

        if(!GlobalVariableCheck(signal_var) || !GlobalVariableCheck(time_var)) continue;

        int current_signal = (int)GlobalVariableGet(signal_var);
        long current_signal_time = (long)GlobalVariableGet(time_var);

        // KIEM TRA: signal MOI != 0 && signal MOI != signal CU && time MOI > time CU
        if(current_signal != 0 &&
           current_signal != g_symbol_data.signals[i] &&
           current_signal_time > g_symbol_data.processed_timestamps[i]) {
            ProcessSignalForTF(i, current_signal, current_signal_time);
        }
    }
}

// ============================================================
// MAIN TIMER FUNCTION | HAM TIMER CHINH
// ============================================================

void OnTimer() {
    if(!g_system_initialized) return;

    int current_second = TimeSeconds(TimeCurrent());

    // ========================================
    // CHUC NANG CHINH: XU LY TIN HIEU 7 TF
    // ========================================
    if(ProcessSignalOnOddSecond) {
        // MODE: Xu ly GIAY LE (1, 3, 5, 7, 9...)
        if(current_second % 2 == 1) {
            ProcessAllSignals();  // Ghi CSDL1 (A,C) + CSDL2 (A,B,C)
        }
    } else {
        // MODE: Xu ly MOI GIAY (0, 1, 2, 3, 4...)
        ProcessAllSignals();  // Ghi CSDL1 (A,C) + CSDL2 (A,B,C)
    }

    // ========================================
    // CHUC NANG PHU: LUON CHAY GIAY CHAN
    // (KHONG LIEN QUAN MODE CHINH)
    // ========================================
    if(current_second % 2 == 0) {  // Giay chan (0, 2, 4, 6, 8...)
        RunStartupReset();
        RunMidnightAndHealthCheck();
        RunDashboardUpdate();
    }
}

// Check if chart window exists with specific symbol and timeframe | Kiem tra cua so bieu do ton tai voi symbol va khung thoi gian cu the
bool IsChartOpenWithSymbolAndTimeframe(string target_symbol, int target_timeframe) {
    long chart_id = ChartFirst();

    while(chart_id >= 0) {
        string chart_symbol = ChartSymbol(chart_id);
        int chart_period = ChartPeriod(chart_id);

        bool timeframe_match = false;

        if(target_timeframe == 240) {
            if(chart_period >= 240) {
                timeframe_match = true;
            }
        } else {
            if(chart_period == target_timeframe) {
                timeframe_match = true;
            }
        }

        if(chart_symbol == target_symbol && timeframe_match) {
            return true;
        }

        chart_id = ChartNext(chart_id);
    }

    return false;
}

// Convert period constant to timeframe string name | Chuyen hang so chu ky thanh ten chuoi khung thoi gian
string PeriodToString(int period) {
    switch(period) {
        case PERIOD_M1:  return "M1";
        case PERIOD_M5:  return "M5";
        case PERIOD_M15: return "M15";
        case PERIOD_M30: return "M30";
        case PERIOD_H1:  return "H1";
        case PERIOD_H4:  return "H4";
        case PERIOD_D1:  return "D1";
        default: return "Unknown";
    }
}

// Smart timeframe reset for all charts of current symbol | Reset thong minh khung thoi gian cho tat ca bieu do symbol hien tai
void SmartTFReset() {
    Print("-------------------------------------------------------");
    Print("   SMART TF RESET - Resetting All Bots...");
    Print("-------------------------------------------------------");

    // Get current chart info | Lay thong tin chart hien tai
    string current_symbol = Symbol();
    int current_period = Period();
    long current_chart_id = ChartID();

    // Step 1: Tim tat ca charts KHAC cua symbol nay (KHONG bao gom chart hien tai)
    int total_charts = 0;
    long chart_ids[];
    ArrayResize(chart_ids, 10);

    long temp_chart = ChartFirst();
    while(temp_chart >= 0) {
        if(ChartSymbol(temp_chart) == current_symbol && temp_chart != current_chart_id) {
            chart_ids[total_charts] = temp_chart;
            total_charts++;
        }
        temp_chart = ChartNext(temp_chart);
    }

    // Step 2: Reset 6 TF con lai TRUOC (W1 -> original TF, delay 1s)
    for(int i = 0; i < total_charts; i++) {
        int other_period = ChartPeriod(chart_ids[i]);
        Print("? Step ", (i+1), ": Reset TF ", PeriodToString(other_period), "...");

        ChartSetSymbolPeriod(chart_ids[i], current_symbol, PERIOD_W1);
        Sleep(1000);  // Delay 1s
        ChartSetSymbolPeriod(chart_ids[i], current_symbol, other_period);
        Sleep(1000);  // Delay 1s
    }

    // Step 3: Reset chart HIEN TAI CUOI CUNG (de nhan dien lai 6 TF con lai)
    Print("? Step ", (total_charts+1), ": Reset current chart ", PeriodToString(current_period), " (LAST)...");
    ChartSetSymbolPeriod(current_chart_id, current_symbol, PERIOD_W1);
    Sleep(1000);  // Delay 1s
    ChartSetSymbolPeriod(current_chart_id, current_symbol, current_period);
    Sleep(1000);  // Delay 1s

    Print("? Smart TF Reset COMPLETED - ", (total_charts + 1), " charts reset");
    Print("...........................................................");
}

// Health check for CSDL1 file activity (called at 8h and 16h) | Kiem tra hoat dong file CSDL1 (goi luc 8h va 16h)
void HealthCheck() {
    // Không c?n check EnableHealthCheck - ?ã check ? OnTimer()
    // Không c?n check th?i gian - ?ã check ? OnTimer()

    // Check CSDL1 file modification time | Kiem tra thoi gian sua doi file CSDL1
    string csdl1_file = DataFolder + g_target_symbol + ".json";

    int handle = FileOpen(csdl1_file, FILE_READ|FILE_TXT|FILE_SHARE_READ);
    if(handle == INVALID_HANDLE) {
        Print("!! Health Check: Cannot open CSDL1 file!");
        return;
    }

    datetime current_modified = (datetime)FileGetInteger(handle, FILE_MODIFY_DATE);
    FileClose(handle);

    // First run - just save timestamp | Lan dau - chi luu timestamp
    if(g_last_csdl1_modified == 0) {
        g_last_csdl1_modified = current_modified;
        Print("? Health Check: Initial timestamp saved");
        return;
    }

    // Check if file unchanged (bot stuck) | Kiem tra file khong doi (bot treo)
    if(current_modified == g_last_csdl1_modified) {
        Print("-------------------------------------------------------");
        Print("   HEALTH CHECK FAILED - Bot SPY Stuck!");
        Print("-------------------------------------------------------");
        Print("  CSDL1 file unchanged since last check!");
        Print("  Last modified: ", TimeToString(current_modified, TIME_DATE|TIME_MINUTES));
        Print("  Current check: ", TimeToString(TimeCurrent(), TIME_DATE|TIME_MINUTES));
        Print("  ? Triggering Smart TF Reset...");
        Print("...........................................................");

        Alert("?? Bot SPY stuck - Auto reset triggered!");
        SmartTFReset();

        // Update timestamp after reset | Cap nhat timestamp sau reset
        g_last_csdl1_modified = TimeCurrent();
    } else {
        Print("? Health Check: CSDL1 active (modified at ", TimeToString(current_modified, TIME_MINUTES), ")");
        g_last_csdl1_modified = current_modified;
    }
}

// Midnight reset at 0h daily with smart TF reset | Reset luc nua dem 0h hang ngay voi reset TF thong minh
void MidnightReset() {
    if(!EnableMidnightReset) return;

    static int last_day = 99;  // Init != -1 to prevent first-time trigger
    int current_day = TimeDay(TimeCurrent());

    // Check if new day (0h crossed) | Kiem tra neu sang ngay moi (qua 0h)
    if(current_day != last_day && TimeHour(TimeCurrent()) == 0) {
        Print("-------------------------------------------------------");
        Print("   MIDNIGHT RESET - ", g_target_symbol, " - New Day Started");
        Print("-------------------------------------------------------");

        SmartTFReset();
        last_day = current_day;
    }
}

// Legacy midnight reset function (deprecated but kept for compatibility) | Ham reset nua dem cu (khong dung nua nhung giu de tuong thich)
void ProcessMidnightReset() {
    datetime current_time = TimeCurrent();

    // Check if it's 00:00:00 (midnight) and we haven't reset today
    if(TimeHour(current_time) == 0 && TimeMinute(current_time) == 0 &&
       !g_midnight_switch_done_today) {

        g_chart_period_before_switch = Period();
        long chart_window = ChartGetInteger(ChartID(), CHART_WINDOW_HANDLE);
        PostMessageA(chart_window, WM_COMMAND, 33137, 0);
        Sleep(2000);  // 2 seconds - ICMarket server rest time at midnight

        int cmd = 0;
        if(g_chart_period_before_switch == PERIOD_M1) cmd = 33137;
        else if(g_chart_period_before_switch == PERIOD_M5) cmd = 33138;
        else if(g_chart_period_before_switch == PERIOD_M15) cmd = 33139;
        else if(g_chart_period_before_switch == PERIOD_M30) cmd = 33140;
        else if(g_chart_period_before_switch == PERIOD_H1) cmd = 33135;
        else if(g_chart_period_before_switch == PERIOD_H4) cmd = 33134;
        else if(g_chart_period_before_switch == PERIOD_D1) cmd = 33133;

        if(cmd > 0) PostMessageA(chart_window, WM_COMMAND, cmd, 0);

        g_midnight_switch_done_today = true;
        g_last_midnight_switch = current_time;

    }

    if(TimeHour(current_time) == 1 && g_midnight_switch_done_today) {
        g_midnight_switch_done_today = false;
    }
}

// Indicator calculation function (required but unused for this indicator) | Ham tinh toan chi bao (bat buoc nhung khong su dung cho chi bao nay)
int OnCalculate(const int rates_total,
                const int prev_calculated,
                const datetime &time[],
                const double &open[],
                const double &high[],
                const double &low[],
                const double &close[],
                const long &tick_volume[],
                const long &volume[],
                const int &spread[]) {
    // This indicator doesn't use OnCalculate, all logic is in OnTimer
    return rates_total;
}

// System cleanup function on indicator removal | Ham don dep he thong khi go bo chi bao
void OnDeinit(const int reason) {
    EventKillTimer();

    // Xóa 4 dashboard objects kh?i chart
    ObjectDelete(0, "SPY_Dashboard_Line1");
    ObjectDelete(0, "SPY_Dashboard_Line2");
    ObjectDelete(0, "SPY_Dashboard_Line3");
    ObjectDelete(0, "SPY_Dashboard_Line4");

    Print("? SUPER_Spy7TF_Oner V2 Deinitialized");
}