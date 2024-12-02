from datetime import datetime
from model_mommy.recipe import Recipe, foreign_key
from accounts.mommy_recipes import mbo_client
from classes.mommy_recipes import program
from services.models import MboClientService, StudioService, MboService, ClientCreditCardInfo, PassportStudioAccess
from slicerepublic.dateutil import make_utc
from venues.mommy_recipes import studio, external_studio

mbo_client_service = Recipe(
    MboClientService,
    name='Intro',
    mbo_client=foreign_key(mbo_client),
    mbo_client_service_id=100246936,
    current=True,
    count=5,
    remaining=5,
    payment_date=make_utc(datetime(2016, 6, 10)).date(),
    active_date=make_utc(datetime(2016, 6, 10)).date(),
    expiration_date=make_utc(datetime(2016, 8, 10)).date(),
    program=foreign_key(program),
    last_sync_date='2016-06-24 07:21:04',
    auto_pay=True
)

# mbo_client_service_2 = Recipe(
# 	MboClientService,
# 	name='Passport',
# 	mbo_client=foreign_key(mbo_client),
# 	mbo_client_service_id=100246934,
# 	current=True,
# 	count=5,
# 	remaining=5,
# 	payment_date=make_utc(datetime(2016, 6, 15)).date(),
# 	active_date=make_utc(datetime(2016, 6, 15)).date(),
# 	expiration_date=make_utc(datetime(2016, 7, 15)).date(),
# 	program=foreign_key(program),
# 	last_sync_date='2016-06-24 07:21:04',
# )
#
# mbo_client_service_3 = Recipe(
# 	MboClientService,
# 	name='Intro',
# 	mbo_client=foreign_key(mbo_client),
# 	mbo_client_service_id=100246934,
# 	current=True,
# 	count=5,
# 	remaining=5,
# 	payment_date=make_utc(datetime(2016, 6, 15)).date(),
# 	active_date=make_utc(datetime(2016, 6, 15)).date(),
# 	expiration_date=make_utc(datetime(2016, 7, 15)).date(),
# 	program=foreign_key(program),
# 	last_sync_date='2016-06-24 07:21:04',
# )

studio_service = Recipe(
    StudioService,
    name='Passport',
    mbo_service_id=1300,
    mbo_product_id=1300,
    price=55.0000,
    online_price=55.0000,
    tax_rate=0.000,
    count=5,
    is_active=True,
    studio=foreign_key(studio),
)

# studio_service_2 = Recipe(
# 	StudioService,
# 	name='10 Class Card',
# 	mbo_service_id=500,
# 	mbo_product_id=500,
# 	price=155.0000,
# 	online_price=155.0000,
# 	tax_rate=0.000,
# 	count=5,
# 	is_active=True,
# 	studio=foreign_key(studio),
# )

mbo_service = Recipe(
    MboService,
    name='Intro',
    studio=foreign_key(studio),
    count=3,
    max_per_studio=1,
    over_flow_days=0,
)

# mbo_service_2 = Recipe(
# 	MboService,
# 	name='Passport',
# 	studio=foreign_key(studio),
# 	count=5,
# 	max_per_studio=5,
# 	over_flow_days=4,
# )


client_credit_card_info = Recipe(
    ClientCreditCardInfo,
    mbo_client=foreign_key(mbo_client),
    type='Type',
    last_four='1111',
    exp_month='12',
    exp_year='2018',
    postal_code='00500',
    is_active=True,
)

passport_studio_access = Recipe(PassportStudioAccess,
                                studio=foreign_key(external_studio),
                                mbo_service=mbo_service,
                                )
