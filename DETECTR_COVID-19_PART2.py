from opentrons import protocol_api

metadata = {
    'protocolName': 'DETECTR COVID-19 Assay Part 2',
    'author': 'Tim S Dobbs',
    'source': 'Mammoth Biosciences',
    'link': 'https://mammoth.bio/wp-content/uploads/2020/03/Mammoth-Biosciences-A-protocol-for-rapid-detection-of-SARS-CoV-2-using-CRISPR-diagnostics-DETECTR.pdf'
    'description': """
                    Part 2 of an implementation of the Mammoth Biosciences DETECTR assay
                    to detect COVID-19 on the Opentrons OT2. This file is Part 2 - Run
                    DETECTR Reaction. This part should be run within 24 hours of running
                    Part 1, because it uses the LbCas12a RNP complex prepped there. It
                    assumes you have already extracted patient RNA and have samples
                    loaded in a 96-well plate.

                    Uses P10 pipette

                    Labware Placement:
                        Opentrons Temperature Module: Slot 5
                        Empty 96-well plate: In Temp Module
                        RNA samples on 96-well plate: Slot 6
                        LbCas12a RNP complex on 96-well plate, pre-prepped: Slot 2
                        Opentrons 24-slot Eppendorf tuberack for 2ml tubes: Slot 8
                        10ul pipette tiprack: Slot 9

                    Reagents are all in 2ml Eppendorf tubes in tuberack. We assume you
                    are running Part 2 right after Part 1, so positions are kept from
                    Part 1 and new reagents are added farther along the tuberack:
                        10X NEBuffer 2.1: A1
                        Nuclease-free water: D1
                        10X Isothermal Amplicatication Buffer (NEB): A3
                        100 mM MgSO4 (NEB): B3
                        10 mM dNTPs (NEB): C3
                        10X Primer Mix: D3
                        Bst 2.0 polymerase (NEB): A4
                        Warmstart RTx (NEB): B4
                    """,
    'apiLevel': '2.0'
    }

def run(protocol: protocol_api.ProtocolContext):
    temp_module = protocol.load_module('Temperature Module', 5)

    p10rack = protocol.load_labware('tiprack-10ul', 9)
    reagents = labware.load(
        'opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap', 8)
    prep_plate = temp_module.load_labware('nest_96_wellplate_200ul_flat')
    sample_plate = protocol.load_labware('nest_96_wellplate_200ul_flat', 6)
    LbCas_plate = protocol.load_labware('nest_96_wellplate_200ul_flat', 2)
    
    # Using 10ul pipette for precision
    p10 = protocol.load_instrument('p10_single', 'left', tipracks = [p10rack]) 


    base_recipe = { # reagent name: [postion on tuberack, uls to each sample]
                    '10X_IsoAmp_Buffer_NEB': ['A3', 2.5],
                    'MgSO4_NEB': ['B3', 1.13],
                    'dNTPs_NEB': ['C3', 3.5], 
                    '10X_Primer_Mix': ['D3', 2.5], 
                    'Bst_20_polymerase': ['A4', 1],
                    'Warmstart_RTx': ['B4', 0.5],
                    'water': ['D1', 3.87],
                    '10X_NEBuffer_21': ['A1', 80],
    }

    LbCas_vol_to_load = 2
    LbCas_recipe = { # reagent name: [postion on tuberack, uls to each sample]
                    'LbCas12a_RNP_complex_N-gene': ['A1', LbCas_vol_to_load],
                    'LbCas12a_RNP_complex_E-gene': ['A2', LbCas_vol_to_load],
                    'LbCas12a_RNP_complex_RNase_P': ['A3', LbCas_vol_to_load]
    }

    sample_vol_to_load = 5
    sample_plate_wells = ['A1']
    sample_plate_locations = [sample_plate.wells(well) for well in sample_plate_wells]

    prep_plate_wells = ['A1','A2','A3'] #1st: N-gene wells, 2nd: E-gene, 3rd: RNase P
    prep_plate_locations = [prep_plate.wells(well) for well in prep_plate_wells]

    buffer_recipe = base_recipe.[pop('10X_NEBuffer_21')] #move reporter to be used later


    #Begin Procedure ---------------------------------------------------------
    for reagent in base_recipe: #TODO Don't need for-loop, can do with .distribute only
        p10.distribute(base_recipe[reagent][1],                  #volume
                    reagents.wells(base_recipe[reagent][0]),     #source location
                    prep_plate_locations)                        #dest location

    for source_location in sample_plate_locations:
        p10.transfer(sample_vol_to_load,
                    source_location,
                    prep_plate_locations, #TODO Handle mutliple-sample case
                    mix_after=(2,10))

    temp_module.set_temperature(62) #robot pauses until temperature is reached
    p10.delay(minutes=20)

    #cooling before loading next reagents to not expose LbCas12a solution high temps
    temp_module.set_temperature(37)
    
    for gRNA in LbCas_recipe:
        p10.distribute(LbCas_recipe[gRNA][1],
                    LbCas_recipe[gRNA][0],
                    prep_plate_locations
                    )

    p10.transfer(buffer_recipe[1],
                buffer_recipe[0],
                prep_plate_locations,
                mix_after=(2,10))

    p10.delay(minutes=10)

    print("""Insert Milenia HybridDetect 1 (TwistDx) lateral flow strip directly into each sample
            Wait 2 minutes at room temp
            Observe results""")

    temp_module.set_temperature(25)
    temp_module.deactivate()



    