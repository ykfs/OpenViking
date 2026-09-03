// GENERATED FROM examples/memory-plugin-shared/lib. DO NOT EDIT.
import { existsSync } from "node:fs";
import { basename, dirname, join, parse, resolve } from "node:path";

/** Working-copy markers; both may appear as a directory or (git worktree/submodule) as a file. */
const GIT_MARKER = ".git";
const SVN_MARKER = ".svn";

/**
 * Walk upward from `cwd` to the directory that owns the version-controlled checkout.
 * Nearest `.git` wins, so a nested checkout belongs to its own project.
 * SVN 1.6 keeps a `.svn` in every directory while 1.7+ keeps one at the working-copy
 * root, so the outermost `.svn` is the one that names the checkout.
 * Returns "" for an empty argument or when no marker exists anywhere above.
 */
export function findWorkspaceRepoRoot(cwd) {
  const start = String(cwd || "").trim();
  if (!start) return "";
  let dir = resolve(start);
  const filesystemRoot = parse(dir).root;
  let outermostSvn = "";
  for (;;) {
    if (existsSync(join(dir, GIT_MARKER))) return dir;
    if (existsSync(join(dir, SVN_MARKER))) outermostSvn = dir;
    if (dir === filesystemRoot) break;
    dir = dirname(dir);
  }
  return outermostSvn;
}

/**
 * Peer segments travel in a header and a URI path, so anything the server would
 * reject as a path or a hidden file has to collapse to a hyphen first.
 */
function sanitizePeerSegment(value) {
  return String(value || "").replace(/[^A-Za-z0-9]/g, "-");
}

export function deriveWorkspacePeerId(cwd) {
  const start = String(cwd || "").trim();
  if (!start) return "";
  return sanitizePeerSegment(basename(findWorkspaceRepoRoot(start) || resolve(start)));
}

export function resolveEffectivePeerId({ cfg = {}, cwd = "" } = {}) {
  const explicit = String(cfg.peerId || "").trim();
  if (explicit) return { peerId: explicit, source: "explicit" };

  if (cfg.workspacePeer !== false) {
    const peerId = deriveWorkspacePeerId(cwd);
    if (peerId) return { peerId, source: "workspace" };
  }

  return { peerId: "", source: "none" };
}
