# Generated migration for KajabiWebhookEvent model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0043_add_kajabi_auth_provider'),
    ]

    operations = [
        migrations.CreateModel(
            name='KajabiWebhookEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_id', models.CharField(help_text='Kajabi event ID for idempotency', max_length=255, unique=True)),
                ('event_type', models.CharField(help_text='Type of event (e.g., purchase.created, subscription.canceled)', max_length=100)),
                ('payload', models.JSONField(help_text='Full webhook payload from Kajabi')),
                ('processed', models.BooleanField(default=False, help_text='Whether this event was successfully processed')),
                ('error_message', models.TextField(blank=True, help_text='Error message if processing failed')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('processed_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(blank=True, help_text='User associated with this event (if any)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='kajabi_events', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['-created_at'], name='core_kajabi_created_idx'),
                    models.Index(fields=['event_type', 'processed'], name='core_kajabi_event_processed_idx'),
                    models.Index(fields=['event_id'], name='core_kajabi_event_id_idx'),
                ],
            },
        ),
    ]
