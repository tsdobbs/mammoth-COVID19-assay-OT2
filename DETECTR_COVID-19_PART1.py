from opentrons import protocol_api

metadata = {
    'protocolName': 'DETECTR COVID-19 Assay Part 1',
    'author': 'Tim S Dobbs',
    'source': 'Mammoth Biosciences',
    'link': 'https://mammoth.bio/wp-content/uploads/2020/03/Mammoth-Biosciences-A-protocol-for-rapid-detection-of-SARS-CoV-2-using-CRISPR-diagnostics-DETECTR.pdf'
    'description': """
                    Part 1 of an implementation of the Mammoth Biosciences DETECTR assay
                    to detect COVID-19 on the Opentrons OT2. This file is Part 1 - Prep
                    of LbCas12a RNP complex. This material is used to report RNA present
                    in the test sample, and can be prepped up to 24 hours before running
                    the assay, as long as the sample is kept at 4 degrees C.

                    Uses P10 pipette

                    Labware Placement:
                        Opentrons Temperature Module: Slot 5
                        Empty 96-well plate: In Temp Module
                        Opentrons 24-slot Eppendorf tuberack for 2ml tubes: Slot 8
                        10ul pipette tiprack: Slot 9

                    Reagents are all in 2ml Eppendorf tubes in tuberack. Positions:
                        10X NEBuffer 2.1: A1
                        LbCas12a: B1
                        Reporter substrate: C1
                        Nuclease-free water: D1
                        N-gene gRNA: A2             #Note gRNA gets its own column
                        E-gene gRNA: B2
                        RNase P gRNA: C2
                    """,
    'apiLevel': '2.0'
    }

def run(protocol: protocol_api.ProtocolContext):
    temp_module = protocol.load_module('Temperature Module', 5)

    p10rack = protocol.load_labware('tiprack-10ul', 9)
    reagents = labware.load(
        'opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap', 8)
    prep_plate = temp_module.load_labware('nest_96_wellplate_200ul_flat')
    
    # Using 10ul pipette for precision
    p10 = protocol.load_instrument('p10_single', 'left', tipracks = [p10rack]) 


    base_recipe = { # reagent name: [postion on tuberack, uls to each sample]
                    '10X_NEBuffer_21': ['A1', 2],
                    'LbCas12a': ['B1', 1],
                    'reporter': ['C1', 1], #TODO Need correct volume
                    'water': ['D1', 15.75]
    }
    gRNA_uls_to_pipette = 1.25
    gRNA_recipe = {# reagent name: [postion on tuberack, uls to each sample]
                    'N-gene_gRNA': ['A2', gRNA_uls_to_pipette],
                    'E-gene_gRNA': ['B2', gRNA_uls_to_pipette],
                    'RNase_P_gRNA': ['C2', gRNA_uls_to_pipette]
    }

    prep_plate_wells = ['A1','A2','A3'] #1st: N-gene wells, 2nd: E-gene, 3rd: RNase P
    prep_plate_locations = [prep_plate.wells(well) for well in prep_plate_wells]

    reporter_recipe = base_recipe.[pop('reporter')] #move reporter to be used later


    #Begin Procedure ---------------------------------------------------------
    for reagent in base_recipe: #TODO Don't need for-loop, can do with .distribute only
        p10.distribute(base_recipe[reagent][1],                  #volume
                    reagents.wells(base_recipe[reagent][0]),     #source location
                    prep_plate_locations)                        #dest location

    for group, gRNA in enum(gRNA_recipe):
        p10.transfer(gRNA_recipe[gRNA][1],                      #volume
                        reagents.wells(base_recipe[gRNA][0]),   #source location
                        prep_plate_locations[group],            #dest location
                        mix_after=(2,10))                       #ensure good mixing

    temp_module.set_temperature(37) #robot pauses until temperature is reached
    p10.delay(minutes=30)

    temp_module.set_temperature(4)

    # Add reporter substrate to final concentration of 500nM
    #p10.distribute(reporter_recipe[1], reporter_recipe[0], prep_plate_locations)

    