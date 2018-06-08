import client, logger, base64, json, control, cache

baseUrl = base64.b64decode('aHR0cDovL3N3YWRlc2kuZGRucy5uZXQvc3dhZGVzaS92YWxpZGF0ZQ==')
auth = base64.b64decode('QmFzaWMgWkRNMlpqUXhOakV6T0RKaE5ESmtZemhpTkdVMlpEbGlaVEZsWmpneU1tUTZRamczTXpVeVF6a3pNVGRtTkdKR1FrRkVOMFEyTURJM1pEY3pNRE0yTlVVPQ==')


def check():
    email = control.setting('email')
    userHash = control.setting('userHash')
    if userHash == '' : userHash = None

    return cache.get(checkRegistery, 168, email, userHash)

def checkRegistery(email=None, userHash=None):


    if email == None :
        return userHash

    if userHash == None :
        query = 'email=%s' % (email)
    else :
        query = 'email=%s&userHash=%s' % (email, userHash)

    url = '%s?%s' % (baseUrl, query)
    headers = {'Authorization': auth}
    result = client.request(url, headers=headers)
    result = json.loads(result)
    userHash = result.get('userHash')
    error = result.get('error')

    control.setSetting(id="userHash", value=userHash)
    return error