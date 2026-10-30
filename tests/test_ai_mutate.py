import json
import random
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "ai"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "library"))
import layer1  # noqa: E402
import mutate  # noqa: E402
import pilot  # noqa: E402
import runner  # noqa: E402
import sessions  # noqa: E402

PILOT = {"eu-cap9_en.pdf": ["Chapter 9 9.1", "Chapter 9 9.3"], "ich-q7.pdf": ["2.40"]}
VERDICT = {"required_by_clause": True, "item_adds": "", "item_omits": "", "strictness": "same",
           "plant_types_ok": True, "strength_ok": True, "verdict": "correct", "reason": "r"}


def answer_all(run_dir, make):
    for batch in sorted((run_dir / "batches").glob("batch_*.json")):
        items = json.loads(batch.read_text())["items"]
        (run_dir / "answers" / batch.name).write_text(json.dumps(
            {"answers": [{"custom_id": i["custom_id"], "answer": make(i["custom_id"], i["input"])} for i in items]}))


def real_mappings():
    """Correct mappings of real clauses: the first sentence of each clause, recommended, in scope."""
    out = []
    sources = layer1.catalog()
    for file, refs in PILOT.items():
        for ref in refs:
            clause = layer1.clauses_of(file)[ref]
            quote = next(s for s in pilot.obligations.sentences(pilot.normalise(clause["text"]))
                         if layer1.strength_of(s))
            scope = sorted(pilot.runner_scope(sources[file]["applies_to"]))
            out.append({"source": file, "ref": ref, "clause_sha256": clause["sha256"], "draft": "draft-000",
                        "statement": "Carry out self inspections at least once a year.", "quote": quote,
                        "strength": layer1.strength_of(quote), "plant_types": scope, "numbers": []})
    return out


class Mutants(unittest.TestCase):
    def test_change_number(self):
        self.assertEqual(mutate.change_number("at least once a year"), "at least twice a year")
        self.assertEqual(mutate.change_number("Once a year"), "Twice a year")
        self.assertEqual(mutate.change_number("within 30 days, then 5"), "within 31 days, then 5")
        self.assertIsNone(mutate.change_number("Keep a record of every self inspection."))
        self.assertIsNone(mutate.change_number("Section 9.3 applies"))   # a reference is not a number to change
        self.assertIsNone(mutate.change_number("Follow Chapter 9 of the guide."))
        self.assertIsNone(mutate.change_number("Once approved, the report is filed."))   # "once" = after
        self.assertIsNone(mutate.change_number("No one may change the record."))
        self.assertEqual(mutate.change_number("Keep for ten years; review 5 times."), "Keep for twelve years; review 5 times.")
        self.assertEqual(mutate.change_number("Once approved, review it once a year."),
                         "Once approved, review it twice a year.")

    def test_change_strength(self):
        m = {"strength": "recommended", "statement": "Reports should list all findings."}
        self.assertEqual(mutate.change_strength(m), ("mandatory", "Reports must list all findings."))
        self.assertEqual(mutate.change_strength({"strength": "mandatory", "statement": "Must keep."}),
                         ("recommended", "Should keep."))
        self.assertEqual(mutate.change_strength({"strength": "optional", "statement": "Audit."}),
                         ("mandatory", "Audit."))

    def test_outside_scope(self):
        self.assertIsNone(mutate.outside_scope("ALL"))
        self.assertEqual(mutate.outside_scope("API"), "OSD")
        self.assertEqual(mutate.outside_scope("OSD;LIQ;SEMI;INJ"), "API")

    def test_code_mutants_are_layer1_errors_and_controls_are_clean(self):
        maps, sources = real_mappings(), layer1.catalog()
        code = mutate.code_mutants(maps, sources, layer1.clauses_of, random.Random(1))
        self.assertEqual({k: len(v) for k, v in code.items()},
                         {"changed_number": 3, "strength": 3, "plant_type": 3, "wrong_clause": 3})
        for kind, group in code.items():
            for mu in group:
                self.assertTrue(mutate.layer1_findings(mu["mapping"], sources), (kind, mu["change"]))
                self.assertNotEqual(mu["mapping"], maps[mu["original"]])
        for m in maps:
            self.assertEqual(mutate.layer1_findings(m, sources), [])
        wrong = code["wrong_clause"][0]["mapping"]
        self.assertIn(wrong["ref"], layer1.clauses_of(wrong["source"]))
        self.assertNotEqual(wrong["ref"], maps[code["wrong_clause"][0]["original"]]["ref"])

    def test_wrong_clause_needs_another_clause(self):
        m = {"source": "s", "ref": "1"}
        self.assertIsNone(mutate.other_clause(m, lambda s: {"1": {"text": "x" * 100}}, random.Random(1), set()))
        tree = {"1": {"text": "x" * 100}, "2": {"text": "y" * 100}}
        self.assertEqual(mutate.other_clause(m, lambda s: tree, random.Random(1), {"2"})[0], "2")   # fallback

    def test_text_mutants_filter_and_force(self):
        maps = [{"source": "who-trs986-a2-gmp-main.pdf", "ref": r, "statement": f"item {r}"} for r in
                ("8.1", "8.9", "8.2")]
        reqs = [runner.Request(f"mutate-dropped_condition-{i:03d}", "s", "u", {},
                               meta={"type": "dropped_condition", "mapping": i, "source": maps[i]["source"],
                                     "ref": maps[i]["ref"]}) for i in range(3)]
        results = [runner.Result(reqs[0].custom_id, True, {"possible": True, "statement": "item 8.1", "change": "c"},
                                 "end_turn", {}),                                       # unchanged: dropped
                   runner.Result(reqs[1].custom_id, True, {"possible": True, "statement": "new", "change": "c"},
                                 "end_turn", {}),
                   runner.Result(reqs[2].custom_id, True, {"possible": False, "statement": "", "change": "no"},
                                 "end_turn", {})]
        out = mutate.text_mutants(maps, results, reqs)
        self.assertEqual([(m["original"], m["mapping"]["statement"]) for m in out["dropped_condition"]], [(1, "new")])
        self.assertEqual((out["added_condition"], out["looser_wording"]), ([], []))

    def test_wilson(self):
        self.assertEqual(mutate.wilson_lower(15, 15), 0.796)
        self.assertIsNone(mutate.wilson_lower(0, 0))

    def test_summarise(self):
        mapping = {"source": "s", "ref": "r", "statement": "x"}
        items = [{"type": "control", "position": 0, "layer1": [], "id": "control-001", "change": "", "mapping": mapping},
                 {"type": "control", "position": 3, "layer1": [], "id": "control-002", "change": "", "mapping": mapping},
                 {"type": "strength", "position": 1, "layer1": [["strength", "m"]], "id": "strength-001",
                  "change": "c", "mapping": mapping},
                 {"type": "looser_wording", "position": 2, "layer1": [], "id": "looser_wording-001", "change": "c",
                  "mapping": mapping},
                 {"type": "looser_wording", "position": 4, "layer1": [], "id": "looser_wording-002", "change": "c",
                  "mapping": mapping}]
        bad = {**VERDICT, "verdict": "incorrect"}
        rows, missed, unverified = mutate.summarise(items, {0: {"a": bad, "b": VERDICT}, 1: {"a": VERDICT, "b": VERDICT},
                                                            2: {"a": VERDICT}, 4: {"a": VERDICT, "b": VERDICT}})
        c = rows["control"]
        self.assertEqual((c["verified"], c["a"], c["answered_a"], c["clean_rate"]), (1, 1, 1, 0.0))   # 3 not answered
        self.assertEqual((rows["strength"]["layer1"], rows["strength"]["any"], rows["strength"]["verifiers"]), (1, 1, 0))
        lw = rows["looser_wording"]
        self.assertEqual((lw["n"], lw["verified"], lw["answered_a"], lw["answered_b"], lw["any_rate"]), (2, 1, 2, 1, 0.0))
        self.assertEqual([m["id"] for m in missed["looser_wording"]], ["looser_wording-002"])   # -001 is unverified
        self.assertEqual([u["id"] for u in unverified], ["control-002", "looser_wording-001"])
        rows, missed, unverified = mutate.summarise(items[:1], {})
        self.assertEqual((rows["control"]["clean_rate"], rows["control"]["a_rate"], missed), (None, None, {}))

    def test_layer1_credit_is_only_new_findings(self):
        maps, sources = real_mappings(), layer1.catalog()
        wrong = {**maps[0], "strength": "mandatory"}               # the quote reads "should"
        self.assertTrue(mutate.layer1_findings(wrong, sources))
        items = mutate.build([wrong], {"looser_wording": [mutate.mutant("looser_wording", 0,
                                                                        {**wrong, "statement": "y"}, "c")]},
                             {}, sources, random.Random(1))
        self.assertEqual({it["type"]: it["layer1"] for it in items}, {"control": [], "looser_wording": []})

    def test_only_correct_originals_are_used(self):
        maps, sources = real_mappings(), layer1.catalog()
        maps[0] = {**maps[0], "strength": "mandatory"}
        code = mutate.code_mutants(maps, sources, layer1.clauses_of, random.Random(1), eligible={1, 2})
        self.assertTrue(all(m["original"] in {1, 2} for g in code.values() for m in g))

    def test_no_batch_holds_two_variants_of_one_original(self):
        items = [{"original": o, "type": t} for o in range(3) for t in range(6)] + \
                [{"original": o, "type": 0} for o in range(3, 40)]
        n = mutate.assign_batches(items, random.Random(1), size=10)
        self.assertGreaterEqual(n, 6)
        for b in range(n):
            members = [it["original"] for it in items if it["batch"] == b]
            self.assertEqual(len(members), len(set(members)))
            self.assertLessEqual(len(members), 10)

    def test_text_requests_sizes(self):
        maps = real_mappings() * 10
        reqs = mutate.text_requests(maps, layer1.catalog(), layer1.clauses_of)
        count = {}
        for r in reqs:
            count[r.meta["type"]] = count.get(r.meta["type"], 0) + 1
        self.assertEqual(count, {"dropped_condition": 30, "added_condition": 18, "looser_wording": 18})

    def test_forced_mutants_beyond_per_type(self):
        maps = [{"source": "who-trs986-a2-gmp-main.pdf", "ref": "8.9", "statement": f"item {i}"} for i in range(20)]
        reqs = [runner.Request(f"mutate-dropped_condition-{i:03d}", "s", "u", {},
                               meta={"type": "dropped_condition", "mapping": i, "source": m["source"], "ref": "8.9"})
                for i, m in enumerate(maps)]
        results = [runner.Result(r.custom_id, True, {"possible": True, "statement": f"new {i}", "change": "c"},
                                 "end_turn", {}) for i, r in enumerate(reqs)]
        self.assertEqual(len(mutate.text_mutants(maps, results, reqs)["dropped_condition"]), 20)
        reqs[3].meta["ref"] = "8.1"                               # answers made for another mapping list
        with self.assertRaises(SystemExit):
            mutate.text_mutants(maps, results, reqs)


class EndToEnd(unittest.TestCase):
    def setUp(self):
        self.runs = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.runs)
        self.original, runner.RUNS = runner.RUNS, self.runs
        self.addCleanup(setattr, runner, "RUNS", self.original)

    def test_mutation_run(self):
        draft_dir = runner.new_run("session-draft")
        runner.write_jsonl(draft_dir / "mappings.jsonl", real_mappings())
        mutator_dir = mutate.prepare_text(draft_dir)
        mreqs = sessions.load_requests(mutator_dir)
        self.assertEqual(sum(r.meta["type"] == "dropped_condition" for r in mreqs), 3)
        self.assertTrue(all(r.user.startswith("CHANGE: ") for r in mreqs))
        n = iter(range(1000))
        answer_all(mutator_dir, lambda cid, inp: {"possible": True, "statement": f"Rewritten item {next(n)}.",
                                                  "change": "c"})
        verify_dir = mutate.prepare_verify(draft_dir, mutator_dir)
        key = runner.read_jsonl(verify_dir / "mutation-key.jsonl")
        types = {}
        for it in key:
            types[it["type"]] = types.get(it["type"], 0) + 1
        self.assertEqual(types["control"], 3)
        self.assertEqual(set(types), set(mutate.TYPES) | {"control"})
        self.assertEqual(sorted(it["position"] for it in key), list(range(len(key))))
        self.assertNotEqual([it["type"] for it in key][:3], ["control"] * 3)        # shuffled (seeded)
        link = json.loads((verify_dir / "mutation-link.json").read_text())
        self.assertEqual(link["mutator_run"], mutator_dir.name)
        # the verifiers get the pilot's own prompts and nothing that marks a mutant
        reqs = sessions.load_requests(verify_dir)
        self.assertEqual({r.system for r in reqs}, {pilot.prompt("verify_a"), pilot.prompt("verify_b")})
        for b in (verify_dir / "batches").glob("*.json"):
            batch = json.loads(b.read_text())
            text = " ".join(i["input"] + " " + i["custom_id"] for i in batch["items"]).lower()
            for word in ("mutant", "mutat", "control-", *(t for t in mutate.TYPES if "_" in t)):
                self.assertNotIn(word, text)
            roles = {i["custom_id"].split("-")[1] for i in json.loads(b.read_text())["items"]}
            self.assertEqual(len(roles), 1)
        names = sorted(b.name for b in (verify_dir / "batches").glob("*.json"))
        self.assertEqual(mutate.record_agents(verify_dir, "m", [0]), {names[0]: "m"})
        self.assertEqual(mutate.record_agents(verify_dir, "n"), {n: "n" for n in names})
        with self.assertRaises(SystemExit):
            mutate.record_agents(verify_dir, "m", [99])
        # no batch holds two variants of one original
        where = {}
        for r in reqs:
            where.setdefault(r.meta["batch"], []).append(key[r.meta["mapping"]]["original"])
        for originals in where.values():
            self.assertEqual(len(originals), 2 * len(set(originals)))      # each original once, for A and for B
        # verifier A rejects every mutant, B accepts everything: A catches all, controls stay clean
        kind = {it["position"]: it["type"] for it in key}
        answer_all(verify_dir, lambda cid, inp: {**VERDICT, "verdict": "incorrect" if "-a-" in cid and
                                                 kind[int(cid.rsplit("-", 1)[1])] != "control" else "correct"})
        rep = mutate.report(verify_dir)
        self.assertEqual(rep["failed_calls"], [])
        self.assertEqual(rep["false_alarms"], {"layer1": 0.0, "a": 0.0, "b": 0.0, "verifiers": 0.0})
        for t in mutate.TYPES:
            self.assertEqual(rep["by_type"][t]["a"], rep["by_type"][t]["n"], t)
            self.assertEqual(rep["by_type"][t]["b"], 0, t)
        self.assertEqual(rep["missed"], {})
        self.assertTrue((verify_dir / "mutation-report.json").exists())
        self.assertEqual(rep["unverified"], [])
        # same inputs, same key (seeded)
        again = mutate.prepare_verify(draft_dir, mutator_dir)
        strip = lambda rows: [{k: v for k, v in r.items()} for r in rows]
        self.assertEqual(strip(runner.read_jsonl(again / "mutation-key.jsonl")), strip(key))

    def test_mutator_run_is_tied_to_its_draft_run(self):
        draft_dir = runner.new_run("session-draft")
        runner.write_jsonl(draft_dir / "mappings.jsonl", real_mappings())
        mutator_dir = mutate.prepare_text(draft_dir)
        answer_all(mutator_dir, lambda cid, inp: {"possible": False, "statement": "", "change": "no"})
        runner.write_jsonl(draft_dir / "mappings.jsonl", real_mappings()[::-1])     # mappings changed
        with self.assertRaises(SystemExit):
            mutate.prepare_verify(draft_dir, mutator_dir)
        with self.assertRaises(SystemExit):
            mutate.prepare_text(mutator_dir)                                       # not a draft run

    def test_accepted_filter(self):
        draft_dir = runner.new_run("session-draft")
        runner.write_jsonl(draft_dir / "mappings.jsonl", real_mappings())
        vdir = pilot.prepare_verify(draft_dir)
        answer_all(vdir, lambda cid, inp: {**VERDICT, "verdict": "incorrect" if cid == "verify-b-001" else "correct"})
        sessions.ingest(vdir)
        self.assertEqual(mutate.accepted_by_both(vdir), {0, 2})
        mutator_dir = mutate.prepare_text(draft_dir)
        answer_all(mutator_dir, lambda cid, inp: {"possible": False, "statement": "", "change": "no"})
        verify_dir = mutate.prepare_verify(draft_dir, mutator_dir, accepted=vdir)
        key = runner.read_jsonl(verify_dir / "mutation-key.jsonl")
        self.assertEqual({it["original"] for it in key}, {0, 2})
        self.assertEqual(json.loads((verify_dir / "mutation-link.json").read_text())["excluded"], [1])

    def test_cli_checks_arguments(self):
        import unittest.mock
        for argv in (["mutate.py", "report"], ["mutate.py", "prepare-verify", "x"],
                     ["mutate.py", "report", "x", "--accepted", "y"]):
            with self.assertRaises(SystemExit), unittest.mock.patch.object(sys, "argv", argv), \
                    unittest.mock.patch("sys.stderr"):
                mutate.main()


if __name__ == "__main__":
    unittest.main()
