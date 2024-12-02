from model_mommy.recipe import Recipe
from staff.models import Staff


staff = Recipe(
    Staff,
    mbo_site_id=29730,
    mbo_staff_id=100000075,
    first_name='Faran',
    last_name='Cooper',
    name='Faran',
    is_male=False,
    email='farancooper@hotmail.com',
    mobile_phone='07549940654',
)

