# 📊 MT5 DASHBOARD REDESIGN PROPOSAL

**Date**: 2025-11-06
**Purpose**: Tối ưu giao diện dashboard MT5 với fonts và ký tự đặc biệt chuyên nghiệp

---

## 🎨 PHẦN 1: WINDOWS FONTS - KÝ TỰ ĐẶC BIỆT

### **1.1. FONTS WINDOWS THƯỜNG DÙNG TRONG WORD**

| Font Name | Đặc điểm | Unicode Support | Khuyến nghị |
|-----------|----------|-----------------|-------------|
| **Segoe UI** | Font hệ thống Windows hiện đại | ✅ Excellent | ⭐⭐⭐⭐⭐ Best |
| **Segoe UI Symbol** | Chuyên cho symbols & icons | ✅ Excellent | ⭐⭐⭐⭐⭐ Best |
| **Consolas** | Monospace, code-friendly | ✅ Good | ⭐⭐⭐⭐ Recommended |
| **Courier New** | Monospace cổ điển (đang dùng) | ⚠️ Limited | ⭐⭐⭐ Current |
| **Arial Unicode MS** | Unicode rộng | ✅ Excellent | ⭐⭐⭐⭐ Good |
| **Lucida Console** | Monospace, readable | ✅ Good | ⭐⭐⭐ OK |
| **Calibri** | Font Word mặc định | ✅ Good | ⭐⭐⭐⭐ Good |
| **Webdings** | Symbol font (⚠️ không có text) | ❌ Symbols only | ⭐⭐ Special use |
| **Wingdings** | Symbol font (⚠️ không có text) | ❌ Symbols only | ⭐⭐ Special use |

### **1.2. KHUYẾN NGHỊ CHO MT5 DASHBOARD**

**Top 3 Fonts**:
1. **Segoe UI** (size 9-10) - Modern, professional, excellent Unicode ✅
2. **Consolas** (size 9) - Monospace, great for tables, good Unicode ✅
3. **Segoe UI Symbol** (size 8-10) - Best for symbols/icons ✅

**Lưu ý**:
- ❌ **KHÔNG dùng Webdings/Wingdings** - Chỉ có symbols, không có chữ cái
- ✅ **Segoe UI** tốt nhất - Vừa có chữ đẹp, vừa hỗ trợ Unicode symbols
- ✅ **Consolas** tốt cho tables - Monospace giúp align columns

---

## 📐 PHẦN 2: KÝ TỰ ĐẶC BIỆT (UNICODE)

### **2.1. BOX DRAWING CHARACTERS - Vẽ khung**

```
Current: "----------------------------------------------------"
Better:  "═════════════════════════════════════════════════"  (Double line)
Better:  "─────────────────────────────────────────────────"  (Single line)
Better:  "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"  (Heavy line)
```

**Full Box Set**:
```
┌───────┬───────┬───────┐  Top border
│  TF   │  Sig  │  P&L  │  Data row
├───────┼───────┼───────┤  Middle separator
│  M1   │   ▲   │ +1.23 │  Data row
└───────┴───────┴───────┘  Bottom border
```

**Unicode codes**:
- `─` (U+2500) - Horizontal line
- `│` (U+2502) - Vertical line
- `┌` (U+250C) - Top-left corner
- `┐` (U+2510) - Top-right corner
- `└` (U+2514) - Bottom-left corner
- `┘` (U+2518) - Bottom-right corner
- `├` (U+251C) - Left T-junction
- `┤` (U+2524) - Right T-junction
- `┬` (U+252C) - Top T-junction
- `┴` (U+2534) - Bottom T-junction
- `┼` (U+253C) - Cross junction
- `═` (U+2550) - Double horizontal line
- `║` (U+2551) - Double vertical line
- `╔` (U+2554) - Double top-left corner
- `╗` (U+2557) - Double top-right corner
- `╚` (U+255A) - Double bottom-left corner
- `╝` (U+255D) - Double bottom-right corner

### **2.2. ARROW SYMBOLS - Mũi tên**

```
Current: "^" (up), "v" (down), "-" (none)
```

**Better Options**:

| Symbol | Unicode | Code | Mô tả |
|--------|---------|------|-------|
| ▲ | U+25B2 | `\u25B2` | Black up-pointing triangle |
| ▼ | U+25BC | `\u25BC` | Black down-pointing triangle |
| △ | U+25B3 | `\u25B3` | White up-pointing triangle |
| ▽ | U+25BD | `\u25BD` | White down-pointing triangle |
| ↑ | U+2191 | `\u2191` | Upwards arrow |
| ↓ | U+2193 | `\u2193` | Downwards arrow |
| ⬆ | U+2B06 | `\u2B06` | Upwards black arrow (bold) |
| ⬇ | U+2B07 | `\u2B07` | Downwards black arrow (bold) |
| ⇧ | U+21E7 | `\u21E7` | Upwards white arrow |
| ⇩ | U+21E9 | `\u21E9` | Downwards white arrow |
| ➚ | U+279A | `\u279A` | North east arrow |
| ➘ | U+2798 | `\u2798` | South east arrow |
| • | U+2022 | `\u2022` | Bullet (for none/neutral) |
| ─ | U+2500 | `\u2500` | Horizontal line (for none) |
| ○ | U+25CB | `\u25CB` | White circle (for none) |

**Khuyến nghị**:
- **BUY**: ▲ (U+25B2) - Đậm, rõ ràng ✅
- **SELL**: ▼ (U+25BC) - Đậm, rõ ràng ✅
- **NONE**: • (U+2022) hoặc ─ (U+2500) ✅

### **2.3. STATUS SYMBOLS - Trạng thái**

| Symbol | Unicode | Mô tả | Dùng cho |
|--------|---------|-------|----------|
| ● | U+25CF | Black circle | Position active |
| ○ | U+25CB | White circle | No position |
| ◉ | U+25C9 | Fisheye | Special state |
| ◎ | U+25CE | Bullseye | Target state |
| ✓ | U+2713 | Check mark | Success |
| ✗ | U+2717 | X mark | Failed |
| ✔ | U+2714 | Heavy check | Strong success |
| ✘ | U+2718 | Heavy X | Strong fail |
| ⚠ | U+26A0 | Warning sign | Alert |
| ⚡ | U+26A1 | Lightning | High activity |
| ★ | U+2605 | Black star | Important |
| ☆ | U+2606 | White star | Normal |

### **2.4. TREND SYMBOLS - Xu hướng**

| Symbol | Unicode | Mô tả | Dùng cho |
|--------|---------|-------|----------|
| ↗ | U+2197 | Up-right arrow | Uptrend |
| ↘ | U+2198 | Down-right arrow | Downtrend |
| → | U+2192 | Right arrow | Sideways |
| ⤴ | U+2934 | Arrow pointing rightwards then curving upwards | Strong up |
| ⤵ | U+2935 | Arrow pointing rightwards then curving downwards | Strong down |
| 📈 | U+1F4C8 | Chart increasing | Trend up |
| 📉 | U+1F4C9 | Chart decreasing | Trend down |

### **2.5. NUMBER SYMBOLS - Số & Level**

| Symbol | Unicode | Mô tả |
|--------|---------|-------|
| ① ② ③ ④ ⑤ ⑥ ⑦ | U+2460-2466 | Circled numbers |
| ⑴ ⑵ ⑶ ⑷ ⑸ ⑹ ⑺ | U+2474-247A | Parenthesized numbers |
| ❶ ❷ ❸ ❹ ❺ ❻ ❼ | U+2776-277C | Negative circled numbers |

### **2.6. CURRENCY & PROFIT SYMBOLS**

| Symbol | Unicode | Mô tả |
|--------|---------|-------|
| $ | U+0024 | Dollar |
| € | U+20AC | Euro |
| £ | U+00A3 | Pound |
| ¥ | U+00A5 | Yen |
| ₿ | U+20BF | Bitcoin |
| + | U+002B | Plus (profit) |
| − | U+2212 | Minus (loss) |
| ± | U+00B1 | Plus-minus |

---

## 🎯 PHẦN 3: DASHBOARD REDESIGN - 3 OPTIONS

### **OPTION 1: MODERN CLEAN (Recommended) ⭐⭐⭐⭐⭐**

**Changes**:
- Font: **Segoe UI** size 9
- Arrows: ▲ (up), ▼ (down), • (none)
- Separators: `─────────────────────────────────────────────────`
- Position status: ● (active), ○ (empty)
- Colors: Keep current (Yellow, White, DodgerBlue)

**Example**:
```
[LTCUSD] DA1 | 7TFx3S | D1:▲ | $5000 DD:2.5% | 12/21
─────────────────────────────────────────────────
TF    Sig   S1      S2      S3      P&L       News    Bonus
─────────────────────────────────────────────────
M1    ▲     ●0.01   ○       ○       +1.23     +10     2|0.02
M5    ▲     ●0.02   ●0.03   ○       +5.67     +20     -
M15   ▲     ●0.02   ●0.03   ○       +3.45     +0      -
M30   ▼     ○       ○       ●0.01   -2.10     -1      1|0.01
H1    •     ○       ○       ○       +0.00     +0      -
H4    ▲     ●0.05   ○       ○       +10.23    +5      -
D1    ▲     ●0.10   ○       ○       +15.67    +7      -
─────────────────────────────────────────────────
BONUS: 3 orders | 0.03 lots | +2.34 USD
NET:$34.15 | S1:5x$20 | S2:2x$9 | S3:1x$5 | 12/21
Exness | Lev:1:500 | 2s
```

**MQL5 Code Changes**:
```mql5
void CreateOrUpdateLabel(string name, string text, int x, int y, color clr, int font_size) {
    if(ObjectFind(name) < 0) {
        ObjectCreate(name, OBJ_LABEL, 0, 0, 0);
        ObjectSet(name, OBJPROP_CORNER, CORNER_LEFT_UPPER);
        ObjectSet(name, OBJPROP_XDISTANCE, x);
        ObjectSet(name, OBJPROP_YDISTANCE, y);
    }
    ObjectSetText(name, text, font_size, "Segoe UI", clr);  // ← Changed from "Courier New"
}

// In UpdateDashboard():
// Replace ASCII arrows
string sig = "";
if(current_signal == 1) sig = "▲";         // ← Changed from "^"
else if(current_signal == -1) sig = "▼";   // ← Changed from "v"
else sig = "•";                             // ← Changed from "-"

// Replace position markers
string s1 = (g_ea.position_flags[tf][0] == 1) ? "●" + DoubleToString(g_ea.lot_sizes[tf][0], 2) : "○";  // ← Changed
string s2 = (g_ea.position_flags[tf][1] == 1) ? "●" + DoubleToString(g_ea.lot_sizes[tf][1], 2) : "○";  // ← Changed
string s3 = (g_ea.position_flags[tf][2] == 1) ? "●" + DoubleToString(g_ea.lot_sizes[tf][2], 2) : "○";  // ← Changed

// Replace separator
CreateOrUpdateLabel(g_ea.symbol_prefix + "dash_1", "─────────────────────────────────────────────────", 10, y_pos, clrWhite, 9);
// ← Changed from "----------------------------------------------------"
```

---

### **OPTION 2: BOXED TABLE (Professional) ⭐⭐⭐⭐**

**Changes**:
- Font: **Consolas** size 9 (monospace for perfect alignment)
- Full box drawing characters
- Same arrows/symbols as Option 1

**Example**:
```
╔═══════════════════════════════════════════════╗
║ [LTCUSD] DA1 | 7TFx3S | D1:▲ | $5000 | 12/21 ║
╠═══╦═════╦═══════╦═══════╦═══════╦═════╦══════╣
║TF ║ Sig ║  S1   ║  S2   ║  S3   ║ P&L ║ News ║
╠═══╬═════╬═══════╬═══════╬═══════╬═════╬══════╣
║M1 ║  ▲  ║●0.01  ║  ○    ║  ○    ║+1.23║ +10  ║
║M5 ║  ▲  ║●0.02  ║●0.03  ║  ○    ║+5.67║ +20  ║
║M15║  ▲  ║●0.02  ║●0.03  ║  ○    ║+3.45║  +0  ║
║M30║  ▼  ║  ○    ║  ○    ║●0.01  ║-2.10║  -1  ║
║H1 ║  •  ║  ○    ║  ○    ║  ○    ║+0.00║  +0  ║
║H4 ║  ▲  ║●0.05  ║  ○    ║  ○    ║+10.2║  +5  ║
║D1 ║  ▲  ║●0.10  ║  ○    ║  ○    ║+15.6║  +7  ║
╠═══╩═════╩═══════╩═══════╩═══════╩═════╩══════╣
║ NET:$34.15 | S1:5x$20 | S2:2x$9 | S3:1x$5    ║
╚═══════════════════════════════════════════════╝
```

**MQL5 Code Changes**:
```mql5
void CreateOrUpdateLabel(string name, string text, int x, int y, color clr, int font_size) {
    // ... (same as Option 1)
    ObjectSetText(name, text, font_size, "Consolas", clr);  // ← Consolas for box alignment
}

// In UpdateDashboard():
// Top border
CreateOrUpdateLabel(g_ea.symbol_prefix + "dash_0", "╔═══════════════════════════════════════════════╗", 10, y_pos, clrYellow, 9);
y_pos += line_height;

// Header row
string header = "║ [" + g_ea.symbol_name + "] " + folder + " | 7TFx3S | D1:" + trend + " | $" + DoubleToString(equity, 0) + " ║";
CreateOrUpdateLabel(g_ea.symbol_prefix + "dash_1", header, 10, y_pos, clrYellow, 9);
y_pos += line_height;

// Column header separator
CreateOrUpdateLabel(g_ea.symbol_prefix + "dash_2", "╠═══╦═════╦═══════╦═══════╦═══════╦═════╦══════╣", 10, y_pos, clrWhite, 9);
y_pos += line_height;

// Data rows with ║ borders
string row = "║" + PadRight(G_TF_NAMES[tf], 3) + "║" + PadRight(sig, 5) + "║" + PadRight(s1, 7) + "║" + ... + "║";
CreateOrUpdateLabel(g_ea.symbol_prefix + "dash_" + IntegerToString(4 + tf), row, 10, y_pos, row_color, 9);

// Bottom border
CreateOrUpdateLabel(g_ea.symbol_prefix + "dash_14", "╚═══════════════════════════════════════════════╝", 10, y_pos, clrYellow, 9);
```

**Lưu ý**: Option 2 phức tạp hơn, cần điều chỉnh PadRight() và spacing cẩn thận.

---

### **OPTION 3: MINIMAL SYMBOLS (Safe) ⭐⭐⭐**

**Changes**:
- Font: Keep **Courier New** (current)
- Only change arrows: ↑ (up), ↓ (down), → (none)
- Keep current separators: `----`
- Minimal risk, easy to implement

**Example**:
```
[LTCUSD] DA1 | 7TFx3S | D1:↑ | $5000 DD:2.5% | 12/21
----------------------------------------------------
TF    Sig   S1      S2      S3      P&L       News    Bonus
----------------------------------------------------
M1    ↑     *0.01   o       o       +1.23     +10     2|0.02
M5    ↑     *0.02   *0.03   o       +5.67     +20     -
M15   ↑     *0.02   *0.03   o       +3.45     +0      -
M30   ↓     o       o       *0.01   -2.10     -1      1|0.01
H1    →     o       o       o       +0.00     +0      -
H4    ↑     *0.05   o       o       +10.23    +5      -
D1    ↑     *0.10   o       o       +15.67    +7      -
----------------------------------------------------
NET:$34.15 | S1:5x$20 | S2:2x$9 | S3:1x$5 | 12/21
```

**MQL5 Code Changes**:
```mql5
// Only change arrows, keep everything else
string sig = "";
if(current_signal == 1) sig = "↑";         // ← Changed from "^"
else if(current_signal == -1) sig = "↓";   // ← Changed from "v"
else sig = "→";                             // ← Changed from "-"

// Trend indicator
string trend = (g_ea.trend_d1 == 1) ? "↑" : (g_ea.trend_d1 == -1 ? "↓" : "→");  // ← Changed
```

---

## 📊 PHẦN 4: SO SÁNH 3 OPTIONS

| Aspect | Option 1 (Modern) | Option 2 (Boxed) | Option 3 (Minimal) |
|--------|-------------------|------------------|--------------------|
| **Visual Impact** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Readability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Implementation** | ⭐⭐⭐⭐ Easy | ⭐⭐⭐ Medium | ⭐⭐⭐⭐⭐ Very Easy |
| **Unicode Support** | ✅ Good | ✅ Excellent | ✅ Good |
| **Professional** | ✅ Yes | ✅ Very | ⚠️ OK |
| **Font Availability** | ✅ Universal | ✅ Universal | ✅ Universal |
| **Code Changes** | ~10 lines | ~30 lines | ~5 lines |
| **Risk** | 🟢 Low | 🟡 Medium | 🟢 Very Low |

---

## 🎯 KHUYẾN NGHỊ CUỐI CÙNG

### **Best Choice: OPTION 1 - MODERN CLEAN** ⭐⭐⭐⭐⭐

**Lý do**:
1. ✅ **Tối ưu nhất** - Visual impact cao, dễ đọc
2. ✅ **Dễ implement** - Chỉ 10-15 dòng code thay đổi
3. ✅ **An toàn** - Segoe UI có sẵn trên mọi Windows 7+
4. ✅ **Professional** - Symbols rõ ràng (▲▼●○)
5. ✅ **Maintain dễ** - Không phức tạp như Option 2

**Alternative: OPTION 3** nếu muốn an toàn tuyệt đối (5 dòng code thay đổi)

**NOT Recommended: OPTION 2** - Đẹp nhưng phức tạp, khó align, khó maintain

---

## 🔧 PHẦN 5: IMPLEMENTATION GUIDE (OPTION 1)

### **Step 1: Update CreateOrUpdateLabel()**

```mql5
void CreateOrUpdateLabel(string name, string text, int x, int y, color clr, int font_size) {
    if(ObjectFind(name) < 0) {
        ObjectCreate(name, OBJ_LABEL, 0, 0, 0);
        ObjectSet(name, OBJPROP_CORNER, CORNER_LEFT_UPPER);
        ObjectSet(name, OBJPROP_XDISTANCE, x);
        ObjectSet(name, OBJPROP_YDISTANCE, y);
    }
    ObjectSetText(name, text, font_size, "Segoe UI", clr);  // ← CHANGED
}
```

### **Step 2: Update Signal Arrows**

```mql5
// In UpdateDashboard(), around line 2643
string sig = "";
if(current_signal == 1) sig = "▲";         // ← CHANGED
else if(current_signal == -1) sig = "▼";   // ← CHANGED
else sig = "•";                             // ← CHANGED
```

### **Step 3: Update Trend Indicator**

```mql5
// Around line 2604
string trend = (g_ea.trend_d1 == 1) ? "▲" : (g_ea.trend_d1 == -1 ? "▼" : "•");  // ← CHANGED
```

### **Step 4: Update Position Markers**

```mql5
// Around line 2650-2652
string s1 = (g_ea.position_flags[tf][0] == 1) ? "●" + DoubleToString(g_ea.lot_sizes[tf][0], 2) : "○";  // ← CHANGED
string s2 = (g_ea.position_flags[tf][1] == 1) ? "●" + DoubleToString(g_ea.lot_sizes[tf][1], 2) : "○";  // ← CHANGED
string s3 = (g_ea.position_flags[tf][2] == 1) ? "●" + DoubleToString(g_ea.lot_sizes[tf][2], 2) : "○";  // ← CHANGED
```

### **Step 5: Update Separators**

```mql5
// Replace all separators (lines 2614, 2625, 2684)
CreateOrUpdateLabel(g_ea.symbol_prefix + "dash_1", "─────────────────────────────────────────────────", 10, y_pos, clrWhite, 9);
// ← CHANGED from "----------------------------------------------------"
```

### **Step 6: Test on MT5**

1. Compile EA
2. Attach to chart
3. Check font rendering
4. Verify Unicode characters display correctly
5. Adjust spacing if needed (PadRight() values)

---

## ⚠️ FALLBACK PLAN

**Nếu Segoe UI không hiển thị Unicode đúng** (rare):

```mql5
// Fallback to Consolas
ObjectSetText(name, text, font_size, "Consolas", clr);
```

**Nếu Unicode symbols không hiển thị** (very rare):

```mql5
// Fallback to ASCII
string sig = "";
if(current_signal == 1) sig = "^";
else if(current_signal == -1) sig = "v";
else sig = "-";
```

---

## 📌 SUMMARY

**TL;DR**:
1. **Best font**: Segoe UI (size 9)
2. **Best arrows**: ▲ (up), ▼ (down), • (none)
3. **Best position**: ● (active), ○ (empty)
4. **Best separator**: `─────────` (U+2500)
5. **Implementation**: ~10-15 lines code changes
6. **Risk**: 🟢 Low (Segoe UI universal on Windows 7+)

**Next Steps**:
1. Review proposal
2. Choose option (recommend Option 1)
3. Implement changes in `_MT5_EAs_MTF ONER_V2.mq5`
4. Test on demo
5. Deploy to live

---

**Prepared by**: Claude Code Session
**For**: Multi-Trading-Bot-Oner_2025 Project
**File**: `MQL5/MT5_DASHBOARD_REDESIGN_PROPOSAL.md`
