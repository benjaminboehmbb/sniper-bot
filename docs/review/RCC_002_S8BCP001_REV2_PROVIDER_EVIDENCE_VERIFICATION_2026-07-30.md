# RCC-002 S8BCP-001 Revision 2 Provider Evidence Verification

## Document Control

| Field | Value |
|---|---|
| Evidence review ID | `RCC-002-S8BCP001-REV2-PEV-001` |
| Date | 2026-07-30 |
| Status | PASS |
| Evidence input | `RCC_002_BINANCE_PROVIDER_EVIDENCE_INPUT_2026-07-30.zip` |
| Evidence input SHA-256 | `e2c8218461d8a41e6c6b6122c3b1f8ac29935834193f3f0757edaae0b2e8ddbf` |
| Scope | Binance Vision BTCUSDT Spot 1m daily/monthly transition evidence |
| Limitation | Provider-profile evidence only; not an implementation certification |

## 1. Method

The uploaded evidence archive was read locally without modifying the source
bytes. For every nested provider archive the verification:

1. reproduced the provider-published SHA-256;
2. tested ZIP integrity and required exactly one safe CSV member;
3. scanned every CSV record, not a sample;
4. verified UTF-8 without BOM, LF, comma delimiter, no header and exactly
   twelve columns;
5. parsed both raw timestamp columns as integers;
6. selected the timestamp unit from the registered archive period before
   interpreting any row value;
7. applied exact integer conversion and remainder rules;
8. reconciled first/last normalized timestamps, row count and one-minute
   continuity with the registered archive period.

## 2. Byte-bound Archive Results

| Archive | Archive SHA-256 | Bytes | CSV SHA-256 | Rows | Unit | Result |
|---|---|---:|---|---:|---|---|
| `BTCUSDT-1m-2024-12-31.zip` | `756551b6eb4f0a0173af3333762e6c95d08c7503bb3b7b79807e10a02575a4af` | 71,638 | `a213238fa1b0d7b4aab40d165433760aff584fca83df782aadca786fcae8575c` | 1,440 | millisecond | PASS |
| `BTCUSDT-1m-2025-01-01.zip` | `10a12909f1b0e3fcc6b7f502e5ea9be5d1ba3455dd8ab16cc61c8650640ba7c0` | 69,062 | `c85bf92e1dc232e8bdedb05fd3a111174c73c5acf2094a1a3233c99a061c9d48` | 1,440 | microsecond | PASS |
| `BTCUSDT-1m-2024-12.zip` | `58fef0b7c7abce7a0201efd04ed3732f236f607f3fcecf228fb8384cad1ae2c1` | 2,218,893 | `7cf556546979e804f56f875768903ac32db2f9d2ece06551578d9e34ef3b5a03` | 44,640 | millisecond | PASS |
| `BTCUSDT-1m-2025-01.zip` | `8d028b2f91aad57d6b693d44449c93f9c4b7044f55f298c8a3ac40ab676dafac` | 2,222,830 | `591e74443aed0082ecd473dd10239ecbc2c671ae19a5227712f4f50aa58632ba` | 44,640 | microsecond | PASS |

All four provider checksum files matched their corresponding archive bytes.

## 3. Transition Evidence

| Boundary case | First raw open/close | Last raw open/close | Canonical result |
|---|---|---|---|
| Daily 2024-12-31 | `1735603200000` / `1735603259999` | `1735689540000` / `1735689599999` | unchanged milliseconds |
| Daily 2025-01-01 | `1735689600000000` / `1735689659999999` | `1735775940000000` / `1735775999999999` | exact integer division by 1000 |
| Monthly 2024-12 | `1733011200000` / `1733011259999` | `1735689540000` / `1735689599999` | unchanged milliseconds |
| Monthly 2025-01 | `1735689600000000` / `1735689659999999` | `1738367940000000` / `1738367999999999` | exact integer division by 1000 |

For every post-transition row:

```text
raw_open_time mod 1000 = 0
raw_close_time mod 1000 = 999
```

For every normalized row:

```text
open_time_ms mod 60000 = 0
close_time_ms = open_time_ms + 59999
```

## 4. Aggregate Assertions

| Assertion | Result |
|---|---|
| Total records scanned | 92,160 |
| Exactly one CSV member per ZIP | PASS |
| Safe member paths | PASS |
| UTF-8 without BOM, LF, comma, no header | PASS |
| Exactly twelve columns on every row | PASS |
| Unique and contiguous one-minute open times | PASS |
| Period-selected millisecond/microsecond branch | PASS |
| No magnitude-based or per-record unit guessing | PASS |
| Exact close-time relation | PASS |
| Daily/monthly boundary reconciliation | PASS |

## 5. Decision

The immutable evidence supports
`BINANCE_SPOT_TIMESTAMP_UNITS_V1/1.0.0` for the registered BTCUSDT Spot 1m
daily and monthly profiles:

```text
period_end_utc <= 2025-01-01T00:00:00Z   -> millisecond
period_start_utc >= 2025-01-01T00:00:00Z -> microsecond
boundary-crossing archive                -> fail closed
```

This closes the provider-byte execution gate for the registered profile
scope. It does not generalize the claim to another provider, market type,
symbol, interval or unregistered archive family.
