[aswg-api](https://github.com/PeterEckmann1/aswg-api) provides:

 * A set of tools for analyzing the reproducibility, transparency, and quality of scientific manuscripts
 * HTML reports, summarizing results from these tools, for each analyzed manuscript
 * An API for fetching data about reports of COVID-19 preprints
 
See reports for COVID-19 preprints at our Twitter account, [@SciScoreReports](https://twitter.com/SciscoreReports).  
Visit our [website](https://scicrunch.org/ASWG), or read more about why we developed these tools in [Research Information](https://www.researchinformation.info/analysis-opinion/paying-it-forward-publishing-your-research-reproducibly).

## API Usage

All API calls are made to the URL `?`.

### GET /recent_reports

Parameters:
```
key    : API key
cursor : first ID to fetch from database
```

Returns the 50 most recent preprints that have reports starting from `cursor`. To iterate through the entire database, use a cursor value of 0, 50, 100, etc.  
Each result will have the following fields:

Field                         |  Description
---                           |  ---
`doi`                         |  DOI of the preprint
`report_generated_timestamp`  |  timestamp of when the report was generated
`url`                         |  URL of the preprint
`annotation_link`             |  link to the hypothes.is annotation
`html_report`                 |  the final report in HTML format

Other fields include preprint metadata and specific results from each of the tools.