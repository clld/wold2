from clld.web.maps import ParameterMap, Map


class MeaningMap(ParameterMap):
    def options(self):
        return {'style_map': 'wold_meaning'}


class LanguageMap(Map):
    def options(self):
        return {'style_map': 'wold_languages'}
