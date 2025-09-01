"""
Bulk Export Service for Report Center
Handles batch processing of multiple reports with various export formats
"""

import os
import tempfile
import zipfile
from datetime import datetime
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

from django.conf import settings
from django.core.files.base import ContentFile
from celery import shared_task

from .report_generator import ReportGeneratorService
from .report_file_storage import ReportFileStorageService
from ..models import Report, ReportTemplate, BulkExportJob
from core.models import Client, Scenario

logger = logging.getLogger(__name__)


class BulkExportService:
    """Service for handling bulk export operations"""
    
    def __init__(self):
        self.report_generator = ReportGeneratorService()
        self.storage_service = ReportFileStorageService()
        self.max_concurrent_exports = getattr(settings, 'BULK_EXPORT_MAX_CONCURRENT', 5)
    
    def initiate_bulk_export(
        self, 
        user_id: int,
        export_config: Dict[str, Any],
        client_ids: Optional[List[int]] = None,
        scenario_ids: Optional[List[int]] = None,
        template_ids: Optional[List[int]] = None
    ) -> BulkExportJob:
        """
        Initiate a bulk export job
        
        Args:
            user_id: ID of the user requesting the export
            export_config: Configuration for the export (formats, options, etc.)
            client_ids: List of client IDs to export (optional)
            scenario_ids: List of scenario IDs to export (optional)
            template_ids: List of template IDs to use (optional)
        
        Returns:
            BulkExportJob instance
        """
        try:
            # Create bulk export job record
            bulk_job = BulkExportJob.objects.create(
                user_id=user_id,
                status='pending',
                export_config=export_config,
                client_ids=client_ids or [],
                scenario_ids=scenario_ids or [],
                template_ids=template_ids or [],
                total_items=self._calculate_total_items(client_ids, scenario_ids, template_ids),
                progress=0
            )
            
            # Start asynchronous processing
            process_bulk_export_job.delay(bulk_job.id)
            
            logger.info(f"Initiated bulk export job {bulk_job.id} for user {user_id}")
            return bulk_job
            
        except Exception as e:
            logger.error(f"Error initiating bulk export: {str(e)}")
            raise
    
    def _calculate_total_items(
        self, 
        client_ids: Optional[List[int]], 
        scenario_ids: Optional[List[int]], 
        template_ids: Optional[List[int]]
    ) -> int:
        """Calculate total number of items to be exported"""
        total = 0
        
        if client_ids and template_ids:
            total += len(client_ids) * len(template_ids)
        elif scenario_ids and template_ids:
            total += len(scenario_ids) * len(template_ids)
        elif client_ids:
            total += len(client_ids)
        elif scenario_ids:
            total += len(scenario_ids)
        else:
            total = 1
            
        return total
    
    def process_bulk_export_job(self, job_id: int) -> Dict[str, Any]:
        """
        Process a bulk export job
        
        Args:
            job_id: ID of the bulk export job
            
        Returns:
            Dictionary with job results
        """
        try:
            bulk_job = BulkExportJob.objects.get(id=job_id)
            bulk_job.status = 'processing'
            bulk_job.started_at = datetime.now()
            bulk_job.save()
            
            export_results = []
            failed_exports = []
            
            # Determine export strategy
            if bulk_job.client_ids and bulk_job.template_ids:
                export_results, failed_exports = self._export_clients_with_templates(bulk_job)
            elif bulk_job.scenario_ids and bulk_job.template_ids:
                export_results, failed_exports = self._export_scenarios_with_templates(bulk_job)
            elif bulk_job.client_ids:
                export_results, failed_exports = self._export_clients_default(bulk_job)
            elif bulk_job.scenario_ids:
                export_results, failed_exports = self._export_scenarios_default(bulk_job)
            else:
                raise ValueError("Invalid export configuration")
            
            # Create archive if multiple files
            final_file_path = None
            if len(export_results) > 1:
                final_file_path = self._create_export_archive(bulk_job, export_results)
            elif export_results:
                final_file_path = export_results[0]['file_path']
            
            # Update job status
            bulk_job.status = 'completed' if not failed_exports else 'completed_with_errors'
            bulk_job.completed_at = datetime.now()
            bulk_job.file_path = final_file_path
            bulk_job.successful_exports = len(export_results)
            bulk_job.failed_exports = len(failed_exports)
            bulk_job.error_details = failed_exports if failed_exports else None
            bulk_job.save()
            
            logger.info(f"Completed bulk export job {job_id}")
            
            return {
                'job_id': job_id,
                'status': bulk_job.status,
                'successful_exports': len(export_results),
                'failed_exports': len(failed_exports),
                'file_path': final_file_path,
                'errors': failed_exports
            }
            
        except Exception as e:
            logger.error(f"Error processing bulk export job {job_id}: {str(e)}")
            
            # Update job with error status
            try:
                bulk_job = BulkExportJob.objects.get(id=job_id)
                bulk_job.status = 'failed'
                bulk_job.completed_at = datetime.now()
                bulk_job.error_message = str(e)
                bulk_job.save()
            except:
                pass
                
            raise
    
    def _export_clients_with_templates(self, bulk_job: BulkExportJob) -> tuple:
        """Export reports for multiple clients using multiple templates"""
        export_results = []
        failed_exports = []
        completed_items = 0
        
        clients = Client.objects.filter(id__in=bulk_job.client_ids)
        templates = ReportTemplate.objects.filter(id__in=bulk_job.template_ids)
        
        with ThreadPoolExecutor(max_workers=self.max_concurrent_exports) as executor:
            # Submit all export tasks
            future_to_info = {}
            for client in clients:
                for template in templates:
                    future = executor.submit(
                        self._export_single_client_report,
                        client,
                        template,
                        bulk_job.export_config
                    )
                    future_to_info[future] = {
                        'client': client,
                        'template': template,
                        'type': 'client_template'
                    }
            
            # Collect results
            for future in as_completed(future_to_info):
                info = future_to_info[future]
                completed_items += 1
                
                try:
                    result = future.result()
                    export_results.append({
                        'client_name': f"{info['client'].first_name} {info['client'].last_name}",
                        'template_name': info['template'].name,
                        'file_path': result['file_path'],
                        'file_name': result['file_name']
                    })
                except Exception as e:
                    failed_exports.append({
                        'client_name': f"{info['client'].first_name} {info['client'].last_name}",
                        'template_name': info['template'].name,
                        'error': str(e)
                    })
                
                # Update progress
                progress = int((completed_items / bulk_job.total_items) * 100)
                bulk_job.progress = progress
                bulk_job.save(update_fields=['progress'])
        
        return export_results, failed_exports
    
    def _export_scenarios_with_templates(self, bulk_job: BulkExportJob) -> tuple:
        """Export reports for multiple scenarios using multiple templates"""
        export_results = []
        failed_exports = []
        completed_items = 0
        
        scenarios = Scenario.objects.filter(id__in=bulk_job.scenario_ids)
        templates = ReportTemplate.objects.filter(id__in=bulk_job.template_ids)
        
        with ThreadPoolExecutor(max_workers=self.max_concurrent_exports) as executor:
            future_to_info = {}
            for scenario in scenarios:
                for template in templates:
                    future = executor.submit(
                        self._export_single_scenario_report,
                        scenario,
                        template,
                        bulk_job.export_config
                    )
                    future_to_info[future] = {
                        'scenario': scenario,
                        'template': template,
                        'type': 'scenario_template'
                    }
            
            # Collect results
            for future in as_completed(future_to_info):
                info = future_to_info[future]
                completed_items += 1
                
                try:
                    result = future.result()
                    export_results.append({
                        'scenario_name': info['scenario'].name,
                        'client_name': f"{info['scenario'].client.first_name} {info['scenario'].client.last_name}",
                        'template_name': info['template'].name,
                        'file_path': result['file_path'],
                        'file_name': result['file_name']
                    })
                except Exception as e:
                    failed_exports.append({
                        'scenario_name': info['scenario'].name,
                        'template_name': info['template'].name,
                        'error': str(e)
                    })
                
                # Update progress
                progress = int((completed_items / bulk_job.total_items) * 100)
                bulk_job.progress = progress
                bulk_job.save(update_fields=['progress'])
        
        return export_results, failed_exports
    
    def _export_clients_default(self, bulk_job: BulkExportJob) -> tuple:
        """Export reports for multiple clients using default template"""
        export_results = []
        failed_exports = []
        completed_items = 0
        
        clients = Client.objects.filter(id__in=bulk_job.client_ids)
        default_template = ReportTemplate.objects.filter(is_default=True).first()
        
        if not default_template:
            raise ValueError("No default template found for bulk export")
        
        with ThreadPoolExecutor(max_workers=self.max_concurrent_exports) as executor:
            future_to_client = {
                executor.submit(
                    self._export_single_client_report,
                    client,
                    default_template,
                    bulk_job.export_config
                ): client
                for client in clients
            }
            
            for future in as_completed(future_to_client):
                client = future_to_client[future]
                completed_items += 1
                
                try:
                    result = future.result()
                    export_results.append({
                        'client_name': f"{client.first_name} {client.last_name}",
                        'template_name': default_template.name,
                        'file_path': result['file_path'],
                        'file_name': result['file_name']
                    })
                except Exception as e:
                    failed_exports.append({
                        'client_name': f"{client.first_name} {client.last_name}",
                        'error': str(e)
                    })
                
                # Update progress
                progress = int((completed_items / bulk_job.total_items) * 100)
                bulk_job.progress = progress
                bulk_job.save(update_fields=['progress'])
        
        return export_results, failed_exports
    
    def _export_scenarios_default(self, bulk_job: BulkExportJob) -> tuple:
        """Export reports for multiple scenarios using default template"""
        export_results = []
        failed_exports = []
        completed_items = 0
        
        scenarios = Scenario.objects.filter(id__in=bulk_job.scenario_ids)
        default_template = ReportTemplate.objects.filter(is_default=True).first()
        
        if not default_template:
            raise ValueError("No default template found for bulk export")
        
        with ThreadPoolExecutor(max_workers=self.max_concurrent_exports) as executor:
            future_to_scenario = {
                executor.submit(
                    self._export_single_scenario_report,
                    scenario,
                    default_template,
                    bulk_job.export_config
                ): scenario
                for scenario in scenarios
            }
            
            for future in as_completed(future_to_scenario):
                scenario = future_to_scenario[future]
                completed_items += 1
                
                try:
                    result = future.result()
                    export_results.append({
                        'scenario_name': scenario.name,
                        'client_name': f"{scenario.client.first_name} {scenario.client.last_name}",
                        'template_name': default_template.name,
                        'file_path': result['file_path'],
                        'file_name': result['file_name']
                    })
                except Exception as e:
                    failed_exports.append({
                        'scenario_name': scenario.name,
                        'error': str(e)
                    })
                
                # Update progress
                progress = int((completed_items / bulk_job.total_items) * 100)
                bulk_job.progress = progress
                bulk_job.save(update_fields=['progress'])
        
        return export_results, failed_exports
    
    def _export_single_client_report(
        self, 
        client: Client, 
        template: ReportTemplate, 
        export_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Export a single client report"""
        try:
            # Get client's primary scenario or create a default one
            scenario = client.scenarios.filter(is_primary=True).first()
            if not scenario:
                scenario = client.scenarios.first()
            
            if not scenario:
                raise ValueError(f"No scenario found for client {client.first_name} {client.last_name}")
            
            return self._export_single_scenario_report(scenario, template, export_config)
            
        except Exception as e:
            logger.error(f"Error exporting report for client {client.id}: {str(e)}")
            raise
    
    def _export_single_scenario_report(
        self, 
        scenario: Scenario, 
        template: ReportTemplate, 
        export_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Export a single scenario report"""
        try:
            # Generate report data
            report_data = {
                'client': scenario.client,
                'scenario': scenario,
                'scenario_results': scenario.get_calculated_results(),
                'template': template
            }
            
            # Determine export format
            export_format = export_config.get('format', 'pdf').lower()
            
            if export_format == 'pdf':
                file_content, file_name = self.report_generator.generate_pdf_report(
                    template.sections, 
                    report_data,
                    export_config.get('pdf_options', {})
                )
            elif export_format == 'excel':
                file_content, file_name = self.report_generator.generate_excel_report(
                    template.sections,
                    report_data,
                    export_config.get('excel_options', {})
                )
            elif export_format == 'powerpoint':
                file_content, file_name = self.report_generator.generate_powerpoint_report(
                    template.sections,
                    report_data,
                    export_config.get('powerpoint_options', {})
                )
            else:
                raise ValueError(f"Unsupported export format: {export_format}")
            
            # Store file
            file_path = self.storage_service.store_report_file(
                file_content,
                file_name,
                f"bulk_exports/{datetime.now().strftime('%Y/%m/%d')}"
            )
            
            return {
                'file_path': file_path,
                'file_name': file_name,
                'scenario_id': scenario.id,
                'client_id': scenario.client.id
            }
            
        except Exception as e:
            logger.error(f"Error exporting report for scenario {scenario.id}: {str(e)}")
            raise
    
    def _create_export_archive(self, bulk_job: BulkExportJob, export_results: List[Dict]) -> str:
        """Create a ZIP archive containing all exported files"""
        try:
            # Create temporary zip file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_zip:
                with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for result in export_results:
                        # Create organized folder structure
                        if 'client_name' in result and 'template_name' in result:
                            if 'scenario_name' in result:
                                folder_path = f"{result['client_name']}/{result['scenario_name']}"
                            else:
                                folder_path = result['client_name']
                        else:
                            folder_path = "Reports"
                        
                        # Add file to zip with organized path
                        archive_path = f"{folder_path}/{result['file_name']}"
                        
                        # Read file content from storage
                        file_content = self.storage_service.get_file_content(result['file_path'])
                        zip_file.writestr(archive_path, file_content)
                
                # Store the archive
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                archive_name = f"bulk_export_{bulk_job.id}_{timestamp}.zip"
                
                with open(temp_zip.name, 'rb') as zip_file:
                    zip_content = zip_file.read()
                
                archive_path = self.storage_service.store_report_file(
                    zip_content,
                    archive_name,
                    f"bulk_exports/{datetime.now().strftime('%Y/%m/%d')}"
                )
                
                # Clean up temp file
                os.unlink(temp_zip.name)
                
                return archive_path
                
        except Exception as e:
            logger.error(f"Error creating export archive for job {bulk_job.id}: {str(e)}")
            raise
    
    def get_job_status(self, job_id: int) -> Dict[str, Any]:
        """Get the status of a bulk export job"""
        try:
            bulk_job = BulkExportJob.objects.get(id=job_id)
            
            return {
                'id': bulk_job.id,
                'status': bulk_job.status,
                'progress': bulk_job.progress,
                'total_items': bulk_job.total_items,
                'successful_exports': bulk_job.successful_exports or 0,
                'failed_exports': bulk_job.failed_exports or 0,
                'started_at': bulk_job.started_at,
                'completed_at': bulk_job.completed_at,
                'file_path': bulk_job.file_path,
                'error_message': bulk_job.error_message,
                'error_details': bulk_job.error_details
            }
            
        except BulkExportJob.DoesNotExist:
            raise ValueError(f"Bulk export job {job_id} not found")
    
    def cancel_job(self, job_id: int) -> bool:
        """Cancel a running bulk export job"""
        try:
            bulk_job = BulkExportJob.objects.get(id=job_id)
            
            if bulk_job.status in ['pending', 'processing']:
                bulk_job.status = 'cancelled'
                bulk_job.completed_at = datetime.now()
                bulk_job.save()
                return True
            
            return False
            
        except BulkExportJob.DoesNotExist:
            raise ValueError(f"Bulk export job {job_id} not found")


@shared_task(bind=True)
def process_bulk_export_job(self, job_id: int):
    """Celery task for processing bulk export jobs"""
    service = BulkExportService()
    try:
        return service.process_bulk_export_job(job_id)
    except Exception as e:
        # Update job status on failure
        try:
            bulk_job = BulkExportJob.objects.get(id=job_id)
            bulk_job.status = 'failed'
            bulk_job.error_message = str(e)
            bulk_job.completed_at = datetime.now()
            bulk_job.save()
        except:
            pass
        raise