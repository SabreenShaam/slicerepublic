from mind_body_online.SiteService import SiteServiceCalls


def get_site(mbo_site_id):
    site_ids = [mbo_site_id]
    site_service_calls = SiteServiceCalls()
    site = site_service_calls.GetSite(siteIDs=site_ids)
    return site


def get_locations(mbo_site_id):
    site_service_calls = SiteServiceCalls()
    mbo_location_result = site_service_calls.GetLocations([mbo_site_id])
    return mbo_location_result


def get_resources(mbo_site_id, page=0):
    site_service_calls = SiteServiceCalls()
    mbo_resources_result = site_service_calls.GetResources(siteIDs=[mbo_site_id], page=page)
    return mbo_resources_result


def get_programs(mbo_site_id):
    site_service_calls = SiteServiceCalls()
    mbo_programs_result = site_service_calls.GetPrograms(siteIDs=[mbo_site_id])
    if mbo_programs_result.ResultCount == 0:
        return
    return mbo_programs_result.Programs.Program
