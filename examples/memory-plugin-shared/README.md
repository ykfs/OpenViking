# Memory Plugin Shared Library

This directory contains shared JavaScript modules that are vendored into the
Claude Code, Codex, OpenCode, and pi memory plugins by `sync.mjs`.

> **Requires an OpenViking server with `viking://~` home-alias support.** Recall targets the
> caller's own context space through `viking://~/memories` and `viking://~/skills`; the uid-less
> `viking://user/memories` shorthand is rejected by newer servers.

## Workspace Peers

`lib/workspace-peer.mjs` derives the default actor peer from the working copy
that owns the current workspace. The path is walked upward for a `.git` marker
(directory or file) or an `.svn` marker: the nearest `.git` wins, an SVN 1.6
working copy resolves to its outermost `.svn`, and the last directory name of
that root becomes the peer. Only `A-Z`, `a-z`, and `0-9` survive; every other
character in the name becomes `-`. Outside any working copy the workspace
directory's own name is used, and an empty path yields no peer. For example,
`/Users/x/Dev/OpenViking` and `/home/y/work/OpenViking` both become
`OpenViking`, so teammates sharing one account share one peer per project.

Two consequences matter when you rely on a shared peer:

- Teammates must clone the repository under the same directory name, because
  that name is the peer.
- Memory captured earlier under the old full-path peer is not matched under the
  new one. Set `OPENVIKING_RECALL_PEER_SCOPE=all` for broad recall, or
  `OPENVIKING_PEER_ID` to the old value, to reach it.

Resolution order is:

1. Explicit peer: `OPENVIKING_PEER_ID`, `actor_peer_id` / `peer_id` in
   `ovcli.conf`, or the harness-specific legacy peer config.
2. Workspace-derived peer when `workspacePeer` is not `false`.
3. No peer.

Set `OPENVIKING_WORKSPACE_PEER=0` or the harness config `workspacePeer=false`
to disable workspace-derived peers.

## Recall Peer Scope

`lib/recall-core.mjs` defaults to the broad recall mode and does not send a
`peer_scope` field. In that mode, the server can recall global memory, the
current workspace, and other workspace memories; other workspaces are penalized
and rendered later.

When `recallPeerScope` is `actor`, the helper sends `peer_scope:"actor"`. This
is the isolation mode: recall only sees global memory plus the current
workspace. If an older server rejects that field with 400 or 422, `postRecall`
removes `peer_scope` and retries once.

For deployments where one bot serves multiple real people, such as zouk,
vikingbot, or AstrBot, configure an explicit actor peer and use the isolation
mode so one person's memories are not recalled into another person's session.
