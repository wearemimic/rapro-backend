"""
Management command to analyze communications with AI
Can be run manually or scheduled via cron
"""

import logging
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q

from core.models import Communication
from core.services.ai_email_service import AIEmailService, analyze_communications_batch

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Analyze communications with AI for sentiment, urgency, and priority scoring'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=50,
            help='Number of communications to process in each batch'
        )
        parser.add_argument(
            '--max-age-days',
            type=int,
            default=30,
            help='Only analyze communications created within this many days'
        )
        parser.add_argument(
            '--force-reanalyze',
            action='store_true',
            help='Re-analyze communications that already have AI analysis'
        )
        parser.add_argument(
            '--advisor-id',
            type=int,
            help='Only analyze communications for specific advisor ID'
        )
        parser.add_argument(
            '--communication-ids',
            type=str,
            help='Comma-separated list of specific communication IDs to analyze'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be analyzed without actually running AI analysis'
        )
    
    def handle(self, *args, **options):
        self.stdout.write("Starting AI communication analysis...")
        
        try:
            # Initialize AI service
            ai_service = AIEmailService()
            
            # Get communications to analyze
            queryset = self._build_queryset(options)
            total_count = queryset.count()
            
            if total_count == 0:
                self.stdout.write(
                    self.style.WARNING("No communications found matching criteria")
                )
                return
            
            self.stdout.write(f"Found {total_count} communications to analyze")
            
            if options['dry_run']:
                self._show_dry_run_info(queryset)
                return
            
            # Process in batches
            batch_size = options['batch_size']
            processed = 0
            errors = []
            
            for i in range(0, total_count, batch_size):
                batch_queryset = queryset[i:i + batch_size]
                batch_ids = list(batch_queryset.values_list('id', flat=True))
                
                self.stdout.write(f"Processing batch {i//batch_size + 1}: IDs {batch_ids}")
                
                # Analyze batch
                batch_results = analyze_communications_batch(batch_ids)
                
                processed += batch_results['success']
                errors.extend(batch_results['errors'])
                
                # Show progress
                self.stdout.write(
                    f"Batch completed: {batch_results['success']} success, "
                    f"{batch_results['failed']} failed"
                )
            
            # Final summary
            self.stdout.write(
                self.style.SUCCESS(
                    f"Analysis completed! Processed: {processed}/{total_count}"
                )
            )
            
            if errors:
                self.stdout.write(
                    self.style.ERROR(f"Errors encountered: {len(errors)}")
                )
                for error in errors[:10]:  # Show first 10 errors
                    self.stdout.write(f"  - {error}")
                
                if len(errors) > 10:
                    self.stdout.write(f"  ... and {len(errors) - 10} more errors")
        
        except Exception as e:
            logger.error(f"AI analysis command failed: {str(e)}")
            raise CommandError(f"Command failed: {str(e)}")
    
    def _build_queryset(self, options):
        """Build queryset based on command options"""
        queryset = Communication.objects.all()
        
        # Filter by advisor if specified
        if options['advisor_id']:
            queryset = queryset.filter(advisor_id=options['advisor_id'])
        
        # Filter by specific communication IDs if provided
        if options['communication_ids']:
            try:
                comm_ids = [
                    int(id.strip()) 
                    for id in options['communication_ids'].split(',')
                ]
                queryset = queryset.filter(id__in=comm_ids)
            except ValueError:
                raise CommandError("Invalid communication IDs format")
        else:
            # Filter by age if not analyzing specific IDs
            if options['max_age_days']:
                cutoff_date = timezone.now() - timedelta(days=options['max_age_days'])
                queryset = queryset.filter(created_at__gte=cutoff_date)
        
        # Filter by analysis status
        if not options['force_reanalyze']:
            # Only analyze communications without AI analysis
            queryset = queryset.filter(
                Q(ai_analysis_date__isnull=True) |
                Q(ai_sentiment_score__isnull=True)
            )
        
        # Only analyze email communications (most suitable for AI analysis)
        queryset = queryset.filter(communication_type='email')
        
        # Order by priority (newest first, then by any existing priority score)
        queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def _show_dry_run_info(self, queryset):
        """Show information about what would be processed in dry run mode"""
        self.stdout.write(self.style.WARNING("DRY RUN MODE - No actual analysis will be performed"))
        self.stdout.write("")
        
        # Show breakdown by advisor
        advisor_counts = {}
        for comm in queryset.select_related('advisor')[:100]:  # Limit for performance
            advisor_name = f"{comm.advisor.first_name} {comm.advisor.last_name}"
            advisor_counts[advisor_name] = advisor_counts.get(advisor_name, 0) + 1
        
        if advisor_counts:
            self.stdout.write("Communications by advisor:")
            for advisor, count in advisor_counts.items():
                self.stdout.write(f"  - {advisor}: {count}")
        
        # Show sample communications
        sample_comms = queryset[:5]
        if sample_comms:
            self.stdout.write("\nSample communications:")
            for comm in sample_comms:
                contact = comm.client or comm.lead
                contact_name = f"{contact.first_name} {contact.last_name}" if contact else "Unknown"
                self.stdout.write(
                    f"  - ID {comm.id}: {comm.subject[:50]}... "
                    f"({contact_name}, {comm.created_at.strftime('%Y-%m-%d')})"
                )