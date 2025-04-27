import os

from configparser import ConfigParser


class ProjectPrefs:
    # Class wide defaults
    DEFAULT_FILENAME = 'project.ini'

    ALLOWED_PREFS = {
        'PATH_TO_IMAGES': {'section': 'PATHS'},
        'PROJECT_NAME': {'section': 'PROJECT'},
        'PATH_TO_MASKS': {'section': 'PATHS'},

        'INIT': {'section': 'TIMING'},
        'INIT_IMAGE_LOAD': {'section': 'TIMING'},
        'INIT_DETECT_MARKERS': {'section': 'TIMING'},
        'INIT_APPLY_MASKS': {'section': 'TIMING'},

        'IMAGE_ALIGN': {'section': 'TIMING'},
        'IMAGE_ALIGN_MATCHING': {'section': 'TIMING'},
        'IMAGE_ALIGN_BUNDLE_ADJUST': {'section': 'TIMING'},

        'DENSE_CLOUD': {'section': 'TIMING'},
        'DENSE_CLOUD_DEPTH_MAPS': {'section': 'TIMING'},
        'DENSE_CLOUD_BUILD': {'section': 'TIMING'},

        'BUILD_MODEL': {'section': 'TIMING'},
        'BUILD_MODEL_MESH': {'section': 'TIMING'},
        'BUILD_MODEL_UV': {'section': 'TIMING'},
        'BUILD_MODEL_TEXTURE': {'section': 'TIMING'},

        'BUILD_MODEL_TIE_POINTS': {'section': 'TIMING'},
        'BUILD_MODEL_MESH_TIE_POINTS': {'section': 'TIMING'},
        'BUILD_MODEL_UV_TIE_POINTS': {'section': 'TIMING'},
        'BUILD_MODEL_TEXTURE_TIE_POINTS': {'section': 'TIMING'},

        'BUILD_MODEL_DENSE_CLOUD': {'section': 'TIMING'},
        'BUILD_MODEL_MESH_DENSE_CLOUD': {'section': 'TIMING'},
        'BUILD_MODEL_UV_DENSE_CLOUD': {'section': 'TIMING'},
        'BUILD_MODEL_TEXTURE_DENSE_CLOUD': {'section': 'TIMING'},

        'BUILD_MODEL_DEPTH_MAPS': {'section': 'TIMING'},
        'BUILD_MODEL_MESH_DEPTH_MAPS': {'section': 'TIMING'},
        'BUILD_MODEL_UV_DEPTH_MAPS': {'section': 'TIMING'},
        'BUILD_MODEL_TEXTURE_DEPTH_MAPS': {'section': 'TIMING'}
    }

    prefsFileName = None

    # Create a new ProjectPrefs that will read from the ini file
    def __init__(self, prefsFilename = None):
        if prefsFilename is not None:
            self.prefsFileName = prefsFilename
        else:
            self.prefsFileName = ProjectPrefs.DEFAULT_FILENAME

        # Attempt to read the ini preferences first
        if self.prefsFileName is not None:
            self.readConfig()

    def readConfig(self, prefsFileName = None):
        # Initialize the config parser
        if prefsFileName is not None:
            self.prefsFileName = prefsFileName
        self.INIConfig = ConfigParser()
        self.INIConfig.optionxform = str

        # Try to read the config file allowing failure
        try:
            self.INIConfig.read(self.prefsFileName)
        except Exception as e:
            print('No existing config file')

        # Check all allowed preferences in ini file
        for name, argument in ProjectPrefs.ALLOWED_PREFS.items():
            # Ensure the section exists
            if not self.INIConfig.has_section(argument['section']):
                self.INIConfig.add_section(argument['section'])

            # Set the default value if there is none
            if self.INIConfig[argument['section']].get(name) is None and 'default' in argument:
                self.INIConfig[argument['section']][name] = argument['default']

    def saveConfig(self, prefsFileName = None, prefsFilePath = './'):
        # Updates the filename and path with the parameters provided.
        if prefsFileName:
            self.prefsFileName = os.path.join(prefsFilePath, prefsFileName)

        # Write out the current config file
        with open(self.prefsFileName, 'w') as prefsFile:
            self.INIConfig.write(prefsFile)

    # Set value of a given preference (throws an exception on unknown
    # preferences)
    # - Does NOT save the ini file (must be done manually with saveConfig())
    def setPref(self, prefName, newValue):
        # check the preference name
        if prefName not in ProjectPrefs.ALLOWED_PREFS:
            raise Exception('Invalid preference name - {}'.format(prefName))

        # Assign newValue to the preference in the INI config object
        pref = ProjectPrefs.ALLOWED_PREFS[prefName]
        self.INIConfig[pref['section']][prefName] = str(newValue)

    # Retrieve value of a given preference (throws an exception on unknown
    # preferences)
    def getPref(self, prefName):
        # check the preference name
        if prefName not in ProjectPrefs.ALLOWED_PREFS:
            raise Exception('Invalid preference name - {}'.format(prefName))

        # Retrieve and return the preference value
        pref = ProjectPrefs.ALLOWED_PREFS[prefName]
        if prefName in self.INIConfig[pref['section']]:
            return self.INIConfig[pref['section']][prefName]
        else:
            print('Preference {} not found in config file'.format(prefName))
            return None
