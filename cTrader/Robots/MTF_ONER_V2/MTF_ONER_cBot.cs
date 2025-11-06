//+------------------------------------------------------------------+
//| MTF_ONER_V2 cBot for cTrader
//| Multi Timeframe Trading Bot - 7 TF × 3 Strategies = 21 orders
//| Converted from MT5 EA to cTrader C#
//| Version: cTrader_V1 (Phase A1)
//+------------------------------------------------------------------+

using System;
using System.Linq;
using System.IO;
using System.Net.Http;
using System.Threading.Tasks;
using System.Collections.Generic;
using cAlgo.API;
using cAlgo.API.Indicators;
using cAlgo.API.Internals;
using Newtonsoft.Json;

namespace cAlgo.Robots
{
    [Robot(TimeZone = TimeZones.UTC, AccessRights = AccessRights.FullAccess)]
    public class MTF_ONER_cBot : Robot
    {
        #region ========== ENUMS (Converted from MQL5) ==========

        /// <summary>
        /// CSDL Source - where to fetch signal data from
        /// </summary>
        public enum CSDLSourceEnum
        {
            FOLDER_1 = 0,  // DataAutoOner (Botspy)
            FOLDER_2 = 1,  // DataAutoOner2 (_Default_Ea)
            FOLDER_3 = 2,  // DataAutoOner3 (_Sync/_Ea)
            HTTP_API = 3   // HTTP API (Remote VPS via Bot Python)
        }

        /// <summary>
        /// S2 Trend Mode - how to determine trend direction
        /// </summary>
        public enum S2TrendMode
        {
            FOLLOW_D1 = 0,    // Follow D1 (Auto)
            FORCE_BUY = 1,    // Force BUY (override=1)
            FORCE_SELL = -1   // Force SELL (override=-1)
        }

        /// <summary>
        /// Stoploss Mode - how to manage stoploss
        /// </summary>
        public enum StoplossMode
        {
            NONE = 0,            // No stoploss (close by signal only)
            LAYER1_MAXLOSS = 1,  // Layer1: max_loss × lot (from CSDL)
            LAYER2_MARGIN = 2    // Layer2: margin/divisor (emergency)
        }

        #endregion

        #region ========== DATA STRUCTURES (Converted from MQL5) ==========

        /// <summary>
        /// CSDL Row - single row of signal data from file/API
        /// Converted from MQL5 struct CSDLLoveRow
        /// </summary>
        public class CSDLRow
        {
            public double MaxLoss { get; set; }     // Col 1: Max loss per 1 LOT
            public long Timestamp { get; set; }     // Col 2: Unix timestamp
            public int Signal { get; set; }         // Col 3: Signal (1=BUY, -1=SELL, 0=NONE)
            public double PriceDiff { get; set; }   // Col 4: Price diff USD (unused)
            public int TimeDiff { get; set; }       // Col 5: Time diff minutes (unused)
            public int News { get; set; }           // Col 6: News CASCADE (±11-16)

            public CSDLRow()
            {
                MaxLoss = 0.0;
                Timestamp = 0;
                Signal = 0;
                PriceDiff = 0.0;
                TimeDiff = 0;
                News = 0;
            }
        }

        /// <summary>
        /// EA Symbol Data - all state for current symbol
        /// Converted from MQL5 struct EASymbolData
        /// </summary>
        public class EASymbolData
        {
            // Symbol & File info
            public string SymbolName { get; set; }
            public string NormalizedSymbolName { get; set; }
            public string SymbolPrefix { get; set; }
            public string CSDLFolder { get; set; }
            public string CSDLFilename { get; set; }

            // CSDL rows (7 rows for 7 timeframes)
            public CSDLRow[] CSDLRows { get; set; }

            // Core signals (old values for comparison)
            public int[] SignalOld { get; set; }
            public DateTime[] TimestampOld { get; set; }

            // Magic numbers [TF][Strategy]: [0]=S1, [1]=S2, [2]=S3
            // In cTrader, we use Labels instead of magic numbers
            public string[,] Labels { get; set; }

            // Lot sizes [TF][Strategy]: pre-calculated
            public double[,] LotSizes { get; set; }

            // Strategy conditions
            public int TrendD1 { get; set; }           // S2: D1 trend (1=BUY, -1=SELL, 0=NONE)
            public int[] NewsLevel { get; set; }       // S3: News level per TF (abs value)
            public int[] NewsDirection { get; set; }   // S3: News direction per TF (-1/0/1)

            // Stoploss thresholds [TF][Strategy]
            public double[,] Layer1Thresholds { get; set; }

            // Position flags [TF][Strategy]: track if position exists
            public int[,] PositionFlags { get; set; }

            // Global state vars
            public bool FirstRunCompleted { get; set; }
            public int WeekendLastDay { get; set; }
            public int HealthLastCheckHour { get; set; }
            public DateTime TimerLastRunTime { get; set; }
            public string InitSummary { get; set; }

            public EASymbolData()
            {
                SymbolName = "";
                NormalizedSymbolName = "";
                SymbolPrefix = "";
                CSDLFolder = "";
                CSDLFilename = "";

                CSDLRows = new CSDLRow[7];
                for (int i = 0; i < 7; i++)
                {
                    CSDLRows[i] = new CSDLRow();
                }

                SignalOld = new int[7];
                TimestampOld = new DateTime[7];

                Labels = new string[7, 3];
                LotSizes = new double[7, 3];

                TrendD1 = 0;
                NewsLevel = new int[7];
                NewsDirection = new int[7];

                Layer1Thresholds = new double[7, 3];
                PositionFlags = new int[7, 3];

                FirstRunCompleted = false;
                WeekendLastDay = 0;
                HealthLastCheckHour = 0;
                TimerLastRunTime = DateTime.MinValue;
                InitSummary = "";
            }
        }

        #endregion

        #region ========== PARAMETERS (Converted from MQL5 inputs) ==========

        // === A. CORE SETTINGS ===

        [Parameter("TF_M1", DefaultValue = false, Group = "A. CORE SETTINGS")]
        public bool TF_M1 { get; set; }

        [Parameter("TF_M5", DefaultValue = true, Group = "A. CORE SETTINGS")]
        public bool TF_M5 { get; set; }

        [Parameter("TF_M15", DefaultValue = true, Group = "A. CORE SETTINGS")]
        public bool TF_M15 { get; set; }

        [Parameter("TF_M30", DefaultValue = true, Group = "A. CORE SETTINGS")]
        public bool TF_M30 { get; set; }

        [Parameter("TF_H1", DefaultValue = true, Group = "A. CORE SETTINGS")]
        public bool TF_H1 { get; set; }

        [Parameter("TF_H4", DefaultValue = true, Group = "A. CORE SETTINGS")]
        public bool TF_H4 { get; set; }

        [Parameter("TF_D1", DefaultValue = false, Group = "A. CORE SETTINGS")]
        public bool TF_D1 { get; set; }

        [Parameter("S1_HOME", DefaultValue = true, Group = "A. CORE SETTINGS")]
        public bool S1_HOME { get; set; }

        [Parameter("S2_TREND", DefaultValue = true, Group = "A. CORE SETTINGS")]
        public bool S2_TREND { get; set; }

        [Parameter("S3_NEWS", DefaultValue = true, Group = "A. CORE SETTINGS")]
        public bool S3_NEWS { get; set; }

        [Parameter("S1_CloseByM1", DefaultValue = true, Group = "A. CORE SETTINGS")]
        public bool S1_CloseByM1 { get; set; }

        [Parameter("S2_CloseByM1", DefaultValue = false, Group = "A. CORE SETTINGS")]
        public bool S2_CloseByM1 { get; set; }

        [Parameter("FixedLotSize", DefaultValue = 0.1, MinValue = 0.01, Group = "A. CORE SETTINGS")]
        public double FixedLotSize { get; set; }

        [Parameter("MaxLoss_Fallback", DefaultValue = -1000.0, Group = "A. CORE SETTINGS")]
        public double MaxLoss_Fallback { get; set; }

        [Parameter("CSDL_Source", DefaultValue = CSDLSourceEnum.FOLDER_2, Group = "A. CORE SETTINGS")]
        public CSDLSourceEnum CSDL_Source { get; set; }

        // HTTP API settings
        [Parameter("HTTP_Server_IP", DefaultValue = "dungalading.duckdns.org", Group = "A. HTTP API")]
        public string HTTP_Server_IP { get; set; }

        [Parameter("HTTP_API_Key", DefaultValue = "", Group = "A. HTTP API")]
        public string HTTP_API_Key { get; set; }

        [Parameter("EnableSymbolNormalization", DefaultValue = true, Group = "A. HTTP API")]
        public bool EnableSymbolNormalization { get; set; }

        // === B. STRATEGY CONFIG ===

        [Parameter("S1_UseNewsFilter", DefaultValue = true, Group = "B. STRATEGY CONFIG")]
        public bool S1_UseNewsFilter { get; set; }

        [Parameter("MinNewsLevelS1", DefaultValue = 2, MinValue = 2, MaxValue = 70, Group = "B. STRATEGY CONFIG")]
        public int MinNewsLevelS1 { get; set; }

        [Parameter("S1_RequireNewsDirection", DefaultValue = true, Group = "B. STRATEGY CONFIG")]
        public bool S1_RequireNewsDirection { get; set; }

        [Parameter("S2_TrendMode", DefaultValue = S2TrendMode.FOLLOW_D1, Group = "B. STRATEGY CONFIG")]
        public S2TrendMode S2_TrendMode { get; set; }

        [Parameter("MinNewsLevelS3", DefaultValue = 20, MinValue = 2, MaxValue = 70, Group = "B. STRATEGY CONFIG")]
        public int MinNewsLevelS3 { get; set; }

        [Parameter("EnableBonusNews", DefaultValue = true, Group = "B. STRATEGY CONFIG")]
        public bool EnableBonusNews { get; set; }

        [Parameter("BonusOrderCount", DefaultValue = 1, MinValue = 1, MaxValue = 5, Group = "B. STRATEGY CONFIG")]
        public int BonusOrderCount { get; set; }

        [Parameter("MinNewsLevelBonus", DefaultValue = 2, MinValue = 2, MaxValue = 70, Group = "B. STRATEGY CONFIG")]
        public int MinNewsLevelBonus { get; set; }

        [Parameter("BonusLotMultiplier", DefaultValue = 1.2, MinValue = 1.0, MaxValue = 10.0, Group = "B. STRATEGY CONFIG")]
        public double BonusLotMultiplier { get; set; }

        // === C. RISK PROTECTION ===

        [Parameter("StoplossMode", DefaultValue = StoplossMode.LAYER1_MAXLOSS, Group = "C. RISK PROTECTION")]
        public StoplossMode StoplossMode { get; set; }

        [Parameter("Layer2_Divisor", DefaultValue = 5.0, Group = "C. RISK PROTECTION")]
        public double Layer2_Divisor { get; set; }

        [Parameter("UseTakeProfit", DefaultValue = false, Group = "C. RISK PROTECTION")]
        public bool UseTakeProfit { get; set; }

        [Parameter("TakeProfit_Multiplier", DefaultValue = 3.0, Group = "C. RISK PROTECTION")]
        public double TakeProfit_Multiplier { get; set; }

        // === D. AUXILIARY SETTINGS ===

        [Parameter("UseEvenOddMode", DefaultValue = true, Group = "D. AUXILIARY")]
        public bool UseEvenOddMode { get; set; }

        [Parameter("EnableWeekendReset", DefaultValue = false, Group = "D. AUXILIARY")]
        public bool EnableWeekendReset { get; set; }

        [Parameter("EnableHealthCheck", DefaultValue = false, Group = "D. AUXILIARY")]
        public bool EnableHealthCheck { get; set; }

        [Parameter("ShowDashboard", DefaultValue = true, Group = "D. AUXILIARY")]
        public bool ShowDashboard { get; set; }

        [Parameter("DebugMode", DefaultValue = false, Group = "D. AUXILIARY")]
        public bool DebugMode { get; set; }

        #endregion

        #region ========== CONSTANTS ==========

        // Timeframe names
        private readonly string[] TF_NAMES = { "M1", "M5", "M15", "M30", "H1", "H4", "D1" };

        // Strategy names
        private readonly string[] STRATEGY_NAMES = { "S1", "S2", "S3" };

        #endregion

        #region ========== PRIVATE FIELDS ==========

        // EA state data
        private EASymbolData _eaData;

        // HTTP client for API calls (reusable)
        private HttpClient _httpClient;

        #endregion

        #region ========== BOT LIFECYCLE METHODS ==========

        /// <summary>
        /// Called when bot starts - Initialize all components
        /// Equivalent to OnInit() in MT5
        /// </summary>
        protected override void OnStart()
        {
            Print("=== MTF_ONER_V2 cBot Starting ===");

            // Initialize EA data structure
            _eaData = new EASymbolData();

            // Setup symbol info
            InitializeSymbolInfo();

            // Setup HTTP client if needed
            if (CSDL_Source == CSDLSourceEnum.HTTP_API)
            {
                InitializeHttpClient();
            }

            // Setup magic numbers (in cTrader, we use Labels)
            InitializeLabels();

            // Setup lot sizes
            InitializeLotSizes();

            // Setup stoploss thresholds
            InitializeStoplossThresholds();

            // Initialize position flags
            InitializePositionFlags();

            // Print initialization summary
            PrintInitSummary();

            Print("=== MTF_ONER_V2 cBot Started Successfully ===");
        }

        /// <summary>
        /// Called on every tick - Main trading logic
        /// Equivalent to OnTick() in MT5
        /// </summary>
        protected override void OnTick()
        {
            // TODO: Implement main trading logic in Phase A2-A4
            // This will include:
            // 1. Read CSDL data (file or HTTP)
            // 2. Detect signal changes
            // 3. Execute S1, S2, S3 strategies
            // 4. Check stoploss and takeprofit
        }

        /// <summary>
        /// Called when bot stops - Cleanup resources
        /// Equivalent to OnDeinit() in MT5
        /// </summary>
        protected override void OnStop()
        {
            Print("=== MTF_ONER_V2 cBot Stopping ===");

            // Cleanup HTTP client
            if (_httpClient != null)
            {
                _httpClient.Dispose();
                _httpClient = null;
            }

            Print("=== MTF_ONER_V2 cBot Stopped ===");
        }

        #endregion

        #region ========== INITIALIZATION METHODS ==========

        /// <summary>
        /// Initialize symbol information
        /// </summary>
        private void InitializeSymbolInfo()
        {
            _eaData.SymbolName = SymbolName;

            // Normalize symbol name if enabled (e.g., LTCUSDC → LTCUSD)
            if (EnableSymbolNormalization)
            {
                _eaData.NormalizedSymbolName = NormalizeSymbolName(SymbolName);
            }
            else
            {
                _eaData.NormalizedSymbolName = SymbolName;
            }

            // Setup symbol prefix (e.g., "LTCUSD_")
            _eaData.SymbolPrefix = _eaData.NormalizedSymbolName + "_";

            // Setup CSDL folder path based on source
            switch (CSDL_Source)
            {
                case CSDLSourceEnum.FOLDER_1:
                    _eaData.CSDLFolder = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData), "MetaQuotes", "Terminal", "Common", "Files", "DataAutoOner");
                    break;
                case CSDLSourceEnum.FOLDER_2:
                    _eaData.CSDLFolder = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData), "MetaQuotes", "Terminal", "Common", "Files", "DataAutoOner2");
                    break;
                case CSDLSourceEnum.FOLDER_3:
                    _eaData.CSDLFolder = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData), "MetaQuotes", "Terminal", "Common", "Files", "DataAutoOner3");
                    break;
                case CSDLSourceEnum.HTTP_API:
                    _eaData.CSDLFolder = "HTTP_API";
                    break;
            }

            // Setup CSDL filename (e.g., "LTCUSD_CSDL.txt")
            _eaData.CSDLFilename = _eaData.NormalizedSymbolName + "_CSDL.txt";

            Print($"[INIT] Symbol: {_eaData.SymbolName} → Normalized: {_eaData.NormalizedSymbolName}");
            Print($"[INIT] CSDL: {_eaData.CSDLFolder}");
        }

        /// <summary>
        /// Initialize HTTP client for API calls
        /// </summary>
        private void InitializeHttpClient()
        {
            _httpClient = new HttpClient();
            _httpClient.Timeout = TimeSpan.FromMilliseconds(500);

            // Add default headers
            _httpClient.DefaultRequestHeaders.Add("User-Agent", "Mozilla/5.0 (compatible; cTrader/1.0)");
            _httpClient.DefaultRequestHeaders.Add("Host", HTTP_Server_IP);

            // Add API key if provided
            if (!string.IsNullOrEmpty(HTTP_API_Key))
            {
                _httpClient.DefaultRequestHeaders.Add("X-API-Key", HTTP_API_Key);
            }

            Print($"[INIT] HTTP Client initialized for {HTTP_Server_IP}");
        }

        /// <summary>
        /// Initialize position labels for tracking (replaces magic numbers)
        /// In cTrader, we use Label instead of Magic Number
        /// </summary>
        private void InitializeLabels()
        {
            for (int tf = 0; tf < 7; tf++)
            {
                for (int strategy = 0; strategy < 3; strategy++)
                {
                    // Format: "LTCUSD_M5_S1" (Symbol_Timeframe_Strategy)
                    _eaData.Labels[tf, strategy] = $"{_eaData.SymbolPrefix}{TF_NAMES[tf]}_{STRATEGY_NAMES[strategy]}";
                }
            }

            Print("[INIT] Position labels initialized (7 TF × 3 Strategies = 21 labels)");
        }

        /// <summary>
        /// Initialize lot sizes for all TF × Strategy combinations
        /// </summary>
        private void InitializeLotSizes()
        {
            for (int tf = 0; tf < 7; tf++)
            {
                for (int strategy = 0; strategy < 3; strategy++)
                {
                    // All strategies use the same fixed lot size
                    _eaData.LotSizes[tf, strategy] = Symbol.NormalizeVolumeInUnits(FixedLotSize * 100000); // Convert lots to units
                }
            }

            Print($"[INIT] Lot sizes initialized (Fixed: {FixedLotSize} lots)");
        }

        /// <summary>
        /// Initialize stoploss thresholds for Layer1 mode
        /// </summary>
        private void InitializeStoplossThresholds()
        {
            // Initialize with fallback value
            for (int tf = 0; tf < 7; tf++)
            {
                for (int strategy = 0; strategy < 3; strategy++)
                {
                    _eaData.Layer1Thresholds[tf, strategy] = MaxLoss_Fallback;
                }
            }

            Print($"[INIT] Stoploss thresholds initialized (Fallback: {MaxLoss_Fallback})");
        }

        /// <summary>
        /// Initialize position flags to 0 (no positions)
        /// </summary>
        private void InitializePositionFlags()
        {
            for (int tf = 0; tf < 7; tf++)
            {
                for (int strategy = 0; strategy < 3; strategy++)
                {
                    _eaData.PositionFlags[tf, strategy] = 0;
                }
            }

            Print("[INIT] Position flags initialized (all = 0)");
        }

        /// <summary>
        /// Print initialization summary
        /// </summary>
        private void PrintInitSummary()
        {
            int enabledTF = 0;
            if (TF_M1) enabledTF++;
            if (TF_M5) enabledTF++;
            if (TF_M15) enabledTF++;
            if (TF_M30) enabledTF++;
            if (TF_H1) enabledTF++;
            if (TF_H4) enabledTF++;
            if (TF_D1) enabledTF++;

            int enabledStrategies = 0;
            if (S1_HOME) enabledStrategies++;
            if (S2_TREND) enabledStrategies++;
            if (S3_NEWS) enabledStrategies++;

            Print($"[INIT] Enabled: {enabledTF} TF × {enabledStrategies} Strategies = {enabledTF * enabledStrategies} potential orders");
            Print($"[INIT] Stoploss: {StoplossMode}, TakeProfit: {(UseTakeProfit ? "ON" : "OFF")}");
            Print($"[INIT] CSDL Source: {CSDL_Source}");
        }

        #endregion

        #region ========== UTILITY METHODS ==========

        /// <summary>
        /// Normalize symbol name (e.g., LTCUSDC → LTCUSD, XAUUSD.xyz → XAUUSD)
        /// </summary>
        private string NormalizeSymbolName(string symbol)
        {
            // Remove suffixes after dot (e.g., XAUUSD.xyz → XAUUSD)
            int dotIndex = symbol.IndexOf('.');
            if (dotIndex > 0)
            {
                symbol = symbol.Substring(0, dotIndex);
            }

            // Remove trailing 'C' for crypto pairs (e.g., LTCUSDC → LTCUSD)
            if (symbol.EndsWith("C") && symbol.Length > 6)
            {
                symbol = symbol.Substring(0, symbol.Length - 1);
            }

            return symbol;
        }

        /// <summary>
        /// Check if timeframe is enabled by user
        /// </summary>
        private bool IsTFEnabled(int tfIndex)
        {
            switch (tfIndex)
            {
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

        /// <summary>
        /// Convert signal integer to readable string
        /// </summary>
        private string SignalToString(int signal)
        {
            if (signal == 1) return "BUY";
            if (signal == -1) return "SELL";
            return "NONE";
        }

        /// <summary>
        /// Debug print (only if DebugMode enabled)
        /// </summary>
        private void DebugPrint(string message)
        {
            if (DebugMode)
            {
                Print($"[DEBUG] {message}");
            }
        }

        #endregion

        #region ========== FILE READER (Phase A1 - Completed) ==========

        /// <summary>
        /// Read CSDL data from local file using System.IO
        /// Parses JSON file with 7 rows of signal data
        /// </summary>
        /// <returns>True if successful, false otherwise</returns>
        private bool ReadCSDLFromFile()
        {
            try
            {
                string fullPath = Path.Combine(_eaData.CSDLFolder, _eaData.CSDLFilename);

                DebugPrint($"[FILE] Reading: {fullPath}");

                // Check if file exists
                if (!File.Exists(fullPath))
                {
                    Print($"[FILE_ERROR] File not found: {fullPath}");
                    return false;
                }

                // Read entire file content
                string jsonContent = File.ReadAllText(fullPath);

                DebugPrint($"[FILE] Size: {jsonContent.Length} chars");

                // Parse JSON content
                if (!ParseCSDLJSON(jsonContent))
                {
                    Print("[FILE_ERROR] Failed to parse JSON");
                    return false;
                }

                DebugPrint("[FILE_OK] Successfully loaded CSDL from file");
                return true;
            }
            catch (Exception ex)
            {
                Print($"[FILE_ERROR] Exception: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Parse CSDL JSON content (array of 7 objects)
        /// Format: [{"max_loss":10.0,"timestamp":1234567890,"signal":1,"pricediff":0.0,"timediff":0,"news":15}, ...]
        /// </summary>
        private bool ParseCSDLJSON(string jsonContent)
        {
            try
            {
                // Parse as dynamic array using Newtonsoft.Json
                dynamic jsonArray = JsonConvert.DeserializeObject(jsonContent);

                if (jsonArray == null)
                {
                    Print("[JSON_ERROR] Failed to deserialize JSON");
                    return false;
                }

                int parsedCount = 0;

                // Parse each row (expect 7 rows for 7 timeframes)
                for (int i = 0; i < 7 && i < jsonArray.Count; i++)
                {
                    var row = jsonArray[i];

                    // Extract fields from JSON object
                    _eaData.CSDLRows[i].MaxLoss = (double)(row.max_loss ?? 0.0);
                    _eaData.CSDLRows[i].Timestamp = (long)(row.timestamp ?? 0);
                    _eaData.CSDLRows[i].Signal = (int)(row.signal ?? 0);
                    _eaData.CSDLRows[i].PriceDiff = (double)(row.pricediff ?? 0.0);
                    _eaData.CSDLRows[i].TimeDiff = (int)(row.timediff ?? 0);
                    _eaData.CSDLRows[i].News = (int)(row.news ?? 0);

                    parsedCount++;

                    DebugPrint($"[JSON] TF{i}: Signal={_eaData.CSDLRows[i].Signal}, News={_eaData.CSDLRows[i].News}, MaxLoss={_eaData.CSDLRows[i].MaxLoss}");
                }

                if (parsedCount < 1)
                {
                    Print("[JSON_ERROR] No rows parsed");
                    return false;
                }

                DebugPrint($"[JSON_OK] Parsed {parsedCount} rows");
                return true;
            }
            catch (Exception ex)
            {
                Print($"[JSON_ERROR] Exception: {ex.Message}");
                return false;
            }
        }

        #endregion

        #region ========== HTTP API CLIENT (Phase A1 - Completed) ==========

        /// <summary>
        /// Read CSDL data from HTTP API using HttpClient
        /// Makes async GET request to remote server
        /// </summary>
        /// <returns>True if successful, false otherwise</returns>
        private bool ReadCSDLFromAPI()
        {
            try
            {
                // Build URL: http://server/api/csdl/{symbol}_LIVE.json
                string url = $"http://{HTTP_Server_IP}/api/csdl/{_eaData.NormalizedSymbolName}_LIVE.json";

                DebugPrint($"[HTTP] Requesting: {url}");

                // Make synchronous HTTP GET request
                // Note: cTrader runs on UI thread, so we use .Result to block
                var response = _httpClient.GetAsync(url).Result;

                if (!response.IsSuccessStatusCode)
                {
                    Print($"[HTTP_ERROR] Status: {response.StatusCode}");
                    return false;
                }

                // Read response content
                string jsonContent = response.Content.ReadAsStringAsync().Result;

                DebugPrint($"[HTTP] Response size: {jsonContent.Length} chars");

                // Parse JSON content
                if (!ParseCSDLJSON(jsonContent))
                {
                    Print("[HTTP_ERROR] Failed to parse JSON response");
                    return false;
                }

                DebugPrint("[HTTP_OK] Successfully loaded CSDL from API");
                return true;
            }
            catch (Exception ex)
            {
                Print($"[HTTP_ERROR] Exception: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Read CSDL with smart routing (HTTP or Local file)
        /// Main entry point for reading signal data
        /// </summary>
        /// <returns>True if successful, false otherwise</returns>
        private bool ReadCSDL()
        {
            bool success = false;

            // Mode 1: HTTP API (Remote VPS)
            if (CSDL_Source == CSDLSourceEnum.HTTP_API)
            {
                // Try 1: Read from HTTP API
                success = ReadCSDLFromAPI();

                if (!success)
                {
                    // Try 2: Wait 100ms and retry HTTP
                    System.Threading.Thread.Sleep(100);
                    success = ReadCSDLFromAPI();
                }

                // No fallback to local file - if HTTP fails, something is seriously wrong
            }
            // Mode 2: Local File (FOLDER_1 / FOLDER_2 / FOLDER_3)
            else
            {
                // Try 1: Read main local file
                success = ReadCSDLFromFile();

                if (!success)
                {
                    // Try 2: Wait 100ms and retry file
                    System.Threading.Thread.Sleep(100);
                    success = ReadCSDLFromFile();
                }
            }

            return success;
        }

        #endregion

        #region ========== TODO: ORDER MANAGEMENT (Phase A2) ==========

        // TODO: Implement OrderSendSafe() - Open order with retry logic
        // TODO: Implement CloseOrderSafely() - Close order with retry logic
        // TODO: Implement position tracking using Positions collection

        #endregion

        #region ========== TODO: STRATEGY LOGIC (Phase A3) ==========

        // TODO: Implement S1 strategy (Binary/News)
        // TODO: Implement S2 strategy (Trend Following)
        // TODO: Implement S3 strategy (News + Bonus)
        // TODO: Implement signal change detection

        #endregion

        #region ========== TODO: RISK MANAGEMENT (Phase A4) ==========

        // TODO: Implement CheckStoplossAndTakeProfit()
        // TODO: Implement Layer1 stoploss
        // TODO: Implement Layer2 stoploss
        // TODO: Implement take profit logic

        #endregion
    }
}
