"""
Language model interface for generating text responses.

Provides a wrapper around Google's Gemini API for consistent
language model interactions throughout the application.
"""
import os
import json
import re
import google.generativeai as genai
from typing import Optional, Any, List, Dict
from dotenv import load_dotenv

load_dotenv()

class LLM:
    """
    Language model client for text generation.
    
    Wraps Google Gemini API with configured safety settings and
    generation parameters for research analysis tasks.
    """
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in .env")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
    
    def call(self, prompt: str, max_tokens: int = 1024) -> str:
        """
        Generate text response from language model.
        
        Args:
            prompt: Input text prompt
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.7
                ),
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                ]
            )
            
            if not response.candidates:
                return "Error: No candidates in response"
            
            candidate = response.candidates[0]
            finish_reason = getattr(candidate, 'finish_reason', None)
            
            # Extract text from response, trying multiple access patterns for API compatibility
            try:
                text = response.text
                if text:
                    return text
            except (ValueError, AttributeError):
                pass
            
            # Fallback to content.parts structure if direct text access fails
            if hasattr(candidate, 'content') and candidate.content:
                parts = getattr(candidate.content, 'parts', [])
                if parts:
                    text_parts = []
                    for part in parts:
                        if hasattr(part, 'text') and part.text:
                            text_parts.append(part.text)
                    if text_parts:
                        return ''.join(text_parts)
            
            # Handle API-specific finish reasons
            if finish_reason == 2:  # MAX_TOKENS
                return "Error: Response truncated - increase max_tokens"
            elif finish_reason == 3:  # SAFETY
                return "Error: Blocked by safety filters"
            
            return f"Error: Could not extract text (finish_reason: {finish_reason})"
                
        except Exception as e:
            return f"Error: {e}"
    
    def extract_json(self, text: str) -> Optional[Any]:
        """Extract JSON from response with improved parsing"""
        if not text or text.startswith("Error:"):
            return None

        text = text.strip()

        # Attempt direct parsing first
        try:
            return json.loads(text)
        except:
            pass

        # Extract JSON from markdown code blocks
        match = re.search(r'```(?:json)?\s*(\[.*?\]|\{.*?\})\s*```', text, re.DOTALL)
        if match:
            try:
                json_str = match.group(1).strip()
                json_str = self._clean_json(json_str)
                return json.loads(json_str)
            except Exception as e:
                print(f"JSON parse error in code block: {e}")
                pass

        # Extract JSON array using bracket matching to handle nested structures
        match = re.search(r'(\[[\s\S]*\])', text)
        if match:
            try:
                json_str = match.group(1).strip()
                json_str = self._clean_json(json_str)
                # Find array boundaries by counting brackets to handle nesting
                bracket_count = 0
                end_pos = 0
                for i, char in enumerate(json_str):
                    if char == '[':
                        bracket_count += 1
                    elif char == ']':
                        bracket_count -= 1
                        if bracket_count == 0:
                            end_pos = i + 1
                            break
                if end_pos > 0:
                    json_str = json_str[:end_pos]
                return json.loads(json_str)
            except Exception as e:
                print(f"JSON parse error in array: {e}")
                pass

        # Extract JSON object using brace matching to handle nested structures
        match = re.search(r'(\{[\s\S]*\})', text)
        if match:
            try:
                json_str = match.group(1).strip()
                json_str = self._clean_json(json_str)
                # Find object boundaries by counting braces to handle nesting
                brace_count = 0
                end_pos = 0
                for i, char in enumerate(json_str):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_pos = i + 1
                            break
                if end_pos > 0:
                    json_str = json_str[:end_pos]
                return json.loads(json_str)
            except Exception as e:
                print(f"JSON parse error in object: {e}")
                pass

        print(f"No valid JSON found in response (length: {len(text)})")
        return None

    def _clean_json(self, json_str: str) -> str:
        """
        Clean JSON string by removing common formatting issues.
        
        Handles trailing commas, comments, and control characters that
        can cause JSON parsing failures in API responses.
        """
        # Remove trailing commas before closing braces/brackets
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)
        # Remove single-line and multi-line comments
        json_str = re.sub(r'//.*?\n', '\n', json_str)
        json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
        # Filter out control characters that invalidate JSON
        json_str = ''.join(char for char in json_str if ord(char) >= 32 or char in '\n\r\t')
        return json_str

