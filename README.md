# QC_virus_samples

## Overview

This repository contains a small Python script for monitoring the quality of weekly virus sequencing samples.

The sequencing pipeline produces a quality metrics file for all samples. The aim here is to identify whether samples from a particular origin are failing QC more frequently than expected and flag this to the user.

## How I approached the problem

I interpreted a sample as failed when either:

- less than 95% of the reference genome is covered, or
- the existing `qc_pass` field is `FALSE`.

The origin of each sample is encoded as the second character of the sample name. I extract this dynamically rather than defining the currently known origins (`C`, `T`, `D`, `N`), since future datasets may contain additional origins.

For each origin, the script calculates:

- number of samples analysed
- number of failed samples
- percentage of failed samples

If more than 10% of samples from an origin fail QC, the script raises a warning.

## Workflow

samples.txt
→ validate input
→ extract sample origin
→ identify failed samples
→ summarise failures by origin
→ calculate failure percentage
→ report results and warnings

## Usage

Run:

```bash
python qc_virus_samples.py samples.txt

