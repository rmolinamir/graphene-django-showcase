# Generated by Django 2.1.4 on 2019-11-21 02:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('links', '0003_vote'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vote',
            name='link',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='links.Link'),
        ),
    ]
