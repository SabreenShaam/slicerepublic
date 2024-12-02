from suds.client import Client
from datetime import datetime
from mind_body_online import BasicRequestHelper


class ClientServiceCalls:
    """This class contains examples of consumer methods for each ClassService method."""

    """AddArrival Methods"""
    def AddArrival(self, clientId, locationId):
        result = ClientServiceMethods().AddArrival(clientId, locationId)
        return result

    """AddClientFormulaNote Methods"""
    def AddFormulaNoteToClientWithAppointment(self, clientId, appointmentId, note):
        result = ClientServiceMethods().AddClientFormulaNote(clientId, appointmentId, note)
        return result

    def AddFormulaNoteToClient(self, clientId, note):
        self.AddFormulaNoteToClientWithAppointment(clientId, None, note)

    """AddOrUpdateClient Methods"""
    def AddOrUpdateClients(self, updateAction="Fail", test=False, clients=None, mbo_site_ids=None, mbo_username=None, mbo_password=None):
        result = ClientServiceMethods().AddOrUpdateClients(updateAction, test, clients, mbo_site_ids, mbo_username, mbo_password)
        return result

    def AddCreditCardToClient(self, clientId, cc):
        """A consumer method for adding a credit card to a client's information.
           Note that adding a credit card in particular requires a secure connection 
           (https url) when setting up your service."""
        result = ClientServiceMethods().AddCreditCardToClient(clientId, cc)
        return result

    def AddNewCreditCardToClient(self, clientId, 
                                       cardType, 
                                       lastFour, 
                                       cardNumber, 
                                       holderName, 
                                       expMonth, 
                                       expYear, 
                                       address, 
                                       city, 
                                       state, 
                                       postalCode):
        """A consumer method for adding a new or default credit card
           to a client's information. Note that adding a credit card 
           in particular requires a secure connection (https url) when 
           setting up your service."""
        result = ClientServiceMethods().CreateAndAddCreditCardToClient(clientId, 
                                                                       cardType, 
                                                                       lastFour, 
                                                                       cardNumber, 
                                                                       holderName, 
                                                                       expMonth, 
                                                                       expYear, 
                                                                       address, 
                                                                       city, 
                                                                       state, 
                                                                       postalCode)
        return result

    """AddOrUpdateContactLogs Methods"""
    def UpdateContactLogText(self, clientId, text):
        result = ClientServiceMethods().UpdateContactLogText(clientId, text)
        return result

    """DeleteClientFormulaNote Methods"""
    def DeleteFormulaNote(self, clientId, formulaNoteId):
        result = ClientServiceMethods().DeleteFormulaNote(clientId, formulaNoteId)
        return result

    """GetActiveClientMemberships Methods"""
    def GetActiveClientMemberships(self, clientId, locationId=None):
        result = ClientServiceMethods().GetActiveClientMemberships(clientId, locationId)
        return result

    """GetClientAccountBalances Methods"""
    def GetRelativeClientAccountBalances(self, clientIds, balanceDate=None, classId=None):
        result = ClientServiceMethods().GetClientAccountBalances(clientIds, balanceDate, classId)
        return result

    def GetCurrentClientAccountBalances(self, clientIds, classId=None):
        self.GetRelativeClientAccountBalances(clientIds, classId=classId)

    """GetClientContactLogs Methods"""
    def GetClientContactLogs(self, clientId, 
                                   startDate=datetime.today(), 
                                   endDate=datetime.today(), 
                                   staffIds=None, 
                                   systemGenerated=False, 
                                   typeIds=None, 
                                   subtypeIds=None):
        result = ClientServiceMethods().GetClientContactLogs(clientId, 
                                                             startDate, 
                                                             endDate, 
                                                             staffIds, 
                                                             systemGenerated, 
                                                             typeIds, 
                                                             subtypeIds)
        return result

    """GetClientContracts Methods"""
    def GetClientContracts(self, clientId=None):
        result = ClientServiceMethods().GetClientContracts(clientId)
        return result

    """GetClientFormulaNotes Methods"""
    def GetClientFormulaNotes(self, clientId, appointmentId=None):
        result = ClientServiceMethods().GetClientFormulaNotes(clientId, appointmentId)
        return result

    """GetClientIndexes Methods"""
    def GetClientIndexes(self):
        result = ClientServiceMethods().GetClientIndexes()
        return result

    """GetClientPurchases Methods"""
    def GetClientPurchases(self, clientId, startDate=datetime.today(), endDate=datetime.today()):
        result = ClientServiceMethods().GetClientPurchases(clientId, startDate, endDate)
        return result

    """GetClientReferralTypes Methods"""
    def GetClientReferralTypes(self):
        result = ClientServiceMethods().GetClientReferralTypes()
        return result

    """GetClients Methods"""
    def GetClientsBySingleId(self, id):
        result = ClientServiceMethods().GetClientsBySingleId(id)
        return result

    def GetClientsByMultipleIds(self, ids, mbo_site_ids, field):
        result = ClientServiceMethods().GetClientsByMultipleIds(ids, mbo_site_ids, field)
        return result

    def GetAllClients(self):
        result = ClientServiceMethods().GetAllClients()
        return result

    def GetClientsByString(self, searchStr, mbo_site_ids=None, mbo_username=None, mbo_password=None):
        result = ClientServiceMethods().GetClientsByString(searchStr, mbo_site_ids=mbo_site_ids, mbo_username=mbo_username, mbo_password=mbo_password)
        return result

    """GetClientSchedule Methods"""
    def GetClientSchedule(self, clientId, startDate=datetime.today(), endDate=datetime.today()):
        result = ClientServiceMethods().GetClientSchedule(clientId, startDate, endDate)
        return result

    """GetClientServices Methods"""
    def GetClientServices(self, clientId, 
                                classId=0,
                                programIds=None, 
                                sessionTypeIds=None, 
                                locationIds=None, 
                                visitCount=0,
                                startDate=None, 
                                endDate=None, 
                                showActiveOnly=False,
                                mbo_site_ids=None):
        result = ClientServiceMethods().GetClientServices(clientId, 
                                                          classId, 
                                                          programIds, 
                                                          sessionTypeIds, 
                                                          locationIds, 
                                                          visitCount, 
                                                          startDate, 
                                                          endDate, 
                                                          showActiveOnly,
                                                          mbo_site_ids)
        return result

    def GetClientServicesForPastYear(self, clientId, 
                                           classId=0, 
                                           programIds=None, 
                                           sessionTypeIds=None, 
                                           locationIds=None, 
                                           visitCount=0, 
                                           showActiveOnly=False):
        self.GetClientServices(clientId, 
                               classId, 
                               programIds, 
                               sessionTypeIds, 
                               locationIds, 
                               visitCount, 
                               BasicRequestHelper.oneYearAgo, 
                               datetime.today(), 
                               showActiveOnly)

    """GetClientVisits Methods"""
    def GetClientVisits(self, clientId, 
                              startDate=datetime.today(), 
                              endDate=datetime.today(), 
                              unpaidsOnly=False,
                              mbo_site_ids=None,
                              mbo_username=None,
                              mbo_password=None):
        result = ClientServiceMethods().GetClientVisits(clientId, 
                                                        startDate, 
                                                        endDate, 
                                                        unpaidsOnly,
                                                        mbo_site_ids,
                                                        mbo_username,
                                                        mbo_password)
        return result

    """GetContactLogTypes Methods"""
    def GetContactLogTypes(self):
        result = ClientServiceMethods().GetContactLogTypes()
        return result

    """GetCustomClientFields Methods"""
    def GetCustomClientFields(self):
        """A consumer method for retrieving all custom client fields. This contains
           an example of parsing a result to print fields out in an easier-to-read
           format than the returned XML."""
        result = ClientServiceMethods().GetCustomClientFields()

        # print "ID - Name"
        # print "------------------------------"
        # for field in result.CustomClientFields.CustomClientField:
        #     print "%2d - %s" % (field.ID, field.Name)

    """GetRequiredClientFields Methods"""
    def GetRequiredClientFields(self, site_ids):
        result = ClientServiceMethods().GetRequiredClientFields(site_ids)
        return result

    """SendUserNewPassword methods"""
    def SendUserNewPassword (self, user_email, first_name, last_name, mbo_site_ids):
        result = ClientServiceMethods().SendUserNewPassword(user_email, first_name, last_name, mbo_site_ids)
        # if hasattr(result, "Message"):
        #     print result.Message
        # else:
        #     print "No error message returned. Success!"
        return result

    """UpdateClientServices Methods"""
    def UpdateClientServices(self, clientServices, test=False):
        result = ClientServiceMethods().UpdateClientServices(clientServices, test)
        return result

    """UploadClientDocument Methods"""
    def UploadClientDocument(self, clientId, fileName, fileSize):
        result = ClientServiceMethods().UploadClientDocument(clientId, fileName, fileSize)
        return result

    """ValidateLogin Methods"""
    def ValidateLogin(self, username, password, mbo_site_ids=None, mbo_username=None, mbo_password=None):
        result = ClientServiceMethods().ValidateLogin(username=username, password=password, mbo_site_ids=mbo_site_ids, mbo_username=mbo_username, mbo_password=mbo_password)
        return result



class ClientServiceMethods(object):
    def __init__(self):
        """This class contains producer methods for all ClientService methods."""
        wsdl = BasicRequestHelper.BuildWsdlUrl("Client")
        """We manually set the SoapAction field here by specifying location. Specifically,
           we need an https connection (for things such as modifying billing information
           and by default, this gets set to http."""
        self.service = Client(wsdl, location="https://api.mindbodyonline.com/0_5/ClientService.asmx")

    def CreateBasicRequest(self, requestName, mbo_site_ids=None, mbo_username=None, mbo_password=None):
        return BasicRequestHelper.CreateBasicRequest(
            self.service,
            requestName=requestName,
            siteIDs=mbo_site_ids,
            mbo_username=mbo_username,
            mbo_password=mbo_password
        )

    """AddArrival methods"""
    def AddArrival(self, clientId, locationId):
        request = self.CreateBasicRequest("AddArrivalRequest")

        request.ClientID = clientId
        request.LocationID = locationId

        return self.service.service.AddArrival(request)

    """AddClientFormulaNote methods"""
    def AddClientFormulaNote(self, clientId, appointmentId, note):
        request = self.CreateBasicRequest("AddClientFormulaNote")

        request.ClientID = clientId
        request.AppointmentID = appointmentId
        request.Note = note

        return self.service.service.AddClientFormulaNote(request)

    """AddOrUpdateClient methods"""
    def AddOrUpdateClients(self, updateAction, test, clients, mbo_site_ids=None, mbo_username=None, mbo_password=None):
        request = self.CreateBasicRequest("AddOrUpdateClients", mbo_site_ids=mbo_site_ids, mbo_username=mbo_username, mbo_password=mbo_password)

        request.UpdateAction = updateAction
        request.Test = test
        request.Clients.Client = clients

        return self.service.service.AddOrUpdateClients(request)

    def AddCreditCardToClient(self, clientId, cc):

        #Call GetClientBySingleID, then grab the first client off the list.
        clientToEdit = self.GetClientsBySingleId(clientId).Clients.Client[0]
        clientToEdit.ClientCreditCard = cc
        Clients = BasicRequestHelper.FillArrayType(self.service, [clientToEdit], "Client", "Client")

        return self.AddOrUpdateClients("Fail", False, Clients)

    def CreateAndAddCreditCardToClient(self, clientId, 
                                             cardType, 
                                             lastFour, 
                                             number, 
                                             holderName, 
                                             expMonth, 
                                             expYear, 
                                             address, 
                                             city, 
                                             state, 
                                             postalCode):
        """This method shows how to create a credit card item from given simple types."""
        cc = self.service.factory.create("ClientCreditCard")
        cc.CardType = cardType
        cc.LastFour = lastFour
        cc.CardNumber = number
        cc.CardHolder = holderName
        cc.ExpMonth = expMonth
        cc.ExpYear = expYear
        cc.Address = address
        cc.City = city
        cc.State = state
        cc.PostalCode = postalCode

        return self.AddCreditCardToClient(clientId, cc)

    """AddOrUpdateContactLogs methods"""
    def UpdateContactLogText(self, clientId, text):
        """This method will change the text of every contact log 
           applied to clientId in the past year to text."""
        request = self.CreateBasicRequest("AddOrUpdateContactLogs")

        contactLogs = self.GetClientContactLogsByClient(clientId, True)
        for log in contactLogs.ContactLogs.ContactLog:
            log.Text = text

        request.UpdateAction = "Fail"
        request.Test = False
        request.ContactLogs = contactLogs
        
        return self.service.service.AddOrUpdateContactLogs(request)

    """DeleteClientFormulaNote methods"""
    def DeleteFormulaNote(self, clientId, formulaNoteId):
        request = self.CreateBasicRequest("DeleteClientFormulaNote")

        request.ClientID = clientId
        request.FormulaNoteID = formulaNoteId

        return self.service.service.DeleteClientFormulaNote(request)

    """GetActiveClientMemberships Methods"""
    def GetActiveClientMemberships(self, clientId, locationId):
        request = self.CreateBasicRequest("GetActiveClientMemberships")

        request.ClientID = clientId
        request.LocationID = locationId

        return self.service.service.GetActiveClientMemberships(request)

    """GetClientAccountBalances methods"""
    def GetClientAccountBalances(self, clientIds, balanceDate, classId):
        request = self.CreateBasicRequest("GetClientAccountBalances")

        ClientIDs = self.service.factory.create("ArrayOfString")
        ClientIDs.string = clientIds

        request.ClientIDs = ClientIDs
        request.BalanceDate = balanceDate
        request.ClassID = classId

        return self.service.service.GetClientAccountBalances(request)

    """GetClientContactLogs methods"""
    def GetClientContactLogs(self, clientId, 
                                   startDate, 
                                   endDate, 
                                   staffIds, 
                                   systemGenerated, 
                                   typeIds, 
                                   subtypeIds):
        request = self.CreateBasicRequest("GetClientContactLogsRequest")

        request.ClientID = clientId
        request.StartDate = startDate
        request.EndDate = endDate
        request.StaffIDs = BasicRequestHelper.FillArrayType(self.service, staffIds, "Long")
        request.ShowSystemGenerated = systemGenerated
        request.TypeIDs = typeIds
        request.SubtypeIDs = subtypeIds

        return self.service.service.GetClientContactLogs(request)

    def GetClientContactLogsByClient(self, clientId, systemGenerated):
        """Convenience method to find all contact logs for a given client within the past year."""
        return self.GetClientContactLogs(clientId, 
                                         BasicRequestHelper.oneYearAgo, 
                                         datetime.today(), 
                                         None, 
                                         systemGenerated, 
                                         None, 
                                         None)

    """GetClientContracts methods"""
    def GetClientContracts(self, clientId):
        request = self.CreateBasicRequest("GetClientContracts")

        request.ClientID = clientId

        return self.service.service.GetClientContracts(request)

    """GetClientFormulaNotes methods"""
    def GetClientFormulaNotes(self, clientId, appointmentId):
        request = self.CreateBasicRequest("GetClientFormulaNotes")

        request.ClientID = clientId
        request.AppointmentID = appointmentId

        return self.service.service.GetClientFormulaNotes(request)

    """GetClientIndexes methods"""
    def GetClientIndexes(self):
        request = self.CreateBasicRequest("GetClientIndexesRequest")

        return self.service.service.GetClientIndexes(request)

    """GetClientPurchases methods"""
    def GetClientPurchases(self, clientId, startDate, endDate):
        request = self.CreateBasicRequest("GetClientPurchases")

        request.ClientID = clientId
        request.StartDate = startDate
        request.EndDate = endDate

        return self.service.service.GetClientPurchases(request)

    """GetClientReferralTypes methods"""
    def GetClientReferralTypes(self):
        request = self.CreateBasicRequest("GetClientReferralTypes")

        return self.service.service.GetClientReferralTypes(request)

    """GetClientVisits methods"""
    def GetClientVisits(self, clientId, startDate, endDate, unpaidsOnly, mbo_site_ids, mbo_username=None,
                        mbo_password=None):
        request = self.CreateBasicRequest("GetClientVisits",
                                          mbo_site_ids=mbo_site_ids,
                                          mbo_username=mbo_username,
                                          mbo_password=mbo_password)

        request.ClientID = clientId
        request.StartDate = startDate
        request.EndDate = endDate
        request.UnpaidsOnly = unpaidsOnly

        return self.service.service.GetClientVisits(request)

    """GetClients methods"""
    def GetAllClients(self):
        return self.GetClientsByString(" ")

    def GetClientsBySingleId(self, id):
        return self.GetClientsByMultipleIds([id])

    def GetClientsByString(self, searchStr, mbo_site_ids, mbo_username, mbo_password):
        """Convenience method to find clients containing searchStr in their name or e-mail."""
        request = self.CreateBasicRequest("GetClientsRequest", mbo_site_ids=mbo_site_ids, mbo_username=mbo_username, mbo_password=mbo_password)

        #Since SearchText is just a string, we can assign it directly.
        request.SearchText = searchStr

        return self.service.service.GetClients(request)

    def GetClientsByMultipleIds(self, ids, mbo_site_ids, fields):
        request = self.CreateBasicRequest("GetClientsRequest", mbo_site_ids=mbo_site_ids)

        """Here, we create an instance of ArrayOfString (the type of ClientIDs in
           the request) and fill it with our ids before assigning it to our request."""
        clientIDs = self.service.factory.create("ArrayOfString")
        clientIDs.string = ids
        request.ClientIDs = clientIDs

        field_names = self.service.factory.create("ArrayOfString")
        field_names.string = fields
        request.Fields = field_names

        return self.service.service.GetClients(request)

    """GetClientSchedule methods"""
    def GetClientSchedule(self, clientId, startDate, endDate):
        request = self.CreateBasicRequest("GetClientSchedule")

        request.ClientID = clientId
        request.StartDate = startDate
        request.EndDate = endDate

        return self.service.service.GetClientSchedule(request)

    """GetClientServices methods"""
    def GetClientServices(self, clientId, 
                                classId, 
                                programIds, 
                                sessionTypeIds, 
                                locationIds, 
                                visitCount, 
                                startDate, 
                                endDate, 
                                showActiveOnly,
                                mbo_site_ids):
        """A few notes about GetClientServices:
            1. If you don't want to pass a Class ID in, pass 0. This acts as you would expect None to.
            2. ProgramIDs is a required field."""
        request = self.CreateBasicRequest("GetClientServices", mbo_site_ids=mbo_site_ids)

        request.ClientID = clientId
        request.ClassID = classId
        request.ProgramIDs = BasicRequestHelper.FillArrayType(self.service, programIds, "Int")
        request.SessionTypeIDs = BasicRequestHelper.FillArrayType(self.service, sessionTypeIds, "Int")
        request.LocationIDs = BasicRequestHelper.FillArrayType(self.service, locationIds, "Int")
        request.VisitCount = visitCount
        request.StartDate = startDate
        request.EndDate = endDate
        request.ShowActiveOnly = showActiveOnly

        return self.service.service.GetClientServices(request)

    """GetContactLogTypes methods"""
    def GetContactLogTypes(self):
        request = self.CreateBasicRequest("GetContactLogTypes")

        return self.service.service.GetContactLogTypes(request)

    """GetCustomClientFields methods"""
    def GetCustomClientFields(self):
        request = self.CreateBasicRequest("GetCustomClientFieldsRequest")

        return self.service.service.GetCustomClientFields(request)

    """GetRequiredClientFields methods"""
    def GetRequiredClientFields(self, site_ids):
        request = self.CreateBasicRequest("GetRequiredClientFields", mbo_site_ids=site_ids)

        return self.service.service.GetRequiredClientFields(request)

    """SendUserNewPassword methods"""
    def SendUserNewPassword (self, user_email,userFirstName, userLastName, mbo_site_ids):
        request = self.CreateBasicRequest("SendUserNewPassword", mbo_site_ids=mbo_site_ids)

        request.UserEmail = user_email
        request.UserFirstName = userFirstName
        request.UserLastName = userLastName

        return self.service.service.SendUserNewPassword(request)

    """UpdateClientServices methods"""
    def UpdateClientServices(self, clientServices, test):
        request = self.CreateBasicRequest("UpdateClientServices")

        ServiceList = self.service.factory.create("ArrayOfClientService")
        ServiceList.ClientService = clientServices

        request.ClientServices = ServiceList
        request.Test = test

        return self.service.service.UpdateClientServices(request)

    """UploadClientDocument methods"""
    def UploadClientDocument(self, clientId, fileName, fileSize):
        request = self.CreateBasicRequest("UploadClientDocument")

        request.ClientID = clientId
        request.FileName = fileName
        request.Bytes = fileSize

        return self.service.service.UploadClientDocument(request)

    """ValidateLogin methods"""
    def ValidateLogin(self, username, password, mbo_site_ids, mbo_username=None, mbo_password=None):
        request = self.CreateBasicRequest("ValidateLogin", mbo_site_ids=mbo_site_ids, mbo_username=mbo_username, mbo_password=mbo_password)

        request.Username = username
        request.Password = password

        return self.service.service.ValidateLogin(request)
