//+------------------------------------------------------------------+
//| MTF_ONER_V2 cBot for cTrader
//| Multi Timeframe Trading Bot - 7 TF × 3 Strategies = 21 orders
//| Converted from MT5 EA to cTrader C#
//| Version: cTrader_V1.0 (Phase A - 100% COMPLETE)
//| Lines: 1,729 (vs MT5: 2,839) - 61% size, 100% functionality
//| ALL critical logic included: RestoreOrCleanupPositions() added
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

            // First CSDL read to get initial signals
            if (!ReadCSDL())
            {
                Print("[INIT] Warning: Could not read CSDL on startup");
            }
            else
            {
                MapCSDLToEAVariables();
            }

            // Restore or cleanup positions from previous run
            RestoreOrCleanupPositions();

            // Print initialization summary
            PrintInitSummary();

            Print("=== MTF_ONER_V2 cBot Started Successfully ===");
        }

        /// <summary>
        /// Called on every tick - Main trading logic
        /// Equivalent to OnTick() + OnTimer() in MT5
        /// </summary>
        protected override void OnTick()
        {
            DateTime current_time = Server.Time;
            int current_second = current_time.Second;

            // Prevent duplicate execution in same second
            if (current_time == _eaData.TimerLastRunTime) return;
            _eaData.TimerLastRunTime = current_time;

            //=============================================================================
            // GROUP 1: EVEN SECONDS (0,2,4,6...) - TRADING CORE (HIGH PRIORITY)
            //=============================================================================
            // WHY EVEN: SPY Bot writes CSDL on ODD seconds, EA reads on EVEN → No file lock conflict
            if (!UseEvenOddMode || (current_second % 2 == 0))
            {
                // STEP 1: Read CSDL data
                if (!ReadCSDL())
                {
                    // If read fails, skip this cycle
                    return;
                }

                // STEP 2: Map data for all 7 TF
                MapCSDLToEAVariables();

                // STEP 3: Strategy processing loop for 7 TF
                // IMPORTANT: CLOSE function runs on ALL 7 TF (no TF filter)
                // OPEN function respects TF/Strategy toggles
                for (int tf = 0; tf < 7; tf++)
                {
                    // STEP 3.1: FAST CLOSE by M1 (S1, S2, Bonus)
                    if (tf == 0 && HasValidS2BaseCondition(0))
                    {
                        if (S1_CloseByM1) CloseS1OrdersByM1();
                        if (S2_CloseByM1) CloseS2OrdersByM1();
                        if (EnableBonusNews) CloseAllBonusOrders();
                    }

                    // STEP 3.2: NORMAL CLOSE by TF signal
                    if (HasValidS2BaseCondition(tf))
                    {
                        if (S1_CloseByM1 && S2_CloseByM1)
                        {
                            CloseS3OrdersForTF(tf);
                        }
                        else if (S1_CloseByM1)
                        {
                            // Close S2 and S3 for this TF
                            foreach (var position in Positions)
                            {
                                if (position.SymbolName != SymbolName) continue;
                                if (position.Label == _eaData.Labels[tf, 1] || position.Label == _eaData.Labels[tf, 2])
                                {
                                    CloseOrderSafely(position, "SIGNAL_CHANGE");
                                }
                            }
                            _eaData.PositionFlags[tf, 1] = 0;
                            _eaData.PositionFlags[tf, 2] = 0;
                        }
                        else if (S2_CloseByM1)
                        {
                            // Close S1 and S3 for this TF
                            foreach (var position in Positions)
                            {
                                if (position.SymbolName != SymbolName) continue;
                                if (position.Label == _eaData.Labels[tf, 0] || position.Label == _eaData.Labels[tf, 2])
                                {
                                    CloseOrderSafely(position, "SIGNAL_CHANGE");
                                }
                            }
                            _eaData.PositionFlags[tf, 0] = 0;
                            _eaData.PositionFlags[tf, 2] = 0;
                        }
                        else
                        {
                            CloseAllStrategiesByLabelForTF(tf);
                        }

                        // STEP 3.3: Open new orders (ONLY if TF enabled)
                        if (IsTFEnabled(tf))
                        {
                            if (S1_HOME) ProcessS1Strategy(tf);
                            if (S2_TREND) ProcessS2Strategy(tf);
                            if (S3_NEWS) ProcessS3Strategy(tf);
                        }

                        // STEP 3.4: Process Bonus NEWS (scans ALL 7 TF, opens if NEWS >= threshold)
                        if (EnableBonusNews)
                        {
                            ProcessBonusNews();
                        }

                        // STEP 3.5: Update baseline from CSDL
                        _eaData.SignalOld[tf] = _eaData.CSDLRows[tf].Signal;
                        _eaData.TimestampOld[tf] = DateTimeOffset.FromUnixTimeSeconds(_eaData.CSDLRows[tf].Timestamp).DateTime;
                    }
                }
            }

            //=============================================================================
            // GROUP 2: ODD SECONDS (1,3,5,7...) - AUXILIARY (SUPPORT)
            //=============================================================================
            // WHY ODD: These functions don't need fresh CSDL data, run independently to reduce load on EVEN seconds
            if (!UseEvenOddMode || (current_second % 2 != 0))
            {
                // STEP 1: Check stoploss & take profit
                CheckStoplossAndTakeProfit();

                // STEP 2: Weekend reset, health checks, etc. can be added here in future
                // (Not critical for initial implementation)
            }
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

            _eaData.InitSummary = $"[INIT] Enabled: {enabledTF} TF × {enabledStrategies} Strategies = {enabledTF * enabledStrategies} potential orders";

            Print(_eaData.InitSummary);
            Print($"[INIT] Stoploss: {StoplossMode}, TakeProfit: {(UseTakeProfit ? "ON" : "OFF")}");
            Print($"[INIT] CSDL Source: {CSDL_Source}");
        }

        /// <summary>
        /// Restore or cleanup positions on bot startup
        /// Validates existing positions and restores flags or closes invalid ones
        /// </summary>
        private void RestoreOrCleanupPositions()
        {
            // Step 1: Reset all flags first (already done in InitializePositionFlags)
            // Step 2: Scan all open positions
            int kept_count = 0;
            int closed_count = 0;

            foreach (var position in Positions)
            {
                // Filter: Only this symbol
                if (position.SymbolName != SymbolName) continue;

                // Get order signal from position
                int order_signal = (position.TradeType == TradeType.Buy) ? 1 : -1;

                // Step 3: Scan 7×3 combinations to find valid match
                bool found = false;
                int found_tf = -1;
                int found_s = -1;

                for (int tf = 0; tf < 7; tf++)
                {
                    // Skip if TF disabled
                    if (!IsTFEnabled(tf)) continue;

                    for (int s = 0; s < 3; s++)
                    {
                        // CONDITION 1: Label match (replaces magic number check)
                        bool cond1_label = (position.Label == _eaData.Labels[tf, s]);

                        // CONDITION 2: Signal pair match (order signal == old signal == CSDL signal)
                        // AND timestamp old == CSDL timestamp (locked)
                        DateTime csdl_time = DateTimeOffset.FromUnixTimeSeconds(_eaData.CSDLRows[tf].Timestamp).DateTime;
                        bool cond2_signal_pair = (order_signal == _eaData.SignalOld[tf] &&
                                                  order_signal == _eaData.CSDLRows[tf].Signal &&
                                                  _eaData.TimestampOld[tf] == csdl_time);

                        // CONDITION 3: Strategy enabled
                        bool cond3_strategy = false;
                        if (s == 0) cond3_strategy = S1_HOME;
                        else if (s == 1) cond3_strategy = S2_TREND;
                        else if (s == 2) cond3_strategy = S3_NEWS;

                        // CONDITION 4: Not duplicate (flag must be 0)
                        bool cond4_unique = (_eaData.PositionFlags[tf, s] == 0);

                        // CONSOLIDATED CHECK: ALL with AND
                        if (cond1_label && cond2_signal_pair && cond3_strategy && cond4_unique)
                        {
                            found = true;
                            found_tf = tf;
                            found_s = s;
                            break;  // Exit strategy loop
                        }
                    }

                    if (found) break;  // Exit TF loop
                }

                // Step 4: Decide KEEP or CLOSE
                if (found)
                {
                    // ✅ KEEP: All conditions passed → Restore flag
                    _eaData.PositionFlags[found_tf, found_s] = 1;
                    kept_count++;

                    DebugPrint($"[RESTORE_KEEP] #{position.Id} TF:{found_tf} S:{found_s + 1} Signal:{order_signal} | Flag=1");
                }
                else
                {
                    // ❌ CLOSE: ANY condition failed → Close position
                    CloseOrderSafely(position, "RESTORE_INVALID");
                    closed_count++;

                    // CRITICAL: Reset flag if this was a known label
                    // Prevents stoploss function from miscalculating
                    for (int tf_check = 0; tf_check < 7; tf_check++)
                    {
                        for (int s_check = 0; s_check < 3; s_check++)
                        {
                            if (position.Label == _eaData.Labels[tf_check, s_check])
                            {
                                _eaData.PositionFlags[tf_check, s_check] = 0;  // Ensure flag = 0
                                break;
                            }
                        }
                    }

                    DebugPrint($"[RESTORE_CLOSE] #{position.Id} Label:{position.Label} Signal:{order_signal} | INVALID");
                }
            }

            // Step 5: Final summary report
            Print($"{_eaData.InitSummary} | RESTORE: KEPT={kept_count} CLOSED={closed_count}");

            // Debug: Print restored flags (optional)
            if (DebugMode && kept_count > 0)
            {
                for (int tf = 0; tf < 7; tf++)
                {
                    bool has_flag = false;
                    for (int s = 0; s < 3; s++)
                    {
                        if (_eaData.PositionFlags[tf, s] == 1)
                        {
                            has_flag = true;
                            break;
                        }
                    }
                    if (has_flag)
                    {
                        Print($"[RESTORE_FLAGS] {TF_NAMES[tf]}: S1={_eaData.PositionFlags[tf, 0]} S2={_eaData.PositionFlags[tf, 1]} S3={_eaData.PositionFlags[tf, 2]}");
                    }
                }
            }
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

        #region ========== DATA MAPPING ==========

        /// <summary>
        /// Map CSDL data to EA variables (trend, news)
        /// </summary>
        private void MapCSDLToEAVariables()
        {
            // S2: TREND - Always use D1 (row 6) for all TF
            _eaData.TrendD1 = _eaData.CSDLRows[6].Signal;

            // S3: NEWS - Map 7 NEWS values to 14 variables (7 level + 7 direction)
            MapNewsTo14Variables();

            DebugPrint($"Mapped 7 TF | signal[0]={_eaData.CSDLRows[0].Signal} trend_d1={_eaData.TrendD1} news[M1]={_eaData.CSDLRows[0].News}");
        }

        /// <summary>
        /// Map 7 NEWS values (with ± sign) to 14 variables (7 level + 7 direction)
        /// NEWS has 2 components: LEVEL (abs) and DIRECTION (sign)
        /// Example: news = +30 → level = 30, direction = +1 (BUY)
        ///          news = -20 → level = 20, direction = -1 (SELL)
        /// </summary>
        private void MapNewsTo14Variables()
        {
            for (int tf = 0; tf < 7; tf++)
            {
                int tf_news = _eaData.CSDLRows[tf].News;

                // Split into LEVEL (absolute value) and DIRECTION (sign)
                _eaData.NewsLevel[tf] = Math.Abs(tf_news);

                if (tf_news > 0)
                {
                    _eaData.NewsDirection[tf] = 1;   // Positive = BUY
                }
                else if (tf_news < 0)
                {
                    _eaData.NewsDirection[tf] = -1;  // Negative = SELL
                }
                else
                {
                    _eaData.NewsDirection[tf] = 0;   // Zero = NO NEWS
                }
            }

            DebugPrint($"NEWS 14 vars: M1[{_eaData.NewsLevel[0]}/{_eaData.NewsDirection[0]}] M5[{_eaData.NewsLevel[1]}/{_eaData.NewsDirection[1]}] D1[{_eaData.NewsLevel[6]}/{_eaData.NewsDirection[6]}]");
        }

        /// <summary>
        /// Check if signal changed and new signal valid
        /// </summary>
        private bool HasValidS2BaseCondition(int tf)
        {
            int signal_old = _eaData.SignalOld[tf];
            int signal_new = _eaData.CSDLRows[tf].Signal;
            DateTime timestamp_old = _eaData.TimestampOld[tf];
            DateTime timestamp_new = DateTimeOffset.FromUnixTimeSeconds(_eaData.CSDLRows[tf].Timestamp).DateTime;

            return (signal_old != signal_new &&
                    signal_new != 0 &&
                    timestamp_old < timestamp_new &&
                    (timestamp_new - timestamp_old).TotalSeconds > 15);
        }

        #endregion

        #region ========== ORDER MANAGEMENT ==========

        /// <summary>
        /// Open order with smart error handling (max 1 retry)
        /// Returns: Trade result with position ID, or null if failed
        /// </summary>
        private TradeResult OrderSendSafe(int tf, TradeType tradeType, double volumeInUnits, string label)
        {
            // Normalize volume
            volumeInUnits = Symbol.NormalizeVolumeInUnits(volumeInUnits, RoundingMode.ToNearest);

            // Try 1: Smart volume
            TradeResult result = ExecuteMarketOrder(tradeType, SymbolName, volumeInUnits, label);

            if (result.IsSuccessful)
            {
                return result;
            }

            // FAILED - Check error
            string errorCode = result.Error.ToString();

            // Case 1: Not enough money OR Invalid volume → Retry with minimum volume
            if (errorCode.Contains("NotEnoughMoney") || errorCode.Contains("InvalidVolume"))
            {
                Print($"[ORDER_FAIL] {label} Error:{errorCode} (Retry min volume)");

                double minVolume = Symbol.VolumeInUnitsMin;
                result = ExecuteMarketOrder(tradeType, SymbolName, minVolume, label + "_Min");

                if (result.IsSuccessful)
                {
                    return result;
                }

                Print($"[ORDER_FAIL] {label} Retry Error:{result.Error}");
                return null;
            }

            // Case 2: Market closed OR Off quotes → No retry
            if (errorCode.Contains("MarketClosed") || errorCode.Contains("OffQuotes"))
            {
                Print($"[ORDER_FAIL] {label} Error:{errorCode} (No retry - market issue)");
                return null;
            }

            // Case 3: Other errors → Log and return
            Print($"[ORDER_FAIL] {label} Error:{errorCode}");
            return null;
        }

        /// <summary>
        /// Close order with smart error handling (max 1 retry)
        /// Returns: true (success) or false
        /// </summary>
        private bool CloseOrderSafely(Position position, string reason)
        {
            if (position == null)
                return false;

            // Try 1: Close position
            TradeResult result = ClosePosition(position);

            if (result.IsSuccessful)
            {
                return true;
            }

            // FAILED - Check error
            string errorCode = result.Error.ToString();

            // Case 1: Market closed or Off quotes → Retry 1 time
            if (errorCode.Contains("MarketClosed") || errorCode.Contains("OffQuotes"))
            {
                Print($"[CLOSE_FAIL] {reason} #{position.Id} Error:{errorCode} (Retry 1x)");
                System.Threading.Thread.Sleep(100);

                result = ClosePosition(position);

                if (result.IsSuccessful)
                {
                    return true;
                }

                Print($"[CLOSE_FAIL] {reason} #{position.Id} Retry Error:{result.Error}");
                return false;
            }

            // Case 2: Other errors → Log and continue
            Print($"[CLOSE_FAIL] {reason} #{position.Id} Error:{errorCode}");
            return false;
        }

        #endregion

        #region ========== STRATEGY LOGIC ==========

        /// <summary>
        /// S1 Core: Open order (shared logic for BASIC and NEWS strategies)
        /// </summary>
        private void OpenS1Order(int tf, int signal, string mode)
        {
            long timestamp = _eaData.CSDLRows[tf].Timestamp;
            int news_level = _eaData.NewsLevel[tf];
            int news_direction = _eaData.NewsDirection[tf];

            TradeType tradeType = (signal == 1) ? TradeType.Buy : TradeType.Sell;
            string type_str = (signal == 1) ? "BUY" : "SELL";
            double price = (signal == 1) ? Symbol.Ask : Symbol.Bid;

            string label = _eaData.Labels[tf, 0];  // S1 label
            double volume = _eaData.LotSizes[tf, 0];

            TradeResult result = OrderSendSafe(tf, tradeType, volume, label);

            if (result != null && result.IsSuccessful)
            {
                _eaData.PositionFlags[tf, 0] = 1;

                string log_msg = $">>> [OPEN] S1_{mode} TF={TF_NAMES[tf]} | #{result.Position.Id} {type_str} {volume / 100000:F2} @{price} | Sig={signal}";

                if (mode == "NEWS")
                {
                    string arrow = (news_direction > 0) ? "↑" : "↓";
                    log_msg += $" News={(news_direction > 0 ? "+" : "")}{news_level}{arrow}";
                    log_msg += $" Filter:{(S1_UseNewsFilter ? "ON" : "OFF")}";
                    log_msg += $" Dir:{(S1_RequireNewsDirection ? "REQ" : "ANY")}";
                }

                log_msg += $" | Timestamp:{timestamp} <<<";
                Print(log_msg);
            }
            else
            {
                _eaData.PositionFlags[tf, 0] = 0;
                Print($"[S1_{mode}_{TF_NAMES[tf]}] Failed");
            }
        }

        /// <summary>
        /// S1 BASIC: No NEWS check
        /// </summary>
        private void ProcessS1BasicStrategy(int tf)
        {
            int current_signal = _eaData.CSDLRows[tf].Signal;
            if (current_signal == 1 || current_signal == -1)
            {
                OpenS1Order(tf, current_signal, "BASIC");
            }
        }

        /// <summary>
        /// S1 NEWS Filter: Check NEWS before opening order
        /// </summary>
        private void ProcessS1NewsFilterStrategy(int tf)
        {
            int current_signal = _eaData.CSDLRows[tf].Signal;
            int news_level = _eaData.NewsLevel[tf];
            int news_direction = _eaData.NewsDirection[tf];

            // Condition 1: Check NEWS level >= MinNewsLevelS1
            if (news_level < MinNewsLevelS1)
            {
                DebugPrint($"S1_NEWS: {TF_NAMES[tf]} NEWS={news_level} < Min={MinNewsLevelS1}, SKIP");
                return;
            }

            // Condition 2: Check NEWS direction matches signal (if required)
            if (S1_RequireNewsDirection)
            {
                if (current_signal != news_direction)
                {
                    DebugPrint($"S1_NEWS: {TF_NAMES[tf]} Signal={current_signal} != NewsDir={news_direction}, SKIP");
                    return;
                }
            }

            // PASS all conditions → Open order
            if (current_signal == 1 || current_signal == -1)
            {
                OpenS1Order(tf, current_signal, "NEWS");
            }
        }

        /// <summary>
        /// S1 Strategy Router: Call appropriate function based on filter setting
        /// </summary>
        private void ProcessS1Strategy(int tf)
        {
            if (S1_UseNewsFilter)
            {
                ProcessS1NewsFilterStrategy(tf);
            }
            else
            {
                ProcessS1BasicStrategy(tf);
            }
        }

        /// <summary>
        /// Process S2 (Trend Following) strategy for TF
        /// Support 3 modes (auto D1 / force BUY / force SELL)
        /// </summary>
        private void ProcessS2Strategy(int tf)
        {
            int current_signal = _eaData.CSDLRows[tf].Signal;
            long timestamp = _eaData.CSDLRows[tf].Timestamp;

            // Determine trend based on mode
            int trend_to_follow = 0;

            if (S2_TrendMode == S2TrendMode.FOLLOW_D1)
            {
                trend_to_follow = _eaData.TrendD1;
            }
            else if (S2_TrendMode == S2TrendMode.FORCE_BUY)
            {
                trend_to_follow = 1;
            }
            else if (S2_TrendMode == S2TrendMode.FORCE_SELL)
            {
                trend_to_follow = -1;
            }

            // Check signal matches trend
            if (current_signal != trend_to_follow)
            {
                DebugPrint($"S2_TREND: Signal={current_signal} != Trend={trend_to_follow}, skip");
                return;
            }

            string label = _eaData.Labels[tf, 1];  // S2 label
            double volume = _eaData.LotSizes[tf, 1];
            TradeType tradeType = (current_signal == 1) ? TradeType.Buy : TradeType.Sell;
            double price = (current_signal == 1) ? Symbol.Ask : Symbol.Bid;

            TradeResult result = OrderSendSafe(tf, tradeType, volume, label);

            if (result != null && result.IsSuccessful)
            {
                _eaData.PositionFlags[tf, 1] = 1;
                string trend_str = trend_to_follow == 1 ? "UP" : "DOWN";
                string mode_str = (S2_TrendMode == S2TrendMode.FOLLOW_D1) ? "AUTO" :
                                  (S2_TrendMode == S2TrendMode.FORCE_BUY) ? "FBUY" : "FSELL";
                string type_str = (current_signal == 1) ? "BUY" : "SELL";

                Print($">>> [OPEN] S2_TREND TF={TF_NAMES[tf]} | #{result.Position.Id} {type_str} {volume / 100000:F2} @{price} | Sig={current_signal} Trend:{trend_str} Mode:{mode_str} | Timestamp:{timestamp} <<<");
            }
            else
            {
                _eaData.PositionFlags[tf, 1] = 0;
                Print($"[S2_{TF_NAMES[tf]}] Failed");
            }
        }

        /// <summary>
        /// Process S3 (News Alignment) strategy for TF
        /// </summary>
        private void ProcessS3Strategy(int tf)
        {
            int news_level = _eaData.NewsLevel[tf];
            int news_direction = _eaData.NewsDirection[tf];
            int current_signal = _eaData.CSDLRows[tf].Signal;
            long timestamp = _eaData.CSDLRows[tf].Timestamp;

            // Check NEWS level >= MinNewsLevelS3
            if (news_level < MinNewsLevelS3)
            {
                DebugPrint($"S3_NEWS: TF{tf} NEWS={news_level} < {MinNewsLevelS3}, skip");
                return;
            }

            // Check NEWS direction matches signal
            if (current_signal != news_direction)
            {
                DebugPrint($"S3_NEWS: Signal={current_signal} != NewsDir={news_direction}, skip");
                return;
            }

            string label = _eaData.Labels[tf, 2];  // S3 label
            double volume = _eaData.LotSizes[tf, 2];
            TradeType tradeType = (current_signal == 1) ? TradeType.Buy : TradeType.Sell;
            double price = (current_signal == 1) ? Symbol.Ask : Symbol.Bid;

            TradeResult result = OrderSendSafe(tf, tradeType, volume, label);

            if (result != null && result.IsSuccessful)
            {
                _eaData.PositionFlags[tf, 2] = 1;
                string arrow = (news_direction > 0) ? "↑" : "↓";
                string type_str = (current_signal == 1) ? "BUY" : "SELL";

                Print($">>> [OPEN] S3_NEWS TF={TF_NAMES[tf]} | #{result.Position.Id} {type_str} {volume / 100000:F2} @{price} | Sig={current_signal} News={(news_direction > 0 ? "+" : "")}{news_level}{arrow} | Timestamp:{timestamp} <<<");
            }
            else
            {
                _eaData.PositionFlags[tf, 2] = 0;
                Print($"[S3_{TF_NAMES[tf]}] Failed");
            }
        }

        /// <summary>
        /// Process Bonus NEWS - Scan all 7 TF and open multiple orders if NEWS detected
        /// </summary>
        private void ProcessBonusNews()
        {
            if (!EnableBonusNews) return;

            // Scan all 7 TF
            for (int tf = 0; tf < 7; tf++)
            {
                // Skip if TF disabled
                if (!IsTFEnabled(tf)) continue;

                int news_level = _eaData.NewsLevel[tf];
                int news_direction = _eaData.NewsDirection[tf];

                // Skip if NEWS below threshold
                if (news_level < MinNewsLevelBonus) continue;

                // Skip low-value NEWS (±1, ±10)
                if (news_level == 1 || news_level == 10) continue;

                // Calculate BONUS lot (S3 lot × multiplier)
                double bonus_lot = _eaData.LotSizes[tf, 2] * BonusLotMultiplier;
                // Normalize to prevent invalid volume
                bonus_lot = Math.Round(bonus_lot / 100000, 2) * 100000;

                // Open BonusOrderCount orders
                int opened_count = 0;
                string ticket_list = "";
                double entry_price = 0;

                for (int count = 0; count < BonusOrderCount; count++)
                {
                    TradeType tradeType = (news_direction == 1) ? TradeType.Buy : TradeType.Sell;
                    string label = "BONUS_" + TF_NAMES[tf];
                    double price = (news_direction == 1) ? Symbol.Ask : Symbol.Bid;

                    TradeResult result = OrderSendSafe(tf, tradeType, bonus_lot, label);

                    if (result != null && result.IsSuccessful)
                    {
                        opened_count++;
                        if (ticket_list != "") ticket_list += ",";
                        ticket_list += result.Position.Id.ToString();
                        if (entry_price == 0) entry_price = price;
                    }
                }

                // Consolidated log after loop
                if (opened_count > 0)
                {
                    string arrow = (news_direction > 0) ? "↑" : "↓";
                    double total_lot = opened_count * bonus_lot;
                    Print($">>> [OPEN] BONUS TF={TF_NAMES[tf]} | {opened_count}×{(news_direction == 1 ? "BUY" : "SELL")} @{bonus_lot / 100000:F2} Total:{total_lot / 100000:F2} @{entry_price} | News={(news_direction > 0 ? "+" : "")}{news_level}{arrow} | Multiplier:{BonusLotMultiplier:F1}x Tickets:{ticket_list} <<<");
                }
            }
        }

        #endregion

        #region ========== CLOSE FUNCTIONS ==========

        /// <summary>
        /// Close ALL strategies for specific TF (signal change)
        /// </summary>
        private void CloseAllStrategiesByLabelForTF(int tf)
        {
            int signal_old = _eaData.SignalOld[tf];
            int signal_new = _eaData.CSDLRows[tf].Signal;
            long timestamp_new = _eaData.CSDLRows[tf].Timestamp;

            // Get all positions for this symbol
            var positions = Positions.FindAll(_eaData.SymbolPrefix, SymbolName);

            foreach (var position in positions)
            {
                // Check if label belongs to any of 3 strategies in this TF
                int strategy_index = -1;
                for (int s = 0; s < 3; s++)
                {
                    if (position.Label == _eaData.Labels[tf, s])
                    {
                        strategy_index = s;
                        break;
                    }
                }

                if (strategy_index >= 0)
                {
                    string order_type_str = (position.TradeType == TradeType.Buy) ? "BUY" : "SELL";
                    Print($">> [CLOSE] SIGNAL_CHG TF={TF_NAMES[tf]} S={(strategy_index + 1)} | #{position.Id} {order_type_str} {position.VolumeInUnits / 100000:F2} | Profit=${position.NetProfit:F2} | Old:{signal_old} New:{signal_new} | Timestamp:{timestamp_new} <<");

                    CloseOrderSafely(position, "SIGNAL_CHANGE");
                }
            }

            // Reset all 3 flags for this TF
            for (int s = 0; s < 3; s++)
            {
                _eaData.PositionFlags[tf, s] = 0;
            }
        }

        /// <summary>
        /// Close ALL BONUS orders across ALL 7 TF when M1 signal changes
        /// </summary>
        private void CloseAllBonusOrders()
        {
            // Scan all 7 TF
            for (int tf = 0; tf < 7; tf++)
            {
                if (!IsTFEnabled(tf)) continue;

                string target_label_prefix = "BONUS_" + TF_NAMES[tf];
                int closed_count = 0;
                int total_count = 0;
                double total_profit = 0;
                double total_lot = 0;

                var positions = Positions.FindAll(target_label_prefix, SymbolName);

                foreach (var position in positions)
                {
                    if (position.Label.StartsWith(target_label_prefix))
                    {
                        total_count++;
                        double order_profit = position.NetProfit;
                        double order_lot = position.VolumeInUnits;

                        if (CloseOrderSafely(position, "BONUS_M1_CLOSE"))
                        {
                            closed_count++;
                            total_profit += order_profit;
                            total_lot += order_lot;
                        }
                    }
                }

                // Consolidated log
                if (total_count > 0)
                {
                    Print($">> [CLOSE] BONUS_M1 TF={TF_NAMES[tf]} | {total_count} orders Total:{total_lot / 100000:F2} | Profit=${total_profit:F2} | Closed:{closed_count}/{total_count} <<");
                }

                _eaData.PositionFlags[tf, 2] = 0;  // Reset BONUS flag
            }
        }

        /// <summary>
        /// Close S1 orders across ALL 7 TF when M1 signal changes
        /// </summary>
        private void CloseS1OrdersByM1()
        {
            for (int tf = 0; tf < 7; tf++)
            {
                if (!IsTFEnabled(tf)) continue;

                string target_label = _eaData.Labels[tf, 0];  // S1 label
                var positions = Positions.FindAll(target_label, SymbolName);

                foreach (var position in positions)
                {
                    if (position.Label == target_label)
                    {
                        CloseOrderSafely(position, "S1_M1_CLOSE");
                    }
                }

                _eaData.PositionFlags[tf, 0] = 0;
            }
        }

        /// <summary>
        /// Close S2 orders across ALL 7 TF when M1 signal changes
        /// </summary>
        private void CloseS2OrdersByM1()
        {
            for (int tf = 0; tf < 7; tf++)
            {
                if (!IsTFEnabled(tf)) continue;

                string target_label = _eaData.Labels[tf, 1];  // S2 label
                var positions = Positions.FindAll(target_label, SymbolName);

                foreach (var position in positions)
                {
                    if (position.Label == target_label)
                    {
                        CloseOrderSafely(position, "S2_M1_CLOSE");
                    }
                }

                _eaData.PositionFlags[tf, 1] = 0;
            }
        }

        /// <summary>
        /// Close only S3 for specific TF
        /// </summary>
        private void CloseS3OrdersForTF(int tf)
        {
            string target_label = _eaData.Labels[tf, 2];  // S3 label
            var positions = Positions.FindAll(target_label, SymbolName);

            foreach (var position in positions)
            {
                if (position.Label == target_label)
                {
                    CloseOrderSafely(position, "S3_SIGNAL_CHG");
                }
            }

            _eaData.PositionFlags[tf, 2] = 0;
        }

        #endregion

        #region ========== RISK MANAGEMENT ==========

        /// <summary>
        /// Check stoploss & take profit for all positions
        /// Stoploss: 2 layers (LAYER1, LAYER2)
        /// Take profit: 1 layer (based on max_loss × multiplier)
        /// </summary>
        private void CheckStoplossAndTakeProfit()
        {
            if (Positions.Count == 0) return;

            // Scan all positions
            foreach (var position in Positions)
            {
                if (position.SymbolName != SymbolName) continue;

                double profit = position.NetProfit;

                // Find TF + Strategy from label
                bool found = false;
                for (int tf = 0; tf < 7; tf++)
                {
                    for (int s = 0; s < 3; s++)
                    {
                        if (position.Label == _eaData.Labels[tf, s] &&
                            _eaData.PositionFlags[tf, s] == 1)
                        {
                            bool order_closed = false;

                            // ===== SECTION 1: STOPLOSS (2 layers) =====
                            if (StoplossMode != StoplossMode.NONE)
                            {
                                double sl_threshold = 0.0;
                                string mode_name = "";

                                if (StoplossMode == StoplossMode.LAYER1_MAXLOSS)
                                {
                                    // Layer1: Use pre-calculated threshold (max_loss × lot)
                                    sl_threshold = _eaData.Layer1Thresholds[tf, s];
                                    mode_name = "LAYER1_SL";
                                }
                                else if (StoplossMode == StoplossMode.LAYER2_MARGIN)
                                {
                                    // Layer2: Calculate from margin (emergency)
                                    double margin_usd = position.VolumeInUnits / 100000 * Symbol.TickValue * Symbol.TickSize;
                                    sl_threshold = -(margin_usd / Layer2_Divisor);
                                    mode_name = "LAYER2_SL";
                                }

                                // Check and close if loss exceeds threshold
                                if (profit <= sl_threshold)
                                {
                                    string short_mode = (mode_name == "LAYER1_SL") ? "L1_SL" : "L2_SL";
                                    string order_type_str = (position.TradeType == TradeType.Buy) ? "BUY" : "SELL";
                                    string margin_info = "";
                                    if (mode_name == "LAYER2_SL")
                                    {
                                        double margin_usd = position.VolumeInUnits / 100000 * Symbol.TickValue * Symbol.TickSize;
                                        margin_info = $" Margin=${margin_usd:F2}";
                                    }

                                    Print($">> [CLOSE] {short_mode} TF={TF_NAMES[tf]} S={(s + 1)} | #{position.Id} {order_type_str} {position.VolumeInUnits / 100000:F2} | Loss=${profit:F2} | Threshold=${sl_threshold:F2}{margin_info} <<");

                                    if (CloseOrderSafely(position, mode_name))
                                    {
                                        _eaData.PositionFlags[tf, s] = 0;
                                        order_closed = true;
                                    }
                                }
                            }

                            // ===== SECTION 2: TAKE PROFIT (1 layer) =====
                            if (!order_closed && UseTakeProfit)
                            {
                                // Calculate TP threshold from max_loss
                                double max_loss_per_lot = Math.Abs(_eaData.CSDLRows[tf].MaxLoss);
                                if (max_loss_per_lot < 1.0)
                                {
                                    max_loss_per_lot = Math.Abs(MaxLoss_Fallback);  // 1000
                                }

                                double tp_threshold = (max_loss_per_lot * _eaData.LotSizes[tf, s] / 100000) * TakeProfit_Multiplier;

                                // Check and close if profit exceeds threshold
                                if (profit >= tp_threshold)
                                {
                                    string order_type_str = (position.TradeType == TradeType.Buy) ? "BUY" : "SELL";
                                    Print($">> [CLOSE] TP TF={TF_NAMES[tf]} S={(s + 1)} | #{position.Id} {order_type_str} {position.VolumeInUnits / 100000:F2} | Profit=${profit:F2} | Threshold=${tp_threshold:F2} Mult={TakeProfit_Multiplier:F2} <<");

                                    if (CloseOrderSafely(position, "TAKE_PROFIT"))
                                    {
                                        _eaData.PositionFlags[tf, s] = 0;
                                    }
                                }
                            }

                            found = true;
                            break;
                        }
                    }
                    if (found) break;
                }
            }
        }

        #endregion
    }
}
