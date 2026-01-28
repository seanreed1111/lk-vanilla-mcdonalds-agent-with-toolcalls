# Snapshot file
# Unset all aliases to avoid conflicts with functions
unalias -a 2>/dev/null || true
# Functions
eval "$(echo 'cGFyc2VfZ2l0X2JyYW5jaCAoKSAKeyAKICAgIGdpdCBicmFuY2ggMj4gL2Rldi9udWxsIHwgc2VkIC1lICcvXlteKl0vZCcgLWUgJ3MvKiBcKC4qXCkvIChcMSkvJwp9Cg==' | base64 -d)" > /dev/null 2>&1
eval "$(echo 'dXZzeW5jICgpIAp7IAogICAgdXYgc3luYyAtLWFsbC1wYWNrYWdlcyAtLWdyb3VwIGRldiAtLWV4dHJhIHRlc3QKfQo=' | base64 -d)" > /dev/null 2>&1
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
alias -- z='_z 2>&1'
# Check for rg availability
if ! command -v rg >/dev/null 2>&1; then
  alias rg='/opt/homebrew/Caskroom/claude-code/2.0.76/claude --ripgrep'
fi
export PATH=/Users/seanreed/.local/bin\:/Users/seanreed/.volta/bin\:/opt/homebrew/opt/libpq/bin\:/opt/homebrew/bin\:/opt/homebrew/sbin\:/usr/local/bin\:/System/Cryptexes/App/usr/bin\:/usr/bin\:/bin\:/usr/sbin\:/sbin\:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/local/bin\:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/bin\:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/appleinternal/bin\:/opt/pmk/env/global/bin\:/Users/seanreed/.local/bin\:/Users/seanreed/.volta/bin\:/Library/Frameworks/Python.framework/Versions/3.13/bin\:/Library/Frameworks/Python.framework/Versions/3.12/bin\:/opt/homebrew/opt/libpq/bin
