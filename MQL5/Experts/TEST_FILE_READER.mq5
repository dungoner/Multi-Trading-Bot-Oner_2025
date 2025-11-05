//+------------------------------------------------------------------+
//| TEST_FILE_READER.mq5 - CHỈ ĐỌC FILE, IN RA LOG                   |
//| Purpose: Test if MT5 can read CSDL file correctly                |
//+------------------------------------------------------------------+
#property copyright "Test File Reader"
#property version   "1.00"
#property strict

// Input parameters
input string TestFile = "DataAutoOner2\\LTCUSD.txt";  // File to test

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   Print("========================================");
   Print("[TEST_INIT] Starting FILE READ test");
   Print("[TEST_INIT] Target file: ", TestFile);
   Print("[TEST_INIT] Terminal data path: ", TerminalInfoString(TERMINAL_DATA_PATH));
   Print("[TEST_INIT] Common data path: ", TerminalInfoString(TERMINAL_COMMONDATA_PATH));
   Print("========================================");

   // Test file reading immediately
   TestFileRead();

   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Test File Reading Function                                       |
//+------------------------------------------------------------------+
void TestFileRead()
{
   Print("\n[TEST] === STARTING FILE READ TEST ===");

   // Correct MT5 flags for reading text files
   int flags = FILE_READ | FILE_TXT | FILE_ANSI | FILE_SHARE_READ | FILE_SHARE_WRITE;

   Print("[TEST] Opening file with flags: ", flags);
   Print("[TEST] FILE_READ=", FILE_READ, " FILE_TXT=", FILE_TXT,
         " FILE_ANSI=", FILE_ANSI);

   // Try to open file
   int handle = FileOpen(TestFile, flags);

   if(handle == INVALID_HANDLE)
   {
      int error = GetLastError();
      Print("[TEST_FAIL] ❌ Cannot open file!");
      Print("[TEST_FAIL] Error code: ", error);
      Print("[TEST_FAIL] Error description: ", ErrorDescription(error));
      Print("[TEST_FAIL] File path: ", TestFile);
      Print("[TEST_FAIL] Full path should be: ", TerminalInfoString(TERMINAL_DATA_PATH),
            "\\MQL5\\Files\\", TestFile);
      return;
   }

   Print("[TEST_OK] ✅ File opened successfully! Handle: ", handle);

   // Read file line by line
   string content = "";
   int line_count = 0;

   while(!FileIsEnding(handle))
   {
      string line = FileReadString(handle);

      if(StringLen(line) > 0)
      {
        content += line;
         line_count++;

         // Print first 10 lines
         if(line_count <= 10)
         {
            Print("[TEST_LINE_", line_count, "] ", line);
         }
      }
   }

   FileClose(handle);

   Print("\n[TEST_RESULT] ============================");
   Print("[TEST_OK] ✅ File read completed!");
   Print("[TEST_OK] Total lines: ", line_count);
   Print("[TEST_OK] Total characters: ", StringLen(content));

   // Print first 200 characters
   if(StringLen(content) > 0)
   {
      int preview_len = MathMin(200, StringLen(content));
      string preview = StringSubstr(content, 0, preview_len);
      Print("[TEST_OK] First 200 chars: ");
      Print(preview);
   }

   Print("[TEST_RESULT] ============================\n");
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   // Do nothing - this is just a test EA
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
      case 4103: return "Cannot open file";
      case 5004: return "Function not allowed for call";
      case 5019: return "File cannot be opened for writing";
      case 5020: return "File already exists";
      default:   return "Error code: " + IntegerToString(error_code);
   }
}
