import json

class Config:
   def __init__ (self, startonload=True, theme="default", fontfamily="'trebuchet ms', verdana, arial, sans-serif;", securitylevel="strict", loglevel="fatal", arrowmarkerabsolute=False):
      self.startOnLoad = startonload
      self.theme = theme
      self.fontFamily = fontfamily
      self.securityLevel = securitylevel
      self.logLevel = loglevel
      self.arrowMarkerAbsolute = arrowmarkerabsolute
   
   def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
