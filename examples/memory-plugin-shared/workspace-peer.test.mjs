import test, { after } from "node:test";
import assert from "node:assert/strict";
import { mkdirSync, mkdtempSync, realpathSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { deriveWorkspacePeerId, findWorkspaceRepoRoot, resolveEffectivePeerId } from "./lib/workspace-peer.mjs";

// A realpathed root keeps path equality assertions stable on macOS, where the
// temp directory is reached through a symlink.
const FIXTURE_ROOT = realpathSync(mkdtempSync(join(tmpdir(), "ov-peer-")));

// Walking upward does not stop at the fixture, so a checkout above the temp
// directory would answer "no marker" cases with that checkout instead. When
// that happens those cases assert the invariants that must hold either way.
const ANCESTORS_CLEAN = findWorkspaceRepoRoot(FIXTURE_ROOT) === "";

after(() => {
  rmSync(FIXTURE_ROOT, { recursive: true, force: true });
});

function fixture(...parts) {
  const target = join(FIXTURE_ROOT, ...parts);
  mkdirSync(target, { recursive: true });
  return target;
}

function gitCheckout(dir) {
  mkdirSync(join(dir, ".git"), { recursive: true });
  return dir;
}

function assertPeerSegment(peer) {
  assert.match(peer, /^[A-Za-z0-9_.@-]*$/);
  assert.doesNotMatch(peer, /[\\/]/);
}

test("findWorkspaceRepoRoot returns the directory owning a .git folder", () => {
  // Arrange
  const repo = gitCheckout(fixture("repo-git"));
  // Act & Assert
  assert.equal(findWorkspaceRepoRoot(repo), repo);
});

test("findWorkspaceRepoRoot accepts a .git file used by worktrees and submodules", () => {
  // Arrange
  const repo = fixture("repo-worktree");
  writeFileSync(join(repo, ".git"), "gitdir: /somewhere/.git/worktrees/linked\n");
  // Act & Assert
  assert.equal(findWorkspaceRepoRoot(repo), repo);
});

test("findWorkspaceRepoRoot picks the nearest .git in nested checkouts", () => {
  // Arrange
  const outer = gitCheckout(fixture("nested-git/outer"));
  const inner = gitCheckout(join(outer, "inner"));
  const deep = fixture("nested-git/outer/inner/src/lib");
  // Act & Assert
  assert.equal(findWorkspaceRepoRoot(deep), inner);
});

test("findWorkspaceRepoRoot resolves an SVN 1.7 working copy from a nested directory", () => {
  // Arrange
  const wc = fixture("svn17");
  mkdirSync(join(wc, ".svn"));
  const deep = fixture("svn17/trunk/module");
  // Act & Assert
  assert.equal(findWorkspaceRepoRoot(deep), wc);
});

test("findWorkspaceRepoRoot resolves an SVN 1.6 working copy to its outermost .svn", () => {
  // Arrange
  const wc = fixture("svn16");
  mkdirSync(join(wc, ".svn"));
  const sub = fixture("svn16/trunk");
  mkdirSync(join(sub, ".svn"));
  // Act & Assert
  assert.equal(findWorkspaceRepoRoot(sub), wc);
});

test("findWorkspaceRepoRoot prefers git over svn at the same level", () => {
  // Arrange
  const mixed = fixture("mixed");
  gitCheckout(mixed);
  mkdirSync(join(mixed, ".svn"));
  const child = fixture("mixed/sub");
  // Act & Assert
  assert.equal(findWorkspaceRepoRoot(mixed), mixed);
  assert.equal(findWorkspaceRepoRoot(child), mixed);
});

test("findWorkspaceRepoRoot returns empty string without markers or input", () => {
  // Arrange
  const plain = fixture("plain/deep");
  // Act & Assert
  assert.equal(findWorkspaceRepoRoot(""), "");
  assert.equal(findWorkspaceRepoRoot(null), "");
  assert.equal(findWorkspaceRepoRoot(undefined), "");
  assert.equal(findWorkspaceRepoRoot("   "), "");
  if (ANCESTORS_CLEAN) {
    assert.equal(findWorkspaceRepoRoot(plain), "");
  }
});

test("deriveWorkspacePeerId gives teammates the same peer for the same checkout name", () => {
  // Arrange
  const machineA = gitCheckout(fixture("machine-a/Documents/work/hsurp-aigc"));
  const machineB = gitCheckout(fixture("machine-b/home/zhang/work/hsurp-aigc"));
  // Act
  const peerA = deriveWorkspacePeerId(machineA);
  const peerB = deriveWorkspacePeerId(machineB);
  // Assert
  assert.equal(peerA, "hsurp-aigc");
  assert.equal(peerB, peerA);
});

test("deriveWorkspacePeerId sanitizes non-alphanumeric characters out of the name", () => {
  // Arrange
  const repo = gitCheckout(fixture("odd/TCMP 4.0"));
  // Act
  const peer = deriveWorkspacePeerId(repo);
  // Assert
  assert.equal(peer, "TCMP-4-0");
  assertPeerSegment(peer);
});

test("deriveWorkspacePeerId keeps a non-ASCII checkout inside the server charset", () => {
  // Arrange
  const repo = gitCheckout(fixture("cjk/中信信托"));
  // Act
  const peer = deriveWorkspacePeerId(repo);
  // Assert
  assert.equal(peer, "----");
  assertPeerSegment(peer);
});

test("deriveWorkspacePeerId falls back to the workspace directory name outside a checkout", () => {
  // Arrange
  const deep = fixture("plain-fallback/plain/deep");
  // Act
  const peer = deriveWorkspacePeerId(deep);
  // Assert
  assertPeerSegment(peer);
  if (ANCESTORS_CLEAN) {
    assert.equal(peer, "deep");
  }
});

test("deriveWorkspacePeerId returns empty string for the filesystem root and blank input", () => {
  // Act & Assert
  assert.equal(deriveWorkspacePeerId(""), "");
  assert.equal(deriveWorkspacePeerId(null), "");
  assert.equal(deriveWorkspacePeerId(undefined), "");
  assert.equal(deriveWorkspacePeerId("   "), "");
  if (process.platform !== "win32") {
    assert.equal(deriveWorkspacePeerId("/"), "");
  }
});

test("deriveWorkspacePeerId never throws on unreachable or malformed paths", () => {
  // Act & Assert
  assert.doesNotThrow(() => deriveWorkspacePeerId("/definitely/not/here/nor/anywhere"));
  assert.doesNotThrow(() => deriveWorkspacePeerId("/no/such/\u0000x"));
  assert.equal(typeof deriveWorkspacePeerId({}), "string");
  assert.equal(typeof deriveWorkspacePeerId(123), "string");
});

test("resolveEffectivePeerId keeps an explicit peer ahead of the checkout name", () => {
  // Arrange
  const repo = gitCheckout(fixture("explicit/proj-x"));
  // Act
  const resolved = resolveEffectivePeerId({ cfg: { peerId: " configured " }, cwd: repo });
  // Assert
  assert.deepEqual(resolved, { peerId: "configured", source: "explicit" });
});

test("resolveEffectivePeerId derives the checkout directory name by default", () => {
  // Arrange
  gitCheckout(fixture("derived/proj-x"));
  const deep = fixture("derived/proj-x/src/main/java");
  // Act
  const resolved = resolveEffectivePeerId({ cfg: {}, cwd: deep });
  // Assert
  assert.deepEqual(resolved, { peerId: "proj-x", source: "workspace" });
});

test("resolveEffectivePeerId returns no peer when workspace derivation is off", () => {
  // Arrange
  const repo = gitCheckout(fixture("disabled/proj-off"));
  // Act & Assert
  assert.deepEqual(
    resolveEffectivePeerId({ cfg: { workspacePeer: false }, cwd: repo }),
    { peerId: "", source: "none" },
  );
  assert.deepEqual(
    resolveEffectivePeerId({ cfg: {}, cwd: "" }),
    { peerId: "", source: "none" },
  );
});
