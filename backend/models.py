from dataclasses import dataclass, field
import json 

@dataclass
class FocusSession():
    id: str = ""
    focuser_positons: list = field(default_factory=list)   # list of values
    fwhm_metrics: list = field(default_factory=list)   # list of values
    hfd_metrics: list = field(default_factory=list)   # list of dicts containing values for each method
    files: list = field(default_factory=list)
    
    fwhm_fit: list = field(default_factory=list)  
    hfd_fits: list = field(default_factory=dict)
    
    def serialize(self):
        return {
            "id": self.id,
            "focuser_positons": self.focuser_positons,
            "fwhm_metrics": self.fwhm_metrics,
            "hfd_metrics": self.hfd_metrics,
            "files": self.files
        }
    