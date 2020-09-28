The [Automated Screening Working Group](https://scicrunch.org/ASWG) (ASWG) is a group of software engineers and biologists 
passionate about improving scientific manuscripts on a large scale. We aim to automatically review and provide 
customized reports for all manuscripts published in the biomedical sciences. Our members have created tools that 
check for common problems in scientific manuscripts, including information needed to improve transparency and 
reproducibility. Read more about us in [Research Information](https://www.researchinformation.info/analysis-opinion/paying-it-forward-publishing-your-research-reproducibly).

<h1>aswg-pipeline</h1>

This repository combines tools from our members into a single unified pipeline, and handles all stages of review, from 
fetching the manuscripts, publishing the reports on hypothes.is, and broadcasting the reports on Twitter. Currently, 
we are only analyzing COVID-19 preprints published on bioRxiv/medRxiv. All results are dumped in a PostgreSQL database.

<h2>Summary</h2>

Each stage of the pipeline is containerized with Docker, and orchestrated with docker-compose. The pipeline covers
the following stages:

1.  `find-new` searches for new preprints published to bioRxiv/medRxiv about COVID-19.
2.  `extractor` downloads and extracts relevant sections from the preprint's PDF format.
3.  Various tools are run on the text and images extracted:
    * [`barzooka`](https://github.com/NicoRiedel/barzooka) looks for bar graphs erroneously used for continuous data.
    * [`jetfighter`](https://github.com/NicoRiedel/barzooka) looks for poor colormaps, which may obscure detail or be 
    inacessible to colorblind readers.
    * [`limitation-recognizer`](https://github.com/kilicogluh/limitation-recognizer) looks for self-acknowledged 
    limitation sentences.
    * [`oddpub`](https://github.com/kilicogluh/limitation-recognizer) looks for the presence of open code and data.
    * [`sciscore`](https://sciscore.com/) reviews methods sections for rigor criteria and uniqueness of 
    identified resources.
    * [`trial-identifier`](https://github.com/bgcarlisle/PreprintScreening) finds and resolves clinical trial numbers.
4. `release` combines all results into one HTML report, publishes the report on hypothes.is, and sends a Tweet
referencing the report ([@SciScoreReports](https://twitter.com/SciscoreReports)).

<h2>Usage</h2>
With Docker v19 and docker-compose v1.26, run

```
docker-compose up
```

Each manuscript takes about one minute to analyze.

If running the tool for the first time, run `docker-compose build` to build the container images.

`barzooka` and `jetfighter` tend to take longer than the other tools, so for optimal performance,
append `--scale barzooka=2` and `--scale jetfighter=2` to the `docker-compose` command. To analyze how each tool
is performing, run `plot_performance_data.py`with `matplotlib` installed.

<h2>Missing files</h2>

Because of GitHub's 100MB file limit, a few model files could not be included in the repository. These files are:

* `barzooka/src/barzooka.pkl`
* `extractor/src/methods-model.bin`
* `limitation-recognizer/src/CombinedPreprintLimitationRecognizer.jar`
* `sciscore/src/pt_model.joblib`
* `sciscore/src/pt_vocab.ser`

There is also an `auth.env` file that is not included, which contains various API keys and tokens needed for the pipeline to run.
For access to these files, contact petereckmann(at)gmail(dot)com.