"""
AI Email Service for sentiment analysis and automated response drafting
Integrates with OpenAI GPT-4 for intelligent email analysis
"""

import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from decimal import Decimal

from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError

try:
    import openai
except ImportError:
    openai = None

from ..models import Communication, Client, Lead

logger = logging.getLogger(__name__)


class AIAnalysisError(Exception):
    """AI analysis related errors"""
    pass


class AIEmailService:
    """
    Service for AI-powered email analysis and response generation
    """
    
    # OpenAI model configuration
    DEFAULT_MODEL = "gpt-4-turbo-preview"
    FALLBACK_MODEL = "gpt-3.5-turbo"
    MAX_TOKENS = 1000
    TEMPERATURE = 0.3
    
    # Urgency keywords and patterns
    URGENCY_KEYWORDS = [
        'urgent', 'emergency', 'asap', 'immediately', 'crisis', 'help',
        'problem', 'issue', 'deadline', 'time sensitive', 'critical',
        'worried', 'concerned', 'anxious', 'panic', 'stress'
    ]
    
    # Financial topics
    FINANCIAL_TOPICS = [
        'retirement', 'investment', 'portfolio', 'market', 'roth', 'ira',
        'social security', 'pension', 'tax', 'medicare', 'insurance',
        'estate planning', 'will', 'beneficiary', 'annuity', 'bond',
        'stock', 'mutual fund', 'etf', '401k', '403b', 'rollover'
    ]
    
    def __init__(self):
        """Initialize AI service with OpenAI configuration"""
        if not openai:
            raise AIAnalysisError("OpenAI library not installed. Run: pip install openai")
        
        # Configure OpenAI
        api_key = getattr(settings, 'OPENAI_API_KEY', None)
        if not api_key:
            raise AIAnalysisError("OPENAI_API_KEY not configured in settings")
        
        self.client = openai.OpenAI(api_key=api_key)
        self.model_version = getattr(settings, 'OPENAI_MODEL_VERSION', self.DEFAULT_MODEL)
    
    def analyze_communication(self, communication: Communication) -> Dict:
        """
        Perform comprehensive AI analysis of a communication
        
        Args:
            communication: Communication model instance
            
        Returns:
            Dict containing analysis results
        """
        try:
            # Prepare analysis context
            context = self._prepare_analysis_context(communication)
            
            # Perform sentiment analysis
            sentiment_result = self._analyze_sentiment(communication.content, context)
            
            # Detect urgency
            urgency_score = self._detect_urgency(communication.content)
            
            # Extract topics
            topics = self._extract_topics(communication.content)
            
            # Calculate priority score
            priority_score = self._calculate_priority_score(
                sentiment_result, urgency_score, communication
            )
            
            # Generate suggested response if appropriate
            suggested_response = None
            response_confidence = None
            
            if self._should_generate_response(sentiment_result, urgency_score):
                response_result = self._generate_response(communication, context, sentiment_result)
                suggested_response = response_result.get('response')
                response_confidence = response_result.get('confidence')
            
            return {
                'sentiment_score': sentiment_result['score'],
                'sentiment_label': sentiment_result['label'],
                'urgency_score': urgency_score,
                'priority_score': priority_score,
                'topics': topics,
                'suggested_response': suggested_response,
                'response_confidence': response_confidence,
                'analysis_date': timezone.now(),
                'model_version': self.model_version
            }
            
        except Exception as e:
            logger.error(f"AI analysis failed for communication {communication.id}: {str(e)}")
            raise AIAnalysisError(f"AI analysis failed: {str(e)}")
    
    def update_communication_analysis(self, communication: Communication) -> bool:
        """
        Update communication with AI analysis results
        
        Args:
            communication: Communication to analyze
            
        Returns:
            bool: Success status
        """
        try:
            analysis = self.analyze_communication(communication)
            
            # Update communication with analysis results
            communication.ai_sentiment_score = analysis['sentiment_score']
            communication.ai_sentiment_label = analysis['sentiment_label']
            communication.ai_urgency_score = analysis['urgency_score']
            communication.ai_priority_score = analysis['priority_score']
            communication.ai_topics = analysis['topics']
            communication.ai_suggested_response = analysis['suggested_response'] or ''
            communication.ai_response_confidence = analysis['response_confidence']
            communication.ai_analysis_date = analysis['analysis_date']
            communication.ai_model_version = analysis['model_version']
            
            communication.save(update_fields=[
                'ai_sentiment_score', 'ai_sentiment_label', 'ai_urgency_score',
                'ai_priority_score', 'ai_topics', 'ai_suggested_response',
                'ai_response_confidence', 'ai_analysis_date', 'ai_model_version'
            ])
            
            logger.info(f"AI analysis completed for communication {communication.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update communication {communication.id} with AI analysis: {str(e)}")
            return False
    
    def _prepare_analysis_context(self, communication: Communication) -> Dict:
        """Prepare context information for AI analysis"""
        context = {
            'communication_type': communication.communication_type,
            'direction': communication.direction,
            'subject': communication.subject,
        }
        
        # Add client/lead context
        if communication.client:
            context.update({
                'contact_type': 'client',
                'contact_name': f"{communication.client.first_name} {communication.client.last_name}",
                'relationship_duration': self._calculate_relationship_duration(communication.client.created_at),
                'client_value': self._estimate_client_value(communication.client)
            })
        elif communication.lead:
            context.update({
                'contact_type': 'lead',
                'contact_name': f"{communication.lead.first_name} {communication.lead.last_name}",
                'lead_status': communication.lead.status,
                'lead_source': communication.lead.lead_source.name if communication.lead.lead_source else None
            })
        
        return context
    
    def _analyze_sentiment(self, content: str, context: Dict) -> Dict:
        """
        Analyze sentiment using OpenAI API
        
        Returns:
            Dict with 'score' (float -1.0 to 1.0) and 'label' (str)
        """
        try:
            prompt = f"""
            Analyze the sentiment of the following {context.get('communication_type', 'communication')} 
            from a {context.get('contact_type', 'contact')} in the context of financial advisory services.
            
            Content: "{content}"
            
            Provide your analysis as JSON with:
            - "score": float between -1.0 (very negative) and 1.0 (very positive)
            - "label": one of "positive", "negative", "neutral", "mixed"
            - "reasoning": brief explanation of the sentiment
            
            Consider financial advisory context - concerns about money, market volatility, 
            retirement planning are normal but may indicate stress or worry.
            """
            
            response = self.client.chat.completions.create(
                model=self.model_version,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=self.TEMPERATURE
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Validate and clean result
            score = float(result.get('score', 0.0))
            score = max(-1.0, min(1.0, score))  # Clamp to valid range
            
            label = result.get('label', 'neutral').lower()
            if label not in ['positive', 'negative', 'neutral', 'mixed']:
                label = 'neutral'
            
            return {
                'score': score,
                'label': label,
                'reasoning': result.get('reasoning', '')
            }
            
        except Exception as e:
            logger.warning(f"Sentiment analysis failed, using fallback: {str(e)}")
            return self._fallback_sentiment_analysis(content)
    
    def _detect_urgency(self, content: str) -> float:
        """
        Detect urgency level in communication content
        
        Returns:
            float: Urgency score from 0.0 to 1.0
        """
        content_lower = content.lower()
        urgency_score = 0.0
        
        # Check for urgency keywords
        for keyword in self.URGENCY_KEYWORDS:
            if keyword in content_lower:
                urgency_score += 0.2
        
        # Check for urgency patterns
        urgency_patterns = [
            r'need.{0,10}(asap|immediately|urgent)',
            r'(please|can you).{0,20}(help|assist).{0,10}(urgent|asap)',
            r'deadline.{0,20}(today|tomorrow|this week)',
            r'(emergency|crisis|problem|issue)',
            r'time.{0,10}sensitive',
            r'worried.{0,20}about',
            r'concerned.{0,20}(about|with)',
        ]
        
        for pattern in urgency_patterns:
            if re.search(pattern, content_lower, re.IGNORECASE):
                urgency_score += 0.15
        
        # Check for excessive punctuation (!!!, ???)
        if re.search(r'[!?]{2,}', content):
            urgency_score += 0.1
        
        # Check for all caps words
        caps_words = re.findall(r'\b[A-Z]{2,}\b', content)
        if len(caps_words) > 2:
            urgency_score += 0.1
        
        return min(1.0, urgency_score)
    
    def _extract_topics(self, content: str) -> List[str]:
        """Extract relevant financial topics from content"""
        content_lower = content.lower()
        topics = []
        
        for topic in self.FINANCIAL_TOPICS:
            if topic in content_lower:
                topics.append(topic)
        
        # Use AI for more sophisticated topic extraction if needed
        if len(topics) < 2:
            topics.extend(self._ai_extract_topics(content))
        
        return list(set(topics))  # Remove duplicates
    
    def _ai_extract_topics(self, content: str) -> List[str]:
        """Use AI to extract topics when keyword matching is insufficient"""
        try:
            prompt = f"""
            Extract the main financial/investment topics discussed in this message:
            
            "{content}"
            
            Return only a JSON array of topics (e.g., ["retirement planning", "market volatility", "tax strategy"]).
            Focus on financial advisory relevant topics. Maximum 5 topics.
            """
            
            response = self.client.chat.completions.create(
                model=self.model_version,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.2
            )
            
            topics = json.loads(response.choices[0].message.content)
            return topics if isinstance(topics, list) else []
            
        except Exception as e:
            logger.warning(f"AI topic extraction failed: {str(e)}")
            return []
    
    def _calculate_priority_score(self, sentiment_result: Dict, urgency_score: float, 
                                communication: Communication) -> float:
        """
        Calculate overall priority score combining multiple factors
        
        Returns:
            float: Priority score from 0.0 to 1.0
        """
        # Base priority from sentiment (negative sentiment = higher priority)
        sentiment_priority = max(0.0, -sentiment_result['score'] * 0.5 + 0.5)
        
        # Urgency contributes directly
        urgency_priority = urgency_score
        
        # Client value factor
        client_value_factor = 1.0
        if communication.client:
            client_value_factor = self._get_client_value_factor(communication.client)
        elif communication.lead and communication.lead.lead_source:
            # High-value lead sources get priority
            client_value_factor = 0.8
        
        # Communication type factor (emails generally lower priority than calls)
        type_factor = {
            'call': 1.0,
            'meeting': 0.9,
            'email': 0.7,
            'sms': 0.8,
            'note': 0.5
        }.get(communication.communication_type, 0.7)
        
        # Combine factors
        priority = (
            sentiment_priority * 0.3 +
            urgency_priority * 0.4 +
            client_value_factor * 0.2 +
            type_factor * 0.1
        )
        
        return min(1.0, priority)
    
    def _should_generate_response(self, sentiment_result: Dict, urgency_score: float) -> bool:
        """Determine if AI should generate a suggested response"""
        # Generate responses for negative sentiment or high urgency
        return (
            sentiment_result['score'] < -0.3 or  # Negative sentiment
            urgency_score > 0.5 or              # High urgency
            sentiment_result['label'] == 'mixed' # Mixed sentiment needs careful handling
        )
    
    def _generate_response(self, communication: Communication, context: Dict, 
                         sentiment_result: Dict) -> Dict:
        """Generate suggested response using AI"""
        try:
            contact_name = context.get('contact_name', 'valued client')
            advisor_name = f"{communication.advisor.first_name} {communication.advisor.last_name}"
            
            prompt = f"""
            As a financial advisor, draft a professional and empathetic response to this {communication.communication_type}:
            
            From: {contact_name} ({context.get('contact_type', 'client')})
            Subject: {communication.subject}
            Content: "{communication.content}"
            
            Context:
            - Sentiment: {sentiment_result['label']} ({sentiment_result['score']:.2f})
            - This is a {context.get('contact_type', 'client')} communication
            
            Draft a response that:
            1. Acknowledges their concerns empathetically
            2. Provides reassurance where appropriate
            3. Offers next steps or solutions
            4. Maintains professional financial advisory tone
            5. Signs with "{advisor_name}"
            
            Keep response concise but thorough (2-3 paragraphs max).
            Return JSON with "response" and "confidence" (0.0-1.0).
            """
            
            response = self.client.chat.completions.create(
                model=self.model_version,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.MAX_TOKENS,
                temperature=self.TEMPERATURE
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                'response': result.get('response', ''),
                'confidence': min(1.0, max(0.0, float(result.get('confidence', 0.7))))
            }
            
        except Exception as e:
            logger.warning(f"Response generation failed: {str(e)}")
            return {'response': '', 'confidence': 0.0}
    
    def _fallback_sentiment_analysis(self, content: str) -> Dict:
        """Fallback sentiment analysis using keyword matching"""
        positive_words = ['thank', 'great', 'excellent', 'happy', 'satisfied', 'appreciate']
        negative_words = ['concerned', 'worried', 'problem', 'issue', 'disappointed', 'upset']
        
        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        if positive_count > negative_count:
            return {'score': 0.3, 'label': 'positive', 'reasoning': 'Keyword-based analysis'}
        elif negative_count > positive_count:
            return {'score': -0.3, 'label': 'negative', 'reasoning': 'Keyword-based analysis'}
        else:
            return {'score': 0.0, 'label': 'neutral', 'reasoning': 'Keyword-based analysis'}
    
    def _calculate_relationship_duration(self, created_at: datetime) -> int:
        """Calculate relationship duration in months"""
        if not created_at:
            return 0
        duration = timezone.now() - created_at
        return max(0, int(duration.days / 30))
    
    def _estimate_client_value(self, client) -> float:
        """Estimate client value for priority calculation"""
        # This is a simplified estimation - in reality you'd use portfolio size, fees, etc.
        # For now, use relationship duration as a proxy
        duration_months = self._calculate_relationship_duration(client.created_at)
        if duration_months > 24:  # 2+ years
            return 1.0
        elif duration_months > 12:  # 1-2 years  
            return 0.8
        elif duration_months > 6:   # 6 months - 1 year
            return 0.6
        else:  # New client
            return 0.4
    
    def _get_client_value_factor(self, client) -> float:
        """Get client value factor for priority scoring"""
        base_value = self._estimate_client_value(client)
        # Could be enhanced with actual AUM, fee data, etc.
        return base_value


# Utility functions for batch processing
def analyze_communications_batch(communication_ids: List[int]) -> Dict[str, any]:
    """
    Analyze multiple communications in batch
    
    Args:
        communication_ids: List of communication IDs to analyze
        
    Returns:
        Dict with success/failure counts and error details
    """
    service = AIEmailService()
    results = {
        'total': len(communication_ids),
        'success': 0,
        'failed': 0,
        'errors': []
    }
    
    for comm_id in communication_ids:
        try:
            communication = Communication.objects.get(id=comm_id)
            success = service.update_communication_analysis(communication)
            if success:
                results['success'] += 1
            else:
                results['failed'] += 1
                results['errors'].append(f"Communication {comm_id}: Analysis failed")
        except Communication.DoesNotExist:
            results['failed'] += 1
            results['errors'].append(f"Communication {comm_id}: Not found")
        except Exception as e:
            results['failed'] += 1
            results['errors'].append(f"Communication {comm_id}: {str(e)}")
    
    return results


def get_high_priority_communications(advisor_id: int, limit: int = 20) -> List[Communication]:
    """
    Get high priority communications that need attention
    
    Args:
        advisor_id: Advisor user ID
        limit: Maximum number of communications to return
        
    Returns:
        List of high priority Communications
    """
    return Communication.objects.filter(
        advisor_id=advisor_id,
        ai_priority_score__isnull=False
    ).order_by('-ai_priority_score', '-created_at')[:limit]