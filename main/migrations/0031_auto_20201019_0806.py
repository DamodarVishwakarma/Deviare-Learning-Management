# Generated by Django 3.0.2 on 2020-10-19 08:06

from django.db import migrations, models


def forwards_func(apps, schema_editor):
    import pandas as pd
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    TMForumUserResponse = apps.get_model("main", "TMForumUserResponse")
    TMForumUserAssessment = apps.get_model("main", "TMForumUserAssessment")
    db_alias = schema_editor.connection.alias
    qs = TMForumUserResponse.objects.using(db_alias).all()
    resp = pd.DataFrame(list(qs.values()))
    resp.uuid = resp.uuid.apply(str)
    grp = resp.groupby(['owner_id', 'criterion_id'], as_index=False).first()
    keep = '", "'.join(grp.uuid.tolist())
    delete_uuids = list(resp.query(f'uuid not in ["{keep}"]').uuid.tolist())
    TMForumUserResponse.objects.using(db_alias).filter(pk__in=delete_uuids).delete()
    tm_assess_delete = []
    tm_keep = []
    for a in TMForumUserAssessment.objects.using(db_alias).all():
        k = str(a.owner_id)+str(a.sub_dimension_id)
        # print(k)
        if k not in tm_keep:
            tm_keep.append(k)
            a.save()
        else:
            tm_assess_delete.append(str(a.uuid))
    # print(tm_assess_delete)
    TMForumUserAssessment.objects.using(db_alias).filter(pk__in=tm_assess_delete).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0030_auto_20201016_0128'),
    ]

    operations = [
        # migrations.RunPython(forwards_func, ),
        migrations.AlterModelOptions(
            name='tmforumcriterion',
            options={'ordering': ['value']},
        ),
        migrations.AlterModelOptions(
            name='tmforumdimension',
            options={'ordering': ['value']},
        ),
        migrations.AlterModelOptions(
            name='tmforumsubdimension',
            options={'ordering': ['value']},
        ),
        migrations.AddField(
            model_name='tmforumuserassessment',
            name='responses',
            field=models.ManyToManyField(related_name='assigned', to='main.TMForumUserResponse'),
        ),
        migrations.AlterField(
            model_name='tmforumassignedassessment',
            name='assessment',
            field=models.ManyToManyField(related_name='assigned', to='main.TMForumUserAssessment'),
        ),
        # migrations.AlterUniqueTogether(
        #     name='tmforumuserassessment',
        #     unique_together={('owner', 'sub_dimension')},
        # ),
        migrations.AlterUniqueTogether(
            name='tmforumuserresponse',
            unique_together={('owner', 'criterion')},
        ),
    ]
