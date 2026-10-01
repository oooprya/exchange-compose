from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wholesale', '0003_remove_wholesaleorder_old_currency_and_more'),
    ]

    operations = [

        # --- Shift.morning_balances ---
        migrations.RunSQL(
            sql="""
                ALTER TABLE wholesale_shift
                ADD COLUMN IF NOT EXISTS morning_balances jsonb NULL;
            """,
            reverse_sql="""
                ALTER TABLE wholesale_shift
                DROP COLUMN IF EXISTS morning_balances;
            """
        ),

        # --- WholesaleOrder.base_currency ---
        migrations.RunSQL(
            sql="""
                ALTER TABLE wholesale_wholesaleorder
                ADD COLUMN IF NOT EXISTS base_currency_id integer NULL;
            """,
            reverse_sql="""
                ALTER TABLE wholesale_wholesaleorder
                DROP COLUMN IF EXISTS base_currency_id;
            """
        ),

        # FK (если вдруг не создалась)
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1
                        FROM information_schema.table_constraints
                        WHERE constraint_name = 'wholesale_wholesaleorder_base_currency_id_fk'
                    ) THEN
                        ALTER TABLE wholesale_wholesaleorder
                        ADD CONSTRAINT wholesale_wholesaleorder_base_currency_id_fk
                        FOREIGN KEY (base_currency_id)
                        REFERENCES currency_currency(id)
                        DEFERRABLE INITIALLY DEFERRED;
                    END IF;
                END$$;
            """,
            reverse_sql="""
                ALTER TABLE wholesale_wholesaleorder
                DROP CONSTRAINT IF EXISTS wholesale_wholesaleorder_base_currency_id_fk;
            """
        ),

        # --- is_reversed ---
        migrations.RunSQL(
            sql="""
                ALTER TABLE wholesale_wholesaleorder
                ADD COLUMN IF NOT EXISTS is_reversed boolean DEFAULT false;
            """,
            reverse_sql="""
                ALTER TABLE wholesale_wholesaleorder
                DROP COLUMN IF EXISTS is_reversed;
            """
        ),

        # --- profit ---
        migrations.RunSQL(
            sql="""
                ALTER TABLE wholesale_wholesaleorder
                ADD COLUMN IF NOT EXISTS profit numeric(18,2) DEFAULT 0;
            """,
            reverse_sql="""
                ALTER TABLE wholesale_wholesaleorder
                DROP COLUMN IF EXISTS profit;
            """
        ),
    ]
