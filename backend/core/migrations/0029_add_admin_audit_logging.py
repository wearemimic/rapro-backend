# Generated manually for RetirementAdvisorPro Admin Area Implementation

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_add_admin_fields_to_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminAuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_type', models.CharField(choices=[('user_created', 'User Created'), ('user_updated', 'User Updated'), ('user_deleted', 'User Deleted'), ('user_impersonated', 'User Impersonated'), ('admin_role_granted', 'Admin Role Granted'), ('admin_role_revoked', 'Admin Role Revoked'), ('permission_changed', 'Permission Changed'), ('system_setting_changed', 'System Setting Changed'), ('bulk_action_performed', 'Bulk Action Performed'), ('data_exported', 'Data Exported'), ('password_reset', 'Password Reset'), ('account_locked', 'Account Locked'), ('account_unlocked', 'Account Unlocked'), ('login_failed', 'Login Failed'), ('access_denied', 'Access Denied')], max_length=50)),
                ('description', models.TextField(help_text='Human-readable description of the action')),
                ('target_user_email', models.EmailField(blank=True, help_text='Email of target user at time of action', max_length=254)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('session_key', models.CharField(blank=True, max_length=255)),
                ('metadata', models.JSONField(blank=True, default=dict, help_text='Additional context about the action (e.g., what fields changed)')),
                ('previous_state', models.JSONField(blank=True, default=dict, help_text='State before the change')),
                ('new_state', models.JSONField(blank=True, default=dict, help_text='State after the change')),
                ('risk_level', models.CharField(choices=[('low', 'Low Risk'), ('medium', 'Medium Risk'), ('high', 'High Risk'), ('critical', 'Critical Risk')], default='medium', max_length=20)),
                ('requires_approval', models.BooleanField(default=False)),
                ('approval_timestamp', models.DateTimeField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('admin_user', models.ForeignKey(help_text='The admin user who performed this action', on_delete=django.db.models.deletion.CASCADE, related_name='admin_actions_performed', to=settings.AUTH_USER_MODEL)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_admin_actions', to=settings.AUTH_USER_MODEL)),
                ('target_user', models.ForeignKey(blank=True, help_text='The user who was the target of this action', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='admin_actions_received', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'admin_audit_log',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='UserImpersonationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('target_user_email', models.EmailField(help_text='Email of impersonated user at start of session', max_length=254)),
                ('session_key', models.CharField(max_length=255, unique=True)),
                ('start_timestamp', models.DateTimeField(auto_now_add=True)),
                ('end_timestamp', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('ip_address', models.GenericIPAddressField()),
                ('user_agent', models.TextField()),
                ('reason', models.TextField(help_text='Business justification for impersonation')),
                ('actions_performed', models.JSONField(blank=True, default=list, help_text='List of actions performed during impersonation')),
                ('pages_accessed', models.JSONField(blank=True, default=list, help_text='List of pages/endpoints accessed during session')),
                ('risk_score', models.IntegerField(default=50, help_text='Risk score 1-100 based on user privileges and session duration')),
                ('flagged_for_review', models.BooleanField(default=False)),
                ('review_timestamp', models.DateTimeField(blank=True, null=True)),
                ('review_notes', models.TextField(blank=True)),
                ('admin_user', models.ForeignKey(help_text='The admin user performing the impersonation', on_delete=django.db.models.deletion.CASCADE, related_name='impersonation_sessions_started', to=settings.AUTH_USER_MODEL)),
                ('approved_by', models.ForeignKey(blank=True, help_text='Admin who approved this impersonation (if required)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='impersonation_approvals_granted', to=settings.AUTH_USER_MODEL)),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='impersonation_reviews_performed', to=settings.AUTH_USER_MODEL)),
                ('target_user', models.ForeignKey(help_text='The user being impersonated', on_delete=django.db.models.deletion.CASCADE, related_name='impersonation_sessions_received', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_impersonation_log',
                'ordering': ['-start_timestamp'],
            },
        ),
        migrations.AddIndex(
            model_name='adminauditlog',
            index=models.Index(fields=['admin_user', '-timestamp'], name='admin_audit_admin_user_idx'),
        ),
        migrations.AddIndex(
            model_name='adminauditlog',
            index=models.Index(fields=['target_user', '-timestamp'], name='admin_audit_target_user_idx'),
        ),
        migrations.AddIndex(
            model_name='adminauditlog',
            index=models.Index(fields=['action_type', '-timestamp'], name='admin_audit_action_type_idx'),
        ),
        migrations.AddIndex(
            model_name='adminauditlog',
            index=models.Index(fields=['ip_address', '-timestamp'], name='admin_audit_ip_address_idx'),
        ),
        migrations.AddIndex(
            model_name='adminauditlog',
            index=models.Index(fields=['risk_level', '-timestamp'], name='admin_audit_risk_level_idx'),
        ),
        migrations.AddIndex(
            model_name='adminauditlog',
            index=models.Index(fields=['-timestamp'], name='admin_audit_timestamp_idx'),
        ),
        migrations.AddIndex(
            model_name='userimpersonationlog',
            index=models.Index(fields=['admin_user', '-start_timestamp'], name='impersonation_admin_user_idx'),
        ),
        migrations.AddIndex(
            model_name='userimpersonationlog',
            index=models.Index(fields=['target_user', '-start_timestamp'], name='impersonation_target_user_idx'),
        ),
        migrations.AddIndex(
            model_name='userimpersonationlog',
            index=models.Index(fields=['is_active'], name='impersonation_is_active_idx'),
        ),
        migrations.AddIndex(
            model_name='userimpersonationlog',
            index=models.Index(fields=['flagged_for_review'], name='impersonation_flagged_idx'),
        ),
        migrations.AddIndex(
            model_name='userimpersonationlog',
            index=models.Index(fields=['session_key'], name='impersonation_session_key_idx'),
        ),
        migrations.AddIndex(
            model_name='userimpersonationlog',
            index=models.Index(fields=['-start_timestamp'], name='impersonation_timestamp_idx'),
        ),
    ]