import sys

if "--self-test" in sys.argv or "--self-test-engine" in sys.argv:
    from audio_transcriptor.diagnostics import run_self_test_cli

    raise SystemExit(run_self_test_cli(include_engine="--self-test-engine" in sys.argv))

from audio_transcriptor.app import main

raise SystemExit(main())
