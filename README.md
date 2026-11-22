# Grid Receipt

Keep Ontario hourly average electricity-demand forecasts and compare them with subsequently reported demand.

Open https://coolcode.ca/gridreceipt/.

<!-- coolcode:guide -->
Select a saved forecast issue. Positive error means the forecast exceeded reported demand. Archived source issues are marked separately from forecasts captured live; both use the same hourly average demand series.
<!-- /coolcode:guide -->

## Collection

No API key is required. Forecasts come from `OntarioDemand/AverageDemand` in IESO Adequacy3 XML. Outcomes come from the `Ontario Demand` column in the Hourly Demand CSV. Peak demand, ForecastOntDemand (which can switch to peak), and Market Demand are deliberately excluded. All IESO delivery hours and CreatedAt values are fixed EST (UTC−5), even in summer. Hour 1 begins at 00:00 EST. Forecast points must be future at capture time. The one-time `--bootstrap` option imports the earliest available versioned reports for the preceding three delivery days, labelled `published_archive`; only points after the source issue time are included.

Schedule: **Every three hours at minute 41 (UTC)**. GitHub schedules are best effort, not a precise timer. Scheduled and manual runs collect; code pushes and pull requests only validate/build the saved archive.

```sh
python3 scripts/collect.py
node --test tests/*.test.mjs
python3 -m unittest discover -s tests -v
python3 scripts/build.py
```

The default build is offline. Collectors validate before saving; failed collection does not replace the good deployment. All dated normalized receipts are permanent tracked files under `archive/YYYY-MM/*.json.gz`. Each includes the capture time, source URL, SHA-256 of the downloaded response, selected values and provenance. These files preserve the selected data, not necessarily the full upstream response. Identical receipts deduplicate; old receipts are never overwritten. No Zenodo configuration is needed.

The dashboard loads the most recent 14 days of captures. Older receipts remain downloadable through `data/archive.json` and retained in Git history. The archive is the durable record; Actions artifact retention is unrelated. Observation revisions remain in their dated source receipts; the dashboard uses the latest reading (or earliest stop encounter for transit). CSV export covers the selected receipt and filter. JSON and individual compressed receipt downloads preserve source links.

## Interpretation

A blank score means outcomes are missing, not zero error. A selected receipt's mean absolute difference is the mean of absolute matched differences; signed bias retains direction. Different receipts can refer to the same outcome, so points across receipts are not independent events. Live lead time is measured from capture to target. Historical IESO issues use source issue time and are explicitly labelled.

## Publishing and monitoring

The main workflow checks models, collection logic, the static builder and browser behaviour, then commits new source receipts before deploying. Set repository Pages source to **GitHub Actions**. PRs cannot collect, commit or deploy. No Cloudflare Worker changes are required.

Optionally add an Actions secret **HEALTHCHECKS_PING_URL**. Scheduled/manual collection sends start/success/failure pings; the collector itself does not send email or accuracy reports. Match the Healthchecks schedule to the cron above and allow enough grace for GitHub queue delays (90 minutes is reasonable). A success ping confirms archive collection and commit; it does not certify forecast accuracy or Pages deployment.

Optional monitoring is inactive without the secret. The site reports the last successful collection and marks it overdue when stale.

## Privacy

Visitors load public saved data from this site. Filtering and CSV export run in the browser without accounts, storage or upstream API calls. The shared CoolCode counter records aggregate page opens without filter values. Source collection happens in GitHub Actions.

## Sources and attribution

IESO data directory: https://www.ieso.ca/en/power-data/data-directory

Field definitions: https://reports-public.ieso.ca/docrefs/helpfile/Adequacy3_h2.pdf

Data is provided by the Independent Electricity System Operator. This project is independent of IESO. Outcomes are reported operational demand and may be revised; they are not an immutable final settlement series.

## Software

Application code is MIT licensed. Upstream datasets retain their original licences. Browser screenshots are saved as seven-day CI artifacts; all data receipts remain in the repository.
