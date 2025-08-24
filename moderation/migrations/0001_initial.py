from django.db import migrations, models
import django.conf
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModerationAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('target_type', models.CharField(choices=[('post', 'Post'), ('comment', 'Comment')], db_index=True, max_length=10)),
                ('target_id', models.PositiveIntegerField(db_index=True)),
                ('action', models.CharField(choices=[('approve', 'Approve'), ('reject', 'Reject'), ('hide', 'Hide'), ('unhide', 'Unhide')], db_index=True, max_length=10)),
                ('reason', models.CharField(blank=True, max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('moderator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='moderation_actions', to=django.conf.settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='moderationaction',
            index=models.Index(fields=['target_type', 'target_id'], name='moderation_target_idx'),
        ),
        migrations.AddIndex(
            model_name='moderationaction',
            index=models.Index(fields=['action'], name='moderation_action_idx'),
        ),
        migrations.AddIndex(
            model_name='moderationaction',
            index=models.Index(fields=['created_at'], name='moderation_created_idx'),
        ),
    ]


