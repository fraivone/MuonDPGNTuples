import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as VarParsing
from Configuration.StandardSequences.Eras import eras
from Configuration.AlCa.GlobalTag import GlobalTag

import subprocess
import sys

options = VarParsing.VarParsing()

options.register('globalTag',
                 #'111X_dataRun3_Express_v4',
                 #"110X_mcRun3_2021_realistic_v9",
                 '112X_mcRun3_2021_realistic_v10',
                 #'auto:phase1_2021_realistic',
                 #'111X_upgrade2018_realistic_v1', #default value
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 "Global Tag")

options.register('nEvents',
                 #1000, #to run on a sub-sample
                 -1, #default value
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.int,
                 "Maximum number of processed events")

options.register('isMC',
                 True, #default value
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.bool,
                 "Maximum number of processed events")



options.register('inputFolder',
                 "/lustre/cms/store/user/gmilella/Run3Summer19GS-step0/CRAB3_MC_ZMuMu_RECO/201111_170703/0000/",
                 #"/eos/user/f/fivone/GEMNTuples/MWGR/338714/0000/",
                 #"/eos/cms//store/express/Commissioning2020/ExpressCosmics/FEVT/Express-v1/000/338/714/00000/",
                 #"/eos/user/f/fivone/GEMNTuples/MC/Input/",
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 "EOS folder with input files")
options.register('inputFile',
                 "",
                 #"/eos/user/f/fivone/GEMNTuples/MWGR/338714/0000/",
                 #"/eos/cms//store/express/Commissioning2020/ExpressCosmics/FEVT/Express-v1/000/338/714/00000/",
                 #"/eos/user/f/fivone/GEMNTuples/MC/Input/",
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 "File name")


options.register('secondaryInputFolder',
                 '', #default value
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 "EOS folder with input files for secondary files")

options.register('ntupleName',
                 #'./MuDPGNtuple_11_1_2_patch2.root',
                 "GEMNtuples.root",
                 #'/lustre/cms/store/user/gmilella/Cosmics/CONDOR_gem_dpg_ntuple_mwgr4_run337973_eos/MuDPGNtuple_MWGR4eos.root',
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 "Folder and name for output ntuple")

options.parseArguments()


process = cms.Process("MUNTUPLES",eras.Run3)#Run2_2018)

process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.load('Configuration.StandardSequences.Services_cff')
process.load('FWCore.MessageService.MessageLogger_cfi')


process.options   = cms.untracked.PSet( wantSummary = cms.untracked.bool(True))

numberOfThreads = cms.untracked.uint32(4)
process.MessageLogger.cerr.FwkReport.reportEvery = 100
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(options.nEvents))

#process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')

process.GlobalTag.globaltag = cms.string(options.globalTag)

process.source = cms.Source("PoolSource",
                            fileNames = cms.untracked.vstring(),
                            secondaryFileNames = cms.untracked.vstring()
)


if "eos/cms" in options.inputFolder:
    files = subprocess.check_output(['ls', options.inputFolder])
    files = files.split()
    process.source.fileNames = ["file:"+options.inputFolder+f for f in files]

elif "lustre/cms/store" in options.inputFolder:
    files = subprocess.check_output(['ls', options.inputFolder])
    files = files.split()
    files = [ f for f in files if options.inputFile in f]
    print files
    process.source.fileNames = ["file://" + options.inputFolder + "/" + f for f in files]

elif "store/" in options.inputFolder:
    files = subprocess.check_output(['xrdfs', 'root://xrootd-cms.infn.it/', 'ls', options.inputFolder])
    process.source.fileNames = ["root://xrootd-cms.infn.it//" +f for f in files.split()]

else:
    files = subprocess.check_output(['ls', options.inputFolder])
    files = files.split()
    process.source.fileNames = ["file://" + options.inputFolder + "/" + f for f in files]

if options.secondaryInputFolder != "" :
    files = subprocess.check_output(["ls", options.secondaryInputFolder])
    process.source.secondaryFileNames = ["file://" + options.secondaryInputFolder + "/" + f for f in files.split()]
 

process.TFileService = cms.Service('TFileService',
                                   fileName = cms.string("GEMntuples_"+options.inputFile)
    )


process.load('Configuration/StandardSequences/GeometryRecoDB_cff')
process.load("Configuration.StandardSequences.MagneticField_cff")

process.load("TrackingTools/TransientTrack/TransientTrackBuilder_cfi")
process.load('TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorAny_cfi')
process.load('TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorAlong_cfi')
process.load('TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorOpposite_cfi')

process.load('Configuration.StandardSequences.RawToDigi_Data_cff')
process.load('MuDPGAnalysis.MuonDPGNtuples.muNtupleProducer_cfi')

process.muNtupleProducer.isMC = cms.bool(options.isMC)

process.p = cms.Path(process.muNtupleProducer)


