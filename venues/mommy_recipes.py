from model_mommy.recipe import Recipe
from accounts.models import UserExternalStudio
from studios.studios_web.models import StudioAccess
from venues.models import Location, Studio


location = Recipe(
    Location,
    name='Slice Studios and Cupcake',
    business_description="London's exercise haven, offering classes \"by the Slice\" in SW6.",
    address_line_1='11 Heathmans Road',
    address_line_2='London, SW6 4TJ',
    city='London',
    postcode='SW6 4TJ',
    phone='02071866007',
    latitude=51.4737606,
    longitude=-0.2026692,
    description="Tucked in West London's Fulham Area."
)


# home_studio = Recipe(
#     Studio,
#     name="Sandbox",
#     mbo_site_id=99,
#     is_active=True,
# )


external_studio = Recipe(
    Studio,
    name="Sandbox",
    mbo_site_id=-99,
    is_active=True,
)

studio = Recipe(
    Studio,
    is_active=True
)


studio_access = Recipe(StudioAccess)