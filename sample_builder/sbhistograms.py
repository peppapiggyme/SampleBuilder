# IMPORT
from ROOT import TFile, gDirectory


# Singleton: one ROOT file -> one instance (singleton not checked)
# FIXME: This step is very slow!!!

class SBHistograms():

    def __init__(self, root_file_name, region_prefix, masses):
        self.root_file_name = root_file_name
        self.region_prefix = region_prefix
        self.masses = masses
        self._histograms = dict()

    def _get_histograms_mass(self, mass):
        name_dict = dict()
        process_list = list()
        name_list = list()
        print("Getting list of region {} ...".format(self.region_prefix))
        root_file = TFile(self.root_file_name)
        hash = gDirectory.GetListOfKeys()
        iter = hash.MakeIterator()
        key = iter.Next()
        while key:
            name = key.ReadObj().GetName()
            key = iter.Next()
            if self.region_prefix + self.masscut[str(mass)] + "_" + self.disc in name:
                if self.signal_prefix in name and self.signal_prefix + str(mass) not in name: continue
                if self.signal_prefix + str(mass) + "Py8" in name: continue
                name_list.append(name)
        root_file.cd("Systematics")
        hash = gDirectory.GetListOfKeys()
        iter = hash.MakeIterator()
        key = iter.Next()
        while key:
            name = key.ReadObj().GetName()
            key = iter.Next()
            if self.region_prefix + self.masscut[str(mass)] + "_" + self.disc in name:
                if self.signal_prefix in name and self.signal_prefix + str(mass) not in name: continue
                if self.signal_prefix + str(mass) + "Py8" in name: continue
                if "data" in name and self.disc + "_Sys" in name: continue
                if name.split('_Sys')[0] not in name_list: continue  # some inconsistency of nominal and systs
                name_list.append(name)
        root_file.Close()
        for name in name_list:
            process_list.append(self._process(name))
        process_list = list(set(process_list))
        print(mass, "  ", process_list)
        for process in process_list:
            name_dict[process] = [h for h in name_list if process in h]
        self._histograms[str(mass)] = name_dict

    def _process(self, name):
        return name.split('_')[0]

    def _get_histograms(self):
        from multiprocessing import Pool
        with Pool() as pool:
            pool.map(self._get_histograms_mass, self.masses)

    @property
    def histograms(self):
        return self._histograms

    def _save_histograms(self, pickle_file_name):
        import pickle
        with open(pickle_file_name, 'wb') as histograms_pickle:
            pickle.dump(self._histograms, histograms_pickle)

    def save_histograms(self, pickle_file_name):
        self._get_histograms()
        self._save_histograms(pickle_file_name)
