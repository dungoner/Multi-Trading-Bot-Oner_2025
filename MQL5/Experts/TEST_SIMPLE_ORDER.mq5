//+------------------------------------------------------------------+
//| TEST_SIMPLE_ORDER.mq5 - CHỈ MỞ 1 LỆNH MUA ĐƠN GIẢN               |
//| Purpose: Test if MT5 can open orders correctly                   |
//+------------------------------------------------------------------+
#property copyright "Test Simple Order"
#property version   "1.00"
#property strict

// Global flag
bool g_order_opened = false;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   Print("========================================");
   Print("[TEST_INIT] Starting SIMPLE ORDER test");
   Print("[TEST_INIT] Symbol: ", _Symbol);
   Print("[TEST_INIT] Will attempt to open 0.01 lot BUY order");
   Print("========================================");

   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert tick function - Open order once                           |
//+------------------------------------------------------------------+
void OnTick()
{
   if(g_order_opened)
      return;  // Already attempted

   Print("\n[TEST] ======== ATTEMPTING TO OPEN BUY ORDER ========");

   // Prepare trade request
   MqlTradeRequest request = {};
   MqlTradeResult result = {};

   // Get current prices
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   int digits = (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS);

   Print("[TEST] Current Ask: ", NormalizeDouble(ask, digits));
   Print("[TEST] Current Bid: ", NormalizeDouble(bid, digits));

   // Fill request structure - PURE MT5 WAY
   request.action = TRADE_ACTION_DEAL;          // Market order
   request.symbol = _Symbol;                    // Current symbol
   request.volume = 0.01;                       // 0.01 lot
   request.type = ORDER_TYPE_BUY;               // BUY order
   request.price = ask;                         // Current ask price
   request.deviation = 10;                      // 10 points slippage
   request.magic = 999999;                      // Test magic number
   request.comment = "TEST_BUY";                // Comment
   request.type_filling = ORDER_FILLING_FOK;    // Fill or Kill

   Print("[TEST] Request prepared:");
   Print("[TEST]   Action: TRADE_ACTION_DEAL");
   Print("[TEST]   Symbol: ", request.symbol);
   Print("[TEST]   Volume: ", request.volume);
   Print("[TEST]   Type: ORDER_TYPE_BUY");
   Print("[TEST]   Price: ", request.price);
   Print("[TEST]   Magic: ", request.magic);

   // Send order - PURE MT5 WAY
   Print("[TEST] Sending order...");
   bool sent = OrderSend(request, result);

   // Check if request was sent to server
   if(!sent)
   {
      int error = GetLastError();
      Print("[TEST_FAIL] ❌ OrderSend() returned FALSE!");
      Print("[TEST_FAIL] Error code: ", error);
      Print("[TEST_FAIL] Error description: ", ErrorDescription(error));
      g_order_opened = true;
      return;
   }

   Print("[TEST_OK] ✅ OrderSend() returned TRUE (request sent to server)");

   // Check server response
   Print("[TEST] Checking server response...");
   Print("[TEST]   retcode: ", result.retcode);
   Print("[TEST]   deal: ", result.deal);
   Print("[TEST]   order: ", result.order);
   Print("[TEST]   volume: ", result.volume);
   Print("[TEST]   price: ", result.price);
   Print("[TEST]   comment: ", result.comment);

   if(result.retcode != TRADE_RETCODE_DONE)
   {
      Print("[TEST_FAIL] ❌ Order NOT executed!");
      Print("[TEST_FAIL] Return code: ", result.retcode);
      Print("[TEST_FAIL] Server comment: ", result.comment);
      Print("[TEST_FAIL] Return code meaning: ", RetcodeDescription(result.retcode));
      g_order_opened = true;
      return;
   }

   // SUCCESS!
   Print("\n[TEST_SUCCESS] ========================================");
   Print("[TEST_SUCCESS] ✅✅✅ ORDER EXECUTED SUCCESSFULLY! ✅✅✅");
   Print("[TEST_SUCCESS] Deal ticket: ", result.deal);
   Print("[TEST_SUCCESS] Order ticket: ", result.order);
   Print("[TEST_SUCCESS] Executed volume: ", result.volume);
   Print("[TEST_SUCCESS] Executed price: ", result.price);
   Print("[TEST_SUCCESS] ========================================\n");

   g_order_opened = true;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   Print("[TEST_DEINIT] Test EA stopped. Reason: ", reason);
}

//+------------------------------------------------------------------+
//| Error description function                                       |
//+------------------------------------------------------------------+
string ErrorDescription(int error_code)
{
   switch(error_code)
   {
      case 0:    return "No error";
      case 4756: return "Trade context is busy";
      case 4057: return "Error in OrderSend() function";
      case 4108: return "Invalid ticket";
      case 4109: return "Trade is not allowed";
      case 4110: return "Longs are not allowed";
      case 4111: return "Shorts are not allowed";
      case 134:  return "Not enough money";
      case 136:  return "Price off quotes";
      case 138:  return "Requote";
      default:   return "Error code: " + IntegerToString(error_code);
   }
}

//+------------------------------------------------------------------+
//| Return code description function                                 |
//+------------------------------------------------------------------+
string RetcodeDescription(uint retcode)
{
   switch(retcode)
   {
      case 10004: return "TRADE_RETCODE_REQUOTE - Requote";
      case 10006: return "TRADE_RETCODE_REJECT - Request rejected";
      case 10007: return "TRADE_RETCODE_CANCEL - Request canceled by trader";
      case 10008: return "TRADE_RETCODE_PLACED - Order placed";
      case 10009: return "TRADE_RETCODE_DONE - Request completed";
      case 10010: return "TRADE_RETCODE_DONE_PARTIAL - Request completed partially";
      case 10011: return "TRADE_RETCODE_ERROR - Request processing error";
      case 10012: return "TRADE_RETCODE_TIMEOUT - Request timeout";
      case 10013: return "TRADE_RETCODE_INVALID - Invalid request";
      case 10014: return "TRADE_RETCODE_INVALID_VOLUME - Invalid volume";
      case 10015: return "TRADE_RETCODE_INVALID_PRICE - Invalid price";
      case 10016: return "TRADE_RETCODE_INVALID_STOPS - Invalid stops";
      case 10017: return "TRADE_RETCODE_TRADE_DISABLED - Trade disabled";
      case 10018: return "TRADE_RETCODE_MARKET_CLOSED - Market closed";
      case 10019: return "TRADE_RETCODE_NO_MONEY - Not enough money";
      case 10020: return "TRADE_RETCODE_PRICE_CHANGED - Price changed";
      case 10021: return "TRADE_RETCODE_PRICE_OFF - Price off quotes";
      case 10022: return "TRADE_RETCODE_INVALID_EXPIRATION - Invalid order expiration";
      case 10023: return "TRADE_RETCODE_ORDER_CHANGED - Order state changed";
      case 10024: return "TRADE_RETCODE_TOO_MANY_REQUESTS - Too many requests";
      case 10025: return "TRADE_RETCODE_NO_CHANGES - No changes in request";
      case 10026: return "TRADE_RETCODE_SERVER_DISABLES_AT - Autotrading disabled by server";
      case 10027: return "TRADE_RETCODE_CLIENT_DISABLES_AT - Autotrading disabled by client";
      case 10028: return "TRADE_RETCODE_LOCKED - Request locked for processing";
      case 10029: return "TRADE_RETCODE_FROZEN - Order or position frozen";
      case 10030: return "TRADE_RETCODE_INVALID_FILL - Invalid fill type";
      default:    return "Unknown retcode: " + IntegerToString(retcode);
   }
}
