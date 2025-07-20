from django.db import migrations, models

def count_exploratory_bringer(apps, schema_editor):
    GamePlayer = apps.get_model('pbf', 'GamePlayer')
    Card = apps.get_model('pbf', 'Card')

    players = GamePlayer.objects.filter(spirit__name='Exploratory Bringer').count()
    cards = Card.objects.filter(spirit__name='Exploratory Bringer').count()
    print(f"{players} players {cards} cards using Exploratory Bringer")

def convert_exploratory_bringer(apps, schema_editor):
    GamePlayer = apps.get_model('pbf', 'GamePlayer')
    Spirit = apps.get_model('pbf', 'Spirit')

    bringer = Spirit.objects.get(name='Bringer')
    players = GamePlayer.objects.filter(spirit__name='Exploratory Bringer')

    players.update(spirit=bringer, aspect='Exploratory')

def delete_exploratory_bringer(apps, schema_editor):
    GamePlayer = apps.get_model('pbf', 'GamePlayer')
    Spirit = apps.get_model('pbf', 'Spirit')

    if GamePlayer.objects.filter(spirit__name='Exploratory Bringer').exists():
        raise Exception("Someone is using Exploratory Bringer")

    try:
        Spirit.objects.get(name='Exploratory Bringer').delete()
    except Spirit.DoesNotExist:
        pass

def add_exploratory_bringer(apps, schema_editor):
    Spirit = apps.get_model('pbf', 'Spirit')
    Spirit(name='Exploratory Bringer').save()

class Migration(migrations.Migration):
    dependencies = [
        ('pbf', '0052_alter_game_screenshot_upload_to_func'),
    ]

    operations = [
            migrations.RunPython(count_exploratory_bringer, migrations.RunPython.noop),
            migrations.RunPython(convert_exploratory_bringer, migrations.RunPython.noop),
            #migrations.RunPython(delete_exploratory_bringer, add_exploratory_bringer),
            migrations.RunPython(delete_exploratory_bringer, migrations.RunPython.noop),
    ]
