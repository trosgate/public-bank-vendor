# Generated by Django 4.1.3 on 2023-02-20 11:04

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import onboarding.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('general_settings', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('justification', models.CharField(choices=[('low_score', 'Low Score'), ('shortlist_satisfied', 'Shortlist already satisfied in order of Score'), ('misconduct', 'Applicant Misconduct prior or after application'), ('misrepresentation', 'Applicant misrepresentation of identity'), ('badhistory', 'Recent finding about vendor against our policies')], max_length=60, verbose_name='Justification (**if Rejected)')),
                ('is_marked', models.BooleanField(default=False)),
                ('visibility', models.BooleanField(default=True)),
                ('applicant', models.CharField(max_length=100, verbose_name='Applicant Fullname')),
                ('email', models.EmailField(max_length=100, unique=True, verbose_name='Business/Support Email')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Company Short Name')),
                ('reference', models.CharField(blank=True, max_length=100, null=True, verbose_name='Reference')),
                ('registered_name', models.CharField(max_length=150, verbose_name='Company Registered Name')),
                ('max_member_per_team', models.PositiveIntegerField(default=1, help_text='The expected team size that will better manage our products or services.', verbose_name='Current Team Size')),
                ('counter', models.PositiveIntegerField(default=0, verbose_name='Count')),
                ('instation', models.PositiveIntegerField(choices=[(1, '1 Hour'), (2, '2 Hours'), (3, '3 Hours'), (4, '4 Hours'), (5, '5 Hours'), (6, '6 Hours'), (7, '7 Hours'), (8, '8 Hours'), (9, '9 Hours'), (10, '10 Hours')], help_text='This will consider working hours agreed by both parties', verbose_name='Response Within Accra')),
                ('outstation', models.PositiveIntegerField(choices=[(1, '1 Hour'), (2, '2 Hours'), (3, '3 Hours'), (4, '4 Hours'), (5, '5 Hours'), (6, '6 Hours'), (7, '7 Hours'), (8, '8 Hours'), (9, '9 Hours'), (10, '10 Hours')], help_text='This will consider working hours agreed by both parties', verbose_name='Response Outside Accra')),
                ('regional_availability', models.BooleanField(choices=[(False, 'Only available in Greater Accra'), (True, 'Available in any Region and/ or country')], help_text='How available are your Team to work accross regions/countries.', verbose_name='Regional Availability')),
                ('working_hours', models.BooleanField(choices=[(True, 'Available for 8am-5pm or 24/7 support'), (False, 'Available for 8am-5pm support only')], help_text='This may depend on the kind of service', verbose_name='Working Hours')),
                ('proposal_attachment', models.FileField(help_text="File must be any of these 'doc', 'docx', 'pdf'", upload_to=onboarding.models.applications_path, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['DOC', 'DOCX', 'PDF'])], verbose_name='1. Attachment (Proposal)')),
                ('company_attachment_1', models.FileField(help_text="File must be any of these 'doc', 'docx', 'pdf'", upload_to=onboarding.models.applications_path, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['DOC', 'DOCX', 'PDF'])], verbose_name='2. Form A Attachment')),
                ('company_attachment_2', models.FileField(help_text="File must be any of these 'doc', 'docx', 'pdf'", upload_to=onboarding.models.applications_path, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['DOC', 'DOCX', 'PDF'])], verbose_name='3. Form C Attachment')),
                ('company_attachment_3', models.FileField(blank=True, help_text="File must be any of these 'doc', 'docx', 'pdf'", null=True, upload_to=onboarding.models.applications_path, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['DOC', 'DOCX', 'PDF'])], verbose_name='3. Other Attachment')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='Date Created')),
                ('status', models.CharField(choices=[('notgraded', 'Not Graded'), ('incomplete', 'Incomplete'), ('reviewed', 'Reviewed'), ('graded', 'Graded'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='notgraded', max_length=20, verbose_name='Status')),
                ('reason', models.TextField(blank=True, max_length=400, null=True, verbose_name='Reason')),
                ('reviewed_at', models.DateTimeField(blank=True, null=True, verbose_name='Date Reviewed')),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='applicationapprover', to=settings.AUTH_USER_MODEL, verbose_name='Approved Officer')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='general_settings.category', verbose_name='Support Category')),
            ],
            options={
                'verbose_name': 'Application',
                'verbose_name_plural': 'Application',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='Contacts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='Company or Receiver name')),
                ('email', models.EmailField(max_length=100, verbose_name='Email')),
                ('phone', models.CharField(blank=True, max_length=15, null=True, verbose_name='Phone Number')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='mycontacts', to=settings.AUTH_USER_MODEL, verbose_name='Creator')),
            ],
            options={
                'verbose_name': 'Contact List',
                'verbose_name_plural': 'Contact List',
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='ActiveVendor',
            fields=[
            ],
            options={
                'verbose_name': 'Active Vendor',
                'verbose_name_plural': 'Active Vendor',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('general_settings.vendorcompany',),
        ),
        migrations.CreateModel(
            name='Composer',
            fields=[
            ],
            options={
                'verbose_name': 'Application Instruction',
                'verbose_name_plural': 'Application Instruction',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('general_settings.websitesetting',),
        ),
        migrations.CreateModel(
            name='Tender',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='This title will be the heading on invite mail and application form', max_length=150, verbose_name='Title')),
                ('slug', models.SlugField(max_length=150, verbose_name='Slug')),
                ('number_of_links', models.PositiveIntegerField(help_text='Please specify number of invite links to generate for this Tender', verbose_name='Number of Links')),
                ('duration', models.DateTimeField(help_text='Deadline for expiration of application link', verbose_name='Expiration of Link')),
                ('mode', models.CharField(choices=[('general', 'General Onboarding'), ('category', 'Category-Based Onboarding')], default='general', max_length=30, verbose_name='Onboarding Mode')),
                ('reference', models.CharField(max_length=15, verbose_name='Reference')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='Last Modified')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='general_settings.category', verbose_name='Support Category')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tendercreator', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Onboarding Group',
                'verbose_name_plural': 'Onboarding Group',
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='Parameters',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Parameter Name')),
                ('preview', models.TextField(help_text='What information does this parameter seek to find from vendors. This will guide but not restrict Panelists.', max_length=350, verbose_name='Guiding Note')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='paramcreator', to=settings.AUTH_USER_MODEL, verbose_name='Creator')),
            ],
            options={
                'verbose_name': 'Appraisal Parameter',
                'verbose_name_plural': 'Appraisal Parameters',
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='Panelist',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('reference', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('mode', models.CharField(choices=[('internal', 'Login Access'), ('external', 'Token Access')], default='internal', max_length=20, verbose_name='Access Type')),
                ('access', models.CharField(choices=[('locked', 'Locked'), ('unlocked', 'Unlocked')], default='locked', max_length=10, verbose_name='Access Status')),
                ('status', models.CharField(choices=[('invited', 'Invited'), ('accepted', 'Applied'), ('graded', 'Graded')], default='invited', max_length=20, verbose_name='Status')),
                ('name', models.CharField(blank=True, max_length=100, null=True, verbose_name='External Panelist Name')),
                ('email', models.EmailField(blank=True, max_length=100, null=True, verbose_name='External Panelist Email')),
                ('token', models.CharField(max_length=100, verbose_name='Access Token')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='applicapanelists', to='onboarding.application')),
                ('panelist', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='parampanelist', to=settings.AUTH_USER_MODEL, verbose_name='Panelist A')),
            ],
            options={
                'verbose_name': 'Panelist',
                'verbose_name_plural': 'Panelist',
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('reference', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('access', models.CharField(choices=[('locked', 'Locked'), ('unlocked', 'Unlocked')], default='locked', max_length=10, verbose_name='Access Status')),
                ('status', models.CharField(choices=[('invited', 'Invited'), ('applied', 'Applied'), ('expired', 'Expired')], default='invited', max_length=20, verbose_name='Status')),
                ('token', models.CharField(max_length=100, unique=True, verbose_name='Access Token')),
                ('sent_on', models.DateTimeField(auto_now_add=True, verbose_name='Date')),
                ('created_by', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, related_name='sender', to=settings.AUTH_USER_MODEL, verbose_name='Sender')),
                ('receiver', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, related_name='receiver', to='onboarding.contacts', verbose_name='Receiver')),
                ('tender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invitations', to='onboarding.tender', verbose_name='Tender')),
            ],
            options={
                'ordering': ('-id',),
            },
        ),
        migrations.CreateModel(
            name='Grading',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criteria1', models.CharField(max_length=100, verbose_name='Criteria 1')),
                ('marks1', models.PositiveIntegerField(choices=[(0, '0 Mark'), (1, '1 Mark'), (2, '2 Marks'), (3, '3 Marks'), (4, '4 Marks'), (5, '5 Marks')], validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)], verbose_name='Marks 1')),
                ('criteria2', models.CharField(max_length=100, verbose_name='Criteria 2')),
                ('marks2', models.PositiveIntegerField(choices=[(0, '0 Mark'), (1, '1 Mark'), (2, '2 Marks'), (3, '3 Marks'), (4, '4 Marks'), (5, '5 Marks')], validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)], verbose_name='Marks 2')),
                ('criteria3', models.CharField(max_length=100, verbose_name='Criteria 3')),
                ('marks3', models.PositiveIntegerField(choices=[(0, '0 Mark'), (1, '1 Mark'), (2, '2 Marks'), (3, '3 Marks'), (4, '4 Marks'), (5, '5 Marks')], validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)], verbose_name='Marks 3')),
                ('criteria4', models.CharField(max_length=100, verbose_name='Criteria 4')),
                ('marks4', models.PositiveIntegerField(choices=[(0, '0 Mark'), (1, '1 Mark'), (2, '2 Marks'), (3, '3 Marks'), (4, '4 Marks'), (5, '5 Marks')], validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)], verbose_name='Marks 4')),
                ('criteria5', models.CharField(max_length=100, verbose_name='Criteria 5')),
                ('marks5', models.PositiveIntegerField(choices=[(0, '0 Mark'), (1, '1 Mark'), (2, '2 Marks'), (3, '3 Marks'), (4, '4 Marks'), (5, '5 Marks')], validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)], verbose_name='Marks 5')),
                ('criteria6', models.CharField(blank=True, max_length=100, null=True, verbose_name='Criteria 6')),
                ('marks6', models.PositiveIntegerField(choices=[(0, '0 Mark'), (1, '1 Mark'), (2, '2 Marks'), (3, '3 Marks'), (4, '4 Marks'), (5, '5 Marks')], default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)], verbose_name='Marks 6')),
                ('criteria7', models.CharField(blank=True, max_length=100, null=True, verbose_name='Criteria 7')),
                ('marks7', models.PositiveIntegerField(choices=[(0, '0 Mark'), (1, '1 Mark'), (2, '2 Marks'), (3, '3 Marks'), (4, '4 Marks'), (5, '5 Marks')], default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)], verbose_name='Marks 7')),
                ('criteria8', models.CharField(blank=True, max_length=100, null=True, verbose_name='Criteria 8')),
                ('marks8', models.PositiveIntegerField(choices=[(0, '0 Mark'), (1, '1 Mark'), (2, '2 Marks'), (3, '3 Marks'), (4, '4 Marks'), (5, '5 Marks')], default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)], verbose_name='Marks 8')),
                ('criteria9', models.CharField(blank=True, max_length=100, null=True, verbose_name='Criteria 9')),
                ('marks9', models.PositiveIntegerField(choices=[(0, '0 Mark'), (1, '1 Mark'), (2, '2 Marks'), (3, '3 Marks'), (4, '4 Marks'), (5, '5 Marks')], default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)], verbose_name='Marks 9')),
                ('criteria10', models.CharField(blank=True, max_length=100, null=True, verbose_name='Criteria 10')),
                ('marks10', models.PositiveIntegerField(choices=[(0, '0 Mark'), (1, '1 Mark'), (2, '2 Marks'), (3, '3 Marks'), (4, '4 Marks'), (5, '5 Marks')], default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)], verbose_name='Marks 10')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='Date Modified')),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='gradings', to='onboarding.application')),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='gradingofficer', to=settings.AUTH_USER_MODEL)),
                ('panelist', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='gradingpanelist', to='onboarding.panelist')),
            ],
            options={
                'verbose_name': 'Grading',
                'verbose_name_plural': 'Gradings',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='BlacklistedVendor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Company Short Name')),
                ('registered_name', models.CharField(max_length=150, verbose_name='Company Registered Name')),
                ('email', models.EmailField(max_length=100, verbose_name='Business/Support Email')),
                ('reason', models.TextField(blank=True, max_length=255, verbose_name='BlackList Reason')),
                ('ordering', models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='Order Priority')),
                ('status', models.BooleanField(choices=[(False, 'Dissolved'), (True, 'Contracted')], default=False, verbose_name='Status')),
                ('ticket_response', models.PositiveIntegerField(default=15, help_text='Counting from the time ticket was created, how long should we wait (in minutes) before sending reminder? E.x: 15 means -> 15 minutes. This works on condition that ticket was not assigned within every 15 minutes', verbose_name='New Ticket Response (Minutes)')),
                ('instation_arrival', models.PositiveIntegerField(default=2, help_text='SLA Tracking will be invoked when ticket is finally assigned (Goal is to know how long it takes vendor to get to instations in line with SLA).', verbose_name='In station Arrival (Hours)')),
                ('outstation_arrival', models.PositiveIntegerField(default=2, help_text='SLA Tracking will be invoked when ticket is finally assigned (Goal is to know how long it takes vendor to get to outstations in line with SLA).', verbose_name='Out station Arrival (Hours)')),
                ('working_hours', models.BooleanField(choices=[(False, 'Every 24/7'), (True, 'Every 8am - 5pm')], default=True, help_text="The 'Every 24/7' means ticket will be tracked as and when it is opened. The 'Every 8am - 5pm' means tickets will be tracked from 8am-5pm and deffered to another day if ticket was opened beyond working hours", verbose_name='Supporting Hours')),
                ('track_working_time', models.BooleanField(choices=[(False, 'No'), (True, 'Yes')], default=True, help_text="This feature is the default behaviour of the software. 'Yes' means, it is MANDATORY for Staffs to confirm vendor arrival before work starts. The system will take record of time vendor arrived on site to time ticket was successfully closed", verbose_name='Total resolution Hours')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(help_text='Category of service provided', on_delete=django.db.models.deletion.PROTECT, related_name='blacklistcategory', to='general_settings.category', verbose_name='Service Category')),
            ],
            options={
                'verbose_name': 'Blacklisted Vendor',
                'verbose_name_plural': 'Blacklisted Vendors',
                'ordering': ['ordering'],
            },
        ),
        migrations.AddField(
            model_name='application',
            name='invitation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tenderapplication', to='onboarding.invitation'),
        ),
        migrations.AddField(
            model_name='application',
            name='reviewed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='applicationreviewer', to=settings.AUTH_USER_MODEL, verbose_name='Review Officer'),
        ),
        migrations.AddField(
            model_name='application',
            name='support_product',
            field=models.ManyToManyField(to='general_settings.supportproduct', verbose_name='Support Products'),
        ),
    ]
