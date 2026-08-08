import os
import sys
import unittest

# Ensure backend import path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.database import init_db
from backend.services.memory_service import MemoryService
from backend.services.agent import AgentOrchestrator
from backend.services.proactive_engine import ProactiveIntelligenceEngine
from backend.services.tools import FinancialTools
from backend.services.normalizer import ChannelNormalizer

class TestAtlasBackend(unittest.TestCase):
    def setUp(self):
        init_db()
        self.user = MemoryService.get_or_create_user(9999, "Test Analyst")

    def test_ambiguity_clarification(self):
        """Blueprint requirement: Ambiguous requests trigger single clarifying question."""
        res = AgentOrchestrator.process_message(self.user["id"], "Tell me about Apple")
        self.assertTrue(res.get("clarification_asked"))
        self.assertIn("would you like the latest market news", res["response"])

    def test_realtime_quote_and_fundamentals(self):
        """Test real-time price quotes and fundamental metrics."""
        quote = FinancialTools.get_quote("NVDA")
        self.assertEqual(quote["status"], "success")
        self.assertEqual(quote["ticker"], "NVDA")
        self.assertIn("price", quote)
        
        fund = FinancialTools.get_fundamentals("NVDA")
        self.assertEqual(fund["status"], "success")
        self.assertIn("market_cap", fund)

    def test_side_by_side_comparison(self):
        """Test entity comparison tool."""
        res = AgentOrchestrator.process_message(self.user["id"], "Compare MSFT vs GOOGL")
        self.assertEqual(res["intent"], "comparison")
        self.assertIn("Side-by-Side: MSFT vs GOOGL", res["response"])

    def test_channel_normalizer(self):
        """Test one brain many senses channel normalization."""
        norm_voice = ChannelNormalizer.normalize_input("voice", "Check NVDA filing")
        self.assertEqual(norm_voice["channel"], "voice")
        self.assertIn("clean_text", norm_voice)

        norm_image = ChannelNormalizer.normalize_input("image", "")
        self.assertEqual(norm_image["channel"], "image")
        self.assertIn("OCR Extracted", norm_image["clean_text"])

    def test_proactive_silence(self):
        """Blueprint requirement: Silence as a feature on quiet days."""
        brief_quiet = ProactiveIntelligenceEngine.generate_daily_brief(self.user["id"], force=False)
        # Should be quiet day or material brief
        self.assertIn("sent", brief_quiet)

if __name__ == "__main__":
    unittest.main()
