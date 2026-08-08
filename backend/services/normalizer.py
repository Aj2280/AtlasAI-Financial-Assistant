import base64

class ChannelNormalizer:
    @staticmethod
    def normalize_input(channel_type: str, content: str, media_data: str = None) -> dict:
        """
        Normalizes input across text, voice, and image channels into a unified format.
        """
        channel_type = channel_type.lower().strip()
        
        if channel_type == "text":
            return {
                "channel": "text",
                "clean_text": content.strip(),
                "raw_content": content,
                "metadata": {}
            }
            
        elif channel_type == "voice":
            # Simulated Speech-To-Text (Whisper transcription)
            transcription = content if content else "[Voice Note Transcribed]: Can you give me today's price action on Nvidia and check if there are any recent SEC filings?"
            return {
                "channel": "voice",
                "clean_text": transcription,
                "raw_content": content,
                "metadata": {"stt_engine": "Whisper-v3", "confidence": 0.98}
            }
            
        elif channel_type == "image":
            # Vision / OCR extraction pass
            extracted_text = content if content else "[OCR Extracted from Chart/Filing]: Q3 Revenue $30.0B, Gross Margin 75.1%, Data Center revenue $26.3B, up 154% YoY."
            return {
                "channel": "image",
                "clean_text": extracted_text,
                "raw_content": content,
                "metadata": {"ocr_engine": "Claude Vision + Tesseract", "extracted_tables_count": 1}
            }
            
        else:
            return {
                "channel": "unknown",
                "clean_text": content,
                "raw_content": content,
                "metadata": {}
            }
