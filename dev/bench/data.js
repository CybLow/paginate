window.BENCHMARK_DATA = {
  "lastUpdate": 1773715374752,
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
      }
    ]
  }
}