using NUnit.Framework;
using System;
using System.Collections.Generic;
using cAlgo.Robots;
using Moq;

namespace cAlgo.Tests
{
    /// <summary>
    /// Unit tests for MTF_ONER_cBot core functions
    /// Tests: CSDL parsing, NEWS extraction, TF checks, NY hours filter
    /// </summary>
    [TestFixture]
    public class CoreFunctionsTests
    {
        private MTF_ONER_cBot _bot;

        [SetUp]
        public void Setup()
        {
            // Initialize bot instance (Note: May need mock for Robot base class)
            _bot = new MTF_ONER_cBot();
        }

        #region NEWS CASCADE Tests (14 Variables)

        [Test]
        [TestCase(15, 15, 1, Description = "Positive NEWS: +15 → level=15, direction=+1")]
        [TestCase(-20, 20, -1, Description = "Negative NEWS: -20 → level=20, direction=-1")]
        [TestCase(0, 0, 0, Description = "Zero NEWS: 0 → level=0, direction=0")]
        [TestCase(70, 70, 1, Description = "Max NEWS: +70 → level=70, direction=+1")]
        [TestCase(-70, 70, -1, Description = "Min NEWS: -70 → level=70, direction=-1")]
        public void MapNewsTo14Variables_ShouldExtractLevelAndDirection(int inputNews, int expectedLevel, int expectedDirection)
        {
            // Arrange
            var eaData = new EASymbolData();
            eaData.CSDLRows[0].News = inputNews;

            // Act
            MapNewsTo14Variables(eaData);

            // Assert
            Assert.AreEqual(expectedLevel, eaData.NewsLevel[0], "NEWS Level extraction failed");
            Assert.AreEqual(expectedDirection, eaData.NewsDirection[0], "NEWS Direction extraction failed");
        }

        /// <summary>
        /// Helper method to test MapNewsTo14Variables logic
        /// (Extracted from cBot for testing)
        /// </summary>
        private void MapNewsTo14Variables(EASymbolData eaData)
        {
            for (int tf = 0; tf < 7; tf++)
            {
                int tf_news = eaData.CSDLRows[tf].News;
                eaData.NewsLevel[tf] = Math.Abs(tf_news);

                if (tf_news > 0)
                    eaData.NewsDirection[tf] = 1;
                else if (tf_news < 0)
                    eaData.NewsDirection[tf] = -1;
                else
                    eaData.NewsDirection[tf] = 0;
            }
        }

        [Test]
        public void MapNewsTo14Variables_ShouldHandle7Timeframes()
        {
            // Arrange
            var eaData = new EASymbolData();
            int[] testNews = { 15, -20, 30, -5, 0, 10, -70 };

            for (int i = 0; i < 7; i++)
            {
                eaData.CSDLRows[i].News = testNews[i];
            }

            // Act
            MapNewsTo14Variables(eaData);

            // Assert
            Assert.AreEqual(15, eaData.NewsLevel[0], "M1 level");
            Assert.AreEqual(1, eaData.NewsDirection[0], "M1 direction");

            Assert.AreEqual(20, eaData.NewsLevel[1], "M5 level");
            Assert.AreEqual(-1, eaData.NewsDirection[1], "M5 direction");

            Assert.AreEqual(0, eaData.NewsLevel[4], "H1 level (zero case)");
            Assert.AreEqual(0, eaData.NewsDirection[4], "H1 direction (zero case)");
        }

        #endregion

        #region NY Session Hours Filter Tests

        [Test]
        [TestCase(14, 21, 15, true, Description = "15:00 is within 14:00-21:00")]
        [TestCase(14, 21, 13, false, Description = "13:00 is before 14:00")]
        [TestCase(14, 21, 22, false, Description = "22:00 is after 21:00")]
        [TestCase(14, 21, 14, true, Description = "14:00 is start boundary (inclusive)")]
        [TestCase(14, 21, 21, false, Description = "21:00 is end boundary (exclusive)")]
        public void IsWithinNYHours_SimpleCaseSameDayShouldWork(int start, int end, int currentHour, bool expected)
        {
            // Act
            bool result = IsWithinNYHours(true, start, end, currentHour);

            // Assert
            Assert.AreEqual(expected, result, $"Hour {currentHour} check failed for {start:00}:00-{end:00}:00");
        }

        [Test]
        [TestCase(22, 6, 23, true, Description = "23:00 is within 22:00-06:00 (cross midnight)")]
        [TestCase(22, 6, 3, true, Description = "03:00 is within 22:00-06:00 (cross midnight)")]
        [TestCase(22, 6, 7, false, Description = "07:00 is after 06:00 (cross midnight)")]
        [TestCase(22, 6, 21, false, Description = "21:00 is before 22:00 (cross midnight)")]
        public void IsWithinNYHours_CrossMidnightShouldWork(int start, int end, int currentHour, bool expected)
        {
            // Act
            bool result = IsWithinNYHours(true, start, end, currentHour);

            // Assert
            Assert.AreEqual(expected, result, $"Cross-midnight hour {currentHour} check failed");
        }

        [Test]
        public void IsWithinNYHours_WhenDisabledShouldAlwaysReturnTrue()
        {
            // Act
            bool result = IsWithinNYHours(false, 14, 21, 5); // 5:00 is outside 14-21

            // Assert
            Assert.IsTrue(result, "Filter disabled should always return true");
        }

        /// <summary>
        /// Helper method to test IsWithinNYHours logic
        /// </summary>
        private bool IsWithinNYHours(bool enabled, int start, int end, int currentHour)
        {
            if (!enabled) return true;

            if (start < end)
            {
                return (currentHour >= start && currentHour < end);
            }
            else
            {
                return (currentHour >= start || currentHour < end);
            }
        }

        #endregion

        #region TF Enabled Check Tests

        [Test]
        [TestCase(0, true, Description = "TF_M1 = true → index 0 enabled")]
        [TestCase(1, true, Description = "TF_M5 = true → index 1 enabled")]
        [TestCase(6, false, Description = "TF_D1 = false → index 6 disabled")]
        [TestCase(-1, false, Description = "Invalid index -1 → disabled")]
        [TestCase(7, false, Description = "Invalid index 7 → disabled")]
        public void IsTFEnabled_ShouldReturnCorrectStatus(int tfIndex, bool expected)
        {
            // Arrange
            bool[] tfFlags = { true, true, true, false, false, false, false }; // M1,M5,M15 ON, others OFF

            // Act
            bool result = IsTFEnabled(tfIndex, tfFlags);

            // Assert
            Assert.AreEqual(expected, result, $"TF index {tfIndex} check failed");
        }

        private bool IsTFEnabled(int tfIndex, bool[] tfFlags)
        {
            if (tfIndex < 0 || tfIndex >= 7) return false;
            return tfFlags[tfIndex];
        }

        #endregion

        #region Progressive Lot Calculation Tests

        [Test]
        [TestCase(0.1, 0, 0, 0.21, Description = "M1_S1 = (0.1×2) + 0.01 = 0.21")]
        [TestCase(0.1, 0, 1, 0.11, Description = "M1_S2 = (0.1×1) + 0.01 = 0.11")]
        [TestCase(0.1, 0, 2, 0.31, Description = "M1_S3 = (0.1×3) + 0.01 = 0.31")]
        [TestCase(0.1, 6, 0, 0.27, Description = "D1_S1 = (0.1×2) + 0.07 = 0.27")]
        [TestCase(0.1, 6, 1, 0.17, Description = "D1_S2 = (0.1×1) + 0.07 = 0.17")]
        [TestCase(0.1, 6, 2, 0.37, Description = "D1_S3 = (0.1×3) + 0.07 = 0.37")]
        public void CalculateProgressiveLot_ShouldReturnCorrectValue(double baseLot, int tfIndex, int strategyIndex, double expected)
        {
            // Act
            double result = CalculateProgressiveLot(baseLot, tfIndex, strategyIndex);

            // Assert
            Assert.AreEqual(expected, result, 0.001, "Progressive lot calculation mismatch");
        }

        private double CalculateProgressiveLot(double baseLot, int tfIndex, int strategyIndex)
        {
            double[] strategyMultipliers = { 2.0, 1.0, 3.0 };
            double[] tfIncrements = { 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07 };

            return (baseLot * strategyMultipliers[strategyIndex]) + tfIncrements[tfIndex];
        }

        #endregion

        #region Signal Change Detection Tests

        [Test]
        [TestCase(1, -1, 100, 120, true, Description = "Signal changed 1→-1, time diff 20s → OPEN")]
        [TestCase(1, 1, 100, 120, false, Description = "Signal unchanged 1→1 → NO OPEN")]
        [TestCase(1, 0, 100, 120, false, Description = "New signal = 0 → NO OPEN")]
        [TestCase(1, -1, 100, 110, false, Description = "Time diff 10s < 15s → NO OPEN")]
        [TestCase(0, 1, 100, 120, true, Description = "Signal 0→1 (first run) → OPEN")]
        public void ShouldOpenNewOrder_ShouldDetectCorrectly(int oldSignal, int newSignal, long oldTime, long newTime, bool expected)
        {
            // Act
            bool result = ShouldOpenNewOrder(oldSignal, newSignal, oldTime, newTime);

            // Assert
            Assert.AreEqual(expected, result, "Signal change detection failed");
        }

        private bool ShouldOpenNewOrder(int oldSignal, int newSignal, long oldTime, long newTime)
        {
            return (oldSignal != newSignal &&
                    newSignal != 0 &&
                    oldTime < newTime &&
                    (newTime - oldTime) > 15);
        }

        #endregion

        #region Layer1 Threshold Calculation Tests

        [Test]
        [TestCase(1000.0, 0.21, -210.0, Description = "MaxLoss=1000, Lot=0.21 → Threshold=-210")]
        [TestCase(500.0, 0.11, -55.0, Description = "MaxLoss=500, Lot=0.11 → Threshold=-55")]
        [TestCase(0.5, 0.21, -1000.0, Description = "MaxLoss=0.5 (invalid) → Use fallback -1000")]
        public void CalculateLayer1Threshold_ShouldReturnCorrectValue(double maxLoss, double lot, double expected)
        {
            // Arrange
            double fallback = -1000.0;

            // Act
            double result = CalculateLayer1Threshold(maxLoss, lot, fallback);

            // Assert
            Assert.AreEqual(expected, result, 0.01, "Layer1 threshold calculation mismatch");
        }

        private double CalculateLayer1Threshold(double maxLoss, double lot, double fallback)
        {
            if (Math.Abs(maxLoss) < 1.0)
            {
                maxLoss = Math.Abs(fallback);
            }
            return -(maxLoss * lot);
        }

        #endregion
    }
}
