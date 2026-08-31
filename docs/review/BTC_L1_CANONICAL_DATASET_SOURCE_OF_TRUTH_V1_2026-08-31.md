# BTC-L1 CANONICAL DATASET SOURCE OF TRUTH V1

Date: 2026-08-31

Status:
CANONICAL DATASET GOVERNANCE RECORD V1

Scope:
BTCUSDT
1-minute historical Live-L1 / BTC-L1 development and regression dataset

Purpose:
This document permanently records the identity, physical integrity,
historical raw-data comparison, known provenance limitations, and
future governance rules for the BTC-L1 canonical historical dataset.

This document exists specifically to prevent repeated re-investigation
of the same dataset identity and provenance questions.

Unless one of the explicit RE-AUDIT TRIGGERS in this document occurs,
the dataset facts established here MUST be treated as settled.

======================================================================
1. CANONICAL HISTORICAL DATASET
======================================================================

Canonical logical path:

data/l1_full_run.csv

Physical artifact inspected on 2026-08-31:

/mnt/c/Users/workstation/Desktop/sniper-bot/data/l1_full_run.csv

Market:

BTCUSDT

Granularity:

1 minute

Physical identity:

SHA-256:
530983b84c461d46a49058428b1549fa87fd320cb2f04a070eeb081275aafe1f

File size:
463326873 bytes

Total file lines:
4374558

Header lines:
1

Data rows:
4374557

Number of columns:
22

First timestamp:
2017-08-17T04:00:00+00:00

Last timestamp:
2025-12-31T23:59:00+00:00

Expected continuous minute span:
4404720 minutes

Observed data rows:
4374557

Difference:
30163 minutes

Exact detected L1 time gaps:
33

Exact missing minutes represented by the 33 gaps:
30163

Gap accounting:
PASS

Therefore:

continuous-span row deficit
=
sum of detected time-gap minutes

There is no unexplained additional row deficit.

======================================================================
2. CSV STRUCTURAL INTEGRITY AUDIT
======================================================================

Full streaming audit result on 2026-08-31:

HEADER_EXACT_MATCH=PASS
BAD_COLUMN_COUNT_ROWS=0
EMPTY_FIELD_ROWS=0
INVALID_TIMESTAMPS=0
NON_MINUTE_ALIGNED=0
DUPLICATE_TIMESTAMPS=0
NON_INCREASING_TIMESTAMPS=0
INVALID_NUMERIC={}
INVALID_OHLC_ROWS=0
NEGATIVE_VOLUME_ROWS=0
INVALID_SIGNAL_VALUES={}
INVALID_REGIME_VALUES={}
INVALID_GATE_VALUES={}

STRUCTURAL_INTEGRITY=PASS
GAP_ACCOUNTING=PASS

Interpretation:

The canonical L1 CSV is structurally ordered and internally consistent.
No malformed timestamps, duplicate timestamps, reversed timestamps,
invalid OHLC values, invalid signal values, invalid regime values,
or invalid gate values were found.

======================================================================
3. CANONICAL COLUMN SCHEMA
======================================================================

The exact validated header is:

timestamp_utc
open
high
low
close
volume
rsi_signal
macd_signal
bollinger_signal
ma200_signal
stoch_signal
atr_signal
ema50_signal
adx_signal
cci_signal
mfi_signal
obv_signal
roc_signal
regime_v1
allow_long
allow_short
regime_v2

Header validation:
PASS

======================================================================
4. INDEPENDENT BINANCE RAW REFERENCE SET
======================================================================

A new Binance historical raw download exists under:

data/btcusdt_1m_2026-07-22/raw/monthly/

IMPORTANT:

This raw archive set is NOT declared to be the historical build source
of l1_full_run.csv.

It is an independent external reference used to verify the physical
market-data content of the existing canonical L1 dataset.

Only historical archives from 2017-08 through 2025-12 were used in the
2026-08-31 comparison.

2026 market content was explicitly excluded from these audits.

Expected historical monthly archives:
101

Archive completeness:
PASS

First archive:
BTCUSDT-1m-2017-08.zip

Last archive:
BTCUSDT-1m-2025-12.zip

Bad ZIP CRC count:
0

Bad CSV-member count:
0

Historical raw archive-set fingerprint:

99caff2dad446aed5e13739fac807d93740c4b18c7c7baae839cf94f2b95b42f

RAW_ARCHIVE_INTEGRITY=PASS

======================================================================
5. BINANCE RAW TIME-STRUCTURE RESULT
======================================================================

Historical Binance raw rows, 2017-08 through 2025-12:

4396159

Normally UTC-minute-aligned raw rows:

4374557

Non-minute-aligned raw rows:

21602

Canonical l1_full_run.csv data rows:

4374557

Important equality:

BINANCE_MINUTE_ALIGNED_RAW_ROWS
=
L1_CANONICAL_DATA_ROWS
=
4374557

No normally minute-aligned raw rows were identified as omitted by the
canonical L1 dataset.

ALIGNED_PIPELINE_LOSS_SIGNAL=NO

Raw timestamp ordering:

DUPLICATE_OR_BACKWARD_RAW=0
BAD_RAW_ROWS=0
RAW_OVERLAP_COUNT=0

RAW_ORDER_AND_STRUCTURE=PASS

======================================================================
6. TWO HISTORICAL NONSTANDARD BINANCE GRID SEGMENTS
======================================================================

Exactly two large non-minute-aligned Binance raw segments were found.

SEGMENT 1

Offset:
20.799 seconds after the normal UTC minute boundary

Start:
2017-12-04T06:00:20.799000+00:00

End:
2017-12-18T10:00:20.799000+00:00

Rows:
20401

SEGMENT 2

Offset:
14.789 seconds after the normal UTC minute boundary

Start:
2018-02-09T09:59:14.789000+00:00

End:
2018-02-10T05:59:14.789000+00:00

Rows:
1201

Total non-minute-aligned raw rows:

20401 + 1201 = 21602

These two segments explain why two L1 gaps contain a mixture of:

- genuine Binance source downtime, and
- Binance candles on a shifted nonstandard time grid.

The canonical L1 dataset contains only normal UTC-minute-aligned rows.

======================================================================
7. COMPLETE L1 GAP REGISTER
======================================================================

The following 33 gaps are the complete gap set detected in the
canonical l1_full_run.csv on 2026-08-31.

Classification meanings:

SOURCE_GAP
The independently downloaded Binance raw reference contains no normal
or shifted candle coverage for the missing L1 minutes apart from the
underlying source outage.

MIXED_SHIFTED_SOURCE_GAP
The interval contains both an actual Binance source interruption and
a Binance nonstandard shifted candle grid.

No gap was classified as ALIGNED_RAW_OMITTED.

01
Last L1:
2017-09-06T15:59:00+00:00
Next L1:
2017-09-06T23:00:00+00:00
Missing minutes:
420
Classification:
SOURCE_GAP

02
Last L1:
2017-12-04T06:00:00+00:00
Next L1:
2017-12-18T10:14:00+00:00
Missing minutes:
20413
Shifted raw rows inside interval:
20400
Raw source-missing time:
797.554 seconds
Classification:
MIXED_SHIFTED_SOURCE_GAP

03
Last L1:
2017-12-18T12:29:00+00:00
Next L1:
2017-12-18T13:34:00+00:00
Missing minutes:
64
Classification:
SOURCE_GAP

04
Last L1:
2018-01-04T03:00:00+00:00
Next L1:
2018-01-04T05:06:00+00:00
Missing minutes:
125
Classification:
SOURCE_GAP

05
Last L1:
2018-02-08T00:28:00+00:00
Next L1:
2018-02-10T06:15:00+00:00
Missing minutes:
3226
Shifted raw rows inside interval:
1201
Raw source-missing time:
121514.789 seconds
Classification:
MIXED_SHIFTED_SOURCE_GAP

06
2018-02-11T04:00:00+00:00
to
2018-02-11T04:35:00+00:00
Missing minutes:
34
Classification:
SOURCE_GAP

07
2018-06-26T01:59:00+00:00
to
2018-06-26T12:00:00+00:00
Missing minutes:
600
Classification:
SOURCE_GAP

08
2018-06-27T12:59:00+00:00
to
2018-06-27T14:45:00+00:00
Missing minutes:
105
Classification:
SOURCE_GAP

09
2018-07-04T00:22:00+00:00
to
2018-07-04T08:00:00+00:00
Missing minutes:
457
Classification:
SOURCE_GAP

10
2018-10-19T05:59:00+00:00
to
2018-10-19T09:30:00+00:00
Missing minutes:
210
Classification:
SOURCE_GAP

11
2018-11-14T01:59:00+00:00
to
2018-11-14T09:00:00+00:00
Missing minutes:
420
Classification:
SOURCE_GAP

12
2019-03-12T01:59:00+00:00
to
2019-03-12T08:00:00+00:00
Missing minutes:
360
Classification:
SOURCE_GAP

13
2019-05-15T02:59:00+00:00
to
2019-05-15T13:00:00+00:00
Missing minutes:
600
Classification:
SOURCE_GAP

14
2019-06-07T21:13:00+00:00
to
2019-06-07T22:15:00+00:00
Missing minutes:
61
Classification:
SOURCE_GAP

15
2019-08-15T01:59:00+00:00
to
2019-08-15T10:00:00+00:00
Missing minutes:
480
Classification:
SOURCE_GAP

16
2019-11-13T01:59:00+00:00
to
2019-11-13T04:20:00+00:00
Missing minutes:
140
Classification:
SOURCE_GAP

17
2019-11-13T05:29:00+00:00
to
2019-11-13T05:33:00+00:00
Missing minutes:
3
Classification:
SOURCE_GAP

18
2019-11-25T01:59:00+00:00
to
2019-11-25T04:00:00+00:00
Missing minutes:
120
Classification:
SOURCE_GAP

19
2020-02-09T01:59:00+00:00
to
2020-02-09T03:00:00+00:00
Missing minutes:
60
Classification:
SOURCE_GAP

20
2020-02-19T11:35:00+00:00
to
2020-02-19T17:30:00+00:00
Missing minutes:
354
Classification:
SOURCE_GAP

21
2020-03-04T09:21:00+00:00
to
2020-03-04T11:30:00+00:00
Missing minutes:
128
Classification:
SOURCE_GAP

22
2020-04-25T01:59:00+00:00
to
2020-04-25T04:30:00+00:00
Missing minutes:
150
Classification:
SOURCE_GAP

23
2020-06-28T01:59:00+00:00
to
2020-06-28T05:30:00+00:00
Missing minutes:
210
Classification:
SOURCE_GAP

24
2020-11-30T05:59:00+00:00
to
2020-11-30T07:00:00+00:00
Missing minutes:
60
Classification:
SOURCE_GAP

25
2020-12-21T14:09:00+00:00
to
2020-12-21T18:00:00+00:00
Missing minutes:
230
Classification:
SOURCE_GAP

26
2020-12-25T01:59:00+00:00
to
2020-12-25T03:00:00+00:00
Missing minutes:
60
Classification:
SOURCE_GAP

27
2021-02-11T03:40:00+00:00
to
2021-02-11T05:00:00+00:00
Missing minutes:
79
Classification:
SOURCE_GAP

28
2021-03-06T01:59:00+00:00
to
2021-03-06T03:30:00+00:00
Missing minutes:
90
Classification:
SOURCE_GAP

29
2021-04-20T01:59:00+00:00
to
2021-04-20T04:30:00+00:00
Missing minutes:
150
Classification:
SOURCE_GAP

30
2021-04-25T04:00:00+00:00
to
2021-04-25T08:45:00+00:00
Missing minutes:
284
Classification:
SOURCE_GAP

31
2021-08-13T01:59:00+00:00
to
2021-08-13T06:30:00+00:00
Missing minutes:
270
Classification:
SOURCE_GAP

32
2021-09-29T06:59:00+00:00
to
2021-09-29T09:00:00+00:00
Missing minutes:
120
Classification:
SOURCE_GAP

33
2023-03-24T12:39:00+00:00
to
2023-03-24T14:00:00+00:00
Missing minutes:
80
Classification:
SOURCE_GAP

Summary:

SOURCE_GAP:
31

MIXED_SHIFTED_SOURCE_GAP:
2

ALIGNED_RAW_OMITTED:
0

======================================================================
8. IMPORTANT CORRECTION TO THE 2026-08-31 AUDIT OUTPUT
======================================================================

One diagnostic flag printed during the exploratory audit was:

NONSTANDARD_BINANCE_GRID_EFFECT=NO

This flag MUST NOT be used.

It was generated from a classification branch that only counted gaps
classified purely as RAW_SHIFTED.

The two affected intervals were correctly classified as mixed because
they contain BOTH:

- shifted Binance rows; and
- genuine source downtime.

Independent direct measurements established:

NON_MINUTE_ALIGNED_RAW_ROWS=21602
SHIFTED_SEGMENT_COUNT=2

Therefore the authoritative conclusion is:

NONSTANDARD_BINANCE_GRID_EFFECT=CONFIRMED

The old exploratory NO flag is superseded by this document.

======================================================================
9. HISTORICAL SIGNAL / REGIME PROVENANCE LIMITATION
======================================================================

Historical project documentation from 2026-06-05 established that the
exact original generation chain for the following fields could not be
fully reconstructed from the then-active repository:

- regime_v1
- regime_v2
- the 12 signal columns

Multiple attempted online-builder reconstructions did not reproduce
l1_full_run.csv sufficiently.

P1E CSV-vs-Online validation therefore failed.

The project made the explicit safety decision:

- do NOT replace the existing CSV logic with an unvalidated online
  reconstruction;
- retain data/l1_full_run.csv as the Source of Truth for controlled
  Paper operation and deterministic historical operation.

Important distinction:

The unresolved historical build provenance does NOT mean that the
existing CSV is structurally corrupt.

It means that the exact original feature-generation pipeline cannot
currently be reproduced with sufficient certainty.

Therefore:

existing canonical CSV use:
ALLOWED

silent regeneration or replacement:
NOT ALLOWED

online signal/regime replacement without successful equivalence
validation:
NOT ALLOWED

======================================================================
10. DOCUMENTED HISTORICAL DATA-PIPELINE RESULT
======================================================================

The 2026-06-05 LIVE_L1_DATA_AUDIT documented the operational data path:

CSV
->
CSVMarketFeed
->
MarketSnapshot
->
FeatureSnapshot
->
Intent
->
Intent Fusion
->
Execution

That audit reported no data loss between:

CSV
->
MarketSnapshot
->
FeatureSnapshot

and concluded:

LIVE_L1_DATA_AUDIT_2026-06-05
Status:
PASS

This result concerns consumption of the already-built canonical CSV.

It does not claim that the historical feature-generation provenance
was reconstructed.

======================================================================
11. CANONICAL DATASET GOVERNANCE DECISION
======================================================================

For BTC-L1 historical development, deterministic regression,
reproducibility work, and already-exposed historical analysis:

USE:

data/l1_full_run.csv

with mandatory identity:

SHA-256:
530983b84c461d46a49058428b1549fa87fd320cb2f04a070eeb081275aafe1f

Data rows:
4374557

Start:
2017-08-17T04:00:00+00:00

End:
2025-12-31T23:59:00+00:00

DO NOT:

- overwrite this file;
- silently regenerate this file;
- append new future data to this file;
- replace it with a newly downloaded dataset under the same identity;
- rebuild its signal/regime columns and call the result the same
  canonical dataset;
- tune BTC-L1 on a replacement dataset while comparing the result as
  if the data basis were unchanged.

======================================================================
12. ROLE OF THE 2026-07-22 BINANCE DOWNLOAD
======================================================================

The archive tree:

data/btcusdt_1m_2026-07-22/

is a separate raw reference dataset.

Its current roles are:

- independent historical market-data verification;
- provenance research;
- future controlled dataset reconstruction work if explicitly
  authorized.

It MUST NOT silently replace:

data/l1_full_run.csv

The raw archive set and the canonical L1 feature dataset have different
roles and MUST remain logically distinct.

======================================================================
13. FUTURE DATA POLICY
======================================================================

New market data MUST NOT be appended to BTC_L1_CANONICAL_V1.

Future evidence must remain separately identified.

Conceptual separation:

BTC_L1_CANONICAL_V1
=
historical exposed development/regression dataset
2017-08-17 through 2025-12-31

BINANCE_RAW_REFERENCE
=
raw external verification/provenance archive

PROSPECTIVE / PAPER DATA
=
new future observations kept outside CANONICAL_V1

If a completely reproducible historical build pipeline is later
established, a replacement dataset MUST receive a new identity such as:

BTC_L1_CANONICAL_V2

V2 must NOT overwrite V1.

V2 requires at minimum:

- exact raw-source manifest;
- raw-source hashes;
- exact build-code commit;
- build-script hashes;
- parameter/configuration manifest;
- deterministic build verification;
- schema verification;
- exact row count;
- exact min/max timestamps;
- output SHA-256;
- comparison against V1;
- explicit scientific approval before use.

======================================================================
14. MANDATORY RUN BINDING
======================================================================

Every future important BTC-L1 historical run must record at minimum:

dataset logical name
dataset path
dataset SHA-256
dataset row count
dataset first timestamp
dataset last timestamp
Git commit
strategy/config identity
relevant configuration hash where available
execution host
run purpose
run type
start UTC
finish UTC
result artifact locations

A historical BTC-L1 run must fail closed if the dataset hash differs
from:

530983b84c461d46a49058428b1549fa87fd320cb2f04a070eeb081275aafe1f

unless a separately authorized new dataset version is explicitly being
tested.

======================================================================
15. RE-AUDIT TRIGGERS
======================================================================

The 2026-08-31 canonical dataset investigation MUST NOT be repeated
merely because a future operator or chat does not remember the details.

Re-open the dataset audit ONLY if at least one of the following occurs:

1. l1_full_run.csv SHA-256 differs from the canonical hash.

2. File size, row count, schema, first timestamp, or last timestamp
   differs from this record.

3. Storage corruption is suspected.

4. A new canonical dataset version is deliberately proposed.

5. The project intends to regenerate the historical signal/regime
   columns instead of consuming the frozen CSV.

6. New documentary or physical evidence directly contradicts a fact
   established in this record.

7. A transfer/copy of the dataset fails hash verification.

8. A formal scientific review explicitly requires renewed provenance
   investigation.

Absent one of these triggers:

DO NOT REPEAT THE DATASET FORENSICS.

Use this document and the machine-readable identity manifest.

======================================================================
16. CURRENT WORKSTATION REPOSITORY CONTEXT
======================================================================

At the time of the 2026-08-31 audit:

Workstation desktop checkout:

/mnt/c/Users/workstation/Desktop/sniper-bot

Branch:
main

Observed local HEAD:
a5cdc25893cb2d6778e6223dfe46f740b429d747

Observed remote main:
d1e865f29f507fcf7eb405c3be7da4a8946b9861

The local checkout was therefore behind remote main.

One pre-existing tracked local modification was present:

scripts/download_btcusdt_1m_binance_bulk.py

Modification:

DATASET_ROOT changed from:

data/btcusdt_1m_2026-01-07

to:

data/btcusdt_1m_2026-07-22

This modification is NOT part of the canonical dataset identity and
must not be accidentally included in a future documentation-only
commit.

The next compute environment must use an isolated clean checkout of the
intended current repository commit.

======================================================================
17. HISTORICAL DOCUMENTARY SOURCES
======================================================================

Relevant existing repository documents include:

docs/research/LIVE_L1_DATA_AUDIT_2026-06-05.md

docs/research/LIVE_L1_GAP_ANALYSIS_2026-06-05.md

docs/research/LIVE_L1_SIGNAL_SOURCE_ANALYSIS_2026-06-05.md

docs/research/LIVE_L1_SOURCE_OF_TRUTH_STATUS_2026-06-05.md

docs/research/LIVE_L1_P1E_CSV_ONLINE_VALIDATION_RESULT_2026-06-05.md

docs/review/P66_FULL_RUNTIME_VALIDATION_4300000_2026-06-09.md

These documents must be interpreted together.

In particular:

"Source of Truth Analysis completed"

must NOT be interpreted as:

"historical feature-generation provenance completely reconstructed".

The original documentation explicitly states that the latter remained
unresolved.

======================================================================
18. FINAL CANONICAL CONCLUSION
======================================================================

BTC_L1_CANONICAL_V1 is physically identified and structurally
validated.

The historical market-time structure was independently compared
against a complete Binance raw historical archive set for
2017-08 through 2025-12.

No evidence was found of omission of normally UTC-minute-aligned
Binance raw candles from the canonical L1 dataset.

Thirty-one L1 gaps correspond to Binance source gaps.

Two L1 gaps contain a combination of genuine Binance source downtime
and historical Binance candles emitted on nonstandard shifted time
grids.

The canonical L1 dataset contains exactly the same number of normal
minute-aligned historical rows as the independent Binance raw
reference:

4374557

The original exact generation provenance of the historical
signal/regime feature columns remains unresolved, as already documented
in June 2026.

Accordingly:

1. Keep BTC_L1_CANONICAL_V1 frozen.

2. Use it for existing historical BTC-L1 reproducibility/regression
   work.

3. Do not rebuild or replace it silently.

4. Keep new/future data separate.

5. Treat a future reproducible rebuild as a new version, never as an
   overwrite.

6. Do not repeat the 2026-08-31 forensic investigation unless a formal
   RE-AUDIT TRIGGER occurs.

This document is the authoritative dataset-governance reference until
explicitly superseded by a later versioned document.

END OF BTC-L1 CANONICAL DATASET SOURCE OF TRUTH V1
