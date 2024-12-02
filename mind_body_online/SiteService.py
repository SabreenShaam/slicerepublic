from mind_body_online import BasicRequestHelper
from suds.client import Client
from datetime import datetime

class SiteServiceCalls():
    """This class contains examples of consumer methods for each SiteService method."""

    """GetActivationCode Methods"""
    def GetActivationCode(self, site_id):
        result = SiteServiceMethods().GetActivationCode(site_id)
        return result

    """GetLocations Methods"""
    def GetLocations(self, siteIDs=None):
        result = SiteServiceMethods().GetLocations(siteIDs)
        return result

    """GetPrograms Methods"""
    def GetPrograms(self, siteIDs=None, scheduleType="All", onlineOnly=False):
        result = SiteServiceMethods().GetPrograms(siteIDs, scheduleType, onlineOnly)
        return result

    """GetRelationships Methods"""
    def GetRelationships(self):
        result = SiteServiceMethods().GetRelationships()
        return result

    """GetResources Methods"""
    def GetResources(self, siteIDs,
                           sessionTypeIds=None,
                           locationId=0,
                           page=0,
                           startDateTime=datetime.today(),
                           endDateTime=datetime.today(),
                           ):
        """Note that 0 is the default value to return from all locations."""
        result = SiteServiceMethods().GetResources(siteIDs,
                                                   sessionTypeIds,
                                                   locationId,
                                                   page,
                                                   startDateTime,
                                                   endDateTime)
        return result

    """GetSessionTypes Methods"""
    def GetSessionTypes(self, programIds=None, onlineOnly=False):
        result = SiteServiceMethods().GetSessionTypes(programIds, onlineOnly)
        return result

    """GetSites Methods"""
    def GetSites(self, searchText=None, relatedSiteId=None):
        result = SiteServiceMethods().GetSites(searchText, relatedSiteId)
        return result

    """GetSite Methods"""
    def GetSite(self, searchText=None, relatedSiteId=None, siteIDs=None):
        result = SiteServiceMethods().GetSite(searchText, relatedSiteId, siteIDs)
        return result

class SiteServiceMethods(object):
    """This class contains producer methods for all SiteService methods."""
    def __init__(self):
        wsdl = BasicRequestHelper.BuildWsdlUrl("Site")
        self.service = Client(wsdl)

    def CreateBasicRequest(self, requestName, siteIDs, page=0):
        return BasicRequestHelper.CreateBasicRequest(self.service, requestName, siteIDs, page)

    """GetActivationCode methods"""
    def GetActivationCode(self, site_id):
        request = self.CreateBasicRequest("GetActivationCode", site_id)

        return self.service.service.GetActivationCode(request)

    """GetLocations methods"""
    def GetLocations(self, siteIDs):
        request = self.CreateBasicRequest("GetLocations", siteIDs)

        return self.service.service.GetLocations(request)

    """GetPrograms methods"""
    def GetPrograms(self, siteIDs, scheduleType, onlineOnly):
        request = self.CreateBasicRequest("GetPrograms", siteIDs)

        request.ScheduleType = BasicRequestHelper.SetEnumerable(self.service, "ScheduleType", scheduleType)
        request.OnlineOnly = onlineOnly

        return self.service.service.GetPrograms(request)

    """GetRelationships methods"""
    def GetRelationships(self):
        request = self.CreateBasicRequest("GetRelationships")

        return self.service.service.GetRelationships(request)

    """GetResources methods"""
    def GetResources(self, siteIDs, sessionTypeIds, locationId, page, startDateTime, endDateTime):
        request = self.CreateBasicRequest("GetResources", siteIDs=siteIDs, page=page)

        request.SessionTypeIDs = BasicRequestHelper.FillArrayType(self.service, sessionTypeIds, "Int")
        request.LocationID = locationId
        request.StartDateTime = startDateTime
        request.EndDateTime = endDateTime

        return self.service.service.GetResources(request)

    """GetSessionTypes methods"""
    def GetSessionTypes(self, programIds, onlineOnly):
        request = self.CreateBasicRequest("GetSessionTypes")

        request.ProgramIDs = BasicRequestHelper.FillArrayType(self.service, programIds, "Int")
        request.OnlineOnly = onlineOnly

        return self.service.service.GetSessionTypes(request)

    """GetSites methods"""
    def GetSites(self, searchText, relatedSiteId):
        request = self.CreateBasicRequest("GetSites")

        request.SearchText = searchText
        request.RelatedSiteID = relatedSiteId

        return self.service.service.GetSites(request)

    """GetSite methods"""
    def GetSite(self, searchText, relatedSiteId, siteIDs):
        request = self.CreateBasicRequest("GetSites", siteIDs)

        request.SearchText = searchText
        request.RelatedSiteID = relatedSiteId

        return self.service.service.GetSites(request)