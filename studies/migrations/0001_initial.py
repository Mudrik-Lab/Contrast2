# Generated by Django 4.1.4 on 2023-01-03 18:17

import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("approval_process", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Author",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="ConsciousnessMeasurePhaseType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name="ConsciousnessMeasureType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name="Experiment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("finding_description", models.CharField(max_length=254)),
                (
                    "type_of_consciousness",
                    models.CharField(
                        choices=[("content", "Content"), ("state", "State"), ("both", "Both")], max_length=20
                    ),
                ),
                (
                    "is_reporting",
                    models.CharField(
                        choices=[("report", "Report"), ("no_report", "No_report"), ("both", "Both")], max_length=20
                    ),
                ),
                (
                    "theory_driven",
                    models.CharField(
                        choices=[("driven", "Driven"), ("mentioning", "Mentioning"), ("both", "Both")], max_length=20
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="FindingTagFamily",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name="FindingTagType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name="MeasureType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name="ModalityType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name="TaskType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name="Technique",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Theory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="studies.theory"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Task",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "experiment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="tasks", to="studies.experiment"
                    ),
                ),
                ("type", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="studies.tasktype")),
            ],
        ),
        migrations.CreateModel(
            name="Study",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("DOI", models.CharField(max_length=100, unique=True)),
                ("title", models.TextField()),
                (
                    "year",
                    models.PositiveIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1900),
                            django.core.validators.MaxValueValidator(2100),
                        ]
                    ),
                ),
                ("corresponding_author_email", models.EmailField(max_length=254)),
                (
                    "approval_status",
                    models.IntegerField(choices=[(0, "Pending"), (1, "Approved"), (2, "Rejected")], default=0),
                ),
                (
                    "key_words",
                    django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=50), size=None),
                ),
                ("references", models.TextField(blank=True, null=True)),
                ("funding", models.TextField(blank=True, null=True)),
                ("source_title", models.CharField(blank=True, max_length=200, null=True)),
                ("abbreviated_source_title", models.CharField(blank=True, max_length=200, null=True)),
                ("link", models.URLField()),
                ("publisher", models.CharField(blank=True, max_length=100, null=True)),
                ("abstract", models.TextField(blank=True, null=True)),
                (
                    "countries",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=django_countries.fields.CountryField(max_length=2), size=None
                    ),
                ),
                ("affiliations", models.TextField()),
                (
                    "approval_process",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="approval_process.approvalprocess",
                    ),
                ),
                ("authors", models.ManyToManyField(related_name="studies", to="studies.author")),
            ],
        ),
        migrations.CreateModel(
            name="Stimulus",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("category", models.CharField(max_length=50)),
                ("sub_category", models.CharField(blank=True, max_length=50, null=True)),
                ("description", models.TextField(blank=True, null=True)),
                ("duration", models.PositiveBigIntegerField(blank=True, null=True)),
                (
                    "experiment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="stimuli", to="studies.experiment"
                    ),
                ),
                ("modality", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="studies.modalitytype")),
            ],
        ),
        migrations.CreateModel(
            name="Sample",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("healthy_adults", "Healthy_adults"),
                            ("children", "Children"),
                            ("patients", "Patients"),
                            ("non_human", "Non_human"),
                            ("computer", "Computer"),
                        ],
                        max_length=30,
                    ),
                ),
                ("total_size", models.IntegerField()),
                ("size_included", models.IntegerField()),
                (
                    "experiment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="samples", to="studies.experiment"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Paradigm",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="child_paradigm",
                        to="studies.paradigm",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Measure",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("notes", models.TextField(blank=True, null=True)),
                (
                    "experiment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="measures", to="studies.experiment"
                    ),
                ),
                (
                    "type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="measures", to="studies.measuretype"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Interpretation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "type",
                    models.CharField(
                        choices=[("pro", "Pro"), ("challenges", "Challenges"), ("neutral", "Neutral")], max_length=30
                    ),
                ),
                (
                    "experiment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="theories", to="studies.experiment"
                    ),
                ),
                (
                    "theory",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="experiments", to="studies.theory"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="FindingTag",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("onset", models.PositiveBigIntegerField(blank=True, null=True)),
                ("offset", models.PositiveBigIntegerField(blank=True, null=True)),
                ("band_lower_bound", models.PositiveBigIntegerField(blank=True, null=True)),
                ("band_higher_bound", models.PositiveBigIntegerField(blank=True, null=True)),
                ("AAL_atlas_tag", models.CharField(blank=True, max_length=100, null=True)),
                ("notes", models.TextField(blank=True, null=True)),
                (
                    "analysis_type",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("power", "Power"),
                            ("connectivity", "Connectivity"),
                            ("phi", "Phi"),
                            ("complexity", "Complexity"),
                            ("te", "Te - transfer entropy"),
                            ("pca", "PCA - principal components analysis"),
                            ("lrtc", "LRTC - long-range temporal correlations"),
                            ("microstates", "Microstates"),
                            ("cd", "CD - correlation dimension"),
                            ("clustering", "Clustering"),
                        ],
                        default="power",
                        max_length=100,
                        null=True,
                    ),
                ),
                (
                    "correlation_sign",
                    models.CharField(
                        blank=True,
                        choices=[("negative", "Negative"), ("positive", "Positive")],
                        default="positive",
                        max_length=10,
                        null=True,
                    ),
                ),
                (
                    "experiment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="finding_tags",
                        to="studies.experiment",
                    ),
                ),
                (
                    "family",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="studies.findingtagfamily"),
                ),
                (
                    "technique",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="findings_tags",
                        to="studies.technique",
                    ),
                ),
                ("type", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="studies.findingtagtype")),
            ],
        ),
        migrations.AddField(
            model_name="experiment",
            name="interpretations",
            field=models.ManyToManyField(
                related_name="experiments_interpretations", through="studies.Interpretation", to="studies.theory"
            ),
        ),
        migrations.AddField(
            model_name="experiment",
            name="paradigms",
            field=models.ManyToManyField(related_name="experiments", to="studies.paradigm"),
        ),
        migrations.AddField(
            model_name="experiment",
            name="study",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="experiments", to="studies.study"
            ),
        ),
        migrations.AddField(
            model_name="experiment",
            name="techniques",
            field=models.ManyToManyField(related_name="experiments", to="studies.technique"),
        ),
        migrations.AddField(
            model_name="experiment",
            name="theory_driven_theories",
            field=models.ManyToManyField(related_name="experiments_driven", to="studies.theory"),
        ),
        migrations.CreateModel(
            name="ConsciousnessMeasure",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "experiment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="consciousness_measures",
                        to="studies.experiment",
                    ),
                ),
                (
                    "phase",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="studies.consciousnessmeasurephasetype"
                    ),
                ),
                (
                    "type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="studies.consciousnessmeasuretype"
                    ),
                ),
            ],
        ),
    ]
