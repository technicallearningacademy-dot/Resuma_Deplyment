# Fixed migration: assigns individual UUIDs to existing rows before adding UNIQUE constraint
import uuid
from django.db import migrations, models


def populate_share_tokens(apps, schema_editor):
    """Give each existing resume its own unique UUID."""
    Resume = apps.get_model('resumes', 'Resume')
    for resume in Resume.objects.all():
        resume.share_token = uuid.uuid4()
        resume.save(update_fields=['share_token'])


class Migration(migrations.Migration):

    dependencies = [
        ("resumes", "0002_initial"),
    ]

    operations = [
        # 1. Add is_public (simple boolean, no uniqueness issue)
        migrations.AddField(
            model_name="resume",
            name="is_public",
            field=models.BooleanField(
                default=True,
                help_text="Allow anyone with the link to view and download this resume",
            ),
        ),
        # 2. Add share_token WITHOUT unique constraint first (so all rows can get same default)
        migrations.AddField(
            model_name="resume",
            name="share_token",
            field=models.UUIDField(
                default=uuid.uuid4,
                editable=False,
                help_text="Unique token for the public share link",
                unique=False,  # Not unique yet
            ),
        ),
        # 3. Populate each row with its own unique UUID
        migrations.RunPython(populate_share_tokens, migrations.RunPython.noop),
        # 4. Now add the UNIQUE constraint
        migrations.AlterField(
            model_name="resume",
            name="share_token",
            field=models.UUIDField(
                default=uuid.uuid4,
                editable=False,
                help_text="Unique token for the public share link",
                unique=True,
            ),
        ),
    ]
