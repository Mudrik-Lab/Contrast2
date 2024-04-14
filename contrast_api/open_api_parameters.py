from drf_spectacular.utils import OpenApiParameter

is_csv = OpenApiParameter(
    name="is_csv", description="get a list of relevant experiments/studies as csv file", type=bool, default=False
)
