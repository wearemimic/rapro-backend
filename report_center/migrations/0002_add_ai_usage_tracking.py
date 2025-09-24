# Generated manually for AI Usage Tracking
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('report_center', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AIUsageTracking',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('feature', models.CharField(choices=[('executive_summary', 'Executive Summary Generation'), ('slide_recommendations', 'Slide Order Recommendations'), ('content_risk_explanation', 'Risk Explanation Content'), ('content_irmaa_impact', 'IRMAA Impact Content'), ('content_roth_strategy', 'Roth Strategy Content'), ('content_tax_optimization', 'Tax Optimization Content'), ('content_social_security', 'Social Security Content'), ('content_monte_carlo_interpretation', 'Monte Carlo Interpretation'), ('client_insights', 'Client Insights Analysis')], max_length=100)),
                ('tokens_used', models.PositiveIntegerField()),
                ('cost', models.DecimalField(decimal_places=4, help_text='Cost in USD', max_digits=10)),
                ('model_used', models.CharField(default='gpt-4-turbo-preview', max_length=100)),
                ('request_metadata', models.JSONField(blank=True, help_text='Additional context about the request', null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('report', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ai_usage', to='report_center.report')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ai_usage', to='core.customuser')),
            ],
            options={
                'verbose_name': 'AI Usage Record',
                'verbose_name_plural': 'AI Usage Records',
                'db_table': 'report_ai_usage',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.AddIndex(
            model_name='aiusagetracking',
            index=models.Index(fields=['feature'], name='report_ai_u_feature_idx'),
        ),
        migrations.AddIndex(
            model_name='aiusagetracking',
            index=models.Index(fields=['user'], name='report_ai_u_user_idx'),
        ),
        migrations.AddIndex(
            model_name='aiusagetracking',
            index=models.Index(fields=['timestamp'], name='report_ai_u_timesta_idx'),
        ),
        migrations.AddIndex(
            model_name='aiusagetracking',
            index=models.Index(fields=['cost'], name='report_ai_u_cost_idx'),
        ),
    ]