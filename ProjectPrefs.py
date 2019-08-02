import argparse
from configparser import ConfigParser

class ProjectPrefs:
    #SFB Class wide defaults
    DEFAULT_FILENAME = 'project.ini'

    #SFB All the configurable properties
    ALLOWED_PREFS = {
        'ImagePath': { 'short': 'I', 'long': 'images', 'section': 'PATHS',
                       'help': 'Path to the folder containing subject images.' },
        'MaskPath': { 'short': 'M', 'long': 'masks', 'section': 'PATHS',
                      'help': 'Path to the images for background subtraction with filename pattern.' },
        'NamePrefix': { 'short': 'N', 'long': 'name', 'default': 'MetaPy', 'section': 'PROJECT',
                        'help': 'A prefix to apply to log and MetaShape file names.' }
    }

    #SFB Create a new ProjectPrefs that will read from the ini file and command line
    def __init__(self, prefsFileName = None):
        #SFB Use the default filename if none was provided
        if not prefsFileName:
            prefsFileName = ProjectPrefs.DEFAULT_FILENAME

        #SFB Attempt to read the ini preferences first
        self.readConfig(prefsFileName)

        #SFB Parse any command line options provided
        self.parseCommandLine()

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

        #SFB Write out the current config file
        with open(self.prefsFileName, 'w') as prefsFile:
            self.INIConfig.write(prefsFile)

    def parseCommandLine(self):
        #SFB Make sure we have an INI ConfigParser object
        if self.INIConfig is None:
            raise Exception('Must read the INI config file before parsing command line arguments')

        #SFB Create the parser
        argParser = argparse.ArgumentParser(description='Process Photogrammetry Images with MetaShape.')

        #SFB Add possible arguments to the parser
        for name, argument in ProjectPrefs.ALLOWED_PREFS.items():
            argParser.add_argument('-' + argument['short'], '--' + argument['long'],
                metavar=name, help=argument['help'],
                default=self.INIConfig[argument['section']].get(name))

        #SFB Parse the actual command line
        CLArgs = argParser.parse_args()

        #SFB Copy values back to the INI prefs argument if they are not None
        for name, argument in ProjectPrefs.ALLOWED_PREFS.items():
            CLValue = getattr(CLArgs, argument['short'], None)
            if not CLValue is None:
                self.INIConfig[argument['section']][name] = CLValue

    #SFB Set value of a given preference (throws an exception on unknown preferences)
    #SFB Does NOT save the ini file (must be done manually with saveConfig())
    def setPref(self, prefName, newValue):
        #SFB check the preference name
        if not prefName in ProjectPrefs.ALLOWED_PREFS:
            raise Exception('Invalid preference name - "{}"'.format(prefName))
        
        #SFB Assign newValue to the preference in the INI config object        
        pref = ProjectPrefs.ALLOWED_PREFS[prefName]
        self.INIConfig[pref['section']][prefName] = newValue
    
    #SFB Retrieve value of a given preference (throws an exception on unknown preferences)
    def getPref(self, prefName):
        #SFB check the preference name
        if not prefName in ProjectPrefs.ALLOWED_PREFS:
            raise Exception('Invalid preference name - "{}"'.format(prefName))

        #SFB Retrieve and return the preference value        
        pref = ProjectPrefs.ALLOWED_PREFS[prefName]
        return self.INIConfig[pref['section']][prefName]
