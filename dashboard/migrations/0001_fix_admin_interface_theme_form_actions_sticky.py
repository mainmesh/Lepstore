from django.db import migrations


class Migration(migrations.Migration):
    dependencies = []

    operations = [
        migrations.RunSQL(
            sql=(
                "UPDATE admin_interface_theme SET form_actions_sticky = false WHERE form_actions_sticky IS NULL;"
                "ALTER TABLE admin_interface_theme ALTER COLUMN form_actions_sticky SET DEFAULT false;"
                "ALTER TABLE admin_interface_theme ALTER COLUMN form_actions_sticky SET NOT NULL;"
            ),
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
