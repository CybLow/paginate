window.BENCHMARK_DATA = {
  "lastUpdate": 1773720152759,
  "repoUrl": "https://github.com/CybLow/pypaginate",
  "entries": {
    "Benchmark": [
      {
        "commit": {
          "author": {
            "email": "git.owiwz@passinbox.com",
            "name": "CybLow"
          },
          "committer": {
            "email": "git.owiwz@passinbox.com",
            "name": "CybLow"
          },
          "distinct": true,
          "id": "1f5604d7e663c86216d479330f1895a5544aab3e",
          "message": "feat(ci): add Codecov config, benchmark dashboard, and benchmark docs\n\n- Add codecov.yml with 85% project / 80% patch coverage targets\n- Add benchmark-action/github-action-benchmark to CI for PR perf\n  comments and historical tracking on gh-pages\n- Enable benchmarks on PRs (Tier 2) for regression detection\n- Switch docs deployment to gh-pages branch via JamesIves action\n  with clean-exclude to preserve /dev/bench/ benchmark charts\n- Add docs/benchmarks.md page with dashboard link, categories,\n  local usage, and dataset documentation",
          "timestamp": "2026-03-17T03:36:33+01:00",
          "tree_id": "8adf197240732c324910dcb0fde2ab7c43a1ef53",
          "url": "https://github.com/CybLow/pypaginate/commit/1f5604d7e663c86216d479330f1895a5544aab3e"
        },
        "date": 1773715373837,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_filter_scaling[10K]",
            "value": 963.6892399834705,
            "unit": "iter/sec",
            "range": "stddev: 0.000044545881942568836",
            "extra": "mean: 1.0376789098705224 msec\nrounds: 233"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_pipeline_scaling[1K]",
            "value": 3269.6173487231654,
            "unit": "iter/sec",
            "range": "stddev: 0.000008937315374861286",
            "extra": "mean: 305.8461872887098 usec\nrounds: 2958"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_sort_scaling[100K]",
            "value": 26.392420254836054,
            "unit": "iter/sec",
            "range": "stddev: 0.0002900816490377399",
            "extra": "mean: 37.889666439998564 msec\nrounds: 25"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_search_scaling[10K]",
            "value": 370.1365275296338,
            "unit": "iter/sec",
            "range": "stddev: 0.00008306177966824175",
            "extra": "mean: 2.7017057913040974 msec\nrounds: 230"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_search_scaling[100K]",
            "value": 26.450767974682634,
            "unit": "iter/sec",
            "range": "stddev: 0.0001417928589548014",
            "extra": "mean: 37.80608566666762 msec\nrounds: 24"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_paginate_scaling[1K]",
            "value": 2605.3650581530724,
            "unit": "iter/sec",
            "range": "stddev: 0.000023480543443142075",
            "extra": "mean: 383.8233712664029 usec\nrounds: 703"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_paginate_scaling[100K]",
            "value": 2340.2876793678106,
            "unit": "iter/sec",
            "range": "stddev: 0.00002720564585653735",
            "extra": "mean: 427.2978953895673 usec\nrounds: 564"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_filter_scaling[100K]",
            "value": 80.51170948950534,
            "unit": "iter/sec",
            "range": "stddev: 0.00017418941578253145",
            "extra": "mean: 12.420553560974252 msec\nrounds: 82"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_pipeline_scaling[100K]",
            "value": 32.96196946848909,
            "unit": "iter/sec",
            "range": "stddev: 0.0002608951212199086",
            "extra": "mean: 30.337993030300506 msec\nrounds: 33"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_paginate_scaling[100K]",
            "value": 603427.6202042075,
            "unit": "iter/sec",
            "range": "stddev: 3.510729702208074e-7",
            "extra": "mean: 1.6571995820502674 usec\nrounds: 47850"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_pipeline_scaling[100K]",
            "value": 74.78793710461532,
            "unit": "iter/sec",
            "range": "stddev: 0.00013621594154124888",
            "extra": "mean: 13.37114030303007 msec\nrounds: 66"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_sort_scaling[100K]",
            "value": 42.9511028650811,
            "unit": "iter/sec",
            "range": "stddev: 0.0017447006548897174",
            "extra": "mean: 23.282289238095256 msec\nrounds: 42"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_filter_scaling[10K]",
            "value": 782.9123061421396,
            "unit": "iter/sec",
            "range": "stddev: 0.00002603596320630698",
            "extra": "mean: 1.2772822602924414 msec\nrounds: 753"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_sort_scaling[10K]",
            "value": 248.82287712518652,
            "unit": "iter/sec",
            "range": "stddev: 0.000049836194803530466",
            "extra": "mean: 4.018923065088123 msec\nrounds: 169"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_sort_scaling[1K]",
            "value": 1322.2921424169538,
            "unit": "iter/sec",
            "range": "stddev: 0.00002672675662289734",
            "extra": "mean: 756.2625292260669 usec\nrounds: 633"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_pipeline_scaling[1K]",
            "value": 702.1150952001949,
            "unit": "iter/sec",
            "range": "stddev: 0.00010806554689670867",
            "extra": "mean: 1.4242679111105976 msec\nrounds: 405"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_sort_scaling[10K]",
            "value": 436.0450900716566,
            "unit": "iter/sec",
            "range": "stddev: 0.00001733061594436907",
            "extra": "mean: 2.2933408098590604 msec\nrounds: 426"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_filter_scaling[1K]",
            "value": 1780.0932554548142,
            "unit": "iter/sec",
            "range": "stddev: 0.000031675687721493364",
            "extra": "mean: 561.7683213706125 usec\nrounds: 613"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_search_scaling[1K]",
            "value": 1384.5298658772733,
            "unit": "iter/sec",
            "range": "stddev: 0.000020563043577884512",
            "extra": "mean: 722.2668319735916 usec\nrounds: 613"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_filter_scaling[100K]",
            "value": 165.1201009776238,
            "unit": "iter/sec",
            "range": "stddev: 0.00013200244381061907",
            "extra": "mean: 6.056197846775268 msec\nrounds: 124"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_search_scaling[100K]",
            "value": 63.620354725754375,
            "unit": "iter/sec",
            "range": "stddev: 0.0001600743309449275",
            "extra": "mean: 15.718239929825268 msec\nrounds: 57"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_paginate_scaling[100K]",
            "value": 896.3297253803196,
            "unit": "iter/sec",
            "range": "stddev: 0.00010499698136171708",
            "extra": "mean: 1.1156608686336855 msec\nrounds: 373"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_filter_scaling[1K]",
            "value": 7637.973447679306,
            "unit": "iter/sec",
            "range": "stddev: 0.000005381623242455416",
            "extra": "mean: 130.9247808793884 usec\nrounds: 6914"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_search_scaling[1K]",
            "value": 4013.3718446084886,
            "unit": "iter/sec",
            "range": "stddev: 0.000006776190758554653",
            "extra": "mean: 249.16704425068087 usec\nrounds: 2757"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_sort_scaling[1K]",
            "value": 684.6911389208678,
            "unit": "iter/sec",
            "range": "stddev: 0.00011421350618015631",
            "extra": "mean: 1.4605125481484775 msec\nrounds: 405"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_pipeline_scaling[10K]",
            "value": 520.7407902083091,
            "unit": "iter/sec",
            "range": "stddev: 0.00005381126633628946",
            "extra": "mean: 1.9203412116035221 msec\nrounds: 293"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_paginate_scaling[10K]",
            "value": 949.6852897755936,
            "unit": "iter/sec",
            "range": "stddev: 0.00008259677491489653",
            "extra": "mean: 1.0529804038939 msec\nrounds: 411"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_filter_scaling[100K]",
            "value": 182.31609178298692,
            "unit": "iter/sec",
            "range": "stddev: 0.0001786576562623182",
            "extra": "mean: 5.484979357665874 msec\nrounds: 137"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_paginate_scaling[1K]",
            "value": 594857.6587758706,
            "unit": "iter/sec",
            "range": "stddev: 3.6385754091337754e-7",
            "extra": "mean: 1.6810744305752954 usec\nrounds: 70737"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_pipeline_scaling[10K]",
            "value": 308.9121533351505,
            "unit": "iter/sec",
            "range": "stddev: 0.000024333481861970825",
            "extra": "mean: 3.237166259739422 msec\nrounds: 308"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_search_scaling[100K]",
            "value": 66.57466440097079,
            "unit": "iter/sec",
            "range": "stddev: 0.00031598300066127864",
            "extra": "mean: 15.02072911666706 msec\nrounds: 60"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_filter_scaling[1K]",
            "value": 838.7962124969914,
            "unit": "iter/sec",
            "range": "stddev: 0.000025687070660831383",
            "extra": "mean: 1.1921846869373969 msec\nrounds: 444"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_search_scaling[1K]",
            "value": 724.6368724823884,
            "unit": "iter/sec",
            "range": "stddev: 0.000075588217732646",
            "extra": "mean: 1.3800015400462582 msec\nrounds: 437"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_pipeline_scaling[1K]",
            "value": 1417.9621812701907,
            "unit": "iter/sec",
            "range": "stddev: 0.000025279925154229443",
            "extra": "mean: 705.2374267868089 usec\nrounds: 560"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_pipeline_scaling[100K]",
            "value": 70.83495726756854,
            "unit": "iter/sec",
            "range": "stddev: 0.00011812557811736268",
            "extra": "mean: 14.117323403226578 msec\nrounds: 62"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_sort_scaling[10K]",
            "value": 289.7993684169542,
            "unit": "iter/sec",
            "range": "stddev: 0.00007519650711265905",
            "extra": "mean: 3.4506631448596923 msec\nrounds: 214"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_paginate_scaling[10K]",
            "value": 2578.919541733015,
            "unit": "iter/sec",
            "range": "stddev: 0.000025062235937551172",
            "extra": "mean: 387.75928594034673 usec\nrounds: 633"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_pipeline_scaling[10K]",
            "value": 398.0427567813091,
            "unit": "iter/sec",
            "range": "stddev: 0.0000511114706777793",
            "extra": "mean: 2.512292920706043 msec\nrounds: 227"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_paginate_scaling[1K]",
            "value": 978.4313351523429,
            "unit": "iter/sec",
            "range": "stddev: 0.00006135568433458964",
            "extra": "mean: 1.0220441272399547 msec\nrounds: 558"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_sort_scaling[1K]",
            "value": 4184.371446437988,
            "unit": "iter/sec",
            "range": "stddev: 0.000007663028627962198",
            "extra": "mean: 238.98451961076873 usec\nrounds: 3493"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_sort_scaling[100K]",
            "value": 26.94089067040232,
            "unit": "iter/sec",
            "range": "stddev: 0.00015452288005794311",
            "extra": "mean: 37.11829769231109 msec\nrounds: 26"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_search_scaling[10K]",
            "value": 351.9996272932559,
            "unit": "iter/sec",
            "range": "stddev: 0.00007457892551770637",
            "extra": "mean: 2.840912098940621 msec\nrounds: 283"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_search_scaling[10K]",
            "value": 491.60730967522744,
            "unit": "iter/sec",
            "range": "stddev: 0.00003043711658963703",
            "extra": "mean: 2.0341438793101636 msec\nrounds: 290"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_filter_scaling[10K]",
            "value": 600.3982132174493,
            "unit": "iter/sec",
            "range": "stddev: 0.0000375679567817515",
            "extra": "mean: 1.6655612524913108 msec\nrounds: 301"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_paginate_scaling[10K]",
            "value": 597433.9956920074,
            "unit": "iter/sec",
            "range": "stddev: 3.682321724774933e-7",
            "extra": "mean: 1.6738250705698472 usec\nrounds: 101338"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_pipeline_scaling[10K]",
            "value": 377.3855752924707,
            "unit": "iter/sec",
            "range": "stddev: 0.00008080429986368562",
            "extra": "mean: 2.649809811159338 msec\nrounds: 233"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_sort_scaling[1K]",
            "value": 2613.177975413057,
            "unit": "iter/sec",
            "range": "stddev: 0.000018639655872664622",
            "extra": "mean: 382.67581060640657 usec\nrounds: 1320"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_filter_scaling[10K]",
            "value": 937.7793934315475,
            "unit": "iter/sec",
            "range": "stddev: 0.00002566887815506274",
            "extra": "mean: 1.0663488737375355 msec\nrounds: 396"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_fastapi_filter_scaling[10K]",
            "value": 2586.750689561439,
            "unit": "iter/sec",
            "range": "stddev: 0.000029645168677796386",
            "extra": "mean: 386.58538066130416 usec\nrounds: 817"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_fastapi_filter_scaling[1K]",
            "value": 2587.390395364507,
            "unit": "iter/sec",
            "range": "stddev: 0.000013240747458777849",
            "extra": "mean: 386.4898013811795 usec\nrounds: 1158"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_filter_scaling[10K]",
            "value": 530.8783639945747,
            "unit": "iter/sec",
            "range": "stddev: 0.00006914257143919111",
            "extra": "mean: 1.8836706632297782 msec\nrounds: 291"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_fp_sa_paginate_scaling[10K]",
            "value": 1525.1205318456834,
            "unit": "iter/sec",
            "range": "stddev: 0.000023100874197403952",
            "extra": "mean: 655.6858812921569 usec\nrounds: 278"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_pipeline_scaling[1K]",
            "value": 1407.6627192229569,
            "unit": "iter/sec",
            "range": "stddev: 0.00002713414321137296",
            "extra": "mean: 710.3974455983387 usec\nrounds: 579"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_paginate_scaling[10K]",
            "value": 768.9623453643344,
            "unit": "iter/sec",
            "range": "stddev: 0.0000985331705140181",
            "extra": "mean: 1.3004537946863965 msec\nrounds: 414"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_paginate_scaling[1K]",
            "value": 756.738212321062,
            "unit": "iter/sec",
            "range": "stddev: 0.00010072880585655945",
            "extra": "mean: 1.3214609540237268 msec\nrounds: 522"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_search_scaling[1K]",
            "value": 688.1246559367293,
            "unit": "iter/sec",
            "range": "stddev: 0.00003468807651938714",
            "extra": "mean: 1.4532250681218821 msec\nrounds: 367"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_filter_scaling[1K]",
            "value": 665.3690056093159,
            "unit": "iter/sec",
            "range": "stddev: 0.00010807368845473018",
            "extra": "mean: 1.502925431707243 msec\nrounds: 410"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_pipeline_scaling[10K]",
            "value": 539.0215234738587,
            "unit": "iter/sec",
            "range": "stddev: 0.000039910870999114497",
            "extra": "mean: 1.8552134867551309 msec\nrounds: 302"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_sort_scaling[1K]",
            "value": 1102.855606180778,
            "unit": "iter/sec",
            "range": "stddev: 0.000024273018248889934",
            "extra": "mean: 906.7370147058779 usec\nrounds: 748"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_fp_sa_paginate_scaling[1K]",
            "value": 1564.1381068329688,
            "unit": "iter/sec",
            "range": "stddev: 0.000013791507367168824",
            "extra": "mean: 639.3297341401502 usec\nrounds: 662"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_paginate_scaling[1K]",
            "value": 2334.112713856368,
            "unit": "iter/sec",
            "range": "stddev: 0.00001427314900015948",
            "extra": "mean: 428.4283248463279 usec\nrounds: 982"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_sa_pagination_lib_scaling[1K]",
            "value": 1808.1826582456024,
            "unit": "iter/sec",
            "range": "stddev: 0.000020783222766572574",
            "extra": "mean: 553.0414725745986 usec\nrounds: 474"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_pipeline_scaling[1K]",
            "value": 641.9886331208963,
            "unit": "iter/sec",
            "range": "stddev: 0.00010213270630979124",
            "extra": "mean: 1.5576599777767164 msec\nrounds: 360"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_search_scaling[10K]",
            "value": 485.05073891161317,
            "unit": "iter/sec",
            "range": "stddev: 0.00003905266000707925",
            "extra": "mean: 2.061639988929533 msec\nrounds: 271"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_paginate_scaling[10K]",
            "value": 2289.87421597539,
            "unit": "iter/sec",
            "range": "stddev: 0.000017855680525848128",
            "extra": "mean: 436.70520984229785 usec\nrounds: 691"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_sort_scaling[10K]",
            "value": 1160.04190530305,
            "unit": "iter/sec",
            "range": "stddev: 0.000014053477340747835",
            "extra": "mean: 862.0378241756356 usec\nrounds: 637"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_sort_scaling[10K]",
            "value": 720.766642696149,
            "unit": "iter/sec",
            "range": "stddev: 0.00005921016291242056",
            "extra": "mean: 1.3874115986546374 msec\nrounds: 446"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_search_scaling[1K]",
            "value": 1610.1264161290692,
            "unit": "iter/sec",
            "range": "stddev: 0.00002799122629989859",
            "extra": "mean: 621.0692464782461 usec\nrounds: 568"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_filter_scaling[1K]",
            "value": 1690.566059684789,
            "unit": "iter/sec",
            "range": "stddev: 0.000022604650262924757",
            "extra": "mean: 591.5178494630685 usec\nrounds: 651"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_search_scaling[10K]",
            "value": 812.300426445684,
            "unit": "iter/sec",
            "range": "stddev: 0.00003569074051263007",
            "extra": "mean: 1.2310716176472019 msec\nrounds: 374"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_sa_pagination_lib_scaling[10K]",
            "value": 1861.2483777375473,
            "unit": "iter/sec",
            "range": "stddev: 0.00002640914895299895",
            "extra": "mean: 537.273806097581 usec\nrounds: 459"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_sa_sort_10k",
            "value": 184.20125779327498,
            "unit": "iter/sec",
            "range": "stddev: 0.00012242678102354244",
            "extra": "mean: 5.428844579998895 msec\nrounds: 100"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_sort_10k",
            "value": 235.97308409025194,
            "unit": "iter/sec",
            "range": "stddev: 0.00007291435355467756",
            "extra": "mean: 4.237771455398416 msec\nrounds: 213"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_offset_10k",
            "value": 555.903084464575,
            "unit": "iter/sec",
            "range": "stddev: 0.00009079131150775428",
            "extra": "mean: 1.7988747102620635 msec\nrounds: 497"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_sort_10k",
            "value": 354.76031136883756,
            "unit": "iter/sec",
            "range": "stddev: 0.003285673283380746",
            "extra": "mean: 2.818804606810481 msec\nrounds: 323"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_fp_fastapi_sa_10k",
            "value": 303.98648414663785,
            "unit": "iter/sec",
            "range": "stddev: 0.0001079713015048807",
            "extra": "mean: 3.2896199408576905 msec\nrounds: 186"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_fp_fastapi_pipeline_10k",
            "value": 305.5141865210508,
            "unit": "iter/sec",
            "range": "stddev: 0.00011778833266440178",
            "extra": "mean: 3.273170425855485 msec\nrounds: 263"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_pipeline_10k",
            "value": 180.5318121235604,
            "unit": "iter/sec",
            "range": "stddev: 0.00009135436551668553",
            "extra": "mean: 5.53918995348906 msec\nrounds: 172"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_100k",
            "value": 416.6926842895639,
            "unit": "iter/sec",
            "range": "stddev: 0.00008418282282568956",
            "extra": "mean: 2.399850147849224 msec\nrounds: 372"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_sa_filter_10k",
            "value": 231.8264804590809,
            "unit": "iter/sec",
            "range": "stddev: 0.005427109620853838",
            "extra": "mean: 4.313571072725264 msec\nrounds: 165"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_sa_10k",
            "value": 323.96522983074414,
            "unit": "iter/sec",
            "range": "stddev: 0.00009816643027579037",
            "extra": "mean: 3.0867510088118117 msec\nrounds: 227"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_sa_search_10k",
            "value": 253.48171669351873,
            "unit": "iter/sec",
            "range": "stddev: 0.00008782462640452995",
            "extra": "mean: 3.9450577068999664 msec\nrounds: 174"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_filter_10k",
            "value": 248.65846190342324,
            "unit": "iter/sec",
            "range": "stddev: 0.00006896163234873771",
            "extra": "mean: 4.021580413331726 msec\nrounds: 225"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_fp_fastapi_offset_10k",
            "value": 337.37741681686737,
            "unit": "iter/sec",
            "range": "stddev: 0.00006373452542936043",
            "extra": "mean: 2.9640395300756373 msec\nrounds: 266"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_sa_search_10k",
            "value": 191.48519854888883,
            "unit": "iter/sec",
            "range": "stddev: 0.0000897878449123035",
            "extra": "mean: 5.2223357605610765 msec\nrounds: 142"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_sa_filter_10k",
            "value": 246.9206663206806,
            "unit": "iter/sec",
            "range": "stddev: 0.00013286339055144114",
            "extra": "mean: 4.049883774010559 msec\nrounds: 177"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_1k",
            "value": 303.75243165567025,
            "unit": "iter/sec",
            "range": "stddev: 0.004969235906490426",
            "extra": "mean: 3.2921547147763635 msec\nrounds: 291"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_search_10k",
            "value": 81.8059851407299,
            "unit": "iter/sec",
            "range": "stddev: 0.00022929756771466152",
            "extra": "mean: 12.224044466669662 msec\nrounds: 75"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_10k",
            "value": 319.13721751559905,
            "unit": "iter/sec",
            "range": "stddev: 0.00008807063023586846",
            "extra": "mean: 3.1334483887048403 msec\nrounds: 301"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_sa_pipeline_10k",
            "value": 195.60549706951457,
            "unit": "iter/sec",
            "range": "stddev: 0.00010099313897768734",
            "extra": "mean: 5.112330762589043 msec\nrounds: 139"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_offset_10k",
            "value": 305.27604723591634,
            "unit": "iter/sec",
            "range": "stddev: 0.0000811403608193406",
            "extra": "mean: 3.2757237557757137 msec\nrounds: 303"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_sa_10k",
            "value": 251.989766621351,
            "unit": "iter/sec",
            "range": "stddev: 0.00012473275701126973",
            "extra": "mean: 3.9684151202165143 msec\nrounds: 183"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_sa_pipeline_10k",
            "value": 176.97396952414005,
            "unit": "iter/sec",
            "range": "stddev: 0.00012646567900016767",
            "extra": "mean: 5.650548511110814 msec\nrounds: 135"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_sa_sort_10k",
            "value": 230.24124332106192,
            "unit": "iter/sec",
            "range": "stddev: 0.00009472208824443871",
            "extra": "mean: 4.343270500001346 msec\nrounds: 190"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_search_10k",
            "value": 223.92446156734056,
            "unit": "iter/sec",
            "range": "stddev: 0.00008741946670865924",
            "extra": "mean: 4.465791691540011 msec\nrounds: 201"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_pipeline_10k",
            "value": 206.605244192911,
            "unit": "iter/sec",
            "range": "stddev: 0.007860963070749195",
            "extra": "mean: 4.840148196172031 msec\nrounds: 209"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_filter_10k",
            "value": 260.4126184565857,
            "unit": "iter/sec",
            "range": "stddev: 0.00009315763083970642",
            "extra": "mean: 3.840059694214524 msec\nrounds: 242"
          },
          {
            "name": "tests/perf/test_overhead.py::test_paginate_full_http",
            "value": 265.62517614211134,
            "unit": "iter/sec",
            "range": "stddev: 0.0001150413703959502",
            "extra": "mean: 3.7647033858906243 msec\nrounds: 241"
          },
          {
            "name": "tests/perf/test_overhead.py::test_filter_plus_paginate_plus_serialize",
            "value": 797.8724090518391,
            "unit": "iter/sec",
            "range": "stddev: 0.00000976729146412016",
            "extra": "mean: 1.2533332255320893 msec\nrounds: 705"
          },
          {
            "name": "tests/perf/test_overhead.py::test_sort_plus_paginate_plus_serialize",
            "value": 447.3243794343291,
            "unit": "iter/sec",
            "range": "stddev: 0.000026183144870090218",
            "extra": "mean: 2.235514195011158 msec\nrounds: 441"
          },
          {
            "name": "tests/perf/test_overhead.py::test_sort_full_http",
            "value": 160.45139977062405,
            "unit": "iter/sec",
            "range": "stddev: 0.00009555697055488854",
            "extra": "mean: 6.232416803029244 msec\nrounds: 132"
          },
          {
            "name": "tests/perf/test_overhead.py::test_sort_plus_paginate",
            "value": 452.3433455140391,
            "unit": "iter/sec",
            "range": "stddev: 0.000018432270079984035",
            "extra": "mean: 2.2107100942617133 msec\nrounds: 488"
          },
          {
            "name": "tests/perf/test_overhead.py::test_paginate_only",
            "value": 622954.7695926026,
            "unit": "iter/sec",
            "range": "stddev: 3.560192642394742e-7",
            "extra": "mean: 1.605252979528475 usec\nrounds: 128453"
          },
          {
            "name": "tests/perf/test_overhead.py::test_paginate_plus_serialize",
            "value": 213882.4935669457,
            "unit": "iter/sec",
            "range": "stddev: 6.204460691332117e-7",
            "extra": "mean: 4.6754644726778345 usec\nrounds: 55605"
          },
          {
            "name": "tests/perf/test_overhead.py::test_pipeline_plus_serialize",
            "value": 88.92211452854046,
            "unit": "iter/sec",
            "range": "stddev: 0.00022425665048528997",
            "extra": "mean: 11.245796451219563 msec\nrounds: 82"
          },
          {
            "name": "tests/perf/test_overhead.py::test_sort_only",
            "value": 440.80271535134165,
            "unit": "iter/sec",
            "range": "stddev: 0.000020869330105149747",
            "extra": "mean: 2.268588566209149 msec\nrounds: 438"
          },
          {
            "name": "tests/perf/test_overhead.py::test_pipeline_plus_paginate",
            "value": 88.90050567582,
            "unit": "iter/sec",
            "range": "stddev: 0.00012925713182960512",
            "extra": "mean: 11.248529942524156 msec\nrounds: 87"
          },
          {
            "name": "tests/perf/test_overhead.py::test_filter_full_http",
            "value": 192.94018505487423,
            "unit": "iter/sec",
            "range": "stddev: 0.00012960128277751578",
            "extra": "mean: 5.182953461538297 msec\nrounds: 117"
          },
          {
            "name": "tests/perf/test_overhead.py::test_search_plus_paginate_plus_serialize",
            "value": 105.49965289388201,
            "unit": "iter/sec",
            "range": "stddev: 0.000073133836668518",
            "extra": "mean: 9.478704171717617 msec\nrounds: 99"
          },
          {
            "name": "tests/perf/test_overhead.py::test_filter_plus_paginate",
            "value": 796.063597846139,
            "unit": "iter/sec",
            "range": "stddev: 0.00003347913105747185",
            "extra": "mean: 1.2561810422001953 msec\nrounds: 782"
          },
          {
            "name": "tests/perf/test_overhead.py::test_search_plus_paginate",
            "value": 105.19115708993247,
            "unit": "iter/sec",
            "range": "stddev: 0.00010738678899419344",
            "extra": "mean: 9.506502520407269 msec\nrounds: 98"
          },
          {
            "name": "tests/perf/test_overhead.py::test_filter_only",
            "value": 809.2248011782372,
            "unit": "iter/sec",
            "range": "stddev: 0.00001971967024191134",
            "extra": "mean: 1.2357505584900423 msec\nrounds: 795"
          },
          {
            "name": "tests/perf/test_overhead.py::test_search_full_http",
            "value": 77.02230859585089,
            "unit": "iter/sec",
            "range": "stddev: 0.00016223155474947928",
            "extra": "mean: 12.983251453123401 msec\nrounds: 64"
          },
          {
            "name": "tests/perf/test_overhead.py::test_pipeline_full_http",
            "value": 69.2264734860603,
            "unit": "iter/sec",
            "range": "stddev: 0.00014439930885821705",
            "extra": "mean: 14.445340772722787 msec\nrounds: 66"
          },
          {
            "name": "tests/perf/test_overhead.py::test_pipeline_ops_only",
            "value": 89.45441333791678,
            "unit": "iter/sec",
            "range": "stddev: 0.00008723542674547626",
            "extra": "mean: 11.178878298854519 msec\nrounds: 87"
          },
          {
            "name": "tests/perf/test_overhead.py::test_search_only",
            "value": 103.57928958073086,
            "unit": "iter/sec",
            "range": "stddev: 0.00006720090667172969",
            "extra": "mean: 9.654439647614968 msec\nrounds: 105"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_paginate_lib_scaling[100K]",
            "value": 371310.2420055008,
            "unit": "iter/sec",
            "range": "stddev: 0.000008550719573724573",
            "extra": "mean: 2.6931656789181306 usec\nrounds: 47574"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_paginate_scaling[10K]",
            "value": 4220877.524424396,
            "unit": "iter/sec",
            "range": "stddev: 3.089576347398291e-8",
            "extra": "mean: 236.9175590178646 nsec\nrounds: 152836"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_sort_scaling[100K]",
            "value": 147.62993109380386,
            "unit": "iter/sec",
            "range": "stddev: 0.000047443562350422874",
            "extra": "mean: 6.773694145834162 msec\nrounds: 144"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_fp_paginate_scaling[100K]",
            "value": 16533.907695311325,
            "unit": "iter/sec",
            "range": "stddev: 0.000004212500672613572",
            "extra": "mean: 60.481769853086774 usec\nrounds: 617"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_search_scaling[10K]",
            "value": 1897.5505001089628,
            "unit": "iter/sec",
            "range": "stddev: 0.000013821228778360827",
            "extra": "mean: 526.9951971990084 usec\nrounds: 1785"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_paginate_lib_scaling[10K]",
            "value": 375610.04055176553,
            "unit": "iter/sec",
            "range": "stddev: 0.000008472152743647154",
            "extra": "mean: 2.6623356461158894 usec\nrounds: 94251"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_pipeline_scaling[1K]",
            "value": 14495.477576782672,
            "unit": "iter/sec",
            "range": "stddev: 0.000003230250322495764",
            "extra": "mean: 68.9870336939912 usec\nrounds: 12020"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_filter_scaling[100K]",
            "value": 296.54780216094076,
            "unit": "iter/sec",
            "range": "stddev: 0.000022733614912207105",
            "extra": "mean: 3.3721376206905274 msec\nrounds: 290"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_pipeline_scaling[10K]",
            "value": 1368.6821946396242,
            "unit": "iter/sec",
            "range": "stddev: 0.000009695738048866469",
            "extra": "mean: 730.6298013640057 usec\nrounds: 1319"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_search_scaling[100K]",
            "value": 186.25199560156483,
            "unit": "iter/sec",
            "range": "stddev: 0.00009516947658476248",
            "extra": "mean: 5.369069989130352 msec\nrounds: 184"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_fp_paginate_scaling[1K]",
            "value": 17427.09189882443,
            "unit": "iter/sec",
            "range": "stddev: 0.000004852373643722233",
            "extra": "mean: 57.38192039186162 usec\nrounds: 5816"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_pipeline_scaling[100K]",
            "value": 129.56327691648892,
            "unit": "iter/sec",
            "range": "stddev: 0.00012770170699624646",
            "extra": "mean: 7.718236399999038 msec\nrounds: 120"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_fp_paginate_scaling[10K]",
            "value": 17567.967063581487,
            "unit": "iter/sec",
            "range": "stddev: 0.0000053787278761415915",
            "extra": "mean: 56.921782490872644 usec\nrounds: 5894"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_paginate_scaling[100K]",
            "value": 4338266.411642939,
            "unit": "iter/sec",
            "range": "stddev: 3.302224899670132e-8",
            "extra": "mean: 230.50682118464516 nsec\nrounds: 194932"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_filter_scaling[1K]",
            "value": 30034.59943679141,
            "unit": "iter/sec",
            "range": "stddev: 0.00000550468297789082",
            "extra": "mean: 33.29493380141545 usec\nrounds: 24351"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_search_scaling[1K]",
            "value": 17788.66369049741,
            "unit": "iter/sec",
            "range": "stddev: 0.000002622034251433686",
            "extra": "mean: 56.215577369883796 usec\nrounds: 15581"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_sort_scaling[10K]",
            "value": 1564.906474740003,
            "unit": "iter/sec",
            "range": "stddev: 0.00001546199355774975",
            "extra": "mean: 639.0158237195244 usec\nrounds: 1543"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_filter_scaling[10K]",
            "value": 3046.776879092269,
            "unit": "iter/sec",
            "range": "stddev: 0.0000055122611443959415",
            "extra": "mean: 328.21569799293326 usec\nrounds: 3288"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_sort_scaling[1K]",
            "value": 13173.366873425255,
            "unit": "iter/sec",
            "range": "stddev: 0.0000045562292643508215",
            "extra": "mean: 75.91073790082538 usec\nrounds: 9050"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_paginate_lib_scaling[1K]",
            "value": 380301.7213536172,
            "unit": "iter/sec",
            "range": "stddev: 0.00000845128782748062",
            "extra": "mean: 2.629491122050869 usec\nrounds: 91067"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_paginate_scaling[1K]",
            "value": 4312888.104084971,
            "unit": "iter/sec",
            "range": "stddev: 2.808948550648884e-8",
            "extra": "mean: 231.86319140829437 nsec\nrounds: 189394"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_valid_search_request",
            "value": 202.98847450983482,
            "unit": "iter/sec",
            "range": "stddev: 0.00021250422428944877",
            "extra": "mean: 4.9263880740753585 msec\nrounds: 135"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_search_invalid_page",
            "value": 446.3400260263971,
            "unit": "iter/sec",
            "range": "stddev: 0.00007952679656955138",
            "extra": "mean: 2.2404443735477555 msec\nrounds: 431"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_valid_cursor_params",
            "value": 855392.3701362226,
            "unit": "iter/sec",
            "range": "stddev: 3.278296751498756e-7",
            "extra": "mean: 1.169054149782454 usec\nrounds: 76953"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_search_spec_many_fields",
            "value": 699313.4807829472,
            "unit": "iter/sec",
            "range": "stddev: 3.227192456098152e-7",
            "extra": "mean: 1.4299738636246595 usec\nrounds: 103649"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_valid_filter_request",
            "value": 239.27731496419872,
            "unit": "iter/sec",
            "range": "stddev: 0.00012712674394986463",
            "extra": "mean: 4.179251176191201 msec\nrounds: 210"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_invalid_params_caught",
            "value": 403794.7603375527,
            "unit": "iter/sec",
            "range": "stddev: 4.77186519939392e-7",
            "extra": "mean: 2.4765056365863907 usec\nrounds: 60053"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_invalid_page",
            "value": 439.28002098697914,
            "unit": "iter/sec",
            "range": "stddev: 0.0000852349240419908",
            "extra": "mean: 2.2764522678568198 msec\nrounds: 392"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_valid_sort_request",
            "value": 227.44587203512796,
            "unit": "iter/sec",
            "range": "stddev: 0.00008222848406667569",
            "extra": "mean: 4.39665046919627 msec\nrounds: 211"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_invalid_limit",
            "value": 434.0591881129379,
            "unit": "iter/sec",
            "range": "stddev: 0.0000853927008888392",
            "extra": "mean: 2.30383327294021 msec\nrounds: 425"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_sort_invalid_limit",
            "value": 427.63104105010393,
            "unit": "iter/sec",
            "range": "stddev: 0.00008007295902105274",
            "extra": "mean: 2.3384644799039127 msec\nrounds: 423"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_filter_spec_empty_field",
            "value": 925705.9327312541,
            "unit": "iter/sec",
            "range": "stddev: 2.850244136385904e-7",
            "extra": "mean: 1.0802566610430426 usec\nrounds: 92328"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_valid_request",
            "value": 242.40481883633717,
            "unit": "iter/sec",
            "range": "stddev: 0.00008848115376771549",
            "extra": "mean: 4.125330530970852 msec\nrounds: 226"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_invalid_filter_param",
            "value": 249.25964899056999,
            "unit": "iter/sec",
            "range": "stddev: 0.00009298994638548497",
            "extra": "mean: 4.011880799999972 msec\nrounds: 250"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_valid_offset_params",
            "value": 905052.7442929295,
            "unit": "iter/sec",
            "range": "stddev: 3.190019426743932e-7",
            "extra": "mean: 1.1049079805633293 usec\nrounds: 152859"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_valid_filter_spec",
            "value": 935309.7115582025,
            "unit": "iter/sec",
            "range": "stddev: 3.123433059522143e-7",
            "extra": "mean: 1.0691645640394614 usec\nrounds: 116605"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_filter_invalid_page",
            "value": 414.0981326919644,
            "unit": "iter/sec",
            "range": "stddev: 0.0001502647659140656",
            "extra": "mean: 2.414886523392925 msec\nrounds: 342"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_valid_search_spec",
            "value": 735643.8210116349,
            "unit": "iter/sec",
            "range": "stddev: 4.096191873727263e-7",
            "extra": "mean: 1.359353496131906 usec\nrounds: 71964"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_sort_spec_desc",
            "value": 1058308.856836358,
            "unit": "iter/sec",
            "range": "stddev: 2.8465761734341923e-7",
            "extra": "mean: 944.9037429293912 nsec\nrounds: 126183"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_valid_sort_spec",
            "value": 1168679.0640023844,
            "unit": "iter/sec",
            "range": "stddev: 2.7805596305682374e-7",
            "extra": "mean: 855.6669070251778 nsec\nrounds: 185840"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_invalid_filter_operator",
            "value": 551061.0792453148,
            "unit": "iter/sec",
            "range": "stddev: 4.2898161525679366e-7",
            "extra": "mean: 1.814680872344519 usec\nrounds: 70887"
          },
          {
            "name": "tests/perf/test_comparison.py::test_raw_list_search_10k",
            "value": 1824.905655547372,
            "unit": "iter/sec",
            "range": "stddev: 0.000009957001747104458",
            "extra": "mean: 547.9735332948238 usec\nrounds: 1682"
          },
          {
            "name": "tests/perf/test_comparison.py::test_sa_async_paginate_10k",
            "value": 979.7283043537478,
            "unit": "iter/sec",
            "range": "stddev: 0.000054470396502000976",
            "extra": "mean: 1.0206911401417804 msec\nrounds: 421"
          },
          {
            "name": "tests/perf/test_comparison.py::test_raw_list_filter_10k",
            "value": 3034.4202767106162,
            "unit": "iter/sec",
            "range": "stddev: 0.000005477161979677128",
            "extra": "mean: 329.55224023351957 usec\nrounds: 2918"
          },
          {
            "name": "tests/perf/test_comparison.py::test_memory_sort_10k",
            "value": 452.28638868725847,
            "unit": "iter/sec",
            "range": "stddev: 0.000051939863470302365",
            "extra": "mean: 2.2109884909480835 msec\nrounds: 442"
          },
          {
            "name": "tests/perf/test_comparison.py::test_memory_search_10k",
            "value": 368.86763677837195,
            "unit": "iter/sec",
            "range": "stddev: 0.0000158574923662026",
            "extra": "mean: 2.7109995572770553 msec\nrounds: 323"
          },
          {
            "name": "tests/perf/test_comparison.py::test_memory_filter_10k",
            "value": 785.2489172527944,
            "unit": "iter/sec",
            "range": "stddev: 0.000011354480265886837",
            "extra": "mean: 1.2734815394569605 msec\nrounds: 773"
          },
          {
            "name": "tests/perf/test_comparison.py::test_memory_paginate_10k",
            "value": 599968.9721520628,
            "unit": "iter/sec",
            "range": "stddev: 3.5765507199383985e-7",
            "extra": "mean: 1.6667528595904604 usec\nrounds: 97657"
          },
          {
            "name": "tests/perf/test_comparison.py::test_sa_sync_paginate_10k",
            "value": 2607.338873882197,
            "unit": "iter/sec",
            "range": "stddev: 0.000021724053261063817",
            "extra": "mean: 383.53280811214614 usec\nrounds: 641"
          },
          {
            "name": "tests/perf/test_comparison.py::test_raw_list_sort_10k",
            "value": 1571.7236472482523,
            "unit": "iter/sec",
            "range": "stddev: 0.000007840532728114974",
            "extra": "mean: 636.2441652836256 usec\nrounds: 1446"
          },
          {
            "name": "tests/perf/test_comparison.py::test_raw_list_slice_10k",
            "value": 4935949.99419966,
            "unit": "iter/sec",
            "range": "stddev: 2.4933306173996033e-8",
            "extra": "mean: 202.5952453275759 nsec\nrounds: 198020"
          },
          {
            "name": "tests/perf/test_comparison.py::test_memory_pipeline_10k",
            "value": 307.9028935731529,
            "unit": "iter/sec",
            "range": "stddev: 0.00008128566983897562",
            "extra": "mean: 3.2477772079216125 msec\nrounds: 303"
          },
          {
            "name": "tests/perf/test_comparison.py::test_raw_pipeline_10k",
            "value": 1354.9125613992342,
            "unit": "iter/sec",
            "range": "stddev: 0.000009022257316921183",
            "extra": "mean: 738.0550070089307 usec\nrounds: 1284"
          },
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_memory_1k",
            "value": 601880.738395096,
            "unit": "iter/sec",
            "range": "stddev: 3.5753978368979866e-7",
            "extra": "mean: 1.661458717995332 usec\nrounds: 113948"
          },
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_sa_async_1k",
            "value": 977.8575939649429,
            "unit": "iter/sec",
            "range": "stddev: 0.00007806060054569701",
            "extra": "mean: 1.0226437941186055 msec\nrounds: 510"
          },
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_sa_async_10k",
            "value": 960.3001743832887,
            "unit": "iter/sec",
            "range": "stddev: 0.00008036591996512083",
            "extra": "mean: 1.0413410584270764 msec\nrounds: 890"
          },
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_sa_sync_1k",
            "value": 2715.9906418275264,
            "unit": "iter/sec",
            "range": "stddev: 0.00001972541553226532",
            "extra": "mean: 368.18978114266383 usec\nrounds: 859"
          },
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_sa_sync_10k",
            "value": 2687.095407296492,
            "unit": "iter/sec",
            "range": "stddev: 0.000024312057924137",
            "extra": "mean: 372.1490488520123 usec\nrounds: 2047"
          },
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_memory_100k",
            "value": 592006.9983138,
            "unit": "iter/sec",
            "range": "stddev: 4.979136363531836e-7",
            "extra": "mean: 1.6891692207157638 usec\nrounds: 132732"
          },
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_memory_10k",
            "value": 608778.9600382034,
            "unit": "iter/sec",
            "range": "stddev: 4.925307222375221e-7",
            "extra": "mean: 1.6426323274004835 usec\nrounds: 141985"
          },
          {
            "name": "tests/perf/test_pipeline.py::test_bench_pipeline_sa_async_10k",
            "value": 239.58385395022103,
            "unit": "iter/sec",
            "range": "stddev: 0.0004869899328774643",
            "extra": "mean: 4.173903973544781 msec\nrounds: 189"
          },
          {
            "name": "tests/perf/test_pipeline.py::test_bench_pipeline_sa_async_1k",
            "value": 679.0658089752734,
            "unit": "iter/sec",
            "range": "stddev: 0.00012527413752239078",
            "extra": "mean: 1.472611323943734 msec\nrounds: 426"
          },
          {
            "name": "tests/perf/test_pipeline.py::test_bench_pipeline_memory_10k",
            "value": 312.6303043377821,
            "unit": "iter/sec",
            "range": "stddev: 0.00003527625105787335",
            "extra": "mean: 3.1986662397243095 msec\nrounds: 292"
          },
          {
            "name": "tests/perf/test_pipeline.py::test_bench_pipeline_memory_100k",
            "value": 32.07658916017802,
            "unit": "iter/sec",
            "range": "stddev: 0.00013808076196689746",
            "extra": "mean: 31.17538448387978 msec\nrounds: 31"
          },
          {
            "name": "tests/perf/test_pipeline.py::test_bench_pipeline_sa_sync_10k",
            "value": 293.56307270377573,
            "unit": "iter/sec",
            "range": "stddev: 0.000034638085107561185",
            "extra": "mean: 3.4064229904319916 msec\nrounds: 209"
          },
          {
            "name": "tests/perf/test_pipeline.py::test_bench_pipeline_sa_sync_1k",
            "value": 1330.403812833306,
            "unit": "iter/sec",
            "range": "stddev: 0.000019308671127962122",
            "extra": "mean: 751.6514838230518 usec\nrounds: 680"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_create[100]",
            "value": 3047113.2469514073,
            "unit": "iter/sec",
            "range": "stddev: 4.1044160502284746e-8",
            "extra": "mean: 328.179466582254 nsec\nrounds: 197629"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_model_dump[20]",
            "value": 501458.9478839865,
            "unit": "iter/sec",
            "range": "stddev: 3.755736833315781e-7",
            "extra": "mean: 1.9941811871534336 usec\nrounds: 72908"
          },
          {
            "name": "tests/perf/test_serialization.py::test_searched_page_model_dump_json[1000]",
            "value": 123035.60602799602,
            "unit": "iter/sec",
            "range": "stddev: 8.222617147076523e-7",
            "extra": "mean: 8.127728486763871 usec\nrounds: 46727"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_sorted_json_dumps[100]",
            "value": 12629.175122128192,
            "unit": "iter/sec",
            "range": "stddev: 0.000003200840259033093",
            "extra": "mean: 79.18173517507499 usec\nrounds: 9848"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_filtered_json_dumps[1000]",
            "value": 1296.0304168420605,
            "unit": "iter/sec",
            "range": "stddev: 0.00002747955966064484",
            "extra": "mean: 771.5868292941956 usec\nrounds: 908"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_create[20]",
            "value": 2963549.222461455,
            "unit": "iter/sec",
            "range": "stddev: 3.4543311907456066e-8",
            "extra": "mean: 337.4332345893726 nsec\nrounds: 139412"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_searched_json_dumps[20]",
            "value": 54767.99571669748,
            "unit": "iter/sec",
            "range": "stddev: 0.0000014821578098593763",
            "extra": "mean: 18.258838705231703 usec\nrounds: 34347"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_searched_json_dumps[1000]",
            "value": 54595.72302917669,
            "unit": "iter/sec",
            "range": "stddev: 0.0000014292712437130063",
            "extra": "mean: 18.316453094056225 usec\nrounds: 23675"
          },
          {
            "name": "tests/perf/test_serialization.py::test_filtered_page_model_dump_json[100]",
            "value": 30605.348309959165,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018257466313607846",
            "extra": "mean: 32.67402775071813 usec\nrounds: 21549"
          },
          {
            "name": "tests/perf/test_serialization.py::test_searched_page_model_dump_json[100]",
            "value": 125089.33010683923,
            "unit": "iter/sec",
            "range": "stddev: 8.43275926174904e-7",
            "extra": "mean: 7.99428695593698 usec\nrounds: 73175"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_model_dump_json[100]",
            "value": 272446.5263614599,
            "unit": "iter/sec",
            "range": "stddev: 5.232036456774471e-7",
            "extra": "mean: 3.6704450350498545 usec\nrounds: 121714"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_json_dumps[20]",
            "value": 291368.1068153416,
            "unit": "iter/sec",
            "range": "stddev: 6.26610919088503e-7",
            "extra": "mean: 3.4320846263169194 usec\nrounds: 85978"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_model_dump[100]",
            "value": 247483.89945861264,
            "unit": "iter/sec",
            "range": "stddev: 5.544579664852285e-7",
            "extra": "mean: 4.040666896665059 usec\nrounds: 81215"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_sorted_json_dumps[20]",
            "value": 54743.28018585434,
            "unit": "iter/sec",
            "range": "stddev: 0.0000013474266934342939",
            "extra": "mean: 18.267082217305642 usec\nrounds: 35394"
          },
          {
            "name": "tests/perf/test_serialization.py::test_fp_filtered_page_serialize[1000]",
            "value": 10668.040836832388,
            "unit": "iter/sec",
            "range": "stddev: 0.000006842126586404148",
            "extra": "mean: 93.73792388827462 usec\nrounds: 6635"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_model_dump[1000]",
            "value": 37527.51634749635,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015010668706113206",
            "extra": "mean: 26.647113833492877 usec\nrounds: 31221"
          },
          {
            "name": "tests/perf/test_serialization.py::test_pipeline_page_model_dump",
            "value": 4640042.599102354,
            "unit": "iter/sec",
            "range": "stddev: 2.61948947826051e-8",
            "extra": "mean: 215.5152627679458 nsec\nrounds: 196079"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_model_dump_json[20]",
            "value": 548538.5245808248,
            "unit": "iter/sec",
            "range": "stddev: 3.646287844354053e-7",
            "extra": "mean: 1.823026014014544 usec\nrounds: 128123"
          },
          {
            "name": "tests/perf/test_serialization.py::test_searched_page_model_dump_json[20]",
            "value": 123171.53739910584,
            "unit": "iter/sec",
            "range": "stddev: 8.361819692643361e-7",
            "extra": "mean: 8.118758774275554 usec\nrounds: 62854"
          },
          {
            "name": "tests/perf/test_serialization.py::test_cursor_page_model_dump[20]",
            "value": 515375.99122573464,
            "unit": "iter/sec",
            "range": "stddev: 3.913197439268151e-7",
            "extra": "mean: 1.9403309758797052 usec\nrounds: 100817"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_create[1000]",
            "value": 3050532.2640320864,
            "unit": "iter/sec",
            "range": "stddev: 3.4824788212760946e-8",
            "extra": "mean: 327.8116451318003 nsec\nrounds: 145709"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_dict_dump[1000]",
            "value": 5324264.883827609,
            "unit": "iter/sec",
            "range": "stddev: 2.2465604217327025e-8",
            "extra": "mean: 187.8193556893933 nsec\nrounds: 196079"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_pipeline_json_dumps",
            "value": 52653.497706886104,
            "unit": "iter/sec",
            "range": "stddev: 0.0000014158669371798894",
            "extra": "mean: 18.992090621725563 usec\nrounds: 18969"
          },
          {
            "name": "tests/perf/test_serialization.py::test_fp_filtered_page_serialize[20]",
            "value": 47781.15140731405,
            "unit": "iter/sec",
            "range": "stddev: 0.000002071920468146646",
            "extra": "mean: 20.928754760960533 usec\nrounds: 24470"
          },
          {
            "name": "tests/perf/test_serialization.py::test_sorted_page_model_dump_json[20]",
            "value": 126980.30873180465,
            "unit": "iter/sec",
            "range": "stddev: 8.342362659760901e-7",
            "extra": "mean: 7.875236798424407 usec\nrounds: 43953"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_filtered_json_dumps[100]",
            "value": 12776.1386181779,
            "unit": "iter/sec",
            "range": "stddev: 0.00000366391035480398",
            "extra": "mean: 78.27091031849007 usec\nrounds: 9556"
          },
          {
            "name": "tests/perf/test_serialization.py::test_filtered_page_model_dump_json[20]",
            "value": 125314.36368042095,
            "unit": "iter/sec",
            "range": "stddev: 8.18075491432425e-7",
            "extra": "mean: 7.979931195678565 usec\nrounds: 65708"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_dict_construction[1000]",
            "value": 7135308.985187626,
            "unit": "iter/sec",
            "range": "stddev: 9.993100694154857e-9",
            "extra": "mean: 140.14810039425916 nsec\nrounds: 71757"
          },
          {
            "name": "tests/perf/test_serialization.py::test_cursor_page_model_dump[100]",
            "value": 245161.40061118384,
            "unit": "iter/sec",
            "range": "stddev: 5.530585874919527e-7",
            "extra": "mean: 4.078945533460873 usec\nrounds: 83244"
          },
          {
            "name": "tests/perf/test_serialization.py::test_filtered_page_model_dump_json[1000]",
            "value": 3170.584356788437,
            "unit": "iter/sec",
            "range": "stddev: 0.00000961297679851894",
            "extra": "mean: 315.3992726479369 usec\nrounds: 2296"
          },
          {
            "name": "tests/perf/test_serialization.py::test_sorted_page_model_dump_json[100]",
            "value": 30623.7166927449,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018590729517839323",
            "extra": "mean: 32.65442957277982 usec\nrounds: 25679"
          },
          {
            "name": "tests/perf/test_serialization.py::test_pipeline_page_model_dump_json",
            "value": 346572.46061030205,
            "unit": "iter/sec",
            "range": "stddev: 4.544395743026289e-7",
            "extra": "mean: 2.885399486846228 usec\nrounds: 52615"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_dict_construction[20]",
            "value": 7055925.634477603,
            "unit": "iter/sec",
            "range": "stddev: 1.1547458134588592e-8",
            "extra": "mean: 141.7248496942504 nsec\nrounds: 71654"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_dict_construction[100]",
            "value": 7342923.117111104,
            "unit": "iter/sec",
            "range": "stddev: 1.0381062682246989e-8",
            "extra": "mean: 136.18554682529094 nsec\nrounds: 73552"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_dict_dump[20]",
            "value": 5366914.758366804,
            "unit": "iter/sec",
            "range": "stddev: 1.2478605551334831e-8",
            "extra": "mean: 186.32679016211745 nsec\nrounds: 53093"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_filtered_json_dumps[20]",
            "value": 54561.52415020485,
            "unit": "iter/sec",
            "range": "stddev: 0.0000013999010584076174",
            "extra": "mean: 18.3279337513933 usec\nrounds: 28212"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_model_dump_json[1000]",
            "value": 39799.39461937103,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015533351955096878",
            "extra": "mean: 25.12601032160633 usec\nrounds: 30422"
          },
          {
            "name": "tests/perf/test_serialization.py::test_sorted_page_model_dump_json[1000]",
            "value": 2971.147068905596,
            "unit": "iter/sec",
            "range": "stddev: 0.000008435890724785652",
            "extra": "mean: 336.5703470102353 usec\nrounds: 2291"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_json_dumps[1000]",
            "value": 18280.709239785858,
            "unit": "iter/sec",
            "range": "stddev: 0.000002644883787727926",
            "extra": "mean: 54.70247280251114 usec\nrounds: 14983"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_sorted_json_dumps[1000]",
            "value": 1294.73057556905,
            "unit": "iter/sec",
            "range": "stddev: 0.000029385258105094488",
            "extra": "mean: 772.3614618126152 usec\nrounds: 838"
          },
          {
            "name": "tests/perf/test_serialization.py::test_cursor_page_model_dump[1000]",
            "value": 38322.51775054507,
            "unit": "iter/sec",
            "range": "stddev: 0.0000022707660938485547",
            "extra": "mean: 26.09431891999781 usec\nrounds: 27035"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_json_dumps[100]",
            "value": 123396.26145534353,
            "unit": "iter/sec",
            "range": "stddev: 9.023730123920234e-7",
            "extra": "mean: 8.103973233920826 usec\nrounds: 62579"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_dict_dump[100]",
            "value": 5300427.936343328,
            "unit": "iter/sec",
            "range": "stddev: 2.9101987597145215e-8",
            "extra": "mean: 188.66401204008872 nsec\nrounds: 184809"
          },
          {
            "name": "tests/perf/test_serialization.py::test_fp_filtered_page_serialize[100]",
            "value": 10593.568409584932,
            "unit": "iter/sec",
            "range": "stddev: 0.000004108538894256095",
            "extra": "mean: 94.39689831947581 usec\nrounds: 8094"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_searched_json_dumps[100]",
            "value": 54295.56015187465,
            "unit": "iter/sec",
            "range": "stddev: 0.000001343120073384103",
            "extra": "mean: 18.417712188672823 usec\nrounds: 32219"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_memory_100k",
            "value": 79.55841101723713,
            "unit": "iter/sec",
            "range": "stddev: 0.00007736476010545946",
            "extra": "mean: 12.569381253521263 msec\nrounds: 71"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_memory_10k_multi",
            "value": 263.01453069213557,
            "unit": "iter/sec",
            "range": "stddev: 0.00007601546545596485",
            "extra": "mean: 3.8020713052181994 msec\nrounds: 249"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_sa_sync_10k",
            "value": 26482.63863419492,
            "unit": "iter/sec",
            "range": "stddev: 0.000003231560182794375",
            "extra": "mean: 37.760587750073356 usec\nrounds: 4604"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_memory_10k_single",
            "value": 807.2632279777217,
            "unit": "iter/sec",
            "range": "stddev: 0.000038847514482519286",
            "extra": "mean: 1.2387533153282653 msec\nrounds: 796"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_sa_sync_1k",
            "value": 27148.29934153914,
            "unit": "iter/sec",
            "range": "stddev: 0.0000034989739585958657",
            "extra": "mean: 36.83471982607461 usec\nrounds: 9644"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_sa_async_10k",
            "value": 26896.05204028928,
            "unit": "iter/sec",
            "range": "stddev: 0.000004267765500525036",
            "extra": "mean: 37.180177912432555 usec\nrounds: 652"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_sa_async_1k",
            "value": 26763.05006825911,
            "unit": "iter/sec",
            "range": "stddev: 0.000003240283470576539",
            "extra": "mean: 37.36494896693396 usec\nrounds: 13070"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_fp_http_paginate_scaling[1K]",
            "value": 218.14694846997662,
            "unit": "iter/sec",
            "range": "stddev: 0.0011015458305395928",
            "extra": "mean: 4.584065956520263 msec\nrounds: 138"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_sort_scaling[10K]",
            "value": 150.24747613443688,
            "unit": "iter/sec",
            "range": "stddev: 0.00009540270429762046",
            "extra": "mean: 6.6556858439687225 msec\nrounds: 141"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_sort_scaling[1K]",
            "value": 230.03507740873437,
            "unit": "iter/sec",
            "range": "stddev: 0.00007650699284960784",
            "extra": "mean: 4.347163099057128 msec\nrounds: 212"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_pipeline_scaling[1K]",
            "value": 207.9401747799552,
            "unit": "iter/sec",
            "range": "stddev: 0.00009777835336188803",
            "extra": "mean: 4.809075499999998 msec\nrounds: 196"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_search_scaling[10K]",
            "value": 181.26903248820295,
            "unit": "iter/sec",
            "range": "stddev: 0.00008457310434237261",
            "extra": "mean: 5.516662092103792 msec\nrounds: 152"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_paginate_scaling[1K]",
            "value": 225.6132488899596,
            "unit": "iter/sec",
            "range": "stddev: 0.00008632394782986195",
            "extra": "mean: 4.432363812498171 msec\nrounds: 208"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_search_scaling[10K]",
            "value": 72.32810076103814,
            "unit": "iter/sec",
            "range": "stddev: 0.00021710251286434577",
            "extra": "mean: 13.82588495312298 msec\nrounds: 64"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_filter_scaling[1K]",
            "value": 217.70607941783274,
            "unit": "iter/sec",
            "range": "stddev: 0.00009673731342021672",
            "extra": "mean: 4.5933489899505675 msec\nrounds: 199"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_search_scaling[1K]",
            "value": 211.85013475119953,
            "unit": "iter/sec",
            "range": "stddev: 0.00007989900724695988",
            "extra": "mean: 4.720317979379232 msec\nrounds: 194"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_sort_scaling[10K]",
            "value": 187.95293527151497,
            "unit": "iter/sec",
            "range": "stddev: 0.0000776344164504712",
            "extra": "mean: 5.320480888236248 msec\nrounds: 170"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_paginate_scaling[10K]",
            "value": 206.14843367319818,
            "unit": "iter/sec",
            "range": "stddev: 0.00011576104688630276",
            "extra": "mean: 4.850873626259389 msec\nrounds: 198"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_sort_scaling[1K]",
            "value": 192.83717016491767,
            "unit": "iter/sec",
            "range": "stddev: 0.00008596302165042898",
            "extra": "mean: 5.185722229509916 msec\nrounds: 183"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_paginate_scaling[1K]",
            "value": 165.99977604139295,
            "unit": "iter/sec",
            "range": "stddev: 0.014342504522608447",
            "extra": "mean: 6.0241045129521416 msec\nrounds: 193"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_filter_scaling[1K]",
            "value": 190.6421535740759,
            "unit": "iter/sec",
            "range": "stddev: 0.00010165875908899877",
            "extra": "mean: 5.245429624311498 msec\nrounds: 181"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_search_scaling[1K]",
            "value": 165.4420288677089,
            "unit": "iter/sec",
            "range": "stddev: 0.00015035320730473343",
            "extra": "mean: 6.04441330201301 msec\nrounds: 149"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_filter_scaling[10K]",
            "value": 152.7628745940178,
            "unit": "iter/sec",
            "range": "stddev: 0.00012985114325430157",
            "extra": "mean: 6.5460931044771 msec\nrounds: 134"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_paginate_scaling[10K]",
            "value": 198.02434820740666,
            "unit": "iter/sec",
            "range": "stddev: 0.00007228802957695042",
            "extra": "mean: 5.049884062502356 msec\nrounds: 176"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_fp_http_paginate_scaling[10K]",
            "value": 183.79279782132627,
            "unit": "iter/sec",
            "range": "stddev: 0.00008707314037780286",
            "extra": "mean: 5.440909610463341 msec\nrounds: 172"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_pipeline_scaling[10K]",
            "value": 117.46226917061219,
            "unit": "iter/sec",
            "range": "stddev: 0.0001652788224705557",
            "extra": "mean: 8.513372056072873 msec\nrounds: 107"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_filter_scaling[10K]",
            "value": 178.0321099662063,
            "unit": "iter/sec",
            "range": "stddev: 0.00008164931064322137",
            "extra": "mean: 5.616964266669749 msec\nrounds: 165"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_pipeline_scaling[10K]",
            "value": 162.19985218170785,
            "unit": "iter/sec",
            "range": "stddev: 0.00008530925160830872",
            "extra": "mean: 6.1652337320241735 msec\nrounds: 153"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_pipeline_scaling[1K]",
            "value": 183.90326716877377,
            "unit": "iter/sec",
            "range": "stddev: 0.0001418318336662951",
            "extra": "mean: 5.437641295857287 msec\nrounds: 169"
          },
          {
            "name": "tests/perf/test_search.py::test_bench_search_sa_async_10k",
            "value": 27063.600343566544,
            "unit": "iter/sec",
            "range": "stddev: 0.000003557790167680293",
            "extra": "mean: 36.949998791927776 usec\nrounds: 5794"
          },
          {
            "name": "tests/perf/test_search.py::test_bench_search_memory_10k",
            "value": 378.4563743221534,
            "unit": "iter/sec",
            "range": "stddev: 0.00003972449256256186",
            "extra": "mean: 2.642312477339251 msec\nrounds: 331"
          },
          {
            "name": "tests/perf/test_search.py::test_bench_search_sa_async_1k",
            "value": 27318.050329850394,
            "unit": "iter/sec",
            "range": "stddev: 0.000003035676867215568",
            "extra": "mean: 36.605833429748884 usec\nrounds: 10362"
          },
          {
            "name": "tests/perf/test_search.py::test_bench_search_sa_sync_1k",
            "value": 27479.342385697084,
            "unit": "iter/sec",
            "range": "stddev: 0.000003204813008675665",
            "extra": "mean: 36.390972751971574 usec\nrounds: 12845"
          },
          {
            "name": "tests/perf/test_search.py::test_bench_search_memory_100k",
            "value": 26.028515217095677,
            "unit": "iter/sec",
            "range": "stddev: 0.00043740915218419904",
            "extra": "mean: 38.419402399995306 msec\nrounds: 25"
          },
          {
            "name": "tests/perf/test_search.py::test_bench_search_sa_sync_10k",
            "value": 26174.930386968477,
            "unit": "iter/sec",
            "range": "stddev: 0.0000034782410364776235",
            "extra": "mean: 38.20449511101137 usec\nrounds: 5932"
          },
          {
            "name": "tests/perf/test_sorting.py::test_bench_sort_sa_async_1k",
            "value": 50408.06579764734,
            "unit": "iter/sec",
            "range": "stddev: 0.000007732022232962257",
            "extra": "mean: 19.838095038486326 usec\nrounds: 14310"
          },
          {
            "name": "tests/perf/test_sorting.py::test_bench_sort_sa_async_10k",
            "value": 50509.32991033835,
            "unit": "iter/sec",
            "range": "stddev: 0.0000056476121559497485",
            "extra": "mean: 19.798322444093998 usec\nrounds: 19591"
          },
          {
            "name": "tests/perf/test_sorting.py::test_bench_sort_sa_sync_1k",
            "value": 50737.94743062609,
            "unit": "iter/sec",
            "range": "stddev: 0.000005856883001052038",
            "extra": "mean: 19.709114196377342 usec\nrounds: 19195"
          },
          {
            "name": "tests/perf/test_sorting.py::test_bench_sort_sa_sync_10k",
            "value": 51604.50354394432,
            "unit": "iter/sec",
            "range": "stddev: 0.00000563847528095238",
            "extra": "mean: 19.378153675065203 usec\nrounds: 19808"
          },
          {
            "name": "tests/perf/test_sorting.py::test_bench_sort_memory_10k",
            "value": 456.2877415837609,
            "unit": "iter/sec",
            "range": "stddev: 0.000016980125954319017",
            "extra": "mean: 2.1915995300005875 msec\nrounds: 400"
          },
          {
            "name": "tests/perf/test_sorting.py::test_bench_sort_memory_100k",
            "value": 44.12657688279488,
            "unit": "iter/sec",
            "range": "stddev: 0.00023772598859882977",
            "extra": "mean: 22.66207965000575 msec\nrounds: 40"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_sort_paginate",
            "value": 456.61280524468873,
            "unit": "iter/sec",
            "range": "stddev: 0.00004256478076874505",
            "extra": "mean: 2.190039325472097 msec\nrounds: 424"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_memory",
            "value": 580163.8976467024,
            "unit": "iter/sec",
            "range": "stddev: 5.012812862898331e-7",
            "extra": "mean: 1.7236508580700447 usec\nrounds: 137288"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_sa_filter",
            "value": 988.9166954884994,
            "unit": "iter/sec",
            "range": "stddev: 0.00005169673149509761",
            "extra": "mean: 1.0112075208782128 msec\nrounds: 455"
          },
          {
            "name": "tests/perf/test_competitors.py::test_fastapi_pagination_full_pipeline",
            "value": 1160.9887442695774,
            "unit": "iter/sec",
            "range": "stddev: 0.00001978815645362627",
            "extra": "mean: 861.3347932405137 usec\nrounds: 1006"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_sa_async",
            "value": 954.551511838072,
            "unit": "iter/sec",
            "range": "stddev: 0.00007631107282668141",
            "extra": "mean: 1.0476123997482472 msec\nrounds: 798"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_100k",
            "value": 496936.2297968023,
            "unit": "iter/sec",
            "range": "stddev: 4.7442787324283165e-7",
            "extra": "mean: 2.012330637291028 usec\nrounds: 125866"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_full_pipeline",
            "value": 332.4513205262025,
            "unit": "iter/sec",
            "range": "stddev: 0.00002793526837011521",
            "extra": "mean: 3.007959175548481 msec\nrounds: 319"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_python_search_paginate",
            "value": 1827.6812662735697,
            "unit": "iter/sec",
            "range": "stddev: 0.000013219513632136702",
            "extra": "mean: 547.1413525175996 usec\nrounds: 1807"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_sa_filter",
            "value": 946.0860998183979,
            "unit": "iter/sec",
            "range": "stddev: 0.000028861866561265345",
            "extra": "mean: 1.0569862512428319 msec\nrounds: 402"
          },
          {
            "name": "tests/perf/test_competitors.py::test_fastapi_pagination_100k",
            "value": 17981.574624940822,
            "unit": "iter/sec",
            "range": "stddev: 0.0000049413943106911684",
            "extra": "mean: 55.61248226909889 usec\nrounds: 5922"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_sqlalchemy",
            "value": 2336.5288113709616,
            "unit": "iter/sec",
            "range": "stddev: 0.000014959456482248672",
            "extra": "mean: 427.9853067222606 usec\nrounds: 714"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_sa_sync",
            "value": 2590.5669730091754,
            "unit": "iter/sec",
            "range": "stddev: 0.00001682258953076758",
            "extra": "mean: 386.01588394312404 usec\nrounds: 1887"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_python_sort_paginate",
            "value": 1579.2560262567974,
            "unit": "iter/sec",
            "range": "stddev: 0.000011825732719676927",
            "extra": "mean: 633.2095514431765 usec\nrounds: 1351"
          },
          {
            "name": "tests/perf/test_competitors.py::test_sqlalchemy_pagination_lib_10k",
            "value": 1841.7553504926448,
            "unit": "iter/sec",
            "range": "stddev: 0.000022884781462597266",
            "extra": "mean: 542.9602795683548 usec\nrounds: 465"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_python_100k",
            "value": 4489054.927577331,
            "unit": "iter/sec",
            "range": "stddev: 2.6201012470974024e-8",
            "extra": "mean: 222.7640374495032 nsec\nrounds: 198020"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_filter_paginate",
            "value": 791.5692550433901,
            "unit": "iter/sec",
            "range": "stddev: 0.000020999164911989314",
            "extra": "mean: 1.2633133407198651 msec\nrounds: 722"
          },
          {
            "name": "tests/perf/test_competitors.py::test_fastapi_pagination_memory",
            "value": 17691.783537769945,
            "unit": "iter/sec",
            "range": "stddev: 0.000004410037525952907",
            "extra": "mean: 56.52341370021365 usec\nrounds: 5956"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_python_filter_paginate",
            "value": 3275.45248824546,
            "unit": "iter/sec",
            "range": "stddev: 0.000008654244229935623",
            "extra": "mean: 305.3013296906845 usec\nrounds: 3294"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_search_paginate",
            "value": 376.52995685506716,
            "unit": "iter/sec",
            "range": "stddev: 0.000024801714103847207",
            "extra": "mean: 2.6558311810099005 msec\nrounds: 337"
          },
          {
            "name": "tests/perf/test_competitors.py::test_paginate_lib_100k",
            "value": 359506.2128514541,
            "unit": "iter/sec",
            "range": "stddev: 0.00001034190722858985",
            "extra": "mean: 2.7815930970105214 usec\nrounds: 85529"
          },
          {
            "name": "tests/perf/test_competitors.py::test_paginate_lib_full_pipeline",
            "value": 1245.5704106389762,
            "unit": "iter/sec",
            "range": "stddev: 0.0008270298876415021",
            "extra": "mean: 802.845019003784 usec\nrounds: 1263"
          },
          {
            "name": "tests/perf/test_competitors.py::test_fastapi_filter_10k",
            "value": 2710.4630332607135,
            "unit": "iter/sec",
            "range": "stddev: 0.00001923315124067719",
            "extra": "mean: 368.9406524747878 usec\nrounds: 869"
          },
          {
            "name": "tests/perf/test_competitors.py::test_paginate_lib_memory",
            "value": 366996.41197433404,
            "unit": "iter/sec",
            "range": "stddev: 0.00000884237545737192",
            "extra": "mean: 2.7248222799244566 usec\nrounds: 88645"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_python_full_pipeline",
            "value": 1370.2723920731996,
            "unit": "iter/sec",
            "range": "stddev: 0.000026681066996964235",
            "extra": "mean: 729.7819074403276 usec\nrounds: 1102"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_python_slice",
            "value": 4899618.047842718,
            "unit": "iter/sec",
            "range": "stddev: 2.506346626335743e-8",
            "extra": "mean: 204.097541937994 nsec\nrounds: 196464"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "git.owiwz@passinbox.com",
            "name": "CybLow"
          },
          "committer": {
            "email": "git.owiwz@passinbox.com",
            "name": "CybLow"
          },
          "distinct": true,
          "id": "82278fe313e6f9f0b0c3070615ab2fc007d64217",
          "message": "fix(test): use DateTime(timezone=True) for asyncpg compat with UTC datetimes",
          "timestamp": "2026-03-17T04:23:49+01:00",
          "tree_id": "f850d43eb960555a955eb197d023d01e5646582c",
          "url": "https://github.com/CybLow/pypaginate/commit/82278fe313e6f9f0b0c3070615ab2fc007d64217"
        },
        "date": 1773718565563,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/perf/test_competitor_scaling.py::test_paginate_lib_scaling[500K]",
            "value": 386290.29662385886,
            "unit": "iter/sec",
            "range": "stddev: 0.000008520406825115787",
            "extra": "mean: 2.588726687519481 usec\nrounds: 39925"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_paginate_scaling[1M]",
            "value": 2981973.554829594,
            "unit": "iter/sec",
            "range": "stddev: 1.5165385603849479e-7",
            "extra": "mean: 335.3483797267093 nsec\nrounds: 193424"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_pipeline_scaling[10K]",
            "value": 1417.9060961254306,
            "unit": "iter/sec",
            "range": "stddev: 0.000020955870887362895",
            "extra": "mean: 705.2653223881323 usec\nrounds: 1340"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_search_scaling[500K]",
            "value": 35.79915271997357,
            "unit": "iter/sec",
            "range": "stddev: 0.0001426665730450649",
            "extra": "mean: 27.933621999999623 msec\nrounds: 37"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_filter_scaling[500K]",
            "value": 60.33865582419533,
            "unit": "iter/sec",
            "range": "stddev: 0.000245589238738899",
            "extra": "mean: 16.573123586207032 msec\nrounds: 58"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_sort_scaling[100K]",
            "value": 147.75894541930114,
            "unit": "iter/sec",
            "range": "stddev: 0.0003898005052789198",
            "extra": "mean: 6.767779758865104 msec\nrounds: 141"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_paginate_scaling[500K]",
            "value": 4344913.016177137,
            "unit": "iter/sec",
            "range": "stddev: 3.195616827010086e-8",
            "extra": "mean: 230.1542047623868 nsec\nrounds: 200000"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_fp_paginate_scaling[100K]",
            "value": 17102.379193580196,
            "unit": "iter/sec",
            "range": "stddev: 0.000005660359501010334",
            "extra": "mean: 58.47139679696582 usec\nrounds: 562"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_pipeline_scaling[500K]",
            "value": 18.394277178543916,
            "unit": "iter/sec",
            "range": "stddev: 0.0005356832177903252",
            "extra": "mean: 54.36473476470466 msec\nrounds: 17"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_paginate_lib_scaling[10K]",
            "value": 376771.393851996,
            "unit": "iter/sec",
            "range": "stddev: 0.000008829849462356972",
            "extra": "mean: 2.654129311082523 usec\nrounds: 68602"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_paginate_scaling[1K]",
            "value": 4307150.716104772,
            "unit": "iter/sec",
            "range": "stddev: 3.052217449685539e-8",
            "extra": "mean: 232.1720473492796 nsec\nrounds: 197629"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_filter_scaling[10K]",
            "value": 3722.0664726945042,
            "unit": "iter/sec",
            "range": "stddev: 0.00000716193026595719",
            "extra": "mean: 268.66795833339137 usec\nrounds: 3576"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_paginate_scaling[10K]",
            "value": 4326524.347029691,
            "unit": "iter/sec",
            "range": "stddev: 3.2932549736179925e-8",
            "extra": "mean: 231.13241017265216 nsec\nrounds: 199243"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_fp_paginate_scaling[1K]",
            "value": 18110.92825801899,
            "unit": "iter/sec",
            "range": "stddev: 0.000004603697773084657",
            "extra": "mean: 55.2152813899657 usec\nrounds: 5583"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_pipeline_scaling[1M]",
            "value": 8.234471209803361,
            "unit": "iter/sec",
            "range": "stddev: 0.0010164690741287388",
            "extra": "mean: 121.44070633333115 msec\nrounds: 9"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_search_scaling[10K]",
            "value": 1887.7492319976025,
            "unit": "iter/sec",
            "range": "stddev: 0.00001064065955749879",
            "extra": "mean: 529.7313769487313 usec\nrounds: 1796"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_paginate_lib_scaling[1M]",
            "value": 384857.37003549846,
            "unit": "iter/sec",
            "range": "stddev: 0.000008508449977923487",
            "extra": "mean: 2.5983652071097456 usec\nrounds: 51798"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_pipeline_scaling[100K]",
            "value": 132.65979836017294,
            "unit": "iter/sec",
            "range": "stddev: 0.00031047574580037084",
            "extra": "mean: 7.538078697247738 msec\nrounds: 109"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_fp_paginate_scaling[10K]",
            "value": 18510.245386709754,
            "unit": "iter/sec",
            "range": "stddev: 0.000005569458282411891",
            "extra": "mean: 54.02413523474919 usec\nrounds: 5154"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_paginate_scaling[100K]",
            "value": 4491346.996737246,
            "unit": "iter/sec",
            "range": "stddev: 3.102776016831233e-8",
            "extra": "mean: 222.65035427600347 nsec\nrounds: 197239"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_fp_paginate_scaling[500K]",
            "value": 18311.002919205963,
            "unit": "iter/sec",
            "range": "stddev: 0.00000465356316036729",
            "extra": "mean: 54.61197316238339 usec\nrounds: 4136"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_filter_scaling[1M]",
            "value": 29.5439788213153,
            "unit": "iter/sec",
            "range": "stddev: 0.0008563372505799024",
            "extra": "mean: 33.84784446428465 msec\nrounds: 28"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_sort_scaling[1K]",
            "value": 13629.966079431055,
            "unit": "iter/sec",
            "range": "stddev: 0.000003610864912834179",
            "extra": "mean: 73.36775412149392 usec\nrounds: 9948"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_search_scaling[1M]",
            "value": 17.52934005916494,
            "unit": "iter/sec",
            "range": "stddev: 0.00023894237290931719",
            "extra": "mean: 57.04721322222087 msec\nrounds: 18"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_sort_scaling[500K]",
            "value": 20.809650000728013,
            "unit": "iter/sec",
            "range": "stddev: 0.000660699532726991",
            "extra": "mean: 48.05462849999955 msec\nrounds: 20"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_search_scaling[100K]",
            "value": 183.21480589058007,
            "unit": "iter/sec",
            "range": "stddev: 0.00019798432750349232",
            "extra": "mean: 5.458074172221769 msec\nrounds: 180"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_paginate_lib_scaling[1K]",
            "value": 390944.95432689047,
            "unit": "iter/sec",
            "range": "stddev: 0.000008437658295731693",
            "extra": "mean: 2.5579048634142114 usec\nrounds: 86791"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_filter_scaling[100K]",
            "value": 358.9878179290419,
            "unit": "iter/sec",
            "range": "stddev: 0.00010593748016760724",
            "extra": "mean: 2.785609845394981 msec\nrounds: 304"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_pipeline_scaling[1K]",
            "value": 14600.97727083442,
            "unit": "iter/sec",
            "range": "stddev: 0.0000035238876457494147",
            "extra": "mean: 68.48856630970235 usec\nrounds: 12140"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_fp_paginate_scaling[1M]",
            "value": 18169.6827629796,
            "unit": "iter/sec",
            "range": "stddev: 0.000005788083365311273",
            "extra": "mean: 55.03673416012975 usec\nrounds: 3709"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_sort_scaling[10K]",
            "value": 1603.8436407561644,
            "unit": "iter/sec",
            "range": "stddev: 0.000012731141073490574",
            "extra": "mean: 623.5021760154436 usec\nrounds: 1551"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_paginate_lib_scaling[100K]",
            "value": 382968.6659948295,
            "unit": "iter/sec",
            "range": "stddev: 0.000008572893340198083",
            "extra": "mean: 2.611179683336028 usec\nrounds: 55698"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_search_scaling[1K]",
            "value": 18586.680315831105,
            "unit": "iter/sec",
            "range": "stddev: 0.0000033968379896277826",
            "extra": "mean: 53.80196909871288 usec\nrounds: 16666"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_sort_scaling[1M]",
            "value": 9.571972049814816,
            "unit": "iter/sec",
            "range": "stddev: 0.00031700157436027735",
            "extra": "mean: 104.47167989999997 msec\nrounds: 10"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_filter_scaling[1K]",
            "value": 36364.16302745148,
            "unit": "iter/sec",
            "range": "stddev: 0.0000019363631917591755",
            "extra": "mean: 27.499601716258258 usec\nrounds: 29366"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_search_spec_many_fields",
            "value": 704266.5930094854,
            "unit": "iter/sec",
            "range": "stddev: 3.646522639262008e-7",
            "extra": "mean: 1.4199168467253016 usec\nrounds: 43041"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_valid_filter_request",
            "value": 486.04583327366385,
            "unit": "iter/sec",
            "range": "stddev: 0.00015573770506377402",
            "extra": "mean: 2.0574191393941215 msec\nrounds: 165"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_filter_invalid_page",
            "value": 845.621517276965,
            "unit": "iter/sec",
            "range": "stddev: 0.00009099207148925316",
            "extra": "mean: 1.1825621505235087 msec\nrounds: 764"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_valid_sort_spec",
            "value": 1161525.0743206604,
            "unit": "iter/sec",
            "range": "stddev: 3.8967246982390384e-7",
            "extra": "mean: 860.93707497866 nsec\nrounds: 82352"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_valid_search_request",
            "value": 270.3584712356749,
            "unit": "iter/sec",
            "range": "stddev: 0.014710521398308552",
            "extra": "mean: 3.6987929227055263 msec\nrounds: 207"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_valid_request",
            "value": 499.5170141927421,
            "unit": "iter/sec",
            "range": "stddev: 0.00008382198028450678",
            "extra": "mean: 2.001933811235793 msec\nrounds: 445"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_sort_spec_desc",
            "value": 1055344.5752314623,
            "unit": "iter/sec",
            "range": "stddev: 3.7620700283446614e-7",
            "extra": "mean: 947.5578152099527 nsec\nrounds: 119389"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_valid_sort_request",
            "value": 403.6555716434351,
            "unit": "iter/sec",
            "range": "stddev: 0.00013730199139279676",
            "extra": "mean: 2.4773595863637414 msec\nrounds: 220"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_invalid_page",
            "value": 762.3406909021238,
            "unit": "iter/sec",
            "range": "stddev: 0.00008770033660992679",
            "extra": "mean: 1.3117494736069246 msec\nrounds: 682"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_valid_offset_params",
            "value": 881688.1454152298,
            "unit": "iter/sec",
            "range": "stddev: 3.700975029363413e-7",
            "extra": "mean: 1.134187870393847 usec\nrounds: 67669"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_valid_filter_spec",
            "value": 914339.6861540715,
            "unit": "iter/sec",
            "range": "stddev: 2.908045151969361e-7",
            "extra": "mean: 1.0936854378554166 usec\nrounds: 81348"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_invalid_filter_param",
            "value": 506.28178592958864,
            "unit": "iter/sec",
            "range": "stddev: 0.00012798509468127145",
            "extra": "mean: 1.9751846260159067 msec\nrounds: 246"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_invalid_limit",
            "value": 743.5716414535656,
            "unit": "iter/sec",
            "range": "stddev: 0.0000858051423334061",
            "extra": "mean: 1.3448603258257097 msec\nrounds: 666"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_sort_invalid_limit",
            "value": 666.305438287451,
            "unit": "iter/sec",
            "range": "stddev: 0.0030956035258807263",
            "extra": "mean: 1.5008132044820408 msec\nrounds: 714"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_invalid_params_caught",
            "value": 407922.9118644331,
            "unit": "iter/sec",
            "range": "stddev: 5.710778751933267e-7",
            "extra": "mean: 2.4514435716038783 usec\nrounds: 35133"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_filter_spec_empty_field",
            "value": 920003.6971887639,
            "unit": "iter/sec",
            "range": "stddev: 3.113928439728969e-7",
            "extra": "mean: 1.0869521536225117 usec\nrounds: 93633"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_valid_search_spec",
            "value": 734405.7948455418,
            "unit": "iter/sec",
            "range": "stddev: 3.3549169783640836e-7",
            "extra": "mean: 1.3616450292447888 usec\nrounds: 69848"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_invalid_filter_operator",
            "value": 528670.0941829737,
            "unit": "iter/sec",
            "range": "stddev: 4.528165253021017e-7",
            "extra": "mean: 1.8915388084234968 usec\nrounds: 61649"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_valid_cursor_params",
            "value": 823534.4610119411,
            "unit": "iter/sec",
            "range": "stddev: 3.4960312766586543e-7",
            "extra": "mean: 1.214278269267836 usec\nrounds: 60021"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_search_invalid_page",
            "value": 727.5169314621475,
            "unit": "iter/sec",
            "range": "stddev: 0.0001257243975281941",
            "extra": "mean: 1.374538456431828 msec\nrounds: 241"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_filtered_json_dumps[1000]",
            "value": 1302.7261520123027,
            "unit": "iter/sec",
            "range": "stddev: 0.000012412207986679355",
            "extra": "mean: 767.6210372036472 usec\nrounds: 887"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_json_dumps[20]",
            "value": 276564.8418786875,
            "unit": "iter/sec",
            "range": "stddev: 7.545775284506811e-7",
            "extra": "mean: 3.615788591228962 usec\nrounds: 90001"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_searched_json_dumps[100]",
            "value": 53542.383051027005,
            "unit": "iter/sec",
            "range": "stddev: 0.0000014429306547818737",
            "extra": "mean: 18.676792907162525 usec\nrounds: 25124"
          },
          {
            "name": "tests/perf/test_serialization.py::test_filtered_page_model_dump_json[100]",
            "value": 30217.238702202467,
            "unit": "iter/sec",
            "range": "stddev: 0.0000025235553132239588",
            "extra": "mean: 33.09369230773268 usec\nrounds: 16172"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_dict_dump[20]",
            "value": 5121516.13367297,
            "unit": "iter/sec",
            "range": "stddev: 2.449204539202082e-8",
            "extra": "mean: 195.25468121153398 nsec\nrounds: 197278"
          },
          {
            "name": "tests/perf/test_serialization.py::test_searched_page_model_dump_json[100]",
            "value": 121871.43253157455,
            "unit": "iter/sec",
            "range": "stddev: 8.892717284111152e-7",
            "extra": "mean: 8.20536838886274 usec\nrounds: 40840"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_json_dumps[100]",
            "value": 122526.08807264197,
            "unit": "iter/sec",
            "range": "stddev: 0.0000010070521030978908",
            "extra": "mean: 8.161527195801197 usec\nrounds: 40907"
          },
          {
            "name": "tests/perf/test_serialization.py::test_fp_filtered_page_serialize[100]",
            "value": 10329.937662819626,
            "unit": "iter/sec",
            "range": "stddev: 0.000005128448923197597",
            "extra": "mean: 96.80600528687444 usec\nrounds: 4918"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_searched_json_dumps[20]",
            "value": 53676.916045892875,
            "unit": "iter/sec",
            "range": "stddev: 0.000001428861810740206",
            "extra": "mean: 18.629982377247913 usec\nrounds: 27124"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_searched_json_dumps[1000]",
            "value": 54413.63171573076,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018311508363027756",
            "extra": "mean: 18.37774778982275 usec\nrounds: 25225"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_json_dumps[1000]",
            "value": 17548.101156000215,
            "unit": "iter/sec",
            "range": "stddev: 0.000004961179906361905",
            "extra": "mean: 56.986222675042555 usec\nrounds: 7850"
          },
          {
            "name": "tests/perf/test_serialization.py::test_cursor_page_model_dump[1000]",
            "value": 37953.501036907146,
            "unit": "iter/sec",
            "range": "stddev: 0.0000016208162502057643",
            "extra": "mean: 26.348030423532457 usec\nrounds: 23896"
          },
          {
            "name": "tests/perf/test_serialization.py::test_filtered_page_model_dump_json[1000]",
            "value": 3075.921652442323,
            "unit": "iter/sec",
            "range": "stddev: 0.000014399212627589105",
            "extra": "mean: 325.1058098979818 usec\nrounds: 2546"
          },
          {
            "name": "tests/perf/test_serialization.py::test_cursor_page_model_dump[20]",
            "value": 506963.0161077497,
            "unit": "iter/sec",
            "range": "stddev: 4.479640512304988e-7",
            "extra": "mean: 1.9725304770308143 usec\nrounds: 71398"
          },
          {
            "name": "tests/perf/test_serialization.py::test_fp_filtered_page_serialize[1000]",
            "value": 10580.341538244265,
            "unit": "iter/sec",
            "range": "stddev: 0.000004381245916246024",
            "extra": "mean: 94.51490732934724 usec\nrounds: 7122"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_model_dump_json[100]",
            "value": 269690.29803779256,
            "unit": "iter/sec",
            "range": "stddev: 6.920697927313837e-7",
            "extra": "mean: 3.7079568945408146 usec\nrounds: 86648"
          },
          {
            "name": "tests/perf/test_serialization.py::test_searched_page_model_dump_json[20]",
            "value": 121940.55871638437,
            "unit": "iter/sec",
            "range": "stddev: 8.488242154657292e-7",
            "extra": "mean: 8.200716894580182 usec\nrounds: 56456"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_create[1000]",
            "value": 2370824.695668226,
            "unit": "iter/sec",
            "range": "stddev: 1.7340290865957512e-7",
            "extra": "mean: 421.79415535324773 nsec\nrounds: 137288"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_model_dump[20]",
            "value": 504939.33955004736,
            "unit": "iter/sec",
            "range": "stddev: 6.306080470617396e-7",
            "extra": "mean: 1.9804359091749562 usec\nrounds: 65493"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_pipeline_json_dumps",
            "value": 53577.39576902317,
            "unit": "iter/sec",
            "range": "stddev: 0.000001399562323130876",
            "extra": "mean: 18.66458766139152 usec\nrounds: 18657"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_sorted_json_dumps[20]",
            "value": 53540.989595598025,
            "unit": "iter/sec",
            "range": "stddev: 0.000001596666526517159",
            "extra": "mean: 18.677278988549308 usec\nrounds: 28632"
          },
          {
            "name": "tests/perf/test_serialization.py::test_pipeline_page_model_dump",
            "value": 4625285.482071856,
            "unit": "iter/sec",
            "range": "stddev: 3.036636278773728e-8",
            "extra": "mean: 216.20287090950535 nsec\nrounds: 197668"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_model_dump[100]",
            "value": 245822.99377927068,
            "unit": "iter/sec",
            "range": "stddev: 5.596646274051828e-7",
            "extra": "mean: 4.067967705648885 usec\nrounds: 53291"
          },
          {
            "name": "tests/perf/test_serialization.py::test_sorted_page_model_dump_json[20]",
            "value": 123947.13239013084,
            "unit": "iter/sec",
            "range": "stddev: 8.611740923177819e-7",
            "extra": "mean: 8.067955915691874 usec\nrounds: 48929"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_sorted_json_dumps[100]",
            "value": 12452.791991440157,
            "unit": "iter/sec",
            "range": "stddev: 0.0000043420797478360425",
            "extra": "mean: 80.3032766216109 usec\nrounds: 7400"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_filtered_json_dumps[100]",
            "value": 12486.664661357572,
            "unit": "iter/sec",
            "range": "stddev: 0.000005624726767156658",
            "extra": "mean: 80.08543731415288 usec\nrounds: 10425"
          },
          {
            "name": "tests/perf/test_serialization.py::test_pipeline_page_model_dump_json",
            "value": 352626.88591415086,
            "unit": "iter/sec",
            "range": "stddev: 4.7313286867838596e-7",
            "extra": "mean: 2.8358586368353547 usec\nrounds: 22375"
          },
          {
            "name": "tests/perf/test_serialization.py::test_searched_page_model_dump_json[1000]",
            "value": 123367.406913257,
            "unit": "iter/sec",
            "range": "stddev: 8.527060344266995e-7",
            "extra": "mean: 8.10586868137001 usec\nrounds: 27399"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_dict_construction[100]",
            "value": 7378383.446197016,
            "unit": "iter/sec",
            "range": "stddev: 1.2044209026057805e-8",
            "extra": "mean: 135.53104244199855 nsec\nrounds: 73606"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_model_dump[1000]",
            "value": 37798.42863576594,
            "unit": "iter/sec",
            "range": "stddev: 0.000002120305739858979",
            "extra": "mean: 26.4561262489566 usec\nrounds: 25022"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_dict_construction[1000]",
            "value": 7410786.602767276,
            "unit": "iter/sec",
            "range": "stddev: 1.2051206413439717e-8",
            "extra": "mean: 134.93844224665648 nsec\nrounds: 73606"
          },
          {
            "name": "tests/perf/test_serialization.py::test_cursor_page_model_dump[100]",
            "value": 249299.16102666414,
            "unit": "iter/sec",
            "range": "stddev: 6.787601296593786e-7",
            "extra": "mean: 4.011244947162272 usec\nrounds: 51852"
          },
          {
            "name": "tests/perf/test_serialization.py::test_filtered_page_model_dump_json[20]",
            "value": 123025.8658072241,
            "unit": "iter/sec",
            "range": "stddev: 8.666619992719045e-7",
            "extra": "mean: 8.128371976401729 usec\nrounds: 47667"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_dict_dump[100]",
            "value": 5179473.320289237,
            "unit": "iter/sec",
            "range": "stddev: 1.6557516454127645e-8",
            "extra": "mean: 193.06982354412258 nsec\nrounds: 52591"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_dict_dump[1000]",
            "value": 5163668.635092342,
            "unit": "iter/sec",
            "range": "stddev: 2.004275269526237e-8",
            "extra": "mean: 193.66076149886038 nsec\nrounds: 51635"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_dict_construction[20]",
            "value": 6671109.541095883,
            "unit": "iter/sec",
            "range": "stddev: 1.1994653059864177e-8",
            "extra": "mean: 149.90010190049108 nsec\nrounds: 71246"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_model_dump_json[20]",
            "value": 530460.9452725141,
            "unit": "iter/sec",
            "range": "stddev: 6.261082090900937e-7",
            "extra": "mean: 1.8851529201386716 usec\nrounds: 69363"
          },
          {
            "name": "tests/perf/test_serialization.py::test_fp_filtered_page_serialize[20]",
            "value": 46988.27715473421,
            "unit": "iter/sec",
            "range": "stddev: 0.000001500019363054169",
            "extra": "mean: 21.28190392482281 usec\nrounds: 19797"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_create[20]",
            "value": 2373307.6489266516,
            "unit": "iter/sec",
            "range": "stddev: 1.691946001692226e-7",
            "extra": "mean: 421.352874521876 nsec\nrounds: 142980"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_create[100]",
            "value": 3065689.1344355266,
            "unit": "iter/sec",
            "range": "stddev: 3.852344644253444e-8",
            "extra": "mean: 326.1909333101724 nsec\nrounds: 145075"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_filtered_json_dumps[20]",
            "value": 54124.32255809144,
            "unit": "iter/sec",
            "range": "stddev: 0.000001604997114854869",
            "extra": "mean: 18.475981827332873 usec\nrounds: 21736"
          },
          {
            "name": "tests/perf/test_serialization.py::test_sorted_page_model_dump_json[100]",
            "value": 30045.445624524684,
            "unit": "iter/sec",
            "range": "stddev: 0.000001917194990752865",
            "extra": "mean: 33.282914572042394 usec\nrounds: 18460"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_model_dump_json[1000]",
            "value": 39895.34313036645,
            "unit": "iter/sec",
            "range": "stddev: 0.0000017834229600363532",
            "extra": "mean: 25.065582134042288 usec\nrounds: 20777"
          },
          {
            "name": "tests/perf/test_serialization.py::test_sorted_page_model_dump_json[1000]",
            "value": 2925.349451618975,
            "unit": "iter/sec",
            "range": "stddev: 0.000007499667060413325",
            "extra": "mean: 341.83950209660264 usec\nrounds: 1908"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_sorted_json_dumps[1000]",
            "value": 1292.6712323997265,
            "unit": "iter/sec",
            "range": "stddev: 0.000015239788119357679",
            "extra": "mean: 773.5919040633333 usec\nrounds: 886"
          },
          {
            "name": "tests/perf/test_overhead.py::test_filter_full_http",
            "value": 276.9666801144798,
            "unit": "iter/sec",
            "range": "stddev: 0.0001241663618991683",
            "extra": "mean: 3.610542609626059 msec\nrounds: 187"
          },
          {
            "name": "tests/perf/test_overhead.py::test_sort_full_http",
            "value": 208.31415152871298,
            "unit": "iter/sec",
            "range": "stddev: 0.00009374063326783301",
            "extra": "mean: 4.8004419894736 msec\nrounds: 190"
          },
          {
            "name": "tests/perf/test_overhead.py::test_sort_plus_paginate",
            "value": 451.0662588866028,
            "unit": "iter/sec",
            "range": "stddev: 0.000049028033432779005",
            "extra": "mean: 2.2169691931033975 msec\nrounds: 435"
          },
          {
            "name": "tests/perf/test_overhead.py::test_pipeline_full_http",
            "value": 78.06023292506727,
            "unit": "iter/sec",
            "range": "stddev: 0.0003549644699745445",
            "extra": "mean: 12.810620241934647 msec\nrounds: 62"
          },
          {
            "name": "tests/perf/test_overhead.py::test_search_full_http",
            "value": 87.11571063995167,
            "unit": "iter/sec",
            "range": "stddev: 0.0002090180468778931",
            "extra": "mean: 11.478985738094815 msec\nrounds: 84"
          },
          {
            "name": "tests/perf/test_overhead.py::test_filter_plus_paginate_plus_serialize",
            "value": 793.6329964232316,
            "unit": "iter/sec",
            "range": "stddev: 0.000016040982258966214",
            "extra": "mean: 1.2600282555120936 msec\nrounds: 771"
          },
          {
            "name": "tests/perf/test_overhead.py::test_filter_only",
            "value": 814.6369857987427,
            "unit": "iter/sec",
            "range": "stddev: 0.00002684990755034743",
            "extra": "mean: 1.2275406315114836 msec\nrounds: 787"
          },
          {
            "name": "tests/perf/test_overhead.py::test_paginate_only",
            "value": 629705.0981006006,
            "unit": "iter/sec",
            "range": "stddev: 6.067771156086542e-7",
            "extra": "mean: 1.588044948367627 usec\nrounds: 57199"
          },
          {
            "name": "tests/perf/test_overhead.py::test_pipeline_ops_only",
            "value": 96.05905952500338,
            "unit": "iter/sec",
            "range": "stddev: 0.0001442293958947946",
            "extra": "mean: 10.410262238094349 msec\nrounds: 84"
          },
          {
            "name": "tests/perf/test_overhead.py::test_search_plus_paginate",
            "value": 112.92790305771324,
            "unit": "iter/sec",
            "range": "stddev: 0.00026415622871046136",
            "extra": "mean: 8.855207375000466 msec\nrounds: 112"
          },
          {
            "name": "tests/perf/test_overhead.py::test_search_only",
            "value": 111.76146786775476,
            "unit": "iter/sec",
            "range": "stddev: 0.00021777165379884393",
            "extra": "mean: 8.947627649122158 msec\nrounds: 114"
          },
          {
            "name": "tests/perf/test_overhead.py::test_filter_plus_paginate",
            "value": 792.306214849368,
            "unit": "iter/sec",
            "range": "stddev: 0.00005274802770797828",
            "extra": "mean: 1.2621382759065174 msec\nrounds: 772"
          },
          {
            "name": "tests/perf/test_overhead.py::test_pipeline_plus_paginate",
            "value": 97.032265436004,
            "unit": "iter/sec",
            "range": "stddev: 0.0000623958986075293",
            "extra": "mean: 10.305850280899948 msec\nrounds: 89"
          },
          {
            "name": "tests/perf/test_overhead.py::test_paginate_full_http",
            "value": 408.4406245789775,
            "unit": "iter/sec",
            "range": "stddev: 0.00010854567855833708",
            "extra": "mean: 2.448336281511675 msec\nrounds: 238"
          },
          {
            "name": "tests/perf/test_overhead.py::test_sort_plus_paginate_plus_serialize",
            "value": 454.03735464183023,
            "unit": "iter/sec",
            "range": "stddev: 0.00002058030675700375",
            "extra": "mean: 2.2024619555561795 msec\nrounds: 405"
          },
          {
            "name": "tests/perf/test_overhead.py::test_paginate_plus_serialize",
            "value": 215093.79165843662,
            "unit": "iter/sec",
            "range": "stddev: 7.766842903318516e-7",
            "extra": "mean: 4.649134650933925 usec\nrounds: 45889"
          },
          {
            "name": "tests/perf/test_overhead.py::test_pipeline_plus_serialize",
            "value": 94.47475304375449,
            "unit": "iter/sec",
            "range": "stddev: 0.0002092001535755799",
            "extra": "mean: 10.584838465117402 msec\nrounds: 86"
          },
          {
            "name": "tests/perf/test_overhead.py::test_sort_only",
            "value": 459.2828148573127,
            "unit": "iter/sec",
            "range": "stddev: 0.000016827492422533183",
            "extra": "mean: 2.1773076798239757 msec\nrounds: 456"
          },
          {
            "name": "tests/perf/test_overhead.py::test_search_plus_paginate_plus_serialize",
            "value": 112.58664680067945,
            "unit": "iter/sec",
            "range": "stddev: 0.00004410343275069",
            "extra": "mean: 8.882047990738855 msec\nrounds: 108"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_offset_10k",
            "value": 418.1061833253769,
            "unit": "iter/sec",
            "range": "stddev: 0.00008965489299535298",
            "extra": "mean: 2.3917369316248167 msec\nrounds: 234"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_sa_sort_10k",
            "value": 157.85972362612233,
            "unit": "iter/sec",
            "range": "stddev: 0.00012524511406472138",
            "extra": "mean: 6.334738063829486 msec\nrounds: 94"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_pipeline_10k",
            "value": 297.18028835596806,
            "unit": "iter/sec",
            "range": "stddev: 0.00009323877516845081",
            "extra": "mean: 3.364960729838789 msec\nrounds: 248"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_sa_sort_10k",
            "value": 234.93886314055578,
            "unit": "iter/sec",
            "range": "stddev: 0.008628853614212851",
            "extra": "mean: 4.25642648743786 msec\nrounds: 199"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_offset_10k",
            "value": 355.190868205299,
            "unit": "iter/sec",
            "range": "stddev: 0.0000869624598122072",
            "extra": "mean: 2.815387695783901 msec\nrounds: 332"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_sa_filter_10k",
            "value": 244.28769780938325,
            "unit": "iter/sec",
            "range": "stddev: 0.0002151855040829631",
            "extra": "mean: 4.093534013244891 msec\nrounds: 151"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_sort_10k",
            "value": 180.66671608275718,
            "unit": "iter/sec",
            "range": "stddev: 0.00033403766016127837",
            "extra": "mean: 5.535053836601174 msec\nrounds: 153"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_pipeline_10k",
            "value": 160.05868835315195,
            "unit": "iter/sec",
            "range": "stddev: 0.00010405899994982273",
            "extra": "mean: 6.247708326795792 msec\nrounds: 153"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_sa_search_10k",
            "value": 228.1333744703387,
            "unit": "iter/sec",
            "range": "stddev: 0.00011689224806681559",
            "extra": "mean: 4.383400729164322 msec\nrounds: 144"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_sa_10k",
            "value": 274.49000710174965,
            "unit": "iter/sec",
            "range": "stddev: 0.00014232592269204295",
            "extra": "mean: 3.64311987368383 msec\nrounds: 190"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_sa_search_10k",
            "value": 175.759633784415,
            "unit": "iter/sec",
            "range": "stddev: 0.0002947753950509657",
            "extra": "mean: 5.689588550386888 msec\nrounds: 129"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_sa_10k",
            "value": 217.65002945102668,
            "unit": "iter/sec",
            "range": "stddev: 0.009387847604054433",
            "extra": "mean: 4.5945318846143754 msec\nrounds: 182"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_search_10k",
            "value": 79.70500805289691,
            "unit": "iter/sec",
            "range": "stddev: 0.0002537789687601972",
            "extra": "mean: 12.546263082193548 msec\nrounds: 73"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_sa_pipeline_10k",
            "value": 179.90226817104718,
            "unit": "iter/sec",
            "range": "stddev: 0.00012813501079418714",
            "extra": "mean: 5.5585736086952595 msec\nrounds: 115"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_10k",
            "value": 297.07244575730624,
            "unit": "iter/sec",
            "range": "stddev: 0.00009009243371199961",
            "extra": "mean: 3.366182270626847 msec\nrounds: 303"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_sa_filter_10k",
            "value": 205.4635017114623,
            "unit": "iter/sec",
            "range": "stddev: 0.0001227823179883299",
            "extra": "mean: 4.867044471014252 msec\nrounds: 138"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_fp_fastapi_offset_10k",
            "value": 267.3402692924175,
            "unit": "iter/sec",
            "range": "stddev: 0.00010605925945637622",
            "extra": "mean: 3.740551330507554 msec\nrounds: 236"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_filter_10k",
            "value": 200.9287953219457,
            "unit": "iter/sec",
            "range": "stddev: 0.00015976517161782588",
            "extra": "mean: 4.976887451087896 msec\nrounds: 184"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_1k",
            "value": 270.1326572558085,
            "unit": "iter/sec",
            "range": "stddev: 0.0001358290246365136",
            "extra": "mean: 3.701884881889813 msec\nrounds: 254"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_fp_fastapi_pipeline_10k",
            "value": 205.58698829189316,
            "unit": "iter/sec",
            "range": "stddev: 0.0001757772026521834",
            "extra": "mean: 4.864121062857326 msec\nrounds: 175"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_filter_10k",
            "value": 248.34559714235743,
            "unit": "iter/sec",
            "range": "stddev: 0.00013403032796989963",
            "extra": "mean: 4.0266467837832325 msec\nrounds: 222"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_100k",
            "value": 214.07176142375897,
            "unit": "iter/sec",
            "range": "stddev: 0.010890564630797265",
            "extra": "mean: 4.671330741379204 msec\nrounds: 232"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_fp_fastapi_sa_10k",
            "value": 195.7402327599107,
            "unit": "iter/sec",
            "range": "stddev: 0.00013315115432728248",
            "extra": "mean: 5.108811744525568 msec\nrounds: 137"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_search_10k",
            "value": 194.84728220058796,
            "unit": "iter/sec",
            "range": "stddev: 0.00020274168045418775",
            "extra": "mean: 5.132224523257848 msec\nrounds: 172"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_sa_pipeline_10k",
            "value": 162.42954385968008,
            "unit": "iter/sec",
            "range": "stddev: 0.000322738833635234",
            "extra": "mean: 6.156515472726327 msec\nrounds: 110"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_sort_10k",
            "value": 205.24907838533474,
            "unit": "iter/sec",
            "range": "stddev: 0.000202180343741961",
            "extra": "mean: 4.872129063218493 msec\nrounds: 174"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_search_scaling[1K]",
            "value": 198.15017222613412,
            "unit": "iter/sec",
            "range": "stddev: 0.000203414205031862",
            "extra": "mean: 5.046677420288962 msec\nrounds: 138"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_filter_scaling[1K]",
            "value": 227.28872937274465,
            "unit": "iter/sec",
            "range": "stddev: 0.000118709454316808",
            "extra": "mean: 4.399690221154957 msec\nrounds: 208"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_pipeline_scaling[10K]",
            "value": 131.84612102287892,
            "unit": "iter/sec",
            "range": "stddev: 0.000260233918304892",
            "extra": "mean: 7.584599321101548 msec\nrounds: 109"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_pipeline_scaling[1K]",
            "value": 232.81219323274726,
            "unit": "iter/sec",
            "range": "stddev: 0.00017042604672746434",
            "extra": "mean: 4.295307673169329 msec\nrounds: 205"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_search_scaling[100K]",
            "value": 56.01027666598606,
            "unit": "iter/sec",
            "range": "stddev: 0.0011962522655147017",
            "extra": "mean: 17.85386646031835 msec\nrounds: 63"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_filter_scaling[100K]",
            "value": 109.30835804444696,
            "unit": "iter/sec",
            "range": "stddev: 0.0009803239197093614",
            "extra": "mean: 9.148431262624767 msec\nrounds: 99"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_search_scaling[10K]",
            "value": 62.667795683367515,
            "unit": "iter/sec",
            "range": "stddev: 0.0013814553776905257",
            "extra": "mean: 15.957159320754712 msec\nrounds: 53"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_pipeline_scaling[1K]",
            "value": 204.84023746046563,
            "unit": "iter/sec",
            "range": "stddev: 0.00023383511553820953",
            "extra": "mean: 4.881853352630491 msec\nrounds: 190"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_fp_http_paginate_scaling[10K]",
            "value": 211.42089873217236,
            "unit": "iter/sec",
            "range": "stddev: 0.00017676452610492708",
            "extra": "mean: 4.729901376811374 msec\nrounds: 138"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_filter_scaling[100K]",
            "value": 50.79605938093277,
            "unit": "iter/sec",
            "range": "stddev: 0.0009052574555879008",
            "extra": "mean: 19.686566481481208 msec\nrounds: 54"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_search_scaling[100K]",
            "value": 9.083765626795923,
            "unit": "iter/sec",
            "range": "stddev: 0.001956237157247193",
            "extra": "mean: 110.08650388888617 msec\nrounds: 9"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_sort_scaling[1K]",
            "value": 209.20791541792335,
            "unit": "iter/sec",
            "range": "stddev: 0.0002996598488794881",
            "extra": "mean: 4.779933866280126 msec\nrounds: 172"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_fp_http_paginate_scaling[1K]",
            "value": 204.95757262631665,
            "unit": "iter/sec",
            "range": "stddev: 0.00012669796516874592",
            "extra": "mean: 4.87905856410206 msec\nrounds: 195"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_pipeline_scaling[100K]",
            "value": 23.74176234668798,
            "unit": "iter/sec",
            "range": "stddev: 0.001659523713466033",
            "extra": "mean: 42.1198723749967 msec\nrounds: 24"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_filter_scaling[1K]",
            "value": 169.88366910786445,
            "unit": "iter/sec",
            "range": "stddev: 0.015979608973737135",
            "extra": "mean: 5.886380987951635 msec\nrounds: 166"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_search_scaling[1K]",
            "value": 208.29183515528246,
            "unit": "iter/sec",
            "range": "stddev: 0.0002057916929906791",
            "extra": "mean: 4.8009563085105835 msec\nrounds: 188"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_paginate_scaling[100K]",
            "value": 210.02491937585665,
            "unit": "iter/sec",
            "range": "stddev: 0.00018586079255644125",
            "extra": "mean: 4.761339763737363 msec\nrounds: 182"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_paginate_scaling[10K]",
            "value": 201.71295692750954,
            "unit": "iter/sec",
            "range": "stddev: 0.00017269192099419998",
            "extra": "mean: 4.957539739796558 msec\nrounds: 196"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_pipeline_scaling[100K]",
            "value": 50.47955251053604,
            "unit": "iter/sec",
            "range": "stddev: 0.001395766737932785",
            "extra": "mean: 19.81000128302011 msec\nrounds: 53"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_search_scaling[10K]",
            "value": 152.08052662206137,
            "unit": "iter/sec",
            "range": "stddev: 0.0003537762288085017",
            "extra": "mean: 6.575463816515588 msec\nrounds: 109"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_paginate_scaling[100K]",
            "value": 193.97542952911098,
            "unit": "iter/sec",
            "range": "stddev: 0.00020962761384242819",
            "extra": "mean: 5.155292102858441 msec\nrounds: 175"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_paginate_scaling[1K]",
            "value": 192.8721851163025,
            "unit": "iter/sec",
            "range": "stddev: 0.00023270187472254454",
            "extra": "mean: 5.184780788359903 msec\nrounds: 189"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_fp_http_paginate_scaling[100K]",
            "value": 177.11156900735475,
            "unit": "iter/sec",
            "range": "stddev: 0.0008097528667034635",
            "extra": "mean: 5.646158551949105 msec\nrounds: 154"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_sort_scaling[10K]",
            "value": 148.3612375512632,
            "unit": "iter/sec",
            "range": "stddev: 0.0008364990875994313",
            "extra": "mean: 6.740305058822863 msec\nrounds: 136"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_filter_scaling[10K]",
            "value": 174.5064810660948,
            "unit": "iter/sec",
            "range": "stddev: 0.000405728720798739",
            "extra": "mean: 5.730446192547126 msec\nrounds: 161"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_pipeline_scaling[10K]",
            "value": 155.8758785693318,
            "unit": "iter/sec",
            "range": "stddev: 0.00042143880678699143",
            "extra": "mean: 6.415360793332828 msec\nrounds: 150"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_paginate_scaling[1K]",
            "value": 188.74513712969198,
            "unit": "iter/sec",
            "range": "stddev: 0.0002948868328096508",
            "extra": "mean: 5.298149744185846 msec\nrounds: 172"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_sort_scaling[10K]",
            "value": 127.00052412786845,
            "unit": "iter/sec",
            "range": "stddev: 0.0002799704300536343",
            "extra": "mean: 7.8739832521727715 msec\nrounds: 115"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_sort_scaling[100K]",
            "value": 30.440669441385875,
            "unit": "iter/sec",
            "range": "stddev: 0.001165933599160903",
            "extra": "mean: 32.850788709674084 msec\nrounds: 31"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_filter_scaling[10K]",
            "value": 142.788619675777,
            "unit": "iter/sec",
            "range": "stddev: 0.00044046702928034816",
            "extra": "mean: 7.003359247191059 msec\nrounds: 89"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_paginate_scaling[10K]",
            "value": 184.6988290879824,
            "unit": "iter/sec",
            "range": "stddev: 0.00017492612587384184",
            "extra": "mean: 5.414219488763753 msec\nrounds: 178"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_sort_scaling[1K]",
            "value": 163.9242925777874,
            "unit": "iter/sec",
            "range": "stddev: 0.0004402634101626295",
            "extra": "mean: 6.100377096490854 msec\nrounds: 114"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_sort_scaling[100K]",
            "value": 50.769731339555555,
            "unit": "iter/sec",
            "range": "stddev: 0.0018136517367803966",
            "extra": "mean: 19.696775492307623 msec\nrounds: 65"
          },
          {
            "name": "tests/perf/test_comparison.py::test_sa_sync_paginate_10k",
            "value": 2395.35305606007,
            "unit": "iter/sec",
            "range": "stddev: 0.000025838167455746344",
            "extra": "mean: 417.4749928700792 usec\nrounds: 561"
          },
          {
            "name": "tests/perf/test_comparison.py::test_memory_sort_10k",
            "value": 431.65262134115693,
            "unit": "iter/sec",
            "range": "stddev: 0.00008770449219391872",
            "extra": "mean: 2.3166776953490325 msec\nrounds: 430"
          },
          {
            "name": "tests/perf/test_comparison.py::test_memory_pipeline_10k",
            "value": 295.32058058853613,
            "unit": "iter/sec",
            "range": "stddev: 0.00003523582481728333",
            "extra": "mean: 3.3861507315444386 msec\nrounds: 298"
          },
          {
            "name": "tests/perf/test_comparison.py::test_sa_async_paginate_10k",
            "value": 815.1263603737124,
            "unit": "iter/sec",
            "range": "stddev: 0.00009586964408536908",
            "extra": "mean: 1.2268036572164447 msec\nrounds: 388"
          },
          {
            "name": "tests/perf/test_comparison.py::test_raw_pipeline_10k",
            "value": 1370.422114339594,
            "unit": "iter/sec",
            "range": "stddev: 0.000013555180977744323",
            "extra": "mean: 729.7021768230146 usec\nrounds: 1001"
          },
          {
            "name": "tests/perf/test_comparison.py::test_raw_list_slice_10k",
            "value": 5008087.240806791,
            "unit": "iter/sec",
            "range": "stddev: 3.7319493804479474e-8",
            "extra": "mean: 199.67703275017521 nsec\nrounds: 194591"
          },
          {
            "name": "tests/perf/test_comparison.py::test_memory_paginate_10k",
            "value": 597020.6359927402,
            "unit": "iter/sec",
            "range": "stddev: 4.0492091389049996e-7",
            "extra": "mean: 1.6749839782961207 usec\nrounds: 59981"
          },
          {
            "name": "tests/perf/test_comparison.py::test_raw_list_sort_10k",
            "value": 1563.7568724636521,
            "unit": "iter/sec",
            "range": "stddev: 0.000013260707588804754",
            "extra": "mean: 639.4855988223603 usec\nrounds: 1189"
          },
          {
            "name": "tests/perf/test_comparison.py::test_raw_list_search_10k",
            "value": 1817.303939030608,
            "unit": "iter/sec",
            "range": "stddev: 0.00001022386688592498",
            "extra": "mean: 550.2656867257016 usec\nrounds: 1695"
          },
          {
            "name": "tests/perf/test_comparison.py::test_memory_search_10k",
            "value": 299.3798563068888,
            "unit": "iter/sec",
            "range": "stddev: 0.00005383745026020728",
            "extra": "mean: 3.34023809195405 msec\nrounds: 261"
          },
          {
            "name": "tests/perf/test_comparison.py::test_raw_list_filter_10k",
            "value": 3660.7700654634355,
            "unit": "iter/sec",
            "range": "stddev: 0.000007628228358131127",
            "extra": "mean: 273.16656936042904 usec\nrounds: 2970"
          },
          {
            "name": "tests/perf/test_comparison.py::test_memory_filter_10k",
            "value": 792.889774081105,
            "unit": "iter/sec",
            "range": "stddev: 0.000023443465841249777",
            "extra": "mean: 1.261209354300122 msec\nrounds: 779"
          },
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_memory_100k",
            "value": 596382.472918866,
            "unit": "iter/sec",
            "range": "stddev: 4.643976543673897e-7",
            "extra": "mean: 1.6767763061609016 usec\nrounds: 61535"
          },
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_memory_10k",
            "value": 593119.8928145593,
            "unit": "iter/sec",
            "range": "stddev: 5.598973850621521e-7",
            "extra": "mean: 1.6859997651649379 usec\nrounds: 132031"
          },
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_memory_1k",
            "value": 609708.1749319439,
            "unit": "iter/sec",
            "range": "stddev: 4.0108184884898353e-7",
            "extra": "mean: 1.6401289028339183 usec\nrounds: 107678"
          },
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_sa_sync_10k",
            "value": 2534.14273776619,
            "unit": "iter/sec",
            "range": "stddev: 0.0000352377961185856",
            "extra": "mean: 394.61076327590195 usec\nrounds: 1111"
          },
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_sa_async_10k",
            "value": 930.9665128757764,
            "unit": "iter/sec",
            "range": "stddev: 0.000034800575526633836",
            "extra": "mean: 1.0741524922426884 msec\nrounds: 709"
          },
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_sa_sync_1k",
            "value": 2609.9255611555704,
            "unit": "iter/sec",
            "range": "stddev: 0.000026711045871304638",
            "extra": "mean: 383.15269020823723 usec\nrounds: 623"
          },
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_sa_async_1k",
            "value": 848.9446599567915,
            "unit": "iter/sec",
            "range": "stddev: 0.00009842515076178976",
            "extra": "mean: 1.1779330822940763 msec\nrounds: 401"
          },
          {
            "name": "tests/perf/test_sorting.py::test_bench_sort_sa_sync_1k",
            "value": 47811.76653336972,
            "unit": "iter/sec",
            "range": "stddev: 0.000007183314676854144",
            "extra": "mean: 20.9153535312706 usec\nrounds: 7377"
          },
          {
            "name": "tests/perf/test_sorting.py::test_bench_sort_memory_100k",
            "value": 41.15533728120387,
            "unit": "iter/sec",
            "range": "stddev: 0.00017257153489949194",
            "extra": "mean: 24.298185024393224 msec\nrounds: 41"
          },
          {
            "name": "tests/perf/test_sorting.py::test_bench_sort_sa_sync_10k",
            "value": 49553.48989160484,
            "unit": "iter/sec",
            "range": "stddev: 0.000006323003252771594",
            "extra": "mean: 20.180213385322354 usec\nrounds: 7142"
          },
          {
            "name": "tests/perf/test_sorting.py::test_bench_sort_memory_10k",
            "value": 452.4659356557227,
            "unit": "iter/sec",
            "range": "stddev: 0.000023684242863042284",
            "extra": "mean: 2.210111129251708 msec\nrounds: 441"
          },
          {
            "name": "tests/perf/test_sorting.py::test_bench_sort_sa_async_10k",
            "value": 50616.65787135422,
            "unit": "iter/sec",
            "range": "stddev: 0.0000062057207234813905",
            "extra": "mean: 19.756341924857427 usec\nrounds: 14278"
          },
          {
            "name": "tests/perf/test_sorting.py::test_bench_sort_sa_async_1k",
            "value": 50234.069376691055,
            "unit": "iter/sec",
            "range": "stddev: 0.000006192546022380144",
            "extra": "mean: 19.906808514780742 usec\nrounds: 15197"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_python_full_pipeline",
            "value": 1409.33270877434,
            "unit": "iter/sec",
            "range": "stddev: 0.00001797133622353698",
            "extra": "mean: 709.5556597630334 usec\nrounds: 1014"
          },
          {
            "name": "tests/perf/test_competitors.py::test_fastapi_filter_10k",
            "value": 2554.6404623445137,
            "unit": "iter/sec",
            "range": "stddev: 0.000019342005928105407",
            "extra": "mean: 391.4445162597373 usec\nrounds: 738"
          },
          {
            "name": "tests/perf/test_competitors.py::test_paginate_lib_memory",
            "value": 378814.9863047573,
            "unit": "iter/sec",
            "range": "stddev: 0.000008919706839249653",
            "extra": "mean: 2.6398110849698493 usec\nrounds: 73938"
          },
          {
            "name": "tests/perf/test_competitors.py::test_paginate_lib_100k",
            "value": 372625.0054180136,
            "unit": "iter/sec",
            "range": "stddev: 0.000009365843940279745",
            "extra": "mean: 2.683663161247572 usec\nrounds: 117151"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_sqlalchemy",
            "value": 2239.793002781588,
            "unit": "iter/sec",
            "range": "stddev: 0.000019132074096577743",
            "extra": "mean: 446.46982947000237 usec\nrounds: 604"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_sa_filter",
            "value": 916.6804838715778,
            "unit": "iter/sec",
            "range": "stddev: 0.00003418130702503312",
            "extra": "mean: 1.0908926475411849 msec\nrounds: 366"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_python_100k",
            "value": 4281975.080894349,
            "unit": "iter/sec",
            "range": "stddev: 3.612460535364239e-8",
            "extra": "mean: 233.5370900362843 nsec\nrounds: 162576"
          },
          {
            "name": "tests/perf/test_competitors.py::test_fastapi_pagination_full_pipeline",
            "value": 1262.109225286971,
            "unit": "iter/sec",
            "range": "stddev: 0.00002422154510569589",
            "extra": "mean: 792.3244517705081 usec\nrounds: 819"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_sa_sync",
            "value": 2509.236111071622,
            "unit": "iter/sec",
            "range": "stddev: 0.00001647365094060233",
            "extra": "mean: 398.5276617005679 usec\nrounds: 1141"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_sa_filter",
            "value": 942.1696856819217,
            "unit": "iter/sec",
            "range": "stddev: 0.00005628685028309227",
            "extra": "mean: 1.0613799352674163 msec\nrounds: 448"
          },
          {
            "name": "tests/perf/test_competitors.py::test_fastapi_pagination_memory",
            "value": 17755.939203859572,
            "unit": "iter/sec",
            "range": "stddev: 0.000005234383209013387",
            "extra": "mean: 56.3191835992901 usec\nrounds: 4951"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_python_sort_paginate",
            "value": 1602.0824628958385,
            "unit": "iter/sec",
            "range": "stddev: 0.00001288774546956661",
            "extra": "mean: 624.1875953079552 usec\nrounds: 1364"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_search_paginate",
            "value": 242.31304583324962,
            "unit": "iter/sec",
            "range": "stddev: 0.00006562658278900026",
            "extra": "mean: 4.126892947762131 msec\nrounds: 268"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_python_filter_paginate",
            "value": 3603.702792688396,
            "unit": "iter/sec",
            "range": "stddev: 0.000008869688061613895",
            "extra": "mean: 277.4923620307741 usec\nrounds: 2718"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_full_pipeline",
            "value": 294.54525447627645,
            "unit": "iter/sec",
            "range": "stddev: 0.00003842208468038634",
            "extra": "mean: 3.3950640344828336 msec\nrounds: 319"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_python_slice",
            "value": 4851234.478221273,
            "unit": "iter/sec",
            "range": "stddev: 3.149700950690713e-8",
            "extra": "mean: 206.13309962430222 nsec\nrounds: 179212"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_filter_paginate",
            "value": 684.1143014524365,
            "unit": "iter/sec",
            "range": "stddev: 0.00008081749429476",
            "extra": "mean: 1.4617440358678508 msec\nrounds: 697"
          },
          {
            "name": "tests/perf/test_competitors.py::test_fastapi_pagination_100k",
            "value": 17658.655019365047,
            "unit": "iter/sec",
            "range": "stddev: 0.000005324632266998067",
            "extra": "mean: 56.62945444618335 usec\nrounds: 5499"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_python_search_paginate",
            "value": 1837.2791167757532,
            "unit": "iter/sec",
            "range": "stddev: 0.000008956870780043063",
            "extra": "mean: 544.2831145628559 usec\nrounds: 1545"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_memory",
            "value": 595303.5707696027,
            "unit": "iter/sec",
            "range": "stddev: 4.4681517195582393e-7",
            "extra": "mean: 1.6798152221852285 usec\nrounds: 57101"
          },
          {
            "name": "tests/perf/test_competitors.py::test_sqlalchemy_pagination_lib_10k",
            "value": 1771.0244036776496,
            "unit": "iter/sec",
            "range": "stddev: 0.000026418488969617502",
            "extra": "mean: 564.6449579821902 usec\nrounds: 357"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_100k",
            "value": 573513.3974745147,
            "unit": "iter/sec",
            "range": "stddev: 4.3380559068118547e-7",
            "extra": "mean: 1.7436384300759724 usec\nrounds: 69508"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_sort_paginate",
            "value": 404.1507148898371,
            "unit": "iter/sec",
            "range": "stddev: 0.000023243389929024258",
            "extra": "mean: 2.474324461538015 msec\nrounds: 416"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_sa_async",
            "value": 848.770645360947,
            "unit": "iter/sec",
            "range": "stddev: 0.00010651912458030073",
            "extra": "mean: 1.178174581632405 msec\nrounds: 588"
          },
          {
            "name": "tests/perf/test_competitors.py::test_paginate_lib_full_pipeline",
            "value": 1299.359825997018,
            "unit": "iter/sec",
            "range": "stddev: 0.0007611939154011297",
            "extra": "mean: 769.6097570453089 usec\nrounds: 1029"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_sa_async_1k",
            "value": 27206.149160639772,
            "unit": "iter/sec",
            "range": "stddev: 0.000003512350862569173",
            "extra": "mean: 36.75639628730479 usec\nrounds: 4633"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_sa_sync_1k",
            "value": 27925.614654453886,
            "unit": "iter/sec",
            "range": "stddev: 0.000003915687371972889",
            "extra": "mean: 35.80941771108014 usec\nrounds: 10852"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_memory_10k_multi",
            "value": 259.0748338441062,
            "unit": "iter/sec",
            "range": "stddev: 0.00008624987564493592",
            "extra": "mean: 3.859888608870951 msec\nrounds: 248"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_sa_sync_10k",
            "value": 27727.98293874226,
            "unit": "iter/sec",
            "range": "stddev: 0.0000035258175469810332",
            "extra": "mean: 36.0646500039054 usec\nrounds: 12863"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_sa_async_10k",
            "value": 27453.474106127887,
            "unit": "iter/sec",
            "range": "stddev: 0.0000034320159939644375",
            "extra": "mean: 36.42526246894159 usec\nrounds: 11308"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_memory_10k_single",
            "value": 788.0930957875427,
            "unit": "iter/sec",
            "range": "stddev: 0.000018067065176853747",
            "extra": "mean: 1.2688856244841207 msec\nrounds: 727"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_memory_100k",
            "value": 76.08864361529751,
            "unit": "iter/sec",
            "range": "stddev: 0.00015315745201629151",
            "extra": "mean: 13.142565729729363 msec\nrounds: 74"
          },
          {
            "name": "tests/perf/test_search.py::test_bench_search_sa_sync_10k",
            "value": 26488.976911939502,
            "unit": "iter/sec",
            "range": "stddev: 0.0000039588125367484975",
            "extra": "mean: 37.75155240326648 usec\nrounds: 5534"
          },
          {
            "name": "tests/perf/test_search.py::test_bench_search_memory_100k",
            "value": 24.861478844122335,
            "unit": "iter/sec",
            "range": "stddev: 0.0005632824478159234",
            "extra": "mean: 40.222868730772085 msec\nrounds: 26"
          },
          {
            "name": "tests/perf/test_search.py::test_bench_search_sa_async_10k",
            "value": 26697.857910373375,
            "unit": "iter/sec",
            "range": "stddev: 0.000004064613101380234",
            "extra": "mean: 37.45618855853798 usec\nrounds: 5314"
          },
          {
            "name": "tests/perf/test_search.py::test_bench_search_sa_async_1k",
            "value": 26842.247853832763,
            "unit": "iter/sec",
            "range": "stddev: 0.0000038510684088197644",
            "extra": "mean: 37.25470405628534 usec\nrounds: 12080"
          },
          {
            "name": "tests/perf/test_search.py::test_bench_search_sa_sync_1k",
            "value": 26299.63674043439,
            "unit": "iter/sec",
            "range": "stddev: 0.000005003583868457878",
            "extra": "mean: 38.02333887230273 usec\nrounds: 10411"
          },
          {
            "name": "tests/perf/test_search.py::test_bench_search_memory_10k",
            "value": 296.5904210936915,
            "unit": "iter/sec",
            "range": "stddev: 0.00006853070817575249",
            "extra": "mean: 3.371653057143423 msec\nrounds: 280"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_sort_scaling[100K]",
            "value": 25.18122453893841,
            "unit": "iter/sec",
            "range": "stddev: 0.0003192145081991595",
            "extra": "mean: 39.71212751999701 msec\nrounds: 25"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_sort_scaling[1K]",
            "value": 4037.469167824556,
            "unit": "iter/sec",
            "range": "stddev: 0.000007904500634099061",
            "extra": "mean: 247.67990997162556 usec\nrounds: 3510"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_paginate_scaling[500K]",
            "value": 597735.5805367043,
            "unit": "iter/sec",
            "range": "stddev: 4.781230879917415e-7",
            "extra": "mean: 1.6729805495301187 usec\nrounds: 38508"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_sort_scaling[500K]",
            "value": 6.986917961185687,
            "unit": "iter/sec",
            "range": "stddev: 0.0008860166302060785",
            "extra": "mean: 143.12462312500074 msec\nrounds: 8"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_search_scaling[1M]",
            "value": 2.4512744105063384,
            "unit": "iter/sec",
            "range": "stddev: 0.0021095962669426343",
            "extra": "mean: 407.95106240000223 msec\nrounds: 5"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_filter_scaling[1M]",
            "value": 7.599409204069921,
            "unit": "iter/sec",
            "range": "stddev: 0.0007830967196739995",
            "extra": "mean: 131.58917662499903 msec\nrounds: 8"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_paginate_scaling[10K]",
            "value": 2491.3733648242405,
            "unit": "iter/sec",
            "range": "stddev: 0.00002594346993053119",
            "extra": "mean: 401.38504092522766 usec\nrounds: 562"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_pipeline_scaling[100K]",
            "value": 69.63341288625907,
            "unit": "iter/sec",
            "range": "stddev: 0.00031049774215025306",
            "extra": "mean: 14.360921841263542 msec\nrounds: 63"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_paginate_scaling[1K]",
            "value": 921.0044627799548,
            "unit": "iter/sec",
            "range": "stddev: 0.0000592241408524709",
            "extra": "mean: 1.085771068884515 msec\nrounds: 421"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_filter_scaling[10K]",
            "value": 548.9427768166255,
            "unit": "iter/sec",
            "range": "stddev: 0.00012166070674022503",
            "extra": "mean: 1.821683501874459 msec\nrounds: 267"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_paginate_scaling[10K]",
            "value": 605842.652960094,
            "unit": "iter/sec",
            "range": "stddev: 4.201095254907491e-7",
            "extra": "mean: 1.6505935907848148 usec\nrounds: 57137"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_search_scaling[10K]",
            "value": 261.60242104456006,
            "unit": "iter/sec",
            "range": "stddev: 0.0003294415464125913",
            "extra": "mean: 3.822594592233017 msec\nrounds: 206"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_pipeline_scaling[1K]",
            "value": 2989.0163160886386,
            "unit": "iter/sec",
            "range": "stddev: 0.00001272858876529941",
            "extra": "mean: 334.5582272727699 usec\nrounds: 2684"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_paginate_scaling[100K]",
            "value": 2252.7324586932664,
            "unit": "iter/sec",
            "range": "stddev: 0.00002807957335029793",
            "extra": "mean: 443.9053542026318 usec\nrounds: 559"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_sort_scaling[10K]",
            "value": 407.6253027816321,
            "unit": "iter/sec",
            "range": "stddev: 0.000030357056008510137",
            "extra": "mean: 2.4532333816767684 msec\nrounds: 393"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_filter_scaling[10K]",
            "value": 960.3802018924788,
            "unit": "iter/sec",
            "range": "stddev: 0.00003355221821048829",
            "extra": "mean: 1.041254284531739 msec\nrounds: 362"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_filter_scaling[100K]",
            "value": 68.00239488530718,
            "unit": "iter/sec",
            "range": "stddev: 0.0004458402915812021",
            "extra": "mean: 14.705364446158105 msec\nrounds: 65"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_sort_scaling[100K]",
            "value": 24.8376986789248,
            "unit": "iter/sec",
            "range": "stddev: 0.00023553229901135552",
            "extra": "mean: 40.261379000000375 msec\nrounds: 24"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_pipeline_scaling[500K]",
            "value": 5.1886854974040855,
            "unit": "iter/sec",
            "range": "stddev: 0.0012725920522733036",
            "extra": "mean: 192.72704050000775 msec\nrounds: 6"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_search_scaling[100K]",
            "value": 23.686495124003052,
            "unit": "iter/sec",
            "range": "stddev: 0.0005768633937904344",
            "extra": "mean: 42.21814982608531 msec\nrounds: 23"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_sort_scaling[1K]",
            "value": 648.3640762286099,
            "unit": "iter/sec",
            "range": "stddev: 0.00007652421716387126",
            "extra": "mean: 1.5423433170708323 msec\nrounds: 287"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_pipeline_scaling[10K]",
            "value": 284.39761454521744,
            "unit": "iter/sec",
            "range": "stddev: 0.00031528254743674346",
            "extra": "mean: 3.516203895026012 msec\nrounds: 181"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_search_scaling[100K]",
            "value": 62.34624823969817,
            "unit": "iter/sec",
            "range": "stddev: 0.0001366495188958594",
            "extra": "mean: 16.039457517240997 msec\nrounds: 58"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_filter_scaling[1K]",
            "value": 7669.25225257406,
            "unit": "iter/sec",
            "range": "stddev: 0.0000057085218767195585",
            "extra": "mean: 130.39080826483 usec\nrounds: 6921"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_search_scaling[1K]",
            "value": 3981.532794260828,
            "unit": "iter/sec",
            "range": "stddev: 0.000008135512253214135",
            "extra": "mean: 251.1595537882918 usec\nrounds: 2640"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_pipeline_scaling[10K]",
            "value": 519.3262946549684,
            "unit": "iter/sec",
            "range": "stddev: 0.00004471646799351137",
            "extra": "mean: 1.9255716690878961 msec\nrounds: 275"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_filter_scaling[100K]",
            "value": 162.59921279042305,
            "unit": "iter/sec",
            "range": "stddev: 0.0001439883518070027",
            "extra": "mean: 6.150091275588875 msec\nrounds: 127"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_sort_scaling[1M]",
            "value": 3.3856016647581693,
            "unit": "iter/sec",
            "range": "stddev: 0.0011756363157815813",
            "extra": "mean: 295.3684748000114 msec\nrounds: 5"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_pipeline_scaling[1K]",
            "value": 1366.6304668103558,
            "unit": "iter/sec",
            "range": "stddev: 0.00005177015319175091",
            "extra": "mean: 731.7266988302608 usec\nrounds: 342"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_sort_scaling[10K]",
            "value": 280.6186157540081,
            "unit": "iter/sec",
            "range": "stddev: 0.00011372055219530524",
            "extra": "mean: 3.563555458760461 msec\nrounds: 194"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_pipeline_scaling[1M]",
            "value": 2.5676517949434396,
            "unit": "iter/sec",
            "range": "stddev: 0.0016580953578870744",
            "extra": "mean: 389.46090819998744 msec\nrounds: 5"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_sort_scaling[1K]",
            "value": 1291.4434573151966,
            "unit": "iter/sec",
            "range": "stddev: 0.00003390279404611873",
            "extra": "mean: 774.3273577605299 usec\nrounds: 464"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_filter_scaling[1K]",
            "value": 734.8185966952975,
            "unit": "iter/sec",
            "range": "stddev: 0.00009658790020925102",
            "extra": "mean: 1.360880092715813 msec\nrounds: 302"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_search_scaling[1K]",
            "value": 655.0555202651457,
            "unit": "iter/sec",
            "range": "stddev: 0.00009720786467647047",
            "extra": "mean: 1.5265881578942069 msec\nrounds: 285"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_paginate_scaling[1K]",
            "value": 606202.2775686459,
            "unit": "iter/sec",
            "range": "stddev: 4.195805843623623e-7",
            "extra": "mean: 1.649614389458906 usec\nrounds: 92679"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_paginate_scaling[100K]",
            "value": 881.2277895353743,
            "unit": "iter/sec",
            "range": "stddev: 0.00003826800292926946",
            "extra": "mean: 1.1347803733325843 msec\nrounds: 375"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_filter_scaling[100K]",
            "value": 142.7382358251047,
            "unit": "iter/sec",
            "range": "stddev: 0.0002443507010550453",
            "extra": "mean: 7.005831298246441 msec\nrounds: 114"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_pipeline_scaling[100K]",
            "value": 66.88672769107276,
            "unit": "iter/sec",
            "range": "stddev: 0.0006468867294836009",
            "extra": "mean: 14.950649172413735 msec\nrounds: 58"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_paginate_scaling[10K]",
            "value": 900.3093294475385,
            "unit": "iter/sec",
            "range": "stddev: 0.0001003074322970739",
            "extra": "mean: 1.1107293541139192 msec\nrounds: 401"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_search_scaling[100K]",
            "value": 58.761872460918845,
            "unit": "iter/sec",
            "range": "stddev: 0.000327986630553317",
            "extra": "mean: 17.017837555552312 msec\nrounds: 54"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_pipeline_scaling[1K]",
            "value": 687.7708539916576,
            "unit": "iter/sec",
            "range": "stddev: 0.00005537582925236146",
            "extra": "mean: 1.453972633757652 msec\nrounds: 314"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_filter_scaling[1K]",
            "value": 1743.3664655876016,
            "unit": "iter/sec",
            "range": "stddev: 0.00003179663139437291",
            "extra": "mean: 573.602865340736 usec\nrounds: 453"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_search_scaling[1K]",
            "value": 1361.956461892534,
            "unit": "iter/sec",
            "range": "stddev: 0.000034513935130945294",
            "extra": "mean: 734.2378614735085 usec\nrounds: 462"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_filter_scaling[500K]",
            "value": 14.143381471489798,
            "unit": "iter/sec",
            "range": "stddev: 0.0017567032061166121",
            "extra": "mean: 70.70444942857534 msec\nrounds: 14"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_search_scaling[500K]",
            "value": 4.835919855534198,
            "unit": "iter/sec",
            "range": "stddev: 0.0021592038370637184",
            "extra": "mean: 206.785891800007 msec\nrounds: 5"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_pipeline_scaling[100K]",
            "value": 23.592862445167512,
            "unit": "iter/sec",
            "range": "stddev: 0.0016531943611887397",
            "extra": "mean: 42.38570043478673 msec\nrounds: 23"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_search_scaling[10K]",
            "value": 480.1175104451874,
            "unit": "iter/sec",
            "range": "stddev: 0.00004462662845881613",
            "extra": "mean: 2.0828234301905657 msec\nrounds: 265"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_paginate_scaling[1M]",
            "value": 527636.4088987755,
            "unit": "iter/sec",
            "range": "stddev: 0.0000011089853319739656",
            "extra": "mean: 1.8952444962755501 usec\nrounds: 38884"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_paginate_scaling[1K]",
            "value": 2598.432927288893,
            "unit": "iter/sec",
            "range": "stddev: 0.00002399365701426107",
            "extra": "mean: 384.84733990935155 usec\nrounds: 659"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_sort_scaling[10K]",
            "value": 240.5952091752006,
            "unit": "iter/sec",
            "range": "stddev: 0.00009670981334862425",
            "extra": "mean: 4.156358738098577 msec\nrounds: 168"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_pipeline_scaling[10K]",
            "value": 385.61903511025344,
            "unit": "iter/sec",
            "range": "stddev: 0.00006207317259882293",
            "extra": "mean: 2.593232981131461 msec\nrounds: 212"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_search_scaling[10K]",
            "value": 335.94293216491786,
            "unit": "iter/sec",
            "range": "stddev: 0.00007029424134532911",
            "extra": "mean: 2.9766960523791868 msec\nrounds: 210"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_filter_scaling[10K]",
            "value": 746.9463395721205,
            "unit": "iter/sec",
            "range": "stddev: 0.000028718267619334972",
            "extra": "mean: 1.338784256674768 msec\nrounds: 487"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_sort_scaling[100K]",
            "value": 33.966978366471906,
            "unit": "iter/sec",
            "range": "stddev: 0.0013811014840652283",
            "extra": "mean: 29.440357903224005 msec\nrounds: 31"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_paginate_scaling[100K]",
            "value": 593819.7018824918,
            "unit": "iter/sec",
            "range": "stddev: 8.911176355981019e-7",
            "extra": "mean: 1.6840128355961574 usec\nrounds: 39422"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_sa_pagination_lib_scaling[100K]",
            "value": 1622.02761106743,
            "unit": "iter/sec",
            "range": "stddev: 0.00002339914827352907",
            "extra": "mean: 616.5123165455342 usec\nrounds: 417"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_fastapi_filter_scaling[100K]",
            "value": 2537.5841468090052,
            "unit": "iter/sec",
            "range": "stddev: 0.000015584446203956134",
            "extra": "mean: 394.0756018898893 usec\nrounds: 741"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_sort_scaling[100K]",
            "value": 158.64235824467562,
            "unit": "iter/sec",
            "range": "stddev: 0.00027742320585809576",
            "extra": "mean: 6.303486729929282 msec\nrounds: 137"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_paginate_scaling[1K]",
            "value": 747.8165186547719,
            "unit": "iter/sec",
            "range": "stddev: 0.000033176015759718694",
            "extra": "mean: 1.3372264118996389 msec\nrounds: 437"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_pipeline_scaling[10K]",
            "value": 537.9959521884256,
            "unit": "iter/sec",
            "range": "stddev: 0.00003979304059417664",
            "extra": "mean: 1.858750044367925 msec\nrounds: 293"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_paginate_scaling[1K]",
            "value": 2345.797957281597,
            "unit": "iter/sec",
            "range": "stddev: 0.000014585079213200154",
            "extra": "mean: 426.29417290431917 usec\nrounds: 775"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_filter_scaling[10K]",
            "value": 472.8243094087837,
            "unit": "iter/sec",
            "range": "stddev: 0.00011474064526824466",
            "extra": "mean: 2.114950479704382 msec\nrounds: 271"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_paginate_scaling[10K]",
            "value": 2231.913616600395,
            "unit": "iter/sec",
            "range": "stddev: 0.00001720462398033012",
            "extra": "mean: 448.0460142194837 usec\nrounds: 633"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_filter_scaling[10K]",
            "value": 922.9365881612322,
            "unit": "iter/sec",
            "range": "stddev: 0.00002757223059841781",
            "extra": "mean: 1.0834980569925192 msec\nrounds: 386"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_fastapi_filter_scaling[1K]",
            "value": 2553.6249027701583,
            "unit": "iter/sec",
            "range": "stddev: 0.0000159769857219457",
            "extra": "mean: 391.60019113034394 usec\nrounds: 947"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_fp_sa_paginate_scaling[100K]",
            "value": 1416.566815082385,
            "unit": "iter/sec",
            "range": "stddev: 0.000028756067893800262",
            "extra": "mean: 705.9321094867254 usec\nrounds: 274"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_sort_scaling[100K]",
            "value": 184.04825413460154,
            "unit": "iter/sec",
            "range": "stddev: 0.00009369296788473439",
            "extra": "mean: 5.433357706662415 msec\nrounds: 150"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_pipeline_scaling[1K]",
            "value": 1383.858923045868,
            "unit": "iter/sec",
            "range": "stddev: 0.000026375211328806282",
            "extra": "mean: 722.6170119993185 usec\nrounds: 500"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_pipeline_scaling[100K]",
            "value": 71.17596815965845,
            "unit": "iter/sec",
            "range": "stddev: 0.0004512206150848143",
            "extra": "mean: 14.049685952382816 msec\nrounds: 63"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_fp_sa_paginate_scaling[10K]",
            "value": 1544.241000574287,
            "unit": "iter/sec",
            "range": "stddev: 0.00002467398777449519",
            "extra": "mean: 647.5673160006181 usec\nrounds: 500"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_search_scaling[100K]",
            "value": 141.32252087544933,
            "unit": "iter/sec",
            "range": "stddev: 0.0001648674617704914",
            "extra": "mean: 7.0760130360349445 msec\nrounds: 111"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_filter_scaling[100K]",
            "value": 181.56110927109742,
            "unit": "iter/sec",
            "range": "stddev: 0.00008470235877267662",
            "extra": "mean: 5.507787455224528 msec\nrounds: 134"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_sort_scaling[10K]",
            "value": 1150.296029811281,
            "unit": "iter/sec",
            "range": "stddev: 0.000020086389475934",
            "extra": "mean: 869.3414339298914 usec\nrounds: 613"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_search_scaling[10K]",
            "value": 808.2417235150275,
            "unit": "iter/sec",
            "range": "stddev: 0.00003349621517593085",
            "extra": "mean: 1.2372536221602364 msec\nrounds: 352"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_filter_scaling[100K]",
            "value": 153.20847618053867,
            "unit": "iter/sec",
            "range": "stddev: 0.00018004896150584652",
            "extra": "mean: 6.527054017700785 msec\nrounds: 113"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_paginate_scaling[100K]",
            "value": 696.952623848479,
            "unit": "iter/sec",
            "range": "stddev: 0.00011327919447357163",
            "extra": "mean: 1.4348177563033395 msec\nrounds: 357"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_pipeline_scaling[10K]",
            "value": 360.8755407570596,
            "unit": "iter/sec",
            "range": "stddev: 0.000114374431579909",
            "extra": "mean: 2.771038452487411 msec\nrounds: 221"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_search_scaling[100K]",
            "value": 118.14291127599495,
            "unit": "iter/sec",
            "range": "stddev: 0.0002234436418284298",
            "extra": "mean: 8.46432502127774 msec\nrounds: 94"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_filter_scaling[1K]",
            "value": 632.8375393229406,
            "unit": "iter/sec",
            "range": "stddev: 0.0000928506561883594",
            "extra": "mean: 1.5801843883500948 msec\nrounds: 309"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_search_scaling[1K]",
            "value": 598.0083425412498,
            "unit": "iter/sec",
            "range": "stddev: 0.00012483939648765644",
            "extra": "mean: 1.6722174740079336 msec\nrounds: 327"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_fastapi_filter_scaling[10K]",
            "value": 2573.3994587972443,
            "unit": "iter/sec",
            "range": "stddev: 0.000014613927110355272",
            "extra": "mean: 388.59105086910216 usec\nrounds: 806"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_pipeline_scaling[1K]",
            "value": 599.8147792026739,
            "unit": "iter/sec",
            "range": "stddev: 0.00012162728637694598",
            "extra": "mean: 1.6671813277580243 msec\nrounds: 299"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_filter_scaling[1K]",
            "value": 1663.4119952551796,
            "unit": "iter/sec",
            "range": "stddev: 0.000030045075178785226",
            "extra": "mean: 601.1739742483898 usec\nrounds: 466"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_search_scaling[1K]",
            "value": 1582.4590563311929,
            "unit": "iter/sec",
            "range": "stddev: 0.000029100399546327277",
            "extra": "mean: 631.9278821143224 usec\nrounds: 492"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_search_scaling[10K]",
            "value": 446.74528902284584,
            "unit": "iter/sec",
            "range": "stddev: 0.00014736325335935953",
            "extra": "mean: 2.2384119644266947 msec\nrounds: 253"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_sa_pagination_lib_scaling[1K]",
            "value": 1750.6380581597502,
            "unit": "iter/sec",
            "range": "stddev: 0.000034846914958164766",
            "extra": "mean: 571.2203018430823 usec\nrounds: 434"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_pipeline_scaling[100K]",
            "value": 76.00375341545518,
            "unit": "iter/sec",
            "range": "stddev: 0.0003353154777856791",
            "extra": "mean: 13.157244939388116 msec\nrounds: 66"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_fp_sa_paginate_scaling[1K]",
            "value": 1579.3333100841378,
            "unit": "iter/sec",
            "range": "stddev: 0.000017405658977441005",
            "extra": "mean: 633.1785656738449 usec\nrounds: 571"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_sort_scaling[1K]",
            "value": 1045.0152737637225,
            "unit": "iter/sec",
            "range": "stddev: 0.00002690131646973909",
            "extra": "mean: 956.9238126045799 usec\nrounds: 603"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_sort_scaling[1K]",
            "value": 2549.42016826375,
            "unit": "iter/sec",
            "range": "stddev: 0.000016421333457720455",
            "extra": "mean: 392.24605361188355 usec\nrounds: 914"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_sa_pagination_lib_scaling[10K]",
            "value": 1785.0197429297011,
            "unit": "iter/sec",
            "range": "stddev: 0.000022069957589471468",
            "extra": "mean: 560.2178933655541 usec\nrounds: 422"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_paginate_scaling[100K]",
            "value": 2082.309602109935,
            "unit": "iter/sec",
            "range": "stddev: 0.00001686641634288002",
            "extra": "mean: 480.23598363410196 usec\nrounds: 611"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_sort_scaling[10K]",
            "value": 654.2195846547697,
            "unit": "iter/sec",
            "range": "stddev: 0.0000651769065722901",
            "extra": "mean: 1.5285387711645744 msec\nrounds: 437"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_paginate_scaling[10K]",
            "value": 700.6057982653814,
            "unit": "iter/sec",
            "range": "stddev: 0.0001400706083040179",
            "extra": "mean: 1.4273361746018716 msec\nrounds: 378"
          },
          {
            "name": "tests/perf/test_pipeline.py::test_bench_pipeline_sa_sync_1k",
            "value": 1305.352983166008,
            "unit": "iter/sec",
            "range": "stddev: 0.000028769787319692956",
            "extra": "mean: 766.0763126113186 usec\nrounds: 563"
          },
          {
            "name": "tests/perf/test_pipeline.py::test_bench_pipeline_memory_10k",
            "value": 297.72347220245183,
            "unit": "iter/sec",
            "range": "stddev: 0.00003722225502812807",
            "extra": "mean: 3.3588215017188854 msec\nrounds: 291"
          },
          {
            "name": "tests/perf/test_pipeline.py::test_bench_pipeline_sa_async_1k",
            "value": 615.1814798786048,
            "unit": "iter/sec",
            "range": "stddev: 0.00006643151917020291",
            "extra": "mean: 1.6255365818186405 msec\nrounds: 330"
          },
          {
            "name": "tests/perf/test_pipeline.py::test_bench_pipeline_memory_100k",
            "value": 30.263335994472847,
            "unit": "iter/sec",
            "range": "stddev: 0.00037795425728843573",
            "extra": "mean: 33.04328379999598 msec\nrounds: 30"
          },
          {
            "name": "tests/perf/test_pipeline.py::test_bench_pipeline_sa_async_10k",
            "value": 238.72331165797794,
            "unit": "iter/sec",
            "range": "stddev: 0.00009679120180788825",
            "extra": "mean: 4.188949931428202 msec\nrounds: 175"
          },
          {
            "name": "tests/perf/test_pipeline.py::test_bench_pipeline_sa_sync_10k",
            "value": 292.53583151031165,
            "unit": "iter/sec",
            "range": "stddev: 0.000049262976472685225",
            "extra": "mean: 3.4183846636399164 msec\nrounds: 220"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "git.owiwz@passinbox.com",
            "name": "CybLow"
          },
          "committer": {
            "email": "git.owiwz@passinbox.com",
            "name": "CybLow"
          },
          "distinct": true,
          "id": "744461fd113aa66fd42515e94f38e89b271943ce",
          "message": "feat: add unified CI status dashboard at /status/\n\n- Real-time pipeline visualization with concurrent stage grouping\n- Python x OS test matrix grids (unit + integration)\n- Specialized suite status (E2E, PostgreSQL, Property, Benchmarks)\n- Benchmark summary by category with ops/sec\n- Coverage badge + Codecov graph embed\n- Recent CI run history with commit links\n- Auto-refreshes every 30s when pipeline is running\n- Fetches live data from GitHub Actions API",
          "timestamp": "2026-03-17T04:31:42+01:00",
          "tree_id": "bf390799f351f6b739625fd5d524c9d3d5addfbe",
          "url": "https://github.com/CybLow/pypaginate/commit/744461fd113aa66fd42515e94f38e89b271943ce"
        },
        "date": 1773719095207,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_search_invalid_page",
            "value": 878.8086968761495,
            "unit": "iter/sec",
            "range": "stddev: 0.00008177321340335483",
            "extra": "mean: 1.137904078048661 msec\nrounds: 205"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_valid_offset_params",
            "value": 898151.7306437935,
            "unit": "iter/sec",
            "range": "stddev: 2.9742566311111714e-7",
            "extra": "mean: 1.1133976207819607 usec\nrounds: 67582"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_invalid_page",
            "value": 895.5259675832132,
            "unit": "iter/sec",
            "range": "stddev: 0.00008347485971351608",
            "extra": "mean: 1.1166622032175508 msec\nrounds: 497"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_invalid_params_caught",
            "value": 408388.0523221482,
            "unit": "iter/sec",
            "range": "stddev: 6.192168352935036e-7",
            "extra": "mean: 2.44865145861606 usec\nrounds: 18543"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_sort_invalid_limit",
            "value": 880.8906157583255,
            "unit": "iter/sec",
            "range": "stddev: 0.00007193808433296155",
            "extra": "mean: 1.1352147271306072 msec\nrounds: 634"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_valid_filter_request",
            "value": 489.4246305435441,
            "unit": "iter/sec",
            "range": "stddev: 0.00008092559670959253",
            "extra": "mean: 2.0432155179632505 msec\nrounds: 334"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_valid_search_request",
            "value": 342.86582316287286,
            "unit": "iter/sec",
            "range": "stddev: 0.003142849227335254",
            "extra": "mean: 2.916592825657535 msec\nrounds: 304"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_invalid_limit",
            "value": 806.5099041025036,
            "unit": "iter/sec",
            "range": "stddev: 0.0000820124400060553",
            "extra": "mean: 1.2399103779299712 msec\nrounds: 725"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_search_spec_many_fields",
            "value": 706451.6740674871,
            "unit": "iter/sec",
            "range": "stddev: 4.0444824849302193e-7",
            "extra": "mean: 1.4155249915997372 usec\nrounds: 59060"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_sort_spec_desc",
            "value": 1069759.04790057,
            "unit": "iter/sec",
            "range": "stddev: 2.807078155435656e-7",
            "extra": "mean: 934.789943550864 nsec\nrounds: 105286"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_valid_filter_spec",
            "value": 921029.072195797,
            "unit": "iter/sec",
            "range": "stddev: 2.9822906224987067e-7",
            "extra": "mean: 1.0857420576485506 usec\nrounds: 86341"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_invalid_filter_param",
            "value": 533.2329433443904,
            "unit": "iter/sec",
            "range": "stddev: 0.00013859452737462611",
            "extra": "mean: 1.8753530000005014 msec\nrounds: 400"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_valid_search_spec",
            "value": 701259.237011906,
            "unit": "iter/sec",
            "range": "stddev: 3.625487991790162e-7",
            "extra": "mean: 1.426006171784689 usec\nrounds: 72913"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_invalid_filter_operator",
            "value": 554448.3780832703,
            "unit": "iter/sec",
            "range": "stddev: 5.749517541363565e-7",
            "extra": "mean: 1.8035944183965384 usec\nrounds: 43895"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_valid_cursor_params",
            "value": 830052.3302981649,
            "unit": "iter/sec",
            "range": "stddev: 3.225402235639109e-7",
            "extra": "mean: 1.2047433197865822 usec\nrounds: 59841"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_valid_sort_request",
            "value": 389.3871054231547,
            "unit": "iter/sec",
            "range": "stddev: 0.00011767787710799728",
            "extra": "mean: 2.56813845675059 msec\nrounds: 289"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_filter_spec_empty_field",
            "value": 906365.3459836253,
            "unit": "iter/sec",
            "range": "stddev: 3.336636690994676e-7",
            "extra": "mean: 1.1033078486851884 usec\nrounds: 108261"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_valid_request",
            "value": 381.09013184534285,
            "unit": "iter/sec",
            "range": "stddev: 0.004975334090168572",
            "extra": "mean: 2.624051153352426 msec\nrounds: 313"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_filter_invalid_page",
            "value": 688.4381995125351,
            "unit": "iter/sec",
            "range": "stddev: 0.00010014321640479543",
            "extra": "mean: 1.4525632085902171 msec\nrounds: 652"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_valid_sort_spec",
            "value": 1133235.515695974,
            "unit": "iter/sec",
            "range": "stddev: 3.070350402093643e-7",
            "extra": "mean: 882.4291033500236 nsec\nrounds: 97762"
          },
          {
            "name": "tests/perf/test_competitors.py::test_sqlalchemy_pagination_lib_10k",
            "value": 1664.9168596103025,
            "unit": "iter/sec",
            "range": "stddev: 0.00006043392329376919",
            "extra": "mean: 600.6305925895089 usec\nrounds: 243"
          },
          {
            "name": "tests/perf/test_competitors.py::test_fastapi_pagination_full_pipeline",
            "value": 1178.380429364291,
            "unit": "iter/sec",
            "range": "stddev: 0.00003543820524423419",
            "extra": "mean: 848.6223761705519 usec\nrounds: 428"
          },
          {
            "name": "tests/perf/test_competitors.py::test_paginate_lib_memory",
            "value": 376409.3736147786,
            "unit": "iter/sec",
            "range": "stddev: 0.00000855276471105335",
            "extra": "mean: 2.656681980038602 usec\nrounds: 67719"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_full_pipeline",
            "value": 326.3257842145001,
            "unit": "iter/sec",
            "range": "stddev: 0.00004223625782807952",
            "extra": "mean: 3.0644222687064198 msec\nrounds: 294"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_sort_paginate",
            "value": 451.61098417066626,
            "unit": "iter/sec",
            "range": "stddev: 0.00002529163333918636",
            "extra": "mean: 2.214295123570543 msec\nrounds: 437"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_sa_filter",
            "value": 942.3414333663447,
            "unit": "iter/sec",
            "range": "stddev: 0.00003935433034303212",
            "extra": "mean: 1.0611864920633707 msec\nrounds: 315"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_sa_filter",
            "value": 920.7054561355994,
            "unit": "iter/sec",
            "range": "stddev: 0.00003016566501221313",
            "extra": "mean: 1.0861236819397346 msec\nrounds: 371"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_100k",
            "value": 562235.0844959287,
            "unit": "iter/sec",
            "range": "stddev: 5.554815062184754e-7",
            "extra": "mean: 1.7786154360974271 usec\nrounds: 56841"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_memory",
            "value": 560694.9654844492,
            "unit": "iter/sec",
            "range": "stddev: 4.871176341179369e-7",
            "extra": "mean: 1.783500943576307 usec\nrounds: 103864"
          },
          {
            "name": "tests/perf/test_competitors.py::test_paginate_lib_full_pipeline",
            "value": 1212.604307276089,
            "unit": "iter/sec",
            "range": "stddev: 0.0008492321916887313",
            "extra": "mean: 824.6713243550415 usec\nrounds: 891"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_sa_sync",
            "value": 2407.2490573920822,
            "unit": "iter/sec",
            "range": "stddev: 0.00004153524426411009",
            "extra": "mean: 415.4119395869076 usec\nrounds: 629"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_python_full_pipeline",
            "value": 1320.308528099608,
            "unit": "iter/sec",
            "range": "stddev: 0.000022410159972763857",
            "extra": "mean: 757.3987281892017 usec\nrounds: 894"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_python_slice",
            "value": 4810927.52332322,
            "unit": "iter/sec",
            "range": "stddev: 3.731108525549402e-8",
            "extra": "mean: 207.8601257557984 nsec\nrounds: 176367"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_python_100k",
            "value": 4367582.077166851,
            "unit": "iter/sec",
            "range": "stddev: 3.3505142196657e-8",
            "extra": "mean: 228.9596354073925 nsec\nrounds: 172712"
          },
          {
            "name": "tests/perf/test_competitors.py::test_fastapi_pagination_memory",
            "value": 17306.038443324484,
            "unit": "iter/sec",
            "range": "stddev: 0.000005147445295326535",
            "extra": "mean: 57.783299353858375 usec\nrounds: 5415"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_sa_async",
            "value": 919.3674671470293,
            "unit": "iter/sec",
            "range": "stddev: 0.00007262896443783492",
            "extra": "mean: 1.087704357326444 msec\nrounds: 389"
          },
          {
            "name": "tests/perf/test_competitors.py::test_fastapi_filter_10k",
            "value": 2507.2131639243635,
            "unit": "iter/sec",
            "range": "stddev: 0.000029209483620171997",
            "extra": "mean: 398.84921409505154 usec\nrounds: 752"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_filter_paginate",
            "value": 789.5084313393066,
            "unit": "iter/sec",
            "range": "stddev: 0.00002893599546727751",
            "extra": "mean: 1.2666109192825459 msec\nrounds: 669"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_sqlalchemy",
            "value": 2253.566291197741,
            "unit": "iter/sec",
            "range": "stddev: 0.000017238728759683716",
            "extra": "mean: 443.7411066654325 usec\nrounds: 675"
          },
          {
            "name": "tests/perf/test_competitors.py::test_fastapi_pagination_100k",
            "value": 17913.563380584103,
            "unit": "iter/sec",
            "range": "stddev: 0.0000054166057991118044",
            "extra": "mean: 55.82362251185968 usec\nrounds: 5677"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_python_sort_paginate",
            "value": 1605.354554168224,
            "unit": "iter/sec",
            "range": "stddev: 0.000009588696821446172",
            "extra": "mean: 622.9153537475876 usec\nrounds: 1241"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_python_search_paginate",
            "value": 1786.19479766659,
            "unit": "iter/sec",
            "range": "stddev: 0.000009713863031485935",
            "extra": "mean: 559.8493519891325 usec\nrounds: 1608"
          },
          {
            "name": "tests/perf/test_competitors.py::test_paginate_lib_100k",
            "value": 366611.72451709874,
            "unit": "iter/sec",
            "range": "stddev: 0.000009252081163447127",
            "extra": "mean: 2.7276814491331414 usec\nrounds: 71706"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_search_paginate",
            "value": 363.0086783280215,
            "unit": "iter/sec",
            "range": "stddev: 0.00001978939870524782",
            "extra": "mean: 2.754755078049074 msec\nrounds: 205"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_python_filter_paginate",
            "value": 3340.4132659438073,
            "unit": "iter/sec",
            "range": "stddev: 0.000029067395139097232",
            "extra": "mean: 299.364156583619 usec\nrounds: 3174"
          },
          {
            "name": "tests/perf/test_serialization.py::test_pipeline_page_model_dump",
            "value": 4159962.261322723,
            "unit": "iter/sec",
            "range": "stddev: 4.281707606664797e-8",
            "extra": "mean: 240.3867961249324 nsec\nrounds: 175439"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_sorted_json_dumps[100]",
            "value": 11980.914171786791,
            "unit": "iter/sec",
            "range": "stddev: 0.000012400349588983077",
            "extra": "mean: 83.46608494657661 usec\nrounds: 5992"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_filtered_json_dumps[1000]",
            "value": 1172.5452911908606,
            "unit": "iter/sec",
            "range": "stddev: 0.000043820915960101505",
            "extra": "mean: 852.8455212031768 usec\nrounds: 731"
          },
          {
            "name": "tests/perf/test_serialization.py::test_fp_filtered_page_serialize[1000]",
            "value": 10205.120089951042,
            "unit": "iter/sec",
            "range": "stddev: 0.000009373951705664275",
            "extra": "mean: 97.9900276709823 usec\nrounds: 6216"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_dict_construction[20]",
            "value": 7352460.6946290415,
            "unit": "iter/sec",
            "range": "stddev: 1.1251039435720602e-8",
            "extra": "mean: 136.00888757285955 nsec\nrounds: 73497"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_create[100]",
            "value": 2358456.133840093,
            "unit": "iter/sec",
            "range": "stddev: 1.727831289995449e-7",
            "extra": "mean: 424.00619017313534 nsec\nrounds: 169463"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_dict_construction[1000]",
            "value": 7352135.387221372,
            "unit": "iter/sec",
            "range": "stddev: 1.1217679213585317e-8",
            "extra": "mean: 136.01490551136072 nsec\nrounds: 73395"
          },
          {
            "name": "tests/perf/test_serialization.py::test_cursor_page_model_dump[100]",
            "value": 241161.15964120178,
            "unit": "iter/sec",
            "range": "stddev: 5.919311020279207e-7",
            "extra": "mean: 4.146604708186818 usec\nrounds: 51825"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_model_dump_json[100]",
            "value": 269936.6621089358,
            "unit": "iter/sec",
            "range": "stddev: 5.76933773582891e-7",
            "extra": "mean: 3.7045727400913004 usec\nrounds: 69604"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_searched_json_dumps[1000]",
            "value": 51819.9578422624,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015348221006131968",
            "extra": "mean: 19.297584205760156 usec\nrounds: 19868"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_json_dumps[20]",
            "value": 283736.597212452,
            "unit": "iter/sec",
            "range": "stddev: 6.292413853604613e-7",
            "extra": "mean: 3.5243955479286835 usec\nrounds: 94608"
          },
          {
            "name": "tests/perf/test_serialization.py::test_fp_filtered_page_serialize[100]",
            "value": 10285.863382920585,
            "unit": "iter/sec",
            "range": "stddev: 0.000004584038452367833",
            "extra": "mean: 97.22081295192726 usec\nrounds: 6362"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_create[1000]",
            "value": 2376037.7007765407,
            "unit": "iter/sec",
            "range": "stddev: 1.7421279012228163e-7",
            "extra": "mean: 420.8687428121104 nsec\nrounds: 158178"
          },
          {
            "name": "tests/perf/test_serialization.py::test_filtered_page_model_dump_json[20]",
            "value": 119049.01155789489,
            "unit": "iter/sec",
            "range": "stddev: 9.919684862353854e-7",
            "extra": "mean: 8.399901745624227 usec\nrounds: 37637"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_dict_dump[20]",
            "value": 5273349.419807362,
            "unit": "iter/sec",
            "range": "stddev: 2.5537356802212986e-8",
            "extra": "mean: 189.632796993097 nsec\nrounds: 198453"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_model_dump[20]",
            "value": 479291.8460146149,
            "unit": "iter/sec",
            "range": "stddev: 4.5743627147776414e-7",
            "extra": "mean: 2.0864114595630054 usec\nrounds: 63056"
          },
          {
            "name": "tests/perf/test_serialization.py::test_searched_page_model_dump_json[1000]",
            "value": 121294.77185683722,
            "unit": "iter/sec",
            "range": "stddev: 9.62642640907164e-7",
            "extra": "mean: 8.24437842366601 usec\nrounds: 35854"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_sorted_json_dumps[1000]",
            "value": 1165.8036642608245,
            "unit": "iter/sec",
            "range": "stddev: 0.000013495561270465213",
            "extra": "mean: 857.7773690855983 usec\nrounds: 634"
          },
          {
            "name": "tests/perf/test_serialization.py::test_sorted_page_model_dump_json[20]",
            "value": 120744.03855358926,
            "unit": "iter/sec",
            "range": "stddev: 9.863521673630773e-7",
            "extra": "mean: 8.281982381732037 usec\nrounds: 40526"
          },
          {
            "name": "tests/perf/test_serialization.py::test_cursor_page_model_dump[20]",
            "value": 489733.7756029448,
            "unit": "iter/sec",
            "range": "stddev: 5.444759346401971e-7",
            "extra": "mean: 2.0419257356077427 usec\nrounds: 74935"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_model_dump[1000]",
            "value": 37873.71534224321,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018126501065345236",
            "extra": "mean: 26.40353582857053 usec\nrounds: 29418"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_filtered_json_dumps[20]",
            "value": 52466.334478678094,
            "unit": "iter/sec",
            "range": "stddev: 0.0000017502960463523586",
            "extra": "mean: 19.05984113310588 usec\nrounds: 20791"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_json_dumps[1000]",
            "value": 17454.708295309374,
            "unit": "iter/sec",
            "range": "stddev: 0.000003540746270349696",
            "extra": "mean: 57.29113217370303 usec\nrounds: 9601"
          },
          {
            "name": "tests/perf/test_serialization.py::test_sorted_page_model_dump_json[1000]",
            "value": 2765.4205795463145,
            "unit": "iter/sec",
            "range": "stddev: 0.000009560974036612368",
            "extra": "mean: 361.6086491133499 usec\nrounds: 2089"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_model_dump_json[1000]",
            "value": 39815.903008636094,
            "unit": "iter/sec",
            "range": "stddev: 0.00000170313351650349",
            "extra": "mean: 25.11559262596906 usec\nrounds: 31271"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_json_dumps[100]",
            "value": 122631.82133070588,
            "unit": "iter/sec",
            "range": "stddev: 0.0000010408346562543305",
            "extra": "mean: 8.15449032028369 usec\nrounds: 34196"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_create[20]",
            "value": 2287077.4188088463,
            "unit": "iter/sec",
            "range": "stddev: 1.732326754151016e-7",
            "extra": "mean: 437.23924331377435 nsec\nrounds: 167758"
          },
          {
            "name": "tests/perf/test_serialization.py::test_filtered_page_model_dump_json[100]",
            "value": 29424.915371445557,
            "unit": "iter/sec",
            "range": "stddev: 0.000002147615274921128",
            "extra": "mean: 33.984804624805044 usec\nrounds: 18595"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_filtered_json_dumps[100]",
            "value": 12102.97945758144,
            "unit": "iter/sec",
            "range": "stddev: 0.000005007164813629396",
            "extra": "mean: 82.62428301269148 usec\nrounds: 5869"
          },
          {
            "name": "tests/perf/test_serialization.py::test_searched_page_model_dump_json[100]",
            "value": 120270.65965858416,
            "unit": "iter/sec",
            "range": "stddev: 8.854102453469206e-7",
            "extra": "mean: 8.314579822200438 usec\nrounds: 39895"
          },
          {
            "name": "tests/perf/test_serialization.py::test_fp_filtered_page_serialize[20]",
            "value": 47052.98834322961,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018626391888152222",
            "extra": "mean: 21.25263527802881 usec\nrounds: 23862"
          },
          {
            "name": "tests/perf/test_serialization.py::test_pipeline_page_model_dump_json",
            "value": 345045.51183312875,
            "unit": "iter/sec",
            "range": "stddev: 4.6127621922134745e-7",
            "extra": "mean: 2.8981684030239494 usec\nrounds: 30712"
          },
          {
            "name": "tests/perf/test_serialization.py::test_filtered_page_model_dump_json[1000]",
            "value": 2850.3681307966963,
            "unit": "iter/sec",
            "range": "stddev: 0.000015333775814000438",
            "extra": "mean: 350.8318764848433 usec\nrounds: 2356"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_model_dump_json[20]",
            "value": 533104.3144603356,
            "unit": "iter/sec",
            "range": "stddev: 4.0504194459445343e-7",
            "extra": "mean: 1.8758054903613102 usec\nrounds: 126040"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_pipeline_json_dumps",
            "value": 52022.88830148164,
            "unit": "iter/sec",
            "range": "stddev: 0.0000017527672038687298",
            "extra": "mean: 19.222308346372984 usec\nrounds: 18823"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_searched_json_dumps[20]",
            "value": 53145.050615851986,
            "unit": "iter/sec",
            "range": "stddev: 0.0000016532637711985503",
            "extra": "mean: 18.81642765246934 usec\nrounds: 34348"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_dict_dump[100]",
            "value": 5248422.960734063,
            "unit": "iter/sec",
            "range": "stddev: 1.7460050142871467e-8",
            "extra": "mean: 190.53342451279397 nsec\nrounds: 50083"
          },
          {
            "name": "tests/perf/test_serialization.py::test_sorted_page_model_dump_json[100]",
            "value": 29213.666531084313,
            "unit": "iter/sec",
            "range": "stddev: 0.0000021594940793447954",
            "extra": "mean: 34.2305543515384 usec\nrounds: 17074"
          },
          {
            "name": "tests/perf/test_serialization.py::test_searched_page_model_dump_json[20]",
            "value": 118716.24304372497,
            "unit": "iter/sec",
            "range": "stddev: 8.964046798773181e-7",
            "extra": "mean: 8.423447157367379 usec\nrounds: 61882"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_dict_dump[1000]",
            "value": 5322403.60221446,
            "unit": "iter/sec",
            "range": "stddev: 1.2925666607318319e-8",
            "extra": "mean: 187.88503742633495 nsec\nrounds: 53839"
          },
          {
            "name": "tests/perf/test_serialization.py::test_cursor_page_model_dump[1000]",
            "value": 37916.7635765023,
            "unit": "iter/sec",
            "range": "stddev: 0.0000016370103274629063",
            "extra": "mean: 26.373558966401813 usec\nrounds: 24268"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_model_dump[100]",
            "value": 240648.25754487695,
            "unit": "iter/sec",
            "range": "stddev: 5.722932447352943e-7",
            "extra": "mean: 4.155442512661935 usec\nrounds: 85749"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_dict_construction[100]",
            "value": 6666036.72763545,
            "unit": "iter/sec",
            "range": "stddev: 1.127755675527629e-8",
            "extra": "mean: 150.01417496760655 nsec\nrounds: 72276"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_sorted_json_dumps[20]",
            "value": 52523.52115437038,
            "unit": "iter/sec",
            "range": "stddev: 0.00000164579671044727",
            "extra": "mean: 19.03908911706298 usec\nrounds: 22476"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_searched_json_dumps[100]",
            "value": 53282.10150638365,
            "unit": "iter/sec",
            "range": "stddev: 0.0000014789236019503277",
            "extra": "mean: 18.7680285072876 usec\nrounds: 27642"
          },
          {
            "name": "tests/perf/test_sorting.py::test_bench_sort_sa_async_1k",
            "value": 30845.919731910475,
            "unit": "iter/sec",
            "range": "stddev: 0.001081320455331729",
            "extra": "mean: 32.41919867169621 usec\nrounds: 8431"
          },
          {
            "name": "tests/perf/test_sorting.py::test_bench_sort_sa_sync_10k",
            "value": 49144.39339589102,
            "unit": "iter/sec",
            "range": "stddev: 0.000006156590062899267",
            "extra": "mean: 20.34820110494253 usec\nrounds: 12670"
          },
          {
            "name": "tests/perf/test_sorting.py::test_bench_sort_sa_async_10k",
            "value": 48822.87026285951,
            "unit": "iter/sec",
            "range": "stddev: 0.000006150289652894536",
            "extra": "mean: 20.482204233713784 usec\nrounds: 14219"
          },
          {
            "name": "tests/perf/test_sorting.py::test_bench_sort_memory_10k",
            "value": 454.08175380281625,
            "unit": "iter/sec",
            "range": "stddev: 0.000026050596943029346",
            "extra": "mean: 2.202246603448081 msec\nrounds: 406"
          },
          {
            "name": "tests/perf/test_sorting.py::test_bench_sort_sa_sync_1k",
            "value": 50432.98466863666,
            "unit": "iter/sec",
            "range": "stddev: 0.000006154164219862574",
            "extra": "mean: 19.828293061978574 usec\nrounds: 10363"
          },
          {
            "name": "tests/perf/test_sorting.py::test_bench_sort_memory_100k",
            "value": 44.040103834577124,
            "unit": "iter/sec",
            "range": "stddev: 0.0003124111183451751",
            "extra": "mean: 22.70657680000454 msec\nrounds: 40"
          },
          {
            "name": "tests/perf/test_pipeline.py::test_bench_pipeline_sa_async_1k",
            "value": 633.0175689215167,
            "unit": "iter/sec",
            "range": "stddev: 0.00009619601318857962",
            "extra": "mean: 1.579734985402882 msec\nrounds: 274"
          },
          {
            "name": "tests/perf/test_pipeline.py::test_bench_pipeline_memory_10k",
            "value": 309.64933813394276,
            "unit": "iter/sec",
            "range": "stddev: 0.00002403383177165102",
            "extra": "mean: 3.2294595106398623 msec\nrounds: 282"
          },
          {
            "name": "tests/perf/test_pipeline.py::test_bench_pipeline_sa_async_10k",
            "value": 240.4275879174186,
            "unit": "iter/sec",
            "range": "stddev: 0.00013607668288686295",
            "extra": "mean: 4.159256467454464 msec\nrounds: 169"
          },
          {
            "name": "tests/perf/test_pipeline.py::test_bench_pipeline_sa_sync_1k",
            "value": 1291.9522542513955,
            "unit": "iter/sec",
            "range": "stddev: 0.000024268893286381685",
            "extra": "mean: 774.0224119810346 usec\nrounds: 551"
          },
          {
            "name": "tests/perf/test_pipeline.py::test_bench_pipeline_sa_sync_10k",
            "value": 292.62344200541133,
            "unit": "iter/sec",
            "range": "stddev: 0.00007837652423155278",
            "extra": "mean: 3.417361210526351 msec\nrounds: 209"
          },
          {
            "name": "tests/perf/test_pipeline.py::test_bench_pipeline_memory_100k",
            "value": 32.01571725195596,
            "unit": "iter/sec",
            "range": "stddev: 0.00027288784449567926",
            "extra": "mean: 31.23465865625441 msec\nrounds: 32"
          },
          {
            "name": "tests/perf/test_comparison.py::test_raw_list_search_10k",
            "value": 1760.653515478549,
            "unit": "iter/sec",
            "range": "stddev: 0.000012503988919615363",
            "extra": "mean: 567.9709217109637 usec\nrounds: 1239"
          },
          {
            "name": "tests/perf/test_comparison.py::test_sa_sync_paginate_10k",
            "value": 2497.7696481231083,
            "unit": "iter/sec",
            "range": "stddev: 0.000015360656797466913",
            "extra": "mean: 400.35717495063125 usec\nrounds: 1006"
          },
          {
            "name": "tests/perf/test_comparison.py::test_raw_list_filter_10k",
            "value": 3499.8952216597504,
            "unit": "iter/sec",
            "range": "stddev: 0.000008438020473379517",
            "extra": "mean: 285.72283930424965 usec\nrounds: 1898"
          },
          {
            "name": "tests/perf/test_comparison.py::test_sa_async_paginate_10k",
            "value": 837.3453275692037,
            "unit": "iter/sec",
            "range": "stddev: 0.0000902990503759377",
            "extra": "mean: 1.194250409091049 msec\nrounds: 572"
          },
          {
            "name": "tests/perf/test_comparison.py::test_raw_list_slice_10k",
            "value": 4685573.22185953,
            "unit": "iter/sec",
            "range": "stddev: 3.1401450478574425e-8",
            "extra": "mean: 213.42105920677005 nsec\nrounds: 198847"
          },
          {
            "name": "tests/perf/test_comparison.py::test_raw_list_sort_10k",
            "value": 1588.9988160967807,
            "unit": "iter/sec",
            "range": "stddev: 0.000013324082191666064",
            "extra": "mean: 629.3270894036294 usec\nrounds: 1208"
          },
          {
            "name": "tests/perf/test_comparison.py::test_memory_paginate_10k",
            "value": 573724.5630207224,
            "unit": "iter/sec",
            "range": "stddev: 3.778052001748488e-7",
            "extra": "mean: 1.7429966650458382 usec\nrounds: 65669"
          },
          {
            "name": "tests/perf/test_comparison.py::test_raw_pipeline_10k",
            "value": 1306.1506806915147,
            "unit": "iter/sec",
            "range": "stddev: 0.00001863239356306161",
            "extra": "mean: 765.6084514464828 usec\nrounds: 968"
          },
          {
            "name": "tests/perf/test_comparison.py::test_memory_search_10k",
            "value": 359.1215133399678,
            "unit": "iter/sec",
            "range": "stddev: 0.000021146241133952775",
            "extra": "mean: 2.784572805732568 msec\nrounds: 314"
          },
          {
            "name": "tests/perf/test_comparison.py::test_memory_sort_10k",
            "value": 451.70424141496744,
            "unit": "iter/sec",
            "range": "stddev: 0.00003065804678571985",
            "extra": "mean: 2.213837968108272 msec\nrounds: 439"
          },
          {
            "name": "tests/perf/test_comparison.py::test_memory_pipeline_10k",
            "value": 309.0099272817373,
            "unit": "iter/sec",
            "range": "stddev: 0.00010477552954058383",
            "extra": "mean: 3.236141986753254 msec\nrounds: 302"
          },
          {
            "name": "tests/perf/test_comparison.py::test_memory_filter_10k",
            "value": 803.4798835500667,
            "unit": "iter/sec",
            "range": "stddev: 0.000012642470309885604",
            "extra": "mean: 1.2445862310598692 msec\nrounds: 792"
          },
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_sa_async_10k",
            "value": 882.1700739562607,
            "unit": "iter/sec",
            "range": "stddev: 0.00010700587905676833",
            "extra": "mean: 1.1335682648078373 msec\nrounds: 574"
          },
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_sa_async_1k",
            "value": 890.0896133555186,
            "unit": "iter/sec",
            "range": "stddev: 0.00012829833065699421",
            "extra": "mean: 1.1234823831166099 msec\nrounds: 462"
          },
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_memory_1k",
            "value": 583783.1732022663,
            "unit": "iter/sec",
            "range": "stddev: 0.0000020471196012409564",
            "extra": "mean: 1.7129647545588385 usec\nrounds: 127960"
          },
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_memory_10k",
            "value": 580054.6812427866,
            "unit": "iter/sec",
            "range": "stddev: 3.772837442733199e-7",
            "extra": "mean: 1.7239753980736205 usec\nrounds: 75279"
          },
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_sa_sync_10k",
            "value": 2538.349108428284,
            "unit": "iter/sec",
            "range": "stddev: 0.0000181609983929147",
            "extra": "mean: 393.9568425318723 usec\nrounds: 1232"
          },
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_memory_100k",
            "value": 579553.9761779652,
            "unit": "iter/sec",
            "range": "stddev: 4.034761914419378e-7",
            "extra": "mean: 1.725464824855118 usec\nrounds: 135081"
          },
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_sa_sync_1k",
            "value": 2552.491997944712,
            "unit": "iter/sec",
            "range": "stddev: 0.00006410784822469269",
            "extra": "mean: 391.7739999989064 usec\nrounds: 642"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_sa_pipeline_10k",
            "value": 216.3264564708218,
            "unit": "iter/sec",
            "range": "stddev: 0.00017052391712259258",
            "extra": "mean: 4.622643093748824 msec\nrounds: 128"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_sa_search_10k",
            "value": 265.3514029353668,
            "unit": "iter/sec",
            "range": "stddev: 0.00009589381203569463",
            "extra": "mean: 3.7685875745815287 msec\nrounds: 181"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_sort_10k",
            "value": 200.56163511907388,
            "unit": "iter/sec",
            "range": "stddev: 0.00010558859356136571",
            "extra": "mean: 4.985998440859828 msec\nrounds: 186"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_sa_sort_10k",
            "value": 156.89961198263006,
            "unit": "iter/sec",
            "range": "stddev: 0.0002598423621936915",
            "extra": "mean: 6.373502058824131 msec\nrounds: 119"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_sa_filter_10k",
            "value": 261.80039042621206,
            "unit": "iter/sec",
            "range": "stddev: 0.00015362575836649182",
            "extra": "mean: 3.819704005681566 msec\nrounds: 176"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_fp_fastapi_sa_10k",
            "value": 218.49054031461412,
            "unit": "iter/sec",
            "range": "stddev: 0.009552735467342765",
            "extra": "mean: 4.576857188233669 msec\nrounds: 170"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_pipeline_10k",
            "value": 167.26998478294092,
            "unit": "iter/sec",
            "range": "stddev: 0.00010925705057102302",
            "extra": "mean: 5.978358886668502 msec\nrounds: 150"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_offset_10k",
            "value": 372.4818429518881,
            "unit": "iter/sec",
            "range": "stddev: 0.00009936908459710413",
            "extra": "mean: 2.6846946204815834 msec\nrounds: 332"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_filter_10k",
            "value": 234.39910801070087,
            "unit": "iter/sec",
            "range": "stddev: 0.0001148134529246998",
            "extra": "mean: 4.266227838863395 msec\nrounds: 211"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_fp_fastapi_pipeline_10k",
            "value": 243.59177154496527,
            "unit": "iter/sec",
            "range": "stddev: 0.0001392503315740608",
            "extra": "mean: 4.105228980673541 msec\nrounds: 207"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_search_10k",
            "value": 79.17881121170541,
            "unit": "iter/sec",
            "range": "stddev: 0.0003885701034015055",
            "extra": "mean: 12.62964149999975 msec\nrounds: 66"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_100k",
            "value": 324.176320443709,
            "unit": "iter/sec",
            "range": "stddev: 0.00008334891356848711",
            "extra": "mean: 3.084741040404409 msec\nrounds: 297"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_sort_10k",
            "value": 264.5271633022444,
            "unit": "iter/sec",
            "range": "stddev: 0.00010479411866661543",
            "extra": "mean: 3.7803301086981995 msec\nrounds: 230"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_sa_pipeline_10k",
            "value": 191.98607297199166,
            "unit": "iter/sec",
            "range": "stddev: 0.00017741662489667988",
            "extra": "mean: 5.2087111555528685 msec\nrounds: 135"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_sa_filter_10k",
            "value": 177.52093064598432,
            "unit": "iter/sec",
            "range": "stddev: 0.011252470903014249",
            "extra": "mean: 5.633138562090007 msec\nrounds: 153"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_search_10k",
            "value": 231.5961052642291,
            "unit": "iter/sec",
            "range": "stddev: 0.00012490232057911732",
            "extra": "mean: 4.31786190384806 msec\nrounds: 208"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_sa_sort_10k",
            "value": 231.20649377500303,
            "unit": "iter/sec",
            "range": "stddev: 0.0000984657086571975",
            "extra": "mean: 4.325138034285244 msec\nrounds: 175"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_sa_10k",
            "value": 247.55129146255607,
            "unit": "iter/sec",
            "range": "stddev: 0.00011078696774705389",
            "extra": "mean: 4.039566887701966 msec\nrounds: 187"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_sa_search_10k",
            "value": 167.11978029943313,
            "unit": "iter/sec",
            "range": "stddev: 0.00014647992795317684",
            "extra": "mean: 5.983732136365141 msec\nrounds: 132"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_filter_10k",
            "value": 262.6454843926156,
            "unit": "iter/sec",
            "range": "stddev: 0.00009919396556413518",
            "extra": "mean: 3.807413640910537 msec\nrounds: 220"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_offset_10k",
            "value": 267.6608633677321,
            "unit": "iter/sec",
            "range": "stddev: 0.00012931019414419317",
            "extra": "mean: 3.736071039366435 msec\nrounds: 254"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_1k",
            "value": 262.3901462418848,
            "unit": "iter/sec",
            "range": "stddev: 0.00010658552221427512",
            "extra": "mean: 3.8111187265323156 msec\nrounds: 245"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_fp_fastapi_offset_10k",
            "value": 245.14757350135292,
            "unit": "iter/sec",
            "range": "stddev: 0.00009979041036591091",
            "extra": "mean: 4.079175599078411 msec\nrounds: 217"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_10k",
            "value": 214.91160047143217,
            "unit": "iter/sec",
            "range": "stddev: 0.01088188021372265",
            "extra": "mean: 4.6530759521886695 msec\nrounds: 251"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_sa_10k",
            "value": 212.81033066473725,
            "unit": "iter/sec",
            "range": "stddev: 0.00014365451118024283",
            "extra": "mean: 4.699019999998996 msec\nrounds: 157"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_pipeline_10k",
            "value": 209.4140083656859,
            "unit": "iter/sec",
            "range": "stddev: 0.00009548288824682133",
            "extra": "mean: 4.775229736559771 msec\nrounds: 186"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_pipeline_scaling[100K]",
            "value": 31.978091713432104,
            "unit": "iter/sec",
            "range": "stddev: 0.0006334149161063514",
            "extra": "mean: 31.271409468750733 msec\nrounds: 32"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_pipeline_scaling[1M]",
            "value": 2.7750000828616734,
            "unit": "iter/sec",
            "range": "stddev: 0.003645642009919312",
            "extra": "mean: 360.3603495999778 msec\nrounds: 5"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_sort_scaling[10K]",
            "value": 293.48369101141026,
            "unit": "iter/sec",
            "range": "stddev: 0.000060286721441816936",
            "extra": "mean: 3.4073443623179775 msec\nrounds: 207"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_pipeline_scaling[100K]",
            "value": 71.539378345859,
            "unit": "iter/sec",
            "range": "stddev: 0.00020233664556342345",
            "extra": "mean: 13.978315483333859 msec\nrounds: 60"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_sort_scaling[1K]",
            "value": 4255.867804432115,
            "unit": "iter/sec",
            "range": "stddev: 0.000007883950502172247",
            "extra": "mean: 234.9697044063698 usec\nrounds: 3745"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_paginate_scaling[100K]",
            "value": 890.132838035152,
            "unit": "iter/sec",
            "range": "stddev: 0.00008065634721430849",
            "extra": "mean: 1.1234278270278906 msec\nrounds: 370"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_paginate_scaling[100K]",
            "value": 587366.4485491725,
            "unit": "iter/sec",
            "range": "stddev: 4.2901589316165586e-7",
            "extra": "mean: 1.702514677966464 usec\nrounds: 47486"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_filter_scaling[1K]",
            "value": 7735.549837290908,
            "unit": "iter/sec",
            "range": "stddev: 0.000004210524411585733",
            "extra": "mean: 129.27329291827218 usec\nrounds: 6425"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_search_scaling[1K]",
            "value": 4056.6450608817263,
            "unit": "iter/sec",
            "range": "stddev: 0.000007792033127994694",
            "extra": "mean: 246.50911898677342 usec\nrounds: 2765"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_sort_scaling[10K]",
            "value": 449.7888424020631,
            "unit": "iter/sec",
            "range": "stddev: 0.000058712424287376266",
            "extra": "mean: 2.2232654653227413 msec\nrounds: 447"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_sort_scaling[1K]",
            "value": 643.9815743404816,
            "unit": "iter/sec",
            "range": "stddev: 0.00008625974729079327",
            "extra": "mean: 1.552839459768901 msec\nrounds: 348"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_paginate_scaling[100K]",
            "value": 2264.050950542137,
            "unit": "iter/sec",
            "range": "stddev: 0.000025401348292079866",
            "extra": "mean: 441.686173078634 usec\nrounds: 572"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_sort_scaling[100K]",
            "value": 25.613870860493204,
            "unit": "iter/sec",
            "range": "stddev: 0.0005417236393351945",
            "extra": "mean: 39.04134620833114 msec\nrounds: 24"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_search_scaling[100K]",
            "value": 26.032739904567954,
            "unit": "iter/sec",
            "range": "stddev: 0.0004903668041958238",
            "extra": "mean: 38.41316755999742 msec\nrounds: 25"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_filter_scaling[100K]",
            "value": 79.29210746788618,
            "unit": "iter/sec",
            "range": "stddev: 0.00014454143237519162",
            "extra": "mean: 12.611595679998876 msec\nrounds: 75"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_filter_scaling[10K]",
            "value": 958.9664793143905,
            "unit": "iter/sec",
            "range": "stddev: 0.000030114676558435303",
            "extra": "mean: 1.0427893170102736 msec\nrounds: 388"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_paginate_scaling[1K]",
            "value": 2627.6474430215003,
            "unit": "iter/sec",
            "range": "stddev: 0.00002101131194590134",
            "extra": "mean: 380.5685586381832 usec\nrounds: 793"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_pipeline_scaling[1K]",
            "value": 3247.4844089200196,
            "unit": "iter/sec",
            "range": "stddev: 0.00001180359943838123",
            "extra": "mean: 307.930654648642 usec\nrounds: 2829"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_search_scaling[10K]",
            "value": 367.78656867071385,
            "unit": "iter/sec",
            "range": "stddev: 0.00004260685650872609",
            "extra": "mean: 2.7189682418645322 msec\nrounds: 215"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_search_scaling[10K]",
            "value": 343.20293148923025,
            "unit": "iter/sec",
            "range": "stddev: 0.00007575017582204034",
            "extra": "mean: 2.9137280257507943 msec\nrounds: 233"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_sort_scaling[1K]",
            "value": 1294.6076937018174,
            "unit": "iter/sec",
            "range": "stddev: 0.000035010217940207126",
            "extra": "mean: 772.4347729933439 usec\nrounds: 511"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_search_scaling[100K]",
            "value": 63.06366322939041,
            "unit": "iter/sec",
            "range": "stddev: 0.00027943629525712727",
            "extra": "mean: 15.856991947368458 msec\nrounds: 57"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_filter_scaling[100K]",
            "value": 159.517841425212,
            "unit": "iter/sec",
            "range": "stddev: 0.0001969769821385784",
            "extra": "mean: 6.268891247935033 msec\nrounds: 121"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_search_scaling[1M]",
            "value": 2.576390259757554,
            "unit": "iter/sec",
            "range": "stddev: 0.0025538808549913955",
            "extra": "mean: 388.1399551999948 msec\nrounds: 5"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_filter_scaling[1M]",
            "value": 7.665989936073146,
            "unit": "iter/sec",
            "range": "stddev: 0.0004653101882490641",
            "extra": "mean: 130.44629699999888 msec\nrounds: 8"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_sort_scaling[500K]",
            "value": 7.116163004900644,
            "unit": "iter/sec",
            "range": "stddev: 0.00035466367524273414",
            "extra": "mean: 140.525167749999 msec\nrounds: 8"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_pipeline_scaling[100K]",
            "value": 74.9425070774398,
            "unit": "iter/sec",
            "range": "stddev: 0.00011415425884771712",
            "extra": "mean: 13.343562138462717 msec\nrounds: 65"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_sort_scaling[1M]",
            "value": 3.658584034523813,
            "unit": "iter/sec",
            "range": "stddev: 0.0007164448859747376",
            "extra": "mean: 273.3297883999967 msec\nrounds: 5"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_pipeline_scaling[1K]",
            "value": 681.0697803728839,
            "unit": "iter/sec",
            "range": "stddev: 0.0001211343241945987",
            "extra": "mean: 1.468278330382685 msec\nrounds: 339"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_sort_scaling[100K]",
            "value": 26.390725002435552,
            "unit": "iter/sec",
            "range": "stddev: 0.00033287940130152636",
            "extra": "mean: 37.89210034615236 msec\nrounds: 26"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_pipeline_scaling[10K]",
            "value": 519.7463088252689,
            "unit": "iter/sec",
            "range": "stddev: 0.00003545077611196509",
            "extra": "mean: 1.9240155880283227 msec\nrounds: 284"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_sort_scaling[100K]",
            "value": 41.9067110184565,
            "unit": "iter/sec",
            "range": "stddev: 0.000539566462935221",
            "extra": "mean: 23.862526447364992 msec\nrounds: 38"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_filter_scaling[10K]",
            "value": 764.5353981194388,
            "unit": "iter/sec",
            "range": "stddev: 0.00005650891411175792",
            "extra": "mean: 1.3079839108296931 msec\nrounds: 628"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_sort_scaling[10K]",
            "value": 248.14295452446245,
            "unit": "iter/sec",
            "range": "stddev: 0.0000641943445224793",
            "extra": "mean: 4.029935090909131 msec\nrounds: 165"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_pipeline_scaling[10K]",
            "value": 379.7319632841018,
            "unit": "iter/sec",
            "range": "stddev: 0.00011697596945132839",
            "extra": "mean: 2.633436467532326 msec\nrounds: 231"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_paginate_scaling[1M]",
            "value": 584977.3079547716,
            "unit": "iter/sec",
            "range": "stddev: 4.476322045510562e-7",
            "extra": "mean: 1.7094680193600202 usec\nrounds: 38539"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_search_scaling[500K]",
            "value": 5.124052023602466,
            "unit": "iter/sec",
            "range": "stddev: 0.0006263070780418909",
            "extra": "mean: 195.15804979999984 msec\nrounds: 5"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_search_scaling[10K]",
            "value": 486.1032497030213,
            "unit": "iter/sec",
            "range": "stddev: 0.0000374173455014076",
            "extra": "mean: 2.0571761258764214 msec\nrounds: 286"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_filter_scaling[500K]",
            "value": 15.24540999936571,
            "unit": "iter/sec",
            "range": "stddev: 0.0005144485900970457",
            "extra": "mean: 65.59351306666107 msec\nrounds: 15"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_paginate_scaling[10K]",
            "value": 582945.0257979438,
            "unit": "iter/sec",
            "range": "stddev: 6.130901745038586e-7",
            "extra": "mean: 1.7154276230956518 usec\nrounds: 58306"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_filter_scaling[10K]",
            "value": 577.1313302085425,
            "unit": "iter/sec",
            "range": "stddev: 0.00010625493298262131",
            "extra": "mean: 1.732707873680427 msec\nrounds: 285"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_paginate_scaling[500K]",
            "value": 582699.9957976192,
            "unit": "iter/sec",
            "range": "stddev: 4.6266788938486987e-7",
            "extra": "mean: 1.7161489741065925 usec\nrounds: 44699"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_filter_scaling[1K]",
            "value": 1772.293130359483,
            "unit": "iter/sec",
            "range": "stddev: 0.00002454075498485451",
            "extra": "mean: 564.240747125824 usec\nrounds: 522"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_search_scaling[1K]",
            "value": 965.5243588072445,
            "unit": "iter/sec",
            "range": "stddev: 0.007343199762800603",
            "extra": "mean: 1.035706650876571 msec\nrounds: 570"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_paginate_scaling[10K]",
            "value": 931.272138967746,
            "unit": "iter/sec",
            "range": "stddev: 0.00007158029741536976",
            "extra": "mean: 1.073799975492056 msec\nrounds: 408"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_paginate_scaling[1K]",
            "value": 897.3175203181787,
            "unit": "iter/sec",
            "range": "stddev: 0.00010307389140066775",
            "extra": "mean: 1.1144327145706585 msec\nrounds: 501"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_paginate_scaling[10K]",
            "value": 2569.516880988736,
            "unit": "iter/sec",
            "range": "stddev: 0.000023223957379182673",
            "extra": "mean: 389.17821766370554 usec\nrounds: 634"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_search_scaling[100K]",
            "value": 66.66490834268032,
            "unit": "iter/sec",
            "range": "stddev: 0.000146524255129855",
            "extra": "mean: 15.000395633331701 msec\nrounds: 60"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_pipeline_scaling[10K]",
            "value": 300.6597690242281,
            "unit": "iter/sec",
            "range": "stddev: 0.000034582425599692426",
            "extra": "mean: 3.3260186530623486 msec\nrounds: 294"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_filter_scaling[100K]",
            "value": 183.45257552911087,
            "unit": "iter/sec",
            "range": "stddev: 0.00013983508897931197",
            "extra": "mean: 5.451000058820743 msec\nrounds: 136"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_paginate_scaling[1K]",
            "value": 590423.5659386212,
            "unit": "iter/sec",
            "range": "stddev: 3.800272139223742e-7",
            "extra": "mean: 1.6936993333087205 usec\nrounds: 105286"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_pipeline_scaling[500K]",
            "value": 5.563363452841923,
            "unit": "iter/sec",
            "range": "stddev: 0.0012572414450741159",
            "extra": "mean: 179.74737916667513 msec\nrounds: 6"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_pipeline_scaling[1K]",
            "value": 1396.0254446432225,
            "unit": "iter/sec",
            "range": "stddev: 0.00004280094381347479",
            "extra": "mean: 716.319321998867 usec\nrounds: 500"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_filter_scaling[1K]",
            "value": 801.5882716268245,
            "unit": "iter/sec",
            "range": "stddev: 0.000048069175278496304",
            "extra": "mean: 1.2475232427870964 msec\nrounds: 416"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_search_scaling[1K]",
            "value": 689.443303456988,
            "unit": "iter/sec",
            "range": "stddev: 0.0000874836903046402",
            "extra": "mean: 1.4504455913718026 msec\nrounds: 394"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_sort_scaling[100K]",
            "value": 161.67708746036286,
            "unit": "iter/sec",
            "range": "stddev: 0.0001376746356793003",
            "extra": "mean: 6.185168323527368 msec\nrounds: 136"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_fastapi_filter_scaling[10K]",
            "value": 2576.0530266896153,
            "unit": "iter/sec",
            "range": "stddev: 0.00002071958521947376",
            "extra": "mean: 388.1907668977843 usec\nrounds: 725"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_paginate_scaling[100K]",
            "value": 2062.5159591815245,
            "unit": "iter/sec",
            "range": "stddev: 0.00003542649485464157",
            "extra": "mean: 484.8447332241897 usec\nrounds: 611"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_sort_scaling[1K]",
            "value": 1067.5808406567721,
            "unit": "iter/sec",
            "range": "stddev: 0.000040441898910289826",
            "extra": "mean: 936.6972147840378 usec\nrounds: 717"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_paginate_scaling[1K]",
            "value": 717.038032763704,
            "unit": "iter/sec",
            "range": "stddev: 0.00011223604031500235",
            "extra": "mean: 1.3946261625002876 msec\nrounds: 400"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_sa_pagination_lib_scaling[100K]",
            "value": 1671.5764802586664,
            "unit": "iter/sec",
            "range": "stddev: 0.00002675813505196434",
            "extra": "mean: 598.2376587670436 usec\nrounds: 422"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_pipeline_scaling[1K]",
            "value": 1408.7522217495364,
            "unit": "iter/sec",
            "range": "stddev: 0.000027205802144216086",
            "extra": "mean: 709.8480375477918 usec\nrounds: 506"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_pipeline_scaling[100K]",
            "value": 78.79886942712632,
            "unit": "iter/sec",
            "range": "stddev: 0.0001238363397958287",
            "extra": "mean: 12.69053740580385 msec\nrounds: 69"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_search_scaling[10K]",
            "value": 803.3153515638664,
            "unit": "iter/sec",
            "range": "stddev: 0.00003498407979491652",
            "extra": "mean: 1.2448411424644565 msec\nrounds: 365"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_sa_pagination_lib_scaling[1K]",
            "value": 1810.6807073065934,
            "unit": "iter/sec",
            "range": "stddev: 0.000019400169101631607",
            "extra": "mean: 552.2784861873912 usec\nrounds: 543"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_filter_scaling[100K]",
            "value": 182.89326364593776,
            "unit": "iter/sec",
            "range": "stddev: 0.00011520547076264721",
            "extra": "mean: 5.46766994073601 msec\nrounds: 135"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_fp_sa_paginate_scaling[10K]",
            "value": 1534.7202813494762,
            "unit": "iter/sec",
            "range": "stddev: 0.000027011194692006114",
            "extra": "mean: 651.5845344277997 usec\nrounds: 305"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_search_scaling[100K]",
            "value": 141.7266273564142,
            "unit": "iter/sec",
            "range": "stddev: 0.00015369768564141086",
            "extra": "mean: 7.055837132744289 msec\nrounds: 113"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_sort_scaling[10K]",
            "value": 701.7526323636074,
            "unit": "iter/sec",
            "range": "stddev: 0.00006038814277156594",
            "extra": "mean: 1.425003560915548 msec\nrounds: 435"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_filter_scaling[1K]",
            "value": 1635.6939666681358,
            "unit": "iter/sec",
            "range": "stddev: 0.00002868421043119383",
            "extra": "mean: 611.3613061965209 usec\nrounds: 565"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_search_scaling[1K]",
            "value": 1563.9050306503273,
            "unit": "iter/sec",
            "range": "stddev: 0.000025665708192400734",
            "extra": "mean: 639.4250164820843 usec\nrounds: 546"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_search_scaling[10K]",
            "value": 467.41150323395266,
            "unit": "iter/sec",
            "range": "stddev: 0.00008261911714646724",
            "extra": "mean: 2.139442425103243 msec\nrounds: 247"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_fp_sa_paginate_scaling[1K]",
            "value": 1543.9438053029753,
            "unit": "iter/sec",
            "range": "stddev: 0.000019545731002236065",
            "extra": "mean: 647.6919668742512 usec\nrounds: 634"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_sa_pagination_lib_scaling[10K]",
            "value": 1748.7318398499579,
            "unit": "iter/sec",
            "range": "stddev: 0.00002079252000956229",
            "extra": "mean: 571.8429648343342 usec\nrounds: 455"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_paginate_scaling[100K]",
            "value": 700.7803367445994,
            "unit": "iter/sec",
            "range": "stddev: 0.00010643351105740282",
            "extra": "mean: 1.426980677918838 msec\nrounds: 385"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_pipeline_scaling[10K]",
            "value": 344.1566826312889,
            "unit": "iter/sec",
            "range": "stddev: 0.0000828157668408873",
            "extra": "mean: 2.905653298243076 msec\nrounds: 228"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_paginate_scaling[10K]",
            "value": 2276.365350206984,
            "unit": "iter/sec",
            "range": "stddev: 0.0000155376574670835",
            "extra": "mean: 439.29679386003323 usec\nrounds: 684"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_paginate_scaling[1K]",
            "value": 2333.2470686965908,
            "unit": "iter/sec",
            "range": "stddev: 0.000016979918800667386",
            "extra": "mean: 428.5872736823472 usec\nrounds: 855"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_search_scaling[100K]",
            "value": 123.25303763576869,
            "unit": "iter/sec",
            "range": "stddev: 0.000138638970534138",
            "extra": "mean: 8.113390300003402 msec\nrounds: 100"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_filter_scaling[100K]",
            "value": 154.43642764208136,
            "unit": "iter/sec",
            "range": "stddev: 0.00015055859831416093",
            "extra": "mean: 6.475156252108985 msec\nrounds: 119"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_pipeline_scaling[100K]",
            "value": 73.91183026327064,
            "unit": "iter/sec",
            "range": "stddev: 0.00020986963313137532",
            "extra": "mean: 13.529633841267962 msec\nrounds: 63"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_filter_scaling[10K]",
            "value": 462.6998177430863,
            "unit": "iter/sec",
            "range": "stddev: 0.000055779060493973006",
            "extra": "mean: 2.161228428568885 msec\nrounds: 266"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_pipeline_scaling[1K]",
            "value": 623.3954009737676,
            "unit": "iter/sec",
            "range": "stddev: 0.00006810880221866543",
            "extra": "mean: 1.6041183467795264 msec\nrounds: 372"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_fp_sa_paginate_scaling[100K]",
            "value": 1446.4586315692627,
            "unit": "iter/sec",
            "range": "stddev: 0.00004397498886632932",
            "extra": "mean: 691.3436569666014 usec\nrounds: 481"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_filter_scaling[1K]",
            "value": 618.9583093607347,
            "unit": "iter/sec",
            "range": "stddev: 0.0001315678466058312",
            "extra": "mean: 1.615617699732973 msec\nrounds: 373"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_sort_scaling[10K]",
            "value": 1159.2812507719675,
            "unit": "iter/sec",
            "range": "stddev: 0.00003020324546937264",
            "extra": "mean: 862.6034444480993 usec\nrounds: 621"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_search_scaling[1K]",
            "value": 632.71650582154,
            "unit": "iter/sec",
            "range": "stddev: 0.00012114013544611833",
            "extra": "mean: 1.5804866647212992 msec\nrounds: 343"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_sort_scaling[1K]",
            "value": 2646.4413295643176,
            "unit": "iter/sec",
            "range": "stddev: 0.000014981309564785211",
            "extra": "mean: 377.8659246394967 usec\nrounds: 1181"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_filter_scaling[10K]",
            "value": 924.231532094442,
            "unit": "iter/sec",
            "range": "stddev: 0.000031064289190091707",
            "extra": "mean: 1.0819799641912842 msec\nrounds: 391"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_fastapi_filter_scaling[1K]",
            "value": 2557.3587674448045,
            "unit": "iter/sec",
            "range": "stddev: 0.00001632287221839771",
            "extra": "mean: 391.0284363422165 usec\nrounds: 864"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_pipeline_scaling[10K]",
            "value": 540.5770000962741,
            "unit": "iter/sec",
            "range": "stddev: 0.00003334877915717679",
            "extra": "mean: 1.849875225586558 msec\nrounds: 297"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_paginate_scaling[10K]",
            "value": 762.7967510836323,
            "unit": "iter/sec",
            "range": "stddev: 0.00006557335068515009",
            "extra": "mean: 1.3109652061042416 msec\nrounds: 393"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_fastapi_filter_scaling[100K]",
            "value": 2592.560010116312,
            "unit": "iter/sec",
            "range": "stddev: 0.000016101665708939715",
            "extra": "mean: 385.7191332497396 usec\nrounds: 788"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_sort_scaling[100K]",
            "value": 185.70787290095393,
            "unit": "iter/sec",
            "range": "stddev: 0.0001263659505057619",
            "extra": "mean: 5.384801324676975 msec\nrounds: 154"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_fp_http_paginate_scaling[10K]",
            "value": 231.50817514312655,
            "unit": "iter/sec",
            "range": "stddev: 0.00009871919043095646",
            "extra": "mean: 4.319501889649316 msec\nrounds: 145"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_fp_http_paginate_scaling[1K]",
            "value": 227.84812381420133,
            "unit": "iter/sec",
            "range": "stddev: 0.00008963957254481249",
            "extra": "mean: 4.3888884545542695 msec\nrounds: 209"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_pipeline_scaling[10K]",
            "value": 132.76470933943605,
            "unit": "iter/sec",
            "range": "stddev: 0.00016448469497987566",
            "extra": "mean: 7.532122090090418 msec\nrounds: 111"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_sort_scaling[10K]",
            "value": 148.61901894101624,
            "unit": "iter/sec",
            "range": "stddev: 0.00014864445385330817",
            "extra": "mean: 6.728613922534901 msec\nrounds: 142"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_pipeline_scaling[1K]",
            "value": 229.1553950855424,
            "unit": "iter/sec",
            "range": "stddev: 0.000157996664342746",
            "extra": "mean: 4.363851000002446 msec\nrounds: 208"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_filter_scaling[100K]",
            "value": 116.47024018382673,
            "unit": "iter/sec",
            "range": "stddev: 0.0009300321674000387",
            "extra": "mean: 8.585884243234021 msec\nrounds: 111"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_filter_scaling[10K]",
            "value": 168.3252626313353,
            "unit": "iter/sec",
            "range": "stddev: 0.0003269913251438836",
            "extra": "mean: 5.940878893444487 msec\nrounds: 122"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_paginate_scaling[1K]",
            "value": 219.39655028542887,
            "unit": "iter/sec",
            "range": "stddev: 0.00014630488890614396",
            "extra": "mean: 4.557956807885208 msec\nrounds: 203"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_search_scaling[100K]",
            "value": 60.988323448608,
            "unit": "iter/sec",
            "range": "stddev: 0.0018257785653778029",
            "extra": "mean: 16.39658123808983 msec\nrounds: 63"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_search_scaling[10K]",
            "value": 173.39988763644112,
            "unit": "iter/sec",
            "range": "stddev: 0.00023475337028768502",
            "extra": "mean: 5.767016424466491 msec\nrounds: 139"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_search_scaling[1K]",
            "value": 215.14222476858208,
            "unit": "iter/sec",
            "range": "stddev: 0.00011476834227511905",
            "extra": "mean: 4.648088031420381 msec\nrounds: 191"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_filter_scaling[1K]",
            "value": 212.3936812563427,
            "unit": "iter/sec",
            "range": "stddev: 0.00014019946503072547",
            "extra": "mean: 4.708237995051641 msec\nrounds: 202"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_paginate_scaling[10K]",
            "value": 207.92480225955038,
            "unit": "iter/sec",
            "range": "stddev: 0.0001257777769225864",
            "extra": "mean: 4.809431049748987 msec\nrounds: 201"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_sort_scaling[1K]",
            "value": 192.13631073820522,
            "unit": "iter/sec",
            "range": "stddev: 0.00027518768405039346",
            "extra": "mean: 5.2046382912105935 msec\nrounds: 182"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_sort_scaling[100K]",
            "value": 30.911052262198773,
            "unit": "iter/sec",
            "range": "stddev: 0.0014682801211050034",
            "extra": "mean: 32.35088833332611 msec\nrounds: 33"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_sort_scaling[10K]",
            "value": 176.57359169281455,
            "unit": "iter/sec",
            "range": "stddev: 0.00022536325678464576",
            "extra": "mean: 5.663361040645887 msec\nrounds: 123"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_sort_scaling[1K]",
            "value": 199.507924811337,
            "unit": "iter/sec",
            "range": "stddev: 0.00029034483329670984",
            "extra": "mean: 5.012332221617972 msec\nrounds: 185"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_filter_scaling[100K]",
            "value": 50.36549499047625,
            "unit": "iter/sec",
            "range": "stddev: 0.0007053194192760464",
            "extra": "mean: 19.854862941168207 msec\nrounds: 51"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_paginate_scaling[1K]",
            "value": 200.68868210783577,
            "unit": "iter/sec",
            "range": "stddev: 0.0001195114869568778",
            "extra": "mean: 4.982842029241446 msec\nrounds: 171"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_search_scaling[100K]",
            "value": 9.035496925507795,
            "unit": "iter/sec",
            "range": "stddev: 0.0024722389256288863",
            "extra": "mean: 110.6745991110832 msec\nrounds: 9"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_pipeline_scaling[1K]",
            "value": 180.402855702512,
            "unit": "iter/sec",
            "range": "stddev: 0.00010547624102201714",
            "extra": "mean: 5.543149503403763 msec\nrounds: 147"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_fp_http_paginate_scaling[100K]",
            "value": 184.76920814799485,
            "unit": "iter/sec",
            "range": "stddev: 0.00013896201603337712",
            "extra": "mean: 5.412157198828436 msec\nrounds: 171"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_pipeline_scaling[10K]",
            "value": 163.04103828378373,
            "unit": "iter/sec",
            "range": "stddev: 0.00015431675053969655",
            "extra": "mean: 6.133425121222754 msec\nrounds: 132"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_search_scaling[1K]",
            "value": 159.99192533719338,
            "unit": "iter/sec",
            "range": "stddev: 0.00017270588694639068",
            "extra": "mean: 6.250315432434699 msec\nrounds: 148"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_filter_scaling[1K]",
            "value": 178.1779045701602,
            "unit": "iter/sec",
            "range": "stddev: 0.0001443010702235763",
            "extra": "mean: 5.612368168839 msec\nrounds: 154"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_pipeline_scaling[100K]",
            "value": 24.596476030277387,
            "unit": "iter/sec",
            "range": "stddev: 0.0010309218778340084",
            "extra": "mean: 40.656230541685545 msec\nrounds: 24"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_filter_scaling[10K]",
            "value": 172.19150118317842,
            "unit": "iter/sec",
            "range": "stddev: 0.0002150410574306875",
            "extra": "mean: 5.807487553849674 msec\nrounds: 130"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_paginate_scaling[100K]",
            "value": 186.53663545449933,
            "unit": "iter/sec",
            "range": "stddev: 0.0001516145971098363",
            "extra": "mean: 5.3608772215896625 msec\nrounds: 176"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_search_scaling[10K]",
            "value": 64.40913386350002,
            "unit": "iter/sec",
            "range": "stddev: 0.0005770383520040024",
            "extra": "mean: 15.52574829090645 msec\nrounds: 55"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_paginate_scaling[10K]",
            "value": 184.65852717458708,
            "unit": "iter/sec",
            "range": "stddev: 0.00012861465292709307",
            "extra": "mean: 5.415401147733301 msec\nrounds: 176"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_pipeline_scaling[100K]",
            "value": 55.358127771783835,
            "unit": "iter/sec",
            "range": "stddev: 0.0009688507058535621",
            "extra": "mean: 18.06419473076368 msec\nrounds: 52"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_sort_scaling[100K]",
            "value": 63.39514035614225,
            "unit": "iter/sec",
            "range": "stddev: 0.0007731382572707554",
            "extra": "mean: 15.774079754097611 msec\nrounds: 61"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_paginate_scaling[100K]",
            "value": 174.55409485106384,
            "unit": "iter/sec",
            "range": "stddev: 0.0002542960731410433",
            "extra": "mean: 5.728883076923735 msec\nrounds: 117"
          },
          {
            "name": "tests/perf/test_overhead.py::test_filter_plus_paginate_plus_serialize",
            "value": 791.6569550811975,
            "unit": "iter/sec",
            "range": "stddev: 0.000020754693022663306",
            "extra": "mean: 1.2631733904206444 msec\nrounds: 689"
          },
          {
            "name": "tests/perf/test_overhead.py::test_search_full_http",
            "value": 65.98448597048812,
            "unit": "iter/sec",
            "range": "stddev: 0.0004898259641747028",
            "extra": "mean: 15.155077519998486 msec\nrounds: 50"
          },
          {
            "name": "tests/perf/test_overhead.py::test_sort_plus_paginate_plus_serialize",
            "value": 453.2525797877859,
            "unit": "iter/sec",
            "range": "stddev: 0.000024865527961369207",
            "extra": "mean: 2.2062753629956227 msec\nrounds: 427"
          },
          {
            "name": "tests/perf/test_overhead.py::test_paginate_full_http",
            "value": 171.17389564617926,
            "unit": "iter/sec",
            "range": "stddev: 0.0003650830751331803",
            "extra": "mean: 5.842012277777594 msec\nrounds: 108"
          },
          {
            "name": "tests/perf/test_overhead.py::test_paginate_only",
            "value": 610789.217725955,
            "unit": "iter/sec",
            "range": "stddev: 4.092530600687298e-7",
            "extra": "mean: 1.637226020005929 usec\nrounds: 131683"
          },
          {
            "name": "tests/perf/test_overhead.py::test_pipeline_plus_paginate",
            "value": 93.09460814024168,
            "unit": "iter/sec",
            "range": "stddev: 0.0001703695197744443",
            "extra": "mean: 10.741760666671022 msec\nrounds: 81"
          },
          {
            "name": "tests/perf/test_overhead.py::test_filter_full_http",
            "value": 131.29117202177667,
            "unit": "iter/sec",
            "range": "stddev: 0.0006502578045650207",
            "extra": "mean: 7.616658337349098 msec\nrounds: 83"
          },
          {
            "name": "tests/perf/test_overhead.py::test_sort_full_http",
            "value": 117.06574658403844,
            "unit": "iter/sec",
            "range": "stddev: 0.0003926059694264951",
            "extra": "mean: 8.542208367347884 msec\nrounds: 98"
          },
          {
            "name": "tests/perf/test_overhead.py::test_sort_only",
            "value": 457.40810788487096,
            "unit": "iter/sec",
            "range": "stddev: 0.000018769228003620676",
            "extra": "mean: 2.1862314698009215 msec\nrounds: 447"
          },
          {
            "name": "tests/perf/test_overhead.py::test_search_plus_paginate",
            "value": 112.46861559105535,
            "unit": "iter/sec",
            "range": "stddev: 0.00009998834425609346",
            "extra": "mean: 8.891369336634122 msec\nrounds: 101"
          },
          {
            "name": "tests/perf/test_overhead.py::test_sort_plus_paginate",
            "value": 455.7741684026336,
            "unit": "iter/sec",
            "range": "stddev: 0.000025831338650438723",
            "extra": "mean: 2.1940690572805654 msec\nrounds: 419"
          },
          {
            "name": "tests/perf/test_overhead.py::test_filter_plus_paginate",
            "value": 797.2718645640103,
            "unit": "iter/sec",
            "range": "stddev: 0.000012092899481832456",
            "extra": "mean: 1.2542772979287962 msec\nrounds: 772"
          },
          {
            "name": "tests/perf/test_overhead.py::test_pipeline_ops_only",
            "value": 93.2932825893331,
            "unit": "iter/sec",
            "range": "stddev: 0.00011938586165575109",
            "extra": "mean: 10.71888534999772 msec\nrounds: 80"
          },
          {
            "name": "tests/perf/test_overhead.py::test_search_plus_paginate_plus_serialize",
            "value": 114.00718746904265,
            "unit": "iter/sec",
            "range": "stddev: 0.00017923696821420124",
            "extra": "mean: 8.771376807024017 msec\nrounds: 114"
          },
          {
            "name": "tests/perf/test_overhead.py::test_search_only",
            "value": 112.59403724258372,
            "unit": "iter/sec",
            "range": "stddev: 0.0005184809472960348",
            "extra": "mean: 8.881464991307677 msec\nrounds: 115"
          },
          {
            "name": "tests/perf/test_overhead.py::test_pipeline_full_http",
            "value": 58.584350332827015,
            "unit": "iter/sec",
            "range": "stddev: 0.0011753102229898353",
            "extra": "mean: 17.069404957447524 msec\nrounds: 47"
          },
          {
            "name": "tests/perf/test_overhead.py::test_pipeline_plus_serialize",
            "value": 93.46457664413089,
            "unit": "iter/sec",
            "range": "stddev: 0.00006774200757272622",
            "extra": "mean: 10.6992406739029 msec\nrounds: 92"
          },
          {
            "name": "tests/perf/test_overhead.py::test_paginate_plus_serialize",
            "value": 213218.2487957005,
            "unit": "iter/sec",
            "range": "stddev: 6.46722582801832e-7",
            "extra": "mean: 4.690030077857787 usec\nrounds: 56520"
          },
          {
            "name": "tests/perf/test_overhead.py::test_filter_only",
            "value": 803.4360071101619,
            "unit": "iter/sec",
            "range": "stddev: 0.000014282133723313711",
            "extra": "mean: 1.244654199152524 msec\nrounds: 708"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_filter_scaling[100K]",
            "value": 280.1128201848291,
            "unit": "iter/sec",
            "range": "stddev: 0.00020500810238630642",
            "extra": "mean: 3.5699901180537257 msec\nrounds: 144"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_search_scaling[100K]",
            "value": 155.73603856855343,
            "unit": "iter/sec",
            "range": "stddev: 0.0003170388849542273",
            "extra": "mean: 6.421121335764618 msec\nrounds: 137"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_paginate_scaling[100K]",
            "value": 2895459.3014934273,
            "unit": "iter/sec",
            "range": "stddev: 1.6639589258260446e-7",
            "extra": "mean: 345.3683494995828 nsec\nrounds: 185495"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_fp_paginate_scaling[100K]",
            "value": 17494.781204821244,
            "unit": "iter/sec",
            "range": "stddev: 0.000006694404087450218",
            "extra": "mean: 57.159903190124965 usec\nrounds: 4576"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_pipeline_scaling[1K]",
            "value": 12378.914461625342,
            "unit": "iter/sec",
            "range": "stddev: 0.000004845496833832021",
            "extra": "mean: 80.78252766831874 usec\nrounds: 8331"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_filter_scaling[1M]",
            "value": 24.39846434792763,
            "unit": "iter/sec",
            "range": "stddev: 0.000421561196658221",
            "extra": "mean: 40.986186086950944 msec\nrounds: 23"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_pipeline_scaling[100K]",
            "value": 113.01533180750909,
            "unit": "iter/sec",
            "range": "stddev: 0.00037554129776795544",
            "extra": "mean: 8.848356979593074 msec\nrounds: 98"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_fp_paginate_scaling[1M]",
            "value": 18000.52131557049,
            "unit": "iter/sec",
            "range": "stddev: 0.000005107370224215261",
            "extra": "mean: 55.55394660347962 usec\nrounds: 4401"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_search_scaling[1M]",
            "value": 16.707900279406836,
            "unit": "iter/sec",
            "range": "stddev: 0.00020626464611386513",
            "extra": "mean: 59.85192533334308 msec\nrounds: 18"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_sort_scaling[500K]",
            "value": 19.96314944350498,
            "unit": "iter/sec",
            "range": "stddev: 0.0005566812747101379",
            "extra": "mean: 50.09229645001483 msec\nrounds: 20"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_paginate_lib_scaling[10K]",
            "value": 384319.63419076457,
            "unit": "iter/sec",
            "range": "stddev: 0.000008720560794779388",
            "extra": "mean: 2.6020008113965636 usec\nrounds: 57931"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_search_scaling[10K]",
            "value": 1588.6934963283697,
            "unit": "iter/sec",
            "range": "stddev: 0.00001404533071739109",
            "extra": "mean: 629.4480353265752 usec\nrounds: 1104"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_paginate_lib_scaling[500K]",
            "value": 381269.55727813893,
            "unit": "iter/sec",
            "range": "stddev: 0.000008482294607003318",
            "extra": "mean: 2.6228162750232182 usec\nrounds: 56971"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_pipeline_scaling[1M]",
            "value": 8.969186592659137,
            "unit": "iter/sec",
            "range": "stddev: 0.0008303091928382943",
            "extra": "mean: 111.49283044445231 msec\nrounds: 9"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_sort_scaling[10K]",
            "value": 1598.0102300226383,
            "unit": "iter/sec",
            "range": "stddev: 0.0000137138201782452",
            "extra": "mean: 625.7782216987642 usec\nrounds: 1484"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_search_scaling[1K]",
            "value": 18377.503642870186,
            "unit": "iter/sec",
            "range": "stddev: 0.000002711185612269264",
            "extra": "mean: 54.41435460620705 usec\nrounds: 16390"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_filter_scaling[1K]",
            "value": 35821.62971925538,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018777163829090918",
            "extra": "mean: 27.91609448920368 usec\nrounds: 28924"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_fp_paginate_scaling[1K]",
            "value": 17483.531437985843,
            "unit": "iter/sec",
            "range": "stddev: 0.000005150631416345486",
            "extra": "mean: 57.19668269233845 usec\nrounds: 5824"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_paginate_scaling[10K]",
            "value": 4318753.460814498,
            "unit": "iter/sec",
            "range": "stddev: 3.1673651402757345e-8",
            "extra": "mean: 231.54829491271855 nsec\nrounds: 191205"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_sort_scaling[1K]",
            "value": 13702.268676764985,
            "unit": "iter/sec",
            "range": "stddev: 0.000003042297701238402",
            "extra": "mean: 72.98061537033686 usec\nrounds: 10397"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_fp_paginate_scaling[10K]",
            "value": 18129.256497124705,
            "unit": "iter/sec",
            "range": "stddev: 0.000005204042681841751",
            "extra": "mean: 55.15946007816701 usec\nrounds: 5160"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_paginate_lib_scaling[1M]",
            "value": 385893.01469571743,
            "unit": "iter/sec",
            "range": "stddev: 0.000008472735414710733",
            "extra": "mean: 2.591391815652624 usec\nrounds: 55424"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_paginate_scaling[1K]",
            "value": 4291004.294068675,
            "unit": "iter/sec",
            "range": "stddev: 2.8155945246937272e-8",
            "extra": "mean: 233.04567683193892 nsec\nrounds: 195695"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_paginate_lib_scaling[100K]",
            "value": 389566.28405505454,
            "unit": "iter/sec",
            "range": "stddev: 0.000007888734040504564",
            "extra": "mean: 2.5669572571600607 usec\nrounds: 58817"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_sort_scaling[100K]",
            "value": 145.65886345454624,
            "unit": "iter/sec",
            "range": "stddev: 0.0001489681810664912",
            "extra": "mean: 6.86535632836416 msec\nrounds: 134"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_paginate_lib_scaling[1K]",
            "value": 382851.1959987439,
            "unit": "iter/sec",
            "range": "stddev: 0.000008523491914581778",
            "extra": "mean: 2.6119808699860534 usec\nrounds: 89598"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_pipeline_scaling[500K]",
            "value": 18.40632623727904,
            "unit": "iter/sec",
            "range": "stddev: 0.0006494161612747032",
            "extra": "mean: 54.32914678946968 msec\nrounds: 19"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_sort_scaling[1M]",
            "value": 10.075990256938805,
            "unit": "iter/sec",
            "range": "stddev: 0.000540704245249423",
            "extra": "mean: 99.24582839997811 msec\nrounds: 10"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_pipeline_scaling[10K]",
            "value": 1401.4605244714,
            "unit": "iter/sec",
            "range": "stddev: 0.000016831788453641093",
            "extra": "mean: 713.5413253093076 usec\nrounds: 1288"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_filter_scaling[10K]",
            "value": 3631.7239277601443,
            "unit": "iter/sec",
            "range": "stddev: 0.000008128508130221721",
            "extra": "mean: 275.3513262272519 usec\nrounds: 2955"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_paginate_scaling[500K]",
            "value": 4385162.034126148,
            "unit": "iter/sec",
            "range": "stddev: 3.168386901451575e-8",
            "extra": "mean: 228.04174445956878 nsec\nrounds: 189394"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_fp_paginate_scaling[500K]",
            "value": 17740.43995108234,
            "unit": "iter/sec",
            "range": "stddev: 0.000006506400873449969",
            "extra": "mean: 56.36838786171086 usec\nrounds: 4383"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_paginate_scaling[1M]",
            "value": 4391586.65978552,
            "unit": "iter/sec",
            "range": "stddev: 3.4312601706585514e-8",
            "extra": "mean: 227.708133180459 nsec\nrounds: 190115"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_filter_scaling[500K]",
            "value": 61.68173081242973,
            "unit": "iter/sec",
            "range": "stddev: 0.00038483646860786795",
            "extra": "mean: 16.212255830513858 msec\nrounds: 59"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_search_scaling[500K]",
            "value": 36.266913485548706,
            "unit": "iter/sec",
            "range": "stddev: 0.00019309284091651206",
            "extra": "mean: 27.57334175676324 msec\nrounds: 37"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_sa_sync_1k",
            "value": 26160.379857439173,
            "unit": "iter/sec",
            "range": "stddev: 0.000004197702656023371",
            "extra": "mean: 38.225744635570805 usec\nrounds: 4288"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_sa_async_1k",
            "value": 26984.074521290375,
            "unit": "iter/sec",
            "range": "stddev: 0.0000037906487907688754",
            "extra": "mean: 37.058895579724336 usec\nrounds: 10180"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_memory_100k",
            "value": 78.6193528431391,
            "unit": "iter/sec",
            "range": "stddev: 0.00020543602674926356",
            "extra": "mean: 12.719514519474544 msec\nrounds: 77"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_sa_async_10k",
            "value": 27102.81624160734,
            "unit": "iter/sec",
            "range": "stddev: 0.000003441030376404749",
            "extra": "mean: 36.896534702723386 usec\nrounds: 5648"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_memory_10k_single",
            "value": 800.0831095836443,
            "unit": "iter/sec",
            "range": "stddev: 0.000016607207518221244",
            "extra": "mean: 1.249870154764785 msec\nrounds: 672"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_sa_sync_10k",
            "value": 26805.322042304182,
            "unit": "iter/sec",
            "range": "stddev: 0.000004093607974302595",
            "extra": "mean: 37.306024468640935 usec\nrounds: 5558"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_memory_10k_multi",
            "value": 259.1990409600193,
            "unit": "iter/sec",
            "range": "stddev: 0.00003350339241219491",
            "extra": "mean: 3.858038966101912 msec\nrounds: 236"
          },
          {
            "name": "tests/perf/test_search.py::test_bench_search_sa_sync_10k",
            "value": 26729.299552156022,
            "unit": "iter/sec",
            "range": "stddev: 0.000003698266988077921",
            "extra": "mean: 37.412128890573136 usec\nrounds: 5431"
          },
          {
            "name": "tests/perf/test_search.py::test_bench_search_memory_10k",
            "value": 354.28810906525604,
            "unit": "iter/sec",
            "range": "stddev: 0.00005235536862083737",
            "extra": "mean: 2.8225615661738477 msec\nrounds: 272"
          },
          {
            "name": "tests/perf/test_search.py::test_bench_search_sa_async_10k",
            "value": 26355.71691852576,
            "unit": "iter/sec",
            "range": "stddev: 0.0000034585223809122967",
            "extra": "mean: 37.94243211411516 usec\nrounds: 5848"
          },
          {
            "name": "tests/perf/test_search.py::test_bench_search_memory_100k",
            "value": 24.98704653286871,
            "unit": "iter/sec",
            "range": "stddev: 0.00025253804516435",
            "extra": "mean: 40.020736291684976 msec\nrounds: 24"
          },
          {
            "name": "tests/perf/test_search.py::test_bench_search_sa_sync_1k",
            "value": 26052.272521882045,
            "unit": "iter/sec",
            "range": "stddev: 0.000003458738319737742",
            "extra": "mean: 38.38436739674328 usec\nrounds: 5196"
          },
          {
            "name": "tests/perf/test_search.py::test_bench_search_sa_async_1k",
            "value": 26569.84234777071,
            "unit": "iter/sec",
            "range": "stddev: 0.0000036819079695307642",
            "extra": "mean: 37.63665538210854 usec\nrounds: 10220"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "git.owiwz@passinbox.com",
            "name": "CybLow"
          },
          "committer": {
            "email": "git.owiwz@passinbox.com",
            "name": "CybLow"
          },
          "distinct": true,
          "id": "48840662293eac58a197e552a786c2ce5b0d7884",
          "message": "feat(bench): add competitor comparison and scaling tabs to dashboard\n\n- New \"vs Competitors\" tab with 9 comparison tables:\n  - In-memory: pagination, pipeline, filter, sort, search\n  - SQLAlchemy: pagination, filter\n  - Scaling: memory pagination, SA sync pagination\n- Each table shows pypaginate vs competitors at each scale (1K/10K/100K)\n- Speed diff badges (Nx faster/slower) relative to pypaginate\n- Visual bar fills showing relative performance\n- New \"Scaling\" tab showing how pypaginate scales from 1K to 1M items\n- Same backend comparison (SA vs SA, memory vs memory)",
          "timestamp": "2026-03-17T04:38:09+01:00",
          "tree_id": "32ce34bab189ac74d2c1d93b48955cc527462790",
          "url": "https://github.com/CybLow/pypaginate/commit/48840662293eac58a197e552a786c2ce5b0d7884"
        },
        "date": 1773719635109,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_memory_1k",
            "value": 583728.3856582502,
            "unit": "iter/sec",
            "range": "stddev: 3.870394263649483e-7",
            "extra": "mean: 1.7131255299026358 usec\nrounds: 34430"
          },
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_sa_async_1k",
            "value": 942.8554821395144,
            "unit": "iter/sec",
            "range": "stddev: 0.000050187854017160795",
            "extra": "mean: 1.060607928726059 msec\nrounds: 463"
          },
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_memory_100k",
            "value": 589736.1460896897,
            "unit": "iter/sec",
            "range": "stddev: 4.1958668133143726e-7",
            "extra": "mean: 1.695673576447043 usec\nrounds: 134157"
          },
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_memory_10k",
            "value": 583911.6325416482,
            "unit": "iter/sec",
            "range": "stddev: 4.946184637968827e-7",
            "extra": "mean: 1.7125879058911775 usec\nrounds: 106068"
          },
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_sa_async_10k",
            "value": 913.8302749897816,
            "unit": "iter/sec",
            "range": "stddev: 0.0000819949507890654",
            "extra": "mean: 1.0942951085869659 msec\nrounds: 396"
          },
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_sa_sync_1k",
            "value": 2582.611837912933,
            "unit": "iter/sec",
            "range": "stddev: 0.00002442676413997158",
            "extra": "mean: 387.204916093052 usec\nrounds: 727"
          },
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_sa_sync_10k",
            "value": 2557.441229226925,
            "unit": "iter/sec",
            "range": "stddev: 0.00002270471275325156",
            "extra": "mean: 391.01582807526904 usec\nrounds: 634"
          },
          {
            "name": "tests/perf/test_comparison.py::test_raw_list_slice_10k",
            "value": 4896231.829357445,
            "unit": "iter/sec",
            "range": "stddev: 3.018817637114162e-8",
            "extra": "mean: 204.2386951540526 nsec\nrounds: 191939"
          },
          {
            "name": "tests/perf/test_comparison.py::test_memory_sort_10k",
            "value": 457.7128315956866,
            "unit": "iter/sec",
            "range": "stddev: 0.000020554818752739303",
            "extra": "mean: 2.1847759795454764 msec\nrounds: 440"
          },
          {
            "name": "tests/perf/test_comparison.py::test_memory_pipeline_10k",
            "value": 314.4536953320187,
            "unit": "iter/sec",
            "range": "stddev: 0.000029430597851843594",
            "extra": "mean: 3.1801184557368334 msec\nrounds: 305"
          },
          {
            "name": "tests/perf/test_comparison.py::test_memory_paginate_10k",
            "value": 575730.8587371262,
            "unit": "iter/sec",
            "range": "stddev: 3.83222906292567e-7",
            "extra": "mean: 1.7369227041147561 usec\nrounds: 122775"
          },
          {
            "name": "tests/perf/test_comparison.py::test_sa_sync_paginate_10k",
            "value": 2486.6288446749336,
            "unit": "iter/sec",
            "range": "stddev: 0.000016372036414930077",
            "extra": "mean: 402.15088879929954 usec\nrounds: 1241"
          },
          {
            "name": "tests/perf/test_comparison.py::test_raw_list_sort_10k",
            "value": 1612.6525821475632,
            "unit": "iter/sec",
            "range": "stddev: 0.00002721950579830415",
            "extra": "mean: 620.0963623971035 usec\nrounds: 1468"
          },
          {
            "name": "tests/perf/test_comparison.py::test_sa_async_paginate_10k",
            "value": 886.1191024322713,
            "unit": "iter/sec",
            "range": "stddev: 0.0001123183258477232",
            "extra": "mean: 1.1285164683338185 msec\nrounds: 600"
          },
          {
            "name": "tests/perf/test_comparison.py::test_raw_list_search_10k",
            "value": 1834.4251328849552,
            "unit": "iter/sec",
            "range": "stddev: 0.000045926327336073415",
            "extra": "mean: 545.129905861748 usec\nrounds: 1689"
          },
          {
            "name": "tests/perf/test_comparison.py::test_raw_pipeline_10k",
            "value": 1429.505998370249,
            "unit": "iter/sec",
            "range": "stddev: 0.00001657930336574485",
            "extra": "mean: 699.5423601860222 usec\nrounds: 1291"
          },
          {
            "name": "tests/perf/test_comparison.py::test_memory_filter_10k",
            "value": 792.0415009778944,
            "unit": "iter/sec",
            "range": "stddev: 0.0001100964031896722",
            "extra": "mean: 1.262560104193214 msec\nrounds: 787"
          },
          {
            "name": "tests/perf/test_comparison.py::test_raw_list_filter_10k",
            "value": 3765.0514223498144,
            "unit": "iter/sec",
            "range": "stddev: 0.000007059965008553678",
            "extra": "mean: 265.6006220961221 usec\nrounds: 3702"
          },
          {
            "name": "tests/perf/test_comparison.py::test_memory_search_10k",
            "value": 386.1332788813864,
            "unit": "iter/sec",
            "range": "stddev: 0.000020646490554178806",
            "extra": "mean: 2.589779370731687 msec\nrounds: 205"
          },
          {
            "name": "tests/perf/test_search.py::test_bench_search_sa_async_1k",
            "value": 26077.081268296817,
            "unit": "iter/sec",
            "range": "stddev: 0.000003743051556957598",
            "extra": "mean: 38.34784996493257 usec\nrounds: 4279"
          },
          {
            "name": "tests/perf/test_search.py::test_bench_search_sa_sync_10k",
            "value": 26303.70772683583,
            "unit": "iter/sec",
            "range": "stddev: 0.000004917611794962879",
            "extra": "mean: 38.0174540557174 usec\nrounds: 9838"
          },
          {
            "name": "tests/perf/test_search.py::test_bench_search_sa_sync_1k",
            "value": 26321.477172846364,
            "unit": "iter/sec",
            "range": "stddev: 0.0000034979896470624137",
            "extra": "mean: 37.99178873713119 usec\nrounds: 9074"
          },
          {
            "name": "tests/perf/test_search.py::test_bench_search_sa_async_10k",
            "value": 26442.336762232055,
            "unit": "iter/sec",
            "range": "stddev: 0.000003746147611272883",
            "extra": "mean: 37.818140241989255 usec\nrounds: 11252"
          },
          {
            "name": "tests/perf/test_search.py::test_bench_search_memory_100k",
            "value": 25.25190432405778,
            "unit": "iter/sec",
            "range": "stddev: 0.002510689829018469",
            "extra": "mean: 39.6009737391286 msec\nrounds: 23"
          },
          {
            "name": "tests/perf/test_search.py::test_bench_search_memory_10k",
            "value": 387.91395449194147,
            "unit": "iter/sec",
            "range": "stddev: 0.000021039242475357108",
            "extra": "mean: 2.577891278259684 msec\nrounds: 345"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_searched_json_dumps[20]",
            "value": 53449.21796708199,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015221500786135606",
            "extra": "mean: 18.70934763939623 usec\nrounds: 20504"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_searched_json_dumps[100]",
            "value": 52815.46099990039,
            "unit": "iter/sec",
            "range": "stddev: 0.0000014293438249958841",
            "extra": "mean: 18.933849692268822 usec\nrounds: 28109"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_json_dumps[100]",
            "value": 122640.07873339063,
            "unit": "iter/sec",
            "range": "stddev: 8.669683381862505e-7",
            "extra": "mean: 8.153941275379617 usec\nrounds: 62461"
          },
          {
            "name": "tests/perf/test_serialization.py::test_sorted_page_model_dump_json[100]",
            "value": 30803.40117578187,
            "unit": "iter/sec",
            "range": "stddev: 0.0000019979672166337435",
            "extra": "mean: 32.46394754570856 usec\nrounds: 17215"
          },
          {
            "name": "tests/perf/test_serialization.py::test_cursor_page_model_dump[1000]",
            "value": 38053.18988397388,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015295241504308747",
            "extra": "mean: 26.279005861244514 usec\nrounds: 25933"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_searched_json_dumps[1000]",
            "value": 53777.2676069884,
            "unit": "iter/sec",
            "range": "stddev: 0.0000014436997303980338",
            "extra": "mean: 18.595217728578852 usec\nrounds: 25913"
          },
          {
            "name": "tests/perf/test_serialization.py::test_fp_filtered_page_serialize[20]",
            "value": 48419.595538300026,
            "unit": "iter/sec",
            "range": "stddev: 0.0000014321228328325132",
            "extra": "mean: 20.652795399932607 usec\nrounds: 14565"
          },
          {
            "name": "tests/perf/test_serialization.py::test_filtered_page_model_dump_json[20]",
            "value": 125435.37697320762,
            "unit": "iter/sec",
            "range": "stddev: 8.109750259398529e-7",
            "extra": "mean: 7.972232588048865 usec\nrounds: 57561"
          },
          {
            "name": "tests/perf/test_serialization.py::test_fp_filtered_page_serialize[100]",
            "value": 10537.835782717651,
            "unit": "iter/sec",
            "range": "stddev: 0.000004554164572170207",
            "extra": "mean: 94.89614571903164 usec\nrounds: 6938"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_sorted_json_dumps[20]",
            "value": 53154.4869684898,
            "unit": "iter/sec",
            "range": "stddev: 0.000001479206095101429",
            "extra": "mean: 18.813087229922925 usec\nrounds: 21942"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_dict_dump[100]",
            "value": 5435147.463615188,
            "unit": "iter/sec",
            "range": "stddev: 2.2516122410262136e-8",
            "extra": "mean: 183.98764830121087 nsec\nrounds: 196851"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_filtered_json_dumps[1000]",
            "value": 1278.8840983065618,
            "unit": "iter/sec",
            "range": "stddev: 0.000011371300985547716",
            "extra": "mean: 781.9316866353668 usec\nrounds: 868"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_dict_construction[100]",
            "value": 7493906.609530656,
            "unit": "iter/sec",
            "range": "stddev: 1.0269216329731939e-8",
            "extra": "mean: 133.4417483570074 nsec\nrounds: 73938"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_create[100]",
            "value": 2473852.9411797617,
            "unit": "iter/sec",
            "range": "stddev: 1.7776749485509352e-7",
            "extra": "mean: 404.2277466675556 nsec\nrounds: 192679"
          },
          {
            "name": "tests/perf/test_serialization.py::test_searched_page_model_dump_json[1000]",
            "value": 124739.69515609297,
            "unit": "iter/sec",
            "range": "stddev: 8.552554768255805e-7",
            "extra": "mean: 8.016694274814848 usec\nrounds: 38672"
          },
          {
            "name": "tests/perf/test_serialization.py::test_sorted_page_model_dump_json[20]",
            "value": 124743.35209547578,
            "unit": "iter/sec",
            "range": "stddev: 8.695538038162546e-7",
            "extra": "mean: 8.01645925976578 usec\nrounds: 62653"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_create[20]",
            "value": 2326791.5528693576,
            "unit": "iter/sec",
            "range": "stddev: 2.2311049481294303e-7",
            "extra": "mean: 429.77635825040625 nsec\nrounds: 146994"
          },
          {
            "name": "tests/perf/test_serialization.py::test_sorted_page_model_dump_json[1000]",
            "value": 2914.470230782076,
            "unit": "iter/sec",
            "range": "stddev: 0.000011459168401521933",
            "extra": "mean: 343.1155307191652 usec\nrounds: 2295"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_model_dump_json[1000]",
            "value": 39634.04320725638,
            "unit": "iter/sec",
            "range": "stddev: 0.000001754494204244481",
            "extra": "mean: 25.230834885321908 usec\nrounds: 32002"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_model_dump[100]",
            "value": 247013.03098720743,
            "unit": "iter/sec",
            "range": "stddev: 5.607618775019945e-7",
            "extra": "mean: 4.048369415991616 usec\nrounds: 75438"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_filtered_json_dumps[100]",
            "value": 12482.989364972114,
            "unit": "iter/sec",
            "range": "stddev: 0.0000033132519471253126",
            "extra": "mean: 80.10901641926007 usec\nrounds: 7552"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_model_dump_json[20]",
            "value": 541526.6431727611,
            "unit": "iter/sec",
            "range": "stddev: 3.9056627888125994e-7",
            "extra": "mean: 1.8466312093918045 usec\nrounds: 68223"
          },
          {
            "name": "tests/perf/test_serialization.py::test_cursor_page_model_dump[20]",
            "value": 510442.81495804974,
            "unit": "iter/sec",
            "range": "stddev: 3.816462554157263e-7",
            "extra": "mean: 1.9590833109918182 usec\nrounds: 74600"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_json_dumps[1000]",
            "value": 18203.196332789143,
            "unit": "iter/sec",
            "range": "stddev: 0.0000028745141578667944",
            "extra": "mean: 54.93540704160373 usec\nrounds: 10225"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_json_dumps[20]",
            "value": 276890.2920884879,
            "unit": "iter/sec",
            "range": "stddev: 6.06189899041832e-7",
            "extra": "mean: 3.611538680021409 usec\nrounds: 98242"
          },
          {
            "name": "tests/perf/test_serialization.py::test_filtered_page_model_dump_json[100]",
            "value": 30687.98974535263,
            "unit": "iter/sec",
            "range": "stddev: 0.0000019150812871208984",
            "extra": "mean: 32.58603800046693 usec\nrounds: 19184"
          },
          {
            "name": "tests/perf/test_serialization.py::test_searched_page_model_dump_json[100]",
            "value": 125284.2682284268,
            "unit": "iter/sec",
            "range": "stddev: 8.889666645865846e-7",
            "extra": "mean: 7.981848113417815 usec\nrounds: 64772"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_model_dump[1000]",
            "value": 37099.94207002529,
            "unit": "iter/sec",
            "range": "stddev: 0.0000038113245729059598",
            "extra": "mean: 26.954219985371484 usec\nrounds: 27520"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_dict_dump[20]",
            "value": 5530917.274806312,
            "unit": "iter/sec",
            "range": "stddev: 1.773991460006913e-8",
            "extra": "mean: 180.80183635270035 nsec\nrounds: 54630"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_dict_construction[1000]",
            "value": 6934420.815210372,
            "unit": "iter/sec",
            "range": "stddev: 7.328736512970968e-8",
            "extra": "mean: 144.2081504206203 nsec\nrounds: 73341"
          },
          {
            "name": "tests/perf/test_serialization.py::test_cursor_page_model_dump[100]",
            "value": 248697.03837991614,
            "unit": "iter/sec",
            "range": "stddev: 5.706057044417594e-7",
            "extra": "mean: 4.020956608547841 usec\nrounds: 53121"
          },
          {
            "name": "tests/perf/test_serialization.py::test_pipeline_page_model_dump_json",
            "value": 345260.7471443862,
            "unit": "iter/sec",
            "range": "stddev: 5.769636628776467e-7",
            "extra": "mean: 2.8963616868436115 usec\nrounds: 24947"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_dict_dump[1000]",
            "value": 5502476.889671297,
            "unit": "iter/sec",
            "range": "stddev: 1.221621523214083e-8",
            "extra": "mean: 181.73633802570427 nsec\nrounds: 51718"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_dict_construction[20]",
            "value": 7400365.320554699,
            "unit": "iter/sec",
            "range": "stddev: 1.0236885367858828e-8",
            "extra": "mean: 135.12846416139266 nsec\nrounds: 73341"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_model_dump_json[100]",
            "value": 269705.3660466351,
            "unit": "iter/sec",
            "range": "stddev: 5.20736023471934e-7",
            "extra": "mean: 3.7077497369002614 usec\nrounds: 61767"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_pipeline_json_dumps",
            "value": 52013.206681385804,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015017805384043209",
            "extra": "mean: 19.225886343167428 usec\nrounds: 17676"
          },
          {
            "name": "tests/perf/test_serialization.py::test_searched_page_model_dump_json[20]",
            "value": 122891.26704627003,
            "unit": "iter/sec",
            "range": "stddev: 9.053850306909033e-7",
            "extra": "mean: 8.137274714756485 usec\nrounds: 40755"
          },
          {
            "name": "tests/perf/test_serialization.py::test_fp_filtered_page_serialize[1000]",
            "value": 10439.324462310795,
            "unit": "iter/sec",
            "range": "stddev: 0.000004151137847178008",
            "extra": "mean: 95.7916389714977 usec\nrounds: 6728"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_sorted_json_dumps[100]",
            "value": 12427.458735390108,
            "unit": "iter/sec",
            "range": "stddev: 0.000003842008046433476",
            "extra": "mean: 80.46697408475515 usec\nrounds: 8142"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_create[1000]",
            "value": 2328347.409669172,
            "unit": "iter/sec",
            "range": "stddev: 1.6599566248820257e-7",
            "extra": "mean: 429.48917152448786 nsec\nrounds: 174217"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_sorted_json_dumps[1000]",
            "value": 1265.0525623520812,
            "unit": "iter/sec",
            "range": "stddev: 0.000019083355847908394",
            "extra": "mean: 790.4809885059042 usec\nrounds: 783"
          },
          {
            "name": "tests/perf/test_serialization.py::test_filtered_page_model_dump_json[1000]",
            "value": 3025.856691072503,
            "unit": "iter/sec",
            "range": "stddev: 0.000008581484348081817",
            "extra": "mean: 330.48491785827235 usec\nrounds: 2727"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_model_dump[20]",
            "value": 504084.24624502735,
            "unit": "iter/sec",
            "range": "stddev: 4.097963971195029e-7",
            "extra": "mean: 1.9837953823177326 usec\nrounds: 78654"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_filtered_json_dumps[20]",
            "value": 53356.46639206491,
            "unit": "iter/sec",
            "range": "stddev: 0.0000014738478349192347",
            "extra": "mean: 18.74187081003397 usec\nrounds: 23121"
          },
          {
            "name": "tests/perf/test_serialization.py::test_pipeline_page_model_dump",
            "value": 4729157.572179318,
            "unit": "iter/sec",
            "range": "stddev: 3.172337209134441e-8",
            "extra": "mean: 211.45415113313692 nsec\nrounds: 189394"
          },
          {
            "name": "tests/perf/test_pipeline.py::test_bench_pipeline_sa_async_1k",
            "value": 688.4004992291976,
            "unit": "iter/sec",
            "range": "stddev: 0.00008878210836178964",
            "extra": "mean: 1.4526427582776313 msec\nrounds: 302"
          },
          {
            "name": "tests/perf/test_pipeline.py::test_bench_pipeline_sa_async_10k",
            "value": 241.38542091614536,
            "unit": "iter/sec",
            "range": "stddev: 0.0006584768832901967",
            "extra": "mean: 4.142752268155371 msec\nrounds: 179"
          },
          {
            "name": "tests/perf/test_pipeline.py::test_bench_pipeline_sa_sync_1k",
            "value": 1280.1671707552457,
            "unit": "iter/sec",
            "range": "stddev: 0.000025063879018596627",
            "extra": "mean: 781.1479803923119 usec\nrounds: 510"
          },
          {
            "name": "tests/perf/test_pipeline.py::test_bench_pipeline_memory_100k",
            "value": 32.09609669087191,
            "unit": "iter/sec",
            "range": "stddev: 0.0005129249751730168",
            "extra": "mean: 31.15643654838561 msec\nrounds: 31"
          },
          {
            "name": "tests/perf/test_pipeline.py::test_bench_pipeline_memory_10k",
            "value": 301.221944163993,
            "unit": "iter/sec",
            "range": "stddev: 0.00007809493466014399",
            "extra": "mean: 3.3198112533779223 msec\nrounds: 296"
          },
          {
            "name": "tests/perf/test_pipeline.py::test_bench_pipeline_sa_sync_10k",
            "value": 295.28985815716794,
            "unit": "iter/sec",
            "range": "stddev: 0.000030392894994012163",
            "extra": "mean: 3.3865030321080325 msec\nrounds: 218"
          },
          {
            "name": "tests/perf/test_sorting.py::test_bench_sort_memory_10k",
            "value": 457.5954393363288,
            "unit": "iter/sec",
            "range": "stddev: 0.00013986686821937857",
            "extra": "mean: 2.185336465438434 msec\nrounds: 434"
          },
          {
            "name": "tests/perf/test_sorting.py::test_bench_sort_memory_100k",
            "value": 44.2267160088172,
            "unit": "iter/sec",
            "range": "stddev: 0.00024258868470322957",
            "extra": "mean: 22.610767659091767 msec\nrounds: 44"
          },
          {
            "name": "tests/perf/test_sorting.py::test_bench_sort_sa_async_10k",
            "value": 50585.04992548404,
            "unit": "iter/sec",
            "range": "stddev: 0.000006053975442374268",
            "extra": "mean: 19.76868662723636 usec\nrounds: 14896"
          },
          {
            "name": "tests/perf/test_sorting.py::test_bench_sort_sa_sync_10k",
            "value": 51396.04246465287,
            "unit": "iter/sec",
            "range": "stddev: 0.000006032562034652493",
            "extra": "mean: 19.456750987933365 usec\nrounds: 15694"
          },
          {
            "name": "tests/perf/test_sorting.py::test_bench_sort_sa_sync_1k",
            "value": 51560.84731674505,
            "unit": "iter/sec",
            "range": "stddev: 0.000005891161499115163",
            "extra": "mean: 19.394561029163636 usec\nrounds: 8668"
          },
          {
            "name": "tests/perf/test_sorting.py::test_bench_sort_sa_async_1k",
            "value": 51251.82615455358,
            "unit": "iter/sec",
            "range": "stddev: 0.000005982099244154322",
            "extra": "mean: 19.511499882646675 usec\nrounds: 8526"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_sa_filter",
            "value": 942.1890000082615,
            "unit": "iter/sec",
            "range": "stddev: 0.000027209646917447633",
            "extra": "mean: 1.0613581775962484 msec\nrounds: 366"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_python_filter_paginate",
            "value": 3675.8611835954575,
            "unit": "iter/sec",
            "range": "stddev: 0.000006765841403559834",
            "extra": "mean: 272.0450936675126 usec\nrounds: 3032"
          },
          {
            "name": "tests/perf/test_competitors.py::test_fastapi_filter_10k",
            "value": 2584.527322752567,
            "unit": "iter/sec",
            "range": "stddev: 0.000024003079878294046",
            "extra": "mean: 386.9179448004374 usec\nrounds: 779"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_search_paginate",
            "value": 391.9255256438374,
            "unit": "iter/sec",
            "range": "stddev: 0.000023456351687047276",
            "extra": "mean: 2.5515051574077643 msec\nrounds: 324"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_full_pipeline",
            "value": 328.5315586973714,
            "unit": "iter/sec",
            "range": "stddev: 0.00007801929231230252",
            "extra": "mean: 3.043847610759231 msec\nrounds: 316"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_python_search_paginate",
            "value": 1859.9971788080438,
            "unit": "iter/sec",
            "range": "stddev: 0.000012210037727063832",
            "extra": "mean: 537.6352240710588 usec\nrounds: 1803"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_sqlalchemy",
            "value": 2284.463439062179,
            "unit": "iter/sec",
            "range": "stddev: 0.000015331212989003194",
            "extra": "mean: 437.73955096016823 usec\nrounds: 677"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_filter_paginate",
            "value": 802.0254552678376,
            "unit": "iter/sec",
            "range": "stddev: 0.000012924345147751037",
            "extra": "mean: 1.2468432185435416 msec\nrounds: 755"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_sa_async",
            "value": 929.0284389103674,
            "unit": "iter/sec",
            "range": "stddev: 0.000054955620163657046",
            "extra": "mean: 1.0763933138288784 msec\nrounds: 564"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_100k",
            "value": 588251.1917813846,
            "unit": "iter/sec",
            "range": "stddev: 3.591744056105184e-7",
            "extra": "mean: 1.6999540569934555 usec\nrounds: 121433"
          },
          {
            "name": "tests/perf/test_competitors.py::test_paginate_lib_100k",
            "value": 373061.68131653353,
            "unit": "iter/sec",
            "range": "stddev: 0.000010447588409090917",
            "extra": "mean: 2.680521881719407 usec\nrounds: 58542"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_sa_sync",
            "value": 2494.150005387352,
            "unit": "iter/sec",
            "range": "stddev: 0.000016190011070541886",
            "extra": "mean: 400.93819451115803 usec\nrounds: 1239"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_sort_paginate",
            "value": 460.40482557109897,
            "unit": "iter/sec",
            "range": "stddev: 0.00003516267127594706",
            "extra": "mean: 2.172001561364115 msec\nrounds: 440"
          },
          {
            "name": "tests/perf/test_competitors.py::test_paginate_lib_full_pipeline",
            "value": 1319.756120371097,
            "unit": "iter/sec",
            "range": "stddev: 0.0007713000249701323",
            "extra": "mean: 757.7157510880221 usec\nrounds: 1378"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_python_slice",
            "value": 4905109.531259049,
            "unit": "iter/sec",
            "range": "stddev: 2.401504459558057e-8",
            "extra": "mean: 203.8690458645882 nsec\nrounds: 194553"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_python_full_pipeline",
            "value": 1434.8529793420435,
            "unit": "iter/sec",
            "range": "stddev: 0.00001633655587972288",
            "extra": "mean: 696.935514925406 usec\nrounds: 1206"
          },
          {
            "name": "tests/perf/test_competitors.py::test_sqlalchemy_pagination_lib_10k",
            "value": 1769.2282245860313,
            "unit": "iter/sec",
            "range": "stddev: 0.00002377777248018926",
            "extra": "mean: 565.2182042449513 usec\nrounds: 377"
          },
          {
            "name": "tests/perf/test_competitors.py::test_fastapi_pagination_full_pipeline",
            "value": 1266.8697046428917,
            "unit": "iter/sec",
            "range": "stddev: 0.000021818510331356997",
            "extra": "mean: 789.3471572768269 usec\nrounds: 426"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_python_100k",
            "value": 4477917.896946442,
            "unit": "iter/sec",
            "range": "stddev: 2.63087550991962e-8",
            "extra": "mean: 223.3180739383568 nsec\nrounds: 188324"
          },
          {
            "name": "tests/perf/test_competitors.py::test_paginate_lib_memory",
            "value": 375260.5043594233,
            "unit": "iter/sec",
            "range": "stddev: 0.00001099356082234295",
            "extra": "mean: 2.664815477203013 usec\nrounds: 66989"
          },
          {
            "name": "tests/perf/test_competitors.py::test_fastapi_pagination_100k",
            "value": 17844.764327609693,
            "unit": "iter/sec",
            "range": "stddev: 0.000004738616403287496",
            "extra": "mean: 56.03884599656969 usec\nrounds: 5870"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_sa_filter",
            "value": 957.5070981363292,
            "unit": "iter/sec",
            "range": "stddev: 0.000037076306910433986",
            "extra": "mean: 1.044378680791378 msec\nrounds: 354"
          },
          {
            "name": "tests/perf/test_competitors.py::test_fastapi_pagination_memory",
            "value": 17761.866824490044,
            "unit": "iter/sec",
            "range": "stddev: 0.00000486858676818495",
            "extra": "mean: 56.300388347760894 usec\nrounds: 5338"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_memory",
            "value": 568906.5864561396,
            "unit": "iter/sec",
            "range": "stddev: 3.809942998173705e-7",
            "extra": "mean: 1.7577578179033722 usec\nrounds: 78346"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_python_sort_paginate",
            "value": 1626.1539604003476,
            "unit": "iter/sec",
            "range": "stddev: 0.000013044819346777299",
            "extra": "mean: 614.9479227377751 usec\nrounds: 1359"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_paginate_scaling[10K]",
            "value": 728.1335908436162,
            "unit": "iter/sec",
            "range": "stddev: 0.0001170135655876622",
            "extra": "mean: 1.373374354067911 msec\nrounds: 418"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_sort_scaling[100K]",
            "value": 163.70459279890514,
            "unit": "iter/sec",
            "range": "stddev: 0.00009179499217307289",
            "extra": "mean: 6.108564108695478 msec\nrounds: 138"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_sa_pagination_lib_scaling[100K]",
            "value": 1653.5744970842904,
            "unit": "iter/sec",
            "range": "stddev: 0.000020349508973526426",
            "extra": "mean: 604.750497642094 usec\nrounds: 424"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_paginate_scaling[10K]",
            "value": 2284.8759585066846,
            "unit": "iter/sec",
            "range": "stddev: 0.00001728206843351514",
            "extra": "mean: 437.66051994068215 usec\nrounds: 677"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_sort_scaling[10K]",
            "value": 666.0635920633817,
            "unit": "iter/sec",
            "range": "stddev: 0.00008275533342048536",
            "extra": "mean: 1.501358146452841 msec\nrounds: 437"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_fp_sa_paginate_scaling[100K]",
            "value": 1417.1531266211282,
            "unit": "iter/sec",
            "range": "stddev: 0.0000212502554060811",
            "extra": "mean: 705.6400477937534 usec\nrounds: 272"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_search_scaling[10K]",
            "value": 811.8142146302054,
            "unit": "iter/sec",
            "range": "stddev: 0.0000337117037809483",
            "extra": "mean: 1.231808931130279 msec\nrounds: 363"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_sa_pagination_lib_scaling[10K]",
            "value": 1822.2807946942087,
            "unit": "iter/sec",
            "range": "stddev: 0.000020073707816824835",
            "extra": "mean: 548.7628486848026 usec\nrounds: 456"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_pipeline_scaling[10K]",
            "value": 544.9950158945013,
            "unit": "iter/sec",
            "range": "stddev: 0.00003343219690133431",
            "extra": "mean: 1.8348791655620893 msec\nrounds: 302"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_pipeline_scaling[1K]",
            "value": 1415.5157466427534,
            "unit": "iter/sec",
            "range": "stddev: 0.000024256794509618116",
            "extra": "mean: 706.4562880149854 usec\nrounds: 559"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_fastapi_filter_scaling[100K]",
            "value": 2635.8614232126006,
            "unit": "iter/sec",
            "range": "stddev: 0.00001556556837623908",
            "extra": "mean: 379.3826151836143 usec\nrounds: 764"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_search_scaling[1K]",
            "value": 1583.4388162710509,
            "unit": "iter/sec",
            "range": "stddev: 0.00012664125868326847",
            "extra": "mean: 631.5368738749053 usec\nrounds: 555"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_fp_sa_paginate_scaling[1K]",
            "value": 1583.0850797354722,
            "unit": "iter/sec",
            "range": "stddev: 0.00001722506576181967",
            "extra": "mean: 631.6779892632786 usec\nrounds: 652"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_filter_scaling[1K]",
            "value": 1674.1146609945138,
            "unit": "iter/sec",
            "range": "stddev: 0.000025559881100712008",
            "extra": "mean: 597.3306508205038 usec\nrounds: 610"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_filter_scaling[100K]",
            "value": 183.3649968236387,
            "unit": "iter/sec",
            "range": "stddev: 0.00012409351333583256",
            "extra": "mean: 5.453603562962481 msec\nrounds: 135"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_search_scaling[100K]",
            "value": 144.38192947537155,
            "unit": "iter/sec",
            "range": "stddev: 0.000092633322787469",
            "extra": "mean: 6.926074499998828 msec\nrounds: 114"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_pipeline_scaling[10K]",
            "value": 366.9254806532141,
            "unit": "iter/sec",
            "range": "stddev: 0.00011790986761847077",
            "extra": "mean: 2.7253490224221104 msec\nrounds: 223"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_filter_scaling[10K]",
            "value": 512.3941339143021,
            "unit": "iter/sec",
            "range": "stddev: 0.00005243245949258338",
            "extra": "mean: 1.9516226549292426 msec\nrounds: 284"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_fp_sa_paginate_scaling[10K]",
            "value": 1545.9056832624003,
            "unit": "iter/sec",
            "range": "stddev: 0.000020175352031382766",
            "extra": "mean: 646.8699939634423 usec\nrounds: 497"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_sort_scaling[10K]",
            "value": 1175.6002450956255,
            "unit": "iter/sec",
            "range": "stddev: 0.00001939414506961026",
            "extra": "mean: 850.6292884607711 usec\nrounds: 624"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_search_scaling[100K]",
            "value": 119.96071407758153,
            "unit": "iter/sec",
            "range": "stddev: 0.00013757382588941224",
            "extra": "mean: 8.336062415844538 msec\nrounds: 101"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_fastapi_filter_scaling[10K]",
            "value": 2523.1267704720017,
            "unit": "iter/sec",
            "range": "stddev: 0.000030777924650932875",
            "extra": "mean: 396.3336332137326 usec\nrounds: 837"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_filter_scaling[100K]",
            "value": 157.83598181212975,
            "unit": "iter/sec",
            "range": "stddev: 0.00010266350395490697",
            "extra": "mean: 6.335690940170334 msec\nrounds: 117"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_pipeline_scaling[1K]",
            "value": 622.8876939913687,
            "unit": "iter/sec",
            "range": "stddev: 0.0000744988957453679",
            "extra": "mean: 1.6054258410407076 msec\nrounds: 346"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_paginate_scaling[100K]",
            "value": 2112.335810279786,
            "unit": "iter/sec",
            "range": "stddev: 0.00001856114202747096",
            "extra": "mean: 473.4095758512689 usec\nrounds: 646"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_sort_scaling[1K]",
            "value": 1045.5575490671629,
            "unit": "iter/sec",
            "range": "stddev: 0.000058235331746240986",
            "extra": "mean: 956.4275069241203 usec\nrounds: 722"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_pipeline_scaling[100K]",
            "value": 73.997408147988,
            "unit": "iter/sec",
            "range": "stddev: 0.00009905439542327025",
            "extra": "mean: 13.513986841270064 msec\nrounds: 63"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_paginate_scaling[100K]",
            "value": 700.9423097324113,
            "unit": "iter/sec",
            "range": "stddev: 0.00012479320147646192",
            "extra": "mean: 1.426650932773277 msec\nrounds: 357"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_sa_pagination_lib_scaling[1K]",
            "value": 1829.1463867674872,
            "unit": "iter/sec",
            "range": "stddev: 0.000022851794314658077",
            "extra": "mean: 546.7031000002272 usec\nrounds: 540"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_filter_scaling[1K]",
            "value": 630.9886609432355,
            "unit": "iter/sec",
            "range": "stddev: 0.0001295730877228138",
            "extra": "mean: 1.5848145329666412 msec\nrounds: 364"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_search_scaling[1K]",
            "value": 662.4515589464798,
            "unit": "iter/sec",
            "range": "stddev: 0.000045472886826586925",
            "extra": "mean: 1.509544337989536 msec\nrounds: 358"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_search_scaling[10K]",
            "value": 471.8022492945009,
            "unit": "iter/sec",
            "range": "stddev: 0.00009688935640361875",
            "extra": "mean: 2.1195320740741024 msec\nrounds: 270"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_pipeline_scaling[100K]",
            "value": 78.13526650310365,
            "unit": "iter/sec",
            "range": "stddev: 0.0004247039082409541",
            "extra": "mean: 12.798318157144552 msec\nrounds: 70"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_fastapi_filter_scaling[1K]",
            "value": 2626.0267682667313,
            "unit": "iter/sec",
            "range": "stddev: 0.000014836533654247233",
            "extra": "mean: 380.80342976093675 usec\nrounds: 1082"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_paginate_scaling[1K]",
            "value": 734.6977417305541,
            "unit": "iter/sec",
            "range": "stddev: 0.00010081222601934656",
            "extra": "mean: 1.3611039522791182 msec\nrounds: 461"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_sort_scaling[1K]",
            "value": 2666.0390487705017,
            "unit": "iter/sec",
            "range": "stddev: 0.00001624168304487226",
            "extra": "mean: 375.0882795438313 usec\nrounds: 1227"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_filter_scaling[10K]",
            "value": 950.3049106366407,
            "unit": "iter/sec",
            "range": "stddev: 0.000023933187496932835",
            "extra": "mean: 1.0522938362278556 msec\nrounds: 403"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_paginate_scaling[1K]",
            "value": 2351.3791531610937,
            "unit": "iter/sec",
            "range": "stddev: 0.00001939565319878878",
            "extra": "mean: 425.28232788644175 usec\nrounds: 918"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_sort_scaling[100K]",
            "value": 187.79147659312721,
            "unit": "iter/sec",
            "range": "stddev: 0.00005937722150112173",
            "extra": "mean: 5.325055312103541 msec\nrounds: 157"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_sa_10k",
            "value": 392.9568395420335,
            "unit": "iter/sec",
            "range": "stddev: 0.00013410692838854485",
            "extra": "mean: 2.5448087407396627 msec\nrounds: 135"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_sa_sort_10k",
            "value": 177.77712949967696,
            "unit": "iter/sec",
            "range": "stddev: 0.00015625622398886334",
            "extra": "mean: 5.625020511999082 msec\nrounds: 125"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_sa_pipeline_10k",
            "value": 239.98987789524278,
            "unit": "iter/sec",
            "range": "stddev: 0.00013025097876182047",
            "extra": "mean: 4.166842405063878 msec\nrounds: 158"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_1k",
            "value": 492.55334124572306,
            "unit": "iter/sec",
            "range": "stddev: 0.0000833478020154351",
            "extra": "mean: 2.0302369637182585 msec\nrounds: 441"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_sa_10k",
            "value": 380.5688768833638,
            "unit": "iter/sec",
            "range": "stddev: 0.00009203155219569943",
            "extra": "mean: 2.6276452456895956 msec\nrounds: 232"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_fp_fastapi_offset_10k",
            "value": 412.38218902551637,
            "unit": "iter/sec",
            "range": "stddev: 0.00008464203034671447",
            "extra": "mean: 2.424934991404599 msec\nrounds: 349"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_offset_10k",
            "value": 447.4630956876612,
            "unit": "iter/sec",
            "range": "stddev: 0.00008638592170937",
            "extra": "mean: 2.2348211721532034 msec\nrounds: 395"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_fp_fastapi_pipeline_10k",
            "value": 284.87183032282326,
            "unit": "iter/sec",
            "range": "stddev: 0.00009021777055931446",
            "extra": "mean: 3.5103505982559846 msec\nrounds: 229"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_100k",
            "value": 387.190045242496,
            "unit": "iter/sec",
            "range": "stddev: 0.00009808919659732809",
            "extra": "mean: 2.5827110285691948 msec\nrounds: 350"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_offset_10k",
            "value": 368.5161155916836,
            "unit": "iter/sec",
            "range": "stddev: 0.00009406875415903972",
            "extra": "mean: 2.7135855331439602 msec\nrounds: 347"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_sa_pipeline_10k",
            "value": 212.12139277726348,
            "unit": "iter/sec",
            "range": "stddev: 0.00011216570070498283",
            "extra": "mean: 4.714281699300564 msec\nrounds: 143"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_search_10k",
            "value": 82.61879029546546,
            "unit": "iter/sec",
            "range": "stddev: 0.0003487389940429541",
            "extra": "mean: 12.103784095890896 msec\nrounds: 73"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_pipeline_10k",
            "value": 162.92961465576468,
            "unit": "iter/sec",
            "range": "stddev: 0.00010959896969584866",
            "extra": "mean: 6.137619622514823 msec\nrounds: 151"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_sa_filter_10k",
            "value": 232.93269157428125,
            "unit": "iter/sec",
            "range": "stddev: 0.00012206766058070382",
            "extra": "mean: 4.293085668831952 msec\nrounds: 154"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_pipeline_10k",
            "value": 268.47817199360424,
            "unit": "iter/sec",
            "range": "stddev: 0.00010291533427151292",
            "extra": "mean: 3.724697589284176 msec\nrounds: 224"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_filter_10k",
            "value": 223.83674957431225,
            "unit": "iter/sec",
            "range": "stddev: 0.00015068889932333139",
            "extra": "mean: 4.467541643192093 msec\nrounds: 213"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_10k",
            "value": 313.2782570162676,
            "unit": "iter/sec",
            "range": "stddev: 0.00010195050316015763",
            "extra": "mean: 3.1920504459014305 msec\nrounds: 305"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_sa_sort_10k",
            "value": 241.13090072704085,
            "unit": "iter/sec",
            "range": "stddev: 0.00012006125978590195",
            "extra": "mean: 4.147125055249537 msec\nrounds: 181"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_sa_search_10k",
            "value": 174.13540258532902,
            "unit": "iter/sec",
            "range": "stddev: 0.00017062793266151358",
            "extra": "mean: 5.7426576397064615 msec\nrounds: 136"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_filter_10k",
            "value": 279.83126347357876,
            "unit": "iter/sec",
            "range": "stddev: 0.00011611115900193126",
            "extra": "mean: 3.573582120835539 msec\nrounds: 240"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_sa_filter_10k",
            "value": 219.31888139720022,
            "unit": "iter/sec",
            "range": "stddev: 0.00012729518256162826",
            "extra": "mean: 4.559570948152602 msec\nrounds: 135"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_search_10k",
            "value": 221.71298444923403,
            "unit": "iter/sec",
            "range": "stddev: 0.00029173033726371183",
            "extra": "mean: 4.5103357499974095 msec\nrounds: 200"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_fp_fastapi_sa_10k",
            "value": 213.07288261138302,
            "unit": "iter/sec",
            "range": "stddev: 0.00012509459695364327",
            "extra": "mean: 4.69322978947006 msec\nrounds: 152"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_sort_10k",
            "value": 237.40273040307355,
            "unit": "iter/sec",
            "range": "stddev: 0.00017107588240347765",
            "extra": "mean: 4.212251469484587 msec\nrounds: 213"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_sa_search_10k",
            "value": 200.83450087165804,
            "unit": "iter/sec",
            "range": "stddev: 0.0001502640056216506",
            "extra": "mean: 4.979224165468678 msec\nrounds: 139"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_sort_10k",
            "value": 158.7480833792082,
            "unit": "iter/sec",
            "range": "stddev: 0.000256654388106932",
            "extra": "mean: 6.299288651008518 msec\nrounds: 149"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_sort_scaling[1M]",
            "value": 9.682567266636125,
            "unit": "iter/sec",
            "range": "stddev: 0.0010791658165048008",
            "extra": "mean: 103.27839430000836 msec\nrounds: 10"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_paginate_scaling[10K]",
            "value": 4334950.169160786,
            "unit": "iter/sec",
            "range": "stddev: 4.069572853498896e-8",
            "extra": "mean: 230.68315920078402 nsec\nrounds: 140985"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_sort_scaling[500K]",
            "value": 20.295168300458222,
            "unit": "iter/sec",
            "range": "stddev: 0.00039724753626641977",
            "extra": "mean: 49.27281140001298 msec\nrounds: 20"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_paginate_lib_scaling[500K]",
            "value": 385402.9128214926,
            "unit": "iter/sec",
            "range": "stddev: 0.000008583914591084804",
            "extra": "mean: 2.594687187699515 usec\nrounds: 43435"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_paginate_scaling[1K]",
            "value": 4092259.6535768798,
            "unit": "iter/sec",
            "range": "stddev: 3.335803935763062e-8",
            "extra": "mean: 244.36377079003697 nsec\nrounds: 193837"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_filter_scaling[1M]",
            "value": 29.55498325789024,
            "unit": "iter/sec",
            "range": "stddev: 0.00015055530627565696",
            "extra": "mean: 33.83524163333883 msec\nrounds: 30"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_search_scaling[1M]",
            "value": 17.496965241295932,
            "unit": "iter/sec",
            "range": "stddev: 0.00037022855192546795",
            "extra": "mean: 57.152768277771 msec\nrounds: 18"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_pipeline_scaling[10K]",
            "value": 1393.9171817879715,
            "unit": "iter/sec",
            "range": "stddev: 0.00001628507740027409",
            "extra": "mean: 717.4027360200155 usec\nrounds: 1216"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_pipeline_scaling[100K]",
            "value": 125.81997467267557,
            "unit": "iter/sec",
            "range": "stddev: 0.0003612940121099126",
            "extra": "mean: 7.947863625004933 msec\nrounds: 120"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_fp_paginate_scaling[500K]",
            "value": 16371.496827038029,
            "unit": "iter/sec",
            "range": "stddev: 0.000008471837439848182",
            "extra": "mean: 61.081769771256916 usec\nrounds: 569"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_sort_scaling[1K]",
            "value": 13751.081969998098,
            "unit": "iter/sec",
            "range": "stddev: 0.0000037946479958985992",
            "extra": "mean: 72.72155036103958 usec\nrounds: 10524"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_search_scaling[10K]",
            "value": 1879.758193099346,
            "unit": "iter/sec",
            "range": "stddev: 0.000008960626769761282",
            "extra": "mean: 531.983317679387 usec\nrounds: 1810"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_sort_scaling[10K]",
            "value": 1608.60153069997,
            "unit": "iter/sec",
            "range": "stddev: 0.000012201295986270828",
            "extra": "mean: 621.6579935522367 usec\nrounds: 1551"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_filter_scaling[500K]",
            "value": 61.150863352661815,
            "unit": "iter/sec",
            "range": "stddev: 0.0001950337456557901",
            "extra": "mean: 16.35299888135547 msec\nrounds: 59"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_search_scaling[500K]",
            "value": 36.18095961221708,
            "unit": "iter/sec",
            "range": "stddev: 0.00009760263538272158",
            "extra": "mean: 27.63884680555388 msec\nrounds: 36"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_search_scaling[1K]",
            "value": 18556.03591779083,
            "unit": "iter/sec",
            "range": "stddev: 0.0000030004468041714387",
            "extra": "mean: 53.89082045488162 usec\nrounds: 15879"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_filter_scaling[1K]",
            "value": 35287.199125895015,
            "unit": "iter/sec",
            "range": "stddev: 0.0000023350098019599424",
            "extra": "mean: 28.338888457320607 usec\nrounds: 19042"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_paginate_scaling[100K]",
            "value": 4334218.6622016225,
            "unit": "iter/sec",
            "range": "stddev: 3.130569271722647e-8",
            "extra": "mean: 230.72209270854745 nsec\nrounds: 184843"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_paginate_scaling[1M]",
            "value": 4509045.507003716,
            "unit": "iter/sec",
            "range": "stddev: 2.9948618268007355e-8",
            "extra": "mean: 221.77642661772595 nsec\nrounds: 196079"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_pipeline_scaling[1K]",
            "value": 14155.433666006918,
            "unit": "iter/sec",
            "range": "stddev: 0.000003852440258415041",
            "extra": "mean: 70.64425037018935 usec\nrounds: 8771"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_paginate_scaling[500K]",
            "value": 4469517.199506437,
            "unit": "iter/sec",
            "range": "stddev: 2.997038895548123e-8",
            "extra": "mean: 223.73781224299483 nsec\nrounds: 196464"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_fp_paginate_scaling[1K]",
            "value": 17255.846452608486,
            "unit": "iter/sec",
            "range": "stddev: 0.000005462424469605535",
            "extra": "mean: 57.95137333577946 usec\nrounds: 5633"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_filter_scaling[100K]",
            "value": 357.72276213921,
            "unit": "iter/sec",
            "range": "stddev: 0.000055704210318118384",
            "extra": "mean: 2.7954609150950365 msec\nrounds: 318"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_paginate_lib_scaling[10K]",
            "value": 383583.4852268033,
            "unit": "iter/sec",
            "range": "stddev: 0.000008689420294899996",
            "extra": "mean: 2.6069944054257843 usec\nrounds: 84725"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_search_scaling[100K]",
            "value": 184.89383454061624,
            "unit": "iter/sec",
            "range": "stddev: 0.000045004916677988146",
            "extra": "mean: 5.408509172220811 msec\nrounds: 180"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_fp_paginate_scaling[10K]",
            "value": 17665.88213620526,
            "unit": "iter/sec",
            "range": "stddev: 0.00000532349127577104",
            "extra": "mean: 56.60628732207801 usec\nrounds: 5419"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_paginate_lib_scaling[1M]",
            "value": 386754.5132591568,
            "unit": "iter/sec",
            "range": "stddev: 0.00000860225029151302",
            "extra": "mean: 2.5856194710517038 usec\nrounds: 49242"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_pipeline_scaling[500K]",
            "value": 18.374139914549406,
            "unit": "iter/sec",
            "range": "stddev: 0.0006378393815345102",
            "extra": "mean: 54.42431616666631 msec\nrounds: 18"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_filter_scaling[10K]",
            "value": 3672.798264176949,
            "unit": "iter/sec",
            "range": "stddev: 0.000007024017478377233",
            "extra": "mean: 272.27196488127663 usec\nrounds: 3303"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_fp_paginate_scaling[100K]",
            "value": 17610.651929890766,
            "unit": "iter/sec",
            "range": "stddev: 0.000005317704980462396",
            "extra": "mean: 56.78381493093327 usec\nrounds: 4474"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_sort_scaling[100K]",
            "value": 148.49197127883008,
            "unit": "iter/sec",
            "range": "stddev: 0.00010865646051438028",
            "extra": "mean: 6.734370830879838 msec\nrounds: 136"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_pipeline_scaling[1M]",
            "value": 8.832854516066913,
            "unit": "iter/sec",
            "range": "stddev: 0.0008097106733066288",
            "extra": "mean: 113.21368400000311 msec\nrounds: 9"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_paginate_lib_scaling[100K]",
            "value": 386673.63059472194,
            "unit": "iter/sec",
            "range": "stddev: 0.000008662517840411096",
            "extra": "mean: 2.5861603193937834 usec\nrounds: 73497"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_fp_paginate_scaling[1M]",
            "value": 17699.38052949842,
            "unit": "iter/sec",
            "range": "stddev: 0.0000049888686816738045",
            "extra": "mean: 56.49915251742084 usec\nrounds: 4052"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_paginate_lib_scaling[1K]",
            "value": 388888.138210348,
            "unit": "iter/sec",
            "range": "stddev: 0.000008574895060727427",
            "extra": "mean: 2.571433535108505 usec\nrounds: 87866"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_sa_sync_10k",
            "value": 27650.28976431424,
            "unit": "iter/sec",
            "range": "stddev: 0.000004231066818250966",
            "extra": "mean: 36.16598627080613 usec\nrounds: 4006"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_memory_10k_multi",
            "value": 264.7173248680221,
            "unit": "iter/sec",
            "range": "stddev: 0.00007158772340106095",
            "extra": "mean: 3.7776144817818844 msec\nrounds: 247"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_memory_100k",
            "value": 79.45386641232385,
            "unit": "iter/sec",
            "range": "stddev: 0.0000897716462518849",
            "extra": "mean: 12.585919920001439 msec\nrounds: 75"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_sa_sync_1k",
            "value": 27741.8004226551,
            "unit": "iter/sec",
            "range": "stddev: 0.000004641644085014215",
            "extra": "mean: 36.04668712068733 usec\nrounds: 5590"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_memory_10k_single",
            "value": 801.1073227588209,
            "unit": "iter/sec",
            "range": "stddev: 0.000011452770996508227",
            "extra": "mean: 1.2482721997300443 msec\nrounds: 741"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_sa_async_1k",
            "value": 28019.28569552129,
            "unit": "iter/sec",
            "range": "stddev: 0.000003410087101495808",
            "extra": "mean: 35.68970354443561 usec\nrounds: 10015"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_sa_async_10k",
            "value": 28254.983664684118,
            "unit": "iter/sec",
            "range": "stddev: 0.000003502117832352391",
            "extra": "mean: 35.39198648519834 usec\nrounds: 10951"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_sort_spec_desc",
            "value": 1098655.247657738,
            "unit": "iter/sec",
            "range": "stddev: 2.9565747421947384e-7",
            "extra": "mean: 910.2036349727864 nsec\nrounds: 89518"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_valid_search_request",
            "value": 209.61111040817445,
            "unit": "iter/sec",
            "range": "stddev: 0.000130620415109393",
            "extra": "mean: 4.7707394806158225 msec\nrounds: 129"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_valid_filter_spec",
            "value": 966083.546925503,
            "unit": "iter/sec",
            "range": "stddev: 3.405923006165559e-7",
            "extra": "mean: 1.035107163539255 usec\nrounds: 109207"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_invalid_limit",
            "value": 451.4796833872888,
            "unit": "iter/sec",
            "range": "stddev: 0.00023361106445208237",
            "extra": "mean: 2.214939092048089 msec\nrounds: 239"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_filter_invalid_page",
            "value": 443.1315700027963,
            "unit": "iter/sec",
            "range": "stddev: 0.0001389691757924532",
            "extra": "mean: 2.2566661183577814 msec\nrounds: 414"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_valid_filter_request",
            "value": 245.36739326116728,
            "unit": "iter/sec",
            "range": "stddev: 0.0001581302169682698",
            "extra": "mean: 4.075521146917868 msec\nrounds: 211"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_valid_search_spec",
            "value": 697421.1986052445,
            "unit": "iter/sec",
            "range": "stddev: 4.607493549548664e-7",
            "extra": "mean: 1.4338537486383771 usec\nrounds: 82700"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_invalid_params_caught",
            "value": 390384.03591930406,
            "unit": "iter/sec",
            "range": "stddev: 5.649537821216721e-7",
            "extra": "mean: 2.5615801569475787 usec\nrounds: 39641"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_filter_spec_empty_field",
            "value": 942926.261237987,
            "unit": "iter/sec",
            "range": "stddev: 3.378217175002435e-7",
            "extra": "mean: 1.0605283160605579 usec\nrounds: 89278"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_valid_sort_spec",
            "value": 1200714.6085703045,
            "unit": "iter/sec",
            "range": "stddev: 2.641886721357756e-7",
            "extra": "mean: 832.8373727298144 nsec\nrounds: 110412"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_valid_cursor_params",
            "value": 855722.2231384402,
            "unit": "iter/sec",
            "range": "stddev: 3.1761082931818415e-7",
            "extra": "mean: 1.1686035175438214 usec\nrounds: 59985"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_invalid_filter_operator",
            "value": 551219.7131257842,
            "unit": "iter/sec",
            "range": "stddev: 4.4161318022889386e-7",
            "extra": "mean: 1.814158630737881 usec\nrounds: 57429"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_valid_sort_request",
            "value": 234.07630638870015,
            "unit": "iter/sec",
            "range": "stddev: 0.0002676686815809784",
            "extra": "mean: 4.272111156519318 msec\nrounds: 115"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_invalid_page",
            "value": 453.58417142781934,
            "unit": "iter/sec",
            "range": "stddev: 0.00009220352561876884",
            "extra": "mean: 2.2046624705887337 msec\nrounds: 425"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_search_spec_many_fields",
            "value": 711164.4166162641,
            "unit": "iter/sec",
            "range": "stddev: 3.784535241264523e-7",
            "extra": "mean: 1.4061445941826252 usec\nrounds: 67852"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_invalid_filter_param",
            "value": 267.43518456004375,
            "unit": "iter/sec",
            "range": "stddev: 0.00016126077425940432",
            "extra": "mean: 3.739223773584971 msec\nrounds: 159"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_sort_invalid_limit",
            "value": 441.679178442433,
            "unit": "iter/sec",
            "range": "stddev: 0.00009084878565490545",
            "extra": "mean: 2.2640868051024428 msec\nrounds: 431"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_valid_request",
            "value": 250.49050459744603,
            "unit": "iter/sec",
            "range": "stddev: 0.00010571986364313103",
            "extra": "mean: 3.992167294353384 msec\nrounds: 248"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_valid_offset_params",
            "value": 917502.1979117636,
            "unit": "iter/sec",
            "range": "stddev: 3.610806505787108e-7",
            "extra": "mean: 1.0899156451897354 usec\nrounds: 157928"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_search_invalid_page",
            "value": 431.69184508132224,
            "unit": "iter/sec",
            "range": "stddev: 0.00016209941031696725",
            "extra": "mean: 2.316467200837717 msec\nrounds: 239"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_fp_http_paginate_scaling[10K]",
            "value": 234.25627635690023,
            "unit": "iter/sec",
            "range": "stddev: 0.00009669412611385954",
            "extra": "mean: 4.268829060001167 msec\nrounds: 200"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_pipeline_scaling[10K]",
            "value": 135.59651663399364,
            "unit": "iter/sec",
            "range": "stddev: 0.00016239590827145693",
            "extra": "mean: 7.374820716812595 msec\nrounds: 113"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_paginate_scaling[100K]",
            "value": 238.54951171538187,
            "unit": "iter/sec",
            "range": "stddev: 0.00012931477247946207",
            "extra": "mean: 4.192001873360025 msec\nrounds: 229"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_pipeline_scaling[100K]",
            "value": 26.131980245663456,
            "unit": "iter/sec",
            "range": "stddev: 0.000744512690493526",
            "extra": "mean: 38.267287461536625 msec\nrounds: 26"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_filter_scaling[100K]",
            "value": 129.80735348365192,
            "unit": "iter/sec",
            "range": "stddev: 0.00028567826505627997",
            "extra": "mean: 7.703723811963712 msec\nrounds: 117"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_sort_scaling[1K]",
            "value": 169.8138401787092,
            "unit": "iter/sec",
            "range": "stddev: 0.022761214259474357",
            "extra": "mean: 5.888801519049431 msec\nrounds: 210"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_search_scaling[100K]",
            "value": 64.10788328665086,
            "unit": "iter/sec",
            "range": "stddev: 0.0004696506600031753",
            "extra": "mean: 15.598705630766464 msec\nrounds: 65"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_pipeline_scaling[1K]",
            "value": 227.77191354377734,
            "unit": "iter/sec",
            "range": "stddev: 0.00012523207285997966",
            "extra": "mean: 4.390356934011541 msec\nrounds: 197"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_paginate_scaling[10K]",
            "value": 230.22093532231813,
            "unit": "iter/sec",
            "range": "stddev: 0.00010950213706701148",
            "extra": "mean: 4.343653623854675 msec\nrounds: 218"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_search_scaling[10K]",
            "value": 68.3268712767699,
            "unit": "iter/sec",
            "range": "stddev: 0.000961324344810957",
            "extra": "mean: 14.635530375001744 msec\nrounds: 56"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_paginate_scaling[10K]",
            "value": 215.10799273148785,
            "unit": "iter/sec",
            "range": "stddev: 0.0001428570843250761",
            "extra": "mean: 4.6488277227721 msec\nrounds: 202"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_sort_scaling[1K]",
            "value": 193.77777316642764,
            "unit": "iter/sec",
            "range": "stddev: 0.00037154678183732724",
            "extra": "mean: 5.160550581521761 msec\nrounds: 184"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_paginate_scaling[1K]",
            "value": 205.2667498983164,
            "unit": "iter/sec",
            "range": "stddev: 0.00018474905701586076",
            "extra": "mean: 4.87170961928989 msec\nrounds: 197"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_search_scaling[1K]",
            "value": 163.12807570356165,
            "unit": "iter/sec",
            "range": "stddev: 0.0002610123194767461",
            "extra": "mean: 6.1301526158943505 msec\nrounds: 151"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_filter_scaling[1K]",
            "value": 192.9623106162279,
            "unit": "iter/sec",
            "range": "stddev: 0.00021489588883137154",
            "extra": "mean: 5.182359170588731 msec\nrounds: 170"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_pipeline_scaling[10K]",
            "value": 162.53513063842684,
            "unit": "iter/sec",
            "range": "stddev: 0.0005549696414019806",
            "extra": "mean: 6.152516050358274 msec\nrounds: 139"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_search_scaling[1K]",
            "value": 201.8124001098372,
            "unit": "iter/sec",
            "range": "stddev: 0.00012304866597229248",
            "extra": "mean: 4.95509690908857 msec\nrounds: 187"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_filter_scaling[1K]",
            "value": 192.13285701777127,
            "unit": "iter/sec",
            "range": "stddev: 0.0006152519224942731",
            "extra": "mean: 5.204731848168506 msec\nrounds: 191"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_filter_scaling[10K]",
            "value": 187.57120456675094,
            "unit": "iter/sec",
            "range": "stddev: 0.00012691351762343178",
            "extra": "mean: 5.331308727849695 msec\nrounds: 158"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_fp_http_paginate_scaling[100K]",
            "value": 189.42074125229342,
            "unit": "iter/sec",
            "range": "stddev: 0.0001478129220275847",
            "extra": "mean: 5.279252912795221 msec\nrounds: 172"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_sort_scaling[10K]",
            "value": 133.28989484293518,
            "unit": "iter/sec",
            "range": "stddev: 0.00015179194232776378",
            "extra": "mean: 7.502444211381291 msec\nrounds: 123"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_sort_scaling[10K]",
            "value": 169.24928469571765,
            "unit": "iter/sec",
            "range": "stddev: 0.00031762564785989657",
            "extra": "mean: 5.908444468748186 msec\nrounds: 160"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_search_scaling[10K]",
            "value": 156.30448963152332,
            "unit": "iter/sec",
            "range": "stddev: 0.00019644582642008",
            "extra": "mean: 6.397768882758445 msec\nrounds: 145"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_paginate_scaling[1K]",
            "value": 192.60719827540035,
            "unit": "iter/sec",
            "range": "stddev: 0.00012436883566840462",
            "extra": "mean: 5.191913952095109 msec\nrounds: 167"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_filter_scaling[10K]",
            "value": 115.92990034472004,
            "unit": "iter/sec",
            "range": "stddev: 0.019624906177759034",
            "extra": "mean: 8.62590235156313 msec\nrounds: 128"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_fp_http_paginate_scaling[1K]",
            "value": 177.6144382934808,
            "unit": "iter/sec",
            "range": "stddev: 0.00013460502865632128",
            "extra": "mean: 5.630172916166041 msec\nrounds: 167"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_sort_scaling[100K]",
            "value": 70.41942416809741,
            "unit": "iter/sec",
            "range": "stddev: 0.0009430437221752784",
            "extra": "mean: 14.200627338458652 msec\nrounds: 65"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_paginate_scaling[100K]",
            "value": 186.35841648817228,
            "unit": "iter/sec",
            "range": "stddev: 0.0001479108290778196",
            "extra": "mean: 5.366003955412809 msec\nrounds: 157"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_sort_scaling[100K]",
            "value": 32.10372986032105,
            "unit": "iter/sec",
            "range": "stddev: 0.0012465207601660266",
            "extra": "mean: 31.149028612901475 msec\nrounds: 31"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_pipeline_scaling[100K]",
            "value": 57.74900764684069,
            "unit": "iter/sec",
            "range": "stddev: 0.0005683708557461109",
            "extra": "mean: 17.316314872723318 msec\nrounds: 55"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_filter_scaling[100K]",
            "value": 50.500268282667136,
            "unit": "iter/sec",
            "range": "stddev: 0.0004886262122080502",
            "extra": "mean: 19.801875000003186 msec\nrounds: 46"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_search_scaling[100K]",
            "value": 9.015765490451486,
            "unit": "iter/sec",
            "range": "stddev: 0.001497725788970567",
            "extra": "mean: 110.91681577777182 msec\nrounds: 9"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_pipeline_scaling[1K]",
            "value": 167.25415205270625,
            "unit": "iter/sec",
            "range": "stddev: 0.00017799061172426106",
            "extra": "mean: 5.978924814284271 msec\nrounds: 140"
          },
          {
            "name": "tests/perf/test_overhead.py::test_search_plus_paginate_plus_serialize",
            "value": 110.60893191691282,
            "unit": "iter/sec",
            "range": "stddev: 0.0002465723071131067",
            "extra": "mean: 9.040861191492018 msec\nrounds: 94"
          },
          {
            "name": "tests/perf/test_overhead.py::test_sort_full_http",
            "value": 122.36328136812635,
            "unit": "iter/sec",
            "range": "stddev: 0.00026438696314551823",
            "extra": "mean: 8.172386265055522 msec\nrounds: 83"
          },
          {
            "name": "tests/perf/test_overhead.py::test_paginate_full_http",
            "value": 175.50057736313587,
            "unit": "iter/sec",
            "range": "stddev: 0.00012889480398655705",
            "extra": "mean: 5.697986952663161 msec\nrounds: 169"
          },
          {
            "name": "tests/perf/test_overhead.py::test_search_plus_paginate",
            "value": 107.61634503952162,
            "unit": "iter/sec",
            "range": "stddev: 0.00009304946207712436",
            "extra": "mean: 9.292268750000332 msec\nrounds: 96"
          },
          {
            "name": "tests/perf/test_overhead.py::test_paginate_only",
            "value": 624283.2661235919,
            "unit": "iter/sec",
            "range": "stddev: 3.63781101177767e-7",
            "extra": "mean: 1.6018369452850687 usec\nrounds: 126663"
          },
          {
            "name": "tests/perf/test_overhead.py::test_filter_full_http",
            "value": 139.8415323052111,
            "unit": "iter/sec",
            "range": "stddev: 0.00014020646602263002",
            "extra": "mean: 7.150951391303767 msec\nrounds: 92"
          },
          {
            "name": "tests/perf/test_overhead.py::test_filter_plus_paginate",
            "value": 716.7696670036162,
            "unit": "iter/sec",
            "range": "stddev: 0.000015833914227452418",
            "extra": "mean: 1.3951483245383414 msec\nrounds: 758"
          },
          {
            "name": "tests/perf/test_overhead.py::test_search_full_http",
            "value": 65.89649247822423,
            "unit": "iter/sec",
            "range": "stddev: 0.00044993190731907104",
            "extra": "mean: 15.175314533325945 msec\nrounds: 45"
          },
          {
            "name": "tests/perf/test_overhead.py::test_pipeline_ops_only",
            "value": 93.26280472586714,
            "unit": "iter/sec",
            "range": "stddev: 0.0000757295382965251",
            "extra": "mean: 10.722388233330093 msec\nrounds: 90"
          },
          {
            "name": "tests/perf/test_overhead.py::test_paginate_plus_serialize",
            "value": 212264.67376244382,
            "unit": "iter/sec",
            "range": "stddev: 6.699396492494026e-7",
            "extra": "mean: 4.71109950739684 usec\nrounds: 33495"
          },
          {
            "name": "tests/perf/test_overhead.py::test_pipeline_plus_serialize",
            "value": 92.60918393490338,
            "unit": "iter/sec",
            "range": "stddev: 0.00007816371094824785",
            "extra": "mean: 10.798065132534992 msec\nrounds: 83"
          },
          {
            "name": "tests/perf/test_overhead.py::test_filter_plus_paginate_plus_serialize",
            "value": 781.7767890838895,
            "unit": "iter/sec",
            "range": "stddev: 0.00001368277518270495",
            "extra": "mean: 1.2791374903466133 msec\nrounds: 777"
          },
          {
            "name": "tests/perf/test_overhead.py::test_sort_plus_paginate",
            "value": 449.3234517382865,
            "unit": "iter/sec",
            "range": "stddev: 0.00003515634834136315",
            "extra": "mean: 2.2255682318190266 msec\nrounds: 440"
          },
          {
            "name": "tests/perf/test_overhead.py::test_sort_only",
            "value": 456.27606264052736,
            "unit": "iter/sec",
            "range": "stddev: 0.000023214165292422455",
            "extra": "mean: 2.191655626667928 msec\nrounds: 450"
          },
          {
            "name": "tests/perf/test_overhead.py::test_pipeline_full_http",
            "value": 60.206153401430946,
            "unit": "iter/sec",
            "range": "stddev: 0.00038877038351592055",
            "extra": "mean: 16.60959791489075 msec\nrounds: 47"
          },
          {
            "name": "tests/perf/test_overhead.py::test_filter_only",
            "value": 806.4319177649111,
            "unit": "iter/sec",
            "range": "stddev: 0.000012022621595849267",
            "extra": "mean: 1.2400302839842674 msec\nrounds: 743"
          },
          {
            "name": "tests/perf/test_overhead.py::test_sort_plus_paginate_plus_serialize",
            "value": 454.4687556323202,
            "unit": "iter/sec",
            "range": "stddev: 0.000027624303363397884",
            "extra": "mean: 2.2003712853893793 msec\nrounds: 438"
          },
          {
            "name": "tests/perf/test_overhead.py::test_pipeline_plus_paginate",
            "value": 92.86520967384226,
            "unit": "iter/sec",
            "range": "stddev: 0.00007003646206268693",
            "extra": "mean: 10.768295290692421 msec\nrounds: 86"
          },
          {
            "name": "tests/perf/test_overhead.py::test_search_only",
            "value": 111.20970221907758,
            "unit": "iter/sec",
            "range": "stddev: 0.0000836781615344826",
            "extra": "mean: 8.992021200003304 msec\nrounds: 110"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_search_scaling[1M]",
            "value": 2.5535602821440513,
            "unit": "iter/sec",
            "range": "stddev: 0.0013170213912423172",
            "extra": "mean: 391.610100999992 msec\nrounds: 5"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_filter_scaling[1M]",
            "value": 7.696106557104436,
            "unit": "iter/sec",
            "range": "stddev: 0.0006759581632883122",
            "extra": "mean: 129.93583087501293 msec\nrounds: 8"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_sort_scaling[500K]",
            "value": 7.481879486434509,
            "unit": "iter/sec",
            "range": "stddev: 0.0007471311525616327",
            "extra": "mean: 133.65625599999476 msec\nrounds: 8"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_pipeline_scaling[1K]",
            "value": 654.4458732158472,
            "unit": "iter/sec",
            "range": "stddev: 0.00010280424776077948",
            "extra": "mean: 1.5280102464183212 msec\nrounds: 349"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_filter_scaling[100K]",
            "value": 77.47097725952614,
            "unit": "iter/sec",
            "range": "stddev: 0.00009476147261287009",
            "extra": "mean: 12.908059706669519 msec\nrounds: 75"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_search_scaling[1K]",
            "value": 1362.6147489018788,
            "unit": "iter/sec",
            "range": "stddev: 0.00003313521432046156",
            "extra": "mean: 733.883146946628 usec\nrounds: 524"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_sort_scaling[100K]",
            "value": 26.16740602145231,
            "unit": "iter/sec",
            "range": "stddev: 0.0004720294117871991",
            "extra": "mean: 38.21548070833577 msec\nrounds: 24"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_filter_scaling[1K]",
            "value": 1820.0000648712537,
            "unit": "iter/sec",
            "range": "stddev: 0.000029584427686281542",
            "extra": "mean: 549.4505298661843 usec\nrounds: 519"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_search_scaling[100K]",
            "value": 26.52657117188487,
            "unit": "iter/sec",
            "range": "stddev: 0.00024171258942543258",
            "extra": "mean: 37.69804976000387 msec\nrounds: 25"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_filter_scaling[100K]",
            "value": 164.18488870332268,
            "unit": "iter/sec",
            "range": "stddev: 0.00012511565879830697",
            "extra": "mean: 6.090694508475569 msec\nrounds: 118"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_pipeline_scaling[1K]",
            "value": 3228.909791247296,
            "unit": "iter/sec",
            "range": "stddev: 0.000009729104542020892",
            "extra": "mean: 309.70205569407057 usec\nrounds: 2801"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_filter_scaling[10K]",
            "value": 979.0858230483885,
            "unit": "iter/sec",
            "range": "stddev: 0.000026483119386763706",
            "extra": "mean: 1.0213609230766871 msec\nrounds: 390"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_search_scaling[100K]",
            "value": 61.69073712483286,
            "unit": "iter/sec",
            "range": "stddev: 0.00019458869387326593",
            "extra": "mean: 16.209888981817045 msec\nrounds: 55"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_paginate_scaling[10K]",
            "value": 945.9367775011772,
            "unit": "iter/sec",
            "range": "stddev: 0.000040605106595377377",
            "extra": "mean: 1.0571531034469748 msec\nrounds: 406"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_filter_scaling[1K]",
            "value": 7635.235388154443,
            "unit": "iter/sec",
            "range": "stddev: 0.000005508481818605978",
            "extra": "mean: 130.97173160521456 usec\nrounds: 5749"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_search_scaling[1K]",
            "value": 3995.8881928975775,
            "unit": "iter/sec",
            "range": "stddev: 0.000008635300199205868",
            "extra": "mean: 250.25725238694938 usec\nrounds: 2409"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_sort_scaling[1K]",
            "value": 659.3290368284103,
            "unit": "iter/sec",
            "range": "stddev: 0.00009896299514742022",
            "extra": "mean: 1.5166934021445941 msec\nrounds: 373"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_pipeline_scaling[100K]",
            "value": 31.150445286014875,
            "unit": "iter/sec",
            "range": "stddev: 0.0007596946576245159",
            "extra": "mean: 32.10226983332897 msec\nrounds: 30"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_pipeline_scaling[10K]",
            "value": 389.59075828375836,
            "unit": "iter/sec",
            "range": "stddev: 0.00009670474993346971",
            "extra": "mean: 2.5667960000007244 msec\nrounds: 225"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_pipeline_scaling[1M]",
            "value": 2.817831667553543,
            "unit": "iter/sec",
            "range": "stddev: 0.0013630395492586556",
            "extra": "mean: 354.88280280000026 msec\nrounds: 5"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_sort_scaling[10K]",
            "value": 245.52191689177107,
            "unit": "iter/sec",
            "range": "stddev: 0.00009072070769682145",
            "extra": "mean: 4.0729561444439675 msec\nrounds: 180"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_filter_scaling[10K]",
            "value": 763.342154312311,
            "unit": "iter/sec",
            "range": "stddev: 0.00001634844269998287",
            "extra": "mean: 1.3100285296059566 msec\nrounds: 608"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_paginate_scaling[100K]",
            "value": 607781.6486034595,
            "unit": "iter/sec",
            "range": "stddev: 3.696264491676637e-7",
            "extra": "mean: 1.6453277296176463 usec\nrounds: 50383"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_paginate_scaling[1K]",
            "value": 2682.446545437148,
            "unit": "iter/sec",
            "range": "stddev: 0.000023557970392904247",
            "extra": "mean: 372.79400840289026 usec\nrounds: 714"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_sort_scaling[10K]",
            "value": 295.9067916292195,
            "unit": "iter/sec",
            "range": "stddev: 0.00005747212010866404",
            "extra": "mean: 3.3794425416670775 msec\nrounds: 216"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_search_scaling[10K]",
            "value": 357.46140025787867,
            "unit": "iter/sec",
            "range": "stddev: 0.00010843436142049928",
            "extra": "mean: 2.79750484745649 msec\nrounds: 236"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_paginate_scaling[10K]",
            "value": 2654.7048228870476,
            "unit": "iter/sec",
            "range": "stddev: 0.000024039181914306364",
            "extra": "mean: 376.6897138162724 usec\nrounds: 608"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_pipeline_scaling[100K]",
            "value": 75.28590630796822,
            "unit": "iter/sec",
            "range": "stddev: 0.00013582688672863938",
            "extra": "mean: 13.282698569229558 msec\nrounds: 65"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_search_scaling[10K]",
            "value": 360.2329347315262,
            "unit": "iter/sec",
            "range": "stddev: 0.0000594794169084368",
            "extra": "mean: 2.7759816040842527 msec\nrounds: 245"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_paginate_scaling[1K]",
            "value": 956.8571208974367,
            "unit": "iter/sec",
            "range": "stddev: 0.000044230680109478035",
            "extra": "mean: 1.0450881099804112 msec\nrounds: 491"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_search_scaling[1K]",
            "value": 655.9319786916692,
            "unit": "iter/sec",
            "range": "stddev: 0.00011642642322454077",
            "extra": "mean: 1.5245483258715535 msec\nrounds: 402"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_sort_scaling[100K]",
            "value": 26.390719136017562,
            "unit": "iter/sec",
            "range": "stddev: 0.0005325692351825968",
            "extra": "mean: 37.89210876922329 msec\nrounds: 26"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_filter_scaling[1K]",
            "value": 768.5839404051206,
            "unit": "iter/sec",
            "range": "stddev: 0.00010496417673339419",
            "extra": "mean: 1.3010940606863317 msec\nrounds: 379"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_paginate_scaling[10K]",
            "value": 600303.394016484,
            "unit": "iter/sec",
            "range": "stddev: 3.92134587576972e-7",
            "extra": "mean: 1.6658243314422114 usec\nrounds: 106644"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_filter_scaling[10K]",
            "value": 591.8947213876039,
            "unit": "iter/sec",
            "range": "stddev: 0.00004498489983976931",
            "extra": "mean: 1.689489640413852 msec\nrounds: 292"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_paginate_scaling[500K]",
            "value": 599292.3796188618,
            "unit": "iter/sec",
            "range": "stddev: 4.323830308238233e-7",
            "extra": "mean: 1.6686345997524286 usec\nrounds: 45145"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_paginate_scaling[1K]",
            "value": 607206.0938398193,
            "unit": "iter/sec",
            "range": "stddev: 3.740131113519566e-7",
            "extra": "mean: 1.64688729270856 usec\nrounds: 114864"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_sort_scaling[1K]",
            "value": 4236.469971990361,
            "unit": "iter/sec",
            "range": "stddev: 0.000011688036438476286",
            "extra": "mean: 236.04557724037969 usec\nrounds: 3638"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_pipeline_scaling[500K]",
            "value": 5.673183912870717,
            "unit": "iter/sec",
            "range": "stddev: 0.0008208063152253536",
            "extra": "mean: 176.26786216665855 msec\nrounds: 6"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_sort_scaling[10K]",
            "value": 424.7383114865706,
            "unit": "iter/sec",
            "range": "stddev: 0.00002580639429834069",
            "extra": "mean: 2.354390863635616 msec\nrounds: 396"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_paginate_scaling[100K]",
            "value": 2432.136171358725,
            "unit": "iter/sec",
            "range": "stddev: 0.0000299528587578502",
            "extra": "mean: 411.16118898940806 usec\nrounds: 545"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_search_scaling[100K]",
            "value": 65.16478061234152,
            "unit": "iter/sec",
            "range": "stddev: 0.0000858061566493805",
            "extra": "mean: 15.345712677970877 msec\nrounds: 59"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_pipeline_scaling[10K]",
            "value": 304.89974263721587,
            "unit": "iter/sec",
            "range": "stddev: 0.00005472716133520542",
            "extra": "mean: 3.2797666254177438 msec\nrounds: 299"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_pipeline_scaling[100K]",
            "value": 70.10550192174003,
            "unit": "iter/sec",
            "range": "stddev: 0.00014924052780214577",
            "extra": "mean: 14.264215683332774 msec\nrounds: 60"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_paginate_scaling[1M]",
            "value": 600397.931600997,
            "unit": "iter/sec",
            "range": "stddev: 4.4096780323592905e-7",
            "extra": "mean: 1.6655620337222683 usec\nrounds: 46773"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_filter_scaling[100K]",
            "value": 185.7102097116549,
            "unit": "iter/sec",
            "range": "stddev: 0.00010696438296956712",
            "extra": "mean: 5.384733567167156 msec\nrounds: 134"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_filter_scaling[500K]",
            "value": 14.90171480122192,
            "unit": "iter/sec",
            "range": "stddev: 0.00037730924603494436",
            "extra": "mean: 67.10637086666036 msec\nrounds: 15"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_pipeline_scaling[10K]",
            "value": 525.3360212792579,
            "unit": "iter/sec",
            "range": "stddev: 0.000045508305991248255",
            "extra": "mean: 1.903543559729403 msec\nrounds: 293"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_pipeline_scaling[1K]",
            "value": 1413.627779501441,
            "unit": "iter/sec",
            "range": "stddev: 0.00002891871920925258",
            "extra": "mean: 707.3997939915135 usec\nrounds: 466"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_search_scaling[500K]",
            "value": 5.1810501338087365,
            "unit": "iter/sec",
            "range": "stddev: 0.0009013194856303752",
            "extra": "mean: 193.0110642000045 msec\nrounds: 5"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_search_scaling[10K]",
            "value": 482.3157423713597,
            "unit": "iter/sec",
            "range": "stddev: 0.0000404072847564725",
            "extra": "mean: 2.0733306258746342 msec\nrounds: 286"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_sort_scaling[1K]",
            "value": 1327.5417355005814,
            "unit": "iter/sec",
            "range": "stddev: 0.000023198782203156322",
            "extra": "mean: 753.2719863025067 usec\nrounds: 584"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_sort_scaling[100K]",
            "value": 40.96852082306072,
            "unit": "iter/sec",
            "range": "stddev: 0.0005509198601620336",
            "extra": "mean: 24.40898474999642 msec\nrounds: 40"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_sort_scaling[1M]",
            "value": 3.6471831763422204,
            "unit": "iter/sec",
            "range": "stddev: 0.0010143414820046248",
            "extra": "mean: 274.1841996000062 msec\nrounds: 5"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_paginate_scaling[100K]",
            "value": 911.2300469361985,
            "unit": "iter/sec",
            "range": "stddev: 0.000061587700243745",
            "extra": "mean: 1.0974177194466643 msec\nrounds: 360"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "git.owiwz@passinbox.com",
            "name": "CybLow"
          },
          "committer": {
            "email": "git.owiwz@passinbox.com",
            "name": "CybLow"
          },
          "distinct": true,
          "id": "c268decca2bffa3f0b8071e1b8968d5af070955c",
          "message": "fix(bench): correct badge labels, SA resolution, scaling display\n\n- Fix diffBadge: explicitly show \"pypaginate Nx faster/slower\"\n- Fix SA sync/async scaling: use test_scaling.py names, add 100K scale\n- Add SA async scaling comparison table\n- Mark raw Python as baseline ceiling (not real competitor)\n- Show overhead % for baseline rows instead of speed comparison\n- Scaling tab: replace misleading \"Relative %\" with \"Slowdown\" factor\n  (1x = same, 10x = 10x slower than 1K baseline)\n- Add throughput column to scaling view\n- Improve subtitles explaining what pipeline comparison means",
          "timestamp": "2026-03-17T04:48:43+01:00",
          "tree_id": "ad96968aa48757e5b3ea4aec2c0d239fe49bc26b",
          "url": "https://github.com/CybLow/pypaginate/commit/c268decca2bffa3f0b8071e1b8968d5af070955c"
        },
        "date": 1773720151576,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_valid_request",
            "value": 614.7224606100569,
            "unit": "iter/sec",
            "range": "stddev: 0.0001096760637540292",
            "extra": "mean: 1.6267503858694046 msec\nrounds: 184"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_sort_spec_desc",
            "value": 1109683.9656230407,
            "unit": "iter/sec",
            "range": "stddev: 2.56571838299421e-7",
            "extra": "mean: 901.1574745414495 nsec\nrounds: 106214"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_sort_invalid_limit",
            "value": 931.2350172268809,
            "unit": "iter/sec",
            "range": "stddev: 0.00010555934346973163",
            "extra": "mean: 1.0738427802875088 msec\nrounds: 487"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_search_spec_many_fields",
            "value": 715688.2871153203,
            "unit": "iter/sec",
            "range": "stddev: 2.858899290619812e-7",
            "extra": "mean: 1.397256344700899 usec\nrounds: 52406"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_valid_cursor_params",
            "value": 888700.930252695,
            "unit": "iter/sec",
            "range": "stddev: 2.1998499783120318e-7",
            "extra": "mean: 1.1252379354612108 usec\nrounds: 58415"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_valid_filter_spec",
            "value": 1010685.7471006069,
            "unit": "iter/sec",
            "range": "stddev: 2.0202141615151064e-7",
            "extra": "mean: 989.4272308368239 nsec\nrounds: 72675"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_valid_filter_request",
            "value": 496.05420283241585,
            "unit": "iter/sec",
            "range": "stddev: 0.00018426097391387172",
            "extra": "mean: 2.0159087339450172 msec\nrounds: 218"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_search_invalid_page",
            "value": 859.3758465845135,
            "unit": "iter/sec",
            "range": "stddev: 0.00011305299388911517",
            "extra": "mean: 1.1636352173200821 msec\nrounds: 612"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_valid_search_request",
            "value": 364.431384179327,
            "unit": "iter/sec",
            "range": "stddev: 0.0031509581304869252",
            "extra": "mean: 2.744000773292145 msec\nrounds: 322"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_valid_search_spec",
            "value": 679626.2790685227,
            "unit": "iter/sec",
            "range": "stddev: 2.4616319816374527e-7",
            "extra": "mean: 1.4713968997352085 usec\nrounds: 107216"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_filter_invalid_page",
            "value": 846.0851320069453,
            "unit": "iter/sec",
            "range": "stddev: 0.00011260963287102369",
            "extra": "mean: 1.1819141622639828 msec\nrounds: 530"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_valid_offset_params",
            "value": 913845.9693314127,
            "unit": "iter/sec",
            "range": "stddev: 1.9820561902983953e-7",
            "extra": "mean: 1.0942763152215018 usec\nrounds: 70235"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_valid_sort_spec",
            "value": 1213080.4445152034,
            "unit": "iter/sec",
            "range": "stddev: 1.9088431269853722e-7",
            "extra": "mean: 824.3476387088583 nsec\nrounds: 92576"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_filter_spec_empty_field",
            "value": 989212.8804490693,
            "unit": "iter/sec",
            "range": "stddev: 2.0270214848154328e-7",
            "extra": "mean: 1.0109047503971376 usec\nrounds: 74499"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_invalid_filter_param",
            "value": 562.5651519211688,
            "unit": "iter/sec",
            "range": "stddev: 0.0001558640030731151",
            "extra": "mean: 1.7775718893802512 msec\nrounds: 226"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_invalid_limit",
            "value": 830.5430101573309,
            "unit": "iter/sec",
            "range": "stddev: 0.0000933070167843265",
            "extra": "mean: 1.2040315646152613 msec\nrounds: 650"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_invalid_page",
            "value": 825.1203869597709,
            "unit": "iter/sec",
            "range": "stddev: 0.00009363299627504472",
            "extra": "mean: 1.2119443608521037 msec\nrounds: 751"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_fastapi_valid_sort_request",
            "value": 418.90471153919566,
            "unit": "iter/sec",
            "range": "stddev: 0.00009066343943471184",
            "extra": "mean: 2.3871777338709474 msec\nrounds: 372"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_invalid_params_caught",
            "value": 388528.39000516705,
            "unit": "iter/sec",
            "range": "stddev: 4.200444448737482e-7",
            "extra": "mean: 2.573814490072916 usec\nrounds: 52008"
          },
          {
            "name": "tests/perf/test_error_handling.py::test_invalid_filter_operator",
            "value": 545099.0955219866,
            "unit": "iter/sec",
            "range": "stddev: 4.163202198476666e-7",
            "extra": "mean: 1.8345288190992144 usec\nrounds: 52604"
          },
          {
            "name": "tests/perf/test_competitors.py::test_sqlalchemy_pagination_lib_10k",
            "value": 1699.446416350644,
            "unit": "iter/sec",
            "range": "stddev: 0.00003720882151775302",
            "extra": "mean: 588.4269079500483 usec\nrounds: 239"
          },
          {
            "name": "tests/perf/test_competitors.py::test_fastapi_pagination_100k",
            "value": 18811.631494475736,
            "unit": "iter/sec",
            "range": "stddev: 0.0000031245625460780854",
            "extra": "mean: 53.15860032095899 usec\nrounds: 623"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_sqlalchemy",
            "value": 2337.9191307419537,
            "unit": "iter/sec",
            "range": "stddev: 0.00001744029960011072",
            "extra": "mean: 427.73079139082256 usec\nrounds: 604"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_python_sort_paginate",
            "value": 1604.9345237403718,
            "unit": "iter/sec",
            "range": "stddev: 0.000009374991246502779",
            "extra": "mean: 623.0783780944878 usec\nrounds: 1333"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_python_full_pipeline",
            "value": 1423.856683747971,
            "unit": "iter/sec",
            "range": "stddev: 0.000019024652710123983",
            "extra": "mean: 702.3178746948977 usec\nrounds: 1229"
          },
          {
            "name": "tests/perf/test_competitors.py::test_fastapi_pagination_full_pipeline",
            "value": 1220.2576241186275,
            "unit": "iter/sec",
            "range": "stddev: 0.00006172018035727928",
            "extra": "mean: 819.4990797310395 usec\nrounds: 1041"
          },
          {
            "name": "tests/perf/test_competitors.py::test_paginate_lib_100k",
            "value": 407940.37473832804,
            "unit": "iter/sec",
            "range": "stddev: 0.000007029770111125278",
            "extra": "mean: 2.4513386316356804 usec\nrounds: 68009"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_100k",
            "value": 589691.7888567627,
            "unit": "iter/sec",
            "range": "stddev: 3.628312604426256e-7",
            "extra": "mean: 1.6958011267864237 usec\nrounds: 66384"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_sa_async",
            "value": 1004.5963804157022,
            "unit": "iter/sec",
            "range": "stddev: 0.00009862042091776833",
            "extra": "mean: 995.42464963511 usec\nrounds: 411"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_sa_filter",
            "value": 936.5136120868489,
            "unit": "iter/sec",
            "range": "stddev: 0.00003570943853887115",
            "extra": "mean: 1.0677901389726556 msec\nrounds: 331"
          },
          {
            "name": "tests/perf/test_competitors.py::test_fastapi_pagination_memory",
            "value": 19086.99605039181,
            "unit": "iter/sec",
            "range": "stddev: 0.000003173021366446657",
            "extra": "mean: 52.39169104241903 usec\nrounds: 5593"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_python_search_paginate",
            "value": 1830.5866717126794,
            "unit": "iter/sec",
            "range": "stddev: 0.000027375609350944345",
            "extra": "mean: 546.2729601676874 usec\nrounds: 1431"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_filter_paginate",
            "value": 855.9328154113948,
            "unit": "iter/sec",
            "range": "stddev: 0.000013242762234764227",
            "extra": "mean: 1.168315996296229 msec\nrounds: 810"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_sa_filter",
            "value": 946.5006858552094,
            "unit": "iter/sec",
            "range": "stddev: 0.00013467846625659773",
            "extra": "mean: 1.056523270341269 msec\nrounds: 381"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_sort_paginate",
            "value": 487.7589463891137,
            "unit": "iter/sec",
            "range": "stddev: 0.000025017549910789584",
            "extra": "mean: 2.0501930459769397 msec\nrounds: 435"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_python_filter_paginate",
            "value": 3761.1988235385775,
            "unit": "iter/sec",
            "range": "stddev: 0.00000647310706558989",
            "extra": "mean: 265.8726770150345 usec\nrounds: 3511"
          },
          {
            "name": "tests/perf/test_competitors.py::test_paginate_lib_memory",
            "value": 407097.00911129365,
            "unit": "iter/sec",
            "range": "stddev: 0.000007351208163878363",
            "extra": "mean: 2.456416966027418 usec\nrounds: 72380"
          },
          {
            "name": "tests/perf/test_competitors.py::test_fastapi_filter_10k",
            "value": 2505.5525296794112,
            "unit": "iter/sec",
            "range": "stddev: 0.000015667119290501625",
            "extra": "mean: 399.11356403609363 usec\nrounds: 773"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_python_100k",
            "value": 4580307.53400515,
            "unit": "iter/sec",
            "range": "stddev: 2.5438681744458e-8",
            "extra": "mean: 218.32595138553205 nsec\nrounds: 167729"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_search_paginate",
            "value": 398.8335139519398,
            "unit": "iter/sec",
            "range": "stddev: 0.00002191902397515944",
            "extra": "mean: 2.507311860759279 msec\nrounds: 237"
          },
          {
            "name": "tests/perf/test_competitors.py::test_paginate_lib_full_pipeline",
            "value": 1269.627397498835,
            "unit": "iter/sec",
            "range": "stddev: 0.0007112333891915257",
            "extra": "mean: 787.6326566124826 usec\nrounds: 1293"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_full_pipeline",
            "value": 362.08695987833977,
            "unit": "iter/sec",
            "range": "stddev: 0.00002877958931844212",
            "extra": "mean: 2.76176750561798 msec\nrounds: 356"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_sa_sync",
            "value": 2657.216608304722,
            "unit": "iter/sec",
            "range": "stddev: 0.00012854508423734373",
            "extra": "mean: 376.33364057512426 usec\nrounds: 626"
          },
          {
            "name": "tests/perf/test_competitors.py::test_pypaginate_memory",
            "value": 604520.5083582603,
            "unit": "iter/sec",
            "range": "stddev: 2.3937294791763987e-7",
            "extra": "mean: 1.6542035980148497 usec\nrounds: 110060"
          },
          {
            "name": "tests/perf/test_competitors.py::test_raw_python_slice",
            "value": 4827442.982996777,
            "unit": "iter/sec",
            "range": "stddev: 2.0444867988602573e-8",
            "extra": "mean: 207.1490027996604 nsec\nrounds: 175040"
          },
          {
            "name": "tests/perf/test_overhead.py::test_pipeline_plus_serialize",
            "value": 96.84006566966008,
            "unit": "iter/sec",
            "range": "stddev: 0.00010307692006291128",
            "extra": "mean: 10.32630443902414 msec\nrounds: 82"
          },
          {
            "name": "tests/perf/test_overhead.py::test_paginate_full_http",
            "value": 461.91193177797976,
            "unit": "iter/sec",
            "range": "stddev: 0.00021936421293641096",
            "extra": "mean: 2.1649148489211463 msec\nrounds: 278"
          },
          {
            "name": "tests/perf/test_overhead.py::test_paginate_plus_serialize",
            "value": 233375.0275336198,
            "unit": "iter/sec",
            "range": "stddev: 4.817324532417043e-7",
            "extra": "mean: 4.284948610690322 usec\nrounds: 48045"
          },
          {
            "name": "tests/perf/test_overhead.py::test_search_plus_paginate",
            "value": 118.0328328278803,
            "unit": "iter/sec",
            "range": "stddev: 0.0002316714742066951",
            "extra": "mean: 8.472218924527853 msec\nrounds: 106"
          },
          {
            "name": "tests/perf/test_overhead.py::test_search_full_http",
            "value": 91.01515582415858,
            "unit": "iter/sec",
            "range": "stddev: 0.00020356241692892873",
            "extra": "mean: 10.987181101266271 msec\nrounds: 79"
          },
          {
            "name": "tests/perf/test_overhead.py::test_filter_plus_paginate",
            "value": 865.3118827206673,
            "unit": "iter/sec",
            "range": "stddev: 0.00001565787384867529",
            "extra": "mean: 1.1556526842736212 msec\nrounds: 833"
          },
          {
            "name": "tests/perf/test_overhead.py::test_pipeline_ops_only",
            "value": 96.25603093648733,
            "unit": "iter/sec",
            "range": "stddev: 0.00040551626038997355",
            "extra": "mean: 10.388959426966508 msec\nrounds: 89"
          },
          {
            "name": "tests/perf/test_overhead.py::test_sort_plus_paginate_plus_serialize",
            "value": 493.0209706997331,
            "unit": "iter/sec",
            "range": "stddev: 0.000019466825499931324",
            "extra": "mean: 2.0283112878154523 msec\nrounds: 476"
          },
          {
            "name": "tests/perf/test_overhead.py::test_filter_plus_paginate_plus_serialize",
            "value": 867.8185860537643,
            "unit": "iter/sec",
            "range": "stddev: 0.000012511629520538724",
            "extra": "mean: 1.1523145690475527 msec\nrounds: 840"
          },
          {
            "name": "tests/perf/test_overhead.py::test_filter_full_http",
            "value": 278.18189222820683,
            "unit": "iter/sec",
            "range": "stddev: 0.00011484859561649884",
            "extra": "mean: 3.5947702849747274 msec\nrounds: 193"
          },
          {
            "name": "tests/perf/test_overhead.py::test_search_only",
            "value": 117.62449869629333,
            "unit": "iter/sec",
            "range": "stddev: 0.00018712764309945608",
            "extra": "mean: 8.50163028181741 msec\nrounds: 110"
          },
          {
            "name": "tests/perf/test_overhead.py::test_filter_only",
            "value": 863.5394137797571,
            "unit": "iter/sec",
            "range": "stddev: 0.000024367344385437193",
            "extra": "mean: 1.1580247340685328 msec\nrounds: 816"
          },
          {
            "name": "tests/perf/test_overhead.py::test_sort_full_http",
            "value": 207.32743422635633,
            "unit": "iter/sec",
            "range": "stddev: 0.00010094263883340151",
            "extra": "mean: 4.823288358974327 msec\nrounds: 156"
          },
          {
            "name": "tests/perf/test_overhead.py::test_sort_only",
            "value": 491.9185454569208,
            "unit": "iter/sec",
            "range": "stddev: 0.0000216728793706208",
            "extra": "mean: 2.0328568809519982 msec\nrounds: 462"
          },
          {
            "name": "tests/perf/test_overhead.py::test_paginate_only",
            "value": 650017.5440251229,
            "unit": "iter/sec",
            "range": "stddev: 2.5137087860953064e-7",
            "extra": "mean: 1.5384200152624654 usec\nrounds: 73314"
          },
          {
            "name": "tests/perf/test_overhead.py::test_sort_plus_paginate",
            "value": 487.4533480065276,
            "unit": "iter/sec",
            "range": "stddev: 0.000031518338581976365",
            "extra": "mean: 2.051478370370345 msec\nrounds: 432"
          },
          {
            "name": "tests/perf/test_overhead.py::test_pipeline_plus_paginate",
            "value": 97.21970720847504,
            "unit": "iter/sec",
            "range": "stddev: 0.00004590522944781953",
            "extra": "mean: 10.285980370786653 msec\nrounds: 89"
          },
          {
            "name": "tests/perf/test_overhead.py::test_pipeline_full_http",
            "value": 78.15205215053366,
            "unit": "iter/sec",
            "range": "stddev: 0.0002897447252021772",
            "extra": "mean: 12.79556930986068 msec\nrounds: 71"
          },
          {
            "name": "tests/perf/test_overhead.py::test_search_plus_paginate_plus_serialize",
            "value": 118.01165823538618,
            "unit": "iter/sec",
            "range": "stddev: 0.000047321984574693974",
            "extra": "mean: 8.473739077586716 msec\nrounds: 116"
          },
          {
            "name": "tests/perf/test_serialization.py::test_searched_page_model_dump_json[1000]",
            "value": 141092.1491567655,
            "unit": "iter/sec",
            "range": "stddev: 5.957565238085353e-7",
            "extra": "mean: 7.087566572459777 usec\nrounds: 41391"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_model_dump_json[1000]",
            "value": 42808.87203525742,
            "unit": "iter/sec",
            "range": "stddev: 0.000001211819442407952",
            "extra": "mean: 23.359643748062304 usec\nrounds: 28303"
          },
          {
            "name": "tests/perf/test_serialization.py::test_sorted_page_model_dump_json[20]",
            "value": 143940.48771998347,
            "unit": "iter/sec",
            "range": "stddev: 6.115542919522749e-7",
            "extra": "mean: 6.947315629118633 usec\nrounds: 60061"
          },
          {
            "name": "tests/perf/test_serialization.py::test_sorted_page_model_dump_json[1000]",
            "value": 3619.412910323092,
            "unit": "iter/sec",
            "range": "stddev: 0.000008067764077058107",
            "extra": "mean: 276.2879021478468 usec\nrounds: 2933"
          },
          {
            "name": "tests/perf/test_serialization.py::test_searched_page_model_dump_json[100]",
            "value": 140688.52328454013,
            "unit": "iter/sec",
            "range": "stddev: 6.114836359331597e-7",
            "extra": "mean: 7.107900322313548 usec\nrounds: 56161"
          },
          {
            "name": "tests/perf/test_serialization.py::test_filtered_page_model_dump_json[100]",
            "value": 34760.452453392354,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015599640014035793",
            "extra": "mean: 28.768325191992936 usec\nrounds: 25262"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_model_dump[1000]",
            "value": 43002.546426181034,
            "unit": "iter/sec",
            "range": "stddev: 0.0000026104302144530887",
            "extra": "mean: 23.254436844027794 usec\nrounds: 29443"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_dict_construction[1000]",
            "value": 7650532.107395727,
            "unit": "iter/sec",
            "range": "stddev: 7.837310833916558e-9",
            "extra": "mean: 130.70986252491136 nsec\nrounds: 76232"
          },
          {
            "name": "tests/perf/test_serialization.py::test_cursor_page_model_dump[100]",
            "value": 281813.8448127667,
            "unit": "iter/sec",
            "range": "stddev: 3.7136360286982565e-7",
            "extra": "mean: 3.5484417050709003 usec\nrounds: 57921"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_filtered_json_dumps[1000]",
            "value": 1273.7158006968286,
            "unit": "iter/sec",
            "range": "stddev: 0.000011259732740903577",
            "extra": "mean: 785.1044946234605 usec\nrounds: 930"
          },
          {
            "name": "tests/perf/test_serialization.py::test_fp_filtered_page_serialize[100]",
            "value": 11413.571949642426,
            "unit": "iter/sec",
            "range": "stddev: 0.000002727681629083757",
            "extra": "mean: 87.61499068057559 usec\nrounds: 6009"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_pipeline_json_dumps",
            "value": 53055.49693741975,
            "unit": "iter/sec",
            "range": "stddev: 9.693741637474796e-7",
            "extra": "mean: 18.848188363583215 usec\nrounds: 18889"
          },
          {
            "name": "tests/perf/test_serialization.py::test_pipeline_page_model_dump",
            "value": 4554559.344310425,
            "unit": "iter/sec",
            "range": "stddev: 1.9739254692857063e-8",
            "extra": "mean: 219.5602086619412 nsec\nrounds: 197707"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_searched_json_dumps[1000]",
            "value": 54696.15328683336,
            "unit": "iter/sec",
            "range": "stddev: 8.718841664163388e-7",
            "extra": "mean: 18.282821366904486 usec\nrounds: 21407"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_dict_dump[1000]",
            "value": 5026061.432509897,
            "unit": "iter/sec",
            "range": "stddev: 1.741348201352175e-8",
            "extra": "mean: 198.9629481109394 nsec\nrounds: 186533"
          },
          {
            "name": "tests/perf/test_serialization.py::test_filtered_page_model_dump_json[20]",
            "value": 143366.66662396461,
            "unit": "iter/sec",
            "range": "stddev: 5.171378414081885e-7",
            "extra": "mean: 6.975122066713686 usec\nrounds: 43509"
          },
          {
            "name": "tests/perf/test_serialization.py::test_fp_filtered_page_serialize[1000]",
            "value": 11419.070736820655,
            "unit": "iter/sec",
            "range": "stddev: 0.000002674951163724643",
            "extra": "mean: 87.57280019078192 usec\nrounds: 7337"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_sorted_json_dumps[1000]",
            "value": 1237.4898162466668,
            "unit": "iter/sec",
            "range": "stddev: 0.000011181806734679253",
            "extra": "mean: 808.0874580713896 usec\nrounds: 954"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_dict_dump[100]",
            "value": 5378153.956687167,
            "unit": "iter/sec",
            "range": "stddev: 1.0041982693898364e-8",
            "extra": "mean: 185.93740678560118 nsec\nrounds: 53023"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_dict_construction[20]",
            "value": 7893806.271667914,
            "unit": "iter/sec",
            "range": "stddev: 7.27809164558896e-9",
            "extra": "mean: 126.68159891240292 nsec\nrounds: 78716"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_model_dump_json[100]",
            "value": 304873.0364129843,
            "unit": "iter/sec",
            "range": "stddev: 3.5688436567862973e-7",
            "extra": "mean: 3.280053925941123 usec\nrounds: 61603"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_create[1000]",
            "value": 2499408.675841417,
            "unit": "iter/sec",
            "range": "stddev: 1.0862419169577364e-7",
            "extra": "mean: 400.0946342491804 nsec\nrounds: 190840"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_filtered_json_dumps[20]",
            "value": 54510.88541093076,
            "unit": "iter/sec",
            "range": "stddev: 0.000001037109518577115",
            "extra": "mean: 18.344959772006852 usec\nrounds: 24560"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_dict_construction[100]",
            "value": 7621938.958128817,
            "unit": "iter/sec",
            "range": "stddev: 7.4393281952895464e-9",
            "extra": "mean: 131.20021106093222 nsec\nrounds: 75239"
          },
          {
            "name": "tests/perf/test_serialization.py::test_searched_page_model_dump_json[20]",
            "value": 140700.60553271062,
            "unit": "iter/sec",
            "range": "stddev: 5.181736580162334e-7",
            "extra": "mean: 7.107289952405472 usec\nrounds: 42438"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_searched_json_dumps[20]",
            "value": 55092.31331797187,
            "unit": "iter/sec",
            "range": "stddev: 8.60673365903178e-7",
            "extra": "mean: 18.151352516790872 usec\nrounds: 24257"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_sorted_json_dumps[20]",
            "value": 54840.29942482536,
            "unit": "iter/sec",
            "range": "stddev: 0.0000012491169853714275",
            "extra": "mean: 18.234765500702487 usec\nrounds: 27902"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_sorted_json_dumps[100]",
            "value": 12529.179958893776,
            "unit": "iter/sec",
            "range": "stddev: 0.000002670791875143519",
            "extra": "mean: 79.81368320040411 usec\nrounds: 8024"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_create[20]",
            "value": 2404968.1136468938,
            "unit": "iter/sec",
            "range": "stddev: 1.2033668205238095e-7",
            "extra": "mean: 415.80592870464295 nsec\nrounds: 178285"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_searched_json_dumps[100]",
            "value": 54586.331368544495,
            "unit": "iter/sec",
            "range": "stddev: 9.80311568086596e-7",
            "extra": "mean: 18.319604467433624 usec\nrounds: 25563"
          },
          {
            "name": "tests/perf/test_serialization.py::test_filtered_page_model_dump_json[1000]",
            "value": 3689.5191715002707,
            "unit": "iter/sec",
            "range": "stddev: 0.0000173919177222902",
            "extra": "mean: 271.03802786132957 usec\nrounds: 2656"
          },
          {
            "name": "tests/perf/test_serialization.py::test_sorted_page_model_dump_json[100]",
            "value": 35024.53722315323,
            "unit": "iter/sec",
            "range": "stddev: 0.0000012601442856293502",
            "extra": "mean: 28.551412217916262 usec\nrounds: 25700"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_model_dump[20]",
            "value": 561141.0761321629,
            "unit": "iter/sec",
            "range": "stddev: 3.4953447014628915e-7",
            "extra": "mean: 1.782083049226777 usec\nrounds: 77725"
          },
          {
            "name": "tests/perf/test_serialization.py::test_cursor_page_model_dump[1000]",
            "value": 43625.741555183595,
            "unit": "iter/sec",
            "range": "stddev: 0.0000012603191820078496",
            "extra": "mean: 22.92224646164623 usec\nrounds: 29534"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_dict_dump[20]",
            "value": 5259546.860502791,
            "unit": "iter/sec",
            "range": "stddev: 9.383860786671525e-9",
            "extra": "mean: 190.1304478356274 nsec\nrounds: 52296"
          },
          {
            "name": "tests/perf/test_serialization.py::test_pipeline_page_model_dump_json",
            "value": 376791.9919706015,
            "unit": "iter/sec",
            "range": "stddev: 3.740707250308925e-7",
            "extra": "mean: 2.653984217578656 usec\nrounds: 46951"
          },
          {
            "name": "tests/perf/test_serialization.py::test_cursor_page_model_dump[20]",
            "value": 577736.5201987071,
            "unit": "iter/sec",
            "range": "stddev: 2.545700440700304e-7",
            "extra": "mean: 1.7308928292365164 usec\nrounds: 62685"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_json_dumps[20]",
            "value": 293354.9268686871,
            "unit": "iter/sec",
            "range": "stddev: 4.259826115918514e-7",
            "extra": "mean: 3.4088399696372735 usec\nrounds: 55402"
          },
          {
            "name": "tests/perf/test_serialization.py::test_fp_filtered_page_serialize[20]",
            "value": 51449.670864651045,
            "unit": "iter/sec",
            "range": "stddev: 9.597259578305898e-7",
            "extra": "mean: 19.43647030572277 usec\nrounds: 21031"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_create[100]",
            "value": 2475041.90273754,
            "unit": "iter/sec",
            "range": "stddev: 1.4219075720533952e-7",
            "extra": "mean: 404.0335635909606 nsec\nrounds: 178795"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_filtered_json_dumps[100]",
            "value": 12717.885667434522,
            "unit": "iter/sec",
            "range": "stddev: 0.0000024937027809025397",
            "extra": "mean: 78.62942207135927 usec\nrounds: 7956"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_json_dumps[1000]",
            "value": 19526.729522452897,
            "unit": "iter/sec",
            "range": "stddev: 0.000001839568663560346",
            "extra": "mean: 51.21185290399734 usec\nrounds: 11863"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_model_dump[100]",
            "value": 277691.53095355455,
            "unit": "iter/sec",
            "range": "stddev: 3.8451087890669795e-7",
            "extra": "mean: 3.601118106001063 usec\nrounds: 57931"
          },
          {
            "name": "tests/perf/test_serialization.py::test_raw_json_dumps[100]",
            "value": 131975.8552113128,
            "unit": "iter/sec",
            "range": "stddev: 5.641653155522647e-7",
            "extra": "mean: 7.577143549468595 usec\nrounds: 41477"
          },
          {
            "name": "tests/perf/test_serialization.py::test_offset_page_model_dump_json[20]",
            "value": 604065.409049923,
            "unit": "iter/sec",
            "range": "stddev: 2.55497457899493e-7",
            "extra": "mean: 1.6554498652270206 usec\nrounds: 67518"
          },
          {
            "name": "tests/perf/test_search.py::test_bench_search_sa_async_1k",
            "value": 26733.202321237568,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018314017177841136",
            "extra": "mean: 37.4066671094459 usec\nrounds: 5269"
          },
          {
            "name": "tests/perf/test_search.py::test_bench_search_sa_sync_1k",
            "value": 26685.79264128952,
            "unit": "iter/sec",
            "range": "stddev: 0.0000017713996846958856",
            "extra": "mean: 37.47312337474858 usec\nrounds: 6922"
          },
          {
            "name": "tests/perf/test_search.py::test_bench_search_memory_10k",
            "value": 393.7867743579103,
            "unit": "iter/sec",
            "range": "stddev: 0.00002244983998536662",
            "extra": "mean: 2.539445367688012 msec\nrounds: 359"
          },
          {
            "name": "tests/perf/test_search.py::test_bench_search_sa_sync_10k",
            "value": 26759.287445430116,
            "unit": "iter/sec",
            "range": "stddev: 0.0000017682145942549165",
            "extra": "mean: 37.37020285160013 usec\nrounds: 6172"
          },
          {
            "name": "tests/perf/test_search.py::test_bench_search_sa_async_10k",
            "value": 26660.41737299738,
            "unit": "iter/sec",
            "range": "stddev: 0.0000019624924754108345",
            "extra": "mean: 37.508790129176134 usec\nrounds: 6504"
          },
          {
            "name": "tests/perf/test_search.py::test_bench_search_memory_100k",
            "value": 26.42823714073499,
            "unit": "iter/sec",
            "range": "stddev: 0.0003463556773970946",
            "extra": "mean: 37.83831644444633 msec\nrounds: 27"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_sort_10k",
            "value": 303.60455566730957,
            "unit": "iter/sec",
            "range": "stddev: 0.00014056842637137477",
            "extra": "mean: 3.2937582171718196 msec\nrounds: 198"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_search_10k",
            "value": 85.93841608972379,
            "unit": "iter/sec",
            "range": "stddev: 0.0002730995591888299",
            "extra": "mean: 11.63623959459472 msec\nrounds: 74"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_sa_pipeline_10k",
            "value": 220.3650922830227,
            "unit": "iter/sec",
            "range": "stddev: 0.00010778697208704834",
            "extra": "mean: 4.537923813793813 msec\nrounds: 145"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_pipeline_10k",
            "value": 293.20584338186745,
            "unit": "iter/sec",
            "range": "stddev: 0.0000938525489835693",
            "extra": "mean: 3.4105732289162227 msec\nrounds: 249"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_filter_10k",
            "value": 247.39508370925958,
            "unit": "iter/sec",
            "range": "stddev: 0.0001171121654271026",
            "extra": "mean: 4.042117511014111 msec\nrounds: 227"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_sa_10k",
            "value": 291.3627043740599,
            "unit": "iter/sec",
            "range": "stddev: 0.00009209679202693958",
            "extra": "mean: 3.432148263959587 msec\nrounds: 197"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_10k",
            "value": 301.9386965281294,
            "unit": "iter/sec",
            "range": "stddev: 0.006704768804836027",
            "extra": "mean: 3.3119305723267485 msec\nrounds: 318"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_fp_fastapi_sa_10k",
            "value": 235.75730965353048,
            "unit": "iter/sec",
            "range": "stddev: 0.00011246147778105173",
            "extra": "mean: 4.241650031846743 msec\nrounds: 157"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_sa_search_10k",
            "value": 221.22520383924189,
            "unit": "iter/sec",
            "range": "stddev: 0.00012825867508149235",
            "extra": "mean: 4.520280612902822 msec\nrounds: 155"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_fp_fastapi_offset_10k",
            "value": 293.6546534448874,
            "unit": "iter/sec",
            "range": "stddev: 0.00009153258343580773",
            "extra": "mean: 3.405360644787733 msec\nrounds: 259"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_filter_10k",
            "value": 285.3572017785243,
            "unit": "iter/sec",
            "range": "stddev: 0.0001056196746332149",
            "extra": "mean: 3.5043797519998634 msec\nrounds: 250"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_sa_pipeline_10k",
            "value": 178.43528182457442,
            "unit": "iter/sec",
            "range": "stddev: 0.0001357817924853224",
            "extra": "mean: 5.604272819672136 msec\nrounds: 122"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_1k",
            "value": 291.2356578320947,
            "unit": "iter/sec",
            "range": "stddev: 0.00010637196267461151",
            "extra": "mean: 3.433645479553631 msec\nrounds: 269"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_sa_filter_10k",
            "value": 176.00342112969525,
            "unit": "iter/sec",
            "range": "stddev: 0.010892952774434733",
            "extra": "mean: 5.681707739437119 msec\nrounds: 142"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_sa_sort_10k",
            "value": 139.5873314404468,
            "unit": "iter/sec",
            "range": "stddev: 0.0001547318317979895",
            "extra": "mean: 7.163973905659465 msec\nrounds: 106"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_search_10k",
            "value": 215.96608109828406,
            "unit": "iter/sec",
            "range": "stddev: 0.00011317625362702485",
            "extra": "mean: 4.630356743589331 msec\nrounds: 195"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_pipeline_10k",
            "value": 147.70416414997126,
            "unit": "iter/sec",
            "range": "stddev: 0.0001652099817484946",
            "extra": "mean: 6.7702898273379155 msec\nrounds: 139"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_sa_sort_10k",
            "value": 208.69018965249168,
            "unit": "iter/sec",
            "range": "stddev: 0.00027059816006803656",
            "extra": "mean: 4.791792089820742 msec\nrounds: 167"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_fp_fastapi_pipeline_10k",
            "value": 202.9330358377234,
            "unit": "iter/sec",
            "range": "stddev: 0.00014158961517156626",
            "extra": "mean: 4.92773389937189 msec\nrounds: 159"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_100k",
            "value": 256.64451866721697,
            "unit": "iter/sec",
            "range": "stddev: 0.00015019359019921143",
            "extra": "mean: 3.8964401234560135 msec\nrounds: 243"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_raw_fastapi_offset_10k",
            "value": 260.24239422402485,
            "unit": "iter/sec",
            "range": "stddev: 0.00009180964394013997",
            "extra": "mean: 3.842571472575558 msec\nrounds: 237"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_sa_10k",
            "value": 208.72758875156492,
            "unit": "iter/sec",
            "range": "stddev: 0.00011140712707744541",
            "extra": "mean: 4.79093351282008 msec\nrounds: 156"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_sort_10k",
            "value": 152.93380696027666,
            "unit": "iter/sec",
            "range": "stddev: 0.00015110042848970028",
            "extra": "mean: 6.538776611110858 msec\nrounds: 144"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_sa_search_10k",
            "value": 152.289335116952,
            "unit": "iter/sec",
            "range": "stddev: 0.00015123673204975094",
            "extra": "mean: 6.566447999999743 msec\nrounds: 118"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_offset_10k",
            "value": 236.8026973825158,
            "unit": "iter/sec",
            "range": "stddev: 0.00011879697506282297",
            "extra": "mean: 4.22292486974785 msec\nrounds: 238"
          },
          {
            "name": "tests/perf/test_fastapi_perf.py::test_pypaginate_fastapi_sa_filter_10k",
            "value": 134.91738634983108,
            "unit": "iter/sec",
            "range": "stddev: 0.017804329541968023",
            "extra": "mean: 7.411943167999652 msec\nrounds: 125"
          },
          {
            "name": "tests/perf/test_sorting.py::test_bench_sort_sa_async_10k",
            "value": 52131.11897871775,
            "unit": "iter/sec",
            "range": "stddev: 0.000006186264217467697",
            "extra": "mean: 19.18240044700066 usec\nrounds: 11637"
          },
          {
            "name": "tests/perf/test_sorting.py::test_bench_sort_memory_10k",
            "value": 495.6017734571406,
            "unit": "iter/sec",
            "range": "stddev: 0.0000290272857670022",
            "extra": "mean: 2.0177490347226925 msec\nrounds: 432"
          },
          {
            "name": "tests/perf/test_sorting.py::test_bench_sort_sa_async_1k",
            "value": 52611.78139882995,
            "unit": "iter/sec",
            "range": "stddev: 0.000006002587946193299",
            "extra": "mean: 19.007149604370536 usec\nrounds: 8596"
          },
          {
            "name": "tests/perf/test_sorting.py::test_bench_sort_sa_sync_1k",
            "value": 52729.276515602214,
            "unit": "iter/sec",
            "range": "stddev: 0.0000060389253760274985",
            "extra": "mean: 18.964796524452733 usec\nrounds: 10876"
          },
          {
            "name": "tests/perf/test_sorting.py::test_bench_sort_memory_100k",
            "value": 44.95941563215895,
            "unit": "iter/sec",
            "range": "stddev: 0.00013658504674605122",
            "extra": "mean: 22.24228197674152 msec\nrounds: 43"
          },
          {
            "name": "tests/perf/test_sorting.py::test_bench_sort_sa_sync_10k",
            "value": 52192.18603247388,
            "unit": "iter/sec",
            "range": "stddev: 0.000006364563008121624",
            "extra": "mean: 19.15995623133704 usec\nrounds: 13023"
          },
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_memory_100k",
            "value": 613370.14187143,
            "unit": "iter/sec",
            "range": "stddev: 3.457226495904984e-7",
            "extra": "mean: 1.6303369396967033 usec\nrounds: 107678"
          },
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_sa_sync_1k",
            "value": 2791.517148970229,
            "unit": "iter/sec",
            "range": "stddev: 0.00003181004785785495",
            "extra": "mean: 358.22814141367286 usec\nrounds: 396"
          },
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_sa_async_10k",
            "value": 1037.6191971358037,
            "unit": "iter/sec",
            "range": "stddev: 0.000060155894511317606",
            "extra": "mean: 963.7446982094723 usec\nrounds: 782"
          },
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_memory_10k",
            "value": 610023.5412349574,
            "unit": "iter/sec",
            "range": "stddev: 2.5535123065955897e-7",
            "extra": "mean: 1.639280998853844 usec\nrounds: 118456"
          },
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_sa_sync_10k",
            "value": 2775.4710603953886,
            "unit": "iter/sec",
            "range": "stddev: 0.000030420307794307677",
            "extra": "mean: 360.2991990330974 usec\nrounds: 1241"
          },
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_memory_1k",
            "value": 618598.6700181535,
            "unit": "iter/sec",
            "range": "stddev: 3.0098903862015306e-7",
            "extra": "mean: 1.6165569834973195 usec\nrounds: 141383"
          },
          {
            "name": "tests/perf/test_pagination.py::test_bench_paginate_sa_async_1k",
            "value": 1056.3643848221636,
            "unit": "iter/sec",
            "range": "stddev: 0.000032545801922175326",
            "extra": "mean: 946.6430470091508 usec\nrounds: 468"
          },
          {
            "name": "tests/perf/test_comparison.py::test_raw_list_slice_10k",
            "value": 4738531.490749862,
            "unit": "iter/sec",
            "range": "stddev: 2.035136527741747e-8",
            "extra": "mean: 211.03584558889148 nsec\nrounds: 191939"
          },
          {
            "name": "tests/perf/test_comparison.py::test_memory_sort_10k",
            "value": 490.8766487839427,
            "unit": "iter/sec",
            "range": "stddev: 0.000018827963584890408",
            "extra": "mean: 2.0371716651776315 msec\nrounds: 448"
          },
          {
            "name": "tests/perf/test_comparison.py::test_raw_list_filter_10k",
            "value": 3707.100965304363,
            "unit": "iter/sec",
            "range": "stddev: 0.00000573235251171909",
            "extra": "mean: 269.7525665902378 usec\nrounds: 3484"
          },
          {
            "name": "tests/perf/test_comparison.py::test_raw_list_search_10k",
            "value": 1800.9381921159322,
            "unit": "iter/sec",
            "range": "stddev: 0.000008305410010756999",
            "extra": "mean: 555.2661409357389 usec\nrounds: 1710"
          },
          {
            "name": "tests/perf/test_comparison.py::test_memory_search_10k",
            "value": 388.2929303427031,
            "unit": "iter/sec",
            "range": "stddev: 0.00005742485153235708",
            "extra": "mean: 2.57537524342102 msec\nrounds: 304"
          },
          {
            "name": "tests/perf/test_comparison.py::test_sa_async_paginate_10k",
            "value": 1016.2254917263738,
            "unit": "iter/sec",
            "range": "stddev: 0.000053263589720199256",
            "extra": "mean: 984.0335714283159 usec\nrounds: 637"
          },
          {
            "name": "tests/perf/test_comparison.py::test_memory_pipeline_10k",
            "value": 320.8938436419198,
            "unit": "iter/sec",
            "range": "stddev: 0.00023168659357843772",
            "extra": "mean: 3.116295372484253 msec\nrounds: 298"
          },
          {
            "name": "tests/perf/test_comparison.py::test_memory_filter_10k",
            "value": 874.4167174806726,
            "unit": "iter/sec",
            "range": "stddev: 0.00003118227743316426",
            "extra": "mean: 1.1436194894365148 msec\nrounds: 852"
          },
          {
            "name": "tests/perf/test_comparison.py::test_sa_sync_paginate_10k",
            "value": 2655.922486369629,
            "unit": "iter/sec",
            "range": "stddev: 0.000016621492600620165",
            "extra": "mean: 376.51701250020153 usec\nrounds: 1200"
          },
          {
            "name": "tests/perf/test_comparison.py::test_memory_paginate_10k",
            "value": 608645.4558892867,
            "unit": "iter/sec",
            "range": "stddev: 2.625610666200752e-7",
            "extra": "mean: 1.6429926327781557 usec\nrounds: 106146"
          },
          {
            "name": "tests/perf/test_comparison.py::test_raw_pipeline_10k",
            "value": 1424.9751174887674,
            "unit": "iter/sec",
            "range": "stddev: 0.000018133364242901415",
            "extra": "mean: 701.7666398009105 usec\nrounds: 1005"
          },
          {
            "name": "tests/perf/test_comparison.py::test_raw_list_sort_10k",
            "value": 1642.0169370305005,
            "unit": "iter/sec",
            "range": "stddev: 0.000010331225244318943",
            "extra": "mean: 609.0071164603494 usec\nrounds: 1537"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_pipeline_scaling[100K]",
            "value": 26.10920763988003,
            "unit": "iter/sec",
            "range": "stddev: 0.0010742999283403453",
            "extra": "mean: 38.30066441666228 msec\nrounds: 24"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_search_scaling[1K]",
            "value": 225.72741148322928,
            "unit": "iter/sec",
            "range": "stddev: 0.00026218444783892333",
            "extra": "mean: 4.430122125749429 msec\nrounds: 167"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_filter_scaling[1K]",
            "value": 225.89103304125868,
            "unit": "iter/sec",
            "range": "stddev: 0.0001489293193597634",
            "extra": "mean: 4.426913218008753 msec\nrounds: 211"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_sort_scaling[10K]",
            "value": 193.8020275901586,
            "unit": "iter/sec",
            "range": "stddev: 0.00011606689065052269",
            "extra": "mean: 5.159904735954273 msec\nrounds: 178"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_paginate_scaling[100K]",
            "value": 218.50285518260944,
            "unit": "iter/sec",
            "range": "stddev: 0.00011364695814439532",
            "extra": "mean: 4.57659923557644 msec\nrounds: 208"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_sort_scaling[10K]",
            "value": 139.5019440601646,
            "unit": "iter/sec",
            "range": "stddev: 0.00024750180426286796",
            "extra": "mean: 7.168358883720779 msec\nrounds: 129"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_pipeline_scaling[1K]",
            "value": 211.1977436354552,
            "unit": "iter/sec",
            "range": "stddev: 0.00013611517597089358",
            "extra": "mean: 4.734899070352204 msec\nrounds: 199"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_filter_scaling[1K]",
            "value": 199.69658881717586,
            "unit": "iter/sec",
            "range": "stddev: 0.00011681750306508064",
            "extra": "mean: 5.007596804347568 msec\nrounds: 184"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_search_scaling[1K]",
            "value": 177.25456225186042,
            "unit": "iter/sec",
            "range": "stddev: 0.0001503017474285882",
            "extra": "mean: 5.64160373248449 msec\nrounds: 157"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_search_scaling[100K]",
            "value": 57.946445315770134,
            "unit": "iter/sec",
            "range": "stddev: 0.0005655982098212802",
            "extra": "mean: 17.257313965518602 msec\nrounds: 58"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_filter_scaling[100K]",
            "value": 116.03457347224514,
            "unit": "iter/sec",
            "range": "stddev: 0.0003921853372427359",
            "extra": "mean: 8.618121048544163 msec\nrounds: 103"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_fp_http_paginate_scaling[1K]",
            "value": 155.9119234494735,
            "unit": "iter/sec",
            "range": "stddev: 0.014145218125590416",
            "extra": "mean: 6.41387764242464 msec\nrounds: 165"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_search_scaling[10K]",
            "value": 61.54138868850202,
            "unit": "iter/sec",
            "range": "stddev: 0.0009456438629508901",
            "extra": "mean: 16.249227086206997 msec\nrounds: 58"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_pipeline_scaling[1K]",
            "value": 184.33630631728673,
            "unit": "iter/sec",
            "range": "stddev: 0.00013731477629203416",
            "extra": "mean: 5.424867298136927 msec\nrounds: 161"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_search_scaling[10K]",
            "value": 156.21156550296575,
            "unit": "iter/sec",
            "range": "stddev: 0.0002959062452200438",
            "extra": "mean: 6.401574664335685 msec\nrounds: 143"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_fp_http_paginate_scaling[10K]",
            "value": 181.52076741290037,
            "unit": "iter/sec",
            "range": "stddev: 0.00011442681649467773",
            "extra": "mean: 5.509011526627843 msec\nrounds: 169"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_filter_scaling[100K]",
            "value": 51.369641665505334,
            "unit": "iter/sec",
            "range": "stddev: 0.0006291282968120232",
            "extra": "mean: 19.46675054717189 msec\nrounds: 53"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_search_scaling[100K]",
            "value": 9.27104376024212,
            "unit": "iter/sec",
            "range": "stddev: 0.000710442567918809",
            "extra": "mean: 107.86272029999395 msec\nrounds: 10"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_filter_scaling[10K]",
            "value": 149.8416293850265,
            "unit": "iter/sec",
            "range": "stddev: 0.00014976756858356535",
            "extra": "mean: 6.673712800001953 msec\nrounds: 115"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_paginate_scaling[10K]",
            "value": 193.78549921185135,
            "unit": "iter/sec",
            "range": "stddev: 0.00011232398720523275",
            "extra": "mean: 5.160344835228223 msec\nrounds: 176"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_paginate_scaling[10K]",
            "value": 187.04819728664606,
            "unit": "iter/sec",
            "range": "stddev: 0.0001226335531322144",
            "extra": "mean: 5.346215651934504 msec\nrounds: 181"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_filter_scaling[10K]",
            "value": 174.4307202353827,
            "unit": "iter/sec",
            "range": "stddev: 0.00011893342666999478",
            "extra": "mean: 5.732935108280046 msec\nrounds: 157"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_paginate_scaling[100K]",
            "value": 185.29306127148186,
            "unit": "iter/sec",
            "range": "stddev: 0.00012272754697155187",
            "extra": "mean: 5.396856164704686 msec\nrounds: 170"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_sort_scaling[1K]",
            "value": 177.98784902953497,
            "unit": "iter/sec",
            "range": "stddev: 0.00014079541661083915",
            "extra": "mean: 5.618361059209508 msec\nrounds: 152"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_pipeline_scaling[100K]",
            "value": 57.45499356318281,
            "unit": "iter/sec",
            "range": "stddev: 0.0010128491586719958",
            "extra": "mean: 17.40492754385757 msec\nrounds: 57"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_sort_scaling[100K]",
            "value": 73.68695892060926,
            "unit": "iter/sec",
            "range": "stddev: 0.0006729340283174112",
            "extra": "mean: 13.57092238095218 msec\nrounds: 63"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_fp_http_paginate_scaling[100K]",
            "value": 170.46288605027107,
            "unit": "iter/sec",
            "range": "stddev: 0.0001297849958356957",
            "extra": "mean: 5.866379615942269 msec\nrounds: 138"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_paginate_scaling[1K]",
            "value": 176.0608153180227,
            "unit": "iter/sec",
            "range": "stddev: 0.0001329406289520459",
            "extra": "mean: 5.679855555557192 msec\nrounds: 171"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_pipeline_scaling[10K]",
            "value": 152.11615066165965,
            "unit": "iter/sec",
            "range": "stddev: 0.00013818447761034533",
            "extra": "mean: 6.573923910448034 msec\nrounds: 134"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_pipeline_scaling[10K]",
            "value": 111.77288638609593,
            "unit": "iter/sec",
            "range": "stddev: 0.00024624697618832244",
            "extra": "mean: 8.946713575470442 msec\nrounds: 106"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_raw_http_paginate_scaling[1K]",
            "value": 173.49127965242673,
            "unit": "iter/sec",
            "range": "stddev: 0.00012511454804350338",
            "extra": "mean: 5.763978466257237 msec\nrounds: 163"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_sort_scaling[100K]",
            "value": 32.049987147054836,
            "unit": "iter/sec",
            "range": "stddev: 0.0006307794377681279",
            "extra": "mean: 31.201260562498945 msec\nrounds: 32"
          },
          {
            "name": "tests/perf/test_fastapi_scaling.py::test_pypaginate_http_sort_scaling[1K]",
            "value": 159.57294115248993,
            "unit": "iter/sec",
            "range": "stddev: 0.00014037546016337776",
            "extra": "mean: 6.266726631580897 msec\nrounds: 114"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_search_scaling[100K]",
            "value": 72.59253117291567,
            "unit": "iter/sec",
            "range": "stddev: 0.00010392151933310519",
            "extra": "mean: 13.775521859376916 msec\nrounds: 64"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_pipeline_scaling[10K]",
            "value": 344.2844224380755,
            "unit": "iter/sec",
            "range": "stddev: 0.000026196186035558433",
            "extra": "mean: 2.904575214058267 msec\nrounds: 313"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_filter_scaling[100K]",
            "value": 189.03556347918354,
            "unit": "iter/sec",
            "range": "stddev: 0.00018112112909277696",
            "extra": "mean: 5.290009888060663 msec\nrounds: 134"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_sort_scaling[100K]",
            "value": 44.92994463659997,
            "unit": "iter/sec",
            "range": "stddev: 0.00015334141842224077",
            "extra": "mean: 22.25687140476463 msec\nrounds: 42"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_paginate_scaling[500K]",
            "value": 626399.3918139746,
            "unit": "iter/sec",
            "range": "stddev: 2.959910589278508e-7",
            "extra": "mean: 1.5964255602230464 usec\nrounds: 50383"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_paginate_scaling[10K]",
            "value": 2734.1423411406618,
            "unit": "iter/sec",
            "range": "stddev: 0.0000269389507643965",
            "extra": "mean: 365.7454057724033 usec\nrounds: 589"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_paginate_scaling[1K]",
            "value": 616614.8106647262,
            "unit": "iter/sec",
            "range": "stddev: 2.431570623192455e-7",
            "extra": "mean: 1.6217579965715954 usec\nrounds: 103606"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_paginate_scaling[100K]",
            "value": 2223.8382991156222,
            "unit": "iter/sec",
            "range": "stddev: 0.00003083129573742656",
            "extra": "mean: 449.67298224771145 usec\nrounds: 507"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_filter_scaling[10K]",
            "value": 839.3472533310149,
            "unit": "iter/sec",
            "range": "stddev: 0.000017129132845595488",
            "extra": "mean: 1.1914020043926064 msec\nrounds: 683"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_filter_scaling[1K]",
            "value": 861.8104490521837,
            "unit": "iter/sec",
            "range": "stddev: 0.00007049059682660796",
            "extra": "mean: 1.1603479641025434 msec\nrounds: 390"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_pipeline_scaling[1K]",
            "value": 1449.90636793395,
            "unit": "iter/sec",
            "range": "stddev: 0.000030465457443653632",
            "extra": "mean: 689.6997089715209 usec\nrounds: 457"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_sort_scaling[10K]",
            "value": 273.0693583421958,
            "unit": "iter/sec",
            "range": "stddev: 0.00006419934660656107",
            "extra": "mean: 3.662073277173977 msec\nrounds: 184"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_paginate_scaling[1K]",
            "value": 1033.0789950360331,
            "unit": "iter/sec",
            "range": "stddev: 0.00006972031827368401",
            "extra": "mean: 967.980188160849 usec\nrounds: 473"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_search_scaling[1K]",
            "value": 777.8857164328265,
            "unit": "iter/sec",
            "range": "stddev: 0.00008611481161640807",
            "extra": "mean: 1.2855358812676616 msec\nrounds: 379"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_pipeline_scaling[100K]",
            "value": 79.40100381119527,
            "unit": "iter/sec",
            "range": "stddev: 0.0002013021328227478",
            "extra": "mean: 12.594299215383515 msec\nrounds: 65"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_pipeline_scaling[500K]",
            "value": 5.831168793758599,
            "unit": "iter/sec",
            "range": "stddev: 0.0016605358606134703",
            "extra": "mean: 171.49220599999637 msec\nrounds: 6"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_paginate_scaling[1M]",
            "value": 616623.6627331034,
            "unit": "iter/sec",
            "range": "stddev: 3.732931624666302e-7",
            "extra": "mean: 1.6217347150896406 usec\nrounds: 50131"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_pipeline_scaling[10K]",
            "value": 549.1389165564202,
            "unit": "iter/sec",
            "range": "stddev: 0.00004193414586121046",
            "extra": "mean: 1.8210328385955084 msec\nrounds: 285"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_search_scaling[10K]",
            "value": 520.6176132188305,
            "unit": "iter/sec",
            "range": "stddev: 0.00004018537987623975",
            "extra": "mean: 1.9207955601372857 msec\nrounds: 291"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_filter_scaling[1K]",
            "value": 1827.842818376566,
            "unit": "iter/sec",
            "range": "stddev: 0.000030300512929197232",
            "extra": "mean: 547.0929939633263 usec\nrounds: 497"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_search_scaling[500K]",
            "value": 5.226890400434514,
            "unit": "iter/sec",
            "range": "stddev: 0.0013726531078927546",
            "extra": "mean: 191.31834100000825 msec\nrounds: 6"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_search_scaling[1K]",
            "value": 1444.9285281978446,
            "unit": "iter/sec",
            "range": "stddev: 0.000026736515585629837",
            "extra": "mean: 692.0757535649379 usec\nrounds: 491"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_paginate_scaling[100K]",
            "value": 953.7956460301018,
            "unit": "iter/sec",
            "range": "stddev: 0.00009085218928198739",
            "extra": "mean: 1.0484426136376386 msec\nrounds: 352"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_paginate_scaling[10K]",
            "value": 626183.2018367859,
            "unit": "iter/sec",
            "range": "stddev: 5.466548865898886e-7",
            "extra": "mean: 1.5969767267258141 usec\nrounds: 103552"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_filter_scaling[10K]",
            "value": 625.7155259998468,
            "unit": "iter/sec",
            "range": "stddev: 0.00007294194000678844",
            "extra": "mean: 1.598170348101998 msec\nrounds: 316"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_filter_scaling[500K]",
            "value": 16.24696915455992,
            "unit": "iter/sec",
            "range": "stddev: 0.0011907598965305117",
            "extra": "mean: 61.549941437498035 msec\nrounds: 16"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_pipeline_scaling[100K]",
            "value": 74.62800096402408,
            "unit": "iter/sec",
            "range": "stddev: 0.00014577971768849215",
            "extra": "mean: 13.399796150000991 msec\nrounds: 60"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_paginate_scaling[10K]",
            "value": 988.9583560285631,
            "unit": "iter/sec",
            "range": "stddev: 0.00008509719758913142",
            "extra": "mean: 1.0111649230770219 msec\nrounds: 403"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_sort_scaling[10K]",
            "value": 319.0751952901064,
            "unit": "iter/sec",
            "range": "stddev: 0.00004026556754748209",
            "extra": "mean: 3.1340574722230903 msec\nrounds: 216"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_search_scaling[100K]",
            "value": 25.773115049674953,
            "unit": "iter/sec",
            "range": "stddev: 0.0006356394197316569",
            "extra": "mean: 38.80012167999894 msec\nrounds: 25"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_filter_scaling[100K]",
            "value": 172.1909115914758,
            "unit": "iter/sec",
            "range": "stddev: 0.00012232802381974107",
            "extra": "mean: 5.807507439025047 msec\nrounds: 123"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_sort_scaling[100K]",
            "value": 28.84778921464615,
            "unit": "iter/sec",
            "range": "stddev: 0.00044033467620968695",
            "extra": "mean: 34.66470142856894 msec\nrounds: 28"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_search_scaling[100K]",
            "value": 67.12016473087262,
            "unit": "iter/sec",
            "range": "stddev: 0.00022156484668106876",
            "extra": "mean: 14.898652349999963 msec\nrounds: 60"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_filter_scaling[100K]",
            "value": 83.32025159703508,
            "unit": "iter/sec",
            "range": "stddev: 0.00023853358402248668",
            "extra": "mean: 12.00188406578917 msec\nrounds: 76"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_filter_scaling[1K]",
            "value": 8715.423483933528,
            "unit": "iter/sec",
            "range": "stddev: 0.000003744203597706317",
            "extra": "mean: 114.73911759347699 usec\nrounds: 7696"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_sort_scaling[1K]",
            "value": 4709.58070977794,
            "unit": "iter/sec",
            "range": "stddev: 0.0000044861776524526825",
            "extra": "mean: 212.3331272195462 usec\nrounds: 3773"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_search_scaling[1K]",
            "value": 4985.370368312186,
            "unit": "iter/sec",
            "range": "stddev: 0.0000064269021895099355",
            "extra": "mean: 200.58690250099784 usec\nrounds: 3159"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_filter_scaling[10K]",
            "value": 991.4824692207691,
            "unit": "iter/sec",
            "range": "stddev: 0.000032725528608625245",
            "extra": "mean: 1.00859070235092 msec\nrounds: 383"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_sort_scaling[1K]",
            "value": 783.9326475719865,
            "unit": "iter/sec",
            "range": "stddev: 0.00005398595606724289",
            "extra": "mean: 1.2756197909313027 msec\nrounds: 397"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_pipeline_scaling[1K]",
            "value": 771.7201107496644,
            "unit": "iter/sec",
            "range": "stddev: 0.00007942736629021429",
            "extra": "mean: 1.2958065833331465 msec\nrounds: 396"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_paginate_scaling[1K]",
            "value": 2939.2216592174036,
            "unit": "iter/sec",
            "range": "stddev: 0.00002499994742971497",
            "extra": "mean: 340.2261264862411 usec\nrounds: 672"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_sort_scaling[1K]",
            "value": 1412.8157245248228,
            "unit": "iter/sec",
            "range": "stddev: 0.00002549361016903328",
            "extra": "mean: 707.8063916200632 usec\nrounds: 549"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_search_scaling[10K]",
            "value": 397.48305615626,
            "unit": "iter/sec",
            "range": "stddev: 0.00006646019554596309",
            "extra": "mean: 2.5158305102869 msec\nrounds: 243"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_pipeline_scaling[1K]",
            "value": 3597.653398981714,
            "unit": "iter/sec",
            "range": "stddev: 0.000017204378224736896",
            "extra": "mean: 277.9589607723306 usec\nrounds: 3263"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_async_pipeline_scaling[10K]",
            "value": 409.3736935150812,
            "unit": "iter/sec",
            "range": "stddev: 0.00008288858058712321",
            "extra": "mean: 2.442755887447273 msec\nrounds: 231"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_pipeline_scaling[100K]",
            "value": 31.5723733141778,
            "unit": "iter/sec",
            "range": "stddev: 0.0005414169898666967",
            "extra": "mean: 31.673260354835058 msec\nrounds: 31"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_search_scaling[1M]",
            "value": 2.5634138011057233,
            "unit": "iter/sec",
            "range": "stddev: 0.0020825154548010966",
            "extra": "mean: 390.1047889999859 msec\nrounds: 5"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_filter_scaling[1M]",
            "value": 8.106579119647304,
            "unit": "iter/sec",
            "range": "stddev: 0.000985217444992569",
            "extra": "mean: 123.35659533333556 msec\nrounds: 9"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_sort_scaling[1M]",
            "value": 3.428923718937349,
            "unit": "iter/sec",
            "range": "stddev: 0.0015219561270066176",
            "extra": "mean: 291.6367006000087 msec\nrounds: 5"
          },
          {
            "name": "tests/perf/test_scaling.py::test_sa_sync_sort_scaling[100K]",
            "value": 29.96706094029149,
            "unit": "iter/sec",
            "range": "stddev: 0.00028646185370714177",
            "extra": "mean: 33.36997251724056 msec\nrounds: 29"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_pipeline_scaling[1M]",
            "value": 2.7739178772158506,
            "unit": "iter/sec",
            "range": "stddev: 0.00252099403741158",
            "extra": "mean: 360.50093920000563 msec\nrounds: 5"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_sort_scaling[10K]",
            "value": 444.3430641349267,
            "unit": "iter/sec",
            "range": "stddev: 0.00002442092541845429",
            "extra": "mean: 2.2505133549161145 msec\nrounds: 417"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_search_scaling[10K]",
            "value": 362.4911077424059,
            "unit": "iter/sec",
            "range": "stddev: 0.000029412113589465324",
            "extra": "mean: 2.758688361289739 msec\nrounds: 310"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_sort_scaling[500K]",
            "value": 7.118747209997752,
            "unit": "iter/sec",
            "range": "stddev: 0.0006346586463982386",
            "extra": "mean: 140.47415514285635 msec\nrounds: 7"
          },
          {
            "name": "tests/perf/test_scaling.py::test_memory_paginate_scaling[100K]",
            "value": 626458.4574682969,
            "unit": "iter/sec",
            "range": "stddev: 2.5109750058386643e-7",
            "extra": "mean: 1.5962750411915492 usec\nrounds: 47971"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_fp_paginate_scaling[1K]",
            "value": 19081.924475958676,
            "unit": "iter/sec",
            "range": "stddev: 0.0000022157425193410273",
            "extra": "mean: 52.40561565265077 usec\nrounds: 5162"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_paginate_scaling[500K]",
            "value": 3055527.612638284,
            "unit": "iter/sec",
            "range": "stddev: 1.115620570481147e-7",
            "extra": "mean: 327.2757201943771 nsec\nrounds: 197200"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_search_scaling[10K]",
            "value": 1302.2124228608025,
            "unit": "iter/sec",
            "range": "stddev: 0.000009817530502133866",
            "extra": "mean: 767.9238674463891 usec\nrounds: 1026"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_pipeline_scaling[500K]",
            "value": 15.8579861939103,
            "unit": "iter/sec",
            "range": "stddev: 0.0005867391451695056",
            "extra": "mean: 63.05970933333356 msec\nrounds: 15"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_sort_scaling[10K]",
            "value": 1386.3822981896774,
            "unit": "iter/sec",
            "range": "stddev: 0.000010894858076081597",
            "extra": "mean: 721.3017659744997 usec\nrounds: 1205"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_paginate_scaling[10K]",
            "value": 4290471.59000483,
            "unit": "iter/sec",
            "range": "stddev: 4.0178073730635616e-8",
            "extra": "mean: 233.07461173490051 nsec\nrounds: 199442"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_paginate_scaling[1K]",
            "value": 4270217.013489258,
            "unit": "iter/sec",
            "range": "stddev: 3.5003608998886434e-8",
            "extra": "mean: 234.18013577321526 nsec\nrounds: 191095"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_fp_paginate_scaling[100K]",
            "value": 19128.146075367993,
            "unit": "iter/sec",
            "range": "stddev: 0.0000029802197883918193",
            "extra": "mean: 52.27898177166977 usec\nrounds: 4718"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_fp_paginate_scaling[1M]",
            "value": 19152.840223715324,
            "unit": "iter/sec",
            "range": "stddev: 0.000002284266546677821",
            "extra": "mean: 52.2115774119906 usec\nrounds: 4560"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_paginate_lib_scaling[500K]",
            "value": 412553.53569313395,
            "unit": "iter/sec",
            "range": "stddev: 0.000006913092608031127",
            "extra": "mean: 2.4239278384074283 usec\nrounds: 49015"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_sort_scaling[100K]",
            "value": 142.37378723934071,
            "unit": "iter/sec",
            "range": "stddev: 0.00009902866519654047",
            "extra": "mean: 7.023764833332185 msec\nrounds: 126"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_pipeline_scaling[10K]",
            "value": 1505.3635181820669,
            "unit": "iter/sec",
            "range": "stddev: 0.000008965083767967494",
            "extra": "mean: 664.2913740912476 usec\nrounds: 1374"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_paginate_scaling[1M]",
            "value": 4301780.288274415,
            "unit": "iter/sec",
            "range": "stddev: 2.030330062405588e-8",
            "extra": "mean: 232.46189553793914 nsec\nrounds: 199721"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_paginate_lib_scaling[10K]",
            "value": 413913.1657134833,
            "unit": "iter/sec",
            "range": "stddev: 0.000006927168739379939",
            "extra": "mean: 2.4159656730808474 usec\nrounds: 74140"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_filter_scaling[500K]",
            "value": 51.351957254482706,
            "unit": "iter/sec",
            "range": "stddev: 0.00033918075288949984",
            "extra": "mean: 19.47345444000007 msec\nrounds: 50"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_search_scaling[500K]",
            "value": 37.29954794724576,
            "unit": "iter/sec",
            "range": "stddev: 0.00013263225349393308",
            "extra": "mean: 26.80997639473647 msec\nrounds: 38"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_filter_scaling[100K]",
            "value": 341.97475185058045,
            "unit": "iter/sec",
            "range": "stddev: 0.00007669188037487088",
            "extra": "mean: 2.924192486692502 msec\nrounds: 263"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_paginate_lib_scaling[1K]",
            "value": 423365.4757513708,
            "unit": "iter/sec",
            "range": "stddev: 0.0000068267458536078855",
            "extra": "mean: 2.3620253829749416 usec\nrounds: 93015"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_filter_scaling[1M]",
            "value": 25.096974540706494,
            "unit": "iter/sec",
            "range": "stddev: 0.0002025290495667948",
            "extra": "mean: 39.845440269225755 msec\nrounds: 26"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_search_scaling[1M]",
            "value": 18.276352589349706,
            "unit": "iter/sec",
            "range": "stddev: 0.00018965807344143126",
            "extra": "mean: 54.715512578956066 msec\nrounds: 19"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_search_scaling[100K]",
            "value": 187.23953764304093,
            "unit": "iter/sec",
            "range": "stddev: 0.00006587560552740158",
            "extra": "mean: 5.340752346368372 msec\nrounds: 179"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_pipeline_scaling[1K]",
            "value": 16329.340259229613,
            "unit": "iter/sec",
            "range": "stddev: 0.0000023783415176290515",
            "extra": "mean: 61.2394612473571 usec\nrounds: 13728"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_sort_scaling[500K]",
            "value": 17.767414172317572,
            "unit": "iter/sec",
            "range": "stddev: 0.0006377382751077403",
            "extra": "mean: 56.28281022221257 msec\nrounds: 18"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_paginate_lib_scaling[100K]",
            "value": 412611.4562482468,
            "unit": "iter/sec",
            "range": "stddev: 0.000006904298778607314",
            "extra": "mean: 2.4235875782332914 usec\nrounds: 66432"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_fp_paginate_scaling[500K]",
            "value": 19175.34653740051,
            "unit": "iter/sec",
            "range": "stddev: 0.0000022256786347198094",
            "extra": "mean: 52.15029611326983 usec\nrounds: 4657"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_sort_scaling[1M]",
            "value": 8.606905349999135,
            "unit": "iter/sec",
            "range": "stddev: 0.0002863573801989708",
            "extra": "mean: 116.18577866667262 msec\nrounds: 9"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_pipeline_scaling[1M]",
            "value": 7.683418007224279,
            "unit": "iter/sec",
            "range": "stddev: 0.0007154247730048435",
            "extra": "mean: 130.15040950001122 msec\nrounds: 8"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_pipeline_scaling[100K]",
            "value": 125.26956224408602,
            "unit": "iter/sec",
            "range": "stddev: 0.0002584760553899222",
            "extra": "mean: 7.982785140188435 msec\nrounds: 107"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_paginate_lib_scaling[1M]",
            "value": 413208.2859839562,
            "unit": "iter/sec",
            "range": "stddev: 0.000006915744671198174",
            "extra": "mean: 2.420086997090923 usec\nrounds: 57841"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_fp_paginate_scaling[10K]",
            "value": 19227.741586096716,
            "unit": "iter/sec",
            "range": "stddev: 0.0000026141394931836296",
            "extra": "mean: 52.00818804029926 usec\nrounds: 5201"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_search_scaling[1K]",
            "value": 18926.394402874088,
            "unit": "iter/sec",
            "range": "stddev: 0.000001831349438445424",
            "extra": "mean: 52.83626551965671 usec\nrounds: 16737"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_filter_scaling[1K]",
            "value": 38587.61804846179,
            "unit": "iter/sec",
            "range": "stddev: 0.0000011625294783265914",
            "extra": "mean: 25.91504867556506 usec\nrounds: 30693"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_sort_scaling[1K]",
            "value": 14748.827489088371,
            "unit": "iter/sec",
            "range": "stddev: 0.0000023740680388227576",
            "extra": "mean: 67.80199990404866 usec\nrounds: 10444"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_paginate_scaling[100K]",
            "value": 4369469.119649694,
            "unit": "iter/sec",
            "range": "stddev: 2.075498482182967e-8",
            "extra": "mean: 228.86075461729473 nsec\nrounds: 196503"
          },
          {
            "name": "tests/perf/test_competitor_scaling.py::test_raw_python_filter_scaling[10K]",
            "value": 3700.2882694053606,
            "unit": "iter/sec",
            "range": "stddev: 0.0000073566299958142744",
            "extra": "mean: 270.24921497824295 usec\nrounds: 3405"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_filter_scaling[1K]",
            "value": 1689.7500661755118,
            "unit": "iter/sec",
            "range": "stddev: 0.00002956668886531488",
            "extra": "mean: 591.8034980542095 usec\nrounds: 514"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_search_scaling[1K]",
            "value": 1618.6092060624642,
            "unit": "iter/sec",
            "range": "stddev: 0.000047437416030736106",
            "extra": "mean: 617.8143533686343 usec\nrounds: 549"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_pipeline_scaling[1K]",
            "value": 1453.1200302109928,
            "unit": "iter/sec",
            "range": "stddev: 0.00003061750356533427",
            "extra": "mean: 688.1743966152612 usec\nrounds: 532"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_paginate_scaling[10K]",
            "value": 2363.468435756456,
            "unit": "iter/sec",
            "range": "stddev: 0.000019841931897747055",
            "extra": "mean: 423.1069833094421 usec\nrounds: 659"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_filter_scaling[100K]",
            "value": 190.63978084063717,
            "unit": "iter/sec",
            "range": "stddev: 0.00014405478869992114",
            "extra": "mean: 5.2454949097740355 msec\nrounds: 133"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_search_scaling[100K]",
            "value": 148.27817547687954,
            "unit": "iter/sec",
            "range": "stddev: 0.00013647161857807994",
            "extra": "mean: 6.744080825002641 msec\nrounds: 120"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_fp_sa_paginate_scaling[10K]",
            "value": 1514.3905931165777,
            "unit": "iter/sec",
            "range": "stddev: 0.00002349187709936258",
            "extra": "mean: 660.3316241829165 usec\nrounds: 306"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_fastapi_filter_scaling[10K]",
            "value": 2608.882453708667,
            "unit": "iter/sec",
            "range": "stddev: 0.000015687693867332776",
            "extra": "mean: 383.30588585102646 usec\nrounds: 841"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_paginate_scaling[1K]",
            "value": 816.1029775121716,
            "unit": "iter/sec",
            "range": "stddev: 0.00007969496930999132",
            "extra": "mean: 1.225335561265105 msec\nrounds: 506"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_fp_sa_paginate_scaling[100K]",
            "value": 1351.4703632146663,
            "unit": "iter/sec",
            "range": "stddev: 0.00002423179388856987",
            "extra": "mean: 739.9348348426645 usec\nrounds: 442"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_paginate_scaling[100K]",
            "value": 780.733584965531,
            "unit": "iter/sec",
            "range": "stddev: 0.00010583033225523482",
            "extra": "mean: 1.2808466540403145 msec\nrounds: 396"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_pipeline_scaling[10K]",
            "value": 572.5307771676495,
            "unit": "iter/sec",
            "range": "stddev: 0.00004111691316848541",
            "extra": "mean: 1.7466309932665476 msec\nrounds: 297"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_fastapi_filter_scaling[100K]",
            "value": 2605.494576567658,
            "unit": "iter/sec",
            "range": "stddev: 0.000019665017079476135",
            "extra": "mean: 383.80429151280276 usec\nrounds: 813"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_filter_scaling[10K]",
            "value": 953.4793668420446,
            "unit": "iter/sec",
            "range": "stddev: 0.00004243827657521611",
            "extra": "mean: 1.0487903931387978 msec\nrounds: 379"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_pipeline_scaling[100K]",
            "value": 79.06812731474713,
            "unit": "iter/sec",
            "range": "stddev: 0.00013759406740325287",
            "extra": "mean: 12.647321164181516 msec\nrounds: 67"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_fastapi_filter_scaling[1K]",
            "value": 2608.6869299278624,
            "unit": "iter/sec",
            "range": "stddev: 0.000015433601658393784",
            "extra": "mean: 383.33461502321893 usec\nrounds: 1065"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_search_scaling[1K]",
            "value": 731.6769056868122,
            "unit": "iter/sec",
            "range": "stddev: 0.00007590557079880874",
            "extra": "mean: 1.3667234707392024 msec\nrounds: 393"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_filter_scaling[1K]",
            "value": 728.2131041610885,
            "unit": "iter/sec",
            "range": "stddev: 0.00008649106563338335",
            "extra": "mean: 1.373224395833983 msec\nrounds: 384"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_filter_scaling[10K]",
            "value": 554.4588657892173,
            "unit": "iter/sec",
            "range": "stddev: 0.00008041973207307323",
            "extra": "mean: 1.803560303029151 msec\nrounds: 297"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_search_scaling[10K]",
            "value": 827.5093200260324,
            "unit": "iter/sec",
            "range": "stddev: 0.0000353388633359638",
            "extra": "mean: 1.2084456039341542 msec\nrounds: 356"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_search_scaling[100K]",
            "value": 131.01879194121057,
            "unit": "iter/sec",
            "range": "stddev: 0.000187542155594",
            "extra": "mean: 7.632492905664326 msec\nrounds: 106"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_filter_scaling[100K]",
            "value": 166.59406408506655,
            "unit": "iter/sec",
            "range": "stddev: 0.00010517176081776252",
            "extra": "mean: 6.002614831998926 msec\nrounds: 125"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_pipeline_scaling[10K]",
            "value": 397.7894371622561,
            "unit": "iter/sec",
            "range": "stddev: 0.000130639192020794",
            "extra": "mean: 2.513892794976619 msec\nrounds: 239"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_sa_pagination_lib_scaling[1K]",
            "value": 1849.750075419208,
            "unit": "iter/sec",
            "range": "stddev: 0.000020374978408198754",
            "extra": "mean: 540.6135743897025 usec\nrounds: 531"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_pipeline_scaling[1K]",
            "value": 648.6394501374509,
            "unit": "iter/sec",
            "range": "stddev: 0.00009476227299938536",
            "extra": "mean: 1.541688529410435 msec\nrounds: 374"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_search_scaling[10K]",
            "value": 515.815024539276,
            "unit": "iter/sec",
            "range": "stddev: 0.00007608050423657273",
            "extra": "mean: 1.9386794731177055 msec\nrounds: 279"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_pipeline_scaling[100K]",
            "value": 82.13496851256099,
            "unit": "iter/sec",
            "range": "stddev: 0.0002974225043695858",
            "extra": "mean: 12.175082283583867 msec\nrounds: 67"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_sa_pagination_lib_scaling[10K]",
            "value": 1777.098619766358,
            "unit": "iter/sec",
            "range": "stddev: 0.00002607578815432296",
            "extra": "mean: 562.7149719645125 usec\nrounds: 428"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_sort_scaling[1K]",
            "value": 1199.0843653630768,
            "unit": "iter/sec",
            "range": "stddev: 0.00002278464109342973",
            "extra": "mean: 833.9696762681122 usec\nrounds: 729"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_sort_scaling[1K]",
            "value": 2785.517665797037,
            "unit": "iter/sec",
            "range": "stddev: 0.000017665527204873647",
            "extra": "mean: 358.99969771466664 usec\nrounds: 1181"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_paginate_scaling[1K]",
            "value": 2462.022880290691,
            "unit": "iter/sec",
            "range": "stddev: 0.000016242163115412793",
            "extra": "mean: 406.1700677135584 usec\nrounds: 827"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_paginate_scaling[100K]",
            "value": 2006.0744969833947,
            "unit": "iter/sec",
            "range": "stddev: 0.000023724961409474206",
            "extra": "mean: 498.48597422664784 usec\nrounds: 582"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_sort_scaling[10K]",
            "value": 767.5212829364034,
            "unit": "iter/sec",
            "range": "stddev: 0.0000697706956723863",
            "extra": "mean: 1.3028954665259227 msec\nrounds: 478"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_sort_scaling[100K]",
            "value": 200.15240524100594,
            "unit": "iter/sec",
            "range": "stddev: 0.0000679978322235564",
            "extra": "mean: 4.9961927701837405 msec\nrounds: 161"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_sort_scaling[100K]",
            "value": 181.99882125592066,
            "unit": "iter/sec",
            "range": "stddev: 0.00007324926794660932",
            "extra": "mean: 5.494541080537183 msec\nrounds: 149"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_sort_scaling[10K]",
            "value": 1220.27212319047,
            "unit": "iter/sec",
            "range": "stddev: 0.000021263801404513128",
            "extra": "mean: 819.4893425783126 usec\nrounds: 613"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_raw_sa_async_paginate_scaling[10K]",
            "value": 830.3232514955729,
            "unit": "iter/sec",
            "range": "stddev: 0.000082257255109833",
            "extra": "mean: 1.2043502313090795 msec\nrounds: 428"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_sa_pagination_lib_scaling[100K]",
            "value": 1534.385153856659,
            "unit": "iter/sec",
            "range": "stddev: 0.000021636829143806782",
            "extra": "mean: 651.7268480384549 usec\nrounds: 408"
          },
          {
            "name": "tests/perf/test_competitor_scaling_sa.py::test_fp_sa_paginate_scaling[1K]",
            "value": 1510.2350339353952,
            "unit": "iter/sec",
            "range": "stddev: 0.000026290761305237466",
            "extra": "mean: 662.1485911329866 usec\nrounds: 609"
          },
          {
            "name": "tests/perf/test_pipeline.py::test_bench_pipeline_memory_100k",
            "value": 32.964533524308045,
            "unit": "iter/sec",
            "range": "stddev: 0.0002010656428291541",
            "extra": "mean: 30.33563327272931 msec\nrounds: 33"
          },
          {
            "name": "tests/perf/test_pipeline.py::test_bench_pipeline_sa_sync_10k",
            "value": 319.9340675604925,
            "unit": "iter/sec",
            "range": "stddev: 0.00004190960762154444",
            "extra": "mean: 3.125644004169459 msec\nrounds: 240"
          },
          {
            "name": "tests/perf/test_pipeline.py::test_bench_pipeline_memory_10k",
            "value": 328.5368238959311,
            "unit": "iter/sec",
            "range": "stddev: 0.000021652783459050604",
            "extra": "mean: 3.0437988294327845 msec\nrounds: 299"
          },
          {
            "name": "tests/perf/test_pipeline.py::test_bench_pipeline_sa_async_10k",
            "value": 258.34855363329444,
            "unit": "iter/sec",
            "range": "stddev: 0.00007075559943422041",
            "extra": "mean: 3.8707396884420797 msec\nrounds: 199"
          },
          {
            "name": "tests/perf/test_pipeline.py::test_bench_pipeline_sa_sync_1k",
            "value": 1386.2061081424497,
            "unit": "iter/sec",
            "range": "stddev: 0.00002469480248329345",
            "extra": "mean: 721.3934451205273 usec\nrounds: 492"
          },
          {
            "name": "tests/perf/test_pipeline.py::test_bench_pipeline_sa_async_1k",
            "value": 736.616008580925,
            "unit": "iter/sec",
            "range": "stddev: 0.00008673769524742527",
            "extra": "mean: 1.3575594181376516 msec\nrounds: 397"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_memory_10k_single",
            "value": 881.3254485725148,
            "unit": "iter/sec",
            "range": "stddev: 0.00003687918087239549",
            "extra": "mean: 1.1346546291380815 msec\nrounds: 755"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_memory_100k",
            "value": 86.24918730649708,
            "unit": "iter/sec",
            "range": "stddev: 0.00008841323466828094",
            "extra": "mean: 11.594312146343794 msec\nrounds: 82"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_sa_sync_10k",
            "value": 27465.44072745207,
            "unit": "iter/sec",
            "range": "stddev: 0.0000017430627609284346",
            "extra": "mean: 36.40939207651188 usec\nrounds: 5124"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_sa_async_10k",
            "value": 27542.09026785821,
            "unit": "iter/sec",
            "range": "stddev: 0.0000016615073033651754",
            "extra": "mean: 36.30806486634045 usec\nrounds: 6814"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_memory_10k_multi",
            "value": 283.1039590599133,
            "unit": "iter/sec",
            "range": "stddev: 0.00005930712353962204",
            "extra": "mean: 3.532271337075756 msec\nrounds: 267"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_sa_sync_1k",
            "value": 27683.536996580075,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018537025270265707",
            "extra": "mean: 36.122551830119704 usec\nrounds: 6174"
          },
          {
            "name": "tests/perf/test_filtering.py::test_bench_filter_sa_async_1k",
            "value": 27647.941877821562,
            "unit": "iter/sec",
            "range": "stddev: 0.0000019833794230919445",
            "extra": "mean: 36.169057516797416 usec\nrounds: 9319"
          }
        ]
      }
    ]
  }
}