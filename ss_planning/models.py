"""
Social Security Planning Models

This module provides models for Social Security claiming strategy analysis,
separate from the core Scenario model. It allows users to save multiple
strategies and compare them without modifying core data.
"""

from django.db import models
from django.utils import timezone
from core.models import Scenario


class SSStrategy(models.Model):
    """
    Represents a saved Social Security claiming strategy for comparison.

    Multiple strategies can exist for a single scenario, allowing users to
    compare different claiming age combinations and their impacts.
    """
    scenario = models.ForeignKey(
        Scenario,
        on_delete=models.CASCADE,
        related_name='ss_strategies',
        help_text="Parent scenario for this strategy"
    )

    # Strategy identification
    name = models.CharField(
        max_length=100,
        help_text="User-defined name (e.g., 'Conservative', 'Max Survivor')"
    )
    is_active = models.BooleanField(
        default=False,
        help_text="Whether this is the currently applied strategy"
    )

    # Claiming ages
    primary_claiming_age = models.FloatField(
        help_text="Primary client's claiming age (62-70)"
    )
    spouse_claiming_age = models.FloatField(
        null=True,
        blank=True,
        help_text="Spouse's claiming age (62-70)"
    )

    # Optimization goal
    OPTIMIZATION_GOALS = [
        ('maximize_lifetime', 'Maximize Lifetime Benefits'),
        ('maximize_liquidity', 'Preserve Asset Liquidity'),
        ('maximize_survivor', 'Maximize Survivor Benefits'),
        ('minimize_taxes', 'Minimize Tax Burden')
    ]
    optimization_goal = models.CharField(
        max_length=50,
        choices=OPTIMIZATION_GOALS,
        default='maximize_lifetime'
    )

    # Health status inputs
    HEALTH_CHOICES = [
        ('poor', 'Poor'),
        ('fair', 'Fair'),
        ('good', 'Good'),
        ('excellent', 'Excellent')
    ]
    health_status_primary = models.CharField(
        max_length=20,
        choices=HEALTH_CHOICES,
        default='good'
    )
    health_status_spouse = models.CharField(
        max_length=20,
        choices=HEALTH_CHOICES,
        default='good',
        null=True,
        blank=True
    )

    # Life expectancy inputs
    life_expectancy_primary = models.IntegerField(
        help_text="Expected age at death for primary client"
    )
    life_expectancy_spouse = models.IntegerField(
        null=True,
        blank=True,
        help_text="Expected age at death for spouse"
    )

    # Earned income (for earnings test)
    earned_income_primary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Annual earned income if claiming before FRA"
    )
    earned_income_spouse = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        null=True,
        blank=True
    )

    # WEP/GPO indicators
    wep_applies = models.BooleanField(
        default=False,
        help_text="Windfall Elimination Provision applies"
    )
    gpo_applies = models.BooleanField(
        default=False,
        help_text="Government Pension Offset applies"
    )
    pension_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        null=True,
        blank=True,
        help_text="Monthly government pension amount"
    )

    # Calculated results (cached for quick comparison)
    lifetime_benefits_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total lifetime benefits for both spouses"
    )
    lifetime_benefits_primary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    lifetime_benefits_spouse = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    total_taxes = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total taxes paid on SS benefits over lifetime"
    )
    total_irmaa = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total IRMAA surcharges over lifetime"
    )
    net_lifetime_benefits = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Lifetime benefits minus taxes and IRMAA"
    )

    # Comparison metrics
    optimal_rank = models.IntegerField(
        null=True,
        blank=True,
        help_text="Rank among all possible strategies (1 = best)"
    )
    percentage_of_maximum = models.FloatField(
        null=True,
        blank=True,
        help_text="Percentage of maximum possible lifetime benefits"
    )

    # Notes
    notes = models.TextField(
        blank=True,
        help_text="User notes about this strategy"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    calculated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When calculations were last run"
    )

    class Meta:
        verbose_name = "SS Strategy"
        verbose_name_plural = "SS Strategies"
        ordering = ['-is_active', '-created_at']
        indexes = [
            models.Index(fields=['scenario', 'is_active']),
            models.Index(fields=['scenario', 'created_at']),
        ]

    def __str__(self):
        return f"{self.name} - {self.scenario.client.first_name} (Primary: {self.primary_claiming_age})"

    def save(self, *args, **kwargs):
        """
        If this strategy is set as active, deactivate all others for the same scenario.
        """
        if self.is_active:
            SSStrategy.objects.filter(
                scenario=self.scenario,
                is_active=True
            ).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class SSCalculationCache(models.Model):
    """
    Caches Social Security calculation results for quick retrieval.

    This avoids re-running expensive scenario_processor calculations
    when the user is just exploring different claiming ages.
    """
    scenario = models.ForeignKey(
        Scenario,
        on_delete=models.CASCADE,
        related_name='ss_calculation_cache'
    )

    # Input parameters (cache key)
    primary_claiming_age = models.FloatField()
    spouse_claiming_age = models.FloatField(null=True, blank=True)
    life_expectancy_primary = models.IntegerField()
    life_expectancy_spouse = models.IntegerField(null=True, blank=True)

    # Cached results (JSON)
    calculation_results = models.JSONField(
        help_text="Full year-by-year calculation results"
    )
    summary_results = models.JSONField(
        help_text="Summary metrics (lifetime benefits, taxes, etc.)"
    )

    # Cache metadata
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        help_text="When this cache entry expires (24 hours)"
    )

    class Meta:
        verbose_name = "SS Calculation Cache"
        verbose_name_plural = "SS Calculation Caches"
        indexes = [
            models.Index(fields=['scenario', 'primary_claiming_age', 'spouse_claiming_age']),
            models.Index(fields=['expires_at']),
        ]
        # Ensure unique cache entries
        unique_together = [
            ['scenario', 'primary_claiming_age', 'spouse_claiming_age',
             'life_expectancy_primary', 'life_expectancy_spouse']
        ]

    def __str__(self):
        return f"Cache: {self.scenario.name} @ {self.primary_claiming_age}/{self.spouse_claiming_age}"

    def is_expired(self):
        """Check if this cache entry has expired."""
        return timezone.now() > self.expires_at

    @classmethod
    def cleanup_expired(cls):
        """Delete all expired cache entries."""
        expired = cls.objects.filter(expires_at__lt=timezone.now())
        count = expired.count()
        expired.delete()
        return count
