import anthropic
from django.conf import settings
import json
import tiktoken
from typing import Dict, List, Optional, Tuple


class LTCAIAssistant:

    SYSTEM_PROMPT = """You are a compassionate and knowledgeable long-term care planning assistant.
Your goal is to help financial advisors assess their clients' long-term care needs through a conversational assessment.

Your responsibilities:
1. Conduct a thorough ADL (Activities of Daily Living) assessment using the Katz Index:
   - Bathing
   - Dressing
   - Toileting
   - Transferring (mobility)
   - Continence
   - Eating

2. Conduct an IADL (Instrumental Activities of Daily Living) assessment using the Lawton-Brody Scale:
   - Using telephone
   - Shopping
   - Food preparation
   - Housekeeping
   - Laundry
   - Transportation
   - Medications
   - Finances

3. Gather information about:
   - Current health conditions
   - Cognitive status
   - Living situation
   - Family support system
   - Geographic location
   - Financial considerations

Guidelines:
- Be empathetic and respectful
- Ask one question at a time
- Use conversational, easy-to-understand language
- Avoid medical jargon unless necessary
- Listen actively to responses and ask follow-up questions
- Summarize information periodically to confirm understanding
- At the end, provide a care level recommendation based on the assessment

Care Level Recommendations:
- Independent with Monitoring: No significant ADL/IADL impairments
- In-Home Care: 1-2 ADL impairments or 3+ IADL impairments
- Adult Day Care: 2-3 ADL impairments with family support
- Assisted Living: 3-4 ADL impairments, some cognitive decline
- Memory Care: Moderate to severe cognitive impairment
- Skilled Nursing: 5-6 ADL impairments or complex medical needs"""

    INTENT_CLASSIFICATION_PROMPT = """Analyze the user's message and classify the intent into ONE of the following categories:

1. adl_assessment - User is providing information about basic activities of daily living (bathing, dressing, toileting, transferring, continence, eating)
2. iadl_assessment - User is providing information about instrumental activities (phone use, shopping, cooking, housekeeping, laundry, transportation, medications, finances)
3. health_conditions - User is discussing medical conditions, diagnoses, or health issues
4. cognitive_status - User is discussing memory, confusion, decision-making ability
5. living_situation - User is discussing where client lives, home modifications, accessibility
6. family_support - User is discussing family members, caregivers, support system
7. geographic_location - User is providing location information (state, city, region)
8. financial_considerations - User is discussing budget, assets, insurance coverage
9. clarification - User is asking for clarification or more information
10. greeting - User is greeting or starting the conversation
11. end_conversation - User wants to end or has finished the assessment

Return ONLY a JSON object with the intent and confidence score:
{"intent": "intent_category", "confidence": 0.95}"""

    ENTITY_EXTRACTION_PROMPT = """Extract relevant entities from the user's message for long-term care assessment.

Return a JSON object with the following structure (omit keys if not present):
{
  "adl_scores": {
    "bathing": "independent|needs_assistance|dependent",
    "dressing": "independent|needs_assistance|dependent",
    "toileting": "independent|needs_assistance|dependent",
    "transferring": "independent|needs_assistance|dependent",
    "continence": "independent|needs_assistance|dependent",
    "eating": "independent|needs_assistance|dependent"
  },
  "iadl_scores": {
    "telephone": "independent|needs_assistance|unable",
    "shopping": "independent|needs_assistance|unable",
    "food_preparation": "independent|needs_assistance|unable",
    "housekeeping": "independent|needs_assistance|unable",
    "laundry": "independent|needs_assistance|unable",
    "transportation": "independent|needs_assistance|unable",
    "medications": "independent|needs_assistance|unable",
    "finances": "independent|needs_assistance|unable"
  },
  "health_conditions": ["condition1", "condition2"],
  "cognitive_status": "normal|mild_impairment|moderate_impairment|severe_impairment",
  "living_situation": "independent_home|family_home|apartment|retirement_community|other",
  "state": "state_name",
  "age": 75,
  "notes": "additional contextual information"
}"""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.CLAUDE_MODEL_VERSION
        self.max_tokens = settings.CLAUDE_MAX_TOKENS
        self.temperature = settings.CLAUDE_TEMPERATURE

        try:
            self.tokenizer = tiktoken.encoding_for_model("gpt-4")
        except KeyError:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        return len(self.tokenizer.encode(text))

    def classify_intent(self, message: str, conversation_history: List[Dict] = None) -> Tuple[str, float]:
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.3,
                system=self.INTENT_CLASSIFICATION_PROMPT,
                messages=[
                    {"role": "user", "content": message}
                ]
            )

            result = json.loads(response.content[0].text)
            return result.get('intent', 'unknown'), result.get('confidence', 0.0)

        except Exception as e:
            print(f"Intent classification error: {str(e)}")
            return 'unknown', 0.0

    def extract_entities(self, message: str, current_context: Dict = None) -> Dict:
        try:
            context_str = json.dumps(current_context) if current_context else "{}"

            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.2,
                system=self.ENTITY_EXTRACTION_PROMPT,
                messages=[
                    {"role": "user", "content": f"Current context: {context_str}\n\nNew message: {message}"}
                ]
            )

            extracted = json.loads(response.content[0].text)

            if current_context:
                if 'adl_scores' in extracted:
                    current_context.setdefault('adl_scores', {}).update(extracted['adl_scores'])
                if 'iadl_scores' in extracted:
                    current_context.setdefault('iadl_scores', {}).update(extracted['iadl_scores'])
                if 'health_conditions' in extracted:
                    current_context.setdefault('health_conditions', []).extend(extracted['health_conditions'])
                    current_context['health_conditions'] = list(set(current_context['health_conditions']))

                for key in ['cognitive_status', 'living_situation', 'state', 'age']:
                    if key in extracted:
                        current_context[key] = extracted[key]

                return current_context

            return extracted

        except Exception as e:
            print(f"Entity extraction error: {str(e)}")
            return current_context or {}

    def generate_next_question(self, conversation_history: List[Dict], extracted_data: Dict) -> str:
        adl_items = ['bathing', 'dressing', 'toileting', 'transferring', 'continence', 'eating']
        iadl_items = ['telephone', 'shopping', 'food_preparation', 'housekeeping', 'laundry', 'transportation', 'medications', 'finances']

        adl_scores = extracted_data.get('adl_scores', {})
        iadl_scores = extracted_data.get('iadl_scores', {})

        missing_adl = [item for item in adl_items if item not in adl_scores]
        missing_iadl = [item for item in iadl_items if item not in iadl_scores]

        if missing_adl:
            return self._generate_adl_question(missing_adl[0])
        elif missing_iadl:
            return self._generate_iadl_question(missing_iadl[0])
        elif 'cognitive_status' not in extracted_data:
            return "Can you tell me about their memory and cognitive abilities? Do they experience any confusion or difficulty making decisions?"
        elif 'living_situation' not in extracted_data:
            return "Where does the client currently live? Are there any accessibility concerns or home modifications needed?"
        elif 'state' not in extracted_data:
            return "In which state does the client reside? This helps us project regional care costs."
        else:
            return self._generate_summary_and_recommendation(extracted_data)

    def _generate_adl_question(self, adl_item: str) -> str:
        questions = {
            'bathing': "Can the client bathe themselves independently, or do they need assistance getting in/out of the shower or tub?",
            'dressing': "Is the client able to dress themselves, including selecting appropriate clothing and managing buttons, zippers?",
            'toileting': "Can the client use the toilet independently, including getting on/off and maintaining hygiene?",
            'transferring': "How is the client's mobility? Can they move from bed to chair, stand up, and walk without assistance?",
            'continence': "Does the client have control over bladder and bowel functions?",
            'eating': "Can the client feed themselves, or do they need help with cutting food or bringing food to their mouth?"
        }
        return questions.get(adl_item, f"Can you tell me about their ability with {adl_item}?")

    def _generate_iadl_question(self, iadl_item: str) -> str:
        questions = {
            'telephone': "Can the client use a telephone independently to make calls and answer calls?",
            'shopping': "Is the client able to shop for groceries and personal items independently?",
            'food_preparation': "Can the client prepare their own meals, from planning to cooking?",
            'housekeeping': "Is the client able to do light housekeeping tasks like making beds and doing dishes?",
            'laundry': "Can the client do their own laundry independently?",
            'transportation': "Is the client able to arrange and use transportation (driving, public transit, or arranging rides)?",
            'medications': "Can the client manage their medications independently, including taking them at the right times?",
            'finances': "Is the client able to manage their finances, pay bills, and handle banking?"
        }
        return questions.get(iadl_item, f"Can you tell me about their ability with {iadl_item}?")

    def _generate_summary_and_recommendation(self, extracted_data: Dict) -> str:
        adl_score = self._calculate_adl_impairment(extracted_data.get('adl_scores', {}))
        iadl_score = self._calculate_iadl_impairment(extracted_data.get('iadl_scores', {}))
        cognitive_status = extracted_data.get('cognitive_status', 'unknown')

        recommendation = self._determine_care_level(adl_score, iadl_score, cognitive_status)

        summary = f"""Based on our conversation, here's a summary of the assessment:

**Functional Status:**
- ADL Impairments: {adl_score} out of 6
- IADL Impairments: {iadl_score} out of 8
- Cognitive Status: {cognitive_status.replace('_', ' ').title()}

**Care Level Recommendation: {recommendation}**

{self._get_care_level_description(recommendation)}

Would you like to proceed with cost projections for this care level?"""

        return summary

    def _calculate_adl_impairment(self, adl_scores: Dict) -> int:
        impairment_count = 0
        for activity, status in adl_scores.items():
            if status in ['needs_assistance', 'dependent', 'assistance']:
                impairment_count += 1
        return impairment_count

    def _calculate_iadl_impairment(self, iadl_scores: Dict) -> int:
        impairment_count = 0
        for activity, status in iadl_scores.items():
            if status in ['needs_assistance', 'unable', 'assistance']:
                impairment_count += 1
        return impairment_count

    def _determine_care_level(self, adl_score: int, iadl_score: int, cognitive_status: str) -> str:
        if cognitive_status in ['moderate_impairment', 'severe_impairment']:
            return 'memory_care'

        if adl_score >= 5:
            return 'skilled_nursing'
        elif adl_score >= 3:
            return 'assisted_living'
        elif adl_score >= 2:
            return 'adult_day_care'
        elif adl_score >= 1 or iadl_score >= 3:
            return 'in_home_care'
        else:
            return 'independent_with_monitoring'

    def _get_care_level_description(self, care_level: str) -> str:
        descriptions = {
            'independent_with_monitoring': "The client can live independently with periodic check-ins and minimal assistance.",
            'in_home_care': "The client would benefit from regular in-home care assistance with daily activities.",
            'adult_day_care': "Adult day care services can provide daytime supervision and activities while allowing the client to remain at home.",
            'assisted_living': "An assisted living facility would provide 24/7 support with daily activities in a residential setting.",
            'memory_care': "A specialized memory care facility is recommended for clients with cognitive impairment.",
            'skilled_nursing': "Skilled nursing care in a nursing home is recommended for complex medical needs and significant functional impairment."
        }
        return descriptions.get(care_level, "")

    def continue_conversation(self, user_message: str, conversation_history: List[Dict], extracted_data: Dict) -> Dict:
        intent, confidence = self.classify_intent(user_message, conversation_history)

        updated_data = self.extract_entities(user_message, extracted_data)

        conversation_history_for_claude = []
        for msg in conversation_history[-10:]:
            role = "assistant" if msg.get('role') == 'assistant' else "user"
            conversation_history_for_claude.append({
                "role": role,
                "content": msg.get('content', '')
            })

        conversation_history_for_claude.append({
            "role": "user",
            "content": user_message
        })

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.SYSTEM_PROMPT,
                messages=conversation_history_for_claude
            )

            assistant_message = response.content[0].text

            next_question = ""
            if intent not in ['end_conversation', 'clarification']:
                next_question = self.generate_next_question(conversation_history, updated_data)

            return {
                'success': True,
                'assistant_message': assistant_message,
                'next_question': next_question,
                'intent': intent,
                'confidence': confidence,
                'extracted_data': updated_data,
                'tokens_used': response.usage.input_tokens + response.usage.output_tokens
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'assistant_message': "I apologize, but I'm having trouble processing your request. Could you please try again?",
                'extracted_data': updated_data
            }

    def start_new_conversation(self, client_info: Dict = None) -> Dict:
        greeting = "Hello! I'm here to help you assess your client's long-term care needs. "

        if client_info and client_info.get('name'):
            greeting += f"I understand we're discussing care planning for {client_info['name']}. "

        greeting += "To start, can you tell me a bit about their current ability to manage daily activities? For example, are they able to bathe and dress themselves independently?"

        return {
            'success': True,
            'assistant_message': greeting,
            'next_question': '',
            'extracted_data': {},
            'conversation_id': None
        }