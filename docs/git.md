# Git

Uzak depo: **GitHub**. Varsayılan branch: `main`.

## Branching
- `feature/<spec-no>-<short-name>` — **no branch without a spec.** Also for CHANGE-lane mini-specs.
- Refactors: `refactor/<spec-no>-<short-name>` (mini-spec with Changed behavior = none).
- Fixes: `fix/<report-id>-<short-name>` (bug fixes carry a report, not a spec number);
  incidents: `incident/<date>-<short-name>`; trivial changes: `trivial/<short-name>` (see below).
- Bilinen sapmaların düzeltmesinde rapor ID'si sapma numarasıdır: `fix/D6-balance-check`.
- Branch adları İngilizce ve ASCII (Türkçe karakter yok).

## Commits
- Conventional Commits, with a plan reference: `feat(catalog): paging endpoint [plan 0001/3]`.
  Review fixes name their fix round instead of the step:
  `fix(catalog): empty page size [plan 0001/fix-2]` — the reviewer counts rounds from these
  (R-06 after round 3).
- Agent commits follow the same standard: the agent writes the message, the human approves.
- Dil: tip ve kapsam İngilizce, açıklama **Türkçe**:
  `fix(domain): 15 yıl kıdemde hak 26 gün [plan 0002/1]`.

## Forbidden
- Direct commits to the default branch.
- Force push, history rewriting on shared branches. Undo = `git revert` (see recovery R-11).
- Tek bilinçli istisna: bootstrap'in `main`'e attığı iki ilk commit (orijinal kod ve çalışma
  alanı) — o anda başka branch yoktu.

## Trivial changes
<!-- Set at bootstrap. Applies only to requests the change-request triage rubric
     (workflows/change-request.md) classifies as TRIVIAL: no acceptance criterion changes, no shared code. -->
- Policy: **(1) PR + one reviewer, no spec** — seçildi (bootstrap, 2026-10-25). Ekip tek kişi
  olduğu için reviewer, read-only reviewer alt ajanıdır (`.claude/agents/reviewer.md`).
- Always: one narrow commit, `scripts/check` green. A second file or a new test means re-triage.

## Pull requests
- PR template checklist completed; `scripts/check` green in CI; squash-merge.
- Ekip tek kişi: GitHub'da zorunlu insan onayı **0** (kendi PR'ınızı onaylayamazsınız).
  Bağımsız review her PR'da reviewer alt ajanıyla yapılır; ikinci bir kişi katılırsa ve koruma
  açıksa zorunlu onay 1'e çıkar.
- **Branch koruması (`main`)**: PR zorunlu; `doctor` ve `check` job'ları zorunlu durum kontrolü
  (`audit` bilgilendirici); force push ve silme kapalı. GitHub ayarından elle yapılır.
  **Şu an uygulanmıyor (2026-11-04):** depo özel; GitHub korumayı açmak için Pro'ya geçmeyi ya da
  depoyu herkese açmayı istiyor (HTTP 403). Bu kuralları şimdilik yalnızca çalışma disiplini tutar.
  CI'daki `doctor` / `check` her push ve PR'da çalışır ama yalnızca sonucu bildirir: kırmızı
  sonuç merge'ü, doğrudan push'u, force push'u ya da silmeyi engellemez. Hesap Pro'ya geçerse ya
  da depo herkese açılırsa koruma elle açılır. O zamana kadar `workflows/segments.md` ve PR
  şablonundaki "CI enforces / gates hold" ifadeleri "CI bildirir" diye okunur.
