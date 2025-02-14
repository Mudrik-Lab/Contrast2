from django.db.models import Q


def get_queryset_to_modify(experiment_model, safe_list, max_id, first_technique, second_technique):
    experiments_to_modify = experiment_model.objects.filter(
        ~Q(id__in=safe_list) & Q(id__lte=max_id) & Q(techniques=first_technique) & Q(techniques=second_technique)
    )

    return experiments_to_modify
