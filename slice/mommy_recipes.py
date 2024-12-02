from model_mommy.recipe import Recipe
from slice.models import SliceClient

slice_client = Recipe(
    SliceClient,
    mbo_site_id=123,
    mbo_client_id=454,
)