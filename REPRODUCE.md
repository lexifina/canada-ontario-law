# How this history was made, and how to make it again

This file records exactly how the repository was built: the sources, the commands, the software, the decisions made
by hand, and what an AI model did and did not do. The build writes it, so it describes the build that made this
commit.

## Short version

```sh
git clone https://github.com/lexifina/canada-ontario-law && cd canada-ontario-law
pip install lxml
python -X utf8 tools/build.py --repo ../rebuilt --today 2026-10-29
git -C ../rebuilt rev-parse main        # the same hash as this repository's main
python -X utf8 tools/check_repo.py --repo ../rebuilt --no-record
python -X utf8 tools/test_repo.py --repo ../rebuilt
```

`tools/build.py` needs Python 3.12 or later with `lxml`, and git. It reads e-Laws (or its own cache, `.cache/` next to
the script) and writes this repository into `--repo`, which must be empty or a git repository. With the same data and
the same `--today` it gives the same commits with the same hashes. `data/versions.json` lists every version it read
with the sha256 of the API answer, so a rebuild can show it read the same bytes; e-Laws may change its answers, and then
the hashes change too.

## Sources

All legal text and all information about versions and amending acts come from **e-Laws** (www.ontario.ca/laws), the
Government of Ontario's database of statutes and regulations, published by the King's Printer for Ontario. Nothing was
typed in, summarised or rewritten. The pages of e-Laws are drawn in the browser from a JSON interface at
`https://www.ontario.ca/laws/api/v2/legislation`; the build reads the same answers the pages read. It read
1288 version lists, 10063 versions and 893 amending acts as enacted:

| What | Where |
| --- | --- |
| The list of every consolidated statute, current and "Repealed / Revoked / Spent" (`tools/list_all.py`, saved as `data/acts.json`) | `/laws/api/v2/legislation/en/browse-search?text=&selection=<current or rrs>&result=statute&page=<n>&pageSize=50&sort=Newest` |
| Each act's point-in-time versions (the "Versions" tab), with the days each applies from and to | `/laws/api/v2/legislation/en/act-versions/statute/<id>` |
| The full text of each version (the same HTML the page shows), with the citations that end each subsection and, since 2016, each section's "Section Amendments with date in force (d/m/y)" | `/laws/api/v2/legislation/en/doc-search/statute/<id>/v<n>` (the current version without `/v<n>`), listed with sha256 in `data/versions.json` |
| Each amending act's title and day of Royal Assent (707 of 974 laws) | `/laws/api/v2/legislation/en/doc-search/statute/S<yy><chapter>` |

| Act | Title | Folder | Versions | In force from | Files today |
| --- | --- | --- | ---: | --- | ---: |
| 00a03 | Arthur Wishart Act (Franchise Disclosure), 2000 | `00a03/` | 5 | 2001-06-29 to 2020-09-01 | 17 |
| 00b23 | Back to School Act (Hamilton-Wentworth District School Board), 2000 | `00b23/` | 2 | 2000-11-21 to 2009-12-15 | 0 |
| 00c01 | Christopher’s Law (Sex Offender Registry), 2000 | `00c01/` | 22 | 2001-04-23 to 2026-07-01 | 21 |
| 00c43 | City of Kawartha Lakes Act, 2000 | `00c43/` | 1 | 2003-01-01 to 2003-01-01 | 13 |
| 00d33 | Domestic Violence Protection Act, 2000 | `00d33/` | 3 | 2002-11-26 to 2009-05-14 | 0 |
| 00d34 | Deaf-Blind Awareness Month Act, 2000 | `00d34/` | 1 | 2000-12-21 to 2000-12-21 | 4 |
| 00e17 | Electronic Commerce Act, 2000 | `00e17/` | 5 | 2000-10-16 to 2020-05-15 | 36 |
| 00e26 | Environmental Review Tribunal Act, 2000 | `00e26/` | 8 | 2000-12-06 to 2021-06-01 | 0 |
| 00e41 | Employment Standards Act, 2000 | `00e41/` | 84 | 2002-11-26 to 2026-01-01 | 260 |
| 00f31 | Firefighters’ Memorial Day Act, 2000 | `00f31/` | 1 | 2000-12-12 to 2000-12-12 | 4 |
| 00g07 | German Pioneers Day Act, 2000 | `00g07/` | 1 | 2000-06-23 to 2000-06-23 | 4 |
| 00i37 | Imitation Firearms Regulation Act, 2000 | `00i37/` | 3 | 2001-03-21 to 2020-10-08 | 8 |
| 00o06 | Ontario Association of Former Parliamentarians Act, 2000 | `00o06/` | 1 | 2000-06-08 to 2000-06-08 | 16 |
| 00o19 | OC Transpo Payments Act, 2000 | `00o19/` | 1 | 2000-10-16 to 2000-10-16 | 4 |
| 00p04 | Parental Responsibility Act, 2000 | `00p04/` | 7 | 2000-08-15 to 2021-04-19 | 15 |
| 00p13 | Professional Geoscientists Act, 2000 | `00p13/` | 4 | 2003-03-31 to 2021-10-19 | 46 |
| 00p18 | Professional Foresters Act, 2000 | `00p18/` | 7 | 2001-05-01 to 2021-12-02 | 68 |
| 00p36 | Post-secondary Education Choice and Excellence Act, 2000 | `00p36/` | 5 | 2003-04-01 to 2015-01-01 | 27 |
| 00r20 | Racing Commission Act, 2000 | `00r20/` | 5 | 2000-12-15 to 2016-04-01 | 0 |
| 00s27 | Social Housing Reform Act, 2000 | `00s27/` | 15 | 2003-01-01 to 2012-01-01 | 0 |
| 00s44 | St. Clair Parks Commission Act, 2000 | `00s44/` | 4 | 2003-01-01 to 2008-10-10 | 0 |
| 00t05 | Town of Moosonee Act, 2000 | `00t05/` | 3 | 2001-01-01 to 2021-06-01 | 9 |
| 00t08 | Tartan Act, 2000 | `00t08/` | 2 | 2000-06-23 to 2006-06-22 | 5 |
| 00t16 | Technical Standards and Safety Act, 2000 | `00t16/` | 20 | 2001-06-29 to 2022-07-01 | 85 |
| 00w26 | Wine Content and Labelling Act, 2000 | `00w26/` | 8 | 2001-01-01 to 2021-11-29 | 0 |
| 01a10 | Ambulance Services Collective Bargaining Act, 2001 | `01a10/` | 6 | 2002-11-26 to 2019-03-26 | 32 |
| 01b01 | Back to School Act (Toronto and Windsor), 2001 | `01b01/` | 2 | 2001-04-27 to 2009-12-15 | 0 |
| 01b19 | Brain Tumour Awareness Month Act, 2001 | `01b19/` | 1 | 2001-12-05 to 2001-12-05 | 4 |
| 01c22 | Celebration of Portuguese Heritage Act, 2001 | `01c22/` | 1 | 2001-12-05 to 2001-12-05 | 5 |
| 01c33 | Community Care Access Corporations Act, 2001 | `01c33/` | 17 | 2001-12-14 to 2017-11-01 | 0 |
| 01f05 | Franco-Ontarian Emblem Act, 2001 | `01f05/` | 2 | 2001-06-29 to 2020-09-24 | 6 |
| 01f20 | Food Safety and Quality Act, 2001 | `01f20/` | 16 | 2001-12-05 to 2024-04-01 | 61 |
| 01g02 | Good Samaritan Act, 2001 | `01g02/` | 1 | 2001-04-27 to 2001-04-27 | 5 |
| 01g23 | GO Transit Act, 2001 | `01g23/` | 13 | 2003-12-18 to 2009-05-14 | 0 |
| 01h04 | Horse Riding Safety Act, 2001 | `01h04/` | 1 | 2001-06-29 to 2001-06-29 | 7 |
| 01h23 | Highway 407 East Completion Act, 2001 | `01h23/` | 4 | 2002-11-26 to 2011-12-31 | 0 |
| 01i18 | Improving Customer Service for Road Users Act, 2001 | `01i18/` | 3 | 2001-12-14 to 2019-07-01 | 19 |
| 01m25 | Municipal Act, 2001 | `01m25/` | 110 | 2004-01-01 to 2026-06-02 | 642 |
| 01o03 | Oak Ridges Moraine Protection Act, 2001 | `01o03/` | 1 | 2001-11-17 to 2001-11-17 | 8 |
| 01o31 | Oak Ridges Moraine Conservation Act, 2001 | `01o31/` | 8 | 2003-01-01 to 2023-12-06 | 28 |
| 01o32 | Ontarians with Disabilities Act, 2001 | `01o32/` | 16 | 2003-01-01 to 2025-01-01 | 23 |
| 01p16 | Patient Restraints Minimization Act, 2001 | `01p16/` | 3 | 2001-06-29 to 2023-05-18 | 14 |
| 01r28 | Civil Remedies Act, 2001 | `01r28/` | 15 | 2003-07-01 to 2024-04-01 | 54 |
| 01s27 | Supply Act, 2001 | `01s27/` | 2 | 2001-12-12 to 2015-03-31 | 0 |
| 01s29 | South Asian Heritage Act, 2001 | `01s29/` | 1 | 2001-12-14 to 2001-12-14 | 5 |
| 02a16 | Agricultural Employees Protection Act, 2002 | `02a16/` | 2 | 2003-06-17 to 2019-04-03 | 22 |
| 02b20 | Back to School Act (Simcoe Muskoka Catholic District School Board), 2002 | `02b20/` | 2 | 2002-11-26 to 2009-12-15 | 0 |
| 02c11 | City of Toronto Labour Disputes Resolution Act, 2002 | `02c11/` | 2 | 2002-07-11 to 2009-12-15 | 0 |
| 02c30 | Consumer Protection Act, 2002 | `02c30/` | 38 | 2002-12-13 to 2025-12-11 | 143 |
| 02c31 | Collision Repair Standards Act, 2002 | `02c31/` | 2 | 2002-12-13 to 2012-12-31 | 0 |
| 02c34 | Cabinet Ministers’ and Opposition Leaders’ Expenses Review and Accountability Act, 2002 | `02c34/` | 7 | 2002-12-13 to 2024-12-31 | 20 |
| 02d14 | Declarations of Death Act, 2002 | `02d14/` | 2 | 2002-11-19 to 2005-03-09 | 12 |
| 02f33 | Funeral, Burial and Cremation Services Act, 2002 | `02f33/` | 18 | 2002-12-13 to 2025-12-11 | 119 |
| 02h03 | Hydro One Inc. Directors and Officers Act, 2002 | `02h03/` | 1 | 2002-06-27 to 2002-06-27 | 26 |
| 02h10 | Heritage Hunting and Fishing Act, 2002 | `02h10/` | 3 | 2002-06-27 to 2018-01-01 | 6 |
| 02h26 | Highway Memorials for Fallen Police Officers Act, 2002 | `02h26/` | 1 | 2002-12-13 to 2002-12-13 | 4 |
| 02i13 | Interjurisdictional Support Orders Act, 2002 | `02i13/` | 9 | 2003-03-31 to 2026-05-01 | 60 |
| 02i18 | International Interests in Mobile Equipment Act (Aircraft Equipment), 2002 | `02i18/` | 3 | 2002-11-26 to 2017-11-14 | 18 |
| 02l24 | Limitations Act, 2002 | `02l24/` | 34 | 2004-01-01 to 2024-12-04 | 30 |
| 02m30 | Motor Vehicle Dealers Act, 2002 | `02m30/` | 18 | 2002-12-13 to 2023-12-04 | 51 |
| 02n04 | Nutrient Management Act, 2002 | `02n04/` | 22 | 2003-07-01 to 2024-04-01 | 69 |
| 02o08e | Ontario College of Art & Design University Act, 2002 | `02o08e/` | 10 | 2004-01-01 to 2023-12-04 | 24 |
| 02o08f | Ontario Colleges of Applied Arts and Technology Act, 2002 | `02o08f/` | 8 | 2003-04-01 to 2021-10-19 | 14 |
| 02o22 | Ontario Strategic Infrastructure Financing Authority Act, 2002 | `02o22/` | 5 | 2003-03-27 to 2006-07-17 | 0 |
| 02p02 | Prohibiting Profiting from Recounting Crimes Act, 2002 | `02p02/` | 8 | 2003-07-01 to 2022-01-01 | 19 |
| 02p08 | Province of Ontario Savings Office Privatization Act, 2002 | `02p08/` | 8 | 2002-11-15 to 2026-04-24 | 20 |
| 02r05 | Rescuing Children from Sexual Exploitation Act, 2002 | `02r05/` | 4 | 2002-06-27 to 2012-12-31 | 0 |
| 02r30 | Trust in Real Estate Services Act, 2002 | `02r30/` | 31 | 2002-12-13 to 2023-12-01 | 64 |
| 02s08 | SkyDome Act (Bus Parking), 2002 | `02s08/` | 4 | 2002-09-27 to 2026-04-24 | 0 |
| 02s29 | Sustainable Water and Sewage Systems Act, 2002 | `02s29/` | 4 | 2002-12-13 to 2012-12-31 | 0 |
| 02s32 | Safe Drinking Water Act, 2002 | `02s32/` | 33 | 2003-10-01 to 2026-06-02 | 179 |
| 02s36 | Supply Act, 2002 | `02s36/` | 2 | 2002-12-13 to 2015-03-31 | 0 |
| 02t17 | Territorial Division Act, 2002 | `02t17/` | 1 | 2003-01-01 to 2003-01-01 | 7 |
| 02t22 | Tax Incentive Zones Act (Pilot Projects), 2002 | `02t22/` | 3 | 2002-12-09 to 2007-01-01 | 18 |
| 02t28 | Toronto Waterfront Revitalization Corporation Act, 2002 | `02t28/` | 9 | 2003-05-15 to 2025-11-27 | 19 |
| 02t30 | Travel Industry Act, 2002 | `02t30/` | 20 | 2002-12-13 to 2022-03-01 | 50 |
| 02u08 | University of Ontario Institute of Technology Act, 2002 | `02u08/` | 9 | 2004-01-01 to 2023-12-04 | 21 |
| 02w06 | Waste Diversion Act, 2002 | `02w06/` | 9 | 2002-06-27 to 2016-11-30 | 0 |
| 03a09 | Automobile Insurance Rate Stabilization Act, 2003 | `03a09/` | 9 | 2003-12-18 to 2019-06-08 | 25 |
| 03b02 | Back to School (Toronto Catholic Elementary) and Education and Provincial Schools Negotiations Amendment Act, 2003 | `03b02/` | 2 | 2003-06-03 to 2009-12-15 | 0 |
| 03k06 | Kawartha Highlands Signature Site Park Act, 2003 | `03k06/` | 13 | 2003-06-26 to 2026-03-30 | 24 |
| 03o07 | Ontario Loan Act, 2003 | `03o07/` | 1 | 2003-12-18 to 2003-12-18 | 5 |
| 03s01 | SARS Assistance and Recovery Strategy Act, 2003 | `03s01/` | 5 | 2003-05-05 to 2020-03-19 | 0 |
| 03s10 | Supply Act, 2003 | `03s10/` | 2 | 2003-12-18 to 2015-03-31 | 0 |
| 04a06 | Adams Mine Lake Act, 2004 | `04a06/` | 2 | 2004-06-17 to 2009-12-15 | 11 |
| 04c05 | Commitment to the Future of Medicare Act, 2004 | `04c05/` | 20 | 2004-06-17 to 2023-09-25 | 36 |
| 04f27 | Fiscal Transparency and Accountability Act, 2004 | `04f27/` | 6 | 2004-12-16 to 2019-05-29 | 0 |
| 04g09 | Greenbelt Protection Act, 2004 | `04g09/` | 3 | 2004-06-24 to 2005-03-09 | 0 |
| 04g20 | Government Advertising Act, 2004 | `04g20/` | 9 | 2004-12-09 to 2025-11-27 | 18 |
| 04i10 | Irish Heritage Day Act, 2004 | `04i10/` | 1 | 2004-06-24 to 2004-06-24 | 4 |
| 04n31 | Northern Ontario Grow Bonds Corporation Act, 2004 | `04n31/` | 7 | 2004-12-16 to 2012-05-01 | 0 |
| 04o07 | Ontario Loan Act, 2004 | `04o07/` | 1 | 2004-06-17 to 2004-06-17 | 5 |
| 04p03 | Personal Health Information Protection Act, 2004 | `04p03/` | 49 | 2004-05-20 to 2026-01-01 | 113 |
| 04p08 | Public Accounting Act, 2004 | `04p08/` | 9 | 2004-06-17 to 2021-04-30 | 36 |
| 04q03 | Quality of Care Information Protection Act, 2004 | `04q03/` | 8 | 2004-05-20 to 2017-07-01 | 0 |
| 04s32 | Supply Act, 2004 | `04s32/` | 2 | 2004-12-16 to 2015-03-31 | 0 |
| 04t29 | Trust Beneficiaries’ Liability Act, 2004 | `04t29/` | 1 | 2004-12-16 to 2004-12-16 | 5 |
| 05a10 | Asian Heritage Act, 2005 | `05a10/` | 1 | 2005-06-13 to 2005-06-13 | 4 |
| 05a11 | Accessibility for Ontarians with Disabilities Act, 2005 | `05a11/` | 6 | 2005-06-13 to 2016-04-19 | 45 |
| 05d30 | Duffins Rouge Agricultural Preserve Act, 2005 | `05d30/` | 3 | 2005-12-15 to 2022-12-15 | 0 |
| 05f17 | Film Classification Act, 2005 | `05f17/` | 8 | 2005-06-13 to 2021-06-08 | 0 |
| 05g01 | Greenbelt Act, 2005 | `05g01/` | 9 | 2005-02-24 to 2023-12-06 | 30 |
| 05h28 | Higher Education Quality Council of Ontario Act, 2005 | `05h28/` | 9 | 2005-12-12 to 2026-05-07 | 19 |
| 05m09 | Mandatory Gunshot Wounds Reporting Act, 2005 | `05m09/` | 5 | 2005-06-13 to 2024-04-01 | 8 |
| 05o22 | Ontario Wine Week Act, 2005 | `05o22/` | 1 | 2005-06-13 to 2005-06-13 | 4 |
| 05o28 | Ontario Loan Act, 2005 | `05o28/` | 1 | 2005-12-12 to 2005-12-12 | 5 |
| 05p13 | Places to Grow Act, 2005 | `05p13/` | 11 | 2005-06-13 to 2024-02-22 | 23 |
| 05p28 | Ontario Career Colleges Act, 2005 | `05p28/` | 19 | 2005-12-12 to 2024-01-01 | 63 |
| 05p34 | Private Security and Investigative Services Act, 2005 | `05p34/` | 11 | 2005-12-15 to 2019-07-01 | 60 |
| 05r20 | Regional Municipality of Peel Act, 2005 | `05r20/` | 5 | 2005-06-13 to 2024-06-06 | 7 |
| 05r35 | Representation Act, 2005 | `05r35/` | 2 | 2005-12-15 to 2015-12-03 | 0 |
| 05s07 | Sabrina’s Law, 2005 | `05s07/` | 3 | 2005-06-13 to 2021-04-19 | 6 |
| 06a34 | Archives and Recordkeeping Act, 2006 | `06a34/` | 7 | 2006-12-20 to 2019-07-01 | 31 |
| 06c11 | City of Toronto Act, 2006 | `06c11/` | 88 | 2006-06-12 to 2026-06-02 | 554 |
| 06c22 | Clean Water Act, 2006 | `06c22/` | 21 | 2006-10-19 to 2026-07-01 | 117 |
| 06c33 | Canadian Public Accountability Board Act (Ontario), 2006 | `06c33/` | 6 | 2006-12-20 to 2024-11-06 | 20 |
| 06d19 | Dissolution of Inactive Corporations Act, 2006 | `06d19/` | 2 | 2006-06-22 to 2010-10-25 | 0 |
| 06e03 | Energy Conservation Leadership Act, 2006 | `06e03/` | 4 | 2006-03-28 to 2009-09-09 | 0 |
| 06f31 | Fair Access to Regulated Professions and Compulsory Trades Act, 2006 | `06f31/` | 28 | 2006-12-20 to 2025-07-01 | 47 |
| 06g16 | Metrolinx Act, 2006 | `06g16/` | 33 | 2006-06-22 to 2026-07-01 | 67 |
| 06l04 | Local Health System Integration Act, 2006 | `06l04/` | 33 | 2006-03-28 to 2024-06-28 | 0 |
| 06l21 | Legislation Act, 2006 | `06l21/` | 15 | 2006-10-19 to 2025-12-11 | 108 |
| 06m26 | Mandatory Blood Testing Act, 2006 | `06m26/` | 8 | 2006-12-20 to 2025-07-01 | 17 |
| 06m29 | Mortgage Brokerages, Lenders and Administrators Act, 2006 | `06m29/` | 14 | 2006-12-20 to 2022-04-29 | 60 |
| 06o02 | Ontario Municipal Employees Retirement System Act, 2006 | `06o02/` | 19 | 2006-02-23 to 2026-03-13 | 53 |
| 06o09i | Ontario Infrastructure Projects Corporation Act, 2006 | `06o09i/` | 6 | 2006-05-18 to 2011-06-06 | 0 |
| 06o09j | Ontario Loan Act, 2006 | `06o09j/` | 1 | 2006-05-18 to 2006-05-18 | 5 |
| 06o09k | Ontario Municipal Employees Retirement System Review Act, 2006 | `06o09k/` | 3 | 2006-05-18 to 2012-07-01 | 7 |
| 06o35 | Ontario Provincial Police Collective Bargaining Act, 2006 | `06o35/` | 9 | 2006-12-20 to 2024-04-01 | 17 |
| 06p12 | Provincial Parks and Conservation Reserves Act, 2006 | `06p12/` | 20 | 2006-06-20 to 2026-03-30 | 68 |
| 06p33 | Provincial Land Tax Act, 2006 | `06p33/` | 7 | 2006-12-20 to 2016-12-08 | 31 |
| 06p35 | Public Service of Ontario Act, 2006 | `06p35/` | 14 | 2006-12-20 to 2024-04-01 | 161 |
| 06r17 | Residential Tenancies Act, 2006 | `06r17/` | 53 | 2006-06-22 to 2026-09-21 | 310 |
| 06s06 | Supply Act, 2006 | `06s06/` | 2 | 2006-03-31 to 2015-03-31 | 0 |
| 06s08 | Securities Transfer Act, 2006 | `06s08/` | 2 | 2006-05-18 to 2007-01-01 | 109 |
| 06t27 | Traditional Chinese Medicine Act, 2006 | `06t27/` | 5 | 2006-12-20 to 2021-06-03 | 18 |
| 06t33 | Tax Increment Financing Act, 2006 | `06t33/` | 1 | 2006-12-20 to 2006-12-20 | 9 |
| 07c10 | Chase McEachern Act (Heart Defibrillator Civil Liability), 2007 | `07c10/` | 2 | 2007-06-04 to 2007-07-03 | 8 |
| 07e01 | Electoral System Referendum Act, 2007 | `07e01/` | 6 | 2007-04-18 to 2013-10-10 | 0 |
| 07e06 | Endangered Species Act, 2007 | `07e06/` | 9 | 2007-05-17 to 2026-03-30 | 0 |
| 07e07 | Early Childhood Educators Act, 2007 | `07e07/` | 22 | 2007-05-17 to 2023-06-08 | 88 |
| 07h10 | Homeopathy Act, 2007 | `07h10/` | 3 | 2007-06-04 to 2021-06-03 | 15 |
| 07i07 | Interim Appropriation Act, 2007 | `07i07/` | 2 | 2007-05-17 to 2008-03-31 | 0 |
| 07k10 | Kinesiology Act, 2007 | `07k10/` | 3 | 2007-06-04 to 2021-06-03 | 15 |
| 07l08 | Long-Term Care Homes Act, 2007 | `07l08/` | 28 | 2007-06-04 to 2022-04-11 | 0 |
| 07n10 | Naturopathy Act, 2007 | `07n10/` | 5 | 2007-06-04 to 2021-06-03 | 17 |
| 07o07 | Ontario Loan Act, 2007 | `07o07/` | 1 | 2007-05-17 to 2007-05-17 | 5 |
| 07o10 | Ontario Agency for Health Protection and Promotion Act, 2007 | `07o10/` | 12 | 2007-06-04 to 2026-04-01 | 33 |
| 07p09 | Provincial Advocate for Children and Youth Act, 2007 | `07p09/` | 14 | 2007-06-04 to 2019-05-01 | 0 |
| 07p10 | Psychotherapy Act, 2007 | `07p10/` | 5 | 2007-06-04 to 2021-06-03 | 17 |
| 07r04 | Regulatory Modernization Act, 2007 | `07r04/` | 4 | 2007-05-17 to 2019-07-01 | 23 |
| 07s02 | Supply Act, 2007 | `07s02/` | 2 | 2007-04-18 to 2015-03-31 | 0 |
| 07s07 | Status of Ontario’s Artists Act, 2007 | `07s07/` | 2 | 2007-05-17 to 2009-12-15 | 10 |
| 07t11 | Taxation Act, 2007 | `07t11/` | 67 | 2007-06-04 to 2026-07-01 | 275 |
| 08a13 | Algoma University Act, 2008 | `08a13/` | 8 | 2008-06-18 to 2023-12-04 | 40 |
| 08c15 | Colleges Collective Bargaining Act, 2008 | `08c15/` | 6 | 2008-10-08 to 2018-12-31 | 88 |
| 08e25 | Emancipation Day Act, 2008 | `08e25/` | 1 | 2008-12-10 to 2008-12-10 | 4 |
| 08i06 | Investing in Ontario Act, 2008 | `08i06/` | 3 | 2008-05-14 to 2019-05-29 | 0 |
| 08i07 | Interim Appropriation Act, 2008 | `08i07/` | 2 | 2008-05-14 to 2009-04-23 | 0 |
| 08i19 | Interim Appropriation for 2009-2010 Act, 2008 | `08i19/` | 4 | 2008-11-27 to 2010-05-18 | 0 |
| 08l23 | Lake Simcoe Protection Act, 2008 | `08l23/` | 12 | 2008-12-10 to 2026-03-30 | 33 |
| 08o07 | Ontario Loan Act, 2008 | `08o07/` | 1 | 2008-05-14 to 2008-05-14 | 5 |
| 08o10 | Ontario French-language Educational Communications Authority Act, 2008 | `08o10/` | 10 | 2008-06-18 to 2022-03-01 | 27 |
| 08o19 | Venture Ontario Act, 2008 | `08o19/` | 10 | 2008-11-27 to 2026-04-01 | 23 |
| 08p09 | Payday Loans Act, 2008 | `08p09/` | 14 | 2008-06-18 to 2021-10-19 | 84 |
| 08p17 | Photo Card Act, 2008 | `08p17/` | 8 | 2008-11-27 to 2026-06-25 | 29 |
| 08s01 | Supply Act, 2008 | `08s01/` | 2 | 2008-03-31 to 2015-03-31 | 0 |
| 08s14 | Services and Supports to Promote the Social Inclusion of Persons with Developmental Disabilities Act, 2008 | `08s14/` | 11 | 2008-10-08 to 2023-06-08 | 50 |
| 08s19 | Supplementary Interim Appropriation Act, 2008 | `08s19/` | 2 | 2008-11-27 to 2009-04-23 | 0 |
| 08t04 | Toronto Public Transit Service Resumption Act, 2008 | `08t04/` | 2 | 2008-04-27 to 2019-11-15 | 0 |
| 09a03 | Apology Act, 2009 | `09a03/` | 1 | 2009-04-23 to 2009-04-23 | 7 |
| 09a31 | Animal Health Act, 2009 | `09a31/` | 13 | 2009-12-15 to 2024-06-06 | 73 |
| 09a33 | Adjudicative Tribunals Accountability, Governance and Appointments Act, 2009 | `09a33/` | 8 | 2009-12-15 to 2019-05-01 | 28 |
| 09b29 | Barrie-Innisfil Boundary Adjustment Act, 2009 | `09b29/` | 1 | 2009-12-15 to 2009-12-15 | 15 |
| 09e32 | Employment Protection for Foreign Nationals Act, 2009 | `09e32/` | 8 | 2009-12-15 to 2023-10-26 | 56 |
| 09g12 | Green Energy Act, 2009 | `09g12/` | 9 | 2009-05-14 to 2019-01-01 | 0 |
| 09h07 | Holodomor Memorial Day Act, 2009 | `09h07/` | 1 | 2009-04-23 to 2009-04-23 | 4 |
| 09i30 | Interprovincial Policing Act, 2009 | `09i30/` | 7 | 2009-12-15 to 2024-04-01 | 46 |
| 09i34 | Interim Appropriation for 2010-2011 Act, 2009 | `09i34/` | 3 | 2009-12-15 to 2011-03-30 | 0 |
| 09o18a | Ontario Child Benefit Equivalent Act, 2009 | `09o18a/` | 2 | 2009-06-05 to 2009-07-31 | 15 |
| 09o18b | Ontario Loan Act, 2009 | `09o18b/` | 1 | 2009-06-05 to 2009-06-05 | 5 |
| 09o22 | Ontario College of Trades and Apprenticeship Act, 2009 | `09o22/` | 19 | 2009-10-28 to 2022-01-01 | 0 |
| 09o24 | Ontario Labour Mobility Act, 2009 | `09o24/` | 32 | 2010-01-01 to 2026-01-01 | 35 |
| 09o34 | Ontario Loan Act, 2009 (No. 2) | `09o34/` | 1 | 2009-12-15 to 2009-12-15 | 5 |
| 09p10 | Poverty Reduction Act, 2009 | `09p10/` | 4 | 2009-05-06 to 2017-11-01 | 12 |
| 09p20 | Public Sector Expenses Review Act, 2009 | `09p20/` | 8 | 2009-10-19 to 2016-12-08 | 14 |
| 09p33 | Public Inquiries Act, 2009 | `09p33/` | 11 | 2009-12-15 to 2026-06-02 | 40 |
| 09s08 | Supply Act, 2009 | `09s08/` | 2 | 2009-04-23 to 2015-03-31 | 0 |
| 09s18 | Supplementary Interim Appropriation for 2009-2010 Act, 2009 | `09s18/` | 2 | 2009-06-05 to 2010-05-18 | 0 |
| 09s34 | Succession Duty Legislation Repeal Act, 2009 | `09s34/` | 2 | 2009-12-15 to 2018-12-06 | 0 |
| 09t13 | Tobacco Damages and Health Care Costs Recovery Act, 2009 | `09t13/` | 9 | 2009-05-14 to 2023-09-25 | 15 |
| 09t19 | Toxics Reduction Act, 2009 | `09t19/` | 15 | 2009-06-05 to 2021-12-31 | 0 |
| 09y01 | York University Labour Disputes Resolution Act, 2009 | `09y01/` | 2 | 2009-01-29 to 2019-11-15 | 0 |
| 10b25 | Broader Public Sector Accountability Act, 2010 | `10b25/` | 28 | 2010-12-08 to 2024-06-28 | 40 |
| 10c06a | Certified General Accountants Act, 2010 | `10c06a/` | 3 | 2010-05-18 to 2017-05-17 | 0 |
| 10c06b | Certified Management Accountants Act, 2010 | `10c06b/` | 3 | 2010-05-18 to 2017-05-17 | 0 |
| 10c06c | Chartered Accountants Act, 2010 | `10c06c/` | 3 | 2010-05-18 to 2017-05-17 | 0 |
| 10c16a | Commercial Mediation Act, 2010 | `10c16a/` | 1 | 2010-10-25 to 2010-10-25 | 18 |
| 10c16b | Creditors’ Relief Act, 2010 | `10c16b/` | 3 | 2010-10-25 to 2023-06-08 | 25 |
| 10e01 | Electronic Land Registration Services Act, 2010 | `10e01/` | 4 | 2010-05-18 to 2019-07-01 | 11 |
| 10e08 | Energy Consumer Protection Act, 2010 | `10e08/` | 11 | 2010-05-18 to 2024-12-04 | 44 |
| 10e14 | Excellent Care for All Act, 2010 | `10e14/` | 26 | 2010-06-08 to 2024-12-01 | 35 |
| 10f04 | Franco-Ontarian Day Act, 2010 | `10f04/` | 1 | 2010-05-18 to 2010-05-18 | 4 |
| 10f18 | Far North Act, 2010 | `10f18/` | 5 | 2010-10-25 to 2024-02-22 | 26 |
| 10i01 | Indian Lands Agreement (1986) Confirmation Act, 2010 | `10i01/` | 1 | 2010-05-18 to 2010-05-18 | 6 |
| 10i17 | Italian Heritage Month Act, 2010 | `10i17/` | 1 | 2010-10-25 to 2010-10-25 | 4 |
| 10i26 | Interim Appropriation for 2011-2012 Act, 2010 | `10i26/` | 3 | 2010-12-08 to 2012-04-24 | 0 |
| 10k20 | Katelyn Bedard Bone Marrow Awareness Month Act, 2010 | `10k20/` | 1 | 2010-11-29 to 2010-11-29 | 4 |
| 10n15 | Not-for-Profit Corporations Act, 2010 | `10n15/` | 17 | 2010-10-25 to 2025-10-01 | 228 |
| 10n22 | Narcotics Safety and Awareness Act, 2010 | `10n22/` | 8 | 2010-11-29 to 2023-07-24 | 20 |
| 10o01 | Ontario Loan Act, 2010 | `10o01/` | 1 | 2010-05-18 to 2010-05-18 | 5 |
| 10o26 | Ontario Clean Energy Benefit Act, 2010 | `10o26/` | 11 | 2010-12-08 to 2020-07-01 | 0 |
| 10p01 | Public Sector Compensation Restraint to Protect Public Services Act, 2010 | `10p01/` | 10 | 2010-05-18 to 2020-09-18 | 0 |
| 10r11 | Retirement Homes Act, 2010 | `10r11/` | 30 | 2010-06-08 to 2024-06-28 | 146 |
| 10s01 | Supplementary Interim Appropriation Act, 2010 | `10s01/` | 2 | 2010-05-18 to 2011-03-30 | 0 |
| 10s02 | Supply Act, 2010 | `10s02/` | 2 | 2010-05-18 to 2015-03-31 | 0 |
| 10v03 | Vimy Ridge Day Act, 2010 | `10v03/` | 1 | 2010-05-18 to 2010-05-18 | 5 |
| 10w19 | Water Opportunities Act, 2010 | `10w19/` | 6 | 2010-11-29 to 2021-12-02 | 31 |
| 11b14 | British Home Child Day Act, 2011 | `11b14/` | 1 | 2011-06-01 to 2011-06-01 | 4 |
| 11d04 | Dutch Heritage Month Act, 2011 | `11d04/` | 1 | 2011-03-30 to 2011-03-30 | 4 |
| 11h06 | Housing Services Act, 2011 | `11h06/` | 23 | 2011-05-04 to 2026-01-01 | 203 |
| 11m09a | Ministry of Energy Act, 2011 | `11m09a/` | 6 | 2011-05-12 to 2019-07-01 | 16 |
| 11m09b | Ministry of Infrastructure Act, 2011 | `11m09b/` | 16 | 2011-05-12 to 2025-06-05 | 31 |
| 11n09 | Northern Ontario Grow Bonds Corporation Repeal Act, 2011 | `11n09/` | 2 | 2011-05-12 to 2012-05-01 | 6 |
| 11o09a | Ontario Infrastructure and Lands Corporation Act, 2011 | `11o09a/` | 15 | 2011-05-12 to 2025-12-11 | 43 |
| 11o09b | Ontario Loan Act, 2011 | `11o09b/` | 1 | 2011-05-12 to 2011-05-12 | 5 |
| 11o10 | Ontario Forest Tenure Modernization Act, 2011 | `11o10/` | 8 | 2011-06-01 to 2026-04-01 | 31 |
| 11s05 | Supply Act, 2011 | `11s05/` | 2 | 2011-03-30 to 2015-03-31 | 0 |
| 11s09 | Supplementary Interim Appropriation Act, 2011 | `11s09/` | 2 | 2011-05-12 to 2012-04-24 | 0 |
| 11t02 | Toronto Transit Commission Labour Disputes Resolution Act, 2011 | `11t02/` | 1 | 2011-03-30 to 2011-03-30 | 25 |
| 11u03 | Ukrainian Heritage Day Act, 2011 | `11u03/` | 1 | 2011-03-30 to 2011-03-30 | 4 |
| 12a10 | Attracting Investment and Creating Jobs Act, 2012 | `12a10/` | 4 | 2012-09-11 to 2022-12-31 | 12 |
| 12d08 | Delegated Administrative Authorities Act, 2012 | `12d08/` | 4 | 2012-06-20 to 2020-07-14 | 0 |
| 12g08 | Government Services and Service Providers Act (ServiceOntario), 2012 | `12g08/` | 4 | 2012-06-20 to 2022-12-31 | 0 |
| 12h08 | Highway 407 East Act, 2012 | `12h08/` | 9 | 2012-06-20 to 2025-06-05 | 23 |
| 12i08 | Interim Appropriation for 2012-2013 Act, 2012 | `12i08/` | 2 | 2012-06-20 to 2013-04-23 | 0 |
| 12j01 | Jewish Heritage Month Act, 2012 | `12j01/` | 1 | 2012-04-24 to 2012-04-24 | 4 |
| 12m02 | Major-General Sir Isaac Brock Day Act, 2012 | `12m02/` | 1 | 2012-04-24 to 2012-04-24 | 4 |
| 12n08 | Nipissing First Nation Agreement Act (Tax Matters), 2012 | `12n08/` | 1 | 2012-06-20 to 2012-06-20 | 6 |
| 12o04 | Ontario Underground Infrastructure Notification System Act, 2012 | `12o04/` | 8 | 2012-06-19 to 2024-12-04 | 35 |
| 12o08 | Ontario Loan Act, 2012 | `12o08/` | 1 | 2012-06-20 to 2012-06-20 | 5 |
| 12p11 | Putting Students First Act, 2012 | `12p11/` | 3 | 2012-09-11 to 2013-01-23 | 0 |
| 12r08 | Research Foundation Repeal Act, 2012 | `12r08/` | 3 | 2012-06-20 to 2013-07-02 | 0 |
| 12s03 | Supply Act, 2012 | `12s03/` | 2 | 2012-04-24 to 2015-03-31 | 0 |
| 13d02 | Dedicated Funding for Public Transportation Act, 2013 | `13d02/` | 3 | 2013-06-13 to 2023-05-18 | 4 |
| 13f04 | Financial Accountability Officer Act, 2013 | `13f04/` | 4 | 2013-09-26 to 2018-12-06 | 30 |
| 13f11 | First Responders Day Act, 2013 | `13f11/` | 1 | 2013-12-12 to 2013-12-12 | 4 |
| 13h14 | Hawkins Gignac Act (Carbon Monoxide Safety), 2013 | `13h14/` | 1 | 2013-12-12 to 2013-12-12 | 5 |
| 13i02 | Interim Appropriation for 2013-2014 Act, 2013 | `13i02/` | 2 | 2013-06-13 to 2014-03-03 | 0 |
| 13l07 | Local Food Act, 2013 | `13l07/` | 8 | 2013-11-06 to 2023-05-18 | 11 |
| 13l18 | Lincoln Alexander Day Act, 2013 | `13l18/` | 1 | 2013-12-12 to 2013-12-12 | 4 |
| 13o02 | Ontario Loan Act, 2013 | `13o02/` | 2 | 2013-06-13 to 2013-06-21 | 5 |
| 13r06 | Registered Human Resources Professionals Act, 2013 | `13r06/` | 4 | 2013-11-06 to 2017-03-22 | 77 |
| 13s01 | Supply Act, 2013 | `13s01/` | 2 | 2013-04-23 to 2015-03-31 | 0 |
| 13s05 | Skin Cancer Prevention Act (Tanning Beds), 2013 | `13s05/` | 2 | 2013-10-10 to 2014-05-01 | 13 |
| 13s12 | Sikh Heritage Month Act, 2013 | `13s12/` | 1 | 2013-12-12 to 2013-12-12 | 4 |
| 13w08 | Wireless Services Agreements Act, 2013 | `13w08/` | 4 | 2013-11-06 to 2019-10-03 | 0 |
| 14b12 | Burden Reduction Reporting Act, 2014 | `14b12/` | 3 | 2014-12-11 to 2021-01-01 | 0 |
| 14b13 | Broader Public Sector Executive Compensation Act, 2014 | `14b13/` | 9 | 2014-12-11 to 2020-09-18 | 29 |
| 14c02 | Children and Youth in Care Day Act, 2014 | `14c02/` | 1 | 2014-03-25 to 2014-03-25 | 4 |
| 14c11 | Child Care and Early Years Act, 2014 | `14c11/` | 20 | 2014-12-04 to 2026-05-07 | 91 |
| 14i07 | Interim Appropriation for 2014-2015 Act, 2014 | `14i07/` | 2 | 2014-07-24 to 2015-03-31 | 0 |
| 14o07 | Ontario Loan Act, 2014 | `14o07/` | 1 | 2014-07-24 to 2014-07-24 | 5 |
| 14p03 | Pope John Paul II Day Act, 2014 | `14p03/` | 1 | 2014-03-25 to 2014-03-25 | 4 |
| 14p12 | Partnerships for Jobs and Growth Act, 2014 | `14p12/` | 3 | 2014-12-11 to 2019-12-10 | 0 |
| 14s01 | Supply Act, 2014 | `14s01/` | 3 | 2014-03-03 to 2015-04-01 | 0 |
| 14s05 | School Boards Collective Bargaining Act, 2014 | `14s05/` | 11 | 2014-04-09 to 2026-05-07 | 69 |
| 14s15 | Security for Electricity Generating Facilities and Nuclear Facilities Act, 2014 | `14s15/` | 2 | 2014-12-11 to 2015-06-24 | 10 |
| 14t04 | Tamil Heritage Month Act, 2014 | `14t04/` | 1 | 2014-03-25 to 2014-03-25 | 4 |
| 14t07 | Trillium Trust Act, 2014 | `14t07/` | 7 | 2014-07-24 to 2019-04-01 | 0 |
| 14v14 | Voluntary Blood Donations Act, 2014 | `14v14/` | 1 | 2014-12-11 to 2014-12-11 | 15 |
| 15c12 | Christmas Tree Day Act, 2015 | `15c12/` | 1 | 2015-06-02 to 2015-06-02 | 4 |
| 15c28 | Condominium Management Services Act, 2015 | `15c28/` | 14 | 2015-12-03 to 2023-01-01 | 62 |
| 15e07 | Electronic Cigarettes Act, 2015 | `15e07/` | 6 | 2015-05-28 to 2018-10-17 | 0 |
| 15e38 | Escheats Act, 2015 | `15e38/` | 7 | 2015-12-10 to 2025-12-11 | 30 |
| 15f38 | Forfeited Corporate Property Act, 2015 | `15f38/` | 9 | 2015-12-10 to 2021-10-19 | 49 |
| 15g24 | Great Lakes Protection Act, 2015 | `15g24/` | 5 | 2015-11-03 to 2024-02-22 | 45 |
| 15h04 | Hispanic Heritage Month Act, 2015 | `15h04/` | 1 | 2015-05-05 to 2015-05-05 | 4 |
| 15h07 | Healthy Menu Choices Act, 2015 | `15h07/` | 3 | 2015-05-28 to 2017-01-01 | 9 |
| 15h38 | Horse Racing Licence Act, 2015 | `15h38/` | 8 | 2015-12-10 to 2021-11-29 | 48 |
| 15i15 | Infrastructure for Jobs and Prosperity Act, 2015 | `15i15/` | 6 | 2015-06-04 to 2022-01-01 | 15 |
| 15i19 | Intergenerational Day Canada Act, 2015 | `15i19/` | 1 | 2015-06-04 to 2015-06-04 | 4 |
| 15i20a | Interim Appropriation for 2015-2016 Act, 2015 | `15i20a/` | 2 | 2015-06-04 to 2016-03-24 | 0 |
| 15i20b | Investment Management Corporation of Ontario Act, 2015 | `15i20b/` | 7 | 2015-06-04 to 2023-12-04 | 29 |
| 15i22 | Invasive Species Act, 2015 | `15i22/` | 4 | 2015-11-03 to 2019-07-01 | 60 |
| 15i38 | Interim Appropriation for 2016-2017 Act, 2015 | `15i38/` | 3 | 2015-12-10 to 2017-03-30 | 0 |
| 15m39 | Métis Nation of Ontario Secretariat Act, 2015 | `15m39/` | 6 | 2015-12-10 to 2021-10-19 | 24 |
| 15o05 | Ontario Retirement Pension Plan Act, 2015 | `15o05/` | 3 | 2015-05-05 to 2016-12-08 | 0 |
| 15o08 | Ontario Immigration Act, 2015 | `15o08/` | 7 | 2015-05-28 to 2025-11-27 | 44 |
| 15o16 | Ontario Bike Month Act, 2015 | `15o16/` | 1 | 2015-06-04 to 2015-06-04 | 4 |
| 15o20a | Ontario Loan Act, 2015 | `15o20a/` | 2 | 2015-06-04 to 2015-09-02 | 5 |
| 15o20b | Ontario Retirement Pension Plan Administration Corporation Act, 2015 | `15o20b/` | 5 | 2015-06-04 to 2016-12-08 | 0 |
| 15o21 | Ontario Flag Day Act, 2015 | `15o21/` | 1 | 2015-06-04 to 2015-06-04 | 4 |
| 15p02 | Protecting Child Performers Act, 2015 | `15p02/` | 4 | 2015-05-05 to 2021-04-19 | 30 |
| 15p09 | Pooled Registered Pension Plans Act, 2015 | `15p09/` | 10 | 2015-05-28 to 2020-12-08 | 37 |
| 15p11 | Protecting the School Year Act, 2015 | `15p11/` | 2 | 2015-05-28 to 2025-12-31 | 24 |
| 15p13 | Provincial Framework and Action Plan concerning Emerging Vector-Borne Diseases Act, 2015 | `15p13/` | 1 | 2015-06-02 to 2015-06-02 | 5 |
| 15p30 | Police Record Checks Reform Act, 2015 | `15p30/` | 10 | 2015-12-03 to 2026-06-02 | 29 |
| 15p37 | Pregnancy and Infant Loss Awareness, Research and Care Act, 2015 | `15p37/` | 1 | 2015-12-10 to 2015-12-10 | 5 |
| 15r03 | Ryan’s Law (Ensuring Asthma Friendly Schools), 2015 | `15r03/` | 2 | 2015-05-05 to 2021-04-19 | 7 |
| 15r31 | Representation Act, 2015 | `15r31/` | 5 | 2015-12-03 to 2017-12-31 | 8 |
| 15s01 | Supply Act, 2015 | `15s01/` | 2 | 2015-03-31 to 2016-04-01 | 0 |
| 15s33 | Safeguarding our Communities Act (Patch for Patch Return Policy), 2015 | `15s33/` | 2 | 2015-12-10 to 2016-10-01 | 7 |
| 15s38 | Supplementary Interim Appropriation for 2015-2016 Act, 2015 | `15s38/` | 2 | 2015-12-10 to 2016-03-24 | 0 |
| 15t17 | Terry Fox Day Act, 2015 | `15t17/` | 1 | 2015-06-04 to 2015-06-04 | 4 |
| 16a29 | Albanian Heritage Month Act, 2016 | `16a29/` | 1 | 2016-12-08 to 2016-12-08 | 4 |
| 16b01 | Black History Month Act, 2016 | `16b01/` | 1 | 2016-02-16 to 2016-02-16 | 4 |
| 16b05 | Benefits Administration Integration Act, 2016 | `16b05/` | 1 | 2016-04-19 to 2016-04-19 | 3 |
| 16b32 | Bangladeshi Heritage Month Act, 2016 | `16b32/` | 1 | 2016-12-08 to 2016-12-08 | 4 |
| 16c07 | Climate Change Mitigation and Low-carbon Economy Act, 2016 | `16c07/` | 5 | 2016-05-18 to 2018-11-14 | 0 |
| 16c09 | Correctional Services Staff Recognition Week Act, 2016 | `16c09/` | 1 | 2016-06-09 to 2016-06-09 | 4 |
| 16f37 | Financial Services Regulatory Authority of Ontario Act, 2016 | `16f37/` | 19 | 2016-12-08 to 2024-04-01 | 53 |
| 16h27 | Hazel McCallion Day Act, 2016 | `16h27/` | 1 | 2016-12-08 to 2016-12-08 | 4 |
| 16h35 | Hindu Heritage Month Act, 2016 | `16h35/` | 1 | 2016-12-08 to 2016-12-08 | 4 |
| 16i20 | Islamic Heritage Month Act, 2016 | `16i20/` | 1 | 2016-11-02 to 2016-11-02 | 4 |
| 16i37 | Interim Appropriation for 2017-2018 Act, 2016 | `16i37/` | 3 | 2016-12-08 to 2018-03-07 | 0 |
| 16n36 | Nurse Practitioner Week Act, 2016 | `16n36/` | 1 | 2016-12-08 to 2016-12-08 | 4 |
| 16o05 | Ontario Loan Act, 2016 | `16o05/` | 1 | 2016-04-19 to 2016-04-19 | 5 |
| 16o08 | Ontario Trails Act, 2016 | `16o08/` | 4 | 2016-06-09 to 2021-10-19 | 15 |
| 16o16 | Ontario Down Syndrome Day Act, 2016 | `16o16/` | 1 | 2016-06-09 to 2016-06-09 | 4 |
| 16o17 | Ontario Retirement Pension Plan Act (Strengthening Retirement Security for Ontarians), 2016 | `16o17/` | 2 | 2016-06-09 to 2016-12-08 | 0 |
| 16o19 | Ontario Rebate for Electricity Consumers Act, 2016 | `16o19/` | 4 | 2016-11-02 to 2019-11-01 | 18 |
| 16o37 | Ontario Retirement Pension Plan Legislation Repeal Act, 2016 | `16o37/` | 1 | 2016-12-08 to 2016-12-08 | 6 |
| 16p31 | PANDAS/PANS Awareness Day Act, 2016 | `16p31/` | 1 | 2016-12-08 to 2016-12-08 | 4 |
| 16q06 | Quality of Care Information Protection Act, 2016 | `16q06/` | 7 | 2016-05-18 to 2024-12-01 | 20 |
| 16r11 | Rowan’s Law Advisory Committee Act, 2016 | `16r11/` | 3 | 2016-06-09 to 2017-12-09 | 0 |
| 16r12 | Resource Recovery and Circular Economy Act, 2016 | `16r12/` | 19 | 2016-06-09 to 2025-12-11 | 119 |
| 16r21 | Remembrance Day and Veterans’ Week Act, 2024 | `16r21/` | 4 | 2016-11-02 to 2024-11-19 | 7 |
| 16s03 | Supply Act, 2016 | `16s03/` | 2 | 2016-03-24 to 2017-04-01 | 0 |
| 16s37 | Supplementary Interim Appropriation for 2016-2017 Act, 2016 | `16s37/` | 2 | 2016-12-08 to 2017-03-30 | 0 |
| 16t18 | Treaties Recognition Week Act, 2016 | `16t18/` | 1 | 2016-06-09 to 2016-06-09 | 2 |
| 16w12 | Waste Diversion Transition Act, 2016 | `16w12/` | 11 | 2016-06-09 to 2024-04-01 | 78 |
| 16w14 | Workers Day of Mourning Act, 2016 | `16w14/` | 4 | 2016-06-09 to 2024-04-01 | 6 |
| 17a15 | Anti-Racism Act, 2017 | `17a15/` | 9 | 2017-06-01 to 2024-06-28 | 19 |
| 17c08 | Chartered Professional Accountants of Ontario Act, 2017 | `17c08/` | 5 | 2017-05-17 to 2021-10-19 | 77 |
| 17c14 | Child, Youth and Family Services Act, 2017 | `17c14/` | 27 | 2017-06-01 to 2026-07-01 | 383 |
| 17c21 | Colleges of Applied Arts and Technology Labour Dispute Resolution Act, 2017 | `17c21/` | 1 | 2017-11-19 to 2017-11-19 | 23 |
| 17c26 | Cannabis Control Act, 2017 | `17c26/` | 10 | 2017-12-12 to 2025-01-01 | 38 |
| 17e34 | English and Wabigoon Rivers Remediation Funding Act, 2017 | `17e34/` | 3 | 2017-12-14 to 2019-07-01 | 22 |
| 17f34 | Financial Services Tribunal Act, 2017 | `17f34/` | 6 | 2017-12-14 to 2020-12-08 | 23 |
| 17h05 | Home Inspection Act, 2017 | `17h05/` | 5 | 2017-04-13 to 2024-03-06 | 5 |
| 17h12 | Human Trafficking Awareness Day Act, 2017 | `17h12/` | 1 | 2017-05-30 to 2017-05-30 | 4 |
| 17h25 | Health Sector Payment Transparency Act, 2017 | `17h25/` | 2 | 2017-12-12 to 2019-05-29 | 3 |
| 17h34 | High Occupancy Toll (HOT) Lanes Act, 2017 | `17h34/` | 1 | 2017-12-14 to 2017-12-14 | 4 |
| 17i02a | International Choice of Court Agreements Convention Act, 2017 | `17i02a/` | 1 | 2017-03-22 to 2017-03-22 | 8 |
| 17i02b | International Commercial Arbitration Act, 2017 | `17i02b/` | 1 | 2017-03-22 to 2017-03-22 | 18 |
| 17i02c | International Electronic Communications Convention Act, 2017 | `17i02c/` | 1 | 2017-03-22 to 2017-03-22 | 8 |
| 17i02d | International Recognition of Trusts Act, 2017 | `17i02d/` | 1 | 2017-03-22 to 2017-03-22 | 8 |
| 17i34a | Indigenous Institutes Act, 2017 | `17i34a/` | 1 | 2017-12-14 to 2017-12-14 | 12 |
| 17i34b | Interim Appropriation for 2018-2019 Act, 2017 | `17i34b/` | 3 | 2017-12-14 to 2019-03-26 | 0 |
| 17k31 | Korean Heritage Month Act, 2017 | `17k31/` | 1 | 2017-12-14 to 2017-12-14 | 4 |
| 17l23a | Local Planning Appeal Tribunal Act, 2017 | `17l23a/` | 9 | 2017-12-12 to 2021-06-01 | 0 |
| 17l23b | Local Planning Appeal Support Centre Act, 2017 | `17l23b/` | 3 | 2017-12-12 to 2019-12-10 | 0 |
| 17l27 | Lebanese Heritage Month Act, 2017 | `17l27/` | 1 | 2017-12-14 to 2017-12-14 | 4 |
| 17l28 | Lung Health Act, 2017 | `17l28/` | 4 | 2017-12-14 to 2019-12-02 | 0 |
| 17l32 | Lawren Harris Day Act, 2017 | `17l32/` | 1 | 2017-12-14 to 2017-12-14 | 4 |
| 17m25 | Medical Radiation and Imaging Technology Act, 2017 | `17m25/` | 5 | 2017-12-12 to 2026-01-01 | 18 |
| 17n33 | New Home Construction Licensing Act, 2017 | `17n33/` | 13 | 2017-12-14 to 2024-06-06 | 96 |
| 17o08 | Ontario Loan Act, 2017 | `17o08/` | 1 | 2017-05-17 to 2017-05-17 | 5 |
| 17o16 | Ontario Fair Hydro Plan Act, 2017 | `17o16/` | 7 | 2017-06-01 to 2022-01-01 | 38 |
| 17o25 | Oversight of Health Facilities and Devices Act, 2017 | `17o25/` | 3 | 2017-12-12 to 2023-05-18 | 0 |
| 17o26 | Ontario Cannabis Retail Corporation Act, 2017 | `17o26/` | 12 | 2017-12-12 to 2026-04-01 | 33 |
| 17o30 | Ontario Craft Beer Week Act, 2017 | `17o30/` | 1 | 2017-12-14 to 2017-12-14 | 4 |
| 17p12 | Prevention of and Remedies for Human Trafficking Act, 2017 | `17p12/` | 4 | 2017-05-30 to 2023-12-04 | 20 |
| 17p33 | Protection for Owners and Purchasers of New Homes Act, 2017 | `17p33/` | 4 | 2017-12-14 to 2020-07-14 | 6 |
| 17r20 | Reducing Regulatory Costs for Business Act, 2017 | `17r20/` | 4 | 2017-11-14 to 2021-01-01 | 0 |
| 17s04 | Supply Act, 2017 | `17s04/` | 2 | 2017-03-30 to 2018-04-01 | 0 |
| 17s11 | Seniors Active Living Centres Act, 2017 | `17s11/` | 2 | 2017-05-30 to 2017-10-01 | 16 |
| 17s19 | Safe Access to Abortion Services Act, 2017 | `17s19/` | 2 | 2017-10-25 to 2018-02-01 | 16 |
| 17s26 | Smoke-Free Ontario Act, 2017 | `17s26/` | 8 | 2017-12-12 to 2024-06-28 | 32 |
| 17s34 | Supplementary Interim Appropriation for 2017-2018 Act, 2017 | `17s34/` | 2 | 2017-12-14 to 2018-03-07 | 0 |
| 17t29 | Trans Day of Remembrance Act, 2017 | `17t29/` | 1 | 2017-12-14 to 2017-12-14 | 5 |
| 17t33 | Ticket Sales Act, 2017 | `17t33/` | 9 | 2017-12-14 to 2026-06-10 | 46 |
| 17u34 | Université de l’Ontario français Act, 2017 | `17u34/` | 4 | 2017-12-14 to 2023-12-04 | 41 |
| 18b10 | Back to Class Act (York University), 2018 | `18b10/` | 1 | 2018-07-25 to 2018-07-25 | 24 |
| 18c06 | Correctional Services and Reintegration Act, 2018 | `18c06/` | 4 | 2018-05-07 to 2024-03-06 | 4 |
| 18c12 | Cannabis Licence Act, 2018 | `18c12/` | 12 | 2018-10-17 to 2025-05-12 | 54 |
| 18c13 | Cap and Trade Cancellation Act, 2018 | `18c13/` | 5 | 2018-10-31 to 2025-11-27 | 19 |
| 18f03 | Forensic Laboratories Act, 2018 | `18f03/` | 2 | 2018-03-08 to 2024-01-01 | 14 |
| 18f04 | Fairness in Procurement Act, 2018 | `18f04/` | 3 | 2018-03-08 to 2018-04-30 | 11 |
| 18g09 | Government Contract Wages Act, 2018 | `18g09/` | 1 | 2018-05-08 to 2018-05-08 | 44 |
| 18h10 | Hydro One Accountability Act, 2018 | `18h10/` | 2 | 2018-07-25 to 2018-08-15 | 13 |
| 18i17 | Interim Appropriation for 2019-2020 Act, 2018 | `18i17/` | 3 | 2018-12-06 to 2020-03-19 | 0 |
| 18m03 | Missing Persons Act, 2018 | `18m03/` | 4 | 2018-03-08 to 2024-04-01 | 15 |
| 18m06 | Ministry of Community Safety and Correctional Services Act, 2018 | `18m06/` | 2 | 2018-05-07 to 2019-05-29 | 3 |
| 18o03a | Ontario Policing Discipline Tribunal Act, 2018 | `18o03a/` | 2 | 2018-03-08 to 2019-03-26 | 0 |
| 18o03b | Ontario Special Investigations Unit Act, 2018 | `18o03b/` | 2 | 2018-03-08 to 2019-03-26 | 0 |
| 18o08 | Ontario Loan Act, 2018 | `18o08/` | 1 | 2018-05-08 to 2018-05-08 | 5 |
| 18o17a | Ontario Loan Act, 2018 (No. 2) | `18o17a/` | 1 | 2018-12-06 to 2018-12-06 | 5 |
| 18o17b | Ontario Place Corporation Repeal Act, 2018 | `18o17b/` | 1 | 2018-12-06 to 2018-12-06 | 3 |
| 18p03a | Police Services Act, 2018 | `18p03a/` | 3 | 2018-03-08 to 2019-03-26 | 0 |
| 18p03b | Policing Oversight Act, 2018 | `18p03b/` | 2 | 2018-03-08 to 2019-03-26 | 0 |
| 18p05 | Pay Transparency Act, 2018 | `18p05/` | 3 | 2018-05-07 to 2023-06-08 | 4 |
| 18r01 | Rowan’s Law (Concussion Safety), 2018 | `18r01/` | 4 | 2018-03-07 to 2022-01-01 | 11 |
| 18r08 | Revenue Integrity Act, 2018 | `18r08/` | 1 | 2018-05-08 to 2018-05-08 | 3 |
| 18s02 | Supply Act, 2018 | `18s02/` | 2 | 2018-03-07 to 2019-04-01 | 0 |
| 18s17a | Special Hockey Day Act, 2018 | `18s17a/` | 1 | 2018-12-06 to 2018-12-06 | 4 |
| 18s17b | Supplementary Interim Appropriation for 2018-2019 Act, 2018 | `18s17b/` | 2 | 2018-12-06 to 2019-03-26 | 0 |
| 18w10 | White Pines Wind Project Termination Act, 2018 | `18w10/` | 2 | 2018-07-25 to 2018-12-06 | 10 |
| 19a15 | Alcohol and Gaming Commission of Ontario Act, 2019 | `19a15/` | 5 | 2019-12-10 to 2025-05-12 | 27 |
| 19c01 | Community Safety and Policing Act, 2019 | `19c01/` | 11 | 2019-03-26 to 2025-06-05 | 265 |
| 19c05 | Connecting Care Act, 2019 | `19c05/` | 22 | 2019-04-18 to 2026-04-24 | 93 |
| 19c07 | Cannabis Taxation Coordination Act, 2019 | `19c07/` | 1 | 2019-05-29 to 2019-05-29 | 4 |
| 19c07b | Combative Sports Act, 2019 | `19c07b/` | 4 | 2019-05-29 to 2025-01-01 | 54 |
| 19c07c | Crown Liability and Proceedings Act, 2019 | `19c07c/` | 6 | 2019-05-29 to 2023-05-18 | 36 |
| 19e15 | Egyptian Heritage Month Act, 2019 | `19e15/` | 1 | 2019-12-10 to 2019-12-10 | 2 |
| 19f07a | Federal Carbon Tax Transparency Act, 2019 | `19f07a/` | 2 | 2019-05-29 to 2019-08-30 | 8 |
| 19f07b | Financial Professionals Title Protection Act, 2019 | `19f07b/` | 5 | 2019-05-29 to 2023-05-18 | 20 |
| 19f07c | Fiscal Sustainability, Transparency and Accountability Act, 2019 | `19f07c/` | 6 | 2019-05-29 to 2026-04-24 | 22 |
| 19f14 | Foreign Cultural Objects Immunity from Seizure Act, 2019 | `19f14/` | 2 | 2019-12-10 to 2022-04-07 | 5 |
| 19h15 | Hellenic Heritage Month Act, 2019 | `19h15/` | 1 | 2019-12-10 to 2019-12-10 | 4 |
| 19i15 | Interim Appropriation for 2020-2021 Act, 2019 | `19i15/` | 2 | 2020-04-01 to 2021-03-11 | 0 |
| 19l14 | Local Planning Appeal Support Centre Repeal Act, 2019 | `19l14/` | 2 | 2019-12-10 to 2020-06-10 | 0 |
| 19l15a | Liquor Control Board of Ontario Act, 2019 | `19l15a/` | 5 | 2019-12-10 to 2026-04-01 | 23 |
| 19l15b | Liquor Licence and Control Act, 2019 | `19l15b/` | 9 | 2019-12-10 to 2025-12-11 | 91 |
| 19m07 | Modernizing the Skilled Trades and Apprenticeship Act, 2019 | `19m07/` | 4 | 2019-05-29 to 2022-01-01 | 0 |
| 19m17 | Mental Health and Addictions Centre of Excellence Act, 2019 | `19m17/` | 3 | 2019-12-12 to 2020-07-08 | 9 |
| 19o07 | Ontario Loan Act, 2019 | `19o07/` | 1 | 2019-05-29 to 2019-05-29 | 5 |
| 19o17 | Opioid Damages and Health Care Costs Recovery Act, 2019 | `19o17/` | 9 | 2019-12-12 to 2024-06-06 | 21 |
| 19p07 | PTSD Awareness Day Act, 2019 | `19p07/` | 1 | 2019-05-29 to 2019-05-29 | 4 |
| 19p12 | Protecting a Sustainable Public Sector for Future Generations Act, 2019 | `19p12/` | 8 | 2019-11-07 to 2024-02-23 | 0 |
| 19p13 | Provincial Animal Welfare Services Act, 2019 | `19p13/` | 8 | 2019-12-05 to 2026-06-02 | 73 |
| 19p15 | Provincial Day of Action on Litter Act, 2019 | `19p15/` | 1 | 2019-12-10 to 2019-12-10 | 4 |
| 19p16 | Poet Laureate of Ontario Act (In Memory of Gord Downie), 2019 | `19p16/` | 2 | 2019-12-12 to 2024-06-06 | 7 |
| 19s01 | Special Investigations Unit Act, 2019 | `19s01/` | 6 | 2019-03-26 to 2024-04-01 | 46 |
| 19s02 | Supply Act, 2019 | `19s02/` | 2 | 2019-03-26 to 2020-04-01 | 0 |
| 19s07 | Simpler, Faster, Better Services Act, 2019 | `19s07/` | 3 | 2019-05-29 to 2024-06-28 | 12 |
| 19s15a | Supplementary Interim Appropriation for 2019-2020 Act, 2019 | `19s15a/` | 2 | 2019-12-10 to 2020-03-19 | 0 |
| 19s15b | Supply Chain Management Act (Government, Broader Public Sector and Health Sector Entities), 2019 | `19s15b/` | 5 | 2019-12-10 to 2022-04-14 | 23 |
| 19t07 | Tribunal Adjudicative Records Act, 2019 | `19t07/` | 3 | 2019-05-29 to 2019-07-01 | 12 |
| 20a07 | Alternative Filing Methods for Business Act, 2020 | `20a07/` | 1 | 2020-05-12 to 2020-05-12 | 12 |
| 20b12 | Building Transit Faster Act, 2020 | `20b12/` | 6 | 2020-07-08 to 2025-11-27 | 87 |
| 20c30 | Compassionate Care Act, 2020 | `20c30/` | 1 | 2020-12-02 to 2020-12-02 | 7 |
| 20c36 | Credit Unions and Caisses Populaires Act, 2020 | `20c36/` | 10 | 2020-12-08 to 2026-07-01 | 302 |
| 20d08 | Defibrillator Registration and Public Access Act, 2020 | `20d08/` | 1 | 2020-06-18 to 2020-06-18 | 3 |
| 20e32 | Eating Disorders Awareness Week Act, 2020 | `20e32/` | 1 | 2020-12-08 to 2020-12-08 | 4 |
| 20f36 | Film Content Information Act, 2020 | `20f36/` | 2 | 2020-12-08 to 2021-06-08 | 23 |
| 20h05 | Hearings in Tribunal Proceedings (Temporary Measures) Act, 2020 | `20h05/` | 1 | 2020-03-25 to 2020-03-25 | 10 |
| 20i36a | Innovation Centre Governance Act, 2020 | `20i36a/` | 2 | 2020-12-08 to 2021-10-19 | 6 |
| 20i36b | Interim Appropriation for 2021-2022 Act, 2020 | `20i36b/` | 3 | 2020-12-08 to 2022-03-21 | 0 |
| 20l11 | Legal Aid Services Act, 2020 | `20l11/` | 5 | 2020-07-08 to 2022-03-01 | 52 |
| 20m18 | Modernizing Ontario for People and Businesses Act, 2020 | `20m18/` | 8 | 2020-07-21 to 2025-12-11 | 14 |
| 20m27 | Magna Carta Day Act (In Memory of Julia Munro, MPP), 2020 | `20m27/` | 1 | 2020-11-30 to 2020-11-30 | 4 |
| 20o05 | Ontario Loan Act, 2020 | `20o05/` | 1 | 2020-03-25 to 2020-03-25 | 5 |
| 20o16 | Ontario Mortgage and Housing Corporation Repeal Act, 2020 | `20o16/` | 2 | 2020-07-21 to 2021-03-31 | 11 |
| 20o34 | Ontario Highway Transport Board Repeal Act, 2020 | `20o34/` | 2 | 2020-12-08 to 2021-07-01 | 8 |
| 20o36 | Ontario Loan Act, 2020 (No. 2) | `20o36/` | 1 | 2020-12-08 to 2020-12-08 | 5 |
| 20p34 | Public Vehicles Repeal Act, 2020 | `20p34/` | 1 | 2020-12-08 to 2020-12-08 | 5 |
| 20r17 | Reopening Ontario (A Flexible Response to COVID-19) Act, 2020 | `20r17/` | 3 | 2020-07-21 to 2020-10-01 | 22 |
| 20s02 | Supply Act, 2020 | `20s02/` | 2 | 2020-03-19 to 2021-04-01 | 0 |
| 20s09 | Security from Trespass and Protecting Food Safety Act, 2020 | `20s09/` | 3 | 2020-06-18 to 2020-12-05 | 26 |
| 20s20 | Stop Cyberbullying in Ontario Day Act, 2020 | `20s20/` | 1 | 2020-09-24 to 2020-09-24 | 4 |
| 20s22 | Somali Heritage Week Act, 2020 | `20s22/` | 1 | 2020-10-01 to 2020-10-01 | 4 |
| 20s24 | Soldiers’ Aid Commission Act, 2020 | `20s24/` | 4 | 2020-11-12 to 2024-11-19 | 16 |
| 20s26 | Supporting Ontario’s Recovery Act, 2020 | `20s26/` | 1 | 2020-11-20 to 2020-11-20 | 8 |
| 20s31 | Supporting Local Restaurants Act, 2020 | `20s31/` | 2 | 2020-12-02 to 2020-12-19 | 15 |
| 20s36 | Supplementary Interim Appropriation for 2020-2021 Act, 2020 | `20s36/` | 2 | 2020-12-08 to 2021-03-11 | 0 |
| 20t18 | Transit-Oriented Communities Act, 2020 | `20t18/` | 5 | 2020-07-21 to 2025-11-27 | 11 |
| 20t19 | Tibetan Heritage Month Act, 2020 | `20t19/` | 1 | 2020-09-24 to 2020-09-24 | 4 |
| 21a21a | Accommodation Sector Registration of Guests Act, 2021 | `21a21a/` | 2 | 2021-06-03 to 2026-01-01 | 13 |
| 21a21b | Anti-Human Trafficking Strategy Act, 2021 | `21a21b/` | 1 | 2021-06-03 to 2021-06-03 | 9 |
| 21a38 | Anti-Asian Racism Education Month Act, 2021 | `21a38/` | 1 | 2021-12-09 to 2021-12-09 | 4 |
| 21b02 | Building Broadband Faster Act, 2021 | `21b02/` | 7 | 2021-04-12 to 2026-04-01 | 36 |
| 21b28 | Building Opportunities in the Skilled Trades Act, 2021 | `21b28/` | 8 | 2021-06-03 to 2025-04-02 | 71 |
| 21c17 | Convenience Store Week Act, 2021 | `21c17/` | 1 | 2021-05-20 to 2021-05-20 | 4 |
| 21c18 | COPD Awareness Day Act, 2021 | `21c18/` | 1 | 2021-06-03 to 2021-06-03 | 4 |
| 21c27 | Covid-19 Vaccination Reporting Act, 2021 | `21c27/` | 1 | 2021-06-03 to 2021-06-03 | 10 |
| 21e41 | Endometriosis Awareness Month Act, 2021 | `21e41/` | 1 | 2021-12-09 to 2021-12-09 | 4 |
| 21e42 | Emancipation Month Act, 2021 | `21e42/` | 1 | 2021-12-09 to 2021-12-09 | 4 |
| 21f15 | Filipino Heritage Month Act, 2021 | `21f15/` | 1 | 2021-05-20 to 2021-05-20 | 4 |
| 21f20 | Front-line and Essential Service Worker Week Act, 2021 | `21f20/` | 1 | 2021-06-03 to 2021-06-03 | 4 |
| 21f30 | Food Day Canada in Ontario (in Honour of Anita Stewart) Act, 2021 | `21f30/` | 1 | 2021-06-03 to 2021-06-03 | 4 |
| 21f39 | Fixing Long-Term Care Act, 2021 | `21f39/` | 8 | 2021-12-09 to 2025-12-11 | 207 |
| 21h27 | Health and Supportive Care Providers Oversight Authority Act, 2021 | `21h27/` | 3 | 2021-06-03 to 2024-12-01 | 68 |
| 21i08 | Invest Ontario Act, 2021 | `21i08/` | 2 | 2021-04-27 to 2022-03-01 | 30 |
| 21i40 | Interim Appropriation for 2022-2023 Act, 2021 | `21i40/` | 3 | 2021-12-09 to 2023-03-22 | 0 |
| 21k16 | Keeping Polystyrene Out of Ontario's Lakes and Rivers Act, 2021 | `21k16/` | 1 | 2021-05-20 to 2021-05-20 | 5 |
| 21l12 | Lupus Awareness Day Act, 2021 | `21l12/` | 1 | 2021-05-12 to 2021-05-12 | 4 |
| 21n25 | Northern Ontario School of Medicine University Act, 2021 | `21n25/` | 2 | 2021-06-03 to 2022-04-01 | 22 |
| 21n29 | Nikola Tesla Day Act, 2021 | `21n29/` | 1 | 2021-06-03 to 2021-06-03 | 4 |
| 21n36 | Non-Profit Sector Appreciation Week Act, 2021 | `21n36/` | 1 | 2021-12-09 to 2021-12-09 | 4 |
| 21o04 | Ontario Land Tribunal Act, 2021 | `21o04/` | 3 | 2021-04-19 to 2022-11-28 | 33 |
| 21o06 | Occupational Safety and Health Day Act, 2021 | `21o06/` | 1 | 2021-04-27 to 2021-04-27 | 4 |
| 21o07 | Ontario Day Act, 2021 | `21o07/` | 1 | 2021-04-27 to 2021-04-27 | 4 |
| 21o08 | Ontario Loan Act, 2021 | `21o08/` | 1 | 2021-04-27 to 2021-04-27 | 5 |
| 21p24 | Persian Heritage Month Act, 2021 | `21p24/` | 1 | 2021-06-03 to 2021-06-03 | 4 |
| 21p27 | Psychology and Applied Behaviour Analysis Act, 2021 | `21p27/` | 4 | 2021-06-03 to 2026-01-01 | 18 |
| 21p37 | Polish Heritage Month Act, 2021 | `21p37/` | 1 | 2021-12-09 to 2021-12-09 | 4 |
| 21r14 | Recovery Month Act, 2021 | `21r14/` | 1 | 2021-05-12 to 2021-05-12 | 4 |
| 21s01 | Supply Act, 2021 | `21s01/` | 2 | 2021-03-11 to 2022-04-01 | 0 |
| 21s08 | Securities Commission Act, 2021 | `21s08/` | 7 | 2021-04-27 to 2025-09-01 | 42 |
| 21s19 | Scottish Heritage Day Act, 2021 | `21s19/` | 1 | 2021-06-03 to 2021-06-03 | 4 |
| 21s22 | Sickle Cell Disease Awareness Day and Thalassemia Awareness Day Act, 2021 | `21s22/` | 1 | 2021-06-03 to 2021-06-03 | 5 |
| 21s23 | Senior Volunteer Appreciation Week Act, 2021 | `21s23/` | 1 | 2021-06-03 to 2021-06-03 | 4 |
| 21s40 | Supplementary Interim Appropriation for 2021-2022 Act, 2021 | `21s40/` | 2 | 2021-12-09 to 2022-03-21 | 0 |
| 21t11 | Tamil Genocide Education Week Act, 2021 | `21t11/` | 1 | 2021-05-12 to 2021-05-12 | 4 |
| 21t26 | Towing and Storage Safety and Enforcement Act, 2021 | `21t26/` | 9 | 2021-06-03 to 2026-07-01 | 69 |
| 21u25 | Université de Hearst Act, 2021 | `21u25/` | 3 | 2021-06-03 to 2024-06-06 | 22 |
| 21y32 | York Region Wastewater Act, 2021 | `21y32/` | 2 | 2021-10-20 to 2022-11-28 | 0 |
| 22a02 | At Your Service Act, 2022 | `22a02/` | 2 | 2022-03-03 to 2025-12-11 | 10 |
| 22a04 | Armenian Heritage Month Act, 2022 | `22a04/` | 1 | 2022-03-31 to 2022-03-31 | 4 |
| 22b02 | Building Ontario Businesses Initiative Act, 2022 | `22b02/` | 4 | 2022-03-03 to 2026-03-30 | 0 |
| 22d07 | Digital Platform Workers’ Rights Act, 2022 | `22d07/` | 3 | 2022-04-11 to 2025-07-01 | 69 |
| 22d24 | Duffins Rouge Agricultural Preserve Repeal Act, 2022 | `22d24/` | 3 | 2022-12-08 to 2023-12-06 | 0 |
| 22g08 | Green Shirt Day Act, 2022 | `22g08/` | 1 | 2022-04-11 to 2022-04-11 | 2 |
| 22h06 | Hungarian Heritage Month Act, 2022 | `22h06/` | 1 | 2022-04-11 to 2022-04-11 | 4 |
| 22i23 | Interim Appropriation for 2023-2024 Act, 2022 | `22i23/` | 3 | 2022-12-08 to 2024-03-21 | 0 |
| 22k10 | Keeping Ontario Open for Business Act, 2022 | `22k10/` | 1 | 2022-04-14 to 2022-04-14 | 20 |
| 22k19 | Keeping Students in Class Act, 2022, S.O. 2022 | `22k19/` | 2 | 2022-11-03 to 2022-11-14 | 0 |
| 22k20 | Keeping Students in Class Repeal Act, 2022 | `22k20/` | 1 | 2022-11-14 to 2022-11-14 | 5 |
| 22m14 | Myasthenia Gravis Month Act, 2022 | `22m14/` | 1 | 2022-04-14 to 2022-04-14 | 4 |
| 22o05 | Ontario Cadets Week Act, 2022 | `22o05/` | 1 | 2022-04-11 to 2022-04-11 | 4 |
| 22o17 | Ontario Loan Act, 2022 | `22o17/` | 1 | 2022-09-08 to 2022-09-08 | 5 |
| 22p01 | Provincial Day of Service Act, 2022 | `22p01/` | 1 | 2022-03-03 to 2022-03-03 | 4 |
| 22p11 | Personal Protective Equipment Supply and Production Act, 2022 | `22p11/` | 1 | 2022-04-14 to 2022-04-14 | 4 |
| 22s03 | Supply Act, 2022 | `22s03/` | 2 | 2022-03-21 to 2023-04-01 | 0 |
| 22s11 | Supporting Retention in Public Services Act, 2022 | `22s11/` | 1 | 2022-04-14 to 2022-04-14 | 14 |
| 22s21 | Supporting Growth and Housing in York and Durham Regions Act, 2022 | `22s21/` | 3 | 2022-11-28 to 2025-10-31 | 89 |
| 22s23 | Supplementary Interim Appropriation for 2022-2023 Act, 2022 | `22s23/` | 2 | 2022-12-08 to 2023-03-22 | 0 |
| 23c23 | Consumer Protection Act, 2023 | `23c23/` | 1 | 2023-12-06 to 2023-12-06 | 4 |
| 23d22 | Duffins Rouge Agricultural Preserve Act, 2023 | `23d22/` | 1 | 2023-12-06 to 2023-12-06 | 4 |
| 23g17 | GO Transit Station Funding Act, 2023 | `23g17/` | 2 | 2023-12-04 to 2025-11-27 | 24 |
| 23h13 | Hazel McCallion Act (Peel Restructuring), 2023 | `23h13/` | 2 | 2023-06-08 to 2024-06-06 | 13 |
| 23i04 | Integrated Community Health Services Centres Act, 2023 | `23i04/` | 2 | 2023-05-18 to 2023-09-25 | 69 |
| 23i09 | International Recovery of Child Support and Family Maintenance Convention Act, 2023 | `23i09/` | 1 | 2023-06-08 to 2023-06-08 | 27 |
| 23i21 | Interim Appropriation for 2024-2025 Act, 2023 | `23i21/` | 3 | 2023-12-04 to 2025-05-29 | 0 |
| 23o02 | Ontario Society for the Prevention of Cruelty to Animals Corporation Act, 2023 | `23o02/` | 2 | 2023-03-22 to 2024-04-12 | 0 |
| 23o24 | Official Plan Adjustments Act, 2023 | `23o24/` | 2 | 2023-12-06 to 2024-05-16 | 7 |
| 23p09 | Protecting Farmers from Non-Payment Act (Regulating Agricultural Product Dealers and Storage Operators), 2023 | `23p09/` | 2 | 2023-06-08 to 2026-01-01 | 122 |
| 23q07 | Queen's Park Restoration Secretariat Act, 2023 | `23q07/` | 2 | 2023-05-18 to 2023-07-31 | 16 |
| 23r25a | Recovery Through Growth Act (City of Toronto), 2023 | `23r25a/` | 1 | 2023-12-06 to 2023-12-06 | 6 |
| 23r25b | Rebuilding Ontario Place Act, 2023 | `23r25b/` | 4 | 2023-12-06 to 2025-11-27 | 28 |
| 23s01 | Supporting Manufacturing in St. Thomas Act, 2023 | `23s01/` | 3 | 2023-03-02 to 2023-12-04 | 16 |
| 23s03 | Supply Act, 2023 | `23s03/` | 2 | 2023-03-22 to 2024-04-01 | 0 |
| 23s21 | Supplementary Interim Appropriation for 2023-2024 Act, 2023 | `23s21/` | 2 | 2023-12-04 to 2024-03-21 | 0 |
| 23v21 | Vaping Product Taxation Coordination Act, 2023 | `23v21/` | 1 | 2023-12-04 to 2023-12-04 | 4 |
| 24b12 | Building Ontario Fund Act, 2024 | `24b12/` | 3 | 2024-05-16 to 2026-04-01 | 37 |
| 24b25 | Building Highways Faster Act, 2024 | `24b25/` | 1 | 2024-11-25 to 2024-11-25 | 22 |
| 24c06 | Croatian Heritage Day Act, 2024 | `24c06/` | 1 | 2024-04-25 to 2024-04-25 | 4 |
| 24c27a | Community Care and Recovery Act, 2024 | `24c27a/` | 2 | 2024-12-04 to 2025-04-01 | 8 |
| 24c27b | Community Safety and Crime Prevention Month Act, 2024 | `24c27b/` | 1 | 2024-12-04 to 2024-12-04 | 4 |
| 24c37 | Chinese Heritage Month Act, 2024 | `24c37/` | 1 | 2024-12-19 to 2024-12-19 | 4 |
| 24e24 | Enhancing Digital Security and Trust Act, 2024 | `24e24/` | 2 | 2024-11-25 to 2025-01-29 | 19 |
| 24g13 | Garrett’s Legacy Act (Requirements for Movable Soccer Goals), 2024 | `24g13/` | 1 | 2024-06-06 to 2024-06-06 | 3 |
| 24g35 | Group of Seven Day Act, 2024 | `24g35/` | 1 | 2024-12-19 to 2024-12-19 | 4 |
| 24g38 | Growing Agritourism Act, 2024 | `24g38/` | 1 | 2024-12-19 to 2024-12-19 | 7 |
| 24h25 | Highway 413 Act, 2024 | `24h25/` | 1 | 2024-11-25 to 2024-11-25 | 20 |
| 24h29 | Heart Valve Disease Awareness Act, 2024 | `24h29/` | 1 | 2024-12-19 to 2024-12-19 | 5 |
| 24i20a | iGaming Ontario Act, 2024 | `24i20a/` | 4 | 2024-11-06 to 2026-04-01 | 31 |
| 24i20b | Interim Appropriation for 2025-2026 Act, 2024 | `24i20b/` | 3 | 2024-11-06 to 2026-04-15 | 0 |
| 24i31 | Injured Workers Day Act, 2024 | `24i31/` | 1 | 2024-12-19 to 2024-12-19 | 4 |
| 24i32 | Improving Dementia Care in Ontario Act, 2024 | `24i32/` | 1 | 2024-12-19 to 2024-12-19 | 5 |
| 24m05 | Murray Whetung Community Service Award Act, 2024 | `24m05/` | 1 | 2024-04-25 to 2024-04-25 | 3 |
| 24o12 | Ontario Loan Act, 2024 | `24o12/` | 1 | 2024-05-16 to 2024-05-16 | 5 |
| 24o36 | Orthodox Christian Week Act, 2024 | `24o36/` | 1 | 2024-12-19 to 2024-12-19 | 4 |
| 24p09 | Protecting Against Carbon Taxes Act, 2024 | `24p09/` | 1 | 2024-05-16 to 2024-05-16 | 23 |
| 24p34 | Planning for Your Silver Years Awareness Week Act, 2024 | `24p34/` | 1 | 2024-12-19 to 2024-12-19 | 4 |
| 24p39 | Persons Day Act, 2024 | `24p39/` | 1 | 2024-12-19 to 2024-12-19 | 4 |
| 24s04 | Supply Act, 2024 | `24s04/` | 2 | 2024-03-21 to 2025-04-01 | 0 |
| 24s20 | Supplementary Interim Appropriation for 2024-2025 Act, 2024 | `24s20/` | 2 | 2024-11-06 to 2025-05-29 | 0 |
| 24s30 | Seniors Month Act, 2024 | `24s30/` | 1 | 2024-12-19 to 2024-12-19 | 4 |
| 24s41 | Skilled Trades Week Act, 2024 | `24s41/` | 1 | 2024-12-19 to 2024-12-19 | 4 |
| 24u40 | Ukrainian Heritage Month Act, 2024 | `24u40/` | 1 | 2024-12-19 to 2024-12-19 | 4 |
| 24v15 | Veterinary Professionals Act, 2024 | `24v15/` | 1 | 2024-06-06 to 2024-06-06 | 15 |
| 25b03 | Buy Ontario, Buy Canadian Day Act, 2025 | `25b03/` | 1 | 2025-06-05 to 2025-06-05 | 4 |
| 25b27 | Buy Ontario Act (Public Sector Procurement), 2025 | `25b27/` | 1 | 2025-12-11 to 2025-12-11 | 16 |
| 25b28 | Barrie - Oro-Medonte - Springwater Boundary Adjustment Act, 2025 | `25b28/` | 2 | 2025-12-11 to 2026-01-01 | 14 |
| 25e21 | Ethiopian Heritage Month Act, 2025 | `25e21/` | 1 | 2025-12-11 to 2025-12-11 | 4 |
| 25g17 | Geologic Carbon Storage Act, 2025 | `25g17/` | 2 | 2025-12-03 to 2026-01-01 | 66 |
| 25h07 | Health Care Staffing Agency Reporting Act, 2025 | `25h07/` | 1 | 2025-06-05 to 2025-06-05 | 3 |
| 25h26 | Hospitality Workers Appreciation Day Act, 2025 | `25h26/` | 1 | 2025-12-11 to 2025-12-11 | 4 |
| 25i15 | Interim Appropriation for 2026-2027 Act, 2025 | `25i15/` | 2 | 2025-11-27 to 2026-04-01 | 8 |
| 25k25 | Kids’ Online Safety and Privacy Month Act, 2025 | `25k25/` | 1 | 2025-12-11 to 2025-12-11 | 4 |
| 25m06 | Measures Respecting Premises with Illegal Drug Activity Act, 2025 | `25m06/` | 2 | 2025-06-05 to 2026-07-01 | 17 |
| 25m10 | Members of Executive Council Recognition Act, 2025 | `25m10/` | 1 | 2025-06-05 to 2025-06-05 | 5 |
| 25o03 | Ontario Free Trade and Mobility Act, 2025 | `25o03/` | 1 | 2025-06-05 to 2025-06-05 | 10 |
| 25o10 | Ontario Loan Act, 2025 | `25o10/` | 1 | 2025-06-05 to 2025-06-05 | 5 |
| 25o18 | Ontario University Athletics Week Act, 2025 | `25o18/` | 1 | 2025-12-11 to 2025-12-11 | 4 |
| 25p08 | Primary Care Act, 2025 | `25p08/` | 1 | 2025-06-05 to 2025-06-05 | 8 |
| 25r05 | Restricting Public Consumption of Illegal Substances Act, 2025 | `25r05/` | 1 | 2025-06-05 to 2025-06-05 | 13 |
| 25s01 | Supply Act, 2025 | `25s01/` | 2 | 2025-05-29 to 2026-04-01 | 0 |
| 25s04a | Special Economic Zones Act, 2025 | `25s04a/` | 1 | 2025-06-05 to 2025-06-05 | 8 |
| 25s04b | Species Conservation Act, 2025 | `25s04b/` | 3 | 2025-06-05 to 2026-03-30 | 70 |
| 25s15 | Supplementary Interim Appropriation for 2025-2026 Act, 2025 | `25s15/` | 2 | 2025-11-27 to 2026-04-15 | 0 |
| 25w14 | Water and Wastewater Public Corporations Act, 2025 | `25w14/` | 3 | 2025-11-27 to 2026-06-19 | 26 |
| 26b02 | Bremner Boulevard Act, 2026 | `26b02/` | 1 | 2026-04-24 to 2026-04-24 | 7 |
| 26b09 | Building Billy Bishop Airport Act, 2026 | `26b09/` | 1 | 2026-06-02 to 2026-06-02 | 16 |
| 26c07 | Constable Joe MacDonald Public Safety Officers’ Survivors Scholarship Fund Act, 2026 | `26c07/` | 1 | 2026-06-02 to 2026-06-02 | 3 |
| 26f08 | Fare Alignment and Seamless Transit Act, 2026 | `26f08/` | 1 | 2026-06-02 to 2026-06-02 | 19 |
| 26o02 | Ontario Loan Act, 2026 | `26o02/` | 1 | 2026-04-24 to 2026-04-24 | 5 |
| 26s01 | Supply Act, 2026 | `26s01/` | 1 | 2026-04-15 to 2026-04-15 | 8 |
| 86e23 | English and Wabigoon River Systems Mercury Contamination Settlement Agreement Act, 1986 | `86e23/` | 1 | 1986-07-28 to 1986-07-28 | 46 |
| 90a02 | Absconding Debtors Act | `90a02/` | 8 | 1990-12-31 to 2021-09-01 | 19 |
| 90a03 | Absentees Act | `90a03/` | 3 | 2000-03-01 to 2006-06-22 | 9 |
| 90a05 | Accumulations Act | `90a05/` | 3 | 1993-12-02 to 2009-12-15 | 6 |
| 90a06 | Administration of Justice Act | `90a06/` | 10 | 2000-12-06 to 2021-09-01 | 16 |
| 90a07 | Age of Majority and Accountability Act | `90a07/` | 3 | 1990-12-31 to 2007-07-25 | 11 |
| 90a08 | Aggregate Resources Act | `90a08/` | 15 | 2003-01-01 to 2021-06-01 | 98 |
| 90a09 | Agricultural and Horticultural Organizations Act | `90a09/` | 9 | 2003-01-01 to 2025-07-01 | 40 |
| 90a11 | Agricultural Rehabilitation and Development Act (Ontario) | `90a11/` | 3 | 1996-06-27 to 2006-06-27 | 0 |
| 90a13 | Agricultural Research and Innovation Ontario Act | `90a13/` | 11 | 1999-03-31 to 2026-04-01 | 29 |
| 90a14 | Agricultural Tile Drainage Installation Act | `90a14/` | 3 | 1999-12-22 to 2009-12-15 | 15 |
| 90a15 | Airports Act | `90a15/` | 1 | 2003-01-01 to 2003-01-01 | 4 |
| 90a16 | Alcoholism and Drug Addiction Research Foundation Act | `90a16/` | 3 | 1990-12-31 to 2006-06-22 | 18 |
| 90a17 | Algonquin Forestry Authority Act | `90a17/` | 17 | 2002-11-26 to 2026-04-01 | 22 |
| 90a18 | Aliens’ Real Property Act | `90a18/` | 1 | 1990-12-31 to 1990-12-31 | 3 |
| 90a19 | Ambulance Act | `90a19/` | 19 | 2004-01-01 to 2021-10-19 | 51 |
| 90a21 | Anatomy Act | `90a21/` | 4 | 2003-01-01 to 2016-12-05 | 15 |
| 90a22 | Animals for Research Act | `90a22/` | 11 | 1999-12-22 to 2026-06-02 | 25 |
| 90a23 | Apportionment Act | `90a23/` | 1 | 1990-12-31 to 1990-12-31 | 7 |
| 90a25 | Arboreal Emblem Act | `90a25/` | 1 | 1990-12-31 to 1990-12-31 | 2 |
| 90a26 | Architects Act | `90a26/` | 9 | 2003-01-15 to 2025-01-01 | 58 |
| 90a27 | Archives Act | `90a27/` | 3 | 1999-12-22 to 2007-09-01 | 0 |
| 90a28 | Art Gallery of Ontario Act | `90a28/` | 8 | 2003-01-01 to 2023-06-08 | 21 |
| 90a30 | Arts Council Act | `90a30/` | 9 | 1990-12-31 to 2024-06-06 | 14 |
| 90a31 | Assessment Act | `90a31/` | 50 | 2003-01-01 to 2026-01-01 | 84 |
| 90a32 | Assessment Review Board Act | `90a32/` | 12 | 2003-01-01 to 2025-07-01 | 15 |
| 90a33 | Assignments and Preferences Act | `90a33/` | 10 | 2001-06-29 to 2022-03-01 | 41 |
| 90a34 | Athletics Control Act | `90a34/` | 10 | 1998-12-18 to 2025-01-01 | 0 |
| 90a35 | Auditor General Act | `90a35/` | 15 | 1999-12-14 to 2024-03-06 | 47 |
| 90b01 | Bail Act | `90b01/` | 8 | 1990-12-31 to 2026-08-17 | 14 |
| 90b02 | Bailiffs Act | `90b02/` | 19 | 2003-01-01 to 2022-03-01 | 40 |
| 90b03 | Barristers Act | `90b03/` | 6 | 1990-12-31 to 2024-03-06 | 4 |
| 90b04 | Beds of Navigable Waters Act | `90b04/` | 1 | 2002-11-26 to 2002-11-26 | 5 |
| 90b05 | Beef Cattle Marketing Act | `90b05/` | 5 | 1999-12-22 to 2019-12-10 | 22 |
| 90b06 | Bees Act | `90b06/` | 4 | 2003-01-01 to 2019-12-10 | 27 |
| 90b07 | Blind Persons’ Rights Act | `90b07/` | 1 | 1990-12-31 to 1990-12-31 | 7 |
| 90b10 | Boundaries Act | `90b10/` | 3 | 2002-11-26 to 2022-12-31 | 24 |
| 90b12 | Bridges Act | `90b12/` | 2 | 1997-04-01 to 2006-06-22 | 5 |
| 90b14 | Bulk Sales Act | `90b14/` | 5 | 2003-01-01 to 2017-03-22 | 0 |
| 90b16 | Business Corporations Act | `90b16/` | 53 | 2004-01-01 to 2025-10-01 | 277 |
| 90b17 | Business Names Act | `90b17/` | 12 | 2001-06-29 to 2021-10-19 | 31 |
| 90b18 | Business Practices Act | `90b18/` | 2 | 2002-12-13 to 2005-07-30 | 0 |
| 90b19 | Business Records Protection Act | `90b19/` | 2 | 1990-12-31 to 2006-06-22 | 3 |
| 90c01 | Cancer Act | `90c01/` | 7 | 2002-11-26 to 2020-04-01 | 0 |
| 90c04 | Cemeteries Act (Revised) | `90c04/` | 12 | 2003-01-01 to 2012-07-01 | 0 |
| 90c05 | Centennial Centre of Science and Technology Act | `90c05/` | 9 | 1993-12-02 to 2024-04-25 | 12 |
| 90c06 | Certification of Titles Act | `90c06/` | 2 | 2004-01-01 to 2009-12-15 | 0 |
| 90c07 | Change of Name Act | `90c07/` | 26 | 2001-01-02 to 2026-07-01 | 21 |
| 90c08 | Charitable Gifts Act | `90c08/` | 5 | 1990-12-31 to 2009-12-15 | 0 |
| 90c09 | Charitable Institutions Act | `90c09/` | 9 | 2002-11-26 to 2010-07-01 | 0 |
| 90c10 | Charities Accounting Act | `90c10/` | 5 | 2003-01-01 to 2023-12-04 | 22 |
| 90c11 | Child and Family Services Act | `90c11/` | 45 | 2003-01-01 to 2018-04-30 | 0 |
| 90c12 | Children’s Law Reform Act | `90c12/` | 29 | 2001-06-29 to 2025-12-11 | 100 |
| 90c14 | Collection and Debt Settlement Services Act | `90c14/` | 30 | 2002-12-13 to 2023-12-06 | 52 |
| 90c15 | Colleges Collective Bargaining Act | `90c15/` | 5 | 2003-04-01 to 2014-03-31 | 0 |
| 90c16 | Commercial Concentration Tax Act | `90c16/` | 3 | 1998-01-01 to 2010-09-15 | 0 |
| 90c17 | Commissioners for Taking Affidavits Act | `90c17/` | 6 | 2003-01-01 to 2020-08-01 | 15 |
| 90c18 | Commodity Board Members Act | `90c18/` | 4 | 1990-12-31 to 2007-07-25 | 8 |
| 90c19 | Commodity Boards and Marketing Agencies Act | `90c19/` | 1 | 1990-12-31 to 1990-12-31 | 5 |
| 90c20 | Commodity Futures Act | `90c20/` | 34 | 2003-04-07 to 2025-09-01 | 126 |
| 90c21 | Community Psychiatric Hospitals Act | `90c21/` | 4 | 1990-12-31 to 2009-12-15 | 0 |
| 90c22 | Community Recreation Centres Act | `90c22/` | 1 | 2003-01-01 to 2003-01-01 | 14 |
| 90c23 | Commuter Services Act | `90c23/` | 4 | 2003-01-01 to 2009-12-15 | 0 |
| 90c24 | Compensation for Victims of Crime Act | `90c24/` | 14 | 2000-12-06 to 2022-01-01 | 0 |
| 90c25 | Compulsory Automobile Insurance Act | `90c25/` | 11 | 2002-12-09 to 2020-12-08 | 28 |
| 90c27 | Conservation Authorities Act | `90c27/` | 36 | 2003-01-01 to 2026-04-24 | 116 |
| 90c28 | Conservation Land Act | `90c28/` | 7 | 2000-12-06 to 2021-10-19 | 4 |
| 90c29 | Consolidated Hearings Act | `90c29/` | 11 | 2003-01-01 to 2021-06-01 | 0 |
| 90c30 | Construction Act | `90c30/` | 22 | 2003-01-01 to 2026-01-01 | 132 |
| 90c31 | Consumer Protection Act | `90c31/` | 2 | 2003-01-01 to 2005-07-30 | 0 |
| 90c32 | Consumer Protection Bureau Act | `90c32/` | 2 | 2002-12-13 to 2005-07-30 | 0 |
| 90c33 | Consumer Reporting Act | `90c33/` | 18 | 2004-01-01 to 2026-07-01 | 41 |
| 90c34 | Conveyancing and Law of Property Act | `90c34/` | 11 | 2003-01-01 to 2024-07-01 | 62 |
| 90c35 | Co-operative Corporations Act | `90c35/` | 31 | 2004-01-01 to 2023-10-01 | 242 |
| 90c37 | Coroners Act | `90c37/` | 37 | 2002-12-13 to 2026-06-02 | 77 |
| 90c38 | Corporations Act | `90c38/` | 34 | 2004-01-01 to 2025-10-01 | 377 |
| 90c39 | Corporations Information Act | `90c39/` | 16 | 2001-06-29 to 2025-11-27 | 45 |
| 90c40 | Corporations Tax Act | `90c40/` | 30 | 2004-01-01 to 2026-04-24 | 192 |
| 90c41 | Costs of Distress Act | `90c41/` | 2 | 1990-12-31 to 2006-06-22 | 8 |
| 90c43 | Courts of Justice Act | `90c43/` | 55 | 2003-03-31 to 2025-12-11 | 197 |
| 90c45 | Creditors’ Relief Act | `90c45/` | 3 | 1997-05-12 to 2010-10-25 | 0 |
| 90c47 | Crown Administration of Estates Act | `90c47/` | 9 | 2002-11-26 to 2024-04-01 | 19 |
| 90c48 | Crown Agency Act | `90c48/` | 1 | 1999-04-01 to 1999-04-01 | 4 |
| 90c49 | Crown Attorneys Act | `90c49/` | 10 | 2003-01-01 to 2019-07-01 | 23 |
| 90c52 | Crown Witnesses Act | `90c52/` | 7 | 2003-01-01 to 2024-04-01 | 8 |
| 90d01 | Dangerous Goods Transportation Act | `90d01/` | 5 | 1990-12-31 to 2021-03-01 | 17 |
| 90d02 | Day Nurseries Act | `90d02/` | 11 | 2003-01-01 to 2015-08-31 | 0 |
| 90d03 | Dead Animal Disposal Act | `90d03/` | 3 | 2001-12-05 to 2009-03-27 | 0 |
| 90d04 | Debt Collectors Act | `90d04/` | 2 | 1990-12-31 to 2011-03-30 | 0 |
| 90d10 | Development Corporations Act | `90d10/` | 16 | 2003-01-01 to 2021-10-19 | 26 |
| 90d11 | Developmental Services Act | `90d11/` | 5 | 2003-01-01 to 2011-07-01 | 0 |
| 90d12 | Discriminatory Business Practices Act | `90d12/` | 8 | 2002-12-13 to 2023-12-06 | 21 |
| 90d13 | Disorderly Houses Act | `90d13/` | 2 | 1990-12-31 to 2006-06-22 | 9 |
| 90d15 | District Social Services Administration Boards Act | `90d15/` | 5 | 2003-01-01 to 2023-09-01 | 12 |
| 90d16 | Dog Owners’ Liability Act | `90d16/` | 12 | 2000-12-06 to 2024-06-06 | 22 |
| 90d17 | Drainage Act | `90d17/` | 16 | 2003-01-01 to 2021-06-30 | 127 |
| 90d18 | Drugless Practitioners Act | `90d18/` | 4 | 1990-12-31 to 2015-07-01 | 0 |
| 90e01 | Edible Oil Products Act | `90e01/` | 2 | 2001-12-05 to 2005-01-01 | 0 |
| 90e02 | Education Act | `90e02/` | 116 | 2003-06-03 to 2026-09-22 | 598 |
| 90e04 | Elderly Persons Centres Act | `90e04/` | 4 | 2003-01-01 to 2017-10-01 | 0 |
| 90e05 | Elderly Persons’ Housing Aid Act | `90e05/` | 2 | 1990-12-31 to 2016-12-08 | 0 |
| 90e06 | Election Act | `90e06/` | 38 | 2002-09-30 to 2025-11-27 | 212 |
| 90e07 | Election Finances Act | `90e07/` | 35 | 2002-09-30 to 2026-01-01 | 100 |
| 90e09 | Emergency Management and Civil Protection Act | `90e09/` | 15 | 2003-05-05 to 2025-12-03 | 45 |
| 90e11 | Employer Health Tax Act | `90e11/` | 19 | 2003-01-01 to 2025-11-27 | 47 |
| 90e12 | Employers and Employees Act | `90e12/` | 3 | 2004-01-01 to 2017-11-14 | 0 |
| 90e15 | Endangered Species Act | `90e15/` | 3 | 1999-01-01 to 2008-06-30 | 0 |
| 90e17 | Energy Efficiency Act | `90e17/` | 3 | 1990-12-31 to 2009-09-09 | 0 |
| 90e18 | Environmental Assessment Act | `90e18/` | 21 | 2003-01-01 to 2025-06-05 | 116 |
| 90e19 | Environmental Protection Act | `90e19/` | 54 | 2004-01-01 to 2025-06-05 | 287 |
| 90e20 | Escheats Act | `90e20/` | 5 | 2002-11-26 to 2016-12-10 | 0 |
| 90e21 | Estates Act | `90e21/` | 6 | 2004-01-01 to 2021-04-01 | 51 |
| 90e22 | Estates Administration Act | `90e22/` | 5 | 1995-04-03 to 2022-01-01 | 29 |
| 90e23 | Evidence Act | `90e23/` | 18 | 2003-01-01 to 2024-03-06 | 72 |
| 90e24 | Execution Act | `90e24/` | 12 | 2001-04-15 to 2026-08-17 | 39 |
| 90e25 | Executive Council Act | `90e25/` | 9 | 2002-12-13 to 2022-12-08 | 12 |
| 90e26 | Expropriations Act | `90e26/` | 14 | 2003-01-01 to 2024-12-04 | 45 |
| 90e27 | Extra-Provincial Corporations Act | `90e27/` | 6 | 2001-06-29 to 2021-10-19 | 44 |
| 90f01 | Factors Act | `90f01/` | 1 | 1990-12-31 to 1990-12-31 | 11 |
| 90f02 | Family Benefits Act | `90f02/` | 6 | 1997-11-28 to 2011-01-01 | 0 |
| 90f03 | Family Law Act | `90f03/` | 34 | 2004-01-01 to 2026-05-01 | 91 |
| 90f04 | Farm Implements Act | `90f04/` | 6 | 1999-12-22 to 2024-12-04 | 37 |
| 90f07 | Farm Products Containers Act | `90f07/` | 2 | 1990-12-31 to 2009-12-15 | 8 |
| 90f08 | Farm Products Grades and Sales Act | `90f08/` | 3 | 1997-04-01 to 2019-12-10 | 0 |
| 90f09 | Farm Products Marketing Act | `90f09/` | 9 | 1994-12-09 to 2021-10-19 | 25 |
| 90f10 | Farm Products Payments Act | `90f10/` | 17 | 1994-12-09 to 2026-01-01 | 0 |
| 90f12 | Financial Administration Act | `90f12/` | 39 | 2003-04-01 to 2026-04-24 | 104 |
| 90f13 | Fines and Forfeitures Act | `90f13/` | 2 | 1990-12-31 to 2006-06-22 | 9 |
| 90f18 | Fish Inspection Act | `90f18/` | 4 | 2001-12-05 to 2021-01-01 | 0 |
| 90f19 | Fisheries Loans Act | `90f19/` | 1 | 1990-12-31 to 1990-12-31 | 5 |
| 90f20 | Flag Act | `90f20/` | 1 | 1990-12-31 to 1990-12-31 | 3 |
| 90f21 | Floral Emblem Act | `90f21/` | 1 | 1990-12-31 to 1990-12-31 | 2 |
| 90f22 | Fluoridation Act | `90f22/` | 3 | 2003-01-01 to 2009-12-15 | 11 |
| 90f23 | Foreign Cultural Objects Immunity from Seizure Act | `90f23/` | 3 | 2002-11-26 to 2022-04-07 | 0 |
| 90f24 | Wildland Fire Management Act | `90f24/` | 11 | 2003-01-01 to 2026-04-01 | 55 |
| 90f26 | Forestry Act | `90f26/` | 2 | 2003-01-01 to 2009-12-15 | 18 |
| 90f28 | Forestry Workers Lien for Wages Act | `90f28/` | 4 | 1990-12-31 to 2017-11-14 | 34 |
| 90f29 | Fraudulent Conveyances Act | `90f29/` | 1 | 1990-12-31 to 1990-12-31 | 9 |
| 90f31 | Freedom of Information and Protection of Privacy Act | `90f31/` | 63 | 2003-07-01 to 2026-09-15 | 112 |
| 90f32 | French Language Services Act | `90f32/` | 27 | 2003-01-01 to 2026-01-01 | 31 |
| 90f33 | Freshwater Fish Marketing Act (Ontario) | `90f33/` | 2 | 1990-12-31 to 2019-12-10 | 0 |
| 90f34 | Frustrated Contracts Act | `90f34/` | 1 | 1993-12-02 to 1993-12-02 | 4 |
| 90f35 | Fuel Tax Act | `90f35/` | 26 | 2003-07-01 to 2025-07-01 | 79 |
| 90f36 | Board of Funeral Services Act | `90f36/` | 11 | 2002-12-13 to 2016-04-01 | 0 |
| 90g03 | Gas and Oil Leases Act | `90g03/` | 2 | 1990-12-31 to 2006-06-22 | 8 |
| 90g05 | Gasoline Tax Act | `90g05/` | 26 | 2003-07-01 to 2025-07-01 | 69 |
| 90g07 | George R. Gardiner Museum of Ceramic Art Act | `90g07/` | 7 | 1998-01-01 to 2021-10-19 | 19 |
| 90g09 | Grain Corn Marketing Act | `90g09/` | 3 | 1990-12-31 to 2010-02-01 | 0 |
| 90g10 | Grains Act | `90g10/` | 5 | 1999-12-22 to 2026-01-01 | 0 |
| 90h01 | Habeas Corpus Act | `90h01/` | 2 | 1990-12-31 to 2006-06-22 | 11 |
| 90h02 | Healing Arts Radiation Protection Act | `90h02/` | 17 | 2002-11-26 to 2026-01-01 | 27 |
| 90h03 | Health Care Accessibility Act | `90h03/` | 4 | 2002-11-26 to 2004-09-23 | 0 |
| 90h04 | Drug and Pharmacies Regulation Act | `90h04/` | 23 | 2001-11-01 to 2026-01-01 | 51 |
| 90h05 | Health Facilities Special Orders Act | `90h05/` | 13 | 2003-01-01 to 2023-05-18 | 22 |
| 90h06 | Health Insurance Act | `90h06/` | 38 | 2002-11-26 to 2023-09-25 | 102 |
| 90h07 | Health Protection and Promotion Act | `90h07/` | 59 | 2003-05-05 to 2025-06-05 | 128 |
| 90h08 | Highway Traffic Act | `90h08/` | 141 | 2004-01-01 to 2026-07-01 | 395 |
| 90h09 | Historical Parks Act | `90h09/` | 9 | 1998-06-01 to 2026-04-01 | 7 |
| 90h10 | Homemakers and Nurses Services Act | `90h10/` | 7 | 2003-01-01 to 2020-05-12 | 13 |
| 90h12 | Homes for Special Care Act | `90h12/` | 2 | 1997-10-10 to 2006-06-22 | 6 |
| 90h13 | Homes for the Aged and Rest Homes Act | `90h13/` | 11 | 2003-01-01 to 2010-07-01 | 0 |
| 90h14 | Hospital Labour Disputes Arbitration Act | `90h14/` | 6 | 2001-06-29 to 2018-05-08 | 23 |
| 90h15 | Hospitals and Charitable Institutions Inquiries Act | `90h15/` | 3 | 1990-12-31 to 2011-06-01 | 2 |
| 90h17 | Hotel Registration of Guests Act | `90h17/` | 3 | 1990-12-31 to 2026-01-01 | 0 |
| 90h18 | Housing Development Act | `90h18/` | 16 | 2003-01-01 to 2021-10-19 | 20 |
| 90h19 | Human Rights Code | `90h19/` | 36 | 2002-11-26 to 2025-07-01 | 91 |
| 90h20 | Gift of Life Act | `90h20/` | 21 | 2002-11-26 to 2023-07-24 | 36 |
| 90i01 | Immunization of School Pupils Act | `90i01/` | 10 | 2002-11-26 to 2021-04-19 | 19 |
| 90i02 | Income Tax Act | `90i02/` | 27 | 2003-12-18 to 2021-04-19 | 93 |
| 90i03 | Independent Health Facilities Act | `90i03/` | 20 | 2002-11-26 to 2023-09-25 | 0 |
| 90i04 | Indian Welfare Services Act | `90i04/` | 5 | 1998-07-01 to 2022-04-11 | 4 |
| 90i05 | Industrial and Mining Lands Compensation Act | `90i05/` | 1 | 1990-12-31 to 1990-12-31 | 5 |
| 90i07 | Innkeepers Act | `90i07/` | 2 | 1990-12-31 to 2023-03-22 | 8 |
| 90i08 | Insurance Act | `90i08/` | 71 | 2004-01-01 to 2026-01-01 | 529 |
| 90i09 | International Commercial Arbitration Act | `90i09/` | 3 | 1990-12-31 to 2017-03-22 | 0 |
| 90i10 | International Sales Conventions Act | `90i10/` | 2 | 1990-12-31 to 2017-03-22 | 11 |
| 90i11 | Interpretation Act | `90i11/` | 5 | 2003-01-01 to 2007-07-25 | 0 |
| 90i12 | Interprovincial Summonses Act | `90i12/` | 4 | 2000-12-06 to 2022-01-01 | 10 |
| 90j01 | Judicial Review Procedure Act | `90j01/` | 3 | 2003-01-01 to 2020-07-08 | 12 |
| 90j03 | Juries Act | `90j03/` | 17 | 2001-06-29 to 2024-12-04 | 55 |
| 90j04 | Justices of the Peace Act | `90j04/` | 27 | 2002-11-26 to 2025-06-06 | 34 |
| 90l01 | Laboratory and Specimen Collection Centre Licensing Act | `90l01/` | 8 | 2002-11-26 to 2022-07-01 | 24 |
| 90l03 | Lakes and Rivers Improvement Act | `90l03/` | 11 | 2003-01-01 to 2019-12-10 | 45 |
| 90l04 | Land Registration Reform Act | `90l04/` | 13 | 2002-11-26 to 2022-12-31 | 40 |
| 90l05 | Land Titles Act | `90l05/` | 28 | 2004-01-01 to 2026-08-17 | 170 |
| 90l06 | Land Transfer Tax Act | `90l06/` | 16 | 2003-01-01 to 2026-04-24 | 47 |
| 90l07 | Commercial Tenancies Act | `90l07/` | 15 | 2003-01-01 to 2022-12-08 | 90 |
| 90l08 | Law Society Act | `90l08/` | 27 | 2002-11-26 to 2024-12-04 | 166 |
| 90l10 | Legislative Assembly Act | `90l10/` | 38 | 2004-01-01 to 2026-01-01 | 133 |
| 90l12 | Libel and Slander Act | `90l12/` | 2 | 1990-12-31 to 2015-11-03 | 26 |
| 90l13 | Lieutenant Governor Act | `90l13/` | 1 | 1990-12-31 to 1990-12-31 | 5 |
| 90l14 | Lightning Rods Act | `90l14/` | 3 | 1997-05-27 to 2011-01-01 | 0 |
| 90l15 | Real Property Limitations Act | `90l15/` | 4 | 1990-12-31 to 2009-12-15 | 46 |
| 90l16 | Limited Partnerships Act | `90l16/` | 11 | 2001-06-29 to 2023-10-01 | 53 |
| 90l17 | Line Fences Act | `90l17/` | 5 | 2003-01-01 to 2024-06-06 | 32 |
| 90l18 | Liquor Sales Agreements Act | `90l18/` | 20 | 1998-02-22 to 2021-11-29 | 30 |
| 90l19 | Liquor Licence Act | `90l19/` | 24 | 2003-02-28 to 2021-11-29 | 0 |
| 90l20 | Livestock and Livestock Products Act | `90l20/` | 6 | 1999-12-22 to 2026-01-01 | 0 |
| 90l21 | Livestock Identification Act | `90l21/` | 2 | 1997-03-01 to 2009-12-15 | 11 |
| 90l22 | Livestock Community Sales Act | `90l22/` | 5 | 1999-12-22 to 2024-06-06 | 20 |
| 90l23 | Livestock Medicines Act | `90l23/` | 7 | 1999-12-22 to 2021-01-01 | 0 |
| 90l24 | Protection of Livestock and Poultry from Dogs Act | `90l24/` | 6 | 2003-01-01 to 2011-07-01 | 21 |
| 90l25 | Loan and Trust Corporations Act | `90l25/` | 16 | 2001-06-29 to 2025-12-31 | 152 |
| 90l27 | Local Roads Boards Act | `90l27/` | 9 | 1999-12-14 to 2025-11-27 | 44 |
| 90l28 | Northern Services Boards Act | `90l28/` | 31 | 2003-01-01 to 2025-08-01 | 63 |
| 90m01 | Management Board of Cabinet Act | `90m01/` | 7 | 1994-02-14 to 2015-06-04 | 8 |
| 90m02 | Marine Insurance Act | `90m02/` | 2 | 1993-12-02 to 2015-06-04 | 0 |
| 90m03 | Marriage Act | `90m03/` | 18 | 2003-01-01 to 2025-12-11 | 42 |
| 90m04 | McMichael Canadian Art Collection Act | `90m04/` | 11 | 2002-12-13 to 2026-04-01 | 19 |
| 90m05 | Meat Inspection Act (Ontario) | `90m05/` | 2 | 2001-12-05 to 2005-06-01 | 0 |
| 90m07 | Mental Health Act | `90m07/` | 6 | 2004-01-01 to 2015-12-21 | 89 |
| 90m08 | Mental Hospitals Act | `90m08/` | 4 | 2004-01-01 to 2009-12-15 | 0 |
| 90m10 | Mercantile Law Amendment Act | `90m10/` | 1 | 1990-12-31 to 1990-12-31 | 17 |
| 90m11 | Metropolitan Toronto Convention Centre Corporation Act | `90m11/` | 17 | 2003-01-01 to 2026-04-01 | 16 |
| 90m12 | Milk Act | `90m12/` | 16 | 2003-01-01 to 2021-10-19 | 43 |
| 90m13 | Mineral Emblem Act | `90m13/` | 1 | 1990-12-31 to 1990-12-31 | 2 |
| 90m14 | Mining Act | `90m14/` | 53 | 2003-01-01 to 2026-01-01 | 265 |
| 90m15 | Mining Tax Act | `90m15/` | 9 | 2002-12-09 to 2017-12-14 | 26 |
| 90m16 | Ministry of Agriculture, Food and Rural Affairs Act | `90m16/` | 21 | 2003-06-17 to 2023-03-22 | 27 |
| 90m17 | Ministry of the Attorney General Act | `90m17/` | 6 | 2000-12-06 to 2019-07-01 | 9 |
| 90m18 | Ministry of Citizenship and Culture Act | `90m18/` | 4 | 2003-01-01 to 2019-07-01 | 14 |
| 90m19 | Ministry of Training, Colleges and Universities Act | `90m19/` | 30 | 2003-04-01 to 2025-11-20 | 40 |
| 90m20 | Ministry of Community and Social Services Act | `90m20/` | 10 | 1997-11-28 to 2025-12-03 | 19 |
| 90m21 | Ministry of Consumer and Business Services Act | `90m21/` | 11 | 2002-12-13 to 2020-07-14 | 21 |
| 90m22 | Ministry of Correctional Services Act | `90m22/` | 29 | 2003-04-22 to 2024-10-16 | 67 |
| 90m23 | Ministry of Energy and Infrastructure Act | `90m23/` | 9 | 1999-04-01 to 2011-06-06 | 0 |
| 90m24 | Ministry of the Environment Act | `90m24/` | 4 | 1990-12-31 to 2020-12-08 | 7 |
| 90m25 | Ministry of Government Services Act | `90m25/` | 13 | 2000-12-06 to 2024-03-06 | 24 |
| 90m26 | Ministry of Health and Long-Term Care Act | `90m26/` | 15 | 2002-11-26 to 2024-06-28 | 17 |
| 90m27 | Ministry of Economic Development and Trade Act | `90m27/` | 7 | 1990-12-31 to 2021-04-27 | 14 |
| 90m28 | Ministry of Intergovernmental Affairs Act | `90m28/` | 3 | 1990-12-31 to 2019-07-01 | 8 |
| 90m29 | Ministry of Labour Act | `90m29/` | 9 | 2001-06-29 to 2019-07-01 | 15 |
| 90m30 | Ministry of Municipal Affairs and Housing Act | `90m30/` | 11 | 2003-01-01 to 2025-12-11 | 14 |
| 90m31 | Ministry of Natural Resources Act | `90m31/` | 14 | 1990-12-31 to 2021-06-01 | 17 |
| 90m32 | Ministry of Northern Development, Mines and Forestry Act | `90m32/` | 6 | 1990-12-31 to 2020-05-12 | 12 |
| 90m33 | Ministry of Revenue Act | `90m33/` | 33 | 2002-12-09 to 2023-12-04 | 34 |
| 90m34 | Ministry of the Solicitor General Act | `90m34/` | 3 | 2000-02-04 to 2007-08-20 | 6 |
| 90m35 | Ministry of Tourism and Recreation Act | `90m35/` | 9 | 1993-12-02 to 2019-07-01 | 16 |
| 90m36 | Ministry of Transportation Act | `90m36/` | 7 | 2002-11-26 to 2019-07-01 | 10 |
| 90m37 | Ministry of Treasury and Economics Act | `90m37/` | 4 | 2002-12-09 to 2009-12-15 | 0 |
| 90m39 | Mortgage Brokers Act | `90m39/` | 9 | 2002-12-13 to 2008-07-01 | 0 |
| 90m40 | Mortgages Act | `90m40/` | 12 | 2000-12-06 to 2022-01-01 | 60 |
| 90m41 | Motor Vehicle Accident Claims Act | `90m41/` | 10 | 2004-01-01 to 2023-06-30 | 35 |
| 90m42 | Motor Vehicle Dealers Act | `90m42/` | 7 | 2002-12-13 to 2010-01-01 | 0 |
| 90m43 | Motor Vehicle Repair Act | `90m43/` | 2 | 2002-12-13 to 2005-07-30 | 0 |
| 90m44 | Motorized Snow Vehicles Act | `90m44/` | 10 | 2003-01-01 to 2025-12-11 | 30 |
| 90m46 | Municipal Affairs Act | `90m46/` | 17 | 2003-01-01 to 2024-04-01 | 55 |
| 90m48 | Municipal Arbitrations Act | `90m48/` | 8 | 2003-01-01 to 2021-06-01 | 16 |
| 90m50 | Municipal Conflict of Interest Act | `90m50/` | 22 | 2003-01-01 to 2024-04-01 | 21 |
| 90m51 | Municipal Corporations Quieting Orders Act | `90m51/` | 3 | 2003-01-01 to 2021-06-01 | 9 |
| 90m54 | Municipal Extra-Territorial Tax Act | `90m54/` | 9 | 2003-01-01 to 2018-01-01 | 15 |
| 90m55 | Municipal Franchises Act | `90m55/` | 2 | 2003-08-01 to 2025-12-11 | 12 |
| 90m56 | Municipal Freedom of Information and Protection of Privacy Act | `90m56/` | 31 | 2003-07-01 to 2026-07-01 | 64 |
| 90m57 | Municipal Health Services Act | `90m57/` | 7 | 2003-01-01 to 2009-12-15 | 0 |
| 90m59 | Municipal Tax Assistance Act | `90m59/` | 7 | 2003-01-01 to 2018-05-08 | 7 |
| 90n01 | Negligence Act | `90n01/` | 1 | 2004-01-01 to 2004-01-01 | 9 |
| 90n02 | Niagara Escarpment Planning and Development Act | `90n02/` | 20 | 2003-01-01 to 2026-04-01 | 37 |
| 90n03 | Niagara Parks Act | `90n03/` | 14 | 2003-01-01 to 2024-06-06 | 26 |
| 90n05 | Northern Ontario Heritage Fund Act | `90n05/` | 12 | 2000-12-21 to 2022-03-01 | 11 |
| 90n06 | Notaries Act | `90n06/` | 8 | 2002-01-01 to 2020-08-01 | 9 |
| 90n07 | Nursing Homes Act | `90n07/` | 11 | 2002-11-26 to 2010-07-01 | 0 |
| 90o01 | Occupational Health and Safety Act | `90o01/` | 52 | 2001-12-12 to 2025-11-27 | 125 |
| 90o02 | Occupiers’ Liability Act | `90o02/` | 7 | 1990-12-31 to 2021-01-29 | 13 |
| 90o03 | Ontario Gazette Act | `90o03/` | 4 | 2003-01-01 to 2024-03-06 | 5 |
| 90o04 | Off-Road Vehicles Act | `90o04/` | 10 | 2004-01-01 to 2021-01-01 | 25 |
| 90o06 | Ombudsman Act | `90o06/` | 27 | 1999-10-28 to 2025-11-20 | 49 |
| 90o08 | Ontario Agricultural Museum Act | `90o08/` | 6 | 1994-12-09 to 2010-10-25 | 0 |
| 90o10 | Ontario Drug Benefit Act | `90o10/` | 23 | 2002-11-26 to 2022-01-01 | 38 |
| 90o12 | Ontario Educational Communications Authority Act | `90o12/` | 16 | 2002-12-23 to 2022-03-01 | 25 |
| 90o15 | Ontario Food Terminal Act | `90o15/` | 14 | 1998-01-01 to 2026-04-01 | 19 |
| 90o16 | Ontario Geographic Names Board Act | `90o16/` | 1 | 1990-12-31 to 1990-12-31 | 6 |
| 90o17 | Ontario Guaranteed Annual Income Act | `90o17/` | 9 | 2001-12-05 to 2023-05-18 | 21 |
| 90o18 | Ontario Heritage Act | `90o18/` | 33 | 2003-01-01 to 2026-04-01 | 117 |
| 90o19 | Ontario Highway Transport Board Act | `90o19/` | 10 | 1996-05-30 to 2021-07-01 | 0 |
| 90o20 | Ontario Home Ownership Savings Plan Act | `90o20/` | 9 | 2002-06-27 to 2009-06-05 | 0 |
| 90o21 | Ontario Mortgage and Housing Corporation Act | `90o21/` | 12 | 2000-12-13 to 2021-03-31 | 0 |
| 90o24 | Ontario Law Reform Commission Act | `90o24/` | 2 | 1990-12-31 to 2009-12-15 | 0 |
| 90o26 | Ontario Mental Health Foundation Act | `90o26/` | 9 | 2004-01-01 to 2018-03-31 | 0 |
| 90o27 | Ontario Mineral Exploration Program Act | `90o27/` | 4 | 1990-12-31 to 2010-10-25 | 0 |
| 90o28 | Ontario Municipal Board Act | `90o28/` | 10 | 2003-01-01 to 2018-04-03 | 0 |
| 90o29 | Ontario Municipal Employees Retirement System Act | `90o29/` | 5 | 2003-01-01 to 2006-06-30 | 0 |
| 90o31 | Ontario New Home Warranties Plan Act | `90o31/` | 20 | 2001-06-29 to 2024-12-04 | 62 |
| 90o32 | Ontario Northland Transportation Commission Act | `90o32/` | 19 | 2003-01-01 to 2026-04-01 | 53 |
| 90o34 | Ontario Place Corporation Act | `90o34/` | 11 | 1998-06-01 to 2021-10-19 | 19 |
| 90o36 | Ontario Society for the Prevention of Cruelty to Animals Act | `90o36/` | 12 | 2002-12-13 to 2020-01-01 | 0 |
| 90o40 | Ontario Water Resources Act | `90o40/` | 47 | 2003-07-01 to 2025-11-27 | 182 |
| 90o44 | Ottawa-Carleton French-Language School Board Transferred Employees Act | `90o44/` | 2 | 2003-01-01 to 2026-05-07 | 10 |
| 90o45 | Ottawa Convention Centre Corporation Act | `90o45/` | 15 | 2003-01-01 to 2026-04-01 | 16 |
| 90p01 | Paperback and Periodical Distributors Act | `90p01/` | 6 | 2001-06-29 to 2019-12-10 | 0 |
| 90p04 | Partition Act | `90p04/` | 3 | 1990-12-31 to 2009-12-15 | 8 |
| 90p05 | Partnerships Act | `90p05/` | 8 | 2001-02-15 to 2023-10-01 | 51 |
| 90p06 | Pawnbrokers Act | `90p06/` | 5 | 2003-01-01 to 2024-04-01 | 30 |
| 90p07 | Pay Equity Act | `90p07/` | 33 | 2003-01-01 to 2024-06-28 | 57 |
| 90p08 | Pension Benefits Act | `90p08/` | 77 | 2002-11-26 to 2026-07-01 | 195 |
| 90p09 | Perpetuities Act | `90p09/` | 6 | 2000-03-01 to 2018-04-30 | 20 |
| 90p10 | Personal Property Security Act | `90p10/` | 34 | 2002-12-13 to 2025-10-01 | 114 |
| 90p11 | Pesticides Act | `90p11/` | 26 | 2003-07-01 to 2024-04-01 | 91 |
| 90p12 | Oil, Gas and Salt Resources Act | `90p12/` | 21 | 2002-11-26 to 2026-01-01 | 43 |
| 90p13 | Planning Act | `90p13/` | 66 | 2003-01-01 to 2026-07-01 | 132 |
| 90p14 | Plant Diseases Act | `90p14/` | 2 | 1997-03-01 to 2009-12-15 | 12 |
| 90p15 | Police Services Act | `90p15/` | 33 | 2003-01-01 to 2024-04-01 | 0 |
| 90p17 | Pounds Act | `90p17/` | 4 | 2003-01-01 to 2007-01-01 | 23 |
| 90p18 | Power Corporation Act | `90p18/` | 2 | 2003-01-01 to 2011-12-31 | 22 |
| 90p20 | Powers of Attorney Act | `90p20/` | 1 | 1995-04-03 to 1995-04-03 | 4 |
| 90p21 | Prepaid Hospital and Medical Services Act | `90p21/` | 10 | 1999-12-22 to 2021-10-19 | 21 |
| 90p22 | Prepaid Services Act | `90p22/` | 2 | 2002-12-13 to 2005-07-30 | 0 |
| 90p23 | Drug Interchangeability and Dispensing Fee Act | `90p23/` | 11 | 1996-05-27 to 2016-06-03 | 18 |
| 90p24 | Private Hospitals Act | `90p24/` | 16 | 2003-01-01 to 2023-09-25 | 38 |
| 90p25 | Private Investigators and Security Guards Act | `90p25/` | 4 | 2000-02-04 to 2007-08-23 | 0 |
| 90p26 | Private Career Colleges Act | `90p26/` | 4 | 2002-06-27 to 2006-09-18 | 0 |
| 90p27 | Proceedings Against the Crown Act | `90p27/` | 13 | 1998-01-01 to 2019-07-01 | 0 |
| 90p28 | Professional Engineers Act | `90p28/` | 17 | 2004-01-01 to 2025-01-01 | 54 |
| 90p29 | Property and Civil Rights Act | `90p29/` | 1 | 1990-12-31 to 1990-12-31 | 2 |
| 90p30 | Province of Ontario Savings Office Act | `90p30/` | 2 | 2002-06-27 to 2012-12-31 | 7 |
| 90p32 | Provincial Land Tax Act | `90p32/` | 3 | 2003-01-01 to 2009-01-01 | 0 |
| 90p33 | Provincial Offences Act | `90p33/` | 42 | 2003-01-01 to 2026-04-15 | 211 |
| 90p34 | Provincial Parks Act | `90p34/` | 5 | 2003-01-01 to 2007-09-04 | 0 |
| 90p35 | Provincial Schools Authority Act | `90p35/` | 8 | 2003-06-03 to 2025-01-31 | 8 |
| 90p37 | Public Accountancy Act | `90p37/` | 3 | 2002-12-09 to 2005-11-01 | 0 |
| 90p38 | Public Authorities Protection Act | `90p38/` | 4 | 2004-01-01 to 2007-05-01 | 13 |
| 90p40 | Public Hospitals Act | `90p40/` | 29 | 2004-01-01 to 2024-06-28 | 48 |
| 90p41 | Public Inquiries Act | `90p41/` | 6 | 2000-06-23 to 2011-06-01 | 0 |
| 90p43 | Public Lands Act | `90p43/` | 23 | 2004-01-01 to 2024-02-22 | 100 |
| 90p44 | Public Libraries Act | `90p44/` | 7 | 2003-01-01 to 2019-12-10 | 39 |
| 90p45 | Public Officers Act | `90p45/` | 4 | 2004-01-01 to 2024-03-06 | 11 |
| 90p47 | Public Service Act | `90p47/` | 8 | 2002-11-26 to 2007-08-20 | 0 |
| 90p48 | Public Service Pension Act | `90p48/` | 9 | 2000-03-01 to 2019-06-08 | 17 |
| 90p49 | Public Service Works on Highways Act | `90p49/` | 6 | 1999-04-01 to 2021-06-01 | 5 |
| 90p50 | Public Transportation and Highway Improvement Act | `90p50/` | 22 | 2004-01-01 to 2025-11-27 | 87 |
| 90p51 | Public Guardian and Trustee Act | `90p51/` | 12 | 2002-11-26 to 2021-10-19 | 28 |
| 90p52 | Public Utilities Act | `90p52/` | 6 | 2003-01-01 to 2025-12-11 | 42 |
| 90p54 | Public Vehicles Act | `90p54/` | 9 | 2003-01-01 to 2021-07-01 | 0 |
| 90p55 | Public Works Protection Act | `90p55/` | 3 | 1990-12-31 to 2015-06-24 | 0 |
| 90r01 | Race Tracks Tax Act | `90r01/` | 2 | 2001-12-05 to 2011-05-12 | 19 |
| 90r04 | Real Estate and Business Brokers Act | `90r04/` | 5 | 2002-12-13 to 2006-03-31 | 0 |
| 90r05 | Reciprocal Enforcement of Judgments Act | `90r05/` | 2 | 1990-12-31 to 2006-06-22 | 9 |
| 90r06 | Reciprocal Enforcement of Judgments (U.K.) Act | `90r06/` | 1 | 1990-12-31 to 1990-12-31 | 8 |
| 90r19 | Registered Insurance Brokers Act | `90r19/` | 14 | 2002-12-13 to 2020-12-08 | 39 |
| 90r20 | Registry Act | `90r20/` | 25 | 2003-01-01 to 2022-12-31 | 125 |
| 90r21 | Regulations Act | `90r21/` | 5 | 2003-01-01 to 2007-07-25 | 0 |
| 90r22 | Religious Freedom Act | `90r22/` | 1 | 1990-12-31 to 1990-12-31 | 2 |
| 90r23 | Religious Organizations’ Lands Act | `90r23/` | 3 | 1990-12-31 to 2009-12-15 | 27 |
| 90r25 | Repair and Storage Liens Act | `90r25/` | 17 | 2000-12-06 to 2024-01-01 | 36 |
| 90r27 | Research Foundation Act | `90r27/` | 4 | 1999-12-22 to 2013-07-01 | 0 |
| 90r28 | Residential Complex Sales Representation Act | `90r28/` | 5 | 1998-06-17 to 2019-12-10 | 0 |
| 90r30 | Retail Business Holidays Act | `90r30/` | 14 | 2003-01-01 to 2026-04-24 | 16 |
| 90r31 | Retail Sales Tax Act | `90r31/` | 43 | 2003-12-18 to 2026-05-12 | 78 |
| 90r33 | Rights of Labour Act | `90r33/` | 1 | 1990-12-31 to 1990-12-31 | 4 |
| 90r34 | Road Access Act | `90r34/` | 3 | 2003-01-01 to 2009-12-15 | 9 |
| 90r35 | Royal Ontario Museum Act | `90r35/` | 11 | 1990-12-31 to 2026-04-01 | 18 |
| 90s01 | Sale of Goods Act | `90s01/` | 1 | 1994-12-09 to 1994-12-09 | 58 |
| 90s03 | School Trust Conveyances Act | `90s03/` | 2 | 2003-01-01 to 2021-04-19 | 4 |
| 90s04 | Science North Act | `90s04/` | 9 | 2002-11-26 to 2026-04-01 | 17 |
| 90s05 | Securities Act | `90s05/` | 71 | 2003-04-07 to 2025-09-01 | 265 |
| 90s07 | Settled Estates Act | `90s07/` | 5 | 2003-01-01 to 2009-12-15 | 38 |
| 90s10 | Shoreline Property Assistance Act | `90s10/` | 3 | 2003-01-01 to 2007-01-01 | 17 |
| 90s11 | Short Forms of Leases Act | `90s11/` | 1 | 1990-12-31 to 1990-12-31 | 7 |
| 90s12 | Small Business Development Corporations Act | `90s12/` | 5 | 1997-10-10 to 2009-10-01 | 0 |
| 90s13 | Smoking in the Workplace Act | `90s13/` | 3 | 1990-12-31 to 2006-05-31 | 0 |
| 90s15 | Solicitors Act | `90s15/` | 7 | 2004-01-01 to 2021-07-01 | 40 |
| 90s18 | Statistics Act | `90s18/` | 3 | 2002-11-26 to 2007-07-25 | 11 |
| 90s19 | Statute of Frauds | `90s19/` | 1 | 1994-12-09 to 1994-12-09 | 12 |
| 90s20 | Statute Labour Act | `90s20/` | 7 | 2003-01-01 to 2022-01-01 | 0 |
| 90s21 | Statutes Act | `90s21/` | 3 | 1999-12-22 to 2007-07-25 | 0 |
| 90s22 | Statutory Powers Procedure Act | `90s22/` | 13 | 2003-01-01 to 2025-07-01 | 57 |
| 90s24 | St. Lawrence Parks Commission Act | `90s24/` | 20 | 2003-01-01 to 2024-03-06 | 24 |
| 90s26 | Succession Law Reform Act | `90s26/` | 18 | 2003-01-01 to 2025-12-11 | 85 |
| 90s29 | Surveyors Act | `90s29/` | 10 | 1998-12-18 to 2026-01-01 | 47 |
| 90s30 | Surveys Act | `90s30/` | 6 | 2003-01-01 to 2020-12-08 | 63 |
| 90t01 | Teachers’ Pension Act | `90t01/` | 13 | 1999-05-01 to 2021-10-19 | 19 |
| 90t02 | Teaching Profession Act | `90t02/` | 8 | 2002-09-03 to 2025-01-31 | 14 |
| 90t06 | Theatres Act | `90t06/` | 5 | 2003-03-31 to 2005-08-31 | 0 |
| 90t07 | Ticket Speculation Act | `90t07/` | 5 | 1990-12-31 to 2018-07-01 | 0 |
| 90t08 | Tile Drainage Act | `90t08/` | 6 | 2003-01-01 to 2015-06-04 | 17 |
| 90t09 | Time Act | `90t09/` | 3 | 1990-12-31 to 2020-11-30 | 3 |
| 90t10 | Tobacco Tax Act | `90t10/` | 42 | 2003-12-18 to 2025-06-05 | 94 |
| 90t11 | Toll Bridges Act | `90t11/` | 1 | 1990-12-31 to 1990-12-31 | 6 |
| 90t13 | Toronto Area Transit Operating Authority Act | `90t13/` | 7 | 2002-01-01 to 2011-05-12 | 0 |
| 90t14 | Toronto Futures Exchange Act | `90t14/` | 2 | 2000-12-15 to 2009-12-15 | 0 |
| 90t15 | Toronto Stock Exchange Act | `90t15/` | 2 | 2000-12-15 to 2019-12-10 | 0 |
| 90t16 | Tourism Act | `90t16/` | 3 | 1999-04-01 to 2009-12-15 | 0 |
| 90t17 | Trades Qualification and Apprenticeship Act | `90t17/` | 5 | 2000-01-01 to 2013-04-08 | 0 |
| 90t18 | Transboundary Pollution Reciprocal Access Act | `90t18/` | 1 | 1990-12-31 to 1990-12-31 | 10 |
| 90t19 | Travel Industry Act | `90t19/` | 3 | 2002-12-13 to 2005-07-01 | 0 |
| 90t21 | Trespass to Property Act | `90t21/` | 4 | 2001-05-31 to 2025-06-05 | 13 |
| 90t22 | Truck Transportation Act | `90t22/` | 2 | 2003-01-01 to 2006-01-01 | 0 |
| 90t23 | Trustee Act | `90t23/` | 7 | 2004-01-01 to 2023-06-08 | 72 |
| 90u01 | Unclaimed Intangible Property Act | `90u01/` | 2 | 2002-11-26 to 2011-12-31 | 0 |
| 90u02 | Unconscionable Transactions Relief Act | `90u02/` | 2 | 1990-12-31 to 2006-06-22 | 6 |
| 90u03 | University Expropriation Powers Act | `90u03/` | 1 | 2003-01-01 to 2003-01-01 | 3 |
| 90v01 | Variation of Trusts Act | `90v01/` | 2 | 1990-12-31 to 2006-06-22 | 2 |
| 90v02 | Vendors and Purchasers Act | `90v02/` | 2 | 1993-12-02 to 2006-06-22 | 5 |
| 90v03 | Veterinarians Act | `90v03/` | 12 | 2004-01-01 to 2024-06-06 | 62 |
| 90v04 | Vital Statistics Act | `90v04/` | 42 | 2003-01-01 to 2022-12-31 | 92 |
| 90w01 | Wages Act | `90w01/` | 4 | 1999-12-22 to 2022-03-01 | 8 |
| 90w03 | Warehouse Receipts Act | `90w03/` | 2 | 1999-12-22 to 2006-06-22 | 32 |
| 90w04 | Water Transfer Control Act | `90w04/` | 3 | 1993-12-02 to 2007-06-04 | 0 |
| 90w05 | Weed Control Act | `90w05/` | 6 | 2003-01-01 to 2022-01-01 | 25 |
| 90w07 | Wild Rice Harvesting Act | `90w07/` | 1 | 1990-12-31 to 1990-12-31 | 6 |
| 90w08 | Wilderness Areas Act | `90w08/` | 5 | 1999-01-01 to 2016-12-31 | 8 |
| 91a17 | Arbitration Act, 1991 | `91a17/` | 6 | 1992-01-01 to 2017-03-22 | 64 |
| 91a19 | Audiology and Speech-Language Pathology Act, 1991 | `91a19/` | 5 | 1999-02-01 to 2026-01-01 | 16 |
| 91c20 | Chiropody Act, 1991 | `91c20/` | 8 | 1999-02-01 to 2026-01-01 | 19 |
| 91c21 | Chiropractic Act, 1991 | `91c21/` | 6 | 1999-02-01 to 2021-06-03 | 15 |
| 91d22 | Dental Hygiene Act, 1991 | `91d22/` | 7 | 1999-02-01 to 2026-01-01 | 18 |
| 91d23 | Dental Technology Act, 1991 | `91d23/` | 6 | 1999-02-01 to 2026-01-01 | 14 |
| 91d24 | Dentistry Act, 1991 | `91d24/` | 8 | 1999-02-01 to 2026-01-01 | 18 |
| 91d25 | Denturism Act, 1991 | `91d25/` | 5 | 1999-02-01 to 2026-01-01 | 15 |
| 91d26 | Dietetics Act, 1991 | `91d26/` | 6 | 1999-02-01 to 2026-01-01 | 15 |
| 91e44 | Electronic Registration Act (Ministry of Consumer and Business Services Statutes), 1991 | `91e44/` | 1 | 2001-06-29 to 2001-06-29 | 10 |
| 91h01 | Health Cards and Numbers Control Act, 1991 | `91h01/` | 3 | 2002-11-26 to 2004-11-01 | 0 |
| 91m27 | Massage Therapy Act, 1991 | `91m27/` | 4 | 1999-02-01 to 2021-06-03 | 13 |
| 91m28 | Medical Laboratory Technology Act, 1991 | `91m28/` | 5 | 1999-02-01 to 2023-07-24 | 16 |
| 91m29 | Medical Radiation Technology Act, 1991 | `91m29/` | 6 | 1999-02-01 to 2020-01-01 | 0 |
| 91m30 | Medicine Act, 1991 | `91m30/` | 11 | 2000-12-21 to 2026-01-01 | 20 |
| 91m31 | Midwifery Act, 1991 | `91m31/` | 7 | 1999-02-01 to 2026-01-01 | 17 |
| 91n32 | Nursing Act, 1991 | `91n32/` | 11 | 1999-02-01 to 2023-12-04 | 21 |
| 91o08 | Ontario Loan Act, 1991 | `91o08/` | 1 | 1991-06-19 to 1991-06-19 | 5 |
| 91o33 | Occupational Therapy Act, 1991 | `91o33/` | 6 | 1999-02-01 to 2026-01-01 | 17 |
| 91o34 | Opticianry Act, 1991 | `91o34/` | 5 | 1999-02-01 to 2026-01-01 | 16 |
| 91o35 | Optometry Act, 1991 | `91o35/` | 8 | 1999-02-01 to 2026-01-01 | 20 |
| 91o51 | Ontario Medical Association Dues Act, 1991 | `91o51/` | 4 | 1991-12-19 to 2023-07-24 | 12 |
| 91p36 | Pharmacy Act, 1991 | `91p36/` | 8 | 1999-02-01 to 2026-01-01 | 18 |
| 91p37 | Physiotherapy Act, 1991 | `91p37/` | 7 | 1999-02-01 to 2026-01-01 | 17 |
| 91p38 | Psychology Act, 1991 | `91p38/` | 5 | 1999-02-01 to 2024-07-01 | 0 |
| 91r18 | Regulated Health Professions Act, 1991 | `91r18/` | 52 | 2004-01-01 to 2026-01-01 | 56 |
| 91r39 | Respiratory Therapy Act, 1991 | `91r39/` | 6 | 1999-02-01 to 2023-07-24 | 17 |
| 91s07 | Supply Act, 1991 | `91s07/` | 2 | 1991-06-13 to 2001-06-29 | 0 |
| 91s58 | Supply Act, 1991 (No. 2) | `91s58/` | 2 | 1991-12-19 to 2001-06-29 | 0 |
| 91t14 | Treasury Board Act, 1991 | `91t14/` | 8 | 2002-06-27 to 2009-12-15 | 0 |
| 92b23 | Building Code Act, 1992 | `92b23/` | 30 | 2003-09-01 to 2026-06-02 | 90 |
| 92c06 | Class Proceedings Act, 1992 | `92c06/` | 5 | 1993-01-01 to 2021-06-03 | 49 |
| 92g24 | Gaming Control Act, 1992 | `92g24/` | 16 | 2003-02-28 to 2025-05-12 | 61 |
| 92l18 | Community Small Business Investment Funds Act, 1992 | `92l18/` | 21 | 2003-01-01 to 2019-07-01 | 62 |
| 92o05 | Ontario Loan Act, 1992 | `92o05/` | 1 | 1992-06-25 to 1992-06-25 | 5 |
| 92s30 | Substitute Decisions Act, 1992 | `92s30/` | 36 | 2003-01-01 to 2024-04-01 | 107 |
| 92u22 | University Foundations Act, 1992 | `92u22/` | 7 | 2002-06-27 to 2022-12-08 | 15 |
| 92w01 | Waste Management Act, 1992 | `92w01/` | 6 | 2003-01-01 to 2010-10-25 | 0 |
| 92w02 | Waterfront Regeneration Trust Agency Act, 1992 | `92w02/` | 7 | 1992-06-25 to 2010-10-25 | 0 |
| 93c23 | Capital Investment Plan Act, 1993 | `93c23/` | 27 | 2003-01-01 to 2026-04-01 | 70 |
| 93c38 | Crown Employees Collective Bargaining Act, 1993 | `93c38/` | 19 | 2002-11-26 to 2018-11-21 | 93 |
| 93e28 | Environmental Bill of Rights, 1993 | `93e28/` | 22 | 2004-01-01 to 2024-02-22 | 124 |
| 93f21 | Farm Registration and Farm Organizations Funding Act, 1993 | `93f21/` | 8 | 1999-12-22 to 2023-12-04 | 58 |
| 93o07 | Ontario Loan Act, 1993 | `93o07/` | 1 | 1993-07-21 to 1993-07-21 | 5 |
| 93r27 | Revised Statutes Confirmation and Corrections Act, 1993 | `93r27/` | 2 | 1993-12-02 to 2018-12-06 | 4 |
| 93s05 | Social Contract Act, 1993 | `93s05/` | 15 | 1996-04-01 to 2023-09-25 | 55 |
| 93t15 | Toronto Islands Residential Community Stewardship Act, 1993 | `93t15/` | 21 | 2003-01-01 to 2023-12-01 | 40 |
| 94a15 | Avian Emblem Act, 1994 | `94a15/` | 1 | 1994-06-23 to 1994-06-23 | 4 |
| 94a20 | Ammunition Regulation Act, 1994 | `94a20/` | 2 | 1994-07-23 to 2009-12-15 | 8 |
| 94b32 | Business Regulation Reform Act, 1994 | `94b32/` | 16 | 1995-04-03 to 2022-03-01 | 26 |
| 94c03 | Chronic Care Patients’ Television Act, 1994 | `94c03/` | 2 | 1994-06-23 to 2009-12-15 | 0 |
| 94c11 | Credit Unions and Caisses Populaires Act, 1994 | `94c11/` | 33 | 2004-01-01 to 2022-03-01 | 0 |
| 94c25 | Crown Forest Sustainability Act, 1994 | `94c25/` | 17 | 2001-06-29 to 2026-07-16 | 100 |
| 94d19 | Donation of Food Act, 1994 | `94d19/` | 1 | 1994-06-23 to 1994-06-23 | 5 |
| 94l22 | Loan Brokers Act, 1994 | `94l22/` | 2 | 2002-12-13 to 2005-07-30 | 0 |
| 94l26 | Home Care and Community Services Act, 1994 | `94l26/` | 25 | 2003-01-01 to 2022-05-01 | 0 |
| 94m38 | Members’ Integrity Act, 1994 | `94m38/` | 12 | 2000-03-01 to 2021-10-18 | 56 |
| 94o16 | Ontario Loan Act, 1994 | `94o16/` | 1 | 1994-06-23 to 1994-06-23 | 5 |
| 94o17 | Ontario Public Service Employees’ Union Pension Act, 1994 | `94o17/` | 4 | 1996-01-30 to 2019-06-08 | 19 |
| 94o23 | Ontario Planning and Development Act, 1994 | `94o23/` | 9 | 2003-01-01 to 2025-11-27 | 25 |
| 94s21 | Superannuation Adjustment Benefits Repeal Act, 1994 | `94s21/` | 3 | 1994-12-09 to 2007-04-01 | 0 |
| 94t10 | Smoke-Free Ontario Act | `94t10/` | 19 | 2002-06-27 to 2018-10-17 | 0 |
| 95l01 | Labour Relations Act, 1995 | `95l01/` | 38 | 2003-06-17 to 2025-12-31 | 232 |
| 95s02 | Shortline Railways Act, 1995 | `95s02/` | 12 | 2003-01-01 to 2021-10-19 | 27 |
| 95v06 | Victims’ Bill of Rights, 1995 | `95v06/` | 14 | 2001-06-11 to 2024-10-16 | 9 |
| 96a17a | AgriCorp Act, 1996 | `96a17a/` | 21 | 1999-12-22 to 2024-04-01 | 22 |
| 96a26 | Liquor Tax Act, 1996 | `96a26/` | 36 | 2003-02-28 to 2026-04-24 | 92 |
| 96c17 | Agricultural Products Insurance Act, 1996 | `96c17/` | 6 | 1999-12-22 to 2019-12-10 | 19 |
| 96c22 | Crown Foundations Act, 1996 | `96c22/` | 10 | 1996-06-27 to 2020-04-01 | 22 |
| 96e11 | Education Quality and Accountability Office Act, 1996 | `96e11/` | 16 | 1998-01-01 to 2024-04-01 | 34 |
| 96f31 | Family Responsibility and Support Arrears Enforcement Act, 1996 | `96f31/` | 31 | 2003-03-31 to 2026-05-01 | 84 |
| 96h02 | Health Care Consent Act, 1996 | `96h02/` | 32 | 2002-11-26 to 2023-05-18 | 103 |
| 96m06 | MPPs Pension Act, 1996 | `96m06/` | 8 | 2000-03-01 to 2026-01-01 | 64 |
| 96m32 | Municipal Elections Act, 1996 | `96m32/` | 29 | 2003-01-01 to 2026-05-07 | 154 |
| 96o01 | Ontario Loan Act, 1996 | `96o01/` | 1 | 1996-01-30 to 1996-01-30 | 5 |
| 96o12 | Ontario College of Teachers Act, 1996 | `96o12/` | 23 | 2002-09-03 to 2026-05-07 | 105 |
| 96o16 | Ontario Institute for Studies in Education Repeal Act, 1996 | `96o16/` | 1 | 1996-07-01 to 1996-07-01 | 9 |
| 96o18 | Ontario Loan Act, 1996 (No. 2) | `96o18/` | 1 | 1996-06-27 to 1996-06-27 | 4 |
| 96p01a | Public Sector Salary Disclosure Act, 1996 | `96p01a/` | 13 | 2003-01-01 to 2026-05-07 | 13 |
| 96p01i | Physician Services Delivery Management Act, 1996 | `96p01i/` | 2 | 1996-01-30 to 2011-03-30 | 0 |
| 96r28 | Representation Act, 1996 | `96r28/` | 2 | 1999-05-05 to 2005-12-15 | 0 |
| 96s19 | Safety and Consumer Statutes Administration Act, 1996 | `96s19/` | 25 | 2003-03-31 to 2023-12-01 | 38 |
| 97c02 | City of Toronto Act, 1997 | `97c02/` | 4 | 2003-01-01 to 2007-01-01 | 0 |
| 97c26 | City of Toronto Act, 1997 (No. 2) | `97c26/` | 9 | 2003-01-01 to 2007-01-01 | 0 |
| 97d27 | Development Charges Act, 1997 | `97d27/` | 33 | 2003-01-01 to 2026-06-02 | 89 |
| 97f04 | Fire Protection and Prevention Act, 1997 | `97f04/` | 28 | 2003-01-01 to 2026-01-01 | 117 |
| 97f28 | Financial Services Commission of Ontario Act, 1997 | `97f28/` | 30 | 1999-12-22 to 2020-12-08 | 0 |
| 97f32 | Fairness for Parents and Employees Act (Teachers’ Withdrawal of Services), 1997 | `97f32/` | 7 | 1997-12-08 to 2020-10-27 | 0 |
| 97f41 | Fish and Wildlife Conservation Act, 1997 | `97f41/` | 21 | 2002-11-26 to 2026-03-30 | 126 |
| 97g33 | Geographic Township of Creighton-Davies Act, 1997 | `97g33/` | 1 | 1997-12-08 to 1997-12-08 | 5 |
| 97m06 | Municipal Water and Sewage Transfer Act, 1997 | `97m06/` | 6 | 2003-01-01 to 2021-06-01 | 18 |
| 97o25a | Ontario Works Act, 1997 | `97o25a/` | 20 | 2003-01-01 to 2025-07-01 | 86 |
| 97o25b | Ontario Disability Support Program Act, 1997 | `97o25b/` | 14 | 2002-11-26 to 2023-10-26 | 63 |
| 97o43 | Municipal Property Assessment Corporation Act, 1997 | `97o43/` | 19 | 2003-01-01 to 2021-12-09 | 23 |
| 97p21a | Public Sector Dispute Resolution Act, 1997 | `97p21a/` | 9 | 1997-10-29 to 2024-04-01 | 6 |
| 97p21b | Public Sector Labour Relations Transition Act, 1997 | `97p21b/` | 27 | 2003-01-01 to 2024-06-28 | 51 |
| 97r18 | Remembrance Day Observance Act, 1997 | `97r18/` | 2 | 1997-10-10 to 2016-11-02 | 0 |
| 97s13 | Supply Act, 1997 | `97s13/` | 2 | 1997-09-03 to 2001-06-29 | 0 |
| 97t24 | Tenant Protection Act, 1997 | `97t24/` | 8 | 2003-01-01 to 2007-01-31 | 0 |
| 97t45 | University Health Network Act, 1997 | `97t45/` | 3 | 2002-11-26 to 2024-12-04 | 17 |
| 97u42 | United Empire Loyalists’ Day Act, 1997 | `97u42/` | 1 | 1997-12-18 to 1997-12-18 | 4 |
| 97w16 | Workplace Safety and Insurance Act, 1997 | `97w16/` | 66 | 2003-03-15 to 2026-04-24 | 227 |
| 98a22 | Apprenticeship and Certification Act, 1998 | `98a22/` | 7 | 2000-07-01 to 2013-04-08 | 0 |
| 98b13 | Back to School Act, 1998 | `98b13/` | 4 | 1998-09-29 to 2009-12-15 | 0 |
| 98c19 | Condominium Act, 1998 | `98c19/` | 39 | 2003-01-01 to 2025-12-31 | 266 |
| 98c32 | City of Toronto XXIX Summer Olympic Games Bid Endorsement Act, 1998 | `98c32/` | 2 | 1998-12-18 to 2006-06-22 | 0 |
| 98e15 | Electricity Act, 1998 | `98e15/` | 86 | 2004-01-01 to 2026-04-24 | 366 |
| 98e34 | Estate Administration Tax Act, 1998 | `98e34/` | 4 | 2001-12-05 to 2024-05-16 | 22 |
| 98f01 | Farming and Food Production Protection Act, 1998 | `98f01/` | 5 | 2003-01-01 to 2017-11-14 | 15 |
| 98h25 | Holocaust Memorial Day Act, 1998 | `98h25/` | 1 | 1998-12-18 to 1998-12-18 | 4 |
| 98h28 | Highway 407 Act, 1998 | `98h28/` | 16 | 2004-01-01 to 2024-04-01 | 68 |
| 98h37 | Hummingbird Performing Arts Centre Corporation Act, 1998 | `98h37/` | 6 | 1998-12-18 to 2017-05-30 | 0 |
| 98i29 | Intercountry Adoption Act, 1998 | `98i29/` | 7 | 2000-04-01 to 2025-07-01 | 33 |
| 98l26 | Legal Aid Services Act, 1998 | `98l26/` | 19 | 2002-11-26 to 2021-10-18 | 0 |
| 98l27 | Lobbyists Registration Act, 1998 | `98l27/` | 18 | 2003-01-01 to 2024-04-01 | 41 |
| 98m18 | Ministry of Health and Long-Term Care Appeal and Review Boards Act, 1998 | `98m18/` | 24 | 2002-11-26 to 2024-12-01 | 22 |
| 98o05 | Ontario Loan Act, 1998 | `98o05/` | 1 | 1998-06-26 to 1998-06-26 | 5 |
| 98o10 | Ontario Agriculture Week Act, 1998 | `98o10/` | 1 | 1998-06-26 to 1998-06-26 | 3 |
| 98o15 | Ontario Energy Board Act, 1998 | `98o15/` | 88 | 2003-12-18 to 2025-12-11 | 261 |
| 98s12 | Sunnybrook and Women’s College Health Sciences Centre Act, 1998 | `98s12/` | 2 | 1998-06-26 to 2007-06-04 | 0 |
| 98s18 | Statute and Regulation Revision Act, 1998 | `98s18/` | 3 | 1998-12-18 to 2007-07-25 | 0 |
| 98s31 | Social Work and Social Service Work Act, 1998 | `98s31/` | 10 | 2001-11-01 to 2024-07-01 | 80 |
| 98t15 | Toronto District Heating Corporation Act, 1998 | `98t15/` | 5 | 2003-01-01 to 2021-06-01 | 17 |
| 99b07 | Balanced Budget Act, 1999 | `99b07/` | 3 | 2001-04-01 to 2004-12-16 | 0 |
| 99c14a | City of Greater Sudbury Act, 1999 | `99c14a/` | 18 | 2003-01-01 to 2024-04-01 | 54 |
| 99c14c | City of Hamilton Act, 1999 | `99c14c/` | 24 | 2003-01-01 to 2025-06-05 | 55 |
| 99c14e | City of Ottawa Act, 1999 | `99c14e/` | 24 | 2003-01-01 to 2024-04-01 | 64 |
| 99e12 | Enforcement of Judgments Conventions Act, 1999 | `99e12/` | 1 | 1999-12-22 to 1999-12-22 | 8 |
| 99f04 | Fairness is a Two-Way Street Act (Construction Labour Mobility), 1999 | `99f04/` | 5 | 2003-01-01 to 2006-06-30 | 0 |
| 99l12 | Licence Appeal Tribunal Act, 1999 | `99l12/` | 50 | 2002-12-13 to 2025-01-01 | 17 |
| 99o12 | Ontario Lottery and Gaming Corporation Act, 1999 | `99o12/` | 23 | 2000-04-01 to 2026-04-01 | 28 |
| 99s08 | Safe Streets Act, 1999 | `99s08/` | 2 | 2003-01-01 to 2005-12-15 | 10 |
| 99s12 | Settlement of International Investment Disputes Act, 1999 | `99s12/` | 2 | 1999-12-22 to 2011-12-31 | 16 |
| 99t07 | Taxpayer Protection Act, 1999 | `99t07/` | 15 | 2002-06-27 to 2024-05-16 | 25 |
| 99t14b | Town of Haldimand Act, 1999 | `99t14b/` | 17 | 2003-01-01 to 2021-11-29 | 63 |
| 99t14d | Town of Norfolk Act, 1999 | `99t14d/` | 17 | 2003-01-01 to 2021-11-29 | 54 |
| 99u16 | University of Ottawa Heart Institute Act, 1999 | `99u16/` | 1 | 2000-04-01 to 2000-04-01 | 9 |
| 99v03 | Vintners Quality Alliance Act, 1999 | `99v03/` | 9 | 2001-06-29 to 2021-11-29 | 18 |

The data was retrieved on 2026-10-28, 2026-10-29: one request at a time, at least 1.1 seconds apart (robots.txt asks for
`Crawl-delay: 1` and names no AI agents; the paths read are not disallowed), with gzip, and the user agent
`lexifina-watch/1.0 (+https://lexifina.com/watch; corpus@lexifina.com)`. Fetch rate: one request per 1.1 seconds or
slower. No login, no challenge page. e-Laws offers no bulk download of past versions.

## The build, step by step

1. `python -X utf8 scripts/canada-ontario-law/fetch_versions.py`, then `build.py --today 2026-10-29` in Lexifina's own
   repository fetched the data into the cache and wrote this repository. `tools/build.py` here is the same file
   (git blob `95d9f5c468cfde9a05ec27d8d090cfcdd3dc3edf`), with `tools/fetchlib.py` (the cached fetcher), `tools/fetch_versions.py`, `tools/reproduce.py`,
   which writes this file, `tools/check_repo.py` and `tools/test_repo.py`. Every later build ran with `--offline`.
2. `python -X utf8 scripts/canada-ontario-law/check_repo.py` read every version of each act back from this repository
   on the day it took effect and compared it file by file with the text parsed afresh from the cached answer; then it
   compared the letters and digits of the whole act with those of the raw version, read by a separate minimal
   extractor that does not use the build's parser. Result: `293 versions checked (82236 files), 0 mismatches; letters and digits of every version (118582957 characters) against the raw source, 0 mismatches`.
3. `python -X utf8 scripts/canada-ontario-law/test_repo.py --record` ran the functional smoke test (6 of 6 passed):
   - pass: blame names a law: 90h08/s-041.md lines by S.O. 2007, c. 13, S.O. 2009, c. 5, S.O. 2015, c. 14, S.O. 2019, c. 8, S.O. 2024, c. 21, S.O. 2024, c. 9, e-Laws (King's Printer for Ontario)
   - pass: text before and after an amendment: 90h08/s-041.md 2009-04-22 != 2009-04-23; 00e41/s-015.md 2021-12-01 != 2021-12-02; 06r17/s-053.md 2026-09-20 != 2026-09-21
   - pass: log --follow in date order: 90h08/s-041.md 10 commits; 00e41/s-015.md 20 commits; 06r17/s-053.md 3 commits
   - pass: tags resolve, In-force on every commit: 529 tags resolve; all 357 commits carry In-force
   - pass: only the documentation commit is by Lexifina: only the documentation commit 23e49a77da is by Lexifina; 120 distinct authors
   - pass: README commands run: 9 README commands ran and printed output
4. `python -X utf8 scripts/canada-ontario-law/build.py --offline --today 2026-10-29 --verify-rebuild` built the repository
   a second time from the same cache into a temporary folder and compared the hashes. A second build from the same cache into an empty folder gave the same history: the last law commit was `a6448b41e683e3524bf20db3b00ba6c8e65ff3c0` in both, and every one of the 356 law commits and 529 tags had the same hash.
5. The build was run once more to write these results into this file, and the final `main` was rebuilt again and
   compared hash for hash before it was pushed.
6. `git push origin main --tags` published it to the private GitHub repository `lexifina/canada-ontario-law`.

It ran with Python 3.12.10, lxml 6.1.3 and git version 2.46.0.windows.1 on Windows 11. No network service other than e-Laws is involved.

## How the text and the commits are derived

Everything below is done by `tools/build.py`, deterministically.

- **Text in force.** Each version's HTML is a flat run of paragraphs, each with a class: `section`, `subsection`,
  `clause`, `definition`, `headnote`, `partnum` and so on (older versions add `-e`). e-Laws prints the text of
  amendments not yet in force in the same consolidation, shaded: classes beginning with `Y` (`Ysection`,
  `Yheadnote`, ...), announced by a note (`Pnote`, "Note: On a day to be named by proclamation ..."). That text is not
  law in force on the version's days, so it is left out, with its notes; on the older pages, which do not shade the
  headnote of a section not yet in force, the headnote directly before a shaded section goes with it. The publisher's
  notice "Disclaimer: This consolidation is not an official copy ..." (two versions of the Employment Standards Act,
  2000, in 2021) and the table of contents are left out too.
- **Files.** Each act is a folder named by its e-Laws identifier (`90h08/`). Each section is one file, named by its
  number with the whole part padded to three digits: `90h08/s-041.0.1.md`; a group printed as one ("247.-260.
  Omitted") is `s-247-260.md`; where the act numbers two sections the same (the Highway Traffic Act's two sections 206
  in 2020-2021), the second is `s-206-b.md`. The headings that begin with a section are `##` (Part), `###`/`####`
  (headings) and `#####` (the headnote) lines; every other paragraph is one line, as printed, with the citations that
  end it. Tables are one line per row, cells separated by ` | `; images are left out. `intro.md` holds the short
  title, the chapter, and anything printed before the first heading; `schedule[-<n>].md` each schedule.
- **Normalised.** Only white space (runs of spaces, line breaks, tabs, no-break and other Unicode spaces become one
  space), soft hyphens and zero-width characters (removed).
- **Changes.** Consecutive versions are compared file by file. 73465 changes of a file were found.
- **Cause.** Tried in this order for each changed file:
  1. since 2016, the section's list "Section Amendments with date in force (d/m/y)" names a law with this day: that
     law (14784 file changes);
  2. a citation new in the file names exactly one law other than the act itself: that law (13116);
  3. only the act's own citation is new (its own provisions taking effect, such as the Legislation Act, 2006 on
     2007-07-25): the act itself (6197);
  4. the list or the new citations name two or more laws: none; committed by the publisher naming them
     (1269);
  5. the same letters and digits as before (spacing, punctuation, hyphens, case, section-number style such as `1.`
     becoming `1` in 2017): a layout commit by the publisher (22517);
  6. no law named for the file, and exactly one law named for the act that day: that law, by date only, labelled
     `Evidence: date only` (2764);
  7. no law named for the file, two or more for the act that day: none; publisher, `Candidate:` trailers
     (0);
  8. nothing named anywhere in the version: no law; committed by the publisher and labelled
     (2872).
- **Date.** The day the version applies from on e-Laws ("Historical version for the period June 20, 2012 to December
  30, 2012"); the build checks that the versions follow each other without a gap. For the version a law produced, that
  is the day the law's provisions took effect.
- **Commits.** One commit per amending law per day (2235 commits by 691 laws), covering every act of the
  record it changed that day; one for the first version of each act (1129); 549 for
  changes with two or more candidate laws; 445 for changes nothing explains; 1039 for
  layout only; 1977 for versions with no change in the English text in force. They are in the order
  they took effect, then one for this documentation.
  - The author is the amending law, `S.O. 2009, c. 5` (Statutes of Ontario 2009, chapter 5), at an address ending
    `@ontario.invalid` (`so-2009-c5@ontario.invalid`), which cannot exist. Publisher commits are by
    `e-Laws (King's Printer for Ontario) <e-laws@ontario.invalid>`, labelled in the subject.
  - Author and committer dates are noon in Toronto on the day the change took effect: UTC-5, or UTC-4 in daylight
    time (from the second Sunday in March to the first Sunday in November since 2007; from the first Sunday in April
    to the last Sunday in October from 1987 to 2006), written into the code because the build machine has no
    time-zone database. The committer is `Lexifina <canada-ontario-law@lexifina.com>`.
  - Trailers: `Evidence:`, `Kind:`, `Enacted:` (Royal Assent), `Date-note:`, `In-force:`, `Source:` (the act as
    enacted), `Affecting:` (one line per provision, `90h08 s. 38`), `Candidate:` and `Consolidated:` (the version the
    text came from).
  - Tags: each act's days (`90h08/2009-10-03`) and each amending law (`so/2009-c5`; a law that took effect on several
    days has one tag per day, `so/2015-c14/2017-05-01`); 12395 in all.
- **Documentation commit.** Dated 2026-10-29, the `--today` of the build, so a later rebuild of the same data with the same
  `--today` gives the same hash. It carries `In-force: 2026-10-29` and `Kind: documentation`.

Changes credited by date only:

2764 in all.

- 00c01 2024-04-01: Title -> S.O. 2019, c. 1
- 00c01 2024-12-04: s. 1 -> S.O. 2024, c. 27
- 00e17 2015-07-01: s. 26 -> S.O. 2013, c. 2
- 00e41 2004-06-29: s. 135 -> S.O. 2004, c. 15
- 00e41 2005-06-13: s. 52 -> S.O. 2004, c. 15
- 00e41 2006-06-30: s. 50 -> S.O. 2006, c. 13
- 00e41 2007-04-01: s. 3 -> S.O. 2006, c. 34
- 00e41 2007-07-25: s. 118 -> S.O. 2006, c. 21
- 00e41 2007-08-20: s. 50 -> S.O. 2006, c. 35
- 00e41 2008-10-08: s. 49.1 -> S.O. 2008, c. 15
- 00e41 2009-12-15: s. 74.11.1 -> S.O. 2009, c. 33
- 00e41 2015-02-20: s. 103 -> S.O. 2014, c. 10
- 00e41 2015-05-20: s. 2 -> S.O. 2014, c. 10
- 00e41 2015-11-20: s. 74.5 -> S.O. 2014, c. 10
- 00e41 2017-12-03: s. 74.14 -> S.O. 2017, c. 22
- 00e41 2022-05-01: s. 45 -> S.O. 2019, c. 5
- 00e41 2023-01-01: s. 91.1 -> S.O. 2022, c. 7
- 00e41 2023-07-01: s. 74.13 -> S.O. 2021, c. 35
- 00e41 2023-10-26: s. 54 -> S.O. 2023, c. 15
- 00p36 2010-06-08: s. 7 -> S.O. 2010, c. 12
- 00s44 2006-05-18: s. 16 -> S.O. 2006, c. 9
- 00s44 2006-05-18: s. 17 -> S.O. 2006, c. 9
- 00t16 2010-05-01: s. 43 -> S.O. 2009, c. 28
- 00t16 2010-05-01: s. 44 -> S.O. 2009, c. 28
- 00t16 2018-05-07: s. 1 -> S.O. 2018, c. 7
- ... and 2739 more (all in `data/uncertain.tsv`)

Changes whose amendment list or new citations name two or more laws (credited to none):

1269 in all.

- 00c01 2026-04-01: s. 1 (candidates: S.O. 2024, c. 27, S.O. 2025, c. 6)
- 00c01 2026-04-01: s. 10 (candidates: S.O. 2024, c. 27, S.O. 2025, c. 24)
- 00c01 2026-04-01: s. 14 (candidates: S.O. 2024, c. 27, S.O. 2025, c. 24, S.O. 2025, c. 6)
- 00c01 2026-04-01: s. 3 (candidates: S.O. 2024, c. 27, S.O. 2025, c. 6)
- 00e41 2019-01-01: s. 141 (candidates: S.O. 2017, c. 22, S.O. 2018, c. 14)
- 00e41 2019-01-01: s. 15 (candidates: S.O. 2017, c. 22, S.O. 2018, c. 14)
- 00e41 2019-01-01: s. 21.2 (candidates: S.O. 2017, c. 22, S.O. 2018, c. 14)
- 00e41 2026-01-01: s. 15 (candidates: S.O. 2024, c. 19, S.O. 2024, c. 3, S.O. 2025, c. 13)
- 00e41 2026-01-01: s. 8.1 (candidates: S.O. 2024, c. 3, S.O. 2025, c. 13)
- 00s27 2007-01-01: s. 95 (candidates: S.O. 2006, c. 11, S.O. 2006, c. 32)
- 00t16 2022-07-01: s. 32.1 (candidates: S.O. 2018, c. 7, S.O. 2019, c. 4)
- 00t16 2022-07-01: s. 37 (candidates: S.O. 2018, c. 7, S.O. 2019, c. 4)
- 00t16 2022-07-01: s. 4 (candidates: S.O. 2018, c. 7, S.O. 2019, c. 4)
- 00t16 2022-07-01: s. 5 (candidates: S.O. 2018, c. 7, S.O. 2019, c. 4)
- 01a10 2019-03-26: s. 1 (candidates: S.O. 2018, c. 3, S.O. 2019, c. 1)
- 01m25 2007-01-01: s. 283 (candidates: S.O. 2006, c. 11, S.O. 2006, c. 32)
- 01m25 2007-01-01: s. 315 (candidates: S.O. 2006, c. 11, S.O. 2006, c. 32)
- 01m25 2007-01-01: s. 7.1 (candidates: S.O. 2006, c. 11, S.O. 2006, c. 32)
- 01m25 2011-01-01: s. 323 (candidates: S.O. 2008, c. 14, S.O. 2009, c. 33)
- 01m25 2016-12-10: s. 329 (candidates: S.O. 2004, c. 31, S.O. 2008, c. 7)
- 01r28 2021-03-01: s. 21 (candidates: S.O. 2019, c. 7, S.O. 2020, c. 11)
- 02c30 2024-01-01: s. 65.12 (candidates: S.O. 2019, c. 1, S.O. 2021, c. 26)
- 02f33 2012-07-01: s. 108 (candidates: S.O. 2006, c. 21, S.O. 2006, c. 34, S.O. 2012, c. 8)
- 02f33 2012-07-01: s. 14 (candidates: S.O. 2006, c. 34, S.O. 2009, c. 33)
- 02f33 2012-07-01: s. 29 (candidates: S.O. 2006, c. 34, S.O. 2007, c. 8)
- ... and 1244 more (all in `data/uncertain.tsv`)

Changes naming no law, on a day two or more laws are new (credited to none):

- none

Changes nothing explains (publisher):

2872 in all.

- 00e17 2013-06-13: Title
- 00e41 2006-06-20: s. 141
- 00e41 2006-12-20: s. 142
- 01c33 2008-03-28: s. 15
- 01m25 2006-10-19: s. 365.1
- 01m25 2019-03-26: s. 409
- 01o32 2011-12-31: s. 21
- 01p16 2023-05-18: Title
- 02c30 2006-12-20: s. 107
- 02c30 2019-03-26: s. 107
- 02f33 2012-12-31: s. 10
- 02f33 2012-12-31: s. 11
- 02f33 2012-12-31: s. 4
- 02f33 2012-12-31: s. 56
- 02l24 2007-01-01: Schedule
- 02l24 2009-01-01: Schedule
- 02l24 2009-05-14: Schedule
- 02l24 2010-01-25: Schedule
- 02l24 2010-10-25: Schedule
- 02l24 2020-12-08: Schedule
- 02l24 2021-12-02: Schedule
- 02r05 2010-07-01: Title
- 02r30 2012-12-31: s. 8
- 02s32 2019-12-31: s. 168
- 02t30 2004-06-17: Title
- ... and 2847 more (all in `data/uncertain.tsv`)

Changes whose new text equals an earlier version of the same file (labelled as a reprint of older text):

570 in all.

- 00e41 2017-12-03: s. 74.14
- 00e41 2025-06-19: s. 1
- 00e41 2025-06-19: s. 10
- 00e41 2025-06-19: s. 100
- 00e41 2025-06-19: s. 102
- 00e41 2025-06-19: s. 102.1
- 00e41 2025-06-19: s. 103
- 00e41 2025-06-19: s. 105
- 00e41 2025-06-19: s. 106
- 00e41 2025-06-19: s. 11
- 00e41 2025-06-19: s. 111
- 00e41 2025-06-19: s. 112
- 00e41 2025-06-19: s. 113
- 00e41 2025-06-19: s. 114
- 00e41 2025-06-19: s. 115
- 00e41 2025-06-19: s. 116
- 00e41 2025-06-19: s. 117
- 00e41 2025-06-19: s. 118
- 00e41 2025-06-19: s. 119
- 00e41 2025-06-19: s. 12
- 00e41 2025-06-19: s. 120
- 00e41 2025-06-19: s. 122
- 00e41 2025-06-19: s. 125.3
- 00e41 2025-06-19: s. 127
- 00e41 2025-06-19: s. 128
- ... and 545 more (all in `data/uncertain.tsv`)

## Decisions made by hand

1. **The acts.** Every consolidated statute e-Laws lists, current and "Repealed / Revoked / Spent": 1288 listed, 1129 in the record, 272 of them repealed within it. The 159 acts
   whose only version on e-Laws is the repealed one (repealed before e-Laws kept point-in-time versions) are not in the
   record, because no day on which their text was in force is known: 00s45 (2001-06-29), 03o04 (2003-12-18), 10s26 (2011-03-30), 90a01 (1997-03-01), 90a04 (1997-10-29), 90a10 (1994-12-09), 90a12 (1994-12-09), 90a20 (2001-06-27), 90a29 (2000-01-01), 90b08 (1998-01-01), 90b09 (2001-06-27), 90b11 (1996-01-30), 90b15 (1994-12-09), 90c02 (1997-10-10), 90c26 (2001-05-05), 90c36 (1994-12-09), 90c42 (2003-01-01), 90c44 (1995-03-01), 90c46 (1997-01-01), 90c51 (1995-04-01), 90d05 (2001-10-01), 90d08 (1997-10-10), 90d09 (1998-03-01), 90d14 (2003-01-01), 90e03 (1997-10-29), 90e08 (2001-06-27), 90e10 (1997-10-10), 90e13 (2001-03-31), 90e14 (2001-09-04), 90e16 (2001-06-27), 90f05 (1997-01-01), 90f06 (1998-05-11), 90f11 (2003-01-01), 90f14 (1997-10-29), 90f15 (1997-10-29), 90f16 (1997-10-29), 90f17 (1997-10-29), 90f25 (1998-12-18), 90f27 (1998-12-18), 90f37 (1997-03-01), 90g01 (1999-01-01), 90g04 (2001-06-27), 90g06 (1998-05-01), 90g08 (2001-09-04), 90g11 (1997-10-10), 90h11 (2001-11-30), 90h16 (1998-07-31), 90h21 (2000-12-06), 90h22 (1997-10-10), 90i06 (2001-09-04), 90i13 (1996-04-01), 90i14 (1997-10-10), 90j02 (2000-09-01), 90l02 (1995-11-10), 90l09 (1999-04-01), 90l11 (1992-01-01), 90l26 (2003-01-01), 90m06 (1995-10-06), 90m09 (1995-04-03), 90m38 (1994-11-30), 90m45 (2003-01-01), 90m47 (1998-01-01), 90m49 (2003-01-01), 90m52 (2003-01-01), 90m53 (1996-12-19), 90m58 (2003-01-01), 90m60 (2003-01-01), 90m61 (2003-01-01), 90m62 (2000-12-06), 90n04 (1997-03-01), 90o05 (1997-11-03), 90o07 (2001-09-04), 90o09 (1997-10-10), 90o11 (1997-10-10), 90o13 (1998-11-07), 90o14 (1998-12-18), 90o22 (1996-07-01), 90o25 (2000-04-01), 90o33 (1997-10-10), 90o35 (1995-01-01), 90o37 (1999-12-22), 90o38 (2003-01-01), 90o39 (1997-06-05), 90o41 (2001-06-29), 90o42 (2001-06-27), 90p02 (1998-12-18), 90p03 (1995-01-01), 90p16 (1998-12-18), 90p19 (1999-04-01), 90p31 (1994-12-09), 90p39 (1996-01-30), 90p42 (1994-12-09), 90p46 (2003-01-01), 90p53 (2003-01-01), 90r02 (2000-12-15), 90r07 (2006-03-31), 90r08 (2003-01-01), 90r09 (2003-01-01), 90r10 (2001-01-01), 90r11 (2003-01-01), 90r12 (2001-01-01), 90r13 (2003-01-01), 90r14 (2001-01-01), 90r15 (2003-01-01), 90r16 (2001-01-01), 90r17 (2003-01-01), 90r18 (2003-01-01), 90r24 (1998-06-17), 90r26 (1999-05-05), 90r32 (1997-04-01), 90r36 (1999-04-01), 90r37 (1999-04-01), 90s02 (1998-01-01), 90s06 (1994-12-09), 90s08 (1998-12-18), 90s09 (1998-12-18), 90s14 (2003-01-01), 90s16 (1997-11-28), 90s17 (1998-12-18), 90s23 (2001-04-27), 90s25 (1999-12-22), 90s28 (1997-05-12), 90t03 (1999-12-22), 90t04 (2003-01-01), 90t05 (2003-01-01), 90t12 (2003-01-01), 90t20 (1998-12-18), 90u04 (2001-06-27), 90v05 (1999-01-18), 90w02 (1997-10-10), 90w06 (2003-01-01), 90w09 (2000-12-31), 90w10 (1998-12-18), 90w11 (1998-01-01), 90w12 (1998-01-01), 92a26 (1996-03-29), 92c31 (1996-03-29), 92l27 (2003-01-01), 92r11 (1998-06-17), 92s33 (2001-06-29), 93c26 (2003-01-01), 93c33 (2003-01-01), 93e35 (1995-12-14), 93f17 (1997-10-29), 93o09 (2000-12-06), 93o25 (2000-04-01), 93s43 (2001-06-29), 94a06 (1995-11-10), 94l23 (2003-01-01), 94s40 (2001-06-29), 94v39 (2003-07-01), 96a17b (1999-03-31), 96s08 (2001-06-29), 97o10 (1997-06-26), 97s30 (2001-01-01), 97s46 (2001-06-29), 98c07 (1999-04-01), 98g23 (2002-01-01), 99s17 (2001-06-29). Regulations are in a separate
   record (`lexifina/canada-ontario-regulations`).
2. **In force only.** Shaded text of amendments not yet in force is left out of every version, so each commit holds
   the law in force on its day. There is no `future` branch: e-Laws gives no day for unproclaimed amendments.
3. **The consolidation's own evidence.** A change is credited to a law only when the section's amendment list gives it
   this day, when its citation is new in the changed file, or by date only (labelled) when it is the only law named that
   day. The amending acts' commencement sections were not parsed.
4. **Two laws are not separated.** Where the evidence names two laws for one file on one day, the amending texts were
   not read to divide the change; it is the publisher's, naming both.
5. **Layout is not law.** A change that leaves every letter and digit in place (e-Laws re-typeset all its statutes in
   2017, dropping the period after section numbers) is the publisher's, labelled `layout only`.
6. **The record starts with the first point-in-time version** of each act on e-Laws (1986-07-28 at the earliest).
   That version is credited to the act that enacted it when it applies from on or after that act's Royal Assent and
   every provision in it cites only that act (569 acts, `Kind: Act of the Legislative Assembly of Ontario`,
   `Enacted:`); otherwise to the publisher, since it already holds amendments made before it.
7. **Repeals.** A repealed act's last version on e-Laws is marked "Repealed / Revoked / Spent" and starts on the day of
   the repeal, with a note ("This Act was repealed on March 1, 1997. See: 1996, c. 17, Sched. J ..."). On that day
   every file of the act is removed, in a commit by the one law the note cites; by the act itself when the note cites
   only one of its own sections; otherwise by the publisher. The act's folder keeps its `README.md`.
8. **Version lists repaired.** Where an act's version list does not join day to day, these repairs were made (rules
   in `version_list` in `tools/build.py`):

- 01a10 v0: last day 2008-11-30 before its first day ignored
- 01r28 v0: listed from 2022-04-14, before v14 ends (2024-03-31); starts 2024-04-01
- 06f31 v16: text not served (404) for v15 from 2018-05-08; the version before stays in force until this one
- 08p17 v5: gap: v3 ends 2019-06-05, this version starts 2019-07-01 (a version between them is not listed); v3 stays in force until then
- 14c11 v19: gap: v17 ends 2024-06-05, this version starts 2025-06-06 (a version between them is not listed); v17 stays in force until then
- 19s07 v4: text not served (404) for v2 from 2019-08-06, v3 from 2023-05-18; the version before stays in force until this one
- 19s07 v0: text not served (404) for v5 from 2023-12-04; the version before stays in force until this one
- 90a31 v47: text not served (404) for v46 from 2023-01-01; the version before stays in force until this one
- 90c14 v22: listed from 2019-05-29, before v21 ends (2019-05-29); starts 2019-05-30
- 90h06 v0: last day 2015-06-30 before its first day ignored
- 90m31 v0: last day 2018-12-05 before its first day ignored
- 90n02 v0: last day 2018-12-05 before its first day ignored
- 90o21 v11: v10 is listed for the same days (2018-01-01 to 2020-07-20); this one, the later number, is taken
- 90p35 v8: text not served (404) for v7 from 2014-04-24; the version before stays in force until this one
- 90p51 v10: gap: v8 ends 2019-05-28, this version starts 2019-07-01 (a version between them is not listed); v8 stays in force until then
- 94t10 v15: text not served (404) for v12 from 2010-07-01, v13 from 2014-12-04, v14 from 2015-05-28; the version before stays in force until this one
- 98c19 v0: last day 2015-12-02 before its first day ignored

9. **Repeals not credited to one law:**

13 in all.

- 01h23 2011-12-31: the repeal note names no law: "Note: This Act was repealed on December 31, 2011. See: Table of Public Statute Provisions Repealed Under Section 10.1 of the Legislation Act, 2006 – December 31, 2011."
- 02c31 2012-12-31: the repeal note names no law: "Note: This Act was repealed on December 31, 2012. See: Table of Public Statute Provisions Repealed Under Section 10.1 of the Legislation Act, 2006 – December 31, 2012."
- 02r05 2012-12-31: the repeal note names no law: "Note: This Act was repealed on December 31, 2012. See: Table of Public Statute Provisions Repealed Under Section 10.1 of the Legislation Act, 2006 – December 31, 2012."
- 02s29 2012-12-31: the repeal note names no law: "Note: This Act was repealed on December 31, 2012. See: Table of Public Statute Provisions Repealed Under Section 10.1 of the Legislation Act, 2006 – December 31, 2012."
- 08t04 2019-11-15: repeal note (its own section): "Note: This Act was repealed on November 15, 2019. (See: s. 20)"
- 09y01 2019-11-15: repeal note (its own section): "Note: This Act was repealed on November 15, 2019. (See: s. 20)"
- 10o26 2020-07-01: repeal note (its own section): "Note: This Act was repealed on July 1, 2020. (See: s. 18)"
- 12g08 2022-12-31: the repeal note names no law: "Note: This Act was repealed on December 31, 2022. See: Table of Public Statute Provisions Repealed Under Section 10.1 of the Legislation Act, 2006."
- 16s03 2017-04-01: the repeal note names no law: "Note: This Act was repealed on April 1, 2017."
- 90e01 2005-01-01: the repeal note names two or more laws: "Note: This Act was repealed on January 1, 2005. See: 2001, c. 20, ss. 57, 61 (2). See also 2002, c. 35, ss. 1, 2; 2004, c. 4, ss. 1, 2."
- 90s20 2022-01-01: the repeal note names two or more laws: "Note: This Act was repealed on January 1, 2022. (See: 2019, c. 14, Sched. 14, s. 6 and 2021, c. 25, Sched. 26, s. 2)"
- 90t13 2011-05-12: repeal note (its own section): "Note: This Act was repealed on May 12, 2011. See: 2011. c. 9, Sched. 41, ss. 1, 4."
- 90u01 2011-12-31: the repeal note names no law: "Note: This Act was repealed on December 31, 2011. See: Table of Public Statute Provisions Repealed Under Section 10.1 of the Legislation Act, 2006 – December 31, 2011."
10. **English only.** The French version is equally authoritative; it is not recorded.

## What an AI model did

This repository was built on 2026-10-29 in **Claude Code**, Anthropic's coding tool, by the model **Claude Opus 5.5**
(model id `claude-opus-5-5`), working from a brief by the user at Lexifina: a private "git for law" repository for
Ontario to the same standard as Lexifina's other corpora.

The model researched the source (e-Laws' pages and the JSON interface behind them, the shape of their HTML, robots.txt
and the King's Printer's copyright policy), wrote all the code and text in this repository, ran the commands above and
checked the results. It did **not** write or edit any legal text: every word of every provision, every date and every
law's title is copied by the script from e-Laws. No AI model is called when the history is built or checked. The work
was not reviewed line by line by a lawyer. This is not an official version (see the README).

## Prior art

- e-Laws itself, whose "Versions" tab shows each point-in-time version; it has no change-by-change view.
- Lexifina's other corpora, whose rules this one follows, and `lexifina/canada-law` (federal Acts), whose builder this
  one adapts.
