export default {
  "kind": "grid",
  "unit": "MW",
  "accent": "#58672a",
  "tint": "#eaf0dc",
  "staleHours": 7,
  "text": {
    "eyebrow": "ELECTRICITY DEMAND / ONTARIO",
    "intro": "Tomorrow’s demand, kept on the record. Compare each saved Ontario electricity forecast with the hourly demand reported afterward.",
    "entity-label": "Demand series",
    "bias-help": "Positive = forecast above reported demand",
    "cadence": "Collected every three hours. Saves hourly average demand forecasts for the next seven delivery dates and retrieves published hourly demand.",
    "observed-heading": "Reported demand (MW)",
    "target-heading": "Delivery hour starts (UTC)",
    "difference-heading": "Forecast − reported"
  },
  "method": [
    "The forecast is the AverageDemand series in IESO’s Adequacy3 report. It is compared with Ontario Demand in the Hourly Demand Report, in megawatts. We do not substitute peak demand or total market demand.",
    "IESO delivery days and report creation timestamps use Eastern Standard Time throughout the year (UTC−5). Hour 1 covers 00:00–01:00 EST. This page labels intervals by their start in UTC.",
    "Live receipts include only hours that had not started when collected. Published archive receipts are explicitly labelled: the versioned source report was issued before the target hour but retrieved later. Lead time uses capture time for live receipts and source issue time for archived reports.",
    "A reported demand value may itself be revised. Every collected version is retained; the dashboard uses the latest collected value. Mean absolute error and signed bias describe one selected receipt, not a representative performance ranking.",
    "The dashboard shows 14 days of collections; the complete dated receipt archive is retained. Data is provided by the Independent Electricity System Operator; this project is independent of IESO."
  ],
  "sources": [
    {
      "label": "IESO Adequacy3 forecast reports",
      "url": "https://reports-public.ieso.ca/public/Adequacy3/"
    },
    {
      "label": "Adequacy report field definitions",
      "url": "https://reports-public.ieso.ca/docrefs/helpfile/Adequacy3_h2.pdf"
    },
    {
      "label": "IESO Hourly Demand Report",
      "url": "https://reports-public.ieso.ca/public/Demand/"
    },
    {
      "label": "IESO data directory",
      "url": "https://www.ieso.ca/en/power-data/data-directory"
    }
  ],
  "chartCaption": "The line is this issue’s hourly average demand forecast. Dots show the latest collected Ontario demand for completed hours.",
  "tableNote": "Pending hours and missing reports are excluded from scores.",
  "id": "gridreceipt"
};
