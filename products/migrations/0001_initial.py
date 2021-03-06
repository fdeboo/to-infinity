# Generated by Django 3.1.4 on 2020-12-23 15:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=75)),
                ('friendly_name', models.CharField(blank=True, max_length=75, null=True)),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('name', models.CharField(max_length=254)),
                ('product_id', models.CharField(max_length=254, primary_key=True, serialize=False)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('image', models.ImageField(blank=True, null=True, upload_to='')),
                ('image_thumb', models.ImageField(blank=True, null=True, upload_to='')),
                ('image_url', models.URLField(blank=True, max_length=1024, null=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.category')),
            ],
        ),
        migrations.CreateModel(
            name='AddOn',
            fields=[
                ('product_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='products.product')),
                ('min_medical_threshold', models.IntegerField(default=0)),
            ],
            bases=('products.product',),
        ),
        migrations.CreateModel(
            name='Insurance',
            fields=[
                ('product_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='products.product')),
                ('friendly_name', models.CharField(blank=True, max_length=75)),
            ],
            bases=('products.product',),
        ),
        migrations.CreateModel(
            name='Destination',
            fields=[
                ('product_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='products.product')),
                ('max_passengers', models.IntegerField(blank=True, null=True)),
                ('duration', models.CharField(blank=True, max_length=20)),
                ('min_medical_threshold', models.IntegerField(default=0)),
                ('addons', models.ManyToManyField(to='products.AddOn')),
            ],
            bases=('products.product',),
        ),
    ]
