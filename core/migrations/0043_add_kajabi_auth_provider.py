# Generated migration for adding Kajabi auth provider

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0042_add_scenario_archiving'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='auth_provider',
            field=models.CharField(
                choices=[
                    ('password', 'Email/Password'),
                    ('google-oauth2', 'Google'),
                    ('facebook', 'Facebook'),
                    ('apple', 'Apple'),
                    ('linkedin', 'LinkedIn'),
                    ('microsoft', 'Microsoft'),
                    ('kajabi', 'Kajabi'),
                ],
                default='password',
                help_text='Authentication provider used for login',
                max_length=50
            ),
        ),
    ]
