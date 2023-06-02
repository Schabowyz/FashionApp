# Generated by Django 4.2.1 on 2023-06-02 18:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0002_item_visibility_price'),
        ('user', '0005_order'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderedItems',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('price_piece', models.FloatField()),
                ('item_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='items.item')),
                ('order_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.order')),
            ],
        ),
    ]