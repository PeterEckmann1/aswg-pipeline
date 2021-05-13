# aswg-pipeline

We are the [Automated Screening Working Group](https://scicrunch.org/ASWG), a group of researchers aiming to improve 
scientific manuscripts on a large scale. Our pipeline combines tools that check for common problems in scientific
manuscripts to produce a single, integrated report for any paper. Currently, we are using the pipeline to
evaluate COVID-19 preprints from [medRxiv](https://www.medrxiv.org/) and [bioRxiv](https://www.biorxiv.org/). See our
publicly available reports, generated with this pipeline, at [@SciScoreReports](https://twitter.com/SciscoreReports).

# Overview

Our pipeline offers a unified framework for retrieval and preprocessing of papers, a pluggable interface for tools,
and formatting and public release of tool results as a unified report. While we encourage developers to experiment with 
and add their own tools, we are currently using the following tools in our production pipeline (that publishes to our
Twitter account):

 * [JetFighter](https://github.com/smsaladi/jetfighter)
 * [limitation-recognizer](https://github.com/kilicogluh/limitation-recognizer)
 * [trial-identifier](https://github.com/bgcarlisle/TRNscreener)
 * [SciScore](https://sciscore.com/)
 * [Barzooka](https://github.com/NicoRiedel/barzooka)
 * [ODDPub](https://github.com/quest-bih/oddpub)
 * [scite Reference Check](https://medium.com/scite/reference-check-an-easy-way-to-check-the-reliability-of-your-references-b2afcd64abc6)
 * [rtransparent](https://github.com/serghiou/rtransparent)

## Publications

[*Automated screening of COVID-19 preprints: can we help authors to improve transparency and reproducibility?*](https://www.nature.com/articles/s41591-020-01203-7) in *Nature Medicine*.