# Generated by Django 3.1.7 on 2021-04-11 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coffee', '0003_auto_20210128_0140'),
    ]

    operations = [
        migrations.CreateModel(
            name='Taste',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('flavor', models.ManyToManyField(to='coffee.Flavor')),
            ],
        ),
        migrations.CreateModel(
            name='Origin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('flavor', models.ManyToManyField(related_name='origins', to='coffee.Flavor')),
            ],
        ),
    ]
