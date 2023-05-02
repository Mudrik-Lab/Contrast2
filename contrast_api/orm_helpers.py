from django.db.models import Subquery, PositiveIntegerField, Func
from django.forms import IntegerField


class SubqueryCount(Subquery):
    template = "(SELECT count(*) FROM (%(subquery)s) _count)"
    output_field = PositiveIntegerField()

class SubquerySumValue(Subquery):
    template = """(SELECT sum((elem ->> 'value')::int)
                    FROM (
                      SELECT json_array_elements(%(subquery)s) AS elem
                    ) sub)
                """
    output_field = PositiveIntegerField()


class JSONSum(Func):
    # Currently doesn't work, until we figure out JSONB support on heroku
    function = 'SUM'
    template = "(SELECT COALESCE(SUM((elem ->> %(field_name)s)::int), 0) FROM json_array_elements(%(expressions)s) AS elem)"
    output_field = PositiveIntegerField()

    def __init__(self, expression, field_name='value', **extra):
        super().__init__(
            expression,
            field_name=field_name,
            **extra
        )