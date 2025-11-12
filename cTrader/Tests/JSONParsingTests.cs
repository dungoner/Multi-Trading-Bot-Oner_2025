using NUnit.Framework;
using System;
using Newtonsoft.Json;
using cAlgo.Robots;

namespace cAlgo.Tests
{
    /// <summary>
    /// Unit tests for CSDL JSON parsing
    /// Tests: JSON structure validation, field extraction, error handling
    /// </summary>
    [TestFixture]
    public class JSONParsingTests
    {
        #region Valid JSON Tests

        [Test]
        public void ParseCSDLJSON_ValidData_ShouldExtractAllFields()
        {
            // Arrange
            string validJSON = @"[
                {""max_loss"": 1000.0, ""timestamp"": 1699876543, ""signal"": 1, ""pricediff"": 0.0, ""timediff"": 0, ""news"": 15},
                {""max_loss"": 950.0, ""timestamp"": 1699876544, ""signal"": -1, ""pricediff"": 0.0, ""timediff"": 0, ""news"": -20},
                {""max_loss"": 900.0, ""timestamp"": 1699876545, ""signal"": 0, ""pricediff"": 0.0, ""timediff"": 0, ""news"": 0},
                {""max_loss"": 850.0, ""timestamp"": 1699876546, ""signal"": 1, ""pricediff"": 0.0, ""timediff"": 0, ""news"": 30},
                {""max_loss"": 800.0, ""timestamp"": 1699876547, ""signal"": -1, ""pricediff"": 0.0, ""timediff"": 0, ""news"": -5},
                {""max_loss"": 750.0, ""timestamp"": 1699876548, ""signal"": 1, ""pricediff"": 0.0, ""timediff"": 0, ""news"": 10},
                {""max_loss"": 700.0, ""timestamp"": 1699876549, ""signal"": -1, ""pricediff"": 0.0, ""timediff"": 0, ""news"": -70}
            ]";

            var eaData = new EASymbolData();

            // Act
            bool result = ParseCSDLJSON(validJSON, eaData);

            // Assert
            Assert.IsTrue(result, "Parsing should succeed");

            // Verify M1 (index 0)
            Assert.AreEqual(1000.0, eaData.CSDLRows[0].MaxLoss, 0.01, "M1 MaxLoss");
            Assert.AreEqual(1699876543, eaData.CSDLRows[0].Timestamp, "M1 Timestamp");
            Assert.AreEqual(1, eaData.CSDLRows[0].Signal, "M1 Signal");
            Assert.AreEqual(15, eaData.CSDLRows[0].News, "M1 News");

            // Verify M5 (index 1)
            Assert.AreEqual(-1, eaData.CSDLRows[1].Signal, "M5 Signal");
            Assert.AreEqual(-20, eaData.CSDLRows[1].News, "M5 News");

            // Verify D1 (index 6)
            Assert.AreEqual(700.0, eaData.CSDLRows[6].MaxLoss, 0.01, "D1 MaxLoss");
            Assert.AreEqual(-70, eaData.CSDLRows[6].News, "D1 News");
        }

        #endregion

        #region Invalid JSON Tests

        [Test]
        public void ParseCSDLJSON_InvalidJSON_ShouldReturnFalse()
        {
            // Arrange
            string invalidJSON = "{this is not valid json}";
            var eaData = new EASymbolData();

            // Act
            bool result = ParseCSDLJSON(invalidJSON, eaData);

            // Assert
            Assert.IsFalse(result, "Parsing should fail for invalid JSON");
        }

        [Test]
        public void ParseCSDLJSON_NotArray_ShouldReturnFalse()
        {
            // Arrange
            string notArrayJSON = @"{""max_loss"": 1000.0}";
            var eaData = new EASymbolData();

            // Act
            bool result = ParseCSDLJSON(notArrayJSON, eaData);

            // Assert
            Assert.IsFalse(result, "Parsing should fail for non-array JSON");
        }

        [Test]
        public void ParseCSDLJSON_EmptyArray_ShouldReturnFalse()
        {
            // Arrange
            string emptyJSON = "[]";
            var eaData = new EASymbolData();

            // Act
            bool result = ParseCSDLJSON(emptyJSON, eaData);

            // Assert
            Assert.IsFalse(result, "Parsing should fail for empty array");
        }

        [Test]
        public void ParseCSDLJSON_LessThan7Rows_ShouldParseAvailable()
        {
            // Arrange
            string partialJSON = @"[
                {""max_loss"": 1000.0, ""timestamp"": 1699876543, ""signal"": 1, ""pricediff"": 0.0, ""timediff"": 0, ""news"": 15},
                {""max_loss"": 950.0, ""timestamp"": 1699876544, ""signal"": -1, ""pricediff"": 0.0, ""timediff"": 0, ""news"": -20}
            ]";

            var eaData = new EASymbolData();

            // Act
            bool result = ParseCSDLJSON(partialJSON, eaData);

            // Assert
            Assert.IsTrue(result, "Should parse successfully even with < 7 rows");
            Assert.AreEqual(1000.0, eaData.CSDLRows[0].MaxLoss, 0.01, "First row parsed");
            Assert.AreEqual(950.0, eaData.CSDLRows[1].MaxLoss, 0.01, "Second row parsed");
        }

        [Test]
        public void ParseCSDLJSON_MissingFields_ShouldUseDefaults()
        {
            // Arrange
            string missingFieldsJSON = @"[
                {""signal"": 1, ""news"": 15},
                {""max_loss"": 950.0},
                {""timestamp"": 1699876545, ""signal"": -1},
                {""max_loss"": 850.0, ""timestamp"": 1699876546, ""signal"": 1, ""pricediff"": 0.0, ""timediff"": 0, ""news"": 30},
                {""max_loss"": 800.0, ""timestamp"": 1699876547, ""signal"": -1, ""pricediff"": 0.0, ""timediff"": 0, ""news"": -5},
                {""max_loss"": 750.0, ""timestamp"": 1699876548, ""signal"": 1, ""pricediff"": 0.0, ""timediff"": 0, ""news"": 10},
                {""max_loss"": 700.0, ""timestamp"": 1699876549, ""signal"": -1, ""pricediff"": 0.0, ""timediff"": 0, ""news"": -70}
            ]";

            var eaData = new EASymbolData();

            // Act
            bool result = ParseCSDLJSON(missingFieldsJSON, eaData);

            // Assert
            Assert.IsTrue(result, "Should handle missing fields with defaults");

            // Row 0: missing max_loss and timestamp
            Assert.AreEqual(0.0, eaData.CSDLRows[0].MaxLoss, "Default MaxLoss = 0.0");
            Assert.AreEqual(0, eaData.CSDLRows[0].Timestamp, "Default Timestamp = 0");
            Assert.AreEqual(1, eaData.CSDLRows[0].Signal, "Signal present");
            Assert.AreEqual(15, eaData.CSDLRows[0].News, "News present");

            // Row 1: missing most fields
            Assert.AreEqual(950.0, eaData.CSDLRows[1].MaxLoss, 0.01, "MaxLoss present");
            Assert.AreEqual(0, eaData.CSDLRows[1].Signal, "Default Signal = 0");
        }

        #endregion

        #region Helper Method

        /// <summary>
        /// Helper method to test ParseCSDLJSON logic
        /// (Extracted and simplified from cBot)
        /// </summary>
        private bool ParseCSDLJSON(string jsonContent, EASymbolData eaData)
        {
            try
            {
                dynamic jsonArray = JsonConvert.DeserializeObject(jsonContent);

                if (jsonArray == null)
                    return false;

                // Check if it's an array
                if (!(jsonArray is Newtonsoft.Json.Linq.JArray))
                    return false;

                int parsedCount = 0;

                for (int i = 0; i < 7 && i < jsonArray.Count; i++)
                {
                    var row = jsonArray[i];

                    eaData.CSDLRows[i].MaxLoss = (double)(row.max_loss ?? 0.0);
                    eaData.CSDLRows[i].Timestamp = (long)(row.timestamp ?? 0);
                    eaData.CSDLRows[i].Signal = (int)(row.signal ?? 0);
                    eaData.CSDLRows[i].PriceDiff = (double)(row.pricediff ?? 0.0);
                    eaData.CSDLRows[i].TimeDiff = (int)(row.timediff ?? 0);
                    eaData.CSDLRows[i].News = (int)(row.news ?? 0);

                    parsedCount++;
                }

                return parsedCount >= 1;
            }
            catch
            {
                return false;
            }
        }

        #endregion
    }
}
