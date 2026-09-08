# Git Runbook: Fork -> Branch -> Push -> PR (and how Daniela sees the result)

*Companion to PROJECT_WORKFLOW.md. That doc explains what's in the repo; this one explains how code gets in and out of it.*

## The repos and branch involved

- **upstream** = `https://github.com/ksshah/seed-and-scale.git`, Kaveesha's repo, the source of truth the team submits from.
- **origin** = `https://github.com/heschmidt04/seed-and-scale`, Heidi's personal fork, where Heidi's work-in-progress branches live.
- **current branch** = `wid_summary`, Heidi's working branch on her fork, currently committed locally but not yet pushed to GitHub at all.

Nobody but Kaveesha can push directly to `ksshah/seed-and-scale`. Everyone else works on their own fork and asks Kaveesha to pull their changes in via a Pull Request (PR). That's not a formality, it's the only way changes reach the shared repo.

## Part 1: One-time setup (already done, kept here for reference)

This is what created the remotes you already have:

```bash
# fork Kaveesha's repo on github.com first (the Fork button), then clone your fork:
git clone https://github.com/heschmidt04/seed-and-scale.git
cd seed-and-scale
git remote add upstream https://github.com/ksshah/seed-and-scale.git
```

`git remote -v` should now show `origin` pointing at your fork and `upstream` pointing at Kaveesha's, which matches what you already have.

## Part 2: Daily workflow for anyone contributing

1. Start from an up-to-date `main`, so you're not branching off stale code:
   ```bash
   git checkout main
   git fetch upstream
   git merge upstream/main
   git push origin main
   ```
2. Create a branch for your piece of work:
   ```bash
   git checkout -b your-branch-name
   ```
3. Edit, then stage and commit as usual:
   ```bash
   git add <files>
   git commit -m "clear one-line description of what changed"
   ```
4. Push your branch to *your own fork* (not upstream, you don't have write access there):
   ```bash
   git push -u origin your-branch-name
   ```
   The `-u` only matters the first time, it tells git that future plain `git push` on this branch should go here.

## Part 3: The Colab URL pattern (how anyone opens any notebook, from any branch)

```
https://colab.research.google.com/github/<OWNER>/<REPO>/blob/<BRANCH>/<PATH>.ipynb
```

- `OWNER` = whichever account's copy you want: `heschmidt04` for Heidi's fork, `ksshah` for the shared upstream.
- `BRANCH` = `wid_summary` while work is in progress, `main` once Kaveesha merges it.
- `PATH` = the file's path inside the repo, e.g. `summary/WiD_Summary_TheWaterBill.ipynb` if the reorg from PROJECT_WORKFLOW.md happens, or just the filename if it doesn't.

Two concrete examples:

- Heidi's in-progress work right now: `https://colab.research.google.com/github/heschmidt04/seed-and-scale/blob/wid_summary/summary/WiD_Summary_TheWaterBill.ipynb`
- The same file after Kaveesha merges to upstream `main`: `https://colab.research.google.com/github/ksshah/seed-and-scale/blob/main/summary/WiD_Summary_TheWaterBill.ipynb`

Saving changes made inside Colab back to GitHub: **File > Save a copy in GitHub**, then pick the *same* repo, branch, and path so it overwrites in place instead of creating a duplicate file somewhere.

## Part 3.5: Checking in a run of `WiD_Summary_TheWaterBill.ipynb`

This notebook is written to be run in Colab (it needs FAOSTAT's bulk-download domain, which this
assistant's own sandbox can't reach). Once you `Run All`, here's the loop for getting the populated
version, plus the charts and tables it produces, back into the repo:

1. In Colab, `Run All`. Every chart and table lands in one `outputs/` folder inside that Colab
   session (the notebook creates this itself in Section 0), rather than scattered across the session's
   root directory.
2. In Colab's left-hand file panel, right-click the `outputs` folder and **Download** -- one zip with
   all 4 PNGs and all 4 CSVs.
3. **File > Save a copy in GitHub**, same repo/branch/path as always (`heschmidt04/seed-and-scale`,
   `wid_summary`, `summary/WiD_Summary_TheWaterBill.ipynb`) -- this overwrites the code-only version
   with the run version, cell outputs and all.
4. On your Mac: `git pull`, unzip the downloaded folder into `summary/outputs/` (create it if it
   doesn't exist), then `git add summary/outputs summary/WiD_Summary_TheWaterBill.ipynb && git commit
   && git push`. Notebook and exported files land in the same commit.

This is also the mechanism for a quick sanity check with Claude mid-session, not just the final push:
Save a copy in GitHub, `git pull`, and the run version is sitting in your local folder where it can be
read directly, no separate export or upload step needed for the notebook itself. If you're mid-iteration
and don't want a commit yet, downloading the `.ipynb` directly from Colab's file panel (rather than
Save-a-copy-in-GitHub) and dropping it anywhere in the local repo folder works too, without touching git
at all until you're ready.

## Part 4: Getting `wid_summary` published and the PR opened (your actual next step)

Your local `wid_summary` branch is committed and clean but hasn't touched GitHub yet. I don't have a shell on your Mac in this session, just file read/write, so these are commands for you to run, and I'm glad to walk through them with you one at a time if you'd rather do that than run the whole block at once.

1. **Sync with upstream one more time before publishing**, in case Shruti or Kaveesha pushed anything since you branched, so the PR doesn't carry avoidable conflicts:
   ```bash
   git fetch upstream
   git merge upstream/main
   ```
   If this reports a conflict, stop and let's look at it together rather than guessing at a resolution.

2. **Push the branch to your fork.** This is the step that actually puts `wid_summary` "in your fork", there's no separate merge-into-your-fork step, pushing the branch *is* that:
   ```bash
   git push -u origin wid_summary
   ```

3. **Open the PR against Kaveesha's `main`.** Two ways, pick whichever's available to you:

   **Web UI** (no tooling needed): go to `https://github.com/heschmidt04/seed-and-scale`. GitHub will show a "Compare & pull request" banner for the branch you just pushed, click it. On the compare screen, confirm base repository = `ksshah/seed-and-scale`, base branch = `main`, and compare = `heschmidt04:wid_summary`. Write a short title and description (the PROJECT_WORKFLOW.md content is good raw material for the description), then **Create pull request**.

   **GitHub CLI** (check first with `gh --version`, skip this if it's not installed):
   ```bash
   gh pr create --repo ksshah/seed-and-scale --base main --head heschmidt04:wid_summary \
     --title "Rice water-stress summary (The Water Bill)" \
     --body "Adds the rice x water-stress analysis, ported from the barley simulator pipeline, plus the reorganized discovery/summary/docs layout. See PROJECT_WORKFLOW.md for the full map."
   ```

4. From there it's Kaveesha's call: she reviews and merges (or asks for changes first). Once merged, the Part 3 URLs pointing at `ksshah/seed-and-scale` on `main` become live.

## Part 5: What Daniela actually needs to do (after Kaveesha merges)

She doesn't need git, a fork, or even a GitHub account for the simplest path. In order of simplicity:

1. **View it rendered, directly on GitHub**: open `https://github.com/ksshah/seed-and-scale/blob/main/summary/WiD_Summary_TheWaterBill.ipynb` in a browser. GitHub renders notebooks with their saved charts and output inline, no login, no waiting for anything to run. This alone is probably enough to record the video from, screen-share and scroll.
2. **If she wants to interact with it live in Colab instead**: open `https://colab.research.google.com/github/ksshah/seed-and-scale/blob/main/summary/WiD_Summary_TheWaterBill.ipynb`. This opens read-only against the shared repo, if she wants to re-run any cells herself she should do **File > Save a copy in Drive** first, so she's working on her own copy rather than accidentally trying to push edits back to Kaveesha's repo.

**One thing to make sure happens before the final push Kaveesha merges**: every cell needs to have actually been *run*, with its output saved in the notebook file, before that last commit. Otherwise option 1 above shows empty cells with no charts, since GitHub only renders whatever was saved, it doesn't execute anything itself. `Run All` then save, as the very last step before pushing, is the way to guarantee Daniela sees charts and not blank cells.
