import os

from configparser import ConfigParser

class ProjectPrefs:
    #SFB Class wide defaults
    DEFAULT_FILENAME = 'project.ini'
    
    ALLOWED_PREFS = {
        'PATH_TO_IMAGES': { 'section': 'PATHS' },
        'IMAGE_PREFIX': { 'section': 'PROJECT' },
        'PATH_TO_MASKS': { 'section': 'PATHS' },
    }
    
    #SFB Create a new ProjectPrefs that will read from the ini file
    def __init__(self, prefsFilename = None):
        #SFB Use the default filename if none was provided
        if not prefsFilename:
            prefsFileName = ProjectPrefs.DEFAULT_FILENAME

        #SFB Attempt to read the ini preferences first
        self.readConfig(prefsFileName)

    def readConfig(self, prefsFileName):
        #SFB Initialize the config parser
        if prefsFileName:
            self.prefsFileName = prefsFileName
        self.INIConfig = ConfigParser()
        self.INIConfig.optionxform=str

        #SFB Try to read the config file allowing failure
        try:
            self.INIConfig.read(self.prefsFileName)
        except:
            pass

        #SFB Check all allowed preferences in ini file
        for name, argument in ProjectPrefs.ALLOWED_PREFS.items():
            #SFB Ensure the section exists
            if not self.INIConfig.has_section(argument['section']):
                self.INIConfig.add_section(argument['section'])

            #SFB Set the default value if there is none
            if self.INIConfig[argument['section']].get(name) is None and 'default' in argument:
                self.INIConfig[argument['section']][name] = argument['default']
    
    def saveConfig(self, prefsFileName = None):
        #SFB Update the filename if provided
        if prefsFileName:
            self.prefsFileName = prefsFileName
        
        #AIW Gets current working directory for testing.
        print('Path being used by saveConfig: ' + os.getcwd())

        #SFB Write out the current config file
        #AIW NEEDS TO SAVE TO SAME PATH AS IMAGES
        with open(self.prefsFileName, 'w') as prefsFile:
            self.INIConfig.write(prefsFile)
    
        #SFB Set value of a given preference (throws an exception on unknown preferences)
    #SFB Does NOT save the ini file (must be done manually with saveConfig())
    def setPref(self, prefName, newValue):
        #SFB check the preference name
        if not prefName in ProjectPrefs.ALLOWED_PREFS:
            raise Exception('Invalid preference name - {}'.format(prefName))
        
        #SFB Assign newValue to the preference in the INI config object        
        pref = ProjectPrefs.ALLOWED_PREFS[prefName]
        self.INIConfig[pref['section']][prefName] = newValue
    
    #SFB Retrieve value of a given preference (throws an exception on unknown preferences)
    def getPref(self, prefName):
        #SFB check the preference name
        if not prefName in ProjectPrefs.ALLOWED_PREFS:
            raise Exception('Invalid preference name - {}'.format(prefName))

        #SFB Retrieve and return the preference value        
        pref = ProjectPrefs.ALLOWED_PREFS[prefName]
        return self.INIConfig[pref['section']][prefName]