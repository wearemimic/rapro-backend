"""
Background tasks for AI processing
Can be integrated with Celery or run synchronously
"""

import logging
from typing import Optional
from django.utils import timezone

from ..models import Communication
from ..services.ai_email_service import AIEmailService

logger = logging.getLogger(__name__)


def analyze_communication_async(communication_id: int) -> bool:
    """
    Analyze a single communication asynchronously
    
    Args:
        communication_id: ID of communication to analyze
        
    Returns:
        bool: Success status
    """
    try:
        communication = Communication.objects.get(id=communication_id)
        service = AIEmailService()
        
        success = service.update_communication_analysis(communication)
        
        if success:
            logger.info(f"AI analysis completed for communication {communication_id}")
        else:
            logger.error(f"AI analysis failed for communication {communication_id}")
            
        return success
        
    except Communication.DoesNotExist:
        logger.error(f"Communication {communication_id} not found")
        return False
    except Exception as e:
        logger.error(f"AI analysis task failed for communication {communication_id}: {str(e)}")
        return False


def analyze_new_inbound_emails():
    """
    Analyze new inbound emails that haven't been processed yet
    This can be run periodically to catch new emails
    """
    try:
        # Find unprocessed inbound emails from the last 24 hours
        recent_cutoff = timezone.now() - timezone.timedelta(hours=24)
        
        unprocessed_emails = Communication.objects.filter(
            communication_type='email',
            direction='inbound',
            ai_analysis_date__isnull=True,
            created_at__gte=recent_cutoff
        ).order_by('-created_at')[:50]  # Limit to 50 to avoid overload
        
        if not unprocessed_emails:
            logger.info("No new inbound emails to analyze")
            return {'processed': 0, 'total': 0}
        
        processed = 0
        total = len(unprocessed_emails)
        
        logger.info(f"Found {total} new inbound emails to analyze")
        
        for email in unprocessed_emails:
            if analyze_communication_async(email.id):
                processed += 1
        
        logger.info(f"Processed {processed}/{total} new inbound emails")
        return {'processed': processed, 'total': total}
        
    except Exception as e:
        logger.error(f"Batch analysis of new emails failed: {str(e)}")
        return {'processed': 0, 'total': 0, 'error': str(e)}


def reanalyze_high_priority_communications(days_back: int = 7):
    """
    Re-analyze communications that might have changed in priority
    Useful for updating priority scores based on new client interactions
    
    Args:
        days_back: How many days back to look for communications to re-analyze
    """
    try:
        cutoff_date = timezone.now() - timezone.timedelta(days=days_back)
        
        # Find communications with negative sentiment or high urgency that might need updates
        high_attention_comms = Communication.objects.filter(
            created_at__gte=cutoff_date,
            ai_analysis_date__isnull=False
        ).filter(
            ai_sentiment_score__lt=-0.5  # Very negative sentiment
        ).order_by('-ai_priority_score')[:20]
        
        processed = 0
        for comm in high_attention_comms:
            if analyze_communication_async(comm.id):
                processed += 1
        
        logger.info(f"Re-analyzed {processed} high-priority communications")
        return {'processed': processed, 'total': len(high_attention_comms)}
        
    except Exception as e:
        logger.error(f"High priority re-analysis failed: {str(e)}")
        return {'processed': 0, 'total': 0, 'error': str(e)}


def get_ai_analysis_stats(advisor_id: Optional[int] = None) -> dict:
    """
    Get statistics about AI analysis coverage
    
    Args:
        advisor_id: Optional advisor ID to filter stats
        
    Returns:
        dict: Analysis statistics
    """
    try:
        queryset = Communication.objects.filter(communication_type='email')
        
        if advisor_id:
            queryset = queryset.filter(advisor_id=advisor_id)
        
        total_emails = queryset.count()
        analyzed_emails = queryset.filter(ai_analysis_date__isnull=False).count()
        
        # Get recent analysis activity
        recent_cutoff = timezone.now() - timezone.timedelta(days=7)
        recent_analyzed = queryset.filter(
            ai_analysis_date__gte=recent_cutoff
        ).count()
        
        # Get sentiment distribution
        sentiment_stats = {
            'positive': queryset.filter(ai_sentiment_label='positive').count(),
            'negative': queryset.filter(ai_sentiment_label='negative').count(),
            'neutral': queryset.filter(ai_sentiment_label='neutral').count(),
            'mixed': queryset.filter(ai_sentiment_label='mixed').count(),
        }
        
        # Get high priority communications
        high_priority = queryset.filter(ai_priority_score__gte=0.7).count()
        
        return {
            'total_emails': total_emails,
            'analyzed_emails': analyzed_emails,
            'analysis_coverage': round(analyzed_emails / total_emails * 100, 1) if total_emails > 0 else 0,
            'recent_analyzed': recent_analyzed,
            'sentiment_distribution': sentiment_stats,
            'high_priority_count': high_priority,
            'needs_analysis': total_emails - analyzed_emails
        }
        
    except Exception as e:
        logger.error(f"Failed to get AI analysis stats: {str(e)}")
        return {'error': str(e)}


# Celery task definitions (if using Celery)
# Uncomment and modify these if you want to use Celery for background processing

# try:
#     from celery import shared_task
#     
#     @shared_task(bind=True, max_retries=3)
#     def celery_analyze_communication(self, communication_id: int):
#         """Celery task for analyzing a communication"""
#         try:
#             return analyze_communication_async(communication_id)
#         except Exception as exc:
#             logger.error(f"Celery task failed for communication {communication_id}: {str(exc)}")
#             # Retry with exponential backoff
#             raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
#     
#     @shared_task
#     def celery_analyze_new_emails():
#         """Celery task for analyzing new emails"""
#         return analyze_new_inbound_emails()
#         
# except ImportError:
#     # Celery not available, tasks will run synchronously
#     pass