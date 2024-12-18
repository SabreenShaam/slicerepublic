"""This is where most universal code for the Python examples of API implementation exist.
   Much of the abstracted logic such as filling out credential objects and arrays
   resides in this class."""
from django.conf import settings


def BuildWsdlUrl(serviceName):
    """This function lets us grab the WSDL for any service we need."""
    return 'https://api.mindbodyonline.com/0_5/{}Service.asmx?wsdl'.format(serviceName)


def CreateStaffCredentials(service, user, password, siteIds):
    """This is a pretty basic method for generating a commonly used field (StaffCredentials)
       in API calls."""
    if(user == None or password == None or siteIds == None):
        return None
    else:
        creds = service.factory.create("StaffCredentials")
        creds.Username = user
        creds.Password = password
        creds.SiteIDs = FillArrayType(service, siteIds, "Int")

        return creds


def FillArrayType(service, elems, arrayType, elemName=None):
    """This method will create an 'ArrayOfX' object and then fill it with the array passed in.
       This takes advantage of the fact that every ArrayOfX object follows the same pattern
       (i.e., ArrayOfLong uses a "long" attribute. ArrayOfInt uses an "int" attribute, etc) a
       vast majority of the time. In the case where this doesn't apply (ArrayOfVisit has a
       capitalized Visit field instead of visit), elemName can be manually set to the desired
       value."""
    if elemName == None:
        elemName = arrayType.lower()

    if elems != None:
        ArrayObject = service.factory.create("ArrayOf" + arrayType)
        setattr(ArrayObject, elemName, elems)
        return ArrayObject
    else:
        return None


def FillAbstractObject(service, objectType, valueDict):
    """This method is useful for creating the "cartItems" and "payments" fields of
       the CheckoutShoppingCart method. It takes in the array currently being built,
       the name in the WSDL of the element to be added (e.g. DebitAccountInfo for payments
       or Package for the Item field of a CartItem."""
    newObject = service.factory.create(objectType)

    for currField in valueDict.keys():
        setattr(newObject, currField, valueDict[currField])

    return newObject


def SetEnumerable(service, enum, value):
    """This method will generate and return an instance of enum.value."""
    if enum == None or value == None:
        return None
    else:
        return getattr(service.factory.create(enum), value)


def FillDefaultCredentials(service, request, siteIDs, page=0, mbo_username=None, mbo_password=None):
    sourceCreds = service.factory.create('SourceCredentials')
    sourceCreds.SourceName = settings.MBO_SOURCE
    sourceCreds.Password = settings.MBO_KEY
    sourceCreds.SiteIDs.int = siteIDs

    if mbo_username and mbo_password:
        userCreds = service.factory.create('UserCredentials')
        userCreds.Username = mbo_username
        userCreds.Password = mbo_password
        userCreds.SiteIDs.int = siteIDs
        request.UserCredentials = userCreds

    request.SourceCredentials = sourceCreds
    request.XMLDetail = "Full"
    request.PageSize = settings.MBO_PAGE_SIZE
    request.CurrentPageIndex = page

    return request


"""Set siteIDs here to whichever site(s) you wish to make calls upon.
   This example represents site -99, the API Sandbox Site."""
# def CreateBasicRequest(service, requestName, siteIDs=settings.MBODY_SITEIDS, page=0):
def CreateBasicRequest(service, requestName, siteIDs, page=0, mbo_username=None, mbo_password=None):
    """Returns a request object defined by requestName in the WSDL with
       source and user credentials set."""
    request = service.factory.create(requestName)

    if hasattr(request, 'Request'):
        request = request.Request
    return FillDefaultCredentials(service, request, siteIDs, page, mbo_username, mbo_password)
