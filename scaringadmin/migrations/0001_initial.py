# Generated by Django 2.1 on 2019-08-22 15:59

import datetime
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('photo', models.CharField(max_length=255)),
                ('phonenumber', models.CharField(max_length=255)),
                ('address', models.CharField(max_length=255)),
                ('status', models.CharField(blank=True, max_length=10, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='EmailSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('smtp_port', models.CharField(blank=True, max_length=25, null=True)),
                ('smtp_host', models.CharField(blank=True, max_length=25, null=True)),
                ('smtp_email', models.CharField(blank=True, max_length=50, null=True)),
                ('smtp_password', models.CharField(blank=True, max_length=50, null=True)),
                ('isEnabledSmtp', models.CharField(blank=True, max_length=10, null=True)),
                ('isEnabledSmtpSSL', models.CharField(blank=True, max_length=10, null=True)),
                ('admin_email', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='FacebookAccountKitSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fb_app_id', models.CharField(blank=True, max_length=100, null=True)),
                ('fb_secret_id', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MinedData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('image', models.TextField(blank=True, null=True)),
                ('price', models.CharField(blank=True, max_length=100, null=True)),
                ('currency', models.CharField(blank=True, max_length=255, null=True)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('category', models.CharField(blank=True, max_length=255, null=True)),
                ('username', models.CharField(blank=True, max_length=100, null=True)),
                ('phonenumber', models.TextField(blank=True, null=True)),
                ('email', models.CharField(blank=True, max_length=50, null=True)),
                ('time', models.DateTimeField(blank=True, null=True)),
                ('link', models.CharField(blank=True, max_length=255, null=True)),
                ('view_number', models.CharField(blank=True, max_length=255, null=True)),
                ('site', models.CharField(blank=True, max_length=255, null=True)),
                ('image_folder', models.CharField(blank=True, max_length=50, null=True)),
                ('product_id', models.CharField(blank=True, max_length=50, null=True)),
                ('image_name', models.CharField(blank=True, max_length=50, null=True)),
                ('posted_at', models.CharField(blank=True, max_length=100, null=True)),
                ('month', models.CharField(blank=True, max_length=50, null=True)),
                ('site_id', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Proxy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(blank=True, max_length=100, null=True)),
                ('password', models.CharField(blank=True, max_length=255, null=True)),
                ('ip', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RPassword',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=255)),
                ('token', models.CharField(max_length=255)),
                ('date', models.DateTimeField(default=datetime.datetime(2019, 8, 22, 15, 59, 5, 344170))),
            ],
        ),
        migrations.CreateModel(
            name='SiteList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_name', models.CharField(blank=True, max_length=255, null=True)),
                ('site_url', models.CharField(blank=True, max_length=255, null=True)),
                ('scraped_status', models.CharField(blank=True, max_length=50, null=True)),
                ('start_time', models.DateTimeField(blank=True, null=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('directory_name', models.CharField(blank=True, max_length=200, null=True)),
                ('cron_time', models.TimeField(blank=True, null=True)),
                ('cron_status', models.CharField(default='Stop', editable=False, max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='TwilioAccountSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('twilio_account_sid', models.CharField(blank=True, max_length=100, null=True)),
                ('twilio_auth_token', models.CharField(blank=True, max_length=255, null=True)),
                ('twilio_sms_number', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
    ]
