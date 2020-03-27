# Implementation of Mammoth Bioscience's DETECTR assay for COVID-19

This is an implementation of the protocol detailed in Mammoth Bioscience's
white paper, included in this repo. It consists of 2 parts

## Part 1 - Prep of LbCas12a RNP complex
This material is used to report RNA present in the test sample, and can
be prepped up to 24 hours before running the assay, as long as the sample
is kept at 4 degrees C.

## Part 2 - Run DETECTR Reaction
This part should be run within 24 hours of running Part 1, because it
uses the LbCas12a RNP complex prepped there. It assumes you have
already extracted patient RNA and have samples loaded in a 96-well plate.

Use the Opentrons app to upload Part 1, then do the same for Part 2 within
24 hours.

Read the individual files for documentation of what kind of labware should
be used and where it should be placed on the robot's deck.

Contributions to make this more efficient or expand capacity welcomed!
