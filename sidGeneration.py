import pprint
pp = pprint.PrettyPrinter()

def addToList(item_, list_):
    if item_ not in list_:
        list_.append(item_)

def concat(*args, delimiter="/"):
    concatString = ""
    for i in args:
        concatString += i + delimiter
    
    concatString = concatString.removeprefix(delimiter)
    concatString = concatString.removesuffix(delimiter)
    return concatString

def guessIdentifiers(messageDict, grandParent=""):
    """
    From a given python dictionary containing an arbitrary message, try to guess the identifers
    Append grandParent to the identifiers
    """
    outputIdentifers = []
    for parent, child in messageDict.items():
        addToList(concat(grandParent, parent), outputIdentifers)
        if type(child) == dict:
            childOutputIdentifiers = guessIdentifiers(child, parent)
            for childIdentifier in childOutputIdentifiers:
                addToList( concat(grandParent, childIdentifier), outputIdentifers)

        elif type(child) == list:
            for infant in child:
                infantOutputIdentifiers = guessIdentifiers(infant, parent)
                for infantIdentifier in infantOutputIdentifiers:
                    addToList( concat( grandParent, infantIdentifier), outputIdentifers)
                    
        else:
            addToList(concat(grandParent, parent), outputIdentifers)

    return outputIdentifers


def generateSIDFile(identifiers, startSID, range, moduleName="moduleName", moduleRevision="unknown"):
    """
    generate a SID dictionary
    """
    if len(identifiers) > range:
        raise Exception("You need to increase the range to at least %s "%(len(identifiers)))

    sidDictionaryTemplate = { "assignment-range": [
        {   "entry-point": 60000,
            "size": 100}],
    "module-name": "energy-saving",
    "module-revision": "unknown",
    "item": []
    }

    sidDictionaryTemplate["assignment-range"][0]["entry-point"] = startSID
    sidDictionaryTemplate["assignment-range"][0]["size"] = range
    sidDictionaryTemplate["module-name"] = moduleName
    sidDictionaryTemplate["module-revision"] = moduleRevision

    # Get items by guessing identifiers
    sidIdentifiers = []

    # Change modulename format to match identifier format
    sidTemplate = {
                "namespace": "data",
                "identifier": None,
                "sid": None,
                "type" : "GenericType"
    }

    moduleItem = dict(sidTemplate)
    moduleItem["namespace"] = "module"
    moduleItem["identifier"] = moduleName
    moduleItem["sid"] = startSID
    sidIdentifiers.append(moduleItem)

    moduleName = "/" + moduleName + ":"
    # Starts from 1 because first SID already utilized for modulename 
    iterator = 1

    for identity in identifiers:
        sidIdentifiers.append(
               {
                "namespace": "data",
                "identifier": moduleName+identity,
                "sid": startSID + iterator,
                "type" : "GenericType"
            }
        )

        iterator += 1

    sidDictionaryTemplate["item"] = sidIdentifiers
    return sidDictionaryTemplate

def main():
    x = {
    "energy-saving": {
      "device": [
        {
          "device-id": "router-01",
          "metrics": {
            "power-consumption": 125.50,
            "energy-saving-mode": "active",
            "temperature": 45.3
          }
  },
     {
          "device-id2": "rout121er-01",
          "metrics": {
            "power-consumption2": 132325.50,
            "energy-saving-mode": "actccive",
            "temperature":145.3
          }}]}}
    
    identifiers = guessIdentifiers(x)
    print(identifiers)

    sidFile = generateSIDFile(identifiers, 60000, 10)
    pp.pprint(sidFile)

if __name__ == "__main__":
    main()