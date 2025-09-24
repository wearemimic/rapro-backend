"""
AI Report Service for Report Center
Integrates OpenAI GPT-4 for intelligent content generation, analysis, and recommendations
"""

import json
import logging
from typing import Dict, List, Optional, Any
from decimal import Decimal
from datetime import datetime

from django.conf import settings
from django.core.cache import cache
from openai import OpenAI

logger = logging.getLogger(__name__)


class AIReportService:
    """Service for AI-powered report generation and content enhancement"""
    
    def __init__(self):
        """Initialize OpenAI client with API key from settings"""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Model configuration
        self.model_config = {
            'content_generation': 'gpt-4-turbo-preview',
            'analysis': 'gpt-4o-mini',
            'recommendations': 'gpt-4-turbo-preview'
        }
        
        # Cost tracking (prices per 1K tokens as of 2024)
        self.token_costs = {
            'gpt-4-turbo-preview': {'input': 0.01, 'output': 0.03},
            'gpt-4o-mini': {'input': 0.00015, 'output': 0.0006},
            'gpt-4': {'input': 0.03, 'output': 0.06}
        }
    
    def generate_executive_summary(
        self, 
        scenario_data: Dict[str, Any], 
        client_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate an AI-powered executive summary from scenario and client data
        
        Args:
            scenario_data: Scenario calculations and results
            client_data: Client profile information
            
        Returns:
            Dict containing summary text, confidence score, and cost tracking
        """
        try:
            # Build context for AI
            context = self._build_client_context(client_data, scenario_data)
            prompt = self._build_executive_summary_prompt(context)
            
            # Generate summary using GPT-4
            response = self.client.chat.completions.create(
                model=self.model_config['content_generation'],
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert financial advisor specializing in retirement planning. Generate professional, clear, and actionable executive summaries."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            # Extract response and calculate costs
            summary_text = response.choices[0].message.content
            usage = response.usage
            cost = self._calculate_api_cost(usage, self.model_config['content_generation'])
            
            # Cache the result for future use
            cache_key = f"exec_summary_{client_data.get('id')}_{scenario_data.get('id')}"
            cache.set(cache_key, summary_text, timeout=3600)  # Cache for 1 hour
            
            return {
                'summary': summary_text,
                'confidence': self._calculate_confidence(response),
                'cost': cost,
                'tokens_used': usage.total_tokens,
                'cached': False
            }
            
        except Exception as e:
            logger.error(f"Error generating executive summary: {str(e)}")
            return {
                'summary': self._get_fallback_summary(client_data, scenario_data),
                'confidence': 0.5,
                'cost': 0,
                'error': str(e)
            }
    
    def recommend_slide_order(
        self,
        client_profile: Dict[str, Any],
        scenario_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        AI-powered slide ordering recommendations based on client profile and scenario
        
        Args:
            client_profile: Client demographics and preferences
            scenario_results: Scenario calculation results
            
        Returns:
            List of recommended slides with priority and reasoning
        """
        try:
            risk_tolerance = self._assess_risk_tolerance(client_profile)
            complexity_level = self._assess_scenario_complexity(scenario_results)
            
            # Build prompt for slide recommendations
            prompt = f"""
            Based on the following client profile and scenario analysis, recommend the optimal order
            and selection of slides for a retirement planning presentation.
            
            Client Profile:
            - Age: {client_profile.get('age', 'Unknown')}
            - Risk Tolerance: {risk_tolerance}
            - Retirement Timeline: {client_profile.get('years_to_retirement', 'Unknown')} years
            - Total Assets: ${client_profile.get('total_assets', 0):,.0f}
            
            Scenario Complexity: {complexity_level}
            Key Findings:
            - Success Probability: {scenario_results.get('success_rate', 0)}%
            - IRMAA Impact: {'Yes' if scenario_results.get('irmaa_impact', False) else 'No'}
            - Tax Optimization Needed: {'Yes' if scenario_results.get('needs_tax_optimization', False) else 'No'}
            
            Available Slide Types:
            1. Cover Page
            2. Executive Summary
            3. Current Financial Snapshot
            4. Retirement Income Timeline
            5. Asset Allocation Analysis
            6. Monte Carlo Analysis
            7. Tax Strategy Overview
            8. IRMAA Analysis
            9. Roth Conversion Strategy
            10. Social Security Optimization
            11. Risk Analysis
            12. Recommendations
            13. Next Steps
            
            Provide a prioritized list of 7-10 slides with brief reasoning for each selection.
            Format as JSON array with fields: slide_type, priority, reason
            """
            
            response = self.client.chat.completions.create(
                model=self.model_config['recommendations'],
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert presentation designer for financial advisors. Provide strategic slide recommendations."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=600,
                response_format={"type": "json_object"}
            )
            
            # Parse JSON response
            recommendations = json.loads(response.choices[0].message.content)
            
            # Add cost tracking
            usage = response.usage
            cost = self._calculate_api_cost(usage, self.model_config['recommendations'])
            
            # Track usage for analytics
            self._track_ai_usage('slide_recommendations', cost, usage.total_tokens)
            
            return recommendations.get('slides', self._get_default_slide_order(risk_tolerance))
            
        except Exception as e:
            logger.error(f"Error generating slide recommendations: {str(e)}")
            return self._get_default_slide_order('moderate')
    
    def generate_content_for_section(
        self,
        section_type: str,
        data: Dict[str, Any],
        tone: str = 'professional'
    ) -> str:
        """
        Generate AI content for specific report sections
        
        Args:
            section_type: Type of section (risk_explanation, irmaa_impact, etc.)
            data: Relevant data for content generation
            tone: Writing tone (professional, friendly, technical)
            
        Returns:
            Generated content text
        """
        try:
            prompts = {
                'risk_explanation': self._build_risk_explanation_prompt(data),
                'irmaa_impact': self._build_irmaa_explanation_prompt(data),
                'roth_strategy': self._build_roth_strategy_prompt(data),
                'tax_optimization': self._build_tax_optimization_prompt(data),
                'social_security': self._build_social_security_prompt(data),
                'monte_carlo_interpretation': self._build_monte_carlo_prompt(data)
            }
            
            if section_type not in prompts:
                return ""
            
            # Add tone instruction
            system_prompt = self._get_system_prompt_for_tone(tone)
            
            response = self.client.chat.completions.create(
                model=self.model_config['content_generation'],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompts[section_type]}
                ],
                temperature=0.4,
                max_tokens=400
            )
            
            content = response.choices[0].message.content
            
            # Track usage
            usage = response.usage
            cost = self._calculate_api_cost(usage, self.model_config['content_generation'])
            self._track_ai_usage(f'content_{section_type}', cost, usage.total_tokens)
            
            return content
            
        except Exception as e:
            logger.error(f"Error generating content for {section_type}: {str(e)}")
            return self._get_fallback_content(section_type, data)
    
    def analyze_client_insights(
        self,
        client_data: Dict[str, Any],
        scenario_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate AI-powered insights about the client's retirement readiness
        
        Args:
            client_data: Client profile information
            scenario_data: Scenario results and projections
            
        Returns:
            Dict containing insights, opportunities, and risks
        """
        try:
            prompt = f"""
            Analyze the following retirement planning scenario and provide professional insights:
            
            Client Information:
            - Current Age: {client_data.get('age', 'Unknown')}
            - Retirement Age: {client_data.get('retirement_age', 65)}
            - Current Assets: ${client_data.get('total_assets', 0):,.0f}
            - Annual Income Need: ${scenario_data.get('annual_income_needed', 0):,.0f}
            
            Scenario Results:
            - Success Probability: {scenario_data.get('success_rate', 0)}%
            - Years of Coverage: {scenario_data.get('years_covered', 0)}
            - Shortfall Risk: {scenario_data.get('shortfall_risk', 'Unknown')}
            
            Provide:
            1. Three key insights about their retirement readiness
            2. Three opportunities for improvement
            3. Three potential risks to address
            
            Format as JSON with fields: insights[], opportunities[], risks[]
            """
            
            response = self.client.chat.completions.create(
                model=self.model_config['analysis'],
                messages=[
                    {
                        "role": "system",
                        "content": "You are a retirement planning expert. Provide actionable insights."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            insights = json.loads(response.choices[0].message.content)
            
            # Add cost tracking
            usage = response.usage
            cost = self._calculate_api_cost(usage, self.model_config['analysis'])
            self._track_ai_usage('client_insights', cost, usage.total_tokens)
            
            return {
                **insights,
                'generated_at': datetime.now().isoformat(),
                'cost': cost
            }
            
        except Exception as e:
            logger.error(f"Error analyzing client insights: {str(e)}")
            return self._get_fallback_insights()
    
    # =========================================================================
    # PRIVATE HELPER METHODS
    # =========================================================================
    
    def _build_client_context(
        self,
        client_data: Dict[str, Any],
        scenario_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build comprehensive context for AI prompts"""
        return {
            'client': {
                'name': f"{client_data.get('first_name', '')} {client_data.get('last_name', '')}",
                'age': client_data.get('age', 'Unknown'),
                'retirement_age': scenario_data.get('retirement_age', 65),
                'years_to_retirement': scenario_data.get('retirement_age', 65) - client_data.get('age', 60),
                'tax_status': client_data.get('tax_status', 'Unknown')
            },
            'financial': {
                'total_assets': scenario_data.get('total_assets', 0),
                'annual_income_needed': scenario_data.get('annual_income_needed', 0),
                'social_security': scenario_data.get('social_security_benefit', 0),
                'pension_income': scenario_data.get('pension_income', 0),
                'success_rate': scenario_data.get('success_rate', 0)
            },
            'analysis': {
                'irmaa_impact': scenario_data.get('irmaa_bracket_number', 0) > 0,
                'tax_rate': scenario_data.get('effective_tax_rate', 0),
                'monte_carlo_percentiles': scenario_data.get('monte_carlo_percentiles', {}),
                'shortfall_risk': scenario_data.get('shortfall_risk', 'Low')
            }
        }
    
    def _build_executive_summary_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for executive summary generation"""
        return f"""
        Create a professional executive summary for a retirement planning report with the following information:
        
        Client: {context['client']['name']}
        Current Age: {context['client']['age']}
        Retirement Age: {context['client']['retirement_age']}
        Years to Retirement: {context['client']['years_to_retirement']}
        
        Financial Snapshot:
        - Total Portfolio Value: ${context['financial']['total_assets']:,.0f}
        - Annual Retirement Income Needed: ${context['financial']['annual_income_needed']:,.0f}
        - Expected Social Security: ${context['financial']['social_security']:,.0f}/year
        - Monte Carlo Success Rate: {context['financial']['success_rate']}%
        
        Key Considerations:
        - IRMAA Impact: {'Yes - requires planning' if context['analysis']['irmaa_impact'] else 'No'}
        - Effective Tax Rate: {context['analysis']['tax_rate']:.1f}%
        - Risk Level: {context['analysis']['shortfall_risk']}
        
        Write a 2-3 paragraph executive summary that:
        1. Summarizes the retirement outlook
        2. Highlights key opportunities and challenges
        3. Provides clear next steps
        
        Use professional but accessible language suitable for client presentations.
        """
    
    def _build_risk_explanation_prompt(self, data: Dict[str, Any]) -> str:
        """Build prompt for risk explanation"""
        return f"""
        Explain the retirement portfolio risk analysis for a client with:
        - Monte Carlo Success Rate: {data.get('success_rate', 0)}%
        - 10th Percentile Outcome: ${data.get('p10_value', 0):,.0f}
        - 50th Percentile Outcome: ${data.get('p50_value', 0):,.0f}
        - 90th Percentile Outcome: ${data.get('p90_value', 0):,.0f}
        
        Explain what these percentiles mean and what actions could improve the outcomes.
        Keep it under 150 words and use clear, non-technical language.
        """
    
    def _build_irmaa_explanation_prompt(self, data: Dict[str, Any]) -> str:
        """Build prompt for IRMAA impact explanation"""
        return f"""
        Explain the Medicare IRMAA (Income-Related Monthly Adjustment Amount) impact for a client:
        - Current IRMAA Bracket: {data.get('irmaa_bracket_number', 0)}
        - Annual MAGI: ${data.get('magi', 0):,.0f}
        - Additional Medicare Premium: ${data.get('irmaa_premium', 0):,.0f}/year
        - Years Affected: {data.get('years_affected', 0)}
        
        Provide strategies to potentially reduce IRMAA impact.
        Keep it under 150 words and focus on actionable advice.
        """
    
    def _build_roth_strategy_prompt(self, data: Dict[str, Any]) -> str:
        """Build prompt for Roth conversion strategy"""
        return f"""
        Explain a Roth conversion strategy for a client with:
        - Traditional IRA Balance: ${data.get('traditional_ira_balance', 0):,.0f}
        - Current Tax Bracket: {data.get('current_tax_bracket', 0)}%
        - Years Until RMDs: {data.get('years_to_rmd', 0)}
        - Recommended Annual Conversion: ${data.get('recommended_conversion', 0):,.0f}
        
        Explain the benefits and tax implications.
        Keep it under 150 words and highlight key decision factors.
        """
    
    def _build_tax_optimization_prompt(self, data: Dict[str, Any]) -> str:
        """Build prompt for tax optimization strategies"""
        return f"""
        Provide tax optimization strategies for a retiree with:
        - Annual Retirement Income: ${data.get('annual_income', 0):,.0f}
        - Federal Tax Rate: {data.get('federal_rate', 0)}%
        - State Tax Rate: {data.get('state_rate', 0)}%
        - Tax-Deferred Accounts: ${data.get('tax_deferred', 0):,.0f}
        - Taxable Accounts: ${data.get('taxable', 0):,.0f}
        
        Suggest withdrawal sequencing and tax-saving strategies.
        Keep it under 150 words with specific, actionable recommendations.
        """
    
    def _build_social_security_prompt(self, data: Dict[str, Any]) -> str:
        """Build prompt for Social Security optimization"""
        return f"""
        Analyze Social Security claiming strategy for:
        - Current Age: {data.get('current_age', 60)}
        - Full Retirement Age: {data.get('fra', 67)}
        - Estimated Benefit at FRA: ${data.get('fra_benefit', 0):,.0f}/month
        - Benefit if Claimed Now: ${data.get('current_benefit', 0):,.0f}/month
        - Benefit at Age 70: ${data.get('age_70_benefit', 0):,.0f}/month
        
        Recommend optimal claiming age and explain the trade-offs.
        Keep it under 150 words.
        """
    
    def _build_monte_carlo_prompt(self, data: Dict[str, Any]) -> str:
        """Build prompt for Monte Carlo interpretation"""
        return f"""
        Interpret Monte Carlo simulation results:
        - Success Rate: {data.get('success_rate', 0)}%
        - Number of Simulations: {data.get('simulations', 10000)}
        - Median Portfolio Value at End: ${data.get('median_final_value', 0):,.0f}
        - Probability of Running Out: {100 - data.get('success_rate', 0)}%
        
        Explain what this means for retirement security and suggest improvements.
        Keep it under 150 words using clear, reassuring language.
        """
    
    def _assess_risk_tolerance(self, client_profile: Dict[str, Any]) -> str:
        """Assess client risk tolerance based on profile"""
        age = client_profile.get('age', 60)
        years_to_retirement = client_profile.get('years_to_retirement', 5)
        
        if age > 70 or years_to_retirement < 3:
            return 'conservative'
        elif age > 60 or years_to_retirement < 10:
            return 'moderate'
        else:
            return 'aggressive'
    
    def _assess_scenario_complexity(self, scenario_results: Dict[str, Any]) -> str:
        """Assess complexity level of scenario"""
        factors = 0
        
        if scenario_results.get('irmaa_impact', False):
            factors += 1
        if scenario_results.get('needs_tax_optimization', False):
            factors += 1
        if scenario_results.get('has_pension', False):
            factors += 1
        if scenario_results.get('has_rental_income', False):
            factors += 1
        if scenario_results.get('success_rate', 100) < 80:
            factors += 1
        
        if factors >= 3:
            return 'high'
        elif factors >= 1:
            return 'moderate'
        else:
            return 'simple'
    
    def _calculate_confidence(self, response) -> float:
        """Calculate confidence score based on response quality"""
        # Simple confidence calculation based on response completeness
        if response.choices and response.choices[0].finish_reason == 'stop':
            return 0.95
        elif response.choices and response.choices[0].finish_reason == 'length':
            return 0.75
        else:
            return 0.5
    
    def _calculate_api_cost(self, usage, model: str) -> float:
        """Calculate API cost based on token usage"""
        costs = self.token_costs.get(model, {'input': 0.01, 'output': 0.03})
        input_cost = (usage.prompt_tokens / 1000) * costs['input']
        output_cost = (usage.completion_tokens / 1000) * costs['output']
        return round(input_cost + output_cost, 4)
    
    def _track_ai_usage(self, feature: str, cost: float, tokens: int):
        """Track AI usage for analytics and cost management"""
        try:
            from ..models import AIUsageTracking
            
            AIUsageTracking.objects.create(
                feature=feature,
                tokens_used=tokens,
                cost=cost,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error tracking AI usage: {str(e)}")
    
    def _get_system_prompt_for_tone(self, tone: str) -> str:
        """Get system prompt based on desired tone"""
        prompts = {
            'professional': "You are a professional financial advisor. Use formal but clear language suitable for client presentations.",
            'friendly': "You are a friendly and approachable financial advisor. Use warm, conversational language while maintaining professionalism.",
            'technical': "You are a financial analyst. Use precise technical language with detailed explanations.",
            'simple': "You are explaining complex financial concepts to someone with limited financial knowledge. Use very simple, clear language."
        }
        return prompts.get(tone, prompts['professional'])
    
    def _get_default_slide_order(self, risk_tolerance: str) -> List[Dict[str, Any]]:
        """Get default slide order based on risk tolerance"""
        if risk_tolerance == 'conservative':
            return [
                {'slide_type': 'cover', 'priority': 1, 'reason': 'Standard opening'},
                {'slide_type': 'executive_summary', 'priority': 2, 'reason': 'Overview first'},
                {'slide_type': 'current_snapshot', 'priority': 3, 'reason': 'Current situation'},
                {'slide_type': 'income_timeline', 'priority': 4, 'reason': 'Income security focus'},
                {'slide_type': 'risk_analysis', 'priority': 5, 'reason': 'Address risk concerns'},
                {'slide_type': 'tax_strategy', 'priority': 6, 'reason': 'Tax efficiency'},
                {'slide_type': 'recommendations', 'priority': 7, 'reason': 'Action items'},
                {'slide_type': 'next_steps', 'priority': 8, 'reason': 'Clear path forward'}
            ]
        elif risk_tolerance == 'aggressive':
            return [
                {'slide_type': 'cover', 'priority': 1, 'reason': 'Standard opening'},
                {'slide_type': 'executive_summary', 'priority': 2, 'reason': 'Quick overview'},
                {'slide_type': 'growth_projections', 'priority': 3, 'reason': 'Growth focus'},
                {'slide_type': 'monte_carlo', 'priority': 4, 'reason': 'Probability analysis'},
                {'slide_type': 'tax_optimization', 'priority': 5, 'reason': 'Maximize efficiency'},
                {'slide_type': 'roth_conversion', 'priority': 6, 'reason': 'Tax-free growth'},
                {'slide_type': 'recommendations', 'priority': 7, 'reason': 'Growth strategies'},
                {'slide_type': 'next_steps', 'priority': 8, 'reason': 'Implementation plan'}
            ]
        else:  # moderate
            return [
                {'slide_type': 'cover', 'priority': 1, 'reason': 'Standard opening'},
                {'slide_type': 'executive_summary', 'priority': 2, 'reason': 'Comprehensive overview'},
                {'slide_type': 'current_snapshot', 'priority': 3, 'reason': 'Starting point'},
                {'slide_type': 'income_timeline', 'priority': 4, 'reason': 'Retirement income'},
                {'slide_type': 'asset_allocation', 'priority': 5, 'reason': 'Diversification'},
                {'slide_type': 'monte_carlo', 'priority': 6, 'reason': 'Success probability'},
                {'slide_type': 'tax_strategy', 'priority': 7, 'reason': 'Tax planning'},
                {'slide_type': 'recommendations', 'priority': 8, 'reason': 'Balanced approach'},
                {'slide_type': 'next_steps', 'priority': 9, 'reason': 'Action plan'}
            ]
    
    def _get_fallback_summary(
        self,
        client_data: Dict[str, Any],
        scenario_data: Dict[str, Any]
    ) -> str:
        """Provide fallback summary if AI generation fails"""
        return f"""
        This retirement analysis for {client_data.get('first_name', 'the client')} shows a 
        {scenario_data.get('success_rate', 0)}% probability of meeting retirement income goals. 
        With current assets of ${scenario_data.get('total_assets', 0):,.0f} and an annual income 
        need of ${scenario_data.get('annual_income_needed', 0):,.0f}, careful planning and 
        monitoring will be essential for retirement success.
        """
    
    def _get_fallback_content(self, section_type: str, data: Dict[str, Any]) -> str:
        """Provide fallback content for specific sections"""
        fallbacks = {
            'risk_explanation': "Your portfolio risk analysis shows the range of possible outcomes based on market performance.",
            'irmaa_impact': "Medicare premiums may be affected by your income level. Consider strategies to manage your modified adjusted gross income.",
            'roth_strategy': "Roth conversions can provide tax-free income in retirement. Consult with your tax advisor for personalized advice.",
            'tax_optimization': "Tax-efficient withdrawal strategies can significantly impact your retirement income.",
            'social_security': "The timing of your Social Security claim can affect your lifetime benefits.",
            'monte_carlo_interpretation': "Monte Carlo analysis tests your plan against thousands of market scenarios."
        }
        return fallbacks.get(section_type, "Please consult with your financial advisor for detailed analysis.")
    
    def _get_fallback_insights(self) -> Dict[str, Any]:
        """Provide fallback insights if AI analysis fails"""
        return {
            'insights': [
                "Review your current retirement savings rate",
                "Consider diversifying your investment portfolio",
                "Plan for healthcare costs in retirement"
            ],
            'opportunities': [
                "Maximize employer retirement plan contributions",
                "Explore tax-advantaged savings strategies",
                "Review Social Security claiming strategies"
            ],
            'risks': [
                "Inflation impact on purchasing power",
                "Healthcare cost increases",
                "Market volatility near retirement"
            ],
            'generated_at': datetime.now().isoformat(),
            'fallback': True
        }


# Singleton instance
_ai_service_instance = None


def get_ai_report_service() -> AIReportService:
    """Get singleton instance of AIReportService"""
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIReportService()
    return _ai_service_instance