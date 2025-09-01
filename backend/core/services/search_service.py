# core/services/search_service.py
"""
Global search and advanced filtering service for admin interface
"""

import re
import logging
from typing import Dict, List, Any, Optional, Union
from django.db import models
from django.db.models import Q, QuerySet
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.core.paginator import Paginator
from django.conf import settings
from elasticsearch import Elasticsearch, NotFoundError
from elasticsearch.exceptions import ConnectionError
from .cache_service import CacheService, cached

logger = logging.getLogger(__name__)


class GlobalSearchService:
    """
    Global search service with support for PostgreSQL full-text search and Elasticsearch
    """
    
    def __init__(self):
        self.use_elasticsearch = getattr(settings, 'USE_ELASTICSEARCH', False)
        self.es_client = None
        
        if self.use_elasticsearch:
            try:
                self.es_client = Elasticsearch([
                    getattr(settings, 'ELASTICSEARCH_HOST', 'localhost:9200')
                ])
                # Test connection
                self.es_client.ping()
                logger.info("Elasticsearch connection established")
            except (ConnectionError, Exception) as e:
                logger.warning(f"Elasticsearch not available, falling back to PostgreSQL: {e}")
                self.use_elasticsearch = False
    
    @cached('search_results', key_func=lambda self, query, filters, page: f'search:{hash((query, str(filters), page))}')
    def search(self, query: str, filters: Dict = None, page: int = 1, per_page: int = 20) -> Dict:
        """
        Perform global search across multiple models
        """
        filters = filters or {}
        
        if self.use_elasticsearch:
            return self._elasticsearch_search(query, filters, page, per_page)
        else:
            return self._postgresql_search(query, filters, page, per_page)
    
    def _elasticsearch_search(self, query: str, filters: Dict, page: int, per_page: int) -> Dict:
        """
        Perform search using Elasticsearch
        """
        try:
            # Build search body
            search_body = self._build_elasticsearch_query(query, filters)
            
            # Calculate pagination
            from_offset = (page - 1) * per_page
            
            # Execute search
            response = self.es_client.search(
                index='admin_global_search',
                body=search_body,
                from_=from_offset,
                size=per_page
            )
            
            # Parse results
            results = []
            for hit in response['hits']['hits']:
                results.append({
                    'id': hit['_id'],
                    'type': hit['_source']['type'],
                    'title': hit['_source']['title'],
                    'description': hit['_source']['description'],
                    'url': hit['_source']['url'],
                    'score': hit['_score'],
                    'highlight': hit.get('highlight', {}),
                    'metadata': hit['_source'].get('metadata', {})
                })
            
            return {
                'results': results,
                'total': response['hits']['total']['value'],
                'page': page,
                'per_page': per_page,
                'total_pages': (response['hits']['total']['value'] + per_page - 1) // per_page,
                'search_time': response['took'],
                'facets': self._parse_elasticsearch_facets(response.get('aggregations', {}))
            }
            
        except Exception as e:
            logger.error(f"Elasticsearch search failed: {e}")
            return self._postgresql_search(query, filters, page, per_page)
    
    def _postgresql_search(self, query: str, filters: Dict, page: int, per_page: int) -> Dict:
        """
        Perform search using PostgreSQL full-text search
        """
        from ..models import CustomUser, Client, Scenario, AdminAudit, SupportTicket
        
        results = []
        total_results = 0
        
        # Define searchable models and fields
        search_configs = [
            {
                'model': CustomUser,
                'type': 'user',
                'search_fields': ['first_name', 'last_name', 'email'],
                'title_field': lambda obj: f"{obj.first_name} {obj.last_name}",
                'description_field': lambda obj: obj.email,
                'url_field': lambda obj: f"/admin/users/{obj.id}",
                'filters': {
                    'is_active': 'is_active',
                    'is_staff': 'is_staff',
                    'role': 'role'
                }
            },
            {
                'model': Client,
                'type': 'client',
                'search_fields': ['first_name', 'last_name', 'email'],
                'title_field': lambda obj: f"{obj.first_name} {obj.last_name}",
                'description_field': lambda obj: f"Client - {obj.email}",
                'url_field': lambda obj: f"/admin/clients/{obj.id}",
                'filters': {
                    'advisor': 'advisor_id'
                }
            },
            {
                'model': Scenario,
                'type': 'scenario',
                'search_fields': ['scenario_name', 'description'],
                'title_field': lambda obj: obj.scenario_name,
                'description_field': lambda obj: obj.description or 'Retirement scenario',
                'url_field': lambda obj: f"/admin/scenarios/{obj.id}",
                'filters': {
                    'client': 'client_id'
                }
            },
            {
                'model': SupportTicket,
                'type': 'ticket',
                'search_fields': ['subject', 'description'],
                'title_field': lambda obj: obj.subject,
                'description_field': lambda obj: obj.description[:200],
                'url_field': lambda obj: f"/admin/support/tickets/{obj.id}",
                'filters': {
                    'status': 'status',
                    'priority': 'priority',
                    'category': 'category'
                }
            },
            {
                'model': AdminAudit,
                'type': 'audit',
                'search_fields': ['action', 'description'],
                'title_field': lambda obj: f"Audit: {obj.action}",
                'description_field': lambda obj: obj.description or '',
                'url_field': lambda obj: f"/admin/audit/{obj.id}",
                'filters': {
                    'admin_user': 'admin_user_id',
                    'action': 'action'
                }
            }
        ]
        
        # Search each model
        for config in search_configs:
            model_results = self._search_model(query, config, filters)
            results.extend(model_results)
        
        # Sort by relevance (simple scoring)
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Paginate
        total_results = len(results)
        paginator = Paginator(results, per_page)
        page_results = paginator.get_page(page)
        
        return {
            'results': page_results.object_list,
            'total': total_results,
            'page': page,
            'per_page': per_page,
            'total_pages': paginator.num_pages,
            'search_time': 0,
            'facets': self._generate_facets(results)
        }
    
    def _search_model(self, query: str, config: Dict, filters: Dict) -> List[Dict]:
        """
        Search a specific model
        """
        model = config['model']
        queryset = model.objects.all()
        
        # Apply filters
        for filter_key, filter_value in filters.items():
            if filter_key in config.get('filters', {}) and filter_value:
                field_name = config['filters'][filter_key]
                if isinstance(filter_value, list):
                    queryset = queryset.filter(**{f"{field_name}__in": filter_value})
                else:
                    queryset = queryset.filter(**{field_name: filter_value})
        
        # Build search query
        if query:
            search_q = Q()
            for field in config['search_fields']:
                search_q |= Q(**{f"{field}__icontains": query})
            queryset = queryset.filter(search_q)
        
        # Convert to result format
        results = []
        for obj in queryset[:100]:  # Limit to prevent memory issues
            try:
                score = self._calculate_relevance_score(query, obj, config['search_fields'])
                
                results.append({
                    'id': str(obj.id),
                    'type': config['type'],
                    'title': config['title_field'](obj),
                    'description': config['description_field'](obj),
                    'url': config['url_field'](obj),
                    'score': score,
                    'highlight': self._generate_highlights(query, obj, config['search_fields']),
                    'metadata': {
                        'created_at': getattr(obj, 'created_at', None),
                        'updated_at': getattr(obj, 'updated_at', None),
                    }
                })
            except Exception as e:
                logger.error(f"Error processing search result for {obj}: {e}")
                continue
        
        return results
    
    def _calculate_relevance_score(self, query: str, obj: Any, search_fields: List[str]) -> float:
        """
        Calculate relevance score for search results
        """
        if not query:
            return 1.0
        
        score = 0.0
        query_words = query.lower().split()
        
        for field in search_fields:
            field_value = str(getattr(obj, field, '')).lower()
            
            # Exact match bonus
            if query.lower() in field_value:
                score += 10.0
            
            # Word match scoring
            for word in query_words:
                if word in field_value:
                    score += 2.0
                
                # Partial match
                for field_word in field_value.split():
                    if word in field_word:
                        score += 1.0
        
        return score
    
    def _generate_highlights(self, query: str, obj: Any, search_fields: List[str]) -> Dict:
        """
        Generate search highlights
        """
        highlights = {}
        if not query:
            return highlights
        
        query_pattern = re.compile(re.escape(query), re.IGNORECASE)
        
        for field in search_fields:
            field_value = str(getattr(obj, field, ''))
            if query.lower() in field_value.lower():
                highlighted = query_pattern.sub(f'<mark>{query}</mark>', field_value)
                highlights[field] = highlighted
        
        return highlights
    
    def _generate_facets(self, results: List[Dict]) -> Dict:
        """
        Generate facets from search results
        """
        facets = {}
        
        # Type facets
        type_counts = {}
        for result in results:
            result_type = result['type']
            type_counts[result_type] = type_counts.get(result_type, 0) + 1
        
        facets['types'] = [
            {'value': k, 'count': v, 'label': k.title()}
            for k, v in sorted(type_counts.items())
        ]
        
        return facets
    
    def _build_elasticsearch_query(self, query: str, filters: Dict) -> Dict:
        """
        Build Elasticsearch query
        """
        must_clauses = []
        filter_clauses = []
        
        # Text search
        if query:
            must_clauses.append({
                "multi_match": {
                    "query": query,
                    "fields": ["title^3", "description^2", "content"],
                    "type": "best_fields",
                    "fuzziness": "AUTO"
                }
            })
        
        # Filters
        for key, value in filters.items():
            if value:
                if isinstance(value, list):
                    filter_clauses.append({"terms": {key: value}})
                else:
                    filter_clauses.append({"term": {key: value}})
        
        # Build final query
        es_query = {
            "query": {
                "bool": {
                    "must": must_clauses,
                    "filter": filter_clauses
                }
            },
            "highlight": {
                "fields": {
                    "title": {},
                    "description": {},
                    "content": {}
                }
            },
            "aggs": {
                "types": {
                    "terms": {"field": "type"}
                }
            }
        }
        
        return es_query
    
    def _parse_elasticsearch_facets(self, aggregations: Dict) -> Dict:
        """
        Parse Elasticsearch aggregations into facets
        """
        facets = {}
        
        if 'types' in aggregations:
            facets['types'] = [
                {
                    'value': bucket['key'],
                    'count': bucket['doc_count'],
                    'label': bucket['key'].title()
                }
                for bucket in aggregations['types']['buckets']
            ]
        
        return facets
    
    def get_suggestions(self, query: str, limit: int = 10) -> List[str]:
        """
        Get search suggestions/autocomplete
        """
        if not query or len(query) < 2:
            return []
        
        # This would typically use a dedicated suggestions index
        # For now, return simple suggestions based on recent searches
        cache_key = f"suggestions:{query.lower()[:50]}"
        suggestions = CacheService.get(cache_key)
        
        if suggestions is None:
            suggestions = self._generate_suggestions(query)
            CacheService.set(cache_key, suggestions, 'search_results')
        
        return suggestions[:limit]
    
    def _generate_suggestions(self, query: str) -> List[str]:
        """
        Generate search suggestions
        """
        # Simple implementation - in production you'd use more sophisticated methods
        suggestions = []
        
        # Add common search terms
        common_terms = [
            'users', 'clients', 'scenarios', 'reports', 'analytics',
            'support tickets', 'admin audit', 'performance', 'monitoring'
        ]
        
        query_lower = query.lower()
        for term in common_terms:
            if query_lower in term:
                suggestions.append(term)
        
        return suggestions


class AdvancedFilterService:
    """
    Advanced filtering service for admin interface
    """
    
    def __init__(self):
        self.filter_cache_timeout = 300  # 5 minutes
    
    def get_filter_options(self, model_name: str) -> Dict:
        """
        Get available filter options for a model
        """
        cache_key = f"filter_options:{model_name}"
        options = CacheService.get(cache_key)
        
        if options is None:
            options = self._generate_filter_options(model_name)
            CacheService.set(cache_key, options, 'search_results')
        
        return options
    
    def _generate_filter_options(self, model_name: str) -> Dict:
        """
        Generate filter options for a model
        """
        from ..models import CustomUser, Client, Scenario, SupportTicket
        
        model_configs = {
            'users': {
                'model': CustomUser,
                'filters': {
                    'role': {
                        'type': 'choice',
                        'label': 'Role',
                        'choices': [
                            ('admin', 'Admin'),
                            ('advisor', 'Advisor'),
                            ('client', 'Client')
                        ]
                    },
                    'is_active': {
                        'type': 'boolean',
                        'label': 'Active Status'
                    },
                    'date_joined': {
                        'type': 'date_range',
                        'label': 'Registration Date'
                    },
                    'last_login': {
                        'type': 'date_range',
                        'label': 'Last Login'
                    }
                }
            },
            'clients': {
                'model': Client,
                'filters': {
                    'advisor': {
                        'type': 'model_choice',
                        'label': 'Advisor',
                        'model': 'CustomUser',
                        'filter_kwargs': {'is_staff': True}
                    },
                    'created_at': {
                        'type': 'date_range',
                        'label': 'Created Date'
                    }
                }
            },
            'scenarios': {
                'model': Scenario,
                'filters': {
                    'client': {
                        'type': 'model_choice',
                        'label': 'Client',
                        'model': 'Client'
                    },
                    'retirement_age': {
                        'type': 'number_range',
                        'label': 'Retirement Age'
                    },
                    'created_at': {
                        'type': 'date_range',
                        'label': 'Created Date'
                    }
                }
            },
            'tickets': {
                'model': SupportTicket,
                'filters': {
                    'status': {
                        'type': 'choice',
                        'label': 'Status',
                        'choices': [
                            ('open', 'Open'),
                            ('in_progress', 'In Progress'),
                            ('resolved', 'Resolved'),
                            ('closed', 'Closed')
                        ]
                    },
                    'priority': {
                        'type': 'choice',
                        'label': 'Priority',
                        'choices': [
                            ('low', 'Low'),
                            ('medium', 'Medium'),
                            ('high', 'High'),
                            ('urgent', 'Urgent')
                        ]
                    },
                    'category': {
                        'type': 'choice',
                        'label': 'Category',
                        'choices': [
                            ('technical', 'Technical'),
                            ('billing', 'Billing'),
                            ('feature_request', 'Feature Request'),
                            ('other', 'Other')
                        ]
                    },
                    'created_at': {
                        'type': 'date_range',
                        'label': 'Created Date'
                    }
                }
            }
        }
        
        if model_name not in model_configs:
            return {}
        
        config = model_configs[model_name]
        filter_options = {}
        
        for filter_key, filter_config in config['filters'].items():
            filter_options[filter_key] = self._build_filter_option(filter_config)
        
        return filter_options
    
    def _build_filter_option(self, config: Dict) -> Dict:
        """
        Build individual filter option
        """
        option = {
            'type': config['type'],
            'label': config['label']
        }
        
        if config['type'] == 'choice':
            option['choices'] = config['choices']
        
        elif config['type'] == 'model_choice':
            # Load model choices
            from django.apps import apps
            model = apps.get_model('core', config['model'])
            
            queryset = model.objects.all()
            if 'filter_kwargs' in config:
                queryset = queryset.filter(**config['filter_kwargs'])
            
            option['choices'] = [
                (str(obj.id), str(obj))
                for obj in queryset.order_by('id')[:100]
            ]
        
        elif config['type'] in ['date_range', 'number_range']:
            option['widget'] = 'range'
        
        elif config['type'] == 'boolean':
            option['choices'] = [
                (True, 'Yes'),
                (False, 'No')
            ]
        
        return option
    
    def apply_filters(self, queryset: QuerySet, filters: Dict) -> QuerySet:
        """
        Apply filters to a queryset
        """
        for filter_key, filter_value in filters.items():
            if not filter_value:
                continue
            
            if isinstance(filter_value, dict):
                # Range filters
                if 'min' in filter_value and filter_value['min']:
                    queryset = queryset.filter(**{f"{filter_key}__gte": filter_value['min']})
                
                if 'max' in filter_value and filter_value['max']:
                    queryset = queryset.filter(**{f"{filter_key}__lte": filter_value['max']})
            
            elif isinstance(filter_value, list):
                # Multiple choice filters
                queryset = queryset.filter(**{f"{filter_key}__in": filter_value})
            
            else:
                # Single value filters
                queryset = queryset.filter(**{filter_key: filter_value})
        
        return queryset
    
    def get_saved_filters(self, user_id: int, model_name: str) -> List[Dict]:
        """
        Get saved filter presets for a user
        """
        cache_key = f"saved_filters:{user_id}:{model_name}"
        return CacheService.get(cache_key, [])
    
    def save_filter_preset(self, user_id: int, model_name: str, name: str, filters: Dict) -> bool:
        """
        Save a filter preset
        """
        try:
            cache_key = f"saved_filters:{user_id}:{model_name}"
            saved_filters = CacheService.get(cache_key, [])
            
            # Remove existing preset with same name
            saved_filters = [f for f in saved_filters if f['name'] != name]
            
            # Add new preset
            saved_filters.append({
                'name': name,
                'filters': filters,
                'created_at': timezone.now().isoformat()
            })
            
            # Keep only last 10 presets
            saved_filters = saved_filters[-10:]
            
            CacheService.set(cache_key, saved_filters, 'search_results')
            return True
            
        except Exception as e:
            logger.error(f"Failed to save filter preset: {e}")
            return False


# Global service instances
search_service = GlobalSearchService()
filter_service = AdvancedFilterService()