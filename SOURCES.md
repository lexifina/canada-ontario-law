# Sources and legal basis

## Source

e-Laws, the Government of Ontario's online database of statutes and regulations: https://www.ontario.ca/laws. Each
statute's "Versions" tab lists its point-in-time consolidations ("Historical version for the period ... to ...").
The pages are drawn from a JSON interface at https://www.ontario.ca/laws/api/v2/legislation, which this build reads:

- `en/act-versions/statute/<id>`: the versions of an act, with the first and last day of each;
- `en/doc-search/statute/<id>[/v<n>]`: the full text of one version (HTML), with the citations ending each
  subsection and, since 2016, each section's "Section Amendments with date in force (d/m/y)";
- `en/doc-search/statute/S<yy><chapter>`: an amending act as enacted (its title and "Assented to" day).

## Legal basis for reuse

Copyright in Ontario statutes is held by the King's Printer for Ontario. Its "Policy on copyright on legal materials"
(https://www.ontario.ca/page/copyright-information, updated September 29, 2022) permits any person to reproduce the
text of statutes and regulations without permission and without charge, on three conditions, which this repository
meets:

1. reproduce accurately: every version is checked against e-Laws (REPRODUCE.md);
2. acknowledge Crown copyright as "(c) King's Printer for Ontario, 20__" (README.md, LICENSE);
3. state that a reproduction that is not an official copy under the Legislation Act, 2006 is not an official version
   (README.md, LICENSE).

The ontario.ca terms of use (https://www.ontario.ca/page/terms-use) refer to that page for reuse and do not forbid
automated access. robots.txt (https://www.ontario.ca/robots.txt) asks for `Crawl-delay: 1`, disallows no path read
here, and has no rule for AI agents; the build makes one request at a time, at least 1.1 seconds apart.
