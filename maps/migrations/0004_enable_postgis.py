from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0001_initial'),  # ← Change to your last maps migration!
    ]

    def enable_postgis(apps, schema_editor):
        with schema_editor.connection.cursor() as cursor:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis;")

    operations = [
        migrations.RunPython(enable_postgis, reverse_code=migrations.RunPython.noop),
    ]