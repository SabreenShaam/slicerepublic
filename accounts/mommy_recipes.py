from model_mommy.recipe import Recipe, foreign_key
from accounts.models import User, MboClient, MboExternalClient, UserExternalStudio
from rest_framework.authtoken.models import Token


# user = Recipe(
#     User,
#     email='155indiran@gmail.com',
#     is_active=True,
#     date_joined=make_utc(datetime(2015, 7, 6, 3, 14, 24)),
# )
#
# mbo_client_home = Recipe(
#     MboClient,
#     user=foreign_key(user),
#     mbo_client_id=123456,
#     mbo_site_id=29730,
# )
#
#
# token = Recipe(
#     Token,
#     key="b8fc2a7ffdc098e3052ac4461e231eccc9760061",
#     user=foreign_key(user),
# )
#
#
# user_other = Recipe(
#     User,
#     email='vinusha88@gmail.com',
#     is_active=True,
#     date_joined=make_utc(datetime(2015, 7, 6, 3, 14, 24)),
# )
#
# mbo_client_other = Recipe(
#     MboClient,
#     user=foreign_key(user_other),
#     mbo_client_id=100015623,
#     mbo_site_id=-99,
# )
from venues.mommy_recipes import  external_studio, studio

user = Recipe(
    User,
    first_name='raj',
    last_name='pira',
    email='rajpira@hotmail.com',
    is_active=True,
    date_joined='2016-06-23 04:30:10',
    mobile_phone='0777123456',
)

# user2 = Recipe(
#     User,
#     first_name='raj',
#     last_name='pira',
#     email='thraka@hotmail.com',
#     is_active=True,
#     date_joined='2016-06-23 04:30:10',
#     mobile_phone='0777123456',
# )

mbo_client = Recipe(
    MboClient,
    user=foreign_key(user),
    mbo_client_id=100015639,
    studio=foreign_key(studio),
)

# mbo_client_home = Recipe(
#     MboClient,
#     user=foreign_key(user),
#     mbo_client_id=100015639,
#     studio=foreign_key(home_studio),
# )
#
# mbo_client_home2 = Recipe(
#     MboClient,
#     user=foreign_key(user2),
#     mbo_client_id=100015639,
#     studio=foreign_key(home_studio),
# )

mbo_client_external = Recipe(
    MboClient,
    user=foreign_key(user),
    mbo_client_id=100015637,
    studio=foreign_key(external_studio),
)


token = Recipe(
    Token,
    key="40b8efb72a71d6a565682b76086475cb58ca17d5",
    user=foreign_key(user),
)


# token2 = Recipe(
#     Token,
#     key="40b8efb72a71d6a565682b76086475cb58ca17d4",
#     user=foreign_key(user2),
# )

mbo_external_client = Recipe(
    MboExternalClient,
    user=foreign_key(user),
    mbo_client_id=1,
    email='abc@gmail.com',
)


user_external_studio = Recipe(
    UserExternalStudio,
    user=foreign_key(user),
    studio=foreign_key(external_studio),
)


# mbo_external_client2 = Recipe(
#     MboExternalClient,
#     user=foreign_key(user2),
#     mbo_client_id=1,
#     email='abc2@gmail.com',
# )


# user_external_studio2 = Recipe(
#     UserExternalStudio,
#     user=foreign_key(user2),
#     studio=foreign_key(external_studio),
# )