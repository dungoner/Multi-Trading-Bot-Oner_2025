================================================================================
EA BOT V2 - CONFIGURATION GUIDE
================================================================================
File: README_CONFIG.txt
Version: 2.0
Last Update: 2025-01-31

================================================================================
OVERVIEW
================================================================================

This EA uses MT4 native .SET files for configuration. This is SMARTER than
JSON because:

✓ MT4 built-in support (no parser code needed)
✓ Load directly in INPUT dialog when attaching EA
✓ Edit in any text editor
✓ Save multiple presets (conservative, aggressive, scalping, etc.)
✓ Copy .set + .ex4 = instant deployment

================================================================================
FILE STRUCTURE
================================================================================

MQL4/Files/DataAutoOner2/
  ├── config_ea_oner.set          ← Standard configuration
  ├── README_CONFIG.txt            ← This file
  ├── [Optional custom presets]
  │   ├── config_conservative.set
  │   ├── config_aggressive.set
  │   └── config_scalping.set

================================================================================
HOW TO USE
================================================================================

METHOD 1: LOAD WHEN ATTACHING EA (RECOMMENDED)
----------------------------------------------
1. Drag EA onto chart
2. INPUT tab will open
3. Click "Load" button (top right of dialog)
4. Browse to: MQL4/Files/DataAutoOner2/config_ea_oner.set
5. Select file → All parameters auto-fill
6. Click "OK" to apply

METHOD 2: EDIT BEFORE LOADING
----------------------------------------------
1. Open config_ea_oner.set in text editor
2. Edit values (see format below)
3. Save file
4. Follow METHOD 1 to load

METHOD 3: SAVE YOUR OWN PRESET
----------------------------------------------
1. Attach EA and configure parameters manually
2. In INPUT tab, click "Save" button
3. Save as: MQL4/Files/DataAutoOner2/config_custom.set
4. Next time, load your custom preset

================================================================================
FILE FORMAT
================================================================================

; Comment lines start with semicolon
ParameterName=Value

EXAMPLES:
---------
; Enable/disable timeframes (1=ON, 0=OFF)
TF_M1=1
TF_M5=0

; Lot size (decimal)
FixedLotSize=0.10

; Integer values
MinNewsLevelS1=20

; Enum values (use number)
StoplossMode=1

IMPORTANT:
- Boolean: 1=TRUE, 0=FALSE
- Decimal: Use dot (0.10 not 0,10)
- Enum: Use number not name (1 not LAYER1_MAXLOSS)
- No quotes needed for values

================================================================================
PARAMETER REFERENCE
================================================================================

A. CORE SETTINGS
----------------
TF_M1, TF_M5, TF_M15, TF_M30, TF_H1, TF_H4, TF_D1  → 1=ON, 0=OFF
S1_HOME, S2_TREND, S3_NEWS                           → 1=ON, 0=OFF
FixedLotSize                                         → 0.01-1.0
MaxLoss_Fallback                                     → -1000.00 (negative)
CSDL_Source                                          → 0/1/2 (folder)

B. STRATEGY CONFIGURATIONS
--------------------------
S1_UseNewsFilter                                     → 1=strict, 0=basic
MinNewsLevelS1                                       → 20-100
S1_RequireNewsDirection                              → 1=match, 0=any
S2_TrendMode                                         → 0=auto, 1=buy, -1=sell
MinNewsLevelS3                                       → 20-100
EnableBonusNews                                      → 1=ON, 0=OFF
BonusOrderCount                                      → 1-5
MinNewsLevelBonus                                    → 20-100

C. RISK PROTECTION
------------------
StoplossMode                                         → 0=none, 1=layer1, 2=layer2
Layer2_Divisor                                       → 20.0
UseTakeProfit                                        → 1=ON, 0=OFF
TakeProfit_Multiplier                                → 0.5=50%, 1.0=100%, 2.0=200%
EnableWeekendReset                                   → 1=ON, 0=OFF
EnableHealthCheck                                    → 1=ON, 0=OFF

D. AUXILIARY SETTINGS
---------------------
UseEvenOddMode                                       → 1=ON, 0=OFF
ShowDashboard                                        → 1=ON, 0=OFF
DebugMode                                            → 1=ON, 0=OFF

================================================================================
PRESET EXAMPLES
================================================================================

CONSERVATIVE (Low risk, tight control)
---------------------------------------
FixedLotSize=0.05
StoplossMode=1
UseTakeProfit=1
TakeProfit_Multiplier=0.30
EnableWeekendReset=1

AGGRESSIVE (High risk, no limits)
----------------------------------
FixedLotSize=0.20
StoplossMode=0
UseTakeProfit=0
S1_UseNewsFilter=0

SCALPING (M1-M15 only, quick trades)
-------------------------------------
TF_M1=1, TF_M5=1, TF_M15=1
TF_M30=0, TF_H1=0, TF_H4=0, TF_D1=0
FixedLotSize=0.01
UseTakeProfit=1
TakeProfit_Multiplier=0.25

SWING TRADING (H1+ only, patient)
----------------------------------
TF_M1=0, TF_M5=0, TF_M15=0, TF_M30=0
TF_H1=1, TF_H4=1, TF_D1=1
FixedLotSize=0.15
StoplossMode=1

================================================================================
DEPLOYMENT WORKFLOW
================================================================================

OLD WAY (Without .set):
-----------------------
1. Attach EA
2. Manually configure 35 INPUT parameters
3. Click OK
4. Repeat for every chart/symbol
→ TEDIOUS!

NEW WAY (With .set):
--------------------
1. Edit config_ea_oner.set once
2. Attach EA → Load .set file
3. Click OK
4. Same settings applied instantly
→ FAST!

TEAM DEPLOYMENT:
----------------
1. Configure optimal settings
2. Save as config_team.set
3. Share .set file with team
4. Everyone loads same config
→ CONSISTENT!

================================================================================
TROUBLESHOOTING
================================================================================

Q: EA doesn't load my .set file
A: Check file is in correct folder (MQL4/Files/DataAutoOner2/)
   File must have .set extension

Q: Values not applied after loading
A: Check format: ParameterName=Value (no spaces around =)
   Boolean must be 1 or 0, not true/false

Q: Where is "Load" button?
A: In INPUT tab when attaching EA, top right corner

Q: Can I use different .set for different symbols?
A: Yes! Save as config_EURUSD.set, config_BTCUSD.set, etc.
   Load appropriate file for each symbol

Q: Do I need to recompile EA?
A: NO! .set files are loaded at runtime, no compilation needed

================================================================================
TIPS & BEST PRACTICES
================================================================================

1. BACKUP CONFIGS
   - Save working configs with date: config_20250131.set
   - Version control: config_v1.set, config_v2.set

2. TEST FIRST
   - Create config_test.set for demo account
   - After testing, copy to config_live.set for real account

3. DOCUMENT CHANGES
   - Add comments in .set file explaining why you changed values
   ; Changed lot from 0.10 to 0.05 due to high volatility

4. MULTIPLE STRATEGIES
   - config_conservative.set (low risk)
   - config_moderate.set (balanced)
   - config_aggressive.set (high risk)
   - Load based on market conditions

5. QUICK SWITCH
   - Save current settings: Click "Save" in INPUT tab
   - Load different preset: Click "Load" → select .set
   - Compare results with different configs

================================================================================
SUPPORT
================================================================================

For issues or questions:
- Check this README first
- Review config_ea_oner.set comments
- Verify parameter values match allowed ranges
- Test with default config before custom configs

================================================================================
END OF GUIDE
================================================================================
