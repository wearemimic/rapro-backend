"""
Report Scheduling Service
Handles creation, management, and execution of scheduled reports
"""

import logging
from datetime import datetime, timedelta, time
from typing import List, Dict, Any, Optional
import pytz
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMessage
from django.template import Context, Template
from celery import shared_task

from ..models import ReportSchedule, ReportScheduleExecution, ReportTemplate
from .report_generator import ReportGeneratorService
from .report_file_storage import ReportFileStorageService
from core.models import Client, Scenario

logger = logging.getLogger(__name__)


class ReportSchedulerService:
    """Service for managing report schedules and executions"""
    
    def __init__(self):
        self.report_generator = ReportGeneratorService()
        self.storage_service = ReportFileStorageService()
    
    def create_schedule(
        self,
        user_id: int,
        schedule_data: Dict[str, Any]
    ) -> ReportSchedule:
        """
        Create a new report schedule
        
        Args:
            user_id: ID of the user creating the schedule
            schedule_data: Schedule configuration data
            
        Returns:
            ReportSchedule instance
        """
        try:
            # Validate template exists and user has access
            template = ReportTemplate.objects.get(
                id=schedule_data['template_id'],
                created_by_id=user_id
            )
            
            # Calculate next run time
            next_run = self._calculate_next_run(
                schedule_data['frequency'],
                schedule_data.get('frequency_config', {}),
                schedule_data['scheduled_time'],
                schedule_data.get('timezone', 'UTC')
            )
            
            # Create schedule
            schedule = ReportSchedule.objects.create(
                user_id=user_id,
                name=schedule_data['name'],
                description=schedule_data.get('description', ''),
                template=template,
                client_id=schedule_data.get('client_id'),
                scenario_id=schedule_data.get('scenario_id'),
                client_filter=schedule_data.get('client_filter'),
                frequency=schedule_data['frequency'],
                frequency_config=schedule_data.get('frequency_config', {}),
                scheduled_time=schedule_data['scheduled_time'],
                timezone=schedule_data.get('timezone', 'UTC'),
                format=schedule_data.get('format', 'pdf'),
                generation_options=schedule_data.get('generation_options', {}),
                auto_email=schedule_data.get('auto_email', False),
                email_recipients=schedule_data.get('email_recipients', []),
                email_subject_template=schedule_data.get('email_subject_template', ''),
                email_body_template=schedule_data.get('email_body_template', ''),
                next_run=next_run,
                end_date=schedule_data.get('end_date'),
                max_runs=schedule_data.get('max_runs')
            )
            
            logger.info(f"Created report schedule {schedule.id} for user {user_id}")
            return schedule
            
        except Exception as e:
            logger.error(f"Error creating report schedule: {str(e)}")
            raise
    
    def update_schedule(
        self,
        schedule_id: int,
        user_id: int,
        update_data: Dict[str, Any]
    ) -> ReportSchedule:
        """
        Update an existing report schedule
        
        Args:
            schedule_id: ID of the schedule to update
            user_id: ID of the user updating the schedule
            update_data: Updated schedule data
            
        Returns:
            Updated ReportSchedule instance
        """
        try:
            schedule = ReportSchedule.objects.get(
                id=schedule_id,
                user_id=user_id
            )
            
            # Update fields
            for field, value in update_data.items():
                if hasattr(schedule, field):
                    setattr(schedule, field, value)
            
            # Recalculate next run if scheduling changed
            if any(field in update_data for field in ['frequency', 'frequency_config', 'scheduled_time', 'timezone']):
                schedule.next_run = self._calculate_next_run(
                    schedule.frequency,
                    schedule.frequency_config,
                    schedule.scheduled_time,
                    schedule.timezone
                )
            
            schedule.save()
            
            logger.info(f"Updated report schedule {schedule_id}")
            return schedule
            
        except ReportSchedule.DoesNotExist:
            raise ValueError(f"Report schedule {schedule_id} not found or not accessible")
        except Exception as e:
            logger.error(f"Error updating report schedule {schedule_id}: {str(e)}")
            raise
    
    def delete_schedule(self, schedule_id: int, user_id: int) -> bool:
        """
        Delete a report schedule
        
        Args:
            schedule_id: ID of the schedule to delete
            user_id: ID of the user deleting the schedule
            
        Returns:
            True if deleted successfully
        """
        try:
            schedule = ReportSchedule.objects.get(
                id=schedule_id,
                user_id=user_id
            )
            
            schedule.delete()
            
            logger.info(f"Deleted report schedule {schedule_id}")
            return True
            
        except ReportSchedule.DoesNotExist:
            raise ValueError(f"Report schedule {schedule_id} not found or not accessible")
        except Exception as e:
            logger.error(f"Error deleting report schedule {schedule_id}: {str(e)}")
            raise
    
    def pause_schedule(self, schedule_id: int, user_id: int) -> ReportSchedule:
        """Pause a report schedule"""
        try:
            schedule = ReportSchedule.objects.get(
                id=schedule_id,
                user_id=user_id
            )
            
            schedule.status = 'paused'
            schedule.save()
            
            logger.info(f"Paused report schedule {schedule_id}")
            return schedule
            
        except ReportSchedule.DoesNotExist:
            raise ValueError(f"Report schedule {schedule_id} not found or not accessible")
    
    def resume_schedule(self, schedule_id: int, user_id: int) -> ReportSchedule:
        """Resume a paused report schedule"""
        try:
            schedule = ReportSchedule.objects.get(
                id=schedule_id,
                user_id=user_id
            )
            
            schedule.status = 'active'
            # Recalculate next run time
            schedule.next_run = self._calculate_next_run(
                schedule.frequency,
                schedule.frequency_config,
                schedule.scheduled_time,
                schedule.timezone
            )
            schedule.save()
            
            logger.info(f"Resumed report schedule {schedule_id}")
            return schedule
            
        except ReportSchedule.DoesNotExist:
            raise ValueError(f"Report schedule {schedule_id} not found or not accessible")
    
    def get_due_schedules(self) -> List[ReportSchedule]:
        """
        Get all schedules that are due to run
        
        Returns:
            List of ReportSchedule instances due for execution
        """
        now = timezone.now()
        
        return ReportSchedule.objects.filter(
            status='active',
            next_run__lte=now
        ).filter(
            # Not ended
            models.Q(end_date__isnull=True) | models.Q(end_date__gt=now),
            # Not reached max runs
            models.Q(max_runs__isnull=True) | models.Q(run_count__lt=models.F('max_runs'))
        )
    
    def execute_schedule(self, schedule_id: int) -> Dict[str, Any]:
        """
        Execute a scheduled report generation
        
        Args:
            schedule_id: ID of the schedule to execute
            
        Returns:
            Dictionary with execution results
        """
        try:
            schedule = ReportSchedule.objects.get(id=schedule_id)
            
            # Create execution record
            execution = ReportScheduleExecution.objects.create(
                schedule=schedule,
                scheduled_for=schedule.next_run or timezone.now(),
                status='running'
            )
            
            start_time = timezone.now()
            execution.started_at = start_time
            execution.save()
            
            try:
                # Generate reports
                generated_reports = self._generate_scheduled_reports(schedule)
                
                # Send emails if configured
                emails_sent = 0
                if schedule.auto_email and schedule.email_recipients:
                    emails_sent = self._send_scheduled_report_emails(
                        schedule,
                        generated_reports
                    )
                
                # Update execution record
                execution.status = 'completed'
                execution.completed_at = timezone.now()
                execution.generated_reports = generated_reports
                execution.emails_sent = emails_sent
                execution.reports_generated = len(generated_reports)
                execution.execution_time_seconds = (
                    execution.completed_at - execution.started_at
                ).total_seconds()
                execution.save()
                
                # Update schedule counters
                schedule.last_run = execution.completed_at
                schedule.run_count += 1
                schedule.success_count += 1
                schedule.next_run = self._calculate_next_run(
                    schedule.frequency,
                    schedule.frequency_config,
                    schedule.scheduled_time,
                    schedule.timezone
                )
                schedule.save()
                
                logger.info(f"Successfully executed schedule {schedule_id}")
                
                return {
                    'schedule_id': schedule_id,
                    'execution_id': execution.id,
                    'status': 'completed',
                    'reports_generated': len(generated_reports),
                    'emails_sent': emails_sent,
                    'execution_time': execution.execution_time_seconds
                }
                
            except Exception as e:
                # Update execution record with error
                execution.status = 'failed'
                execution.completed_at = timezone.now()
                execution.error_message = str(e)
                execution.execution_time_seconds = (
                    execution.completed_at - execution.started_at
                ).total_seconds()
                execution.save()
                
                # Update schedule counters
                schedule.run_count += 1
                schedule.failure_count += 1
                schedule.last_run = execution.completed_at
                schedule.next_run = self._calculate_next_run(
                    schedule.frequency,
                    schedule.frequency_config,
                    schedule.scheduled_time,
                    schedule.timezone
                )
                schedule.save()
                
                logger.error(f"Failed to execute schedule {schedule_id}: {str(e)}")
                raise
                
        except ReportSchedule.DoesNotExist:
            raise ValueError(f"Report schedule {schedule_id} not found")
        except Exception as e:
            logger.error(f"Error executing schedule {schedule_id}: {str(e)}")
            raise
    
    def _generate_scheduled_reports(self, schedule: ReportSchedule) -> List[Dict[str, Any]]:
        """
        Generate reports for a scheduled execution
        
        Args:
            schedule: ReportSchedule instance
            
        Returns:
            List of generated report information
        """
        generated_reports = []
        
        try:
            if schedule.client:
                # Single client report
                report_info = self._generate_single_report(
                    schedule,
                    schedule.client,
                    schedule.scenario
                )
                generated_reports.append(report_info)
                
            elif schedule.scenario:
                # Single scenario report
                report_info = self._generate_single_report(
                    schedule,
                    schedule.scenario.client,
                    schedule.scenario
                )
                generated_reports.append(report_info)
                
            elif schedule.client_filter:
                # Bulk report generation based on client filter
                clients = self._get_filtered_clients(schedule.client_filter, schedule.user_id)
                
                for client in clients:
                    try:
                        # Get client's primary or first scenario
                        scenario = client.scenarios.filter(is_primary=True).first()
                        if not scenario:
                            scenario = client.scenarios.first()
                        
                        if scenario:
                            report_info = self._generate_single_report(
                                schedule,
                                client,
                                scenario
                            )
                            generated_reports.append(report_info)
                    except Exception as e:
                        logger.error(f"Error generating report for client {client.id}: {str(e)}")
                        continue
            else:
                raise ValueError("No target specified for report generation")
            
            return generated_reports
            
        except Exception as e:
            logger.error(f"Error generating scheduled reports: {str(e)}")
            raise
    
    def _generate_single_report(
        self,
        schedule: ReportSchedule,
        client: Client,
        scenario: Optional[Scenario] = None
    ) -> Dict[str, Any]:
        """
        Generate a single report for the schedule
        
        Args:
            schedule: ReportSchedule instance
            client: Client for the report
            scenario: Optional Scenario for the report
            
        Returns:
            Dictionary with report information
        """
        try:
            # Prepare report data
            report_data = {
                'client': client,
                'scenario': scenario,
                'scenario_results': scenario.get_calculated_results() if scenario else {},
                'template': schedule.template
            }
            
            # Generate report based on format
            if schedule.format == 'pdf':
                file_content, file_name = self.report_generator.generate_pdf_report(
                    schedule.template.sections.all(),
                    report_data,
                    schedule.generation_options
                )
            elif schedule.format == 'excel':
                file_content, file_name = self.report_generator.generate_excel_report(
                    schedule.template.sections.all(),
                    report_data,
                    schedule.generation_options
                )
            elif schedule.format == 'powerpoint':
                file_content, file_name = self.report_generator.generate_powerpoint_report(
                    schedule.template.sections.all(),
                    report_data,
                    schedule.generation_options
                )
            elif schedule.format == 'both':
                # Generate both PDF and PowerPoint
                pdf_content, pdf_name = self.report_generator.generate_pdf_report(
                    schedule.template.sections.all(),
                    report_data,
                    schedule.generation_options
                )
                pptx_content, pptx_name = self.report_generator.generate_powerpoint_report(
                    schedule.template.sections.all(),
                    report_data,
                    schedule.generation_options
                )
                
                # Store both files
                pdf_path = self.storage_service.store_report_file(
                    pdf_content,
                    pdf_name,
                    f"scheduled_reports/{schedule.id}/{datetime.now().strftime('%Y/%m/%d')}"
                )
                pptx_path = self.storage_service.store_report_file(
                    pptx_content,
                    pptx_name,
                    f"scheduled_reports/{schedule.id}/{datetime.now().strftime('%Y/%m/%d')}"
                )
                
                return {
                    'client_id': client.id,
                    'scenario_id': scenario.id if scenario else None,
                    'file_paths': [pdf_path, pptx_path],
                    'file_names': [pdf_name, pptx_name],
                    'format': 'both'
                }
            else:
                raise ValueError(f"Unsupported format: {schedule.format}")
            
            # Store single file
            if schedule.format != 'both':
                file_path = self.storage_service.store_report_file(
                    file_content,
                    file_name,
                    f"scheduled_reports/{schedule.id}/{datetime.now().strftime('%Y/%m/%d')}"
                )
                
                return {
                    'client_id': client.id,
                    'scenario_id': scenario.id if scenario else None,
                    'file_path': file_path,
                    'file_name': file_name,
                    'format': schedule.format
                }
            
        except Exception as e:
            logger.error(f"Error generating single report: {str(e)}")
            raise
    
    def _get_filtered_clients(self, client_filter: Dict[str, Any], user_id: int) -> List[Client]:
        """
        Get clients based on filter criteria
        
        Args:
            client_filter: Filter criteria
            user_id: User ID for filtering
            
        Returns:
            List of filtered clients
        """
        queryset = Client.objects.filter(advisor_id=user_id)
        
        # Apply filters
        if client_filter.get('tags'):
            queryset = queryset.filter(tags__overlap=client_filter['tags'])
        
        if client_filter.get('created_after'):
            queryset = queryset.filter(created_at__gte=client_filter['created_after'])
        
        if client_filter.get('created_before'):
            queryset = queryset.filter(created_at__lte=client_filter['created_before'])
        
        if client_filter.get('has_scenarios'):
            queryset = queryset.filter(scenarios__isnull=False)
        
        return list(queryset.distinct())
    
    def _send_scheduled_report_emails(
        self,
        schedule: ReportSchedule,
        generated_reports: List[Dict[str, Any]]
    ) -> int:
        """
        Send emails for scheduled reports
        
        Args:
            schedule: ReportSchedule instance
            generated_reports: List of generated report information
            
        Returns:
            Number of emails sent
        """
        emails_sent = 0
        
        try:
            for report_info in generated_reports:
                client_id = report_info.get('client_id')
                client = Client.objects.get(id=client_id) if client_id else None
                
                # Prepare email context
                context = {
                    'client': client,
                    'schedule': schedule,
                    'report_info': report_info,
                    'user': schedule.user
                }
                
                # Render email subject and body
                subject = self._render_email_template(
                    schedule.email_subject_template or f"Scheduled Report: {schedule.name}",
                    context
                )
                body = self._render_email_template(
                    schedule.email_body_template or "Please find your scheduled report attached.",
                    context
                )
                
                # Create email
                email = EmailMessage(
                    subject=subject,
                    body=body,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@retirementadvisorpro.com'),
                    to=schedule.email_recipients
                )
                
                # Attach report files
                if 'file_path' in report_info:
                    file_content = self.storage_service.get_file_content(report_info['file_path'])
                    email.attach(report_info['file_name'], file_content)
                elif 'file_paths' in report_info:
                    for file_path, file_name in zip(report_info['file_paths'], report_info['file_names']):
                        file_content = self.storage_service.get_file_content(file_path)
                        email.attach(file_name, file_content)
                
                # Send email
                email.send()
                emails_sent += 1
            
            logger.info(f"Sent {emails_sent} scheduled report emails")
            return emails_sent
            
        except Exception as e:
            logger.error(f"Error sending scheduled report emails: {str(e)}")
            raise
    
    def _render_email_template(self, template_string: str, context: Dict[str, Any]) -> str:
        """Render an email template with context variables"""
        try:
            template = Template(template_string)
            return template.render(Context(context))
        except Exception as e:
            logger.error(f"Error rendering email template: {str(e)}")
            return template_string
    
    def _calculate_next_run(
        self,
        frequency: str,
        frequency_config: Dict[str, Any],
        scheduled_time: time,
        timezone_name: str
    ) -> datetime:
        """
        Calculate the next run time for a schedule
        
        Args:
            frequency: Schedule frequency
            frequency_config: Additional frequency configuration
            scheduled_time: Time of day to run
            timezone_name: Timezone for the schedule
            
        Returns:
            Next run datetime
        """
        try:
            tz = pytz.timezone(timezone_name)
            now = timezone.now().astimezone(tz)
            
            # Combine today's date with scheduled time
            next_run = tz.localize(datetime.combine(now.date(), scheduled_time))
            
            # If the time has already passed today, start with tomorrow
            if next_run <= now:
                next_run += timedelta(days=1)
            
            if frequency == 'daily':
                # Already set to next day if needed
                pass
            elif frequency == 'weekly':
                # Find next occurrence of specified day of week
                target_weekday = frequency_config.get('day_of_week', 0)  # 0 = Monday
                days_ahead = target_weekday - next_run.weekday()
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                next_run += timedelta(days=days_ahead)
            elif frequency == 'monthly':
                # Find next occurrence of specified day of month
                target_day = frequency_config.get('day_of_month', 1)
                
                # Try next month first
                next_month = next_run.replace(day=1) + relativedelta(months=1)
                try:
                    next_run = next_month.replace(day=target_day)
                except ValueError:
                    # Day doesn't exist in next month (e.g., Feb 31), use last day
                    next_run = next_month.replace(day=1) + relativedelta(months=1, days=-1)
            elif frequency == 'quarterly':
                # Add 3 months
                next_run += relativedelta(months=3)
            elif frequency == 'yearly':
                # Add 1 year
                next_run += relativedelta(years=1)
            elif frequency == 'custom':
                # Use custom interval
                interval_type = frequency_config.get('interval_type', 'days')
                interval_value = frequency_config.get('interval_value', 1)
                
                if interval_type == 'days':
                    next_run += timedelta(days=interval_value)
                elif interval_type == 'weeks':
                    next_run += timedelta(weeks=interval_value)
                elif interval_type == 'months':
                    next_run += relativedelta(months=interval_value)
                elif interval_type == 'years':
                    next_run += relativedelta(years=interval_value)
            
            # Convert back to UTC
            return next_run.astimezone(pytz.UTC)
            
        except Exception as e:
            logger.error(f"Error calculating next run time: {str(e)}")
            # Fallback to 24 hours from now
            return timezone.now() + timedelta(days=1)


@shared_task(bind=True)
def execute_scheduled_reports(self):
    """
    Celery task to execute all due scheduled reports
    """
    service = ReportSchedulerService()
    
    try:
        due_schedules = service.get_due_schedules()
        
        results = []
        for schedule in due_schedules:
            try:
                result = service.execute_schedule(schedule.id)
                results.append(result)
            except Exception as e:
                logger.error(f"Error executing schedule {schedule.id}: {str(e)}")
                results.append({
                    'schedule_id': schedule.id,
                    'status': 'failed',
                    'error': str(e)
                })
        
        return {
            'executed_schedules': len(results),
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Error in execute_scheduled_reports task: {str(e)}")
        raise


@shared_task(bind=True)
def execute_single_schedule(self, schedule_id: int):
    """
    Celery task to execute a single scheduled report
    """
    service = ReportSchedulerService()
    
    try:
        return service.execute_schedule(schedule_id)
    except Exception as e:
        logger.error(f"Error executing single schedule {schedule_id}: {str(e)}")
        raise