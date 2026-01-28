# Snapshot file
# Unset all aliases to avoid conflicts with functions
unalias -a 2>/dev/null || true
# Functions
eval "$(echo 'YnVpbGRhbmR1cCAoKSAKeyAKICAgIG1ha2UgZG93biAmJiBtYWtlIGJ1aWxkLWFuZC11cCAmJiBzZXJ2ZXJsb2dzCn0K' | base64 -d)" > /dev/null 2>&1
eval "$(echo 'bGlzdGVuICgpIAp7IAogICAgdXYgcnVuIGxpc3Rlbl9jbGllbnQucHkgLS1ob3N0IGhtZS13c3MtcGV0LTEtdXMtZWFzdC0xLmF1ZGl2aS5haTo0NDMgLS1iYXNlLXNuIDA4NTFVRTA4IC0tbGFuZSAxIC0tc3NsIC0tc3NsLW5vLXZlcmlmeQp9Cg==' | base64 -d)" > /dev/null 2>&1
eval "$(echo 'bnVrZSAoKSAKeyAKICAgIG1ha2UgZG93biAmJiBkb2NrZXIgc3lzdGVtIHBydW5lIC1hZiAmJiBkb2NrZXIgYnVpbGRlciBwcnVuZSAtLWFsbCAtZiAmJiBtYWtlIGJ1aWxkLWFuZC11cAp9Cg==' | base64 -d)" > /dev/null 2>&1
eval "$(echo 'bnVrZWFuZGxpc3RlbiAoKSAKeyAKICAgIGdpdCBzdGFzaCAmJiBnaXQgc3dpdGNoIGR4L2xpc3RlbmVyICYmIG51a2UgJiYgbGlzdGVuCn0K' | base64 -d)" > /dev/null 2>&1
eval "$(echo 'bnVrZWFuZHVwICgpIAp7IAogICAgbWFrZSBkb3duICYmIGRvY2tlciBzeXN0ZW0gcHJ1bmUgLWFmICYmIGRvY2tlciBidWlsZGVyIHBydW5lIC0tYWxsIC1mICYmIG1ha2UgYnVpbGQtYW5kLXVwICYmIHNlcnZlcmxvZ3MKfQo=' | base64 -d)" > /dev/null 2>&1
eval "$(echo 'cGFyc2VfZ2l0X2JyYW5jaCAoKSAKeyAKICAgIGdpdCBicmFuY2ggMj4gL2Rldi9udWxsIHwgc2VkIC1lICcvXlteKl0vZCcgLWUgJ3MvKiBcKC4qXCkvIChcMSkvJwp9Cg==' | base64 -d)" > /dev/null 2>&1
eval "$(echo 'c2VydmVybG9ncyAoKSAKeyAKICAgIGRvY2tlciBsb2dzIC1mIGF1ZGl2aV9zZXJ2ZXIKfQo=' | base64 -d)" > /dev/null 2>&1
eval "$(echo 'dXBvbmx5ICgpIAp7IAogICAgbWFrZSBkb3duICYmIG1ha2UgdXAtb25seSAmJiBzZXJ2ZXJsb2dzCn0K' | base64 -d)" > /dev/null 2>&1
# Shell Options
shopt -u array_expand_once
shopt -u assoc_expand_once
shopt -s autocd
shopt -u bash_source_fullpath
shopt -u cdable_vars
shopt -u cdspell
shopt -u checkhash
shopt -u checkjobs
shopt -s checkwinsize
shopt -s cmdhist
shopt -u compat31
shopt -u compat32
shopt -u compat40
shopt -u compat41
shopt -u compat42
shopt -u compat43
shopt -u compat44
shopt -s complete_fullquote
shopt -u direxpand
shopt -u dirspell
shopt -u dotglob
shopt -u execfail
shopt -u expand_aliases
shopt -u extdebug
shopt -u extglob
shopt -s extquote
shopt -u failglob
shopt -s force_fignore
shopt -s globasciiranges
shopt -s globskipdots
shopt -s globstar
shopt -u gnu_errfmt
shopt -u histappend
shopt -u histreedit
shopt -u histverify
shopt -s hostcomplete
shopt -u huponexit
shopt -u inherit_errexit
shopt -s interactive_comments
shopt -u lastpipe
shopt -u lithist
shopt -u localvar_inherit
shopt -u localvar_unset
shopt -s login_shell
shopt -u mailwarn
shopt -u no_empty_cmd_completion
shopt -u nocaseglob
shopt -u nocasematch
shopt -u noexpand_translation
shopt -u nullglob
shopt -s patsub_replacement
shopt -s progcomp
shopt -u progcomp_alias
shopt -s promptvars
shopt -u restricted_shell
shopt -u shift_verbose
shopt -s sourcepath
shopt -u varredir_close
shopt -u xpg_echo
set -o braceexpand
set -o hashall
set -o interactive-comments
set -o monitor
set -o onecmd
shopt -s expand_aliases
# Aliases
# Check for rg availability
if ! command -v rg >/dev/null 2>&1; then
  alias rg='/opt/homebrew/Caskroom/claude-code/2.0.76/claude --ripgrep'
fi
export PATH=/Users/seanreed/.volta/bin\:/Library/Frameworks/Python.framework/Versions/3.13/bin\:/Library/Frameworks/Python.framework/Versions/3.12/bin\:/opt/homebrew/opt/libpq/bin\:/opt/homebrew/bin\:/opt/homebrew/sbin\:/usr/local/bin\:/System/Cryptexes/App/usr/bin\:/usr/bin\:/bin\:/usr/sbin\:/sbin\:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/local/bin\:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/bin\:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/appleinternal/bin\:/Users/seanreed/.volta/bin\:/Library/Frameworks/Python.framework/Versions/3.13/bin\:/Library/Frameworks/Python.framework/Versions/3.12/bin\:/opt/homebrew/opt/libpq/bin\:/Users/seanreed/.cursor/extensions/ms-python.debugpy-2025.18.0-darwin-arm64/bundled/scripts/noConfigScripts
