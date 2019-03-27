#############################################################################
##  © Copyright CERN 2018. All rights not expressly granted are reserved.  ##
##                 Author: Gian.Michele.Innocenti@cern.ch                  ##
## This program is free software: you can redistribute it and/or modify it ##
##  under the terms of the GNU General Public License as published by the  ##
## Free Software Foundation, either version 3 of the License, or (at your  ##
## option) any later version. This program is distributed in the hope that ##
##  it will be useful, but WITHOUT ANY WARRANTY; without even the implied  ##
##     warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    ##
##           See the GNU General Public License for more details.          ##
##    You should have received a copy of the GNU General Public License    ##
##   along with this program. if not, see <https://www.gnu.org/licenses/>. ##
#############################################################################
import os
import pickle
import pandas as pd
from root_numpy import fill_hist # pylint: disable=import-error, no-name-in-module
from ROOT import TFile, TH1F # pylint: disable=import-error, no-name-in-module
from machine_learning_hep.selectionutils import getnormforselevt


def extractmasshisto(data_config, data, case, useml, mcordata):
    binmin = data_config["analysis"]["binmin"]
    binmax = data_config["analysis"]["binmax"]
    invmassbins = data[case]["invmassbins"]
    invmasslow = data[case]["invmasslow"]
    invmasshigh = data[case]["invmasshigh"]
    namefilereco_ml_tot = data[case]["files_names"]["namefile_reco_skim_ml_tot"]
    namefilereco_std_tot = data[case]["files_names"]["namefile_reco_skim_std_tot"]
    namefile_evt_skim_tot = data[case]["files_names"]["namefile_evt_skim_tot"]
    outputdirfin = data[case]["output_folders"]["pkl_final"][mcordata]
    modelname = data_config["analysis"]["modelname"]

    namefilereco_ml_tot = os.path.join(outputdirfin, namefilereco_ml_tot)
    namefilereco_std_tot = os.path.join(outputdirfin, namefilereco_std_tot)
    namefile_evt_skim_tot = os.path.join(outputdirfin, namefile_evt_skim_tot)
    probcutoptimal = data_config["analysis"]["probcutoptimal"]

    index = 0
    histomassall = []
    for imin, imax in zip(binmin, binmax):
        df = pd.DataFrame()
        if useml == 0:
            namefilereco_std_tot = \
            namefilereco_std_tot.replace(".pkl", "%d_%d.pkl" % (imin, imax))
            df = pickle.load(open(namefilereco_std_tot, "rb"))
        if useml == 1:
            namefilereco_ml_tot = \
                namefilereco_ml_tot.replace(".pkl", "%d_%d.pkl" % (imin, imax))
            df = pickle.load(open(namefilereco_ml_tot, "rb"))
            sel_ml = "y_test_prob%s>%s" % (modelname, probcutoptimal)
            df = df.query(sel_ml)
        array_inv_mass_sel = df.inv_mass.values
        namehisto = "h_invmass%d_%d" % (imin, imax)
        h_invmass = TH1F(namehisto, "", invmassbins, invmasslow, invmasshigh)
        fill_hist(h_invmass, array_inv_mass_sel)
        histomassall.append(h_invmass)
        index = index + 1

    df_evt = pickle.load(open(namefile_evt_skim_tot, "rb"))
    print("events for normalisation", getnormforselevt(df_evt))

    myfile = TFile.Open("roottotal%s%s.root" % (mcordata, useml), "recreate")
    myfile.cd()
    for index, _ in enumerate(binmin):
        histomassall[index].Write()
    h_invmass.Write()
    myfile.Close()