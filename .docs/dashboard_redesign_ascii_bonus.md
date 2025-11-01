# DASHBOARD REDESIGN - OPTIMIZED WITH ASCII + BONUS STATUS
## Thiết kế tối ưu Dashboard với ký tự ASCII thông thường + Trạng thái BONUS

---

## I. YÊU CẦU TỪ USER

### A. Giữ nguyên Color Scheme
- ✅ 7 TF rows: Xen kẽ TRẮNG/XANH (giống cũ)
- ✅ Footer lines: VÀNG (giống cũ)

### B. Thay đổi Format
- ❌ KHÔNG dùng ↑ ▲ ▼ (MT4 không support, cần font .symbol)
- ✅ CHỈ dùng ASCII thông thường: ^ v + - * o [ ]
- ✅ Thêm cột P&L per TF
- ✅ Compact summary: S1:5x$140

### C. Thêm dòng mới - BONUS STATUS
**Vị trí:** Dưới bảng 7 TF, trước P&L summary

**Nội dung cần hiển thị:**
1. **TF đang quét được** (có News >= MinNewsLevelBonus)
2. **Số lượng lệnh sẽ đánh** (BonusOrderCount)
3. **Trạng thái**: WAIT (chờ) / OPEN (đang đánh)
4. **Thời gian đánh** (timestamp khi mở lệnh)

**Ví dụ:**
```
BONUS: M1(5x) M5(3x) | Status:WAIT | Last:15:30:45
BONUS: H1(5x) | Status:OPEN | Last:16:25:10
BONUS: None | Status:IDLE
```

---

## II. DASHBOARD MỚI - FULL LAYOUT

```
┌────────────────────────────────────────────────────────────┐
│ Line 0 (WHITE 9px):                                         │
│ [LTCUSD] DA2 | 7TFx3S | D1:^ News:45^ | $5000 DD:2.3% | 8/21│
├────────────────────────────────────────────────────────────┤
│ Line 1 (WHITE 9px):                                         │
│ TF   Sig  S1     S2     S3     P&L     News                │
├────────────────────────────────────────────────────────────┤
│ Line 2 (BLUE 9px):                                          │
│ M1   ^    *0.05  o      *0.02  +12.30  +55                 │
├────────────────────────────────────────────────────────────┤
│ Line 3 (WHITE 9px):                                         │
│ M5   v    o      *0.10  o      -25.00  -30                 │
├────────────────────────────────────────────────────────────┤
│ Line 4 (BLUE 9px):                                          │
│ M15  ^    *0.08  *0.12  o      +95.20  +42                 │
├────────────────────────────────────────────────────────────┤
│ Line 5 (WHITE 9px):                                         │
│ M30  -    o      o      o      +0.00   +18                 │
├────────────────────────────────────────────────────────────┤
│ Line 6 (BLUE 9px):                                          │
│ H1   ^    *0.15  o      *0.03  -8.50   +60                 │
├────────────────────────────────────────────────────────────┤
│ Line 7 (WHITE 9px):                                         │
│ H4   v    o      *0.20  o      +80.00  -25                 │
├────────────────────────────────────────────────────────────┤
│ Line 8 (BLUE 9px):                                          │
│ D1   ^    *0.05  *0.10  *0.02  +81.50  +35                 │
├────────────────────────────────────────────────────────────┤
│ Line 9 (WHITE 9px):                                         │
│ BONUS: M1(5x +65^) H1(3x +58^) | WAIT | Last:15:30:45     │
├────────────────────────────────────────────────────────────┤
│ Line 10 (YELLOW 9px):                                       │
│ NET:$235.50 | S1:5x$140 S2:2x$55 S3:1x$40.5 | 8/21         │
├────────────────────────────────────────────────────────────┤
│ Line 11 (YELLOW 9px):                                       │
│ Exness-Real12 | Lev:1:500 | 2s                             │
└────────────────────────────────────────────────────────────┘

Total: 12 lines (vs 16 cũ = giảm 25%)
```

---

## III. CHI TIẾT TỪNG DÒNG

### Line 0 - HEADER (WHITE)

**CŨ:**
```
[LTCUSD] DA2 | 7TFx3S=21 | Trend:D1[^] News:Lv45[^] | Eq:$5000 DD:2.3%
```

**MỚI (ngắn gọn hơn):**
```
[LTCUSD] DA2 | 7TFx3S | D1:^ News:45^ | $5000 DD:2.3% | 8/21
```

**Thay đổi:**
- ❌ Bỏ `=21` (hiển thị `8/21` ở cuối đủ rồi)
- ❌ Bỏ `Trend:` `Lv` (thừa)
- ✅ Thêm `8/21` (orders count) ở cuối
- ✅ Dùng `^` thay `[^]` (ngắn hơn)

---

### Line 1 - COLUMN HEADERS (WHITE)

**CŨ:**
```
TF   Signal  S1      S2      S3      Age   DPrice  News
```

**MỚI:**
```
TF   Sig  S1     S2     S3     P&L     News
```

**Thay đổi:**
- ❌ Bỏ column `Signal` → `Sig` (ngắn)
- ❌ Bỏ column `Age` (ít giá trị)
- ❌ Bỏ column `DPrice` (ít dùng)
- ✅ Thêm column `P&L` (QUAN TRỌNG - profit/loss per TF)
- ✅ Giữ column `News`

**Column widths:**
```cpp
TF:    4 chars (M1, M5, M15, M30, H1, H4, D1)
Sig:   5 chars (^, v, -)
S1:    7 chars (*0.05, o)
S2:    7 chars (*0.10, o)
S3:    7 chars (*0.02, o)
P&L:   8 chars (+12.30, -25.00)
News:  variable (+55, -30, +42)
```

---

### Lines 2-8 - 7 TF ROWS (BLUE/WHITE xen kẽ)

**Format:**
```
M1   ^    *0.05  o      *0.02  +12.30  +55
```

**Chi tiết:**
- `M1` - Timeframe (4 chars)
- `^` - Signal: `^`=BUY, `v`=SELL, `-`=NONE (5 chars)
- `*0.05` - S1 có lệnh lot 0.05, hoặc `o` nếu không có (7 chars)
- `o` - S2 không có lệnh (7 chars)
- `*0.02` - S3 có lệnh lot 0.02 (7 chars)
- `+12.30` - P&L của TF này (tất cả strategies) (8 chars)
- `+55` - News cascade level (variable)

**Màu sắc:**
- Line 2 (M1):  **BLUE** (clrDodgerBlue)
- Line 3 (M5):  **WHITE** (clrWhite)
- Line 4 (M15): **BLUE**
- Line 5 (M30): **WHITE**
- Line 6 (H1):  **BLUE**
- Line 7 (H4):  **WHITE**
- Line 8 (D1):  **BLUE**

---

### Line 9 - BONUS STATUS (WHITE) ⭐ MỚI

**Format 1 - Có BONUS đang chờ:**
```
BONUS: M1(5x +65^) H1(3x +58^) | WAIT | Last:15:30:45
```

**Giải thích:**
- `M1(5x +65^)` - M1 sẽ mở 5 lệnh BONUS, News=+65, hướng UP
- `H1(3x +58^)` - H1 sẽ mở 3 lệnh BONUS, News=+58, hướng UP
- `WAIT` - Trạng thái: Đang chờ signal trigger
- `Last:15:30:45` - Lần cuối đánh lúc 15:30:45

**Format 2 - BONUS đang OPEN:**
```
BONUS: M1(5x +65^) | OPEN | Last:16:25:10 | P&L:+$120.50
```

**Giải thích:**
- `M1(5x +65^)` - Đã mở 5 lệnh BONUS trên M1
- `OPEN` - Trạng thái: Đã đánh, lệnh đang mở
- `Last:16:25:10` - Đã đánh lúc 16:25:10
- `P&L:+$120.50` - Tổng P&L của 5 lệnh BONUS

**Format 3 - Không có BONUS:**
```
BONUS: None | IDLE | Last:--:--:--
```

**Giải thích:**
- `None` - Không có TF nào đủ điều kiện BONUS
- `IDLE` - Trạng thái: Nghỉ
- `Last:--:--:--` - Chưa đánh lần nào

**Logic hiển thị:**
```cpp
if(EnableBonusNews) {
    // Scan 7 TF, tìm TF có news >= MinNewsLevelBonus
    string bonus_tfs = ""; // "M1(5x +65^) H1(3x +58^)"
    string status = "IDLE"; // IDLE / WAIT / OPEN
    string last_time = "--:--:--";
    string pnl_info = "";

    // Check có lệnh BONUS đang mở không?
    bool has_bonus_orders = false;
    for(int tf=0; tf<7; tf++) {
        if(HasBonusOrders(tf)) {
            has_bonus_orders = true;
            status = "OPEN";
            // Tính P&L của lệnh BONUS
        }
    }

    // Nếu không có lệnh mở, check có TF đủ điều kiện không
    if(!has_bonus_orders) {
        for(int tf=0; tf<7; tf++) {
            int news_abs = MathAbs(g_ea.csdl_rows[tf].news);
            if(news_abs >= MinNewsLevelBonus) {
                status = "WAIT";
                // Thêm vào bonus_tfs
                bonus_tfs += TF_NAMES[tf] + "(" + IntegerToString(BonusOrderCount) + "x " +
                             (g_ea.csdl_rows[tf].news > 0 ? "+" : "") +
                             IntegerToString(g_ea.csdl_rows[tf].news) +
                             (g_ea.csdl_rows[tf].news > 0 ? "^" : "v") + ") ";
            }
        }
    }

    if(bonus_tfs == "") bonus_tfs = "None";

    string line = "BONUS: " + bonus_tfs + " | " + status + " | Last:" + last_time;
    if(pnl_info != "") line += " | " + pnl_info;

    CreateOrUpdateLabel("dash_9", line, 10, y_pos, clrWhite, 9);
}
```

---

### Line 10 - P&L SUMMARY (YELLOW)

**CŨ:**
```
Orders:8/21 | Net:$235.50 | Profit:+$280.00 Loss:$-44.50 | 2s
```

**MỚI (compact):**
```
NET:$235.50 | S1:5x$140 S2:2x$55 S3:1x$40.5 | 8/21
```

**Giải thích:**
- `NET:$235.50` - Net P&L (Profit + Loss)
- `S1:5x$140` - 5 lệnh S1, tổng P&L = $140
- `S2:2x$55` - 2 lệnh S2, tổng P&L = $55
- `S3:1x$40.5` - 1 lệnh S3, tổng P&L = $40.5
- `8/21` - 8 lệnh đang mở / 21 lệnh tối đa
- ❌ Bỏ `Profit` `Loss` riêng lẻ (dư thừa)
- ❌ Bỏ `2s` (không cần)

---

### Line 11 - BROKER INFO (YELLOW)

**CŨ:**
```
Exness | Server:ExnessReal-12 | Leverage:1:500
```

**MỚI:**
```
Exness-Real12 | Lev:1:500 | 2s
```

**Thay đổi:**
- ✅ Gộp Broker+Server: `Exness-Real12`
- ✅ Ngắn: `Lev:` thay `Leverage:`
- ✅ Thêm `2s` update interval (optional)

---

## IV. CODE STRUCTURE

### A. Data to Track

**Cần thêm biến vào `g_ea` struct:**
```cpp
struct EASymbolData {
    // ... existing vars

    // BONUS tracking (3 vars)
    datetime bonus_last_open_time;   // Thời gian đánh BONUS lần cuối
    int bonus_status;                 // 0=IDLE, 1=WAIT, 2=OPEN
    string bonus_tfs_list;            // "M1(5x +65^) H1(3x +58^)"
};
```

**HOẶC** không cần thêm vào struct, tính real-time trong `UpdateDashboard()`:
- Scan 7 TF → Tìm TF có `news_abs >= MinNewsLevelBonus`
- Check có lệnh BONUS đang mở không (magic number matching)
- Format string hiển thị

---

### B. Helper Functions

**1. Check TF có lệnh BONUS không:**
```cpp
bool HasBonusOrders(int tf) {
    int target_magic = g_ea.magic_numbers[tf][2]; // S3 magic
    for(int i = 0; i < OrdersTotal(); i++) {
        if(!OrderSelect(i, SELECT_BY_POS, MODE_TRADES)) continue;
        if(OrderSymbol() != Symbol()) continue;
        if(OrderMagicNumber() == target_magic) {
            // Check comment có "BONUS" không
            if(StringFind(OrderComment(), "BONUS") >= 0) {
                return true;
            }
        }
    }
    return false;
}
```

**2. Tính P&L của BONUS orders:**
```cpp
double GetBonusOrdersPnL(int tf) {
    double total_pnl = 0;
    int target_magic = g_ea.magic_numbers[tf][2];
    for(int i = 0; i < OrdersTotal(); i++) {
        if(!OrderSelect(i, SELECT_BY_POS, MODE_TRADES)) continue;
        if(OrderSymbol() != Symbol()) continue;
        if(OrderMagicNumber() == target_magic) {
            if(StringFind(OrderComment(), "BONUS") >= 0) {
                total_pnl += OrderProfit() + OrderSwap() + OrderCommission();
            }
        }
    }
    return total_pnl;
}
```

**3. Format BONUS status line:**
```cpp
string FormatBonusStatus() {
    if(!EnableBonusNews) return "BONUS: Disabled";

    string bonus_list = "";
    string status = "IDLE";
    int total_bonus_orders = 0;
    double total_bonus_pnl = 0;

    // Check có lệnh BONUS đang mở
    for(int tf = 0; tf < 7; tf++) {
        if(!IsTFEnabled(tf)) continue;

        if(HasBonusOrders(tf)) {
            status = "OPEN";
            total_bonus_orders++;
            total_bonus_pnl += GetBonusOrdersPnL(tf);

            int news = g_ea.csdl_rows[tf].news;
            string arrow = (news > 0) ? "^" : "v";
            bonus_list += G_TF_NAMES[tf] + "(" + IntegerToString(BonusOrderCount) + "x " +
                         (news > 0 ? "+" : "") + IntegerToString(news) + arrow + ") ";
        }
    }

    // Nếu không có lệnh mở, check TF nào đủ điều kiện
    if(status == "IDLE") {
        for(int tf = 0; tf < 7; tf++) {
            if(!IsTFEnabled(tf)) continue;

            int news_abs = MathAbs(g_ea.csdl_rows[tf].news);
            if(news_abs >= MinNewsLevelBonus) {
                status = "WAIT";
                int news = g_ea.csdl_rows[tf].news;
                string arrow = (news > 0) ? "^" : "v";
                bonus_list += G_TF_NAMES[tf] + "(" + IntegerToString(BonusOrderCount) + "x " +
                             (news > 0 ? "+" : "") + IntegerToString(news) + arrow + ") ";
            }
        }
    }

    if(bonus_list == "") bonus_list = "None";

    // Get last open time (cần track trong g_ea hoặc scan OrderOpenTime)
    string last_time = "--:--:--";

    string result = "BONUS: " + bonus_list + " | " + status + " | Last:" + last_time;

    if(status == "OPEN" && total_bonus_pnl != 0) {
        result += " | P&L:";
        if(total_bonus_pnl > 0) result += "+";
        result += "$" + DoubleToStr(total_bonus_pnl, 2);
    }

    return result;
}
```

---

## V. IMPLEMENTATION SUMMARY

### Changes to Make:

**1. Modify `UpdateDashboard()` function:**
```cpp
void UpdateDashboard() {
    if(!ShowDashboard) {
        for(int i = 0; i <= 11; i++) ObjectDelete("dash_" + IntegerToString(i));
        return;
    }

    int y_start = 150;
    int line_height = 14;
    int y_pos = y_start;

    // Line 0: HEADER (compact)
    string header = "[" + g_ea.symbol_name + "] " + folder + " | 7TFx3S | D1:" +
                    trend_char + " News:" + IntegerToString(g_ea.news_level) + news_char +
                    " | $" + DoubleToStr(equity, 0) + " DD:" + DoubleToStr(dd, 1) + "% | " +
                    IntegerToString(total_orders) + "/21";
    CreateOrUpdateLabel("dash_0", header, 10, y_pos, clrWhite, 9);
    y_pos += line_height;

    // Line 1: COLUMN HEADERS
    string col_header = PadRight("TF", 4) + PadRight("Sig", 5) + PadRight("S1", 7) +
                        PadRight("S2", 7) + PadRight("S3", 7) + PadRight("P&L", 8) + "News";
    CreateOrUpdateLabel("dash_1", col_header, 10, y_pos, clrWhite, 9);
    y_pos += line_height;

    // Lines 2-8: 7 TF ROWS
    for(int tf = 0; tf < 7; tf++) {
        // Calculate P&L for this TF
        double tf_pnl = CalculateTFPnL(tf);

        // Signal
        int sig = g_ea.csdl_rows[tf].signal;
        string sig_str = (sig == 1) ? "^" : (sig == -1) ? "v" : "-";

        // S1/S2/S3
        string s1 = (g_ea.position_flags[tf][0] == 1) ? "*" + DoubleToStr(g_ea.lot_sizes[tf][0], 2) : "o";
        string s2 = (g_ea.position_flags[tf][1] == 1) ? "*" + DoubleToStr(g_ea.lot_sizes[tf][1], 2) : "o";
        string s3 = (g_ea.position_flags[tf][2] == 1) ? "*" + DoubleToStr(g_ea.lot_sizes[tf][2], 2) : "o";

        // P&L
        string pnl_str = (tf_pnl > 0 ? "+" : "") + DoubleToStr(tf_pnl, 2);

        // News
        int news = g_ea.csdl_rows[tf].news;
        string news_str = (news > 0 ? "+" : "") + IntegerToString(news);

        // Build row
        string row = PadRight(G_TF_NAMES[tf], 4) + PadRight(sig_str, 5) + PadRight(s1, 7) +
                     PadRight(s2, 7) + PadRight(s3, 7) + PadRight(pnl_str, 8) + news_str;

        // Alternating colors
        color row_color = (tf % 2 == 0) ? clrDodgerBlue : clrWhite;
        CreateOrUpdateLabel("dash_" + IntegerToString(2 + tf), row, 10, y_pos, row_color, 9);
        y_pos += line_height;
    }

    // Line 9: BONUS STATUS
    string bonus_line = FormatBonusStatus();
    CreateOrUpdateLabel("dash_9", bonus_line, 10, y_pos, clrWhite, 9);
    y_pos += line_height;

    // Line 10: P&L SUMMARY (compact)
    string summary = "NET:$" + DoubleToStr(net, 2) + " | " +
                     "S1:" + IntegerToString(s1_count) + "x$" + DoubleToStr(s1_pnl, 0) + " " +
                     "S2:" + IntegerToString(s2_count) + "x$" + DoubleToStr(s2_pnl, 0) + " " +
                     "S3:" + IntegerToString(s3_count) + "x$" + DoubleToStr(s3_pnl, 1) + " | " +
                     IntegerToString(total_orders) + "/21";
    CreateOrUpdateLabel("dash_10", summary, 10, y_pos, clrYellow, 9);
    y_pos += line_height;

    // Line 11: BROKER INFO
    string broker_info = broker + "-" + StringSubstr(server, 0, 10) + " | Lev:1:" +
                        IntegerToString(leverage) + " | 2s";
    CreateOrUpdateLabel("dash_11", broker_info, 10, y_pos, clrYellow, 9);
}
```

**2. Add helper function:**
```cpp
double CalculateTFPnL(int tf) {
    double total_pnl = 0;
    for(int s = 0; s < 3; s++) {
        if(g_ea.position_flags[tf][s] != 1) continue;

        int target_magic = g_ea.magic_numbers[tf][s];
        for(int i = 0; i < OrdersTotal(); i++) {
            if(!OrderSelect(i, SELECT_BY_POS, MODE_TRADES)) continue;
            if(OrderSymbol() != Symbol()) continue;
            if(OrderMagicNumber() == target_magic) {
                total_pnl += OrderProfit() + OrderSwap() + OrderCommission();
            }
        }
    }
    return total_pnl;
}
```

---

## VI. FINAL COMPARISON

### CŨ (16 lines):
```
[LTCUSD] DA2 | 7TFx3S=21 | Trend:D1[^] News:Lv45[^] | Eq:$5000 DD:2.3%
-------------------------------------------------------------
TF   Signal  S1      S2      S3      Age   DPrice  News
-------------------------------------------------------------
M1   [^]     *0.05   o       *0.02   15s   +2.3    +55
M5    v      o       *0.10   o       2m    -1.5    -30
...
-------------------------------------------------------------
Orders:8/21 | Net:$235.50 | Profit:+$280.00 Loss:$-44.50 | 2s
S1 Orders: M1=$12.30 M15=$45.20 H1=$-8.50 D1=$15.80 +3 more
S2+S3 Orders: M5=$-25.00 M15=$50.00 H4=$80.00 +2 more
Exness | Server:ExnessReal-12 | Leverage:1:500
```

### MỚI (12 lines):
```
[LTCUSD] DA2 | 7TFx3S | D1:^ News:45^ | $5000 DD:2.3% | 8/21
TF   Sig  S1     S2     S3     P&L     News
M1   ^    *0.05  o      *0.02  +12.30  +55
M5   v    o      *0.10  o      -25.00  -30
...
BONUS: M1(5x +65^) H1(3x +58^) | WAIT | Last:15:30:45
NET:$235.50 | S1:5x$140 S2:2x$55 S3:1x$40.5 | 8/21
Exness-Real12 | Lev:1:500 | 2s
```

**Improvements:**
- ✅ Giảm 16→12 lines (25% nhỏ gọn)
- ✅ Thêm P&L per TF
- ✅ Thêm BONUS status (mới)
- ✅ Compact summary
- ✅ Chỉ dùng ASCII: ^ v + - * o
- ✅ Giữ màu cũ: BLUE/WHITE xen kẽ, YELLOW footer

---

**READY TO IMPLEMENT?** 🚀
